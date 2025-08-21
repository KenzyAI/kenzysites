"""
Content Automation API endpoints
Implements automated content generation with editorial calendar
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.services.content_automation_service import (
    content_automation_service,
    EditorialCalendarItem,
    ContentPlan,
    ContentStatus,
    ContentFrequency,
    PublishingPlatform
)
from app.services.agno_manager import AgnoManager
from app.core.config import PLAN_LIMITS

logger = logging.getLogger(__name__)
router = APIRouter()

# Request models
class CreateContentPlanRequest(BaseModel):
    """Request to create content automation plan"""
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    topics: List[str] = Field(..., description="Content topics")
    frequency: ContentFrequency = Field(..., description="Publishing frequency")
    auto_generate: bool = Field(True, description="Auto-generate content")
    auto_publish: bool = Field(False, description="Auto-publish content")
    target_platforms: List[str] = Field(default_factory=lambda: ["wordpress"])

class ScheduleContentRequest(BaseModel):
    """Request to schedule content"""
    title: str
    topic: str
    scheduled_date: str  # ISO format
    content_type: str = "blog_post"
    keywords: Optional[List[str]] = None
    custom_instructions: Optional[str] = None

class BulkScheduleRequest(BaseModel):
    """Request for bulk scheduling"""
    topics: List[str]
    start_date: str  # ISO format
    end_date: str    # ISO format
    frequency: ContentFrequency

# Mock user authentication
async def get_current_user():
    return {
        "user_id": "user123",
        "plan": "professional",
        "email": "user@example.com"
    }

async def get_agno_manager() -> AgnoManager:
    """Get Agno manager from app state"""
    from main import app
    return app.state.agno_manager

# Initialize service on startup
@router.on_event("startup")
async def initialize_service():
    """Initialize content automation service"""
    try:
        from main import app
        await content_automation_service.initialize(app.state.agno_manager)
        logger.info("Content Automation Service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Content Automation Service: {str(e)}")

# Content Plans
@router.post("/plans", response_model=ContentPlan)
async def create_content_plan(
    request: CreateContentPlanRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a content automation plan
    Posts per month based on user's plan (PRD limits)
    """
    
    try:
        plan = await content_automation_service.create_content_plan(
            user_id=current_user["user_id"],
            plan_name=request.name,
            topics=request.topics,
            frequency=request.frequency,
            user_plan=current_user["plan"]
        )
        
        # Update plan with additional settings
        plan.description = request.description
        plan.auto_generate = request.auto_generate
        plan.auto_publish = request.auto_publish
        plan.target_platforms = [PublishingPlatform(p) for p in request.target_platforms]
        
        logger.info(f"Created content plan {plan.id} for user {current_user['user_id']}")
        return plan
        
    except Exception as e:
        logger.error(f"Failed to create content plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create content plan: {str(e)}"
        )

@router.get("/plans", response_model=List[ContentPlan])
async def get_content_plans(
    current_user: dict = Depends(get_current_user)
):
    """Get all content plans for current user"""
    
    try:
        # Filter plans for current user
        plans = [
            plan for plan in content_automation_service.content_plans.values()
            if plan.id in ["plan_1", "plan_2"]  # Mock filtering
        ]
        
        return plans
        
    except Exception as e:
        logger.error(f"Failed to get content plans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content plans: {str(e)}"
        )

