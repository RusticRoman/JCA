import hashlib
import secrets
import uuid

from fastapi import APIRouter, Cookie, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.curriculum import Program, Video
from app.models.progress import VideoProgress
from app.models.user import User, UserRole

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/pages", tags=["pages"])
root_router = APIRouter(tags=["root"])

# Simple in-memory session store (use Redis in production)
_sessions: dict[str, uuid.UUID] = {}


def _hash_password(password: str, salt: str = "") -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}", salt


def _verify_password(password: str, stored: str) -> bool:
    salt, expected_hash = stored.split(":", 1)
    actual = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return actual == expected_hash


async def _get_session_user(db: AsyncSession, session_id: str | None) -> User | None:
    if not session_id or session_id not in _sessions:
        return None
    user_id = _sessions[session_id]
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


# ── Root redirect ────────────────────────────────────────────────────

@root_router.get("/")
async def root_redirect():
    return RedirectResponse(url="/pages/login", status_code=303)


# ── Login ────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "No account found with that email address.",
        })

    if not user.firebase_uid.startswith("local:"):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "This account uses Firebase sign-in. Please use Google sign-in.",
        })

    stored_password = user.firebase_uid.removeprefix("local:")
    if not _verify_password(password, stored_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Incorrect password.",
        })

    # Create session and redirect based on role
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = user.id
    dest = "/pages/mentor-dashboard" if user.role in (UserRole.RABBI, UserRole.TEACHER, UserRole.ADMIN) else "/pages/dashboard"
    response = RedirectResponse(url=dest, status_code=303)
    response.set_cookie(key="session", value=session_id, httponly=True, max_age=86400)
    return response


# ── Register ─────────────────────────────────────────────────────────

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = "", success: str = ""):
    return templates.TemplateResponse("register.html", {
        "request": request, "error": error, "success": success,
    })


@router.post("/register")
async def register_submit(
    request: Request,
    display_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Passwords do not match.", "success": "",
        })

    if len(password) < 8:
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "Password must be at least 8 characters.", "success": "",
        })

    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        return templates.TemplateResponse("register.html", {
            "request": request, "error": "An account with that email already exists.", "success": "",
        })

    hashed, _ = _hash_password(password)

    # Auto-assign to a mentor (first available RABBI)
    mentor_result = await db.execute(
        select(User).where(User.role == UserRole.RABBI, User.is_active.is_(True)).limit(1)
    )
    mentor = mentor_result.scalar_one_or_none()

    user = User(
        firebase_uid=f"local:{hashed}",
        email=email,
        display_name=display_name,
        mentor_id=mentor.id if mentor else None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Auto-login after registration
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = user.id
    response = RedirectResponse(url="/pages/dashboard", status_code=303)
    response.set_cookie(key="session", value=session_id, httponly=True, max_age=86400)
    return response


# ── Dashboard ────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    session: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_session_user(db, session)
    if not user:
        return RedirectResponse(url="/pages/login", status_code=303)

    # Gather progress stats
    progress_result = await db.execute(
        select(VideoProgress).where(VideoProgress.user_id == user.id)
    )
    all_progress = progress_result.scalars().all()
    completed = [p for p in all_progress if p.is_completed]

    # Gather curriculum stats
    programs_result = await db.execute(select(Program))
    programs = programs_result.scalars().all()
    total_videos = 0
    for program in programs:
        for semester in program.semesters:
            for subject in semester.subjects:
                total_videos += len(subject.videos)

    completion_pct = (len(completed) / total_videos * 100) if total_videos > 0 else 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "videos_completed": len(completed),
        "videos_total": total_videos,
        "videos_in_progress": len(all_progress) - len(completed),
        "completion_pct": round(completion_pct, 1),
        "programs": programs,
    })


# ── Mentor Dashboard ──────────────────────────────────────────────────

