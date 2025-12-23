from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession

# This is the shared dependency script, such as database connection
from app.db.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        yield session
