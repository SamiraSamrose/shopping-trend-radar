"""
backend/app/models/users.py
User-related data models
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MERCHANT = "merchant"
    CONSUMER = "consumer"


class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    username: str
    role: UserRole
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class UserPreferences(BaseModel):
    """User preferences and settings"""
    user_id: str
    favorite_categories: List[str] = []
    preferred_platforms: List[str] = []
    notification_enabled: bool = True
    email_alerts: bool = True
    price_alert_threshold: float = 0.1  # 10% price change
    min_trend_score: float = 0.7
