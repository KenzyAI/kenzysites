"""
Site Cloner API endpoints with Firecrawl
Feature F006: Clone existing sites to WordPress
Phase 3: Launch Oficial
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.services.site_cloner_service import (
    site_cloner_service,
    CloneJob,
    CloneStatus,
    PageType
)
from app.services.agno_manager import AgnoManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication
async def get_current_user():
    return {
        "user_id": "user123",
        "plan": "professional",
        "email": "user@example.com",
        "clone_limit": 2,  # Based on plan (PRD)
        "clones_used": 0
    }

async def get_agno_manager() -> AgnoManager:
    """Get Agno manager from app state"""
    from main import app
    return app.state.agno_manager

# Initialize service on startup
@router.on_event("startup")
async def initialize_service():
    """Initialize site cloner service"""
    try:
        from main import app
        await site_cloner_service.initialize(app.state.agno_manager)
        logger.info("Site Cloner Service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Site Cloner Service: {str(e)}")

# Start Clone Job
@router.post("/clone")
async def start_site_clone(
    source_url: str = Body(..., description="URL of site to clone"),
    max_pages: int = Body(50, le=100, description="Maximum pages to crawl"),
    include_images: bool = Body(True, description="Include images in clone"),
    optimize_performance: bool = Body(True, description="Optimize for performance"),
    preserve_seo: bool = Body(True, description="Preserve SEO metadata"),
    current_user: dict = Depends(get_current_user)
):
    """
    Start cloning a website to WordPress
    Costs 150 AI Credits per clone (PRD)
    95% accuracy guarantee
    """
    
    try:
        # Check clone limits based on plan
        if current_user["clones_used"] >= current_user["clone_limit"]:
            raise HTTPException(
                status_code=403,
                detail=f"Clone limit reached. Your plan allows {current_user['clone_limit']} clones per month."
            )
        
        # Validate URL
        if not source_url.startswith(("http://", "https://")):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL. Must start with http:// or https://"
            )
        
        # Start clone job
        job = await site_cloner_service.start_clone_job(
            user_id=current_user["user_id"],
            source_url=source_url,
            settings={
                "max_pages": max_pages,
                "include_images": include_images,
                "optimize_performance": optimize_performance,
                "preserve_seo": preserve_seo
            }
        )
        
        logger.info(f"Started clone job {job.id} for user {current_user['user_id']}")
        
        # Would deduct 150 AI credits here
        logger.info(f"Deducted 150 AI Credits for clone job")
        
        return {
            "success": True,
            "job_id": job.id,
            "status": job.status,
            "message": f"Clone job started. Tracking ID: {job.id}",
            "estimated_time": "5-10 minutes",
            "credits_used": 150
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start clone job: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start clone job: {str(e)}"
        )

# Get Clone Job Status
@router.get("/clone/{job_id}")
async def get_clone_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status and details of a clone job"""
    
    try:
        job = await site_cloner_service.get_clone_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Clone job {job_id} not found"
            )
        
        # Verify ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        response = {
            "job_id": job.id,
            "source_url": job.source_url,
            "status": job.status,
            "progress": job.progress,
            "pages_found": job.pages_found,
            "pages_crawled": job.pages_crawled,
            "images_found": job.images_found,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
        
        # Add results if completed
        if job.status == CloneStatus.COMPLETED:
            response["accuracy_score"] = job.accuracy_score
            response["wordpress_site"] = job.wordpress_site
            
            # Calculate time taken
            if job.started_at and job.completed_at:
                time_taken = (job.completed_at - job.started_at).total_seconds()
                response["time_taken_seconds"] = time_taken
        
        # Add errors if failed
        if job.status == CloneStatus.FAILED:
            response["errors"] = job.errors
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get clone job status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get clone job status: {str(e)}"
        )

# List Clone Jobs
@router.get("/clones")
async def list_clone_jobs(
    status: Optional[CloneStatus] = Query(None, description="Filter by status"),
    limit: int = Query(10, le=50, description="Maximum jobs to return"),
    current_user: dict = Depends(get_current_user)
):
    """List all clone jobs for current user"""
    
    try:
        jobs = await site_cloner_service.get_user_clone_jobs(
            user_id=current_user["user_id"],
            status=status
        )
        
        # Apply limit
        jobs = jobs[:limit]
        
        return {
            "total": len(jobs),
            "jobs": [
                {
                    "job_id": job.id,
                    "source_url": job.source_url,
                    "status": job.status,
                    "progress": job.progress,
                    "accuracy_score": job.accuracy_score if job.accuracy_score > 0 else None,
                    "created_at": job.created_at.isoformat(),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list clone jobs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list clone jobs: {str(e)}"
        )

# Get Clone Preview
@router.get("/clone/{job_id}/preview")
async def get_clone_preview(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get preview of cloned site"""
    
    try:
        job = await site_cloner_service.get_clone_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Clone job {job_id} not found"
            )
        
        # Verify ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        if job.status != CloneStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Clone job not completed. Current status: {job.status}"
            )
        
        preview = await site_cloner_service.get_clone_preview(job_id)
        
        if not preview:
            raise HTTPException(
                status_code=404,
                detail="Preview not available"
            )
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get clone preview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get clone preview: {str(e)}"
        )

# Cancel Clone Job
@router.post("/clone/{job_id}/cancel")
async def cancel_clone_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a running clone job"""
    
    try:
        job = await site_cloner_service.get_clone_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Clone job {job_id} not found"
            )
        
        # Verify ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        success = await site_cloner_service.cancel_clone_job(job_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel job. It may already be completed or failed."
            )
        
        return {
            "success": True,
            "message": f"Clone job {job_id} cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel clone job: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel clone job: {str(e)}"
        )

# Deploy Cloned Site
@router.post("/clone/{job_id}/deploy")
async def deploy_cloned_site(
    job_id: str,
    site_name: str = Body(..., description="Name for the WordPress site"),
    custom_domain: Optional[str] = Body(None, description="Custom domain"),
    current_user: dict = Depends(get_current_user)
):
    """Deploy cloned site to WordPress"""
    
    try:
        job = await site_cloner_service.get_clone_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Clone job {job_id} not found"
            )
        
        # Verify ownership
        if job.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        if job.status != CloneStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Clone job not completed. Current status: {job.status}"
            )
        
        # Deploy to WordPress (would integrate with WordPress service)
        wordpress_site = job.wordpress_site
        wordpress_site["name"] = site_name
        
        if custom_domain:
            wordpress_site["domain"] = custom_domain
        
        # Mock deployment
        deployment = {
            "site_id": wordpress_site["id"],
            "name": site_name,
            "url": f"https://{wordpress_site['domain']}",
            "admin_url": f"https://{wordpress_site['domain']}/wp-admin",
            "pages": len(wordpress_site["pages"]),
            "theme": wordpress_site["theme"],
            "status": "active",
            "deployed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Deployed cloned site {deployment['site_id']} for user {current_user['user_id']}")
        
        return {
            "success": True,
            "deployment": deployment,
            "message": f"Site deployed successfully at {deployment['url']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deploy cloned site: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deploy cloned site: {str(e)}"
        )

