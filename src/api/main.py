"""Main FastAPI application for Splunk Agentic AI API."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from config.config import config
from src.api.routes.query import router as query_router
from src.utils.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Splunk Agentic AI API...")
    
    # Validate configuration
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    logger.info("API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server...")

# Create FastAPI application
app = FastAPI(
    title="Splunk Agentic AI API",
    description="""
    A powerful API that converts natural language questions to SPL queries and executes them on Splunk.
    
    ## Features
    
    * **Natural Language Processing**: Convert English questions to SPL queries using OpenAI
    * **Direct SPL Execution**: Execute raw SPL queries directly
    * **Query Enhancement**: Improve existing queries based on feedback
    * **Query Suggestions**: Get suggested questions based on partial input
    * **Health Monitoring**: Check system component health
    * **Comprehensive Logging**: Detailed logging for debugging and monitoring
    
    ## Authentication
    
    This API uses Splunk token-based authentication or username/password.
    Configure your credentials in the environment variables.
    
    ## Rate Limits
    
    * Natural language queries: 60 per minute
    * SPL queries: 100 per minute
    * Health checks: Unlimited
    """,
    version="1.0.0",
    contact={
        "name": "Splunk Agentic AI Team",
        "email": "support@example.com"
    },
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"in {duration:.3f}s"
    )
    
    return response

# Include routers
app.include_router(query_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Splunk Agentic AI API",
        "version": "1.0.0",
        "description": "Natural language to SPL query conversion and execution",
        "docs_url": "/api/v1/docs",
        "health_url": "/api/v1/query/health",
        "endpoints": {
            "natural_language_query": "/api/v1/query/natural",
            "spl_query": "/api/v1/query/spl",
            "query_enhancement": "/api/v1/query/enhance",
            "query_suggestions": "/api/v1/query/suggestions",
            "health_check": "/api/v1/query/health",
            "get_indexes": "/api/v1/query/indexes",
            "search_history": "/api/v1/query/history"
        }
    }

# Global health check
@app.get("/health", tags=["health"])
async def global_health():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Splunk Agentic AI API"
    }

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError in {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "status_code": 400,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception in {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )

# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Splunk Agentic AI API",
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom schema information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://www.splunk.com/content/dam/splunk2/en_us/images/logos/splunk-logo.svg"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
