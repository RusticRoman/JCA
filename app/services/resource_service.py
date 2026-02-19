from app.gcp.storage import get_resource_url


def get_download_url(gcs_path: str) -> str:
    return get_resource_url(gcs_path)
