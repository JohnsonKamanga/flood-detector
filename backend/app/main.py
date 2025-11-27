from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routes import gauges, predictions, websocket
from app.services.data_ingestion import DataIngestionService
from app.tasks.scheduled_tasks import start_scheduler
from app.utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Flood Prediction System...")
    
    # GeoPandas check removed (using pure Python implementation)
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background tasks
    start_scheduler()
    
    # Initialize data ingestion
    ingestion_service = DataIngestionService()
    await ingestion_service.start()
    
    logger.info("System startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await ingestion_service.stop()

app = FastAPI(
    title="Urban Flood Prediction API",
    version="1.0.0",
    description="Real-time flood prediction and monitoring system",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(gauges.router, prefix="/api/gauges", tags=["gauges"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "flood-prediction-api"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )