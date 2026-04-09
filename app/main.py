from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Database and ORM imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import engine, Base, AsyncSessionLocal
from app.models.url import URLMapping

# --- 1. HASH GENERATION LOGIC (BASE62) ---
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(BASE62_ALPHABET)

def encode_base62(num: int) -> str:
    """Converts a base-10 integer to a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    
    base62_str = []
    while num > 0:
        rem = num % BASE
        base62_str.append(BASE62_ALPHABET[rem])
        num = num // BASE
    
    return "".join(reversed(base62_str))

# Counter (Temporary until we build the standalone KGS tomorrow)
current_id_counter = 100000 

class URLRequest(BaseModel):
    long_url: str

# --- 2. DEPENDENCY INJECTION ---
async def get_db():
    """Yields a database session and safely closes it after the request."""
    async with AsyncSessionLocal() as session:
        yield session

# --- 3. LIFESPAN & APP INIT ---
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

# --- 4. API ENDPOINTS ---

@app.post("/api/v1/shorten", status_code=201)
async def shorten_url(request: URLRequest, db: AsyncSession = Depends(get_db)):
    global current_id_counter
    
    # 1. Generate the alias
    url_id = current_id_counter
    current_id_counter += 1
    short_alias = encode_base62(url_id)
    
    # 2. Create the database record
    new_url = URLMapping(short_url=short_alias, original_url=request.long_url)
    db.add(new_url)
    
    # 3. Await the actual write to PostgreSQL
    await db.commit()
    await db.refresh(new_url)
    
    return {
        "short_url": f"http://localhost:8000/{short_alias}",
        "original_url": request.long_url
    }

@app.get("/{alias}")
async def redirect_to_url(alias: str, db: AsyncSession = Depends(get_db)):
    # 1. Query PostgreSQL for the alias
    result = await db.execute(select(URLMapping).where(URLMapping.short_url == alias))
    db_url = result.scalar_one_or_none()
    
    # 2. Handle missing aliases
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # 3. Perform the redirect
    return RedirectResponse(url=db_url.original_url)