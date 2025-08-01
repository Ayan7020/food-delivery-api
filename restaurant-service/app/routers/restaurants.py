from fastapi import APIRouter
from app.schemas.restaurant_schema import RestaurantInsertionModel,RestaurantUpdateModel 
from app.controllers.restaurant_controller import add_restaurant_controller , update_restaurant_controller , get_restaurant_data_controller
from app.core.db import db

router = APIRouter()

@router.post("/add-restaurant")
async def add_restaurant(data: RestaurantInsertionModel):
    """
    Create a new restaurant along with its menu items.
    """
    return await add_restaurant_controller(data,db)

@router.get("/restaurants/available")
async def get_available_restaurants(hour: int):
    return await get_restaurant_data_controller(hour, db)

@router.patch("/update-restaurants/{restaurant_id}")
async def update_menu(restaurant_id: str,data: RestaurantUpdateModel):
    """
    Update restaurant details & menu (add/update/delete items). If you dont gave the menu id it will create new menu for that restaurant_id
    Important -> you cannot update the rating field from here 
    """
    return await update_restaurant_controller(restaurant_id,data,db)
