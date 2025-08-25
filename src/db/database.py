import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# --- PostgreSQL Connection Setup ---
# It's best practice to load these from environment variables
# to keep credentials out of your code.
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "podcasts_db")

# The database URL format for asyncpg is:
# "postgresql+asyncpg://user:password@host:port/dbname"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


print(f"Connecting to database at: postgresql+asyncpg://{DB_USER}:******@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Create the async engine
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Create a factory for async sessions
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)