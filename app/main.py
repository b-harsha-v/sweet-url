from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.db.database import engine, Base
from app.routes.url_routes import router as url_router
from app.routes.auth_routes import router as auth_router
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Enterprise URL Shortener",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key="super-secret-session-key")

app.include_router(auth_router)
app.include_router(url_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def serve_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )