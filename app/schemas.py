from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint
from .models import UserRoleEnum

# Baza użytkownika
class User(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    image: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.USER
    isTwoFactorEnabled: bool = False

# Do tworzenia użytkownika
class UserCreate(User):
    id: str
    password: str

# Do update'u użytkownika
class UserUpdate(User):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Do wypisania użytkownika
class UserOut(User):
    id: str
    email_verified: Optional[datetime] = None

    class Config:
        from_attributes = True

# class User(BaseModel):
#     id: int
#     email: EmailStr
#     first_name: str
#     last_name: str
#     phone_number: int
#     role: str
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

class ChargingStationBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class CreateChargingStation(ChargingStationBase):
    pass