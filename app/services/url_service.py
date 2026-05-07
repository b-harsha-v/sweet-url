import os
import re
import qrcode

from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URLMapping
from app.models.unused_key import UnusedKey
from app.db.redis_client import cache


async def create_short_url(request, db: AsyncSession, current_user):

    short_alias = None

    # CUSTOM ALIAS LOGIC
    if request.custom_alias:

        short_alias = request.custom_alias.strip()
        short_alias = short_alias.replace(" ", "-")
        short_alias = re.sub(r"[^a-zA-Z0-9_-]", "", short_alias)
        short_alias = short_alias.lower()

        if not short_alias:
            raise HTTPException(
                status_code=400,
                detail="Invalid custom alias."
            )

        result = await db.execute(
            select(URLMapping).where(
                URLMapping.short_url == short_alias
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Custom alias is already taken."
            )

    else:

        stmt = select(UnusedKey).with_for_update(
            skip_locked=True
        ).limit(1)

        result = await db.execute(stmt)

        unused_key_obj = result.scalar_one_or_none()

        if not unused_key_obj:
            raise HTTPException(
                status_code=500,
                detail="Key pool exhausted!"
            )

        short_alias = unused_key_obj.key

        await db.delete(unused_key_obj)

    # EXPIRATION LOGIC
    expires_at = None
    cache_ttl = 86400

    if request.expires_in_hours:

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(hours=request.expires_in_hours)
        )

        cache_ttl = min(
            cache_ttl,
            request.expires_in_hours * 3600
        )

    # SAVE TO DB
    new_url = URLMapping(
        short_url=short_alias,
        original_url=request.long_url,
        expires_at=expires_at,
        user_id=current_user.id
    )

    db.add(new_url)

    await db.commit()

    # CACHE
    await cache.set(
        short_alias,
        request.long_url,
        ex=cache_ttl
    )

    # BASE URL
    base_url = os.getenv(
        "BASE_URL",
        "https://sweet-url.duckdns.org"
    )

    short_url_full = f"{base_url}/{short_alias}"

    # QR GENERATION
    qr = qrcode.make(short_url_full)

    os.makedirs("static/qr", exist_ok=True)

    qr_path = f"static/qr/{short_alias}.png"

    qr.save(qr_path)

    return {
        "short_url": short_url_full,
        "original_url": request.long_url,
        "expires_at": expires_at,
        "qr_code": f"{base_url}/{qr_path}"
    }