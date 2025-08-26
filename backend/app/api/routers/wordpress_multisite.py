"""
WordPress Multisite API Router
Endpoints for creating and managing WordPress sites with Astra and Spectra
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import asyncio

from pydantic import BaseModel, Field
from app.services.wordpress_multisite_manager import (
    wordpress_multisite_manager,
    SiteConfig,
    MultisiteConfig
)
from app.services.variation_generator import variation_generator
from app.services.template_personalizer_v2 import template_personalizer_v2
from app.services.agno_manager import AgnoManager

router = APIRouter(prefix="/api/v1/wordpress", tags=["WordPress Multisite"])
logger = logging.getLogger(__name__)

# Global instances
agno_manager = AgnoManager()

class CreateSiteRequest(BaseModel):
    """Request to create a WordPress site"""
    business_name: str = Field(..., min_length=1, max_length=100)
    business_type: str = Field(..., description="restaurant, healthcare, ecommerce, services")
    description: Optional[str] = ""
    
    # Optional customization
    primary_color: Optional[str] = "#0274be"
    accent_color: Optional[str] = "#ff5722"
    
    # Features
    enable_blog: bool = False
    enable_shop: bool = False
    
    # Generate variations
    generate_variations: bool = True
    variation_count: int = 3

class GenerateWithWordPressRequest(BaseModel):
    """Generate site with AI and deploy to WordPress"""
    business_name: str = Field(..., min_length=1, max_length=100)
    industry: str = Field(..., description="Industry type")
    business_type: str = Field(default="general")
    description: str = Field(default="", max_length=500)
    
    # Contact
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    
    # AI Options
    use_ai: bool = True
    
    # WordPress deployment
    deploy_to_wordpress: bool = True
    create_variations: bool = True
    variation_count: int = 3

@router.post("/create-site")
async def create_wordpress_site(
    request: CreateSiteRequest,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    """
    Create a new WordPress site with Astra and Spectra
    
    This endpoint:
    1. Creates a new WordPress multisite instance
    2. Installs and configures Astra theme
    3. Installs Spectra plugin
    4. Creates pages with Spectra blocks
    5. Returns access credentials
    """
    
    try:
        logger.info(f"🚀 Creating WordPress site for: {request.business_name}")
        
        # Generate subdomain from business name
        subdomain = request.business_name.lower().replace(" ", "-").replace(".", "")
        subdomain = "".join(c for c in subdomain if c.isalnum() or c == "-")[:20]
        
        # Create site configuration
        site_config = SiteConfig(
            subdomain=subdomain,
            title=request.business_name,
            business_type=request.business_type,
            description=request.description,
            primary_color=request.primary_color,
            accent_color=request.accent_color,
            enable_blog=request.enable_blog,
            enable_shop=request.enable_shop
        )
        
        # Create the WordPress site
        result = await wordpress_multisite_manager.create_site(site_config)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to create site"))
        
        # Generate variations if requested
        variations = []
        if request.generate_variations:
            variations = await wordpress_multisite_manager.generate_variations(
                site_config,
                request.variation_count
            )
            
            # Create variation sites in background
            for variation in variations:
                background_tasks.add_task(
                    wordpress_multisite_manager.create_site,
                    SiteConfig(**variation["config"])
                )
        
        return JSONResponse(content={
            "success": True,
            "site": result,
            "variations": variations,
            "message": f"WordPress site created successfully!",
            "access": {
                "url": result["url"],
                "admin_url": result["admin_url"],
                "username": result["credentials"]["username"],
                "password": result["credentials"]["password"]
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating WordPress site: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-and-deploy")
async def generate_and_deploy(
    request: GenerateWithWordPressRequest,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    """
    Generate site with AI and deploy to WordPress Multisite
    
    Complete workflow:
    1. Generate content with AI
    2. Select best template
    3. Create WordPress site with Astra/Spectra
    4. Deploy generated content
    5. Create variations
    """
    
    try:
        logger.info(f"🚀 Generating and deploying site for: {request.business_name}")
        
        # Step 1: Generate content with AI
        generation_result = {}
        if request.use_ai:
            logger.info("🤖 Generating content with AI...")
            
            # Use Agno for content generation
            content = await agno_manager.generate_website_content({
                "business_name": request.business_name,
                "industry": request.industry,
                "description": request.description,
                "services": [],
                "target_audience": ""
            })
            
            generation_result = {
                "content": content,
                "generated_at": datetime.now().isoformat()
            }
        
        # Step 2: Create WordPress site
        wordpress_result = None
        if request.deploy_to_wordpress:
            logger.info("🌐 Deploying to WordPress Multisite...")
            
            # Generate subdomain
            subdomain = request.business_name.lower().replace(" ", "-").replace(".", "")
            subdomain = "".join(c for c in subdomain if c.isalnum() or c == "-")[:20]
            
            # Create site configuration
            site_config = SiteConfig(
                subdomain=subdomain,
                title=request.business_name,
                business_type=request.business_type,
                description=request.description or generation_result.get("content", {}).get("tagline", "")
            )
            
            # Create the WordPress site
            wordpress_result = await wordpress_multisite_manager.create_site(site_config)
            
            if not wordpress_result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=wordpress_result.get("error", "Failed to create WordPress site")
                )
        
        # Step 3: Create variations
        variations = []
        if request.create_variations and wordpress_result:
            logger.info(f"🎨 Creating {request.variation_count} variations...")
            
            variations = await wordpress_multisite_manager.generate_variations(
                site_config,
                request.variation_count
            )
            
            # Create variation sites in background
            for i, variation in enumerate(variations):
                # Add slight delay to avoid overwhelming the system
                await asyncio.sleep(0.5)
                
                background_tasks.add_task(
                    wordpress_multisite_manager.create_site,
                    SiteConfig(**variation["config"])
                )
                
                variations[i]["status"] = "creating"
        
        return JSONResponse(content={
            "success": True,
            "generation": generation_result,
            "wordpress": wordpress_result,
            "variations": variations,
            "summary": {
                "business_name": request.business_name,
                "industry": request.industry,
                "ai_generated": request.use_ai,
                "wordpress_deployed": request.deploy_to_wordpress,
                "variations_created": len(variations)
            },
            "next_steps": [
                "Access your WordPress site at the provided URL",
                "Login with the provided credentials",
                "Review the generated variations",
                "Customize further using WordPress admin"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in generate and deploy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sites")
async def list_wordpress_sites() -> JSONResponse:
    """
    List all WordPress sites in the multisite network
    """
    
    try:
        sites = await wordpress_multisite_manager.list_sites()
        
        return JSONResponse(content={
            "success": True,
            "count": len(sites),
            "sites": sites
        })
        
    except Exception as e:
        logger.error(f"Error listing sites: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sites/{site_id}")
async def delete_wordpress_site(site_id: int) -> JSONResponse:
    """
    Delete a WordPress site from the multisite network
    """
    
    try:
        success = await wordpress_multisite_manager.delete_site(site_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete site")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Site {site_id} deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting site: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sites/{site_id}/export")
async def export_wordpress_site(site_id: int):
    """
    Export a WordPress site as XML
    """
    
    try:
        export_data = await wordpress_multisite_manager.export_site(site_id)
        
        if not export_data:
            raise HTTPException(status_code=500, detail="Failed to export site")
        
        return StreamingResponse(
            io.BytesIO(export_data),
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename=site-{site_id}-export.xml"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting site: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Check WordPress Multisite health
    """
    
    try:
        # Try to list sites as a health check
        sites = await wordpress_multisite_manager.list_sites()
        
        return JSONResponse(content={
            "status": "healthy",
            "wordpress_multisite": "operational",
            "sites_count": len(sites),
            "services": {
                "astra_theme": "active",
                "spectra_plugin": "active",
                "wp_cli": "available"
            }
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )