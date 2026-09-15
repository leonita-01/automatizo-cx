import logging
import re
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .config import settings
from .database import SessionLocal, init_db
from .observability import configure_logging
from .routers import audit, chat, handoffs, knowledge, operations
from .seed import seed_knowledge_base


configure_logging()
logger = logging.getLogger("automatizocx.api")
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,80}$")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as database:
        seed_knowledge_base(database)
    logger.info("application_started")
    yield
    logger.info("application_stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    description=(
        "Secure multilingual customer-support automation, knowledge management, "
        "human handoff and process-assessment API."
    ),
    contact={"name": "Leonita Bahtiri"},
    license_info={"name": "MIT"},
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    supplied_request_id = request.headers.get("X-Request-ID", "")
    request_id = (
        supplied_request_id
        if REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
        else str(uuid4())
    )
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "unhandled_request_error", extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
        )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    duration_ms = round((perf_counter() - started_at) * 1000)
    logger.info(
        "%s %s %s %sms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={"request_id": request_id},
    )
    return response


@app.get("/api/health", tags=["Platform"])
def health():
    database_status = "healthy"
    try:
        with SessionLocal() as database:
            database.execute(text("SELECT 1"))
    except Exception:
        database_status = "unhealthy"
    status_code = 200 if database_status == "healthy" else 503
    payload = {
        "status": "healthy" if status_code == 200 else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "database": database_status,
        "environment": settings.environment,
    }
    return JSONResponse(status_code=status_code, content=payload)


app.include_router(chat.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")
app.include_router(operations.router, prefix="/api")
app.include_router(handoffs.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
