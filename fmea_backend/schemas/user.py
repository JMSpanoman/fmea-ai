from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str  # Changed from EmailStr to str temporarily
    full_name: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None  # Changed from EmailStr to str temporarily
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class PasswordReset(BaseModel):
    email: str  # Changed from EmailStr to str temporarily

class PasswordChange(BaseModel):
    current_password: str
    new_password: str 