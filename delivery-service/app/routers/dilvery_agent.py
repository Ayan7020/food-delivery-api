from fastapi import APIRouter
from app.schemas.dilvery_agent_schema import DilveryAgentModel, UpdateDilveryStatusModel
from app.core.db import db
from app.controllers.dilvery_agent_controller import add_dilvery_agent_controller, update_dilvery_status_controller , get_dilvery_status_controller

router = APIRouter()


@router.post("/add-dilvery-agent")
async def add_dilvery_agent(data: DilveryAgentModel):
    """
    (TESTING PURPOSE ONLY)
    Add a new delivery agent to the system.

    This endpoint registers a new delivery agent with the provided details.
    Useful when onboarding new agents who will handle deliveries.
    """
    return await add_dilvery_agent_controller(data, db)


@router.patch("/update-dilvery-status")
async def update_dilvery_status(data: UpdateDilveryStatusModel):
    """
    Update the status of a delivery assignment.

    Use this endpoint to change the status of an order (e.g., PENDING, IN_PROGRESS, DELIVERED, or CANCELLED).
    If an order is marked as DELIVERED or CANCELLED, the assigned delivery agent will automatically become AVAILABLE again.
    """
    return await update_dilvery_status_controller(data.order_id, data.status, db)


@router.get("/get-all-dilvery-agent")
async def get_all_dilvery():
    """
    (TESTING PURPOSE ONLY)
    Get a list of all delivery agents.

    This returns every delivery agent along with their current assignments.
    Helpful for monitoring availability and active deliveries.
    """
    return await db.dilveryagent.find_many(
        where={},
        include={
            "assignments": True
        }
    )

@router.get("/get-delivery-status")
async def get_delivery(order_id: str):
    """Get delivery status by order id"""
    return await  get_dilvery_status_controller(order_id,db)