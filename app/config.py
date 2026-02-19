from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://jca:jca@localhost:5432/jca"

    # Firebase
    firebase_project_id: str = ""
    firebase_credentials_path: str = ""

    # GCS
    gcs_video_bucket: str = "jca-videos"
    gcs_resource_bucket: str = "jca-resources"

    # Cloud Tasks
    cloud_tasks_project: str = ""
    cloud_tasks_location: str = "us-central1"
    cloud_tasks_queue: str = "questionnaire-dispatch"

    # App
    app_base_url: str = "http://localhost:8000"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
