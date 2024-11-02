from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

from tasks_module.api import auth_api
from tasks_module.api import tasks_api
from tasks_module.models.database import engine, session, Base
from tasks_module.models.redis_client import RedisClient

load_dotenv()


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(auth_api.router, prefix="/auth", tags=["Auth"])
app.include_router(tasks_api.router, prefix="/tasks", tags=["Tasks"])


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await RedisClient.get_instance()


@app.on_event("shutdown")
async def shutdown():
    await session.close()
    await engine.dispose()
    await RedisClient.close()


@app.get("/")
async def root():
    return {"message": "Welcome to API"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
