from pydantic import BaseModel
from typing import Literal

class DilveryAgentModel(BaseModel):
    name: str
    userName: str
    gender: Literal["MALE", "FEMALE"]
    
    
class UpdateDilveryStatusModel(BaseModel):
    order_id: str
    status: Literal["PICKED_UP","DELIVERED","CANCELLED"]       