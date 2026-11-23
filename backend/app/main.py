"""
BloodBridge FastAPI Application Entrypoint.

Emergency blood coordination platform for Peshawar, Khyber Pakhtunkhwa.
Provides secure REST APIs, role-based authorization, rate limiting,
and the intelligent donor matching engine.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.blood_banks import router as blood_banks_router
from app.api.blood_requests import router as blood_requests_router
from app.api.donors import router as donors_router
from app.api.notifications import router as notifications_router
from app.api.public import router as public_router
from app.core.config import get_settings
from app.core.exceptions import BloodBridgeException
from app.core.logging import get_logger, setup_logging
from app.core.security import limiter

logger = get_logger("bloodbridge.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown routines."""
    setup_logging()
    settings = get_settings()
    logger.info(
        "bloodbridge_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        city="Peshawar",
    )
    yield
    logger.info("bloodbridge_shutdown")


settings = get_settings()

app = FastAPI(
    title="BloodBridge API — Peshawar Emergency Network",
    description=(
        "Production-grade REST API powering the AI-enabled emergency blood coordination platform "
        "for Peshawar, Khyber Pakhtunkhwa, Pakistan. Connects patients with compatible registered donors "
        "and verified institutional blood banks."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Custom application exception handler
@app.exception_handler(BloodBridgeException)
async def bloodbridge_exception_handler(request: Request, exc: BloodBridgeException) -> JSONResponse:
    """Handle custom BloodBridge exceptions with structured error responses."""
    logger.warning(
        "application_exception",
        error_type=exc.__class__.__name__,
        message=exc.message,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "success": False,
        },
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(donors_router)
app.include_router(blood_requests_router)
app.include_router(blood_banks_router)
app.include_router(notifications_router)
app.include_router(admin_router)


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Health status probe for deployment monitors."""
    return {
        "status": "healthy",
        "service": "BloodBridge API",
        "city": "Peshawar, PK",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"])
async def root() -> dict:
    """Root metadata discovery endpoint."""
    return {
        "platform": "BloodBridge",
        "tagline": "Connecting Lives. One Donation at a Time.",
        "region": "Peshawar, Khyber Pakhtunkhwa, Pakistan",
        "documentation": "/docs",
        "status": "active",
    }
