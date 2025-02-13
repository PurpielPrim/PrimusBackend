from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

# class UserOut(BaseModel):
#     id: str
#     email: EmailStr
#     created_at: datetime

# U Karola już to jest(?)
# class UserCreate(BaseModel):
#     name: str
#     email: EmailStr
#     password: str

# U Karola już to jest(?)
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# U Karola już to jest(?)
# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     id: Optional[str] = None
