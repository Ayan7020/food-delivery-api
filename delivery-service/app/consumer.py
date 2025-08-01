from app.core.db import db


async def assign_dilvery_agent(message: dict):
    try:
        agent = await db.dilveryagent.find_first(
            where={"agent_status": "AVAILABLE"},
            order={"createdAt": "asc"}
        )
        if not agent:
            print(f"No dilvery agent found")
            
        assignment = await db.deliveryassignment.create(
            data={
                "orderId": message["order_id"],
                "agentId": agent.id,
            }
        )

        await db.dilveryagent.update(
            where={"id": agent.id},
            data={"agent_status": "BUSY"}
        )
        print(f"[Consumer] Dilvery Agent of {message['order_id']} processed successfully.")
    except Exception as e:
        print(f"[Consumer] Failed to process order: {e}")

async def process_dilvery_rating(message: dict):
    try:
        order_id = message["order_id"]
        await db.deliveryassignment.update(
            where={
                "orderId": order_id
            },
            data= {
                "rating": message["agent_rating"]
            }
        )
        print(f"[Consumer] Dilvery Aget rating of the order {message['order_id']} processed successfully.")
    except Exception as e:
        print(f"[Consumer] Failed to process order: {e}")