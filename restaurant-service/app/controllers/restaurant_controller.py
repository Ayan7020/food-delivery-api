from app.schemas.restaurant_schema import RestaurantInsertionModel, RestaurantUpdateModel
from prisma import Prisma
from fastapi import HTTPException
from app.errors.custom_exceptions import BadRequestException
from datetime import time


async def add_restaurant_controller(data: RestaurantInsertionModel, db: Prisma):
    restaurant_response = await db.restaurant.create(
        data={
            "name": data.name,
            "description": data.description,
            "opening_time": data.opening_time.strftime("%H:%M"),
            "closing_time": data.closing_time.strftime("%H:%M"),
            "menu": {
                "create": [
                    {
                        "name": item.name,
                        "description": item.description,
                        "price": item.price,
                        "type": item.type
                    } for item in data.menu
                ]
            },
        },
        include={
            "menu": True
        }
    )
    return {
        "status": True,
        "message": "Restaurant Created Successfully",
        "data": {
            "restaurant_id": restaurant_response.id,
            "menu_ids": [m.id for m in restaurant_response.menu]
        }
    }


async def get_restaurant_data_controller(hour: int, db: Prisma):
    if hour is None or hour < 0 or hour > 23:
        raise BadRequestException(detail="Please provide a valid hour between 0–23")
    given_time = time(hour, 0)

    restaurants = await db.restaurant.find_many(
        where={
            "status": "ONLINE",
            "opening_time": {"lte": given_time.strftime("%H:%M")},
            "closing_time": {"gte": given_time.strftime("%H:%M")}
        },
        include={
            "menu": True
        }
    )
    return {
        "status": True,
        "message": "Available restaurants retrieved successfully",
        "data": {
            "count": len(restaurants),
            "restaurant_data": restaurants
        }
    }


async def update_restaurant_controller(restaurant_id: str, data: RestaurantUpdateModel, db: Prisma):
    async with db.tx() as transaction:
        restaurant_data = data.model_dump(exclude_unset=True, exclude={"menu"})
        if "opening_time" in restaurant_data and isinstance(restaurant_data["opening_time"], time):
            restaurant_data["opening_time"] = restaurant_data["opening_time"].strftime(
                "%H:%M")
        if "closing_time" in restaurant_data and isinstance(restaurant_data["closing_time"], time):
            restaurant_data["closing_time"] = restaurant_data["closing_time"].strftime(
                "%H:%M")

        if restaurant_data:
            restaurant_update = await transaction.restaurant.update(
                where={"id": restaurant_id},
                data=restaurant_data
            )
            if not restaurant_update:
                raise HTTPException(
                    status_code=404, detail="Restaurant not found.")

        if data.menu:
            for item in data.menu:
                item_data = item.model_dump(exclude_unset=True)
                if item_data.get("delete") and item_data.get("id"):
                    await transaction.menuitem.delete(where={"id": item_data["id"]})
                elif item_data.get("id"):
                    await transaction.menuitem.update(
                        where={"id": item_data["id"]},
                        data={k: v for k, v in item_data.items() if k not in {
                            "id", "delete"}}
                    )
                else:
                    await transaction.menuitem.create(
                        data={
                            "name": item_data["name"],
                            "description": item_data.get("description"),
                            "price": item_data["price"],
                            "type": item_data["type"],
                            "restaurant_id": restaurant_id
                        }
                    )
    return {
        "status": True,
        "message": "Restaurant and menu updated successfully"
    }
