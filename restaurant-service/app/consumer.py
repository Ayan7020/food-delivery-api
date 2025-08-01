from app.core.db import db
from datetime import datetime
import uuid

async def process_order(message: dict):
    """
    Process an incoming order message: create OrderGroup, Orders, and OrderItems.
    """
    try:
        order_group_id = message["order_id"]    
        user_id = message["user_id"]
        placed_at = datetime.fromisoformat(message["placed_at"])
        status = message["status"]
        restaurants = message["restaurants"]
 
        await db.ordergroup.create(
            data={
                "id": order_group_id,
                "user_id": user_id,
                "status": status,
                "placed_at": placed_at
            }
        )
 
        for restaurant in restaurants: 
            restaurant_id = restaurant["restaurant_id"]
            items = restaurant["items"]

            order_id = str(uuid.uuid4())  
 
            await db.order.create(
                data={
                    "id": order_id,
                    "user_id": user_id,
                    "status": message["status"],
                    "order_group_id": order_group_id,
                    "restaurant_id": restaurant_id
                }
            )
 
            menu_item_ids = [item["menu_item_id"] for item in items]
            menu_items = await db.menuitem.find_many(
                where={"id": {"in": menu_item_ids}}
            )
            price_map = {m.id: m.price for m in menu_items}
 
            order_items_data = [
                {
                    "order_id": order_id,
                    "menu_item_id": item["menu_item_id"],
                    "quantity": item["quantity"],
                    "price": price_map.get(item["menu_item_id"], 0.0)   
                }
                for item in items
            ]
 
            await db.orderitem.create_many(data=order_items_data)

        print(f"[Consumer] OrderGroup {order_group_id} processed successfully.")

    except Exception as e:
        print(f"[Consumer] Failed to process order: {e}")
        
async def process_order_rating(message: dict):
    """
    Process an incoming order message: create OrderGroup, Orders, and OrderItems.
    """
    try:
        order_id = message["order_id"]
        await db.ordergroup.update(
            where={
                "id": order_id
            },
            data = {
                "rating": message["order_rating"]
            }
        )
        print(f"[Consumer] OrderGroup rating of {order_id} processed successfully.")

    except Exception as e:
        print(f"[Consumer] Failed to process order rating: {e}")