"""Authentication and user models"""

from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRole(str, Enum):
    """User roles in the system"""
    CLIENT = "client"
    MANAGER = "manager"


class UserRegister(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.CLIENT


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None
    role: Optional[str] = None


class User(BaseModel):
    """User model"""
    email: str
    full_name: str
    role: UserRole
    is_active: bool = True


class UserInDB(User):
    """User model in database with hashed password"""
    hashed_password: str


class Distance(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float
