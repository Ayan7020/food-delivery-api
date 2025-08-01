from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.controllers.restaurant_controller import get_available_restaurant_controller , place_order_available_restaurant_controller
from app.schema.order_schema import OrderPlacementModel
from app.core.db import db

router = APIRouter() 


@router.get("/get-available-restaurants")
async def get_available_restaurant(hour: int):
    """The hour is range from 0 to 23"""
    return await get_available_restaurant_controller(hour)

@router.post("/place-order")
async def place_order(data: OrderPlacementModel):
    """It will place the order and publish your order to queue for the restaurant services."""
    return await place_order_available_restaurant_controller(data,db)
