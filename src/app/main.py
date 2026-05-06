import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.core.errors import register_exception_handlers
from app.db.mongo import close_mongo, connect_mongo
from app.infra.messaging.rabbitmq_consumer import stop_rabbitmq_consumer, start_rabbitmq_consumer

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    app = FastAPI(title="ms-notifications", version="1.0.0")

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.on_event("startup")
    async def _startup() -> None:
        await connect_mongo()
        await start_rabbitmq_consumer()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await stop_rabbitmq_consumer()
        await close_mongo()

    return app


app = create_app()