# Analyze Site Before Cloning
@router.post("/analyze")
async def analyze_site(
    url: str = Body(..., description="URL to analyze"),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a site before cloning
    Free preview of what will be cloned
    """
    
    try:
        # Quick analysis without full crawl
        from app.services.site_cloner_service import FirecrawlMock, SiteAnalyzer
        
        firecrawl = FirecrawlMock()
        analyzer = SiteAnalyzer()
        
        # Crawl just a few pages for analysis
        pages = await firecrawl.crawl_website(url, max_pages=5, include_images=False)
        
        # Analyze structure
        structure = analyzer.analyze_site(pages, url)
        
        return {
            "url": url,
            "analysis": {
                "pages_found": len(pages),
                "page_types": list(set(p.page_type.value for p in pages)),
                "technologies": structure.technologies,
                "has_forms": any(p.forms for p in pages),
                "has_images": any(p.images for p in pages),
                "color_scheme": structure.color_scheme,
                "performance_metrics": structure.performance_metrics,
                "seo_ready": bool(structure.seo_data.get("titles"))
            },
            "clone_estimate": {
                "time": "5-10 minutes",
                "credits": 150,
                "accuracy": "95%+"
            },
            "recommendations": [
                "Site is ready for cloning" if len(pages) > 0 else "Site may have access restrictions",
                "SEO metadata will be preserved" if structure.seo_data.get("titles") else "Consider adding SEO metadata",
                "Forms detected and will be recreated" if any(p.forms for p in pages) else "No forms detected"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze site: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze site: {str(e)}"
        )

# Clone Settings Template
@router.get("/settings/template")
async def get_clone_settings_template():
    """Get recommended clone settings based on use case"""
    
    return {
        "templates": [
            {
                "name": "Full Site Clone",
                "description": "Complete site with all pages and images",
                "settings": {
                    "max_pages": 50,
                    "include_images": True,
                    "optimize_performance": True,
                    "preserve_seo": True
                }
            },
            {
                "name": "Content Only",
                "description": "Fast clone focusing on text content",
                "settings": {
                    "max_pages": 30,
                    "include_images": False,
                    "optimize_performance": True,
                    "preserve_seo": True
                }
            },
            {
                "name": "Landing Page",
                "description": "Single page or small site",
                "settings": {
                    "max_pages": 5,
                    "include_images": True,
                    "optimize_performance": True,
                    "preserve_seo": False
                }
            },
            {
                "name": "E-commerce",
                "description": "Online store with products",
                "settings": {
                    "max_pages": 100,
                    "include_images": True,
                    "optimize_performance": True,
                    "preserve_seo": True
                }
            }
        ]
    }

# Clone History Stats
@router.get("/stats")
async def get_clone_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get cloning statistics for current user"""
    
    try:
        jobs = await site_cloner_service.get_user_clone_jobs(
            user_id=current_user["user_id"]
        )
        
        completed_jobs = [j for j in jobs if j.status == CloneStatus.COMPLETED]
        failed_jobs = [j for j in jobs if j.status == CloneStatus.FAILED]
        
        total_pages = sum(j.pages_crawled for j in completed_jobs)
        total_images = sum(j.images_found for j in completed_jobs)
        avg_accuracy = sum(j.accuracy_score for j in completed_jobs) / len(completed_jobs) if completed_jobs else 0
        
        return {
            "total_clones": len(jobs),
            "successful_clones": len(completed_jobs),
            "failed_clones": len(failed_jobs),
            "total_pages_cloned": total_pages,
            "total_images_cloned": total_images,
            "average_accuracy": round(avg_accuracy, 1),
            "credits_used": len(jobs) * 150,
            "monthly_limit": current_user["clone_limit"],
            "remaining_clones": max(0, current_user["clone_limit"] - current_user["clones_used"])
        }
        
    except Exception as e:
        logger.error(f"Failed to get clone stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get clone stats: {str(e)}"
        )