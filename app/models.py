from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base

# tabela z samochodami
class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    car_brand = Column(String, nullable=False)
    car_number = Column(String, nullable=False, unique=True)
    curr_battery = Column(String, nullable=True)
    max_battery = Column(String, nullable=False)
    req_battery = Column(String, nullable=True)
    last_charge = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

# class Post(Base):
#     __tablename__ = "posts"

#     id = Column(Integer, primary_key=True, nullable=False)
#     owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     title = Column(String, nullable=False)
#     content = Column(String, nullable=False)
#     published = Column(Boolean, server_default='TRUE', nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     owner = relationship("User")


# # tabela z uzytkownikami - musimy to jakos zgrac od Karola(?)
# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
#     phone_number = Column(String)


# # tabela ze stacjami
# class Station(Base):
#     __tablename__ = "stations"

#     id = Column(Integer, primary_key=True, nullable=False)
#     country = Column(String, nullable=False)
#     city = Column(String, nullable=False)
#     street = Column(String, nullable=False)

# # tabela ze

