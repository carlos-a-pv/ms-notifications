from datetime import datetime, timezone
from typing import List

from app.repositories.notifications_repository import NotificationsRepository
from app.schemas.notification import NotificationCreated, NotificationDeleted, NotificationKind, NotificationOut


class NotificationsService:
    def __init__(self) -> None:
        self._repo = NotificationsRepository()

    async def list_notifications(self) -> List[NotificationOut]:
        items = await self._repo.list_notifications()
        return [NotificationOut(**item) for item in items]

    async def get_notification_by_id(self, notification_id: str) -> NotificationOut:
        item = await self._repo.get_by_id(notification_id)
        return NotificationOut(**item)

    async def create_from_employee_event(
        self, event: NotificationCreated | NotificationDeleted, *, kind: NotificationKind
    ) -> None:
        now = datetime.now(timezone.utc)
        if kind == NotificationKind.BIENVENIDA:
            message = f"Bienvenido/a {event.name}"
        else:
            message = f"El empleado {event.name} ha sido desvinculado"

        doc = {
            "kind": kind.value,
            "recipient": event.email,
            "message": message,
            "date_sent": now,
            "employeeId": str(event.id),
            "employeeName": event.name,
        }

        await self._repo.create(doc)
