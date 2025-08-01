from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.rabbit import Broker
import uvicorn
from app.routers import restaurants , rating
from app.core.redis import redis_client
from app.core.db import db
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
    await db.connect()
    await redis_client.ping() 
    yield
    # Shut down
    await Broker.connection.close()
    
    
app = FastAPI(title="User Service",lifespan=lifespan)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(UniqueViolationError, prisma_unique_violation_handler)
app.add_exception_handler(RecordNotFoundError, prisma_record_not_found_handler)
app.add_exception_handler(Exception, internal_server_error_handler)


app.include_router(restaurants.router, tags=["Restaurants"])
app.include_router(rating.router, tags=["Ratings"])


@app.get("/health")
def get_health():
    """Check the health of the user-service"""
    return {
        "Success": True,
        "message": "Good"
    } 

if __name__=="__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8001,reload=True)    