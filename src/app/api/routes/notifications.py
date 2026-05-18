from typing import List

from fastapi import APIRouter

from app.schemas.notification import NotificationOut
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/notifications")


@router.get("", response_model=List[NotificationOut])
async def get_notifications() -> List[NotificationOut]:
    service = NotificationsService()
    return await service.list_notifications()


@router.get("/{id}", response_model=List[NotificationOut])
async def get_notification_by_id(id: str) -> List[NotificationOut]:
    service = NotificationsService()
    return await service.get_notification_by_id(id)
