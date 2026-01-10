from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import gauges, predictions, websocket, historical
from app.config import settings
from app.utils.logger import setup_logging
from app.tasks.scheduled_tasks import start_scheduler, stop_scheduler

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
        
        # Start scheduler
        start_scheduler()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    logger.info("System startup complete")
    
    yield
    
    logger.info("Shutting down...")
    stop_scheduler()

# ADD THIS NEW MIDDLEWARE CLASS
class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip for websockets
        if request.scope["type"] == "websocket":
            return await call_next(request)

        # Get the path
        path = request.scope["path"]
        
        # If path ends with / and is not root, remove it
        if path != "/" and path.endswith("/"):
            request.scope["path"] = path.rstrip("/")
        
        response = await call_next(request)
        return response

class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Trust the X-Forwarded-Proto header from Nginx
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto:
            request.scope["scheme"] = forwarded_proto
        
        response = await call_next(request)
        return response

app = FastAPI(
    title="Urban Flood Prediction API",
    version="1.0.0",
    description="Real-time flood prediction and monitoring system",
    lifespan=lifespan,
    redirect_slashes=False
)

# Add middlewares in order (IMPORTANT: Order matters!)
app.add_middleware(TrailingSlashMiddleware)  # ADD THIS FIRST
app.add_middleware(ProxyHeadersMiddleware)

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
app.include_router(historical.router, prefix="/api/historical", tags=["historical"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocket"])

@app.get("/api")
async def root():
    return {
        "service": "Flood Prediction API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/health")
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