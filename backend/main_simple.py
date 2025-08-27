"""
Simplified WordPress AI SaaS - FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import random
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WordPress AI SaaS",
    description="SaaS platform for automated WordPress site creation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "WordPress AI SaaS Backend - Simplified"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "WordPress AI SaaS Backend",
        "version": "1.0.0-simple"
    }

@app.get("/api/v1/health")
async def health_check_v1():
    """Health check endpoint compatible with Render"""
    return {
        "status": "healthy",
        "service": "KenzySites Backend",
        "version": "1.0.0-simple",
        "mode": "simplified_without_agno",
        "timestamp": time.time()
    }

# Mock generation endpoint for demo
class GenerationRequest(BaseModel):
    business_name: str
    business_type: str
    business_description: Optional[str] = None
    services: Optional[List[str]] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = "São Paulo"
    primary_color: Optional[str] = "#0066ff"
    target_audience: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    features: Optional[Dict[str, bool]] = None
    
    model_config = {"extra": "allow"}

@app.post("/api/v2/generation/generate")
async def generate_site(request: GenerationRequest):
    """Generate AI site with variations"""
    
    # Simulate processing time
    time.sleep(2)
    
    # Generate mock variations
    variations = []
    templates = ["Modern", "Classic", "Minimal", "Bold", "Elegant"]
    
    for i, template in enumerate(random.sample(templates, 3)):
        variations.append({
            "id": f"var_{i+1}",
            "name": f"{template} Design",
            "description": f"Um design {template.lower()} perfeito para {request.business_name}",
            "preview_url": f"/preview/variation_{i+1}",
            "template": template.lower(),
            "features": {
                "responsive": True,
                "seo_optimized": True,
                "fast_loading": True,
                "whatsapp_integration": True,
                "pix_payment": request.features.get("pix", False) if request.features else False
            },
            "score": random.randint(85, 98),
            "estimated_time": f"{random.randint(30, 60)}s"
        })
    
    return {
        "success": True,
        "generation_id": f"gen_{int(time.time())}",
        "business_data": {
            "name": request.business_name,
            "type": request.business_type,
            "city": request.city
        },
        "variations": variations,
        "total_variations": len(variations),
        "processing_time": "2.5s",
        "cache_hit": False,
        "ai_provider": "mock"
    }

# Cache stats router
@app.get("/api/v2/generation/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "stats": {
            "connected_clients": 5,
            "used_memory": "12.4MB",
            "total_commands_processed": 15234,
            "keyspace_hits": 8756,
            "keyspace_misses": 2341,
            "hit_rate": "78.9%",
            "cache_type": "memory"
        },
        "key_counts": {
            "template_gen": 45,
            "variations": 123,
            "ai_response": 234,
            "wp_templates": 12,
            "session": 5,
            "generation_progress": 3
        },
        "total_keys": 422,
        "cache_status": "memory"
    }

@app.delete("/api/v2/generation/cache/clear")
async def clear_cache():
    """Clear cache"""
    return {
        "message": "Cache cleared successfully",
        "cleared": 422
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)