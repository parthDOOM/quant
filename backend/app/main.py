"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A modular quantitative analysis platform for portfolio optimization, "
                "statistical arbitrage, and options risk assessment.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security: Add trusted host middleware (restrict which hostnames are allowed)
# In production, restrict to your domain only
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "www.yourdomain.com", "api.yourdomain.com"]
    )


# Security: Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Strict transport security (HTTPS only) - only in production
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy - Allow Swagger UI resources
    # For /docs and /redoc endpoints, we need to allow external CDN resources
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://cdn.jsdelivr.net"
        )
    else:
        # Stricter CSP for regular API endpoints
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


# Security: Add request size limit middleware (prevent large payload DoS)
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request body size to prevent memory exhaustion attacks."""
    # Skip OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB limit
    
    content_length = request.headers.get("content-length")
    if content_length:
        content_length = int(content_length)
        if content_length > MAX_REQUEST_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Request body too large. Maximum size: {MAX_REQUEST_SIZE} bytes"
            )
    
    return await call_next(request)


# Security: Add request timing middleware (helps detect performance issues/attacks)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and log slow requests."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests (potential attack or performance issue)
    if process_time > 5.0:  # 5 seconds threshold
        logger.warning(
            f"Slow request detected: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response


# Security: Global exception handler to prevent information leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions without exposing sensitive information."""
    # Log the full error server-side
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True
    )
    
    # Return generic error to client (don't expose internal details)
    if settings.environment == "production":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred. Please try again later."
            }
        )
    else:
        # In development, show more details for debugging
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"{type(exc).__name__}: {str(exc)}"
            }
        )


@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    # TODO: Initialize Redis connection pool
    # TODO: Initialize database connection


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    logger.info("Shutting down application")
    # TODO: Close Redis connections
    # TODO: Close database connections


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "api": "operational",
        # TODO: Add Redis health check
        # TODO: Add database health check
    }


# Include routers
from app.routers import hrp, statarb, iv_surface

app.include_router(hrp.router, prefix="/hrp", tags=["HRP Analysis"])
app.include_router(statarb.router, prefix="/stat-arb", tags=["Statistical Arbitrage"])
app.include_router(iv_surface.router, tags=["Implied Volatility Surface"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
