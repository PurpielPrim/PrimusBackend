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
    user_id = Column(Text, ForeignKey("User.id"), nullable=False)
    license_plate = Column(String(255), nullable=False, unique=True)
    brand = Column(String(255), nullable=False)
    battery_capacity_kwh = Column(Integer, nullable=True)  # Changed from battery_capacity_kWh
    battery_condition = Column(Float)  # This should be set manually, not calculated
    max_charging_powerkwh = Column(BigInteger, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    current_battery_capacity_kw = Column(Float)
    
    # Remove any @hybrid_property or event listeners that might be updating battery_condition
    
    # If there was an event listener like this, remove it:
    # @validates('current_battery_capacity_kw')
    # def validate_battery(self, key, value):
    #     self.battery_condition = value / self.battery_capacity_kWh
    #     return value

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
    power_kw = Column(BigInteger, nullable=False)
    status = Column(String(255), nullable=False)
    last_service_date = Column(Date, nullable=True)  # Make it nullable
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# tabela z sesją 
class ChargingSession(Base):
    __tablename__ = "charging_sessions"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("User.id"), nullable=False)  # Change Text to String
    vehicle_id = Column(BigInteger, ForeignKey("vehicles.id"), nullable=False)
    port_id = Column(BigInteger, ForeignKey("charging_ports.id"), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    energy_used_kwh = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)
    status = Column(String(255), nullable=False, default='IN_PROGRESS')
    payment_status = Column(String(255), nullable=False, default='PENDING')  # Add this line
    
    # Add property to calculate duration
    @property
    def duration_minutes(self):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    # Add relationships
    user = relationship("User", backref="charging_sessions")
    vehicle = relationship("Vehicle", backref="charging_sessions")
    port = relationship("ChargingPort", backref="charging_sessions")

# tabela z płatnościami
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(Text, ForeignKey("User.id"), nullable=False)
    session_id = Column(BigInteger, ForeignKey("charging_sessions.id"), nullable=False)
    status = Column(String(255), nullable=False)
    transaction_id = Column(BigInteger, nullable=False)
    payment_method = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    charging_session = relationship("ChargingSession", backref="payment", lazy="joined")

# tabela z kuponami
class Discount(Base):
    __tablename__ = "discounts"
    
    id = Column(BigInteger, primary_key=True, nullable=False)
    code = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    discount_percentage = Column(BigInteger, nullable=False)
    expiration_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
