import os

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.user import User
from app.utils.security import create_access_token
from app.utils.dependencies import get_current_user

router = APIRouter()


oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/login/google")
async def login_google(request: Request):

    redirect_uri = (
    f"{os.getenv('BASE_URL')}/auth/google/callback"
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@router.get("/auth/google/callback")
async def auth_google(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    token = await oauth.google.authorize_access_token(
        request
    )

    user_info = token["userinfo"]

    google_id = user_info["sub"]

    email = user_info["email"]

    result = await db.execute(
        select(User).where(
            User.google_id == google_id
        )
    )

    db_user = result.scalar_one_or_none()

    if not db_user:

        db_user = User(
            google_id=google_id,
            email=email
        )

        db.add(db_user)

        await db.commit()

        await db.refresh(db_user)

    jwt_token = create_access_token({
        "sub": str(db_user.id)
    })

    response = RedirectResponse(
        url="/"
    )

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )

    return response

@router.get("/me")
async def get_me(
    current_user = Depends(get_current_user)
):

    return {
        "email": current_user.email
    }