"""Check registered routes in FastAPI app."""

from src.api import main

print("Total routes:", len(main.app.routes))
print("\nRegistered routes:")
for r in main.app.routes:
    path = getattr(r, "path", "N/A")
    methods = getattr(r, "methods", set())
    name = getattr(r, "name", "N/A")
    print(f"  Path: {path}, Methods: {methods}, Name: {name}")
