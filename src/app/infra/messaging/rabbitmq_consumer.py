from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

import aio_pika
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.notification import NotificationCreated, NotificationDeleted, NotificationKind
from app.services.notifications_service import NotificationsService

logger = logging.getLogger(__name__)

_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[aio_pika.abc.AbstractRobustChannel] = None
_consume_task: Optional[asyncio.Task[None]] = None


async def start_rabbitmq_consumer() -> None:
    global _connection, _channel, _consume_task

    if _consume_task is not None and not _consume_task.done():
        logger.info("RabbitMQ consumer already running")
        return

    logger.info(
        "Starting RabbitMQ consumers (uri=%s)",
        settings.rabbitmq_uri,
    )
    _connection = await aio_pika.connect_robust(settings.rabbitmq_uri)
    _channel = await _connection.channel()

    async def _consume_employee_events(
        *,
        exchange_name: str,
        queue_name: str,
        kind: NotificationKind,
    ) -> None:
        assert _channel is not None

        queue = await _channel.declare_queue(queue_name, durable=True)

        onboarding_exchange = await _channel.declare_exchange(settings.rabbitmq_onboarding_exchange, aio_pika.ExchangeType.FANOUT, durable=True)
        offboarding_exchange = await _channel.declare_exchange(settings.rabbitmq_offboarding_exchange, aio_pika.ExchangeType.FANOUT, durable=True)

        await queue.bind(onboarding_exchange)
        await queue.bind(offboarding_exchange)

        logger.info(
            "RabbitMQ exchange/queue ready (exchange=%s, queue=%s)",
            exchange_name,
            queue_name,
        )

        async def _on_message(message: aio_pika.IncomingMessage) -> None:
            async with message.process(ignore_processed=True):
                try:
                    raw_body = message.body
                    body_preview = raw_body[:500].decode("utf-8", errors="replace")
                    logger.info(
                        "RabbitMQ message received (exchange=%s, queue=%s, delivery_tag=%s, body_preview=%s)",
                        exchange_name,
                        queue_name,
                        message.delivery_tag,
                        body_preview,
                    )

                    payload = json.loads(raw_body.decode("utf-8"))

                    event_type = payload["eventType"]
                    data = payload["data"]

                    if event_type == "EMPLOYEE_CREATED":
                        kind = NotificationKind.BIENVENIDA
                        event = NotificationCreated.model_validate(data)
                        logger.info(
                            "[NOTIFICACIÓN] Tipo: %s | Para %s  | Mensaje:  Bienvenido/a %s",
                            event_type,
                            data.get("email"),
                            data.get("name"),
                        )
                    elif event_type == "EMPLOYEE_DELETED":
                        kind = NotificationKind.DESVINCULACION
                        event = NotificationDeleted.model_validate(data)
                        logger.info(
                            "[NOTIFICACIÓN] Tipo: %s | Para %s  | Mensaje: Hola %s, su cuenta ha sido deshabilitada",
                            event_type,
                            data.get("email"),
                            data.get("name"),
                        )
                    else:
                        logger.warning(f"Unknown eventType: {event_type}")
                        return

                    service = NotificationsService()
                    await service.create_from_employee_event(event, kind=kind)

                    logger.info(
                        "RabbitMQ message processed successfully (exchange=%s, queue=%s, delivery_tag=%s)",
                        exchange_name,
                        queue_name,
                        message.delivery_tag,
                    )

                except (json.JSONDecodeError, UnicodeDecodeError, ValidationError):
                    await message.reject(requeue=False)
                    logger.warning(
                        "RabbitMQ message rejected (invalid payload) (exchange=%s, queue=%s, delivery_tag=%s)",
                        exchange_name,
                        queue_name,
                        message.delivery_tag,
                    )
                    return
                except Exception:
                    await message.nack(requeue=True)
                    logger.exception(
                        "RabbitMQ message nacked (will requeue) (exchange=%s, queue=%s, delivery_tag=%s)",
                        exchange_name,
                        queue_name,
                        message.delivery_tag,
                    )
                    return

        await queue.consume(_on_message, no_ack=False)
        logger.info(
            "RabbitMQ consumer started (exchange=%s, queue=%s)", exchange_name, queue_name
        )

    await _consume_employee_events(
        exchange_name=settings.rabbitmq_onboarding_exchange,
        queue_name=settings.rabbitmq_onboarding_queue,
        kind=NotificationKind.BIENVENIDA,
    )
    await _consume_employee_events(
        exchange_name=settings.rabbitmq_offboarding_exchange,
        queue_name=settings.rabbitmq_onboarding_queue,
        kind=NotificationKind.DESVINCULACION,
    )

    async def _keep_alive() -> None:
        while True:
            await asyncio.sleep(3600)

    _consume_task = asyncio.create_task(_keep_alive())


async def stop_rabbitmq_consumer() -> None:
    global _connection, _channel, _consume_task

    logger.info("Stopping RabbitMQ consumer")
    if _consume_task is not None:
        _consume_task.cancel()
        try:
            await _consume_task
        except asyncio.CancelledError:
            pass
        _consume_task = None

    if _channel is not None:
        await _channel.close()
        _channel = None

    if _connection is not None:
        await _connection.close()
        _connection = None

    logger.info("RabbitMQ consumer stopped")
