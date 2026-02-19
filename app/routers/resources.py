import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.resource import Resource
from app.models.user import User
from app.schemas.resource import ResourceDownloadResponse, ResourceResponse
from app.services.resource_service import get_download_url

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=list[ResourceResponse])
async def list_resources(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resource).order_by(Resource.created_at.desc()).offset(skip).limit(min(limit, 100))
    )
    return result.scalars().all()


@router.get("/{resource_id}/download", response_model=ResourceDownloadResponse)
async def download_resource(
    resource_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    url = get_download_url(resource.gcs_path)
    return ResourceDownloadResponse(download_url=url)
