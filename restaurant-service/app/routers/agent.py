from fastapi import APIRouter, Query, HTTPException
from app.core.db import db
from app.controllers.agent_controller import auto_assign_agent_controller

router = APIRouter()

@router.post("/assign-agent")
async def assign_agent(order_id: str = Query(..., description="The ID of the order to assign an agent for")):
    """
    Assign a delivery agent to an order.

    - Checks if the order exists and is not already assigned.
    - Publishes a message to the agent assignment queue.
    - Marks the order as assigned in the database.

    Args:
        order_id (str): The unique ID of the order.

    Returns:
        dict: Success message indicating the order has been queued for agent assignment.

    Raises:
        HTTPException:
            - 404 if the order does not exist or is already assigned.
            - 500 for unexpected server errors.
    """     
    return await auto_assign_agent_controller(order_id, db)