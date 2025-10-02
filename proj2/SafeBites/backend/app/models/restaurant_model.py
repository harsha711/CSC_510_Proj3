from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RestaurantBase(BaseModel):
    name:str
    location:str
    cuisine:Optional[str] = None
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name:Optional[str]
    location:Optional[str]
    cuisine:Optional[str]
    rating:Optional[float]

class RestaurantInDB(RestaurantBase):
    id:str = Field(alias="_id")

    class Config:
        populate_by_name = True