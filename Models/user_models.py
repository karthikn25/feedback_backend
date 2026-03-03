from pydantic import BaseModel, EmailStr,Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    clientId: Optional[str] = None
    userId: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    role: Optional[str] = "user" 

class UserLogin(BaseModel):
    userId: str
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    clientId: str
    userId: str
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    role: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None