@router.get("/mentor-dashboard", response_class=HTMLResponse)
async def mentor_dashboard_page(
    request: Request,
    session: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_session_user(db, session)
    if not user:
        return RedirectResponse(url="/pages/login", status_code=303)
    if user.role not in (UserRole.RABBI, UserRole.TEACHER, UserRole.ADMIN):
        return RedirectResponse(url="/pages/dashboard", status_code=303)

    # Get assigned students
    result = await db.execute(
        select(User).where(User.mentor_id == user.id, User.is_active.is_(True))
    )
    students = result.scalars().all()

    # Total videos for percentage calculation
    programs_result = await db.execute(select(Program))
    programs = programs_result.scalars().all()
    total_videos = 0
    for program in programs:
        for semester in program.semesters:
            for subject in semester.subjects:
                total_videos += len(subject.videos)

    # Enrich each student with their completion stats
    student_data = []
    total_completed_all = 0
    for s in students:
        prog_result = await db.execute(
            select(VideoProgress).where(VideoProgress.user_id == s.id)
        )
        progress = prog_result.scalars().all()
        completed = sum(1 for p in progress if p.is_completed)
        total_completed_all += completed
        pct = round(completed / total_videos * 100, 1) if total_videos > 0 else 0
        student_data.append({
            "id": s.id,
            "display_name": s.display_name,
            "email": s.email,
            "enrollment_semester": s.enrollment_semester,
            "completion_pct": pct,
        })

    avg_completion = round(
        sum(s["completion_pct"] for s in student_data) / len(student_data), 1
    ) if student_data else 0

    return templates.TemplateResponse("mentor_dashboard.html", {
        "request": request,
        "user": user,
        "students": student_data,
        "avg_completion": avg_completion,
        "total_completed": total_completed_all,
    })


# ── Mentor: Student Detail ───────────────────────────────────────────

@router.get("/mentor/student/{student_id}", response_class=HTMLResponse)
async def mentor_student_detail(
    request: Request,
    student_id: uuid.UUID,
    session: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_session_user(db, session)
    if not user:
        return RedirectResponse(url="/pages/login", status_code=303)
    if user.role not in (UserRole.RABBI, UserRole.TEACHER, UserRole.ADMIN):
        return RedirectResponse(url="/pages/dashboard", status_code=303)

    # Verify this student is assigned to this mentor
    result = await db.execute(
        select(User).where(User.id == student_id, User.mentor_id == user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        return RedirectResponse(url="/pages/mentor-dashboard", status_code=303)

    # Get all progress for this student
    prog_result = await db.execute(
        select(VideoProgress).where(VideoProgress.user_id == student.id)
    )
    all_progress = prog_result.scalars().all()
    progress_by_video = {p.video_id: p for p in all_progress}
    completed = [p for p in all_progress if p.is_completed]
    in_progress = [p for p in all_progress if not p.is_completed]
    live_count = sum(1 for p in all_progress if p.attendance_type.value == "LIVE")

    # Build curriculum breakdown
    programs_result = await db.execute(select(Program))
    programs = programs_result.scalars().all()
    total_videos = 0
    semesters_data = []

    for program in programs:
        for semester in program.semesters:
            sem_completed = 0
            sem_total = 0
            subjects_data = []
            for subject in semester.subjects:
                videos_data = []
                subj_completed = 0
                for video in subject.videos:
                    total_videos += 1
                    sem_total += 1
                    p = progress_by_video.get(video.id)
                    if p and p.is_completed:
                        status = "completed"
                        subj_completed += 1
                        sem_completed += 1
                    elif p:
                        status = "in_progress"
                    else:
                        status = "not_started"
                    videos_data.append({
                        "title": video.title,
                        "status": status,
                    })
                subjects_data.append({
                    "name": subject.name,
                    "videos": videos_data,
                    "completed": subj_completed,
                })
            semesters_data.append({
                "name": semester.name,
                "number": semester.number,
                "subjects": subjects_data,
                "completed_videos": sem_completed,
                "total_videos": sem_total,
            })

    completion_pct = round(len(completed) / total_videos * 100, 1) if total_videos > 0 else 0

    # Recent activity (last 10 video interactions)
    recent_result = await db.execute(
        select(VideoProgress)
        .where(VideoProgress.user_id == student.id)
        .order_by(VideoProgress.updated_at.desc())
        .limit(10)
    )
    recent = recent_result.scalars().all()

    # Resolve video titles for recent activity
    video_ids = [r.video_id for r in recent]
    if video_ids:
        videos_result = await db.execute(select(Video).where(Video.id.in_(video_ids)))
        videos_map = {v.id: v.title for v in videos_result.scalars().all()}
    else:
        videos_map = {}

    recent_activity = []
    for r in recent:
        recent_activity.append({
            "video_title": videos_map.get(r.video_id, "Unknown"),
            "attendance_type": r.attendance_type.value,
            "is_completed": r.is_completed,
            "updated_at": r.updated_at,
        })

    return templates.TemplateResponse("mentor_student_detail.html", {
        "request": request,
        "student": student,
        "videos_completed": len(completed),
        "videos_in_progress": len(in_progress),
        "videos_total": total_videos,
        "live_count": live_count,
        "completion_pct": completion_pct,
        "semesters": semesters_data,
        "recent_activity": recent_activity,
    })


# ── Logout ───────────────────────────────────────────────────────────

@router.get("/logout")
async def logout(session: str | None = Cookie(None)):
    if session and session in _sessions:
        del _sessions[session]
    response = RedirectResponse(url="/pages/login", status_code=303)
    response.delete_cookie("session")
    return response