# Editorial Calendar
@router.get("/calendar", response_model=List[EditorialCalendarItem])
async def get_editorial_calendar(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    status: Optional[ContentStatus] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get editorial calendar items
    Shows scheduled, draft, and published content
    """
    
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        items = await content_automation_service.get_editorial_calendar(
            user_id=current_user["user_id"],
            start_date=start,
            end_date=end,
            status=status
        )
        
        return items
        
    except Exception as e:
        logger.error(f"Failed to get editorial calendar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get editorial calendar: {str(e)}"
        )

@router.post("/calendar/schedule")
async def schedule_content(
    request: ScheduleContentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Schedule a single content item"""
    
    try:
        scheduled_date = datetime.fromisoformat(request.scheduled_date)
        
        item = EditorialCalendarItem(
            title=request.title,
            topic=request.topic,
            content_type=request.content_type,
            scheduled_date=scheduled_date,
            keywords=request.keywords or [],
            custom_instructions=request.custom_instructions,
            created_by=current_user["user_id"]
        )
        
        content_automation_service.editorial_calendar.append(item)
        
        logger.info(f"Scheduled content item {item.id} for {scheduled_date}")
        
        return {
            "success": True,
            "calendar_item": item,
            "message": f"Content scheduled for {scheduled_date.strftime('%B %d, %Y')}"
        }
        
    except Exception as e:
        logger.error(f"Failed to schedule content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule content: {str(e)}"
        )

@router.post("/calendar/bulk-schedule")
async def bulk_schedule_content(
    request: BulkScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Bulk schedule content for a date range
    Useful for planning months in advance
    """
    
    try:
        start_date = datetime.fromisoformat(request.start_date)
        end_date = datetime.fromisoformat(request.end_date)
        
        items = await content_automation_service.bulk_schedule_content(
            user_id=current_user["user_id"],
            topics=request.topics,
            start_date=start_date,
            end_date=end_date,
            frequency=request.frequency
        )
        
        logger.info(f"Bulk scheduled {len(items)} content items")
        
        return {
            "success": True,
            "items_scheduled": len(items),
            "date_range": f"{start_date.date()} to {end_date.date()}",
            "message": f"Successfully scheduled {len(items)} content items"
        }
        
    except Exception as e:
        logger.error(f"Failed to bulk schedule content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bulk schedule content: {str(e)}"
        )

# Content Generation
@router.post("/generate")
async def generate_content_batch(
    calendar_ids: List[str] = Body(..., description="Calendar item IDs to generate"),
    current_user: dict = Depends(get_current_user),
    agno_manager: AgnoManager = Depends(get_agno_manager)
):
    """
    Generate content for scheduled items
    Uses AI to create content based on topics
    Costs AI Credits based on plan
    """
    
    try:
        # Ensure service is initialized
        if not content_automation_service.agno_manager:
            await content_automation_service.initialize(agno_manager)
        
        generated = await content_automation_service.generate_content_batch(
            user_id=current_user["user_id"],
            calendar_ids=calendar_ids,
            user_plan=current_user["plan"]
        )
        
        # Calculate credits used (20 per blog post)
        credits_used = len(generated) * 20
        
        logger.info(f"Generated {len(generated)} content pieces, used {credits_used} AI Credits")
        
        return {
            "success": True,
            "generated_count": len(generated),
            "credits_used": credits_used,
            "content": generated,
            "message": f"Successfully generated {len(generated)} content pieces"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content: {str(e)}"
        )

# Publishing
@router.post("/publish/{calendar_id}")
async def publish_content(
    calendar_id: str,
    platform: PublishingPlatform = Body(PublishingPlatform.WORDPRESS),
    site_id: Optional[str] = Body(None, description="Target site ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Publish content to specified platform
    Supports WordPress, Landing Pages, Social Media
    """
    
    try:
        result = await content_automation_service.publish_content(
            calendar_id=calendar_id,
            platform=platform,
            site_id=site_id
        )
        
        logger.info(f"Published content {calendar_id} to {platform}")
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error(f"Failed to publish content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish content: {str(e)}"
        )

@router.post("/auto-publishing")
async def configure_auto_publishing(
    enable: bool = Body(..., description="Enable or disable auto-publishing"),
    current_user: dict = Depends(get_current_user)
):
    """
    Enable/disable automatic content publishing
    Content will be published at scheduled times
    """
    
    try:
        result = await content_automation_service.schedule_auto_publishing(
            user_id=current_user["user_id"],
            enable=enable
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to configure auto-publishing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure auto-publishing: {str(e)}"
        )

# Analytics
@router.get("/performance")
async def get_content_performance(
    period_days: int = Query(30, description="Period in days"),
    current_user: dict = Depends(get_current_user)
):
    """Get content performance analytics"""
    
    try:
        performance = await content_automation_service.get_content_performance(
            user_id=current_user["user_id"],
            period_days=period_days
        )
        
        return performance
        
    except Exception as e:
        logger.error(f"Failed to get content performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get content performance: {str(e)}"
        )

@router.get("/optimize-strategy")
async def optimize_content_strategy(
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-powered content strategy recommendations
    Analyzes performance and suggests improvements
    """
    
    try:
        optimization = await content_automation_service.optimize_content_strategy(
            user_id=current_user["user_id"]
        )
        
        return optimization
        
    except Exception as e:
        logger.error(f"Failed to optimize content strategy: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize content strategy: {str(e)}"
        )

# Plan Limits
@router.get("/limits")
async def get_content_limits(
    current_user: dict = Depends(get_current_user)
):
    """Get content limits based on user's plan"""
    
    plan_limits = PLAN_LIMITS.get(current_user["plan"], PLAN_LIMITS["starter"])
    
    return {
        "plan": current_user["plan"],
        "limits": {
            "blog_posts_monthly": plan_limits.get("blog_posts_monthly", 4),
            "ai_credits_monthly": plan_limits.get("ai_credits_monthly", 1000),
            "sites_wordpress": plan_limits.get("sites_wordpress", 1)
        },
        "usage": {
            "blog_posts_this_month": 8,  # Mock data
            "ai_credits_used": 320,      # Mock data
            "sites_active": 2             # Mock data
        },
        "recommendations": [
            "You have 12 blog posts remaining this month",
            "Consider scheduling content for next week",
            "Your best performing day is Tuesday"
        ]
    }

# Calendar View Helpers
@router.get("/calendar/view/{view_type}")
async def get_calendar_view(
    view_type: str,  # "month", "week", "list"
    date: Optional[str] = Query(None, description="Reference date (ISO format)"),
    current_user: dict = Depends(get_current_user)
):
    """Get calendar in different view formats"""
    
    try:
        ref_date = datetime.fromisoformat(date) if date else datetime.now()
        
        if view_type == "month":
            start_date = ref_date.replace(day=1)
            # Get last day of month
            if ref_date.month == 12:
                end_date = ref_date.replace(year=ref_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = ref_date.replace(month=ref_date.month + 1, day=1) - timedelta(days=1)
        elif view_type == "week":
            start_date = ref_date - timedelta(days=ref_date.weekday())
            end_date = start_date + timedelta(days=6)
        else:  # list view
            start_date = ref_date
            end_date = ref_date + timedelta(days=30)
        
        items = await content_automation_service.get_editorial_calendar(
            user_id=current_user["user_id"],
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "view_type": view_type,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "items": items,
            "total": len(items)
        }
        
    except Exception as e:
        logger.error(f"Failed to get calendar view: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get calendar view: {str(e)}"
        )

# Content Ideas Generator
@router.get("/ideas")
async def get_content_ideas(
    industry: str = Query(..., description="Business industry"),
    count: int = Query(10, description="Number of ideas to generate"),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate content ideas based on industry and trends
    Uses AI to suggest relevant topics
    """
    
    try:
        # Mock content ideas - would use AI in production
        ideas = [
            {
                "topic": f"{industry} Best Practices Guide",
                "keywords": [industry.lower(), "guide", "best practices"],
                "estimated_traffic": 1500,
                "competition": "medium"
            },
            {
                "topic": f"Top 10 {industry} Trends for 2025",
                "keywords": [industry.lower(), "trends", "2025"],
                "estimated_traffic": 2500,
                "competition": "low"
            },
            {
                "topic": f"How to Start a {industry} Business",
                "keywords": [industry.lower(), "startup", "business"],
                "estimated_traffic": 3000,
                "competition": "high"
            }
        ]
        
        return {
            "industry": industry,
            "ideas": ideas[:count],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate content ideas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate content ideas: {str(e)}"
        )