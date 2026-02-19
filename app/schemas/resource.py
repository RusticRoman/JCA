import uuid
from datetime import datetime

from pydantic import BaseModel


class ResourceResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    category: str
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ResourceDownloadResponse(BaseModel):
    download_url: str
