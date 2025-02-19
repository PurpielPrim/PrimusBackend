from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint
from .models import UserRoleEnum

# Baza użytkownika
class User(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
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
    pass
    email_verified: Optional[datetime] = None

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    id: Optional[int] = None
    user_id: str
    license_plate: str
    brand: str
    battery_capacity_kWh: Optional[int] = None
    battery_condition: Optional[float] = None
    max_charging_powerkWh: Optional[int] = None
    created_at: Optional[datetime] = None

class VehicleCreate(VehicleBase):
    user_id: str
    license_plate: str
    brand: str

class VehicleOut(VehicleBase):
    pass

class ChargingStationBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class ChargingStationCreate(ChargingStationBase):
    pass

class ChargingStationOut(ChargingStationBase):
    id: int
    pass
    created_at: datetime

    class Config:
        from_attributes = True
