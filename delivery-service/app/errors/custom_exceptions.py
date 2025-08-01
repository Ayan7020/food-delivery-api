from fastapi import HTTPException

class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
 
class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(400, detail)

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(404, detail)

class DuplicateEntryException(AppException):
    def __init__(self, detail: str = "Duplicate entry"):
        super().__init__(400, detail)

class InternalServerError(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(500, detail)
