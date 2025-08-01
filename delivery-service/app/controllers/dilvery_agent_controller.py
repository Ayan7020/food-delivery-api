from app.schemas.dilvery_agent_schema import DilveryAgentModel
from prisma import Prisma
from prisma.errors import UniqueViolationError , RecordNotFoundError
from fastapi import HTTPException
from app.errors.custom_exceptions import DuplicateEntryException , BadRequestException , NotFoundException 

async def add_dilvery_agent_controller(data: DilveryAgentModel, db: Prisma):  
    agent_response = await db.dilveryagent.create(
        data={
            "name": data.name,
            "userName": data.userName,
            "gender": data.gender
        })

    return {
        "status": True,
        "message": "Agent Created Successfully",
        "data": {
            "agent_id": agent_response.id
        }
    } 

async def update_dilvery_status_controller(order_id: str,status: str,db: Prisma):
    if not order_id or not isinstance(order_id, str):
        raise BadRequestException("Invalid order_id.") 
    async with db.tx() as transaction:    
        agent_assignment = await transaction.deliveryassignment.update(
            where={"orderId": order_id},
            data={"status": status},
            include={"agent": True}   
        )

        if not agent_assignment:
            raise HTTPException(status_code=404, detail="Order assignment not found.")

        if status in {"CANCELLED", "DELIVERED"} and agent_assignment.agentId:
            await transaction.dilveryagent.update(
                where={"id": agent_assignment.agentId},
                data={"agent_status": "AVAILABLE"}
            ) 
    return {"success": True, "message": f"Order {order_id} status updated to {status}"} 


async def get_dilvery_status_controller(order_id: str,db: Prisma):
    data = await db.deliveryassignment.find_first(
        where= {
            "orderId": order_id
        }
    )
    
    if not data:
        raise NotFoundException(f"the agent for order id {order_id} didnt find")
    
    return {
        "success": True,
        "message": "Successfull retrive the data",
        "data": {
            "status": data.status
        }
    }