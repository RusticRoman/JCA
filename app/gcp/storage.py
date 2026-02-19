import datetime

from app.config import settings


def generate_signed_url(bucket_name: str, blob_path: str, expiration_minutes: int = 60) -> str:
    """Generate a signed URL for a GCS object."""
    if not settings.firebase_credentials_path:
        # Development mode - return a placeholder URL
        return f"https://storage.googleapis.com/{bucket_name}/{blob_path}?dev=true"

    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=expiration_minutes),
        method="GET",
    )
    return url


def get_video_url(gcs_path: str) -> str:
    return generate_signed_url(settings.gcs_video_bucket, gcs_path)


def get_resource_url(gcs_path: str) -> str:
    return generate_signed_url(settings.gcs_resource_bucket, gcs_path)
