import asyncio
from backend.app.database.session import engine, Base
import backend.app.models.domain  # noqa: F401

async def reset_database():
    """Drops and recreates all database tables for a clean development environment."""
    print("Resetting CodePilot-MCP database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables recreated successfully.")

if __name__ == "__main__":
    asyncio.run(reset_database())
