from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from app.utils.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select

from app.models.url import URLMapping
from app.db.redis_client import cache

from datetime import datetime, timezone
from app.db.database import AsyncSessionLocal
from app.schemas.url import URLRequest

from app.services.url_service import create_short_url

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/api/v1/shorten", status_code=201)
async def shorten_url(
    request: URLRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return await create_short_url(
        request=request,
        db=db,
        current_user=current_user
    )

@router.get("/{alias}")
async def redirect_to_url(
    alias: str,
    db: AsyncSession = Depends(get_db)
):

    # CACHE CHECK
    cached_url = await cache.get(alias)

    if cached_url:

        return RedirectResponse(
            url=cached_url
        )

    # DATABASE LOOKUP
    result = await db.execute(
        select(URLMapping).where(
            URLMapping.short_url == alias
        )
    )

    db_url = result.scalar_one_or_none()

    if not db_url:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    # EXPIRATION CHECK
    if (
        db_url.expires_at
        and
        db_url.expires_at.replace(
            tzinfo=timezone.utc
        ) < datetime.now(timezone.utc)
    ):

        raise HTTPException(
            status_code=410,
            detail="URL expired"
        )

    # CACHE WARM
    await cache.set(
        alias,
        db_url.original_url,
        ex=86400
    )

    return RedirectResponse(
        url=db_url.original_url
    )