from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, Date, ForeignKey, CheckConstraint, Text, Enum
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

# tabela z użytkownikami
class User(Base):
    __tablename__ = "User"

    id = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    email_verified = Column(TIMESTAMP, nullable=True)
    image = Column(Text, nullable=True)
    password = Column(Text, nullable=True)
    role = Column(Enum(UserRoleEnum, name="user_role_enum"), nullable=False, default=UserRoleEnum.USER)
    isTwoFactorEnabled = Column(Boolean, nullable=False, default=False)

# tabela z samochodami
class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=False)
    license_plate = Column(String(255), nullable=False, unique=True)
    brand = Column(String(255), nullable=False)
    battery_capacity_kWh = Column(Integer, nullable=False)
    battery_condition = Column(Float, nullable=False)
    max_charging_powerkWh = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# tabela ze stacjami
class ChargingStation(Base):
    __tablename__ = "charging_stations"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# tabela z portami
class ChargingPort(Base):
    __tablename__ = "charging_ports"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    station_id = Column(BigInteger, ForeignKey("charging_stations.id"), nullable=False)
    power_kW = Column(BigInteger, nullable=False)
    status = Column(String(255), nullable=False)
    last_service_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# tabela z sesją 
class ChargingSession(Base):
    __tablename__ = "charging_sessions"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=False)
    vehicle_id = Column(BigInteger, ForeignKey("vehicles.id"), nullable=False)
    port_id = Column(BigInteger, ForeignKey("charging_ports.id"), nullable=False)
    start_time = Column(Date, nullable=False)
    end_time = Column(Date, nullable=False)
    energy_used_kWh = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    status = Column(String(255), nullable=False)

# tabela z płatnościami
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("charging_sessions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(255), nullable=False)
    transaction_id = Column(BigInteger, nullable=False)
    payment_method = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# tabela z kuponami
class Discount(Base):
    __tablename__ = "discounts"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    code = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    discount_percentage = Column(BigInteger, nullable=False)
    expiration_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
