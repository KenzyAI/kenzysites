"""
WordPress AI SaaS - FastAPI Backend with Agno Framework
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from contextlib import asynccontextmanager

# Import our AI agents and routers
from app.core.config import settings
from app.api.routers import content, sites, ai_credits, health
from app.services.agno_manager import AgnoManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting WordPress AI SaaS Backend with Agno Framework")
    
    # Initialize Agno Manager
    agno_manager = AgnoManager()
    await agno_manager.initialize()
    app.state.agno_manager = agno_manager
    
    logger.info("✅ Agno Framework initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down WordPress AI SaaS Backend")
    await agno_manager.cleanup()
    logger.info("✅ Cleanup completed")

# Create FastAPI application
app = FastAPI(
    title="WordPress AI SaaS",
    description="AI-powered WordPress site generation and management platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(sites.router, prefix="/api/v1/sites", tags=["sites"])
app.include_router(ai_credits.router, prefix="/api/v1/ai-credits", tags=["ai-credits"])

# Import and include billing router
from app.api.routers import billing
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])

# Import and include analytics router
from app.api.routers import analytics
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# Import and include landing pages router (V1 - Mock)
from app.api.routers import landing_pages
app.include_router(landing_pages.router, prefix="/api/v1/landing-pages", tags=["landing-pages"])

# Import and include landing pages V2 router (Bolt.DIY)
from app.api.routers import landing_pages_v2
app.include_router(landing_pages_v2.router, prefix="/api/v2/landing-pages", tags=["landing-pages-v2"])

# Import and include content automation router
from app.api.routers import content_automation
app.include_router(content_automation.router, prefix="/api/v1/content-automation", tags=["content-automation"])

# Import and include customer portal router
from app.api.routers import customer_portal
app.include_router(customer_portal.router, prefix="/api/v1/portal", tags=["customer-portal"])

# Import and include site cloner router
from app.api.routers import site_cloner
app.include_router(site_cloner.router, prefix="/api/v1/cloner", tags=["site-cloner"])

# Import and include Stripe payments router
from app.api.routers import stripe_payments
app.include_router(stripe_payments.router, prefix="/api/v1/stripe", tags=["stripe-payments"])

# Import and include white label router
from app.api.routers import white_label
app.include_router(white_label.router, prefix="/api/v1/white-label", tags=["white-label"])

# Import and include marketing router
from app.api.routers import marketing
app.include_router(marketing.router, prefix="/api/v1/marketing", tags=["marketing"])

# Import and include site generation V2 router (MAIN GENERATION SYSTEM)
from app.api.routers import site_generation_v2
app.include_router(site_generation_v2.router, prefix="/api/v2/generation", tags=["site-generation-v2"])

# Import and include instant sites router
from app.api.routers import instant_sites
app.include_router(instant_sites.router, prefix="/api/instant", tags=["instant-sites"])

# Import and include templates router
from app.api.routers import templates
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "WordPress AI SaaS Backend",
        "version": "1.0.0",
        "framework": "Agno",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "WordPress AI SaaS Backend is running",
        "agno_status": "initialized"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG,
        log_level="info"
    )