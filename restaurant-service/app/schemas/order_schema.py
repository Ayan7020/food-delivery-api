from pydantic import BaseModel
from typing import Literal

class OrderStatusUpdateModel(BaseModel):
    status: Literal[ 
    "CONFIRMED",
    "CANCELLED"
]