"""
Content Generation API endpoints using Agno Framework
Implements Feature F007: Content Generation Engine
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import asyncio
import logging

from app.models.ai_models import (
    ContentGenerationRequest,
    BatchContentRequest,
    AIResponse,
    GeneratedContent,
    BatchProcessingStatus
)
from app.services.agno_manager import AgnoManager

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_agno_manager() -> AgnoManager:
    """Dependency to get Agno manager"""
    from main import app
    return app.state.agno_manager

# Mock user data - in production this would come from authentication
async def get_current_user():
    return {"user_id": "user123", "plan": "professional"}

@router.post("/generate", response_model=AIResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user),
    agno_manager: AgnoManager = Depends(get_agno_manager)
):
    """
    Generate content using Agno Framework
    Costs 20 AI Credits per blog post (PRD section 6.2)
    """
    
    try:
        logger.info(f"Content generation request from user {current_user['user_id']}")
        logger.info(f"Request: {request.content_type} - {request.topic}")
        
        # Use Agno Manager to generate content
        response = await agno_manager.generate_content(
            request=request,
            user_id=current_user["user_id"],
            user_plan=current_user["plan"]
        )
        
        if response.success:
            logger.info(f"Content generated successfully. Credits used: {response.credits_used}")
        else:
            logger.warning(f"Content generation failed: {response.message}")
        
        return response
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/generate/batch", response_model=Dict[str, Any])
async def generate_content_batch(
    request: BatchContentRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    agno_manager: AgnoManager = Depends(get_agno_manager)
):
    """
    Generate multiple pieces of content in batch
    Useful for content calendar automation
    """
    
    # Validate batch size (max 10 items)
    if len(request.requests) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 items allowed per batch"
        )
    
    # Calculate total credits required
    total_credits = len(request.requests) * 20  # 20 credits per blog post
    
    job_id = f"batch_{current_user['user_id']}_{int(asyncio.get_event_loop().time())}"
    
    # Start batch processing in background
    background_tasks.add_task(
        process_content_batch,
        job_id=job_id,
        requests=request.requests,
        user_id=current_user["user_id"],
        user_plan=current_user["plan"],
        agno_manager=agno_manager
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "total_items": len(request.requests),
        "estimated_credits": total_credits,
        "message": "Batch processing started. Check status with job_id."
    }

async def process_content_batch(
    job_id: str,
    requests: List[ContentGenerationRequest],
    user_id: str,
    user_plan: str,
    agno_manager: AgnoManager
):
    """Background task for batch content processing"""
    
    logger.info(f"Starting batch job {job_id} with {len(requests)} items")
    
    results = []
    for i, request in enumerate(requests):
        try:
            response = await agno_manager.generate_content(
                request=request,
                user_id=user_id,
                user_plan=user_plan
            )
            results.append(response)
            logger.info(f"Batch job {job_id}: Completed item {i+1}/{len(requests)}")
            
        except Exception as e:
            logger.error(f"Batch job {job_id}: Failed item {i+1}: {str(e)}")
            results.append(
                AIResponse(
                    success=False,
                    message=f"Failed: {str(e)}",
                    credits_used=0
                )
            )
    
    # Store results (would use Redis/database in production)
    logger.info(f"Batch job {job_id} completed. {len([r for r in results if r.success])} successful")

@router.get("/batch/{job_id}/status", response_model=BatchProcessingStatus)
async def get_batch_status(job_id: str):
    """Get status of batch processing job"""
    
    # In production, this would query actual job status from database/Redis
    return BatchProcessingStatus(
        job_id=job_id,
        total_items=5,  # Placeholder
        completed_items=3,  # Placeholder
        failed_items=0,
        status="processing"
    )

@router.post("/optimize-seo", response_model=AIResponse)
async def optimize_content_seo(
    content: str,
    target_keywords: List[str] = [],
    current_user: dict = Depends(get_current_user),
    agno_manager: AgnoManager = Depends(get_agno_manager)
):
    """
    Optimize existing content for SEO
    Costs 10 AI Credits (PRD section 6.2)
    """
    
    try:
        # Use SEO optimization agent
        if "seo_optimizer" not in agno_manager.agents:
            raise HTTPException(
                status_code=503,
                detail="SEO optimization agent not available"
            )
        
        agent = agno_manager.agents["seo_optimizer"]
        
        # Build SEO optimization prompt
        prompt = f"""
        Optimize the following content for SEO:
        
        Content:
        {content}
        
        Target Keywords: {', '.join(target_keywords) if target_keywords else 'Not specified'}
        
        Provide:
        1. Optimized version of the content
        2. Suggested meta title and description
        3. SEO score analysis (0-100)
        4. Specific improvement recommendations
        5. Keyword density analysis
        """
        
        response = await agent.arun(prompt)
        
        # Deduct AI Credits (10 credits for SEO optimization)
        await agno_manager._deduct_ai_credits(current_user["user_id"], 10)
        
        return AIResponse(
            success=True,
            content=response.content,
            message="SEO optimization completed",
            credits_used=10,
            model_used=agent.model.id if hasattr(agent.model, 'id') else "unknown"
        )
        
    except Exception as e:
        logger.error(f"SEO optimization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"SEO optimization failed: {str(e)}"
        )

@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_content_templates():
    """Get available content templates"""
    
    # These would be stored in database in production
    templates = [
        {
            "id": "blog_post_tutorial",
            "name": "Tutorial Blog Post",
            "description": "Step-by-step tutorial format",
            "category": "blog",
            "estimated_credits": 20
        },
        {
            "id": "blog_post_review",
            "name": "Product Review",
            "description": "Product review with pros/cons",
            "category": "blog",
            "estimated_credits": 20
        },
        {
            "id": "landing_page_sales",
            "name": "Sales Landing Page",
            "description": "Conversion-focused landing page",
            "category": "page",
            "estimated_credits": 50
        },
        {
            "id": "about_page_business",
            "name": "Business About Page",
            "description": "Professional about page for businesses",
            "category": "page",
            "estimated_credits": 30
        }
    ]
    
    return templates

@router.get("/stats", response_model=Dict[str, Any])
async def get_content_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get content generation statistics for user"""
    
    # In production, these would be real metrics from database
    return {
        "user_id": current_user["user_id"],
        "plan": current_user["plan"],
        "this_month": {
            "blog_posts_generated": 12,
            "pages_created": 4,
            "images_generated": 8,
            "seo_optimizations": 15,
            "total_credits_used": 320
        },
        "all_time": {
            "blog_posts_generated": 45,
            "pages_created": 12,
            "images_generated": 23,
            "seo_optimizations": 38,
            "total_credits_used": 1150
        },
        "popular_topics": [
            {"topic": "WordPress Development", "count": 8},
            {"topic": "SEO Best Practices", "count": 6},
            {"topic": "Small Business Marketing", "count": 5}
        ]
    }