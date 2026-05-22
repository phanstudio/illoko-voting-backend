from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,

    # important
    pool_pre_ping=True,
    pool_recycle=3600,

    # safer asyncpg ssl handling
    connect_args={
        "ssl": "require"
    }
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
