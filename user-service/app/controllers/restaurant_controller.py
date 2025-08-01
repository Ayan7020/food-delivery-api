import os
import httpx
import json
from app.errors.custom_exceptions import HTTPException , NotFoundException 
from app.core.redis import redis_client   
from app.core.rabbit import Broker
from app.schema.order_schema import OrderPlacementModel
from app.schema.rating_schema import RatingModel
from datetime import datetime
import uuid 
from prisma import Prisma
from app.core.config import settings 

CACHE_TTL = 15    

async def get_available_restaurant_controller(hour: int):  

    cache_key = f"available_restaurants:{hour}" 
    
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        print("Serving from cache")
        return json.loads(cached_data)

    async with httpx.AsyncClient(timeout=7.0) as client: 
        response = await client.get(
            f"{settings.RESTAURANT_SERVICE_URL}/restaurants/available",
            params={"hour": hour}
        )
 
    data = response.json() 
    
    await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL)

    return data
 


async def place_order_available_restaurant_controller(data: OrderPlacementModel,db: Prisma): 
    placed_at = datetime.utcnow().isoformat()
    current_hour = datetime.utcnow().hour
    
    async with httpx.AsyncClient(timeout=7.0) as client: 
        response = await client.get(
            f"{settings.RESTAURANT_SERVICE_URL}/restaurants/available",
            params={"hour": current_hour}
        )
        
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    available_restaurants = response.json()
    
    available_rest_map = {r["id"]: r for r in available_restaurants["data"]["restaurant_data"]}
    
    for restaurant in data.restaurants:
        if str(restaurant.restaurant_id) not in available_rest_map:
            raise NotFoundException(detail=f"Restaurant {restaurant.restaurant_id} is not available")
        
        menu_ids = {m["id"] for m in available_rest_map[str(restaurant.restaurant_id)]["menu"]}
        
        for item in restaurant.items:
            if str(item.menu_item_id) not in menu_ids:
                raise NotFoundException(detail=f"Menu item {item.menu_item_id} not available in restaurant {restaurant.restaurant_id}")   
        
    order_id = str(uuid.uuid4())
    await db.userorder.create(
        data = {
            "user_id": str(data.user_id),
            "order_id": order_id
        }
    )
    payload = {
        "order_id": order_id,
        "user_id": str(data.user_id),
        "restaurants": [r.model_dump() for r in data.restaurants],
        "status": "PENDING",
        "placed_at": placed_at           
    }
    
    
    await Broker.publish("place-order-queue",payload)
    
    return {
        "order_id": order_id,
        "status": "PENDING",
        "placed_at": placed_at,
        "message": "Your order has been placed and is pending confirmation."
    }
          