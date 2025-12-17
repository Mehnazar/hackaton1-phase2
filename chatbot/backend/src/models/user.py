"""User and authentication models."""

from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)
    software_background: Literal["beginner", "intermediate", "advanced"]
    hardware_background: Literal["low-end", "mid-range", "high-end"]


class UserProfile(BaseModel):
    """User profile model."""
    user_id: UUID
    software_background: Literal["beginner", "intermediate", "advanced"]
    hardware_background: Literal["low-end", "mid-range", "high-end"]
    preferred_language: str = "en"
    onboarding_completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model."""
    id: UUID
    email: str
    name: Optional[str]
    email_verified: bool
    profile: Optional[UserProfile] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class SessionResponse(BaseModel):
    """Session response model."""
    token: str
    user: UserResponse
    expires_at: datetime


class ChapterPreference(BaseModel):
    """Chapter preference model."""
    chapter_id: str
    personalized: bool = False
    translated_to_urdu: bool = False
    difficulty_level: Optional[str] = None


class ChapterPreferenceUpdate(BaseModel):
    """Update chapter preferences."""
    personalized: Optional[bool] = None
    translated_to_urdu: Optional[bool] = None
    difficulty_level: Optional[str] = None


class PersonalizedContent(BaseModel):
    """Personalized chapter content."""
    chapter_id: str
    original_content: str
    personalized_content: str
    personalization_applied: bool
    difficulty_level: str
    modifications: list[str] = []


class TranslatedContent(BaseModel):
    """Translated chapter content."""
    chapter_id: str
    original_content: str
    translated_content: str
    language: str = "ur"


class PersonalizeRequest(BaseModel):
    """Request to personalize chapter content."""
    content: str
    title: str


class TranslateRequest(BaseModel):
    """Request to translate chapter content."""
    content: str
    title: str
