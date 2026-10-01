import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine, Base, SessionLocal
from .seed_data import ensure_demo_user
from .routers import (
    auth_routes, profile_routes, ideas_routes,
    briefs_routes, feedback_routes, workspace_routes
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("copilot")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed demo creator
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_demo_user(db)
        logger.info("Demo creator Rahul initialized successfully.")
    except Exception as e:
        logger.warning(f"Demo user seed warning: {e}")
    finally:
        db.close()
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Content Copilot for short-form video creators. Turn your niche, audience, and constraints into concrete shootable content.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe error handling (Section 22: Never expose raw stack traces)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later or contact support."}
    )

# Include routers
app.include_router(auth_routes.router, prefix=settings.API_V1_STR)
app.include_router(profile_routes.router, prefix=settings.API_V1_STR)
app.include_router(ideas_routes.router, prefix=settings.API_V1_STR)
app.include_router(briefs_routes.router, prefix=settings.API_V1_STR)
app.include_router(feedback_routes.router, prefix=settings.API_V1_STR)
app.include_router(workspace_routes.router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "active_provider": settings.AI_PROVIDER,
        "database": "connected"
    }

@app.get("/api/ai/diagnostic")
def ai_diagnostic():
    """
    Safe diagnostic endpoint per Section 30:
    Reports configured provider, model, key presence, fallback status,
    without ever printing or exposing the actual API key.
    """
    has_gemini_key = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 0)
    has_openai_key = bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 0)
    
    provider_pref = settings.AI_PROVIDER.lower().strip()
    if provider_pref == "gemini":
        active_model = "gemini-2.5-flash"
        key_present = has_gemini_key
    elif provider_pref == "openai":
        active_model = "gpt-4o-mini"
        key_present = has_openai_key
    elif provider_pref == "auto":
        if has_gemini_key:
            active_model = "gemini-2.5-flash"
            key_present = True
        elif has_openai_key:
            active_model = "gpt-4o-mini"
            key_present = True
        else:
            active_model = "creative-engine-v1"
            key_present = False
    else:
        active_model = "creative-engine-v1"
        key_present = False

    generation_success = key_present or settings.AI_FALLBACK_ON_ERROR or provider_pref in ["creative_engine", "auto"]
    fallback_used = not key_present and provider_pref in ["gemini", "openai"] and settings.AI_FALLBACK_ON_ERROR

    return {
        "provider": settings.AI_PROVIDER,
        "model": active_model,
        "key_present": key_present,
        "generation_success": generation_success,
        "fallback_used": fallback_used,
        "fallback_enabled": settings.AI_FALLBACK_ON_ERROR,
        "generation_status": "ready",
        "notice": "Never logs or exposes API keys. Trend data is unverified in MVP."
    }

# Frontend static serving if dist exists
DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        file_path = DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DIST_DIR / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to Influencer Help — AI Content Copilot API",
            "docs": "/docs",
            "health": "/api/health"
        }
