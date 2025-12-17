"""
Create database schema for authentication system.
Run this script once to initialize the database tables.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_schema():
    """Create database schema in Neon Postgres."""

    # Get database URL from environment
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        print("ERROR: NEON_DATABASE_URL not found in environment")
        return False

    print("Connecting to Neon database...")

    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("SUCCESS: Connected to database successfully")

        # Read the schema file
        print("Reading schema file...")
        with open('sql/auth_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()

        # Execute the schema
        print("Creating tables...")
        await conn.execute(schema)

        print("SUCCESS: Database schema created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - sessions")
        print("  - user_profiles")
        print("  - user_chapter_preferences")
        print("  - user_reading_progress")

        # Close connection
        await conn.close()
        return True

    except FileNotFoundError:
        print("ERROR: sql/auth_schema.sql file not found")
        return False
    except asyncpg.PostgresError as e:
        print(f"DATABASE ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Schema Creation Script")
    print("=" * 60)
    print()

    success = asyncio.run(create_schema())

    print()
    if success:
        print("Setup complete! You can now use signup/signin features.")
    else:
        print("Setup failed. Please check the errors above.")

    print("=" * 60)
