from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import users, candidates, votes, upload, auth


from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# -----------------------------
# Rate limiter setup (fallback-safe)
# -----------------------------

storage = None

if REDIS_URL:
    try:
        import redis.asyncio as aioredis
        from limits.storage import RedisStorage

        redis_client = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

        storage = RedisStorage(redis_client)
        print("✅ Redis enabled for rate limiting")

    except Exception as e:
        print("⚠️ Redis unavailable, falling back to memory limiter:", e)

# fallback if Redis not available
limiter = Limiter(key_func=get_remote_address)

# -----------------------------
# Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # only close redis if it exists
    if REDIS_URL and "redis_client" in globals():
        try:
            await redis_client.close()
        except:
            pass

app = FastAPI(
    title="Voting Application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://illoko-voting-platform.netlify.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach rate-limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(users.router)
app.include_router(candidates.router)
app.include_router(votes.router)
if DEBUG:
    app.include_router(upload.router) 
app.include_router(auth.router) 

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Welcome to the Voting API"}
