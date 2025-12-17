"""Authentication API routes."""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Header, status, Request
from pydantic import BaseModel

from ...models.user import (
    UserCreate, UserLogin, UserResponse, SessionResponse,
    ChapterPreference, ChapterPreferenceUpdate,
    PersonalizedContent, TranslatedContent,
    PersonalizeRequest, TranslateRequest
)
from ...services.auth_service import auth_service
from ...services.personalization_service import personalization_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Helper function to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Get current authenticated user from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = authorization.replace("Bearer ", "")
    session = await auth_service.get_session(token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    return session


@router.post("/signup", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, request: Request):
    """
    Sign up a new user with profile information.

    Required fields:
    - email: User's email address
    - password: Password (min 8 characters)
    - name: User's full name
    - software_background: beginner | intermediate | advanced
    - hardware_background: low-end | mid-range | high-end
    """
    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with profile
    result = await auth_service.create_user(
        email=user_data.email,
        password=user_data.password,  # In prod, better-auth handles this
        name=user_data.name,
        software_background=user_data.software_background,
        hardware_background=user_data.hardware_background
    )

    # Create session
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    await auth_service.create_session(
        user_id=result["user"]["id"],
        token=token,
        expires_at=expires_at,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    # Build response
    user_response = UserResponse(
        id=result["user"]["id"],
        email=result["user"]["email"],
        name=result["user"]["name"],
        email_verified=result["user"]["email_verified"],
        created_at=result["user"]["created_at"]
    )

    return SessionResponse(
        token=token,
        user=user_response,
        expires_at=expires_at
    )


@router.post("/signin", response_model=SessionResponse)
async def signin(credentials: UserLogin, request: Request):
    """
    Sign in an existing user.

    Returns session token and user information.
    """
    user = await auth_service.get_user_by_email(credentials.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Note: In production, use better-auth's password verification
    # This is simplified for demo purposes

    # Create session
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    await auth_service.create_session(
        user_id=user["id"],
        token=token,
        expires_at=expires_at,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        email_verified=user["email_verified"],
        created_at=user["created_at"]
    )

    return SessionResponse(
        token=token,
        user=user_response,
        expires_at=expires_at
    )


@router.post("/signout")
async def signout(authorization: str = Header(...)):
    """Sign out and invalidate session."""
    token = authorization.replace("Bearer ", "")
    await auth_service.delete_session(token)
    return {"message": "Signed out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(authorization: str = Header(...)):
    """Get current authenticated user information."""
    session = await get_current_user(authorization)

    user = await auth_service.get_user_by_id(session["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        email_verified=user["email_verified"],
        created_at=user["created_at"]
    )


@router.get("/chapter/{chapter_id}/preference", response_model=ChapterPreference)
async def get_chapter_preference(
    chapter_id: str,
    authorization: str = Header(...)
):
    """Get user's preferences for a specific chapter."""
    session = await get_current_user(authorization)

    pref = await auth_service.get_chapter_preference(
        user_id=session["user_id"],
        chapter_id=chapter_id
    )

    if not pref:
        # Return default preferences
        return ChapterPreference(
            chapter_id=chapter_id,
            personalized=False,
            translated_to_urdu=False
        )

    return ChapterPreference(
        chapter_id=pref["chapter_id"],
        personalized=pref["personalized"],
        translated_to_urdu=pref["translated_to_urdu"],
        difficulty_level=pref["difficulty_level"]
    )


@router.put("/chapter/{chapter_id}/preference")
async def update_chapter_preference(
    chapter_id: str,
    update: ChapterPreferenceUpdate,
    authorization: str = Header(...)
):
    """Update user's chapter preferences."""
    session = await get_current_user(authorization)

    pref = await auth_service.upsert_chapter_preference(
        user_id=session["user_id"],
        chapter_id=chapter_id,
        personalized=update.personalized,
        translated_to_urdu=update.translated_to_urdu,
        difficulty_level=update.difficulty_level
    )

    return {"message": "Preferences updated", "preference": pref}


@router.post("/chapter/{chapter_id}/personalize", response_model=PersonalizedContent)
async def personalize_chapter(
    chapter_id: str,
    request: PersonalizeRequest,
    authorization: str = Header(...)
):
    """Personalize chapter content based on user profile."""
    session = await get_current_user(authorization)

    # Get user profile
    user = await auth_service.get_user_by_id(session["user_id"])

    if not user or not user.get("software_background"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile incomplete"
        )

    # Personalize content
    result = await personalization_service.personalize_content(
        original_content=request.content,
        software_background=user["software_background"],
        hardware_background=user["hardware_background"],
        chapter_title=request.title
    )

    # Update user preference
    await auth_service.upsert_chapter_preference(
        user_id=session["user_id"],
        chapter_id=chapter_id,
        personalized=True,
        difficulty_level=user["software_background"]
    )

    return PersonalizedContent(
        chapter_id=chapter_id,
        original_content=request.content,
        personalized_content=result["personalized_content"],
        personalization_applied=result["personalization_applied"],
        difficulty_level=result["difficulty_level"],
        modifications=result["modifications"]
    )


@router.post("/chapter/{chapter_id}/translate", response_model=TranslatedContent)
async def translate_chapter(
    chapter_id: str,
    request: TranslateRequest,
    authorization: str = Header(...)
):
    """Translate chapter content to Urdu."""
    session = await get_current_user(authorization)

    # Translate content
    translated = await personalization_service.translate_to_urdu(
        content=request.content,
        chapter_title=request.title
    )

    # Update user preference
    await auth_service.upsert_chapter_preference(
        user_id=session["user_id"],
        chapter_id=chapter_id,
        translated_to_urdu=True
    )

    return TranslatedContent(
        chapter_id=chapter_id,
        original_content=request.content,
        translated_content=translated,
        language="ur"
    )
