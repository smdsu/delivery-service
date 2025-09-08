from decimal import Decimal
import asyncio
import logging
import aio_pika
import json
from typing import Any, Dict, Optional
from uuid import UUID

from src.core.mq_settings import mq_settings
from src.services.currency import currency_service
from src.services.package_worker import package_worker_service

logger = logging.getLogger(__name__)


class PackageConsumer:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None
        self._consuming = False

        self.max_retries = 3
        self.retry_delay = 5

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                mq_settings.get_mq_url(),
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            self.queue = await self.channel.declare_queue(
                name="package_processing",
                durable=True,
                arguments={
                    "x-message-ttl": 3600000,  # 1 hour
                    "x-dead-letter-exchange": "packages_dlx",
                    "x-dead-letter-routing-key": "failed_packages",
                },
            )
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {e}")
            raise

    def calculate_delivery_cost(
        self, weight: float, value_of_contents_usd: Decimal, usd_rate: Decimal
    ) -> Decimal:
        base_cost_usd = Decimal(weight * 0.5) + Decimal(
            value_of_contents_usd
        ) * Decimal(0.01)
        delivery_cost_rub: Decimal = Decimal(base_cost_usd * usd_rate)

        return delivery_cost_rub

    async def process_package_message(self, message_data: Dict[str, Any]) -> bool:
        package_id = UUID(message_data["id"])

        try:
            usd_rate = await currency_service.get_usd_rate()

            delivery_cost = self.calculate_delivery_cost(
                weight=float(message_data["weight"]),
                value_of_contents_usd=Decimal(
                    str(message_data["value_of_contents_usd"])
                ),
                usd_rate=usd_rate,
            )
            updated_package = await package_worker_service.update_package_delivery_cost(
                package_id, delivery_cost
            )

            if updated_package:
                logger.info(
                    "Successfully updated delivery cost for package %s", package_id
                )
                return True
            else:
                logger.error("Package %s not found in database", package_id)
                return False

        except ValueError as e:
            logger.error("Invalid data in message for package %s: %s", package_id, e)
            return False
        except Exception as e:
            logger.error("Failed to process package %s: %s", package_id, e)
            return False

    async def handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process(requeue=False):
            try:
                message_data = json.loads(message.body.decode("utf-8"))
                package_id = message_data["id"]

                logger.info(f"Message received for package {package_id}")

                retry_count = 0
                if message.headers:
                    retry_count = message.headers.get("retry_count", 0)  # type: ignore

                if retry_count >= self.max_retries:
                    logger.error(
                        f"Too much retries for package {package_id}; Send to DLX"
                    )
                    return False

                success = await self.process_package_message(message_data=message_data)

                if success:
                    logger.info(f"Message for package {package_id} processed")
                    return True
                else:
                    logger.warning(
                        f"Error while processing package {package_id},"
                        f"retry {retry_count + 1}/{self.max_retries}"
                    )

                    new_headers = dict(message.headers) if message.headers else {}
                    new_headers["retry_count"] = retry_count + 1

                    await asyncio.sleep(self.retry_delay * (retry_count + 1))

                    await self.channel.default_exchange.publish(  # type: ignore
                        aio_pika.Message(
                            body=message.body,
                            headers=new_headers,
                            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                            priority=1,
                            message_id=package_id,
                            expiration=3600000,  # 1 hour
                        ),
                        routing_key=self.queue.name,  # type: ignore
                    )

                    return True
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return False
            except Exception as e:
                logger.critical(f"Unexpected error while processing message: {e}")
                raise

    async def start_consuming(self):
        if not self.connection:
            await self.connect()

        async def message_handler(message: aio_pika.IncomingMessage):
            try:
                await self.handle_message(message=message)
            except aio_pika.exceptions.MessageProcessError:
                pass
            except Exception as e:
                logger.critical(f"Critical processing error: {e}")

        consumer_tag = await self.queue.consume(callback=message_handler, no_ack=False)

        self._consuming = True

        try:
            while self._consuming:
                await asyncio.sleep(1)
        except KeyboardInterrupt as ki:
            logger.info(ki)
        finally:
            await self.queue.cancel(consumer_tag)
            await self.close()

    async def stop_consuming(self):
        self._consuming = False

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


async def main():
    consumer = PackageConsumer()

    try:
        await consumer.start_consuming()
    except Exception as e:
        logger.critical(f"Critical worker error: {e}")
    finally:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
