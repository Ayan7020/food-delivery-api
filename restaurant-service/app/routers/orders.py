from fastapi import APIRouter, Query
from app.controllers.order_controller import get_all_order_controller , update_order_status_controller
from app.schemas.order_schema import OrderStatusUpdateModel
from app.core.db import db

router = APIRouter()

@router.get("/orders")
async def get_orders(
    order_id: str | None = Query(None, description="OrderGroup ID (optional)"),
    user_id: str | None = Query(None, description="User ID (optional)")
):
    """
    Retrieve orders (OrderGroups) with optional filters by order_id or user_id.
    """
    return await get_all_order_controller(order_id, user_id, db)

@router.post("/change-order-status")
async def change_order_status(
    data: OrderStatusUpdateModel,
    order_id: str | None = Query(None, description="OrderGroup ID (optional)"),
):
    return await update_order_status_controller(order_id,data.status,db)