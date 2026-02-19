from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import assessments, auth_routes, beit_din, curriculum, dashboard, events, faq, health, pages, questionnaires, rabbi, resources, teacher, users, video_progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
    app.include_router(pages.router)
    app.include_router(pages.root_router)

    return app


app = create_app()
