from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class NotificationKind(str, Enum):
    BIENVENIDA = "BIENVENIDA"
    DESVINCULACION = "DESVINCULACION"


class NotificationOut(BaseModel):
    id: str = Field(..., description="Notification id")
    kind: Optional[NotificationKind] = Field(default=None, description="Notification type")
    recipient: Optional[str] = None
    message: Optional[str] = None
    date_sent: Optional[datetime] = None
    employeeId: Optional[str] = None


class NotificationCreated(BaseModel):
    id: int
    name: str
    email: str
    departmentId: int
    hiringDate: datetime

class NotificationDeleted(BaseModel):
    id: int
    name: str
    email: str


