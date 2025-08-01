from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.controllers.rating_contoller import  ratings_controller
from app.schema.rating_schema import RatingModel
from app.core.db import db

router = APIRouter() 


@router.post("/dilvery-agent-rating")
async def dilvery_agent_rating(data: RatingModel):
    """
    Submit a rating for a delivery agent and order.

    - Requires a valid order ID.
    - Fetches delivery status from the Agent Service (with Redis caching to reduce repeated calls) cache for 1 minute.
    - Only allows submitting ratings for orders with the status "DELIVERED".
    - Publishes the rating data to RabbitMQ for further processing by other services.
    """
    return await ratings_controller(data,db)