"""
WordPress AI SaaS - FastAPI Backend with Agno Framework v1.8.0
FASE 2: Integração completa com Agno Framework
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Phidata (formerly Agno) - if it fails, fall back to simple mode
try:
    from app.services.agno_manager import AgnoManager
    PHIDATA_AVAILABLE = True
    logger.info("✅ Phidata Framework available")
except ImportError as e:
    PHIDATA_AVAILABLE = False
    logger.warning(f"⚠️ Phidata Framework not available: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting WordPress AI SaaS Backend with Phidata Framework v2.6.0")
    
    if PHIDATA_AVAILABLE:
        try:
            # Initialize Agno Manager
            agno_manager = AgnoManager()
            await agno_manager.initialize()
            app.state.agno_manager = agno_manager
            app.state.agno_enabled = True
            logger.info("✅ Agno Framework initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Agno initialization failed: {e}")
            app.state.agno_manager = None
            app.state.agno_enabled = False
    else:
        app.state.agno_manager = None
        app.state.agno_enabled = False
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down WordPress AI SaaS Backend")
    if hasattr(app.state, 'agno_manager') and app.state.agno_manager:
        try:
            await app.state.agno_manager.cleanup()
            logger.info("✅ Agno cleanup completed")
        except:
            pass

# Create FastAPI application
app = FastAPI(
    title="WordPress AI SaaS",
    description="AI-powered WordPress site generation and management platform",
    version="1.8.0-with-agno",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Enhanced health check with Agno status"""
    agno_status = "enabled" if getattr(app.state, 'agno_enabled', False) else "disabled"
    
    return JSONResponse({
        "status": "healthy",
        "message": "KenzySites Backend is running",
        "version": "2.6.0-with-phidata",
        "phidata_framework": agno_status,
        "features": {
            "phidata_available": PHIDATA_AVAILABLE,
            "agno_initialized": getattr(app.state, 'agno_enabled', False),
            "ai_agents": getattr(app.state, 'agno_enabled', False),
        }
    })

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with enhanced info"""
    return JSONResponse({
        "message": "Welcome to KenzySites Backend with Agno Framework",
        "version": "1.8.0-with-agno",
        "agno_available": AGNO_AVAILABLE,
        "agno_enabled": getattr(app.state, 'agno_enabled', False),
        "docs": "/api/docs",
        "health": "/api/v1/health"
    })

# Agno status endpoint
@app.get("/api/v1/agno/status")
async def agno_status():
    """Get Agno Framework status"""
    if not AGNO_AVAILABLE:
        return JSONResponse({
            "agno_available": False,
            "message": "Agno Framework not installed",
            "suggestion": "Install with: pip install agno==1.8.0"
        })
    
    agno_manager = getattr(app.state, 'agno_manager', None)
    if not agno_manager:
        return JSONResponse({
            "agno_available": True,
            "agno_enabled": False,
            "message": "Agno Framework available but not initialized",
            "reason": "Likely missing API keys"
        })
    
    return JSONResponse({
        "agno_available": True,
        "agno_enabled": True,
        "agents_count": len(agno_manager.agents),
        "specialized_agents_count": len(agno_manager.specialized_agents),
        "primary_model": str(agno_manager.primary_model) if agno_manager.primary_model else None,
        "secondary_models_count": len(agno_manager.secondary_models),
    })

# Import and include routers
from app.api.routers import simple_landing_pages

# Include routers
app.include_router(
    simple_landing_pages.router, 
    prefix="/api/v1/simple-landing",
    tags=["Simple Landing Pages"]
)

# Test AI endpoint (if Agno is available)
@app.post("/api/v1/ai/test")
async def test_ai():
    """Test AI functionality"""
    if not getattr(app.state, 'agno_enabled', False):
        raise HTTPException(
            status_code=503,
            detail="Agno Framework not available. Check API keys and configuration."
        )
    
    try:
        agno_manager = app.state.agno_manager
        if "content_generator" in agno_manager.agents:
            # Test the content generation agent
            result = await agno_manager.agents["content_generator"].generate_response(
                "Test message for AI functionality"
            )
            return JSONResponse({
                "status": "success",
                "message": "AI test completed",
                "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            })
        else:
            return JSONResponse({
                "status": "partial",
                "message": "Agno available but no agents configured"
            })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"AI test failed: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)