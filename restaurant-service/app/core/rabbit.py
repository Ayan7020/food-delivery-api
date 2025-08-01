import aio_pika
from app.core.config import settings
import json 


class RabbitMQBroker:
    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None

    async def connect(self):
        """"""
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()

    async def publish(self, queue: str, message: dict):
        """"""
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode(),
                             delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=queue
        )

    async def consume(self, queue_name, callback):
        queue = await self.channel.declare_queue(queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body.decode())
                        await callback(payload)
                    except Exception as e:
                        print(
                            f"[RabbitMQ][consume] Error processing message: {e}")

    async def consume_fan_out(self, exchange_name: str, callback):
        exchange = await self.channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.FANOUT
        )
        queue = await self.channel.declare_queue("", exclusive=True)
        await queue.bind(exchange)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        await callback(data)
                    except Exception as e:
                        print(f"Error processing message: {e}")


Broker = RabbitMQBroker()
