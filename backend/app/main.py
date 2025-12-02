from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import gauges, predictions, websocket, historical  # Add historical
from app.config import settings
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Flood Prediction System...")
    logger.info(f"Environment: {settings.log_level}")

    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    logger.info("System startup complete")

    yield

    logger.info("Shutting down...")

app = FastAPI(
    title="Urban Flood Prediction API",
    version="1.0.0",
    description="Real-time flood prediction and monitoring system",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ['*'] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(gauges.router, prefix="/api/gauges", tags=["gauges"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(historical.router, prefix="/api/historical", tags=["historical"])  # Add this
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {
        "service": "Flood Prediction API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "flood-prediction-api"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )