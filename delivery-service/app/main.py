from fastapi import FastAPI
from contextlib import asynccontextmanager 
import uvicorn 
import asyncio  
from contextlib import asynccontextmanager
from app.core.rabbit import Broker
from app.core.db import db
from app.routers import dilvery_agent
from app.consumer import assign_dilvery_agent , process_dilvery_rating
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
    await db.connect()
    await Broker.connect()
    asyncio.create_task(Broker.consume("assign-dilvery-agent-queue",assign_dilvery_agent))
    asyncio.create_task(Broker.consume_fan_out("ratings-exchange",process_dilvery_rating))
    yield
    await Broker.connection.close()

app = FastAPI(title="Dilvery Agent Service",lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(UniqueViolationError, prisma_unique_violation_handler)
app.add_exception_handler(RecordNotFoundError, prisma_record_not_found_handler)
app.add_exception_handler(Exception, internal_server_error_handler)

@app.get("/health")
def get_health():
    """Check the health of the dilvery-agent-service"""
    return {
        "Success": True,
        "message": "Good"
    }  

app.include_router(dilvery_agent.router,tags=["DilveryAgent"])

if __name__=="__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8003,reload=True)    