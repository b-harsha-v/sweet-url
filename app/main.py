import os
import re
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates


from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import engine, Base, AsyncSessionLocal
from app.models.url import URLMapping
from app.models.unused_key import UnusedKey
from app.db.redis_client import cache



# --- 1. UPDATED SCHEMA ---
class URLRequest(BaseModel):
    long_url: str
    custom_alias: Optional[str] = None
    expires_in_hours: Optional[int] = None

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Enterprise URL Shortener",
    version="1.1.0",
    lifespan=lifespan
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def serve_ui(request: Request):
    # Notice we are explicitly saying request=request and name="index.html"
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/v1/shorten", status_code=201)
async def shorten_url(request: URLRequest, db: AsyncSession = Depends(get_db)):
    short_alias = None

    # --- 2. CUSTOM ALIAS LOGIC ---
    if request.custom_alias:
        # sanitize custom alias
        short_alias = request.custom_alias.strip()
        short_alias = short_alias.replace(" ", "-")
        short_alias = re.sub(r"[^a-zA-Z0-9_-]", "", short_alias)
        short_alias = short_alias.lower()

        if not short_alias:
            raise HTTPException(
                status_code=400,
                detail="Invalid custom alias."
            )
        # Check if alias already exists
        result = await db.execute(
            select(URLMapping).where(URLMapping.short_url == short_alias)
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Custom alias is already taken."
            )
    else:
        # Standard KGS Logic
        stmt = select(UnusedKey).with_for_update(skip_locked=True).limit(1)
        result = await db.execute(stmt)
        unused_key_obj = result.scalar_one_or_none()
        
        if not unused_key_obj:
            raise HTTPException(status_code=500, detail="Key pool exhausted! Run the KGS worker.")
            
        short_alias = unused_key_obj.key
        await db.delete(unused_key_obj)

    # --- 3. EXPIRATION LOGIC ---
    expires_at = None
    cache_ttl = 86400  # Default Redis cache time: 24 hours
    
    if request.expires_in_hours:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=request.expires_in_hours)
        # Ensure Redis deletes the cache exactly when the link expires
        cache_ttl = min(cache_ttl, request.expires_in_hours * 3600)

    # Save to database
    new_url = URLMapping(short_url=short_alias, original_url=request.long_url, expires_at=expires_at)
    db.add(new_url)
    await db.commit()
    
    # Warm the cache
    await cache.set(short_alias, request.long_url, ex=cache_ttl)
    
    # Grab the base URL from the environment, but default to localhost for local testing
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    return {
        "short_url": f"{base_url}/{short_alias}",
        "original_url": request.long_url,
        "expires_at": expires_at
    }

@app.get("/{alias}")
async def redirect_to_url(alias: str, db: AsyncSession = Depends(get_db)):
    # CACHE CHECK
    cached_url = await cache.get(alias)
    if cached_url:
        print(f"⚡ CACHE HIT for {alias}")
        return RedirectResponse(url=cached_url)
        
    print(f"🐢 CACHE MISS for {alias}. Querying database...")
    
    # DATABASE FALLBACK
    result = await db.execute(select(URLMapping).where(URLMapping.short_url == alias))
    db_url = result.scalar_one_or_none()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # --- 4. EXPIRATION CHECK ---
    # We force the tzinfo to UTC so Python doesn't throw the same timezone error we fixed earlier
    if db_url.expires_at and db_url.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        # Auto-clean the database by deleting the expired link
        await db.delete(db_url)
        await db.commit()
        raise HTTPException(status_code=410, detail="This URL has expired and has been deleted.")
        
    # WARM CACHE
    cache_ttl = 86400
    if db_url.expires_at:
        time_left = (db_url.expires_at.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds()
        cache_ttl = min(86400, int(time_left))
        
    await cache.set(alias, db_url.original_url, ex=cache_ttl)
    
    return RedirectResponse(url=db_url.original_url)