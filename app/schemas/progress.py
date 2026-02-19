import uuid

from pydantic import BaseModel

from app.models.progress import AttendanceType


class SyncProgressRequest(BaseModel):
    video_id: uuid.UUID
    last_position_seconds: int
    total_duration_seconds: int
    attendance_type: AttendanceType = AttendanceType.RECORDED


class SyncProgressResponse(BaseModel):
    video_id: uuid.UUID
    last_position_seconds: int
    total_duration_seconds: int
    is_completed: bool
    attendance_type: AttendanceType

    model_config = {"from_attributes": True}


class VideoStateResponse(BaseModel):
    video_id: uuid.UUID
    last_position_seconds: int
    total_duration_seconds: int
    is_completed: bool
    attendance_type: AttendanceType

    model_config = {"from_attributes": True}
