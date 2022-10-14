import asyncio
import time

import aioredis
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi_plugins import redis_plugin
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.sse.notifications import sse_router
from app.db import create_tables

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.mount("/static/", StaticFiles(directory="app/static"), name="static")


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
    app.redis = aioredis.from_url("redis://localhost")
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(sse_router, prefix="/sse")


STREAM_DELAY = 3  # second
RETRY_TIMEOUT = 15000  # millisecond


@app.get("/stream")
async def message_stream(request: Request):
    def new_messages():
        # Add logic here to check for new messages
        yield "Hello World"

    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                yield {
                    "event": "new_message",
                    "id": "message_id",
                    "retry": RETRY_TIMEOUT,
                    "data": "message_content",
                }

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
