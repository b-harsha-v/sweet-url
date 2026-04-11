from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import engine, Base, AsyncSessionLocal
from app.models.url import URLMapping
from app.models.unused_key import UnusedKey
from app.db.redis_client import cache

class URLRequest(BaseModel):
    long_url: str

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
    description="A high-throughput, low-latency URL shortening service.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/api/v1/shorten", status_code=201)
async def shorten_url(request: URLRequest, db: AsyncSession = Depends(get_db)):
    
    # 1. Grab an unused key safely using SKIP LOCKED to prevent race conditions
    stmt = select(UnusedKey).with_for_update(skip_locked=True).limit(1)
    result = await db.execute(stmt)
    unused_key_obj = result.scalar_one_or_none()
    
    if not unused_key_obj:
        raise HTTPException(status_code=500, detail="Key pool exhausted! Run the KGS worker.")
        
    short_alias = unused_key_obj.key
    
    # 2. Remove it from the pool
    await db.delete(unused_key_obj)
    
    # 3. Create the mapping in the main table
    new_url = URLMapping(short_url=short_alias, original_url=request.long_url)
    db.add(new_url)
    
    # 4. Commit the transaction (Atomically deletes from pool and adds to mapping)
    await db.commit()
    
    # 5. Proactively warm the cache so the very first click is O(1)
    await cache.set(short_alias, request.long_url, ex=86400)
    
    return {
        "short_url": f"http://localhost:8000/{short_alias}",
        "original_url": request.long_url
    }

@app.get("/{alias}")
async def redirect_to_url(alias: str, db: AsyncSession = Depends(get_db)):
    # CACHE CACHE CACHE
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
        
    # WARM CACHE FOR NEXT TIME
    await cache.set(alias, db_url.original_url, ex=86400)
    
    return RedirectResponse(url=db_url.original_url)