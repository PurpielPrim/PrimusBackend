from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, Date, ForeignKey, CheckConstraint, Text, Enum
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRoleEnum(str, enum.Enum):
    """User role enumeration for access control"""
    ADMIN = "ADMIN"
    USER = "USER"

class User(Base):
    """
    User model representing system users
    Attributes:
        id: Unique user identifier
        email: User's email address
        password: Hashed password
        role: User's role (ADMIN/USER)
        isTwoFactorEnabled: 2FA status
    """
    __tablename__ = "User"

    id = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    email_verified = Column(TIMESTAMP, nullable=True)
    image = Column(Text, nullable=True)
    password = Column(Text, nullable=True)
    role = Column(Enum(UserRoleEnum, name="user_role_enum"), nullable=False, default=UserRoleEnum.USER)
    isTwoFactorEnabled = Column(Boolean, nullable=False, default=False)

class Vehicle(Base):
    """
    Vehicle model for electric vehicles
    Attributes:
        id: Unique vehicle identifier
        user_id: Owner's user ID
        license_plate: Vehicle's license plate
        brand: Vehicle manufacturer
        battery_capacity_kwh: Maximum battery capacity
        battery_condition: Current battery health
        current_battery_capacity_kw: Current charge level
    """
    __tablename__ = "vehicles"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(Text, ForeignKey("User.id"), nullable=False)
    license_plate = Column(String(255), nullable=False, unique=True)
    brand = Column(String(255), nullable=False)
    battery_capacity_kwh = Column(Integer, nullable=True)
    battery_condition = Column(Float)
    max_charging_powerkwh = Column(BigInteger, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    current_battery_capacity_kw = Column(Float)

class ChargingStation(Base):
    """
    Charging station model representing physical charging locations
    Attributes:
        id: Unique station identifier
        name: Station name
        latitude: Geographic latitude
        longitude: Geographic longitude
    """
    __tablename__ = "charging_stations"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class ChargingPort(Base):
    """
    Charging port model representing individual charging points
    Attributes:
        id: Unique port identifier
        station_id: Parent station ID
        power_kw: Maximum charging power
        status: Current port status
        last_service_date: Last maintenance date
    """
    __tablename__ = "charging_ports"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    station_id = Column(BigInteger, ForeignKey("charging_stations.id"), nullable=False)
    power_kw = Column(BigInteger, nullable=False)
    status = Column(String(255), nullable=False)
    last_service_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class ChargingSession(Base):
    """
    Charging session model tracking individual charging events
    Attributes:
        id: Unique session identifier
        user_id: User who started the session
        vehicle_id: Vehicle being charged
        port_id: Port being used
        start_time: Session start time
        end_time: Session end time
        energy_used_kwh: Energy consumed
        total_cost: Session cost
        status: Current session status
        payment_status: Payment status
    """
    __tablename__ = "charging_sessions"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("User.id"), nullable=False)
    vehicle_id = Column(BigInteger, ForeignKey("vehicles.id"), nullable=False)
    port_id = Column(BigInteger, ForeignKey("charging_ports.id"), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    energy_used_kwh = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)
    status = Column(String(255), nullable=False, default='IN_PROGRESS')
    payment_status = Column(String(255), nullable=False, default='PENDING')

    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    user = relationship("User", backref="charging_sessions")
    vehicle = relationship("Vehicle", backref="charging_sessions")
    port = relationship("ChargingPort", backref="charging_sessions")

class Payment(Base):
    """
    Payment model for tracking charging session payments
    Attributes:
        id: Unique payment identifier
        user_id: User making the payment
        session_id: Related charging session
        status: Payment status
        transaction_id: External payment reference
        payment_method: Method of payment
    """
    __tablename__ = "payments"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(Text, ForeignKey("User.id"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("charging_sessions.id"), nullable=False)
    status = Column(String(255), nullable=False)
    transaction_id = Column(BigInteger, nullable=False)
    payment_method = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    charging_session = relationship("ChargingSession", backref="payment", lazy="joined")

class Discount(Base):
    """
    Discount model for promotional codes
    Attributes:
        id: Unique discount identifier
        code: Discount code
        description: Discount description
        discount_percentage: Discount amount
        expiration_date: Code validity end date
    """
    __tablename__ = "discounts"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    code = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    discount_percentage = Column(BigInteger, nullable=False)
    expiration_date = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))