"""Authentication and user management service."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import asyncpg
from asyncpg import Pool

from ..config import settings


class AuthService:
    """Service for authentication and user management."""

    def __init__(self):
        self.db_url = settings.neon_database_url
        self.pool: Optional[Pool] = None

    async def init_pool(self):
        """Initialize database connection pool."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,
                max_size=10
            )

    async def close_pool(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()

    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (better-auth handles this in prod)."""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            salt, pwd_hash = hashed.split("$")
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except:
            return False

    async def create_user(
        self,
        email: str,
        password: str,
        name: Optional[str],
        software_background: str,
        hardware_background: str
    ) -> dict:
        """Create new user with profile."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            # Start transaction
            async with conn.transaction():
                # Create user
                user = await conn.fetchrow(
                    """
                    INSERT INTO users (email, name, email_verified)
                    VALUES ($1, $2, FALSE)
                    RETURNING id, email, name, email_verified, created_at
                    """,
                    email, name
                )

                # Create user profile
                profile = await conn.fetchrow(
                    """
                    INSERT INTO user_profiles (
                        user_id, software_background, hardware_background,
                        onboarding_completed
                    )
                    VALUES ($1, $2, $3, TRUE)
                    RETURNING *
                    """,
                    user["id"], software_background, hardware_background
                )

                return {
                    "user": dict(user),
                    "profile": dict(profile)
                }

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email with profile."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT u.*, p.*
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.email = $1
                """,
                email
            )
            return dict(user) if user else None

    async def get_user_by_id(self, user_id: UUID) -> Optional[dict]:
        """Get user by ID with profile."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            user = await conn.fetchrow(
                """
                SELECT u.*, p.software_background, p.hardware_background,
                       p.preferred_language, p.onboarding_completed
                FROM users u
                LEFT JOIN user_profiles p ON u.id = p.user_id
                WHERE u.id = $1
                """,
                user_id
            )
            return dict(user) if user else None

    async def create_session(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """Create new session."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            session = await conn.fetchrow(
                """
                INSERT INTO sessions (user_id, token, expires_at, ip_address, user_agent)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
                """,
                user_id, token, expires_at, ip_address, user_agent
            )
            return dict(session)

    async def get_session(self, token: str) -> Optional[dict]:
        """Get session by token."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            session = await conn.fetchrow(
                """
                SELECT s.*, u.id as user_id, u.email, u.name, u.email_verified
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.token = $1 AND s.expires_at > NOW()
                """,
                token
            )
            return dict(session) if session else None

    async def delete_session(self, token: str):
        """Delete session (logout)."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM sessions WHERE token = $1", token)

    async def get_chapter_preference(
        self,
        user_id: UUID,
        chapter_id: str
    ) -> Optional[dict]:
        """Get user's chapter preferences."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            pref = await conn.fetchrow(
                """
                SELECT * FROM user_chapter_preferences
                WHERE user_id = $1 AND chapter_id = $2
                """,
                user_id, chapter_id
            )
            return dict(pref) if pref else None

    async def upsert_chapter_preference(
        self,
        user_id: UUID,
        chapter_id: str,
        personalized: Optional[bool] = None,
        translated_to_urdu: Optional[bool] = None,
        difficulty_level: Optional[str] = None
    ) -> dict:
        """Create or update chapter preference."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            # Build dynamic update query
            updates = []
            params = [user_id, chapter_id]
            param_idx = 3

            if personalized is not None:
                updates.append(f"personalized = ${param_idx}")
                params.append(personalized)
                param_idx += 1

            if translated_to_urdu is not None:
                updates.append(f"translated_to_urdu = ${param_idx}")
                params.append(translated_to_urdu)
                param_idx += 1

            if difficulty_level is not None:
                updates.append(f"difficulty_level = ${param_idx}")
                params.append(difficulty_level)
                param_idx += 1

            updates.append("last_accessed = NOW()")

            pref = await conn.fetchrow(
                f"""
                INSERT INTO user_chapter_preferences (user_id, chapter_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, chapter_id)
                DO UPDATE SET {', '.join(updates)}
                RETURNING *
                """,
                *params
            )
            return dict(pref)

    async def update_reading_progress(
        self,
        user_id: UUID,
        chapter_id: str,
        completed: bool = False,
        time_spent_seconds: int = 0
    ):
        """Update user's reading progress."""
        await self.init_pool()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_reading_progress (user_id, chapter_id, completed, time_spent_seconds)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, chapter_id)
                DO UPDATE SET
                    completed = $3,
                    time_spent_seconds = user_reading_progress.time_spent_seconds + $4,
                    updated_at = NOW()
                """,
                user_id, chapter_id, completed, time_spent_seconds
            )


# Global instance
auth_service = AuthService()
