"""
backend/app/main.py
Main FastAPI application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
from app.config import get_settings
from app.api import trends, products, alerts
from app.utils.logger import get_logger
from app.utils.metrics import MetricsCollector

settings = get_settings()
logger = get_logger(__name__)
metrics = MetricsCollector()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered shopping trend analysis across multiple platforms"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Middleware for metrics
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Record metrics
    metrics.record_api_call(
        endpoint=request.url.path,
        duration_ms=process_time,
        status_code=response.status_code
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# Include routers
app.include_router(trends.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)

# Frontend routes
@app.get("/")
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/merchant")
async def merchant_dashboard(request: Request):
    """Merchant dashboard"""
    return templates.TemplateResponse("merchant_dashboard.html", {"request": request})

@app.get("/consumer")
async def consumer_dashboard(request: Request):
    """Consumer dashboard"""
    return templates.TemplateResponse("consumer_dashboard.html", {"request": request})

@app.get("/demo")
async def demo(request: Request):
    """Interactive demo"""
    return templates.TemplateResponse("demo.html", {"request": request})

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }

# API info
@app.get(f"{settings.API_V1_PREFIX}/info")
async def api_info():
    """API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "trends": f"{settings.API_V1_PREFIX}/trends",
            "products": f"{settings.API_V1_PREFIX}/products",
            "alerts": f"{settings.API_V1_PREFIX}/alerts"
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
