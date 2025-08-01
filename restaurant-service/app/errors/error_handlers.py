from fastapi import Request
from fastapi.responses import JSONResponse
from prisma.errors import UniqueViolationError, RecordNotFoundError
from .custom_exceptions import AppException
 
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )
 
async def prisma_unique_violation_handler(request: Request, exc: UniqueViolationError):
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": "Duplicate entry: A record with these details already exists."},
    )
 
async def prisma_record_not_found_handler(request: Request, exc: RecordNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "The requested record was not found."},
    )
 
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal Server Error"},
    )
