import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import admin, assessments, auth_routes, beit_din, curriculum, dashboard, events, export, faq, health, pages, questionnaires, rabbi, resources, teacher, users, video_progress

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("jca")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Jewish Conversion Academy",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info("%s %s %d %.0fms", request.method, request.url.path, response.status_code, duration_ms)
        return response

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(health.router)
    app.include_router(auth_routes.router)
    app.include_router(users.router)
    app.include_router(curriculum.router)
    app.include_router(video_progress.router)
    app.include_router(assessments.router)
    app.include_router(dashboard.router)
    app.include_router(rabbi.router)
    app.include_router(teacher.router)
    app.include_router(beit_din.router)
    app.include_router(questionnaires.router)
    app.include_router(resources.router)
    app.include_router(events.router)
    app.include_router(faq.router)
    app.include_router(admin.router)
    app.include_router(export.router)
    app.include_router(pages.router)
    app.include_router(pages.root_router)

    return app


app = create_app()
