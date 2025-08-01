from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class MenuSelectionModel(BaseModel):
    menu_item_id: UUID = Field(..., description="ID of the menu item")
    quantity: int = Field(..., gt=0, description="Quantity of the menu item")

class RestaurantOrderModel(BaseModel):
    restaurant_id: UUID = Field(..., description="ID of the restaurant")
    items: List[MenuSelectionModel] = Field(..., description="List of menu items with quantities")

class OrderPlacementModel(BaseModel):
    user_id: UUID = Field(..., description="ID of the user placing the order")
    restaurants: List[RestaurantOrderModel] = Field(..., description="List of restaurants with their menu selections")
