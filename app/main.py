from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.api.routes_auth import router as auth_router
from app.api.routes_predict import router as predict_router
from app.utils.logger import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade API for Laptop Price Prediction with security, caching, logging, and monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Setup Exception Handlers
setup_exception_handlers(app)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(predict_router, prefix=settings.API_V1_STR)

# Initialize and expose Prometheus metrics endpoint '/metrics'
Instrumentator().instrument(app).expose(app)

@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}!",
        "status": "operational",
        "docs_url": "/docs",
        "metrics_url": "/metrics"
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI application...")
