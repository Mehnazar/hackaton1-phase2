"""Test script to verify app loads correctly."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.main import app

print("App loaded successfully!")
print("\nRegistered routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', set())
        print(f"  {route.path} - {methods}")

# Test the book endpoint directly
import asyncio
from src.api.routes.book import get_chapters

async def test():
    print("\n Testing book endpoint...")
    try:
        chapters = await get_chapters()
        print(f"  ✓ Got {len(chapters)} chapters")
        for ch in chapters:
            print(f"    - {ch.title}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

asyncio.run(test())
