from app.schema.rating_schema import RatingModel
from prisma import Prisma
from app.core.rabbit import Broker
from fastapi import HTTPException
from app.errors.custom_exceptions import BadRequestException
import httpx
import os 
from app.core.redis import redis_client
import json
from app.core.config import settings 
 

CACHE_EXPIRY = 60  

async def ratings_controller(data: RatingModel, db: Prisma):
    order = await db.userorder.find_first(where={"order_id": data.order_id})
    if not order:
        raise BadRequestException("Order does not exist. Cannot create a rating.")

    datauser = await db.userorder.find_first(
        where={"order_id": order.order_id}
    )
 
    cache_key = f"delivery_status:{data.order_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        service_data = json.loads(cached_data)
    else: 
        async with httpx.AsyncClient(timeout=7.0) as client:
            response = await client.get(
                f"{settings.AGENT_SERVICE_URL}/get-delivery-status",
                params={"order_id": data.order_id}
            )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="You cannot place rating right now!")
        
        service_data = response.json() 
        await redis_client.setex(cache_key, CACHE_EXPIRY, json.dumps(service_data))

    response_status = service_data["data"]["status"]

    if response_status != "DELIVERED":
        raise BadRequestException("You cannot give a rating before the order is delivered.")

    rating = await db.userrating.create(
        data={
            "user_order_id": datauser.id,
            "agent_rating": data.agent_rating,
            "order_rating": data.order_rating
        }
    )
    payload = {
        "order_id": data.order_id,
        "order_rating": data.order_rating,
        "agent_rating": data.agent_rating
    }

    await Broker.publish_fanout("ratings-exchange", payload)
    return {
        "success": True,
        "message": "Rating submitted successfully.",
        "data": rating
    }
