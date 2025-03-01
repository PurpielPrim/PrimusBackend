from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime, date
from typing import Optional
from .models import UserRoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

# Baza użytkownika
class User(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRoleEnum = UserRoleEnum.USER
    isTwoFactorEnabled: bool = False

# Logowanie użytkownika - potrzebne do tokena
class UserLogin(User):
    email: EmailStr
    password: str

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

# Baza pojazdu
class VehicleBase(BaseModel):
    id: Optional[int] = None
    user_id: str
    license_plate: str
    brand: str
    created_at: Optional[datetime] = None

# Do tworzenia pojazdu
class VehicleCreate(VehicleBase):
    user_id: str
    license_plate: str
    brand: str
    battery_capacity_kwh: Optional[int] = None
    battery_condition: Optional[float] = None
    max_charging_powerkwh: Optional[int] = None
    current_battery_capacity_kw: float

class VehicleUpdate(VehicleBase):
    brand: Optional[str] = None
    battery_capacity_kWh: Optional[int] = None
    battery_condition: Optional[float] = None
    current_battery_capacity_kw: Optional[int] = None

# Do wypisywania pojazdu
class VehicleOut(VehicleBase):
    pass
    battery_capacity_kwh: int
    battery_condition: float
    max_charging_powerkwh: int
    current_battery_capacity_kw: float

    class Config:
        from_attributes = True

# Baza stacji
class ChargingStationBase(BaseModel):
    name: str
    latitude: float
    longitude: float

# Do tworzenia stacji
class ChargingStationCreate(ChargingStationBase):
    pass

# Do wypisywania stacji
class ChargingStationOut(ChargingStationBase):
    id: int
    pass
    created_at: datetime

    class Config:
        from_attributes = True

class ChargingStationUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
    
class ChargingPortBase(BaseModel):
    station_id: int
    power_kw: int  # Changed from power_kW to power_kw
    status: str

class ChargingPortCreate(ChargingPortBase):
    pass

class ChargingPortUpdate(BaseModel):
    power_kw: float | None = None
    status: str | None = None

    class Config:
        orm_mode = True

class ChargingPortOut(BaseModel):
    id: int
    station_id: int
    power_kw: int
    status: str
    last_service_date: Optional[date] = None  # Make it optional

    class Config:
        orm_mode = True

# Podstawowa struktura sesji ładowania
class ChargingSessionBase(BaseModel):
    id: int  # Make sure id is included
    user_id: str
    vehicle_id: int
    port_id: int
    start_time: datetime
    energy_used_kwh: float
    total_cost: float
    status: str

    class Config:
        orm_mode = True

# Tworzenie nowej sesji ładowania
class ChargingSessionCreate(BaseModel):
    vehicle_id: int
    port_id: int
    duration_minutes: int
    energy_used_kwh: float = 0.0
    total_cost: float = 0.0
    status: str = "IN_PROGRESS"
    
    class Config:
        from_attributes = True

# Odpowiedź dla użytkownika (np. po rozpoczęciu lub zakończeniu sesji)
class ChargingSessionOut(ChargingSessionBase):
    id: int
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_used_kwh: float
    total_cost: float
    status: str

    class Config:
        from_attributes = True     

# Add this class to your schemas.py file
class ChargingSessionUpdate(BaseModel):
    energy_used_kwh: float
    total_cost: float
    current_battery_capacity_kw: float

    class Config:
        from_attributes = True

# Baza płatności
class PaymentBase(BaseModel):
    user_id: str
    session_id: int
    amount: float
    status: str
    transaction_id: int
    payment_method: str

# Do tworzenia płatności
class PaymentCreate(PaymentBase):
    pass

# Do wypisywania płatności
class PaymentOut(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
