from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime, date
from typing import Optional
from .models import UserRoleEnum

class Token(BaseModel):
    """Authentication token schema"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token payload data"""
    id: Optional[str] = None

class User(BaseModel):
    """
    Base user schema
    Attributes:
        id: Unique user identifier
        name: User's display name
        email: User's email address
        role: User's role in the system
        isTwoFactorEnabled: Two-factor authentication status
    """
    id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRoleEnum = UserRoleEnum.USER
    isTwoFactorEnabled: bool = False

class UserLogin(User):
    """Authentication credentials schema"""
    email: EmailStr
    password: str

class UserCreate(User):
    """User creation schema"""
    id: str
    password: str

class UserUpdate(User):
    """User update schema"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserOut(User):
    """User response schema"""
    email_verified: Optional[datetime] = None

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    """
    Base vehicle schema
    Attributes:
        id: Vehicle identifier
        user_id: Owner's user ID
        license_plate: Vehicle registration number
        brand: Vehicle manufacturer
        created_at: Registration timestamp
    """
    id: Optional[int] = None
    user_id: str
    license_plate: str
    brand: str
    created_at: Optional[datetime] = None

class VehicleCreate(VehicleBase):
    """
    Vehicle creation schema
    Additional Attributes:
        battery_capacity_kwh: Maximum battery capacity
        battery_condition: Battery health percentage
        max_charging_powerkwh: Maximum charging power
        current_battery_capacity_kw: Current battery level
    """
    user_id: str
    license_plate: str
    brand: str
    battery_capacity_kwh: Optional[int] = None
    battery_condition: Optional[float] = None
    max_charging_powerkwh: Optional[int] = None
    current_battery_capacity_kw: float

class VehicleUpdate(VehicleBase):
    """Vehicle update schema"""
    brand: Optional[str] = None
    battery_capacity_kWh: Optional[int] = None
    battery_condition: Optional[float] = None
    current_battery_capacity_kw: Optional[int] = None

class VehicleOut(VehicleBase):
    """Vehicle response schema"""
    battery_capacity_kwh: int
    battery_condition: float
    max_charging_powerkwh: int
    current_battery_capacity_kw: float

    class Config:
        from_attributes = True

class ChargingStationBase(BaseModel):
    """Base charging station schema"""
    name: str
    latitude: float
    longitude: float

class ChargingStationCreate(ChargingStationBase):
    """Charging station creation schema"""
    pass

class ChargingStationOut(ChargingStationBase):
    """Charging station response schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChargingStationUpdate(BaseModel):
    """Charging station update schema"""
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
    
class ChargingPortBase(BaseModel):
    """Base charging port schema"""
    station_id: int
    power_kw: int
    status: str

class ChargingPortCreate(ChargingPortBase):
    """Charging port creation schema"""
    pass

class ChargingPortUpdate(BaseModel):
    """Charging port update schema"""
    power_kw: float | None = None
    status: str | None = None

    class Config:
        orm_mode = True

class ChargingPortOut(BaseModel):
    """Charging port response schema"""
    id: int
    station_id: int
    power_kw: int
    status: str
    last_service_date: Optional[date] = None

    class Config:
        orm_mode = True

class ChargingSessionBase(BaseModel):
    """Base charging session schema"""
    id: int
    vehicle_id: int
    port_id: int
    start_time: datetime
    end_time: Optional[datetime]
    energy_used_kwh: float
    total_cost: float
    status: str
    payment_status: str

    class Config:
        from_attributes = True

class ChargingSessionCreate(BaseModel):
    """Charging session creation schema"""
    vehicle_id: int
    port_id: int
    duration_minutes: int
    energy_used_kwh: float = 0.0
    total_cost: float = 0.0
    status: str = "IN_PROGRESS"
    payment_status: str = "PENDING"
    
    class Config:
        from_attributes = True

class ChargingSessionOut(ChargingSessionBase):
    """Charging session response schema"""
    id: int
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_used_kwh: float
    total_cost: float
    status: str
    payment_status: str

    class Config:
        from_attributes = True     

class ChargingSessionUpdate(BaseModel):
    """Charging session update schema"""
    energy_used_kwh: float
    total_cost: float
    current_battery_level: Optional[float] = None
    payment_status: Optional[str] = None

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    """Base payment schema"""
    user_id: str
    session_id: int
    status: str
    transaction_id: int
    payment_method: str

class PaymentCreate(PaymentBase):
    """Payment creation schema"""
    pass

class PaymentOut(BaseModel):
    """Payment response schema"""
    id: int
    user_id: str
    session_id: int
    status: str
    transaction_id: int
    payment_method: str
    created_at: datetime
    charging_session: ChargingSessionBase

    class Config:
        from_attributes = True


class DiscountIn(BaseModel):
    code: str 
    description: str
    discount_percentage: int 

class DiscountOut(BaseModel):
    id: int
    code: str
    description: str
    discount_percentage: int
    expiration_date: datetime
    created_at: datetime

    class Config:
        orm_mode = True