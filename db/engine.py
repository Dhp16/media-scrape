import os

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncAttrs, # Recommended for ORM async operations
)
from sqlalchemy.orm import (
    DeclarativeBase
)

from manage_podcasts.constants import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB

# --- Database Configuration ---
# Replace with your actual async PostgreSQL connection string
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"

# --- Base Class ---
# Inheriting from AsyncAttrs helps with async loading of relationships
class Base(AsyncAttrs, DeclarativeBase):
    pass

# --- ORM Models ---


# --- Basic Async Setup & Table Creation Example ---

async def start_db_engine():
    engine = create_async_engine(DATABASE_URL, echo=False) # Set echo=True to see SQL

    async with engine.begin() as conn:
        # Optional: Drop all tables defined in Base metadata
        # await conn.run_sync(Base.metadata.drop_all)
        # Create all tables defined in Base metadata if they don't exist
        await conn.run_sync(Base.metadata.create_all)

    # Engine disposal is usually handled by application shutdown logic
    # await engine.dispose()

    print("Database tables checked/created.")

    # Example of creating a session factory for later use
    # async_session = async_sessionmaker(engine, expire_on_commit=False)
    # async with async_session() as session:
    #     # Example query (won't return anything unless data exists)
    #     stmt = select(PodcastSeries).where(PodcastSeries.name == "Some Series")
    #     result = await session.execute(stmt)
    #     series = result.scalar_one_or_none()
    #     print(f"Found series: {series}")
