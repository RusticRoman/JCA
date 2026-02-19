import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def create_task(url: str, payload: dict, delay_seconds: int = 0) -> str:
    """Create a Cloud Tasks task. Returns task name."""
    if not settings.cloud_tasks_project:
        return f"dev-task-{url}"

    from google.cloud import tasks_v2
    from google.protobuf import timestamp_pb2
    import datetime

    try:
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(
            settings.cloud_tasks_project,
            settings.cloud_tasks_location,
            settings.cloud_tasks_queue,
        )

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
            }
        }

        if delay_seconds > 0:
            d = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=delay_seconds)
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)
            task["schedule_time"] = timestamp

        response = client.create_task(parent=parent, task=task)
        return response.name
    except Exception:
        logger.exception("Failed to create Cloud Task for %s", url)
        raise
