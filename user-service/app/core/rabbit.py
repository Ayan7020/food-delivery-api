import aio_pika 
import os 
import json 
from app.core.config import settings

class RabbitMQBroker:
    def __init__(self):
        self.connection: aio_pika.RobustConnection | None  = None
        self.channel: aio_pika.RobustChannel | None  = None
        
    async def connect(self):
        """"""
        self.connection = await aio_pika.connect_robust(settings.RABBIT_MQ)
        self.channel = await self.connection.channel()
        
    async def publish(self,queue: str,message: dict):
        """"""
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message, default=str).encode(),delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=queue
        )
    async def publish_fanout(self,exchange_name: str, message: dict):
        exchange = await self.channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.FANOUT
        )
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json"
            ),
            routing_key=""  
        )
        
Broker = RabbitMQBroker()