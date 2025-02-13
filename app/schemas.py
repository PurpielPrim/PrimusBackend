from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class User(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChargingStationBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class CreateChargingStation(ChargingStationBase):
    pass