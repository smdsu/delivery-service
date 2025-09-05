import datetime
import logging
import json
from typing import Optional, Dict, Any
import aio_pika
from ..core.mq_settings import mq_settings

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    def __init__(self) -> None:
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self._is_connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def _setup_exchanges_and_queues(self):
        self.exchange = await self.channel.declare_exchange(
            name="packages_exchange", type=aio_pika.ExchangeType.DIRECT, durable=True
        )

        package_queue = await self.channel.declare_queue(
            name="package_processing",
            durable=True,
            arguments={
                "x-message-ttl": 3600000,  # 1 hour
                "x-dead-letter-exchange": "packages_dlx",
                "x-dead-letter-routing-key": "failed_packages",
            },
        )
        await package_queue.bind(exchange=self.exchange, routing_key="package.process")

        dlx_exchange = await self.channel.declare_exchange(
            name="packages_dlx", type=aio_pika.ExchangeType.DIRECT, durable=True
        )

        dead_letter_queue = await self.channel.declare_queue(
            name="failed_packages",
            durable=True,
        )
        await dead_letter_queue.bind(
            exchange=dlx_exchange,
            routing_key="failed_packages",
        )

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                mq_settings.get_mq_url(),
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            await self._setup_exchanges_and_queues()
            self._is_connected = True
        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")
            raise

    async def publish_package(self, package_data: Dict[str, Any]) -> bool:
        if not self._is_connected:
            await self.connect()

        try:
            message_body = json.dumps(package_data, ensure_ascii=False)

            message = aio_pika.Message(
                body=message_body.encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={
                    "content_type": "application/json",
                    "package_id": package_data["id"],
                    "created_at": package_data["created_at"],
                    "retry_count": 0,
                },
                priority=1,
                message_id=package_data["id"],
                expiration=3600000,  # 1 hour
            )

            await self.exchange.publish(  # type: ignore
                message=message,
                routing_key="package.process",
                mandatory=True,
                immediate=False,
            )

            logger.info(f"Package {package_data['id']} published to RabbitMQ")
            return True
        except Exception as e:
            logger.error(
                f"Error publishing package {package_data['id']} to RabbitMQ: {e}"
            )
            return False

    async def publish_with_confirmation(self, package_data: Dict[str, Any]) -> bool:
        if not self._is_connected:
            await self.connect()

        try:
            message_body = json.dumps(package_data, ensure_ascii=False)

            message = aio_pika.Message(
                body=message_body.encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                headers={
                    "content_type": "application/json",
                    "package_id": package_data["id"],
                    "created_at": datetime.datetime.now(),
                    "retry_count": 0,
                },
                priority=1,
                message_id=package_data["id"],
                expiration=3600000,  # 1 hour
            )

            result = await self.exchange.publish(  # type: ignore
                message=message,
                routing_key="package.process",
                mandatory=True,
            )

            if result:
                logger.info(
                    f"Package {package_data['id']} published to RabbitMQ with confirmation"
                )
                return True
            else:
                logger.error(
                    f"Package {package_data['id']} failed to publish to RabbitMQ with confirmation"
                )
                return False
        except Exception as e:
            logger.error(
                f"Error publishing package {package_data['id']} to RabbitMQ with confirmation: {e}"
            )
            return False

    async def close(self):
        if self._is_connected:
            await self.connection.close()
            self._is_connected = False


rabbitmq_producer = RabbitMQProducer()


async def ensure_connection():
    if not rabbitmq_producer._is_connected:
        await rabbitmq_producer.connect()


async def send_package_for_processing(package_data: Dict[str, Any]) -> bool:
    await ensure_connection()
    return await rabbitmq_producer.publish_with_confirmation(package_data)


async def close_connection():
    await rabbitmq_producer.close()
