from pydantic import BaseModel, Field 

class RatingModel(BaseModel):
    user_id: str
    order_id: str
    order_rating: float = Field(..., ge=1, le=5, description="Order rating between 1 and 5")
    agent_rating: float = Field(..., ge=1, le=5, description="Agent rating between 1 and 5")