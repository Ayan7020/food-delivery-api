from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn 
import asyncio
from app.core.rabbit import Broker
from app.core.db import db
from app.routers import restaurants , orders , agent
from app.consumer import process_order , process_order_rating

from app.errors.error_handlers import (
    app_exception_handler,
    prisma_unique_violation_handler,
    prisma_record_not_found_handler,
    internal_server_error_handler,
)
from app.errors.custom_exceptions import AppException
from prisma.errors import UniqueViolationError , RecordNotFoundError

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on Start
    await Broker.connect()
    asyncio.create_task(Broker.consume("place-order-queue",process_order))
    asyncio.create_task(Broker.consume_fan_out("ratings-exchange",process_order_rating))
    await db.connect()
    yield
    # Shut down
    await Broker.connection.close()
    
app = FastAPI(title="Restaurant  Service",lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(UniqueViolationError, prisma_unique_violation_handler)
app.add_exception_handler(RecordNotFoundError, prisma_record_not_found_handler)
app.add_exception_handler(Exception, internal_server_error_handler)

@app.get("/health")
def get_health():
    """Check the health of the user-service"""
    return {
        "Success": True,
        "message": "Good"
    } 
    
app.include_router(restaurants.router,tags=["Restaurants"])
app.include_router(orders.router,tags=["Orders"]) 


if __name__=="__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8002,reload=True)    