from fastapi import HTTPException
from prisma import Prisma
from typing import Optional
from app.schemas.order_schema import  OrderStatusUpdateModel
from prisma.errors import RecordNotFoundError
from app.errors.custom_exceptions import BadRequestException
from app.core.rabbit import Broker

async def get_all_order_controller(
    order_id: Optional[str],          
    user_id: Optional[str],           
    db: Prisma
):
    try:
        filters = {}
        if order_id:
            filters["id"] = order_id
        if user_id:
            filters["user_id"] = user_id

        order_groups = await db.ordergroup.find_many(
            where=filters if filters else None,
            include={
                "orders": {
                    "include": {
                        "restaurant": True,
                        "items": {
                            "include": {
                                "menu_item": True
                            }
                        }
                    }
                }
            }
        )

        if not order_groups:
            raise HTTPException(status_code=404, detail="No orders found matching the criteria")

        return {
            "status": True,
            "message": "Orders retrieved successfully",
            "data": order_groups
        }

    except HTTPException:
        raise
    except Exception as e:
        print("[restaurant-service][get-all-orders]: ", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
async def update_order_status_controller(order_id: str, status: OrderStatusUpdateModel, db: Prisma):
    """
    Update the status of an order (restaurant or delivery agent).
    Auto-assigns a delivery agent if status becomes ACCEPTED.
    """ 
    order = await db.ordergroup.find_unique(where={"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "PENDING":
        raise BadRequestException("order status can only be update where status is pending!")
    
    async with db.tx() as tx:
            
        await tx.order.update_many(
            where={"order_group_id": order_id},
            data={"status": status}
        )

        updated_order_group = await tx.ordergroup.update(
            where={"id": order_id},
            data={"status": status},
            include={"orders": True}  
        )
        
    if status == "CONFIRMED":
            payload = {
            "order_id": str(order_id)
            }
            await Broker.publish("assign-dilvery-agent-queue",payload)
            return {
            "status": True,
            "message": f"Order group & child orders updated to {status} and queued for assign the agent to agent service.",
            "data": updated_order_group
            }   

    return {
        "status": True,
        "message": f"Order group & child orders updated to {status} and queued for assign the agent to agent service.",
        "data": updated_order_group
    } 
