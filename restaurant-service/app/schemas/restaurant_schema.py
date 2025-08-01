from pydantic import BaseModel, Field , model_validator , ConfigDict
from typing import List, Optional , Literal
from datetime import  time

class MenuInsertionModel(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    type: Literal["VEG", "NON_VEG"] 

class RestaurantInsertionModel(BaseModel):
    name: str
    description: Optional[str] = None
    opening_time: time
    closing_time: time  
    menu: List[MenuInsertionModel]
    
    @model_validator(mode="after")
    def check_menu_items(self):
        if not self.menu or len(self.menu) == 0:
            raise ValueError("At least one menu item is required.")
        return self
    
class MenuUpsertModel(BaseModel):
    id: Optional[str] = None   
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    type: Optional[Literal["VEG", "NON_VEG"]] = None
    delete: Optional[bool] = False   

class RestaurantUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None 
    status: Optional[Literal["ONLINE", "OFFLINE"]] = None
    menu: Optional[List[MenuUpsertModel]] = None
     
    model_config = ConfigDict(extra="forbid")
    
    @model_validator(mode="after")
    def validate_timings(self): 
        if self.opening_time and self.closing_time:
            if self.closing_time <= self.opening_time:
                raise ValueError("Closing time must be later than opening time.")
        return self