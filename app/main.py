import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_plugins import redis_plugin
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.exceptions import ObjectDoesNotExist
from app.db import create_tables
from app.sse.notifications import sse_router

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.mount("/static/", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(ObjectDoesNotExist)
async def object_not_found_handler(_: Request, exc: ObjectDoesNotExist):
    return JSONResponse(status_code=404, content={"detail": exc.message})


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def on_startup() -> None:
    create_tables()
    await redis_plugin.init_app(app)
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(sse_router, prefix="/sse")


STREAM_DELAY = 3  # second
RETRY_TIMEOUT = 15000  # millisecond


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
