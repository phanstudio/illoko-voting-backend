from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from slowapi import Limiter, \_rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from limits.storage import RedisStorage
import redis.asyncio as aioredis
import os
from dotenv import load_dotenv

from app.database import engine, Base
from app.routers import users, candidates, votes

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Redis connection and Slowapi limiter with Redis storage

redis_client = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
storage = RedisStorage(redis_client)
limiter = Limiter(key_func=get_remote_address, storage=storage)

@asynccontextmanager
async def lifespan(app: FastAPI): # Create tables on startup (for production use Alembic)
async with engine.begin() as conn:
await conn.run_sync(Base.metadata.create_all)
yield
await redis_client.close()
