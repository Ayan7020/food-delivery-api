from prisma import Prisma
from app.core.rabbit import Broker
from fastapi import HTTPException

async def auto_assign_agent_controller(order_id: str,db: Prisma):
    """"""
    try:
        order_info = await db.ordergroup.find_first(
            where={
                "id": order_id,
                "agent_assign": False
            }
        )
        if not order_info:
            raise HTTPException(status_code=404, detail="Order not found or already assigned.")
        
        payload = {
            "order_id": str(order_id)
        }
        
        Broker.publish("assign-dilvery-agent-queue",payload)
        await db.ordergroup.update(
            where={"id": order_id},
            data={"agent_assign": True}
        )
        return {"success": True, "message": f"Order {order_id} queued for agent assignment."}
    except Exception as E:
        print()
        raise HTTPException(status_code=500, detail="Failed to auto-assign agent.")