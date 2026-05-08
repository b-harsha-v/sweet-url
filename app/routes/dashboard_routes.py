from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi.templating import Jinja2Templates

from app.db.database import AsyncSessionLocal
from app.models.url import URLMapping
from app.utils.dependencies import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    result = await db.execute(
        select(URLMapping)
        .where(
            URLMapping.user_id == current_user.id
        )
        .order_by(
            URLMapping.created_at.desc()
        )
    )

    urls = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "urls": urls,
            "user": current_user
        }
    )


@router.post("/delete/{url_id}")
async def delete_url(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    result = await db.execute(
        select(URLMapping).where(
            URLMapping.id == url_id,
            URLMapping.user_id == current_user.id
        )
    )

    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    await db.delete(url)

    await db.commit()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )