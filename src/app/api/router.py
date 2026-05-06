from fastapi import APIRouter

from app.api.routes.notifications import router as notifications_router

api_router = APIRouter()

api_router.include_router(notifications_router, tags=["notifications"])
