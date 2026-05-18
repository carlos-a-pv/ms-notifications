from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.errors import APIError
from app.db.mongo import get_db


class NotificationsRepository:
    def __init__(self) -> None:
        self._collection = get_db()["notifications"]

    async def list_notifications(self, *, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self._collection.find({}).sort("_id", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._map_doc(doc) for doc in docs]

    async def get_by_id(self, notification_id: str) -> List[Dict[str, Any]]:
        docs = await self._collection.find({"employeeId": notification_id}).to_list(length=100)
        if not docs:
            raise APIError(
                "Notification not found",
                status_code=404,
                code="not_found",
                details={"employeeId": notification_id},
            )
        return [self._map_doc(doc) for doc in docs]

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self._collection.insert_one(dict(data))
        doc = await self._collection.find_one({"_id": result.inserted_id})
        if doc is None:
            raise APIError(
                "Notification could not be created",
                status_code=500,
                code="create_failed",
                details={},
            )
        return self._map_doc(doc)

    def _map_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        mapped = dict(doc)
        mapped["id"] = str(mapped.pop("_id"))
        return mapped
