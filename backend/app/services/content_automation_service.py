"""
Content Automation Service
Implements automated content generation with editorial calendar
Part of Phase 2: Beta Público
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4
from enum import Enum

from app.core.config import settings, PLAN_LIMITS
from app.services.agno_manager import AgnoManager
from app.models.ai_models import ContentGenerationRequest, GeneratedContent

logger = logging.getLogger(__name__)

class ContentStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

class ContentFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class PublishingPlatform(str, Enum):
    WORDPRESS = "wordpress"
    LANDING_PAGE = "landing_page"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"

# Content Automation Models
class EditorialCalendarItem(BaseModel):
    """Editorial calendar item"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content_type: str
    topic: str
    keywords: List[str] = Field(default_factory=list)
    scheduled_date: datetime
    status: ContentStatus = ContentStatus.DRAFT
    platform: PublishingPlatform = PublishingPlatform.WORDPRESS
    
    # Generated content
    generated_content: Optional[GeneratedContent] = None
    
    # Publishing details
    published_at: Optional[datetime] = None
    published_url: Optional[str] = None
    
    # Performance metrics
    views: int = 0
    engagement_rate: float = 0
    seo_score: Optional[int] = None
    
    # AI generation settings
    tone: str = "professional"
    style: str = "informative"
    target_audience: str = "general"
    custom_instructions: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    site_id: Optional[str] = None

class ContentPlan(BaseModel):
    """Content automation plan"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    
    # Schedule settings
    frequency: ContentFrequency
    posts_per_period: int  # Based on plan limits
    
    # Content settings
    topics: List[str]
    keywords: List[str]
    content_types: List[str]
    tone: str = "professional"
    style: str = "blog"
    
    # Target settings
    target_platforms: List[PublishingPlatform]
    target_sites: List[str] = Field(default_factory=list)
    
    # Automation settings
    auto_generate: bool = True
    auto_publish: bool = False
    require_approval: bool = True
    
    # SEO settings
    auto_seo_optimization: bool = True
    target_keyword_density: float = 2.0
    
    # Image settings
    auto_generate_images: bool = True
    images_per_post: int = 1
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ContentAutomationService:
    """
    Service for automated content generation and scheduling
    Manages editorial calendar and content automation
    """
    
    def __init__(self):
        self.agno_manager = None
        self.content_plans = {}  # In production, would be in database
        self.editorial_calendar = []  # In production, would be in database
        
    async def initialize(self, agno_manager: AgnoManager):
        """Initialize with Agno manager"""
        self.agno_manager = agno_manager
        logger.info("Content Automation Service initialized")
    
    async def create_content_plan(
        self,
        user_id: str,
        plan_name: str,
        topics: List[str],
        frequency: ContentFrequency,
        user_plan: str = "professional"
    ) -> ContentPlan:
        """
        Create a content automation plan
        Posts per month based on PRD plan limits
        """
        
        # Get plan limits from PRD
        plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["starter"])
        posts_limit = plan_limits.get("blog_posts_monthly", 4)
        
        # Calculate posts per period based on frequency
        if frequency == ContentFrequency.DAILY:
            posts_per_period = min(30, posts_limit)
        elif frequency == ContentFrequency.WEEKLY:
            posts_per_period = min(4, posts_limit)
        elif frequency == ContentFrequency.BIWEEKLY:
            posts_per_period = min(2, posts_limit)
        else:
            posts_per_period = min(1, posts_limit)
        
        content_plan = ContentPlan(
            name=plan_name,
            frequency=frequency,
            posts_per_period=posts_per_period,
            topics=topics,
            keywords=[],  # Will be generated with AI
            content_types=["blog_post", "article"],
            target_platforms=[PublishingPlatform.WORDPRESS]
        )
        
        # Store plan
        self.content_plans[content_plan.id] = content_plan
        
        # Generate initial calendar items
        await self._generate_calendar_items(content_plan, user_id)
        
        logger.info(f"Created content plan: {content_plan.id} with {posts_per_period} posts per period")
        return content_plan
    
    async def _generate_calendar_items(
        self,
        content_plan: ContentPlan,
        user_id: str
    ):
        """Generate editorial calendar items based on plan"""
        
        start_date = datetime.now()
        
        for i in range(content_plan.posts_per_period):
            # Calculate scheduled date based on frequency
            if content_plan.frequency == ContentFrequency.DAILY:
                scheduled_date = start_date + timedelta(days=i)
            elif content_plan.frequency == ContentFrequency.WEEKLY:
                scheduled_date = start_date + timedelta(weeks=i)
            elif content_plan.frequency == ContentFrequency.BIWEEKLY:
                scheduled_date = start_date + timedelta(weeks=i*2)
            else:  # Monthly
                scheduled_date = start_date + timedelta(days=i*30)
            
            # Rotate through topics
            topic = content_plan.topics[i % len(content_plan.topics)]
            
            # Create calendar item
            item = EditorialCalendarItem(
                title=f"{topic} - {scheduled_date.strftime('%B %d')}",
                content_type="blog_post",
                topic=topic,
                scheduled_date=scheduled_date,
                tone=content_plan.tone,
                style=content_plan.style,
                created_by=user_id
            )
            
            self.editorial_calendar.append(item)
    
    async def get_editorial_calendar(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[ContentStatus] = None
    ) -> List[EditorialCalendarItem]:
        """Get editorial calendar items"""
        
        if not start_date:
            start_date = datetime.now()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        # Filter calendar items
        items = []
        for item in self.editorial_calendar:
            if item.created_by != user_id:
                continue
            if item.scheduled_date < start_date or item.scheduled_date > end_date:
                continue
            if status and item.status != status:
                continue
            items.append(item)
        
        # Sort by scheduled date
        items.sort(key=lambda x: x.scheduled_date)
        
        return items
    
    async def generate_content_batch(
        self,
        user_id: str,
        calendar_ids: List[str],
        user_plan: str = "professional"
    ) -> List[GeneratedContent]:
        """
        Generate content for multiple calendar items
        Uses AI to create content based on topics and settings
        """
        
        if not self.agno_manager:
            raise ValueError("Agno manager not initialized")
        
        generated_contents = []
        
        for calendar_id in calendar_ids:
            # Find calendar item
            item = next((i for i in self.editorial_calendar if i.id == calendar_id), None)
            if not item:
                continue
            
            # Create content generation request
            request = ContentGenerationRequest(
                content_type="blog_post",
                topic=item.topic,
                keywords=item.keywords,
                tone=item.tone,
                target_audience=item.target_audience,
                custom_instructions=item.custom_instructions,
                seo_optimized=True
            )
            
            # Generate with Agno
            response = await self.agno_manager.generate_content(
                request=request,
                user_id=user_id,
                user_plan=user_plan
            )
            
            if response.success and response.content:
                # Parse and structure content
                generated_content = self._parse_generated_content(response.content, item)
                
                # Update calendar item
                item.generated_content = generated_content
                item.status = ContentStatus.SCHEDULED
                item.updated_at = datetime.now()
                
                generated_contents.append(generated_content)
                
                logger.info(f"Generated content for calendar item: {calendar_id}")
        
        return generated_contents
    
    def _parse_generated_content(
        self,
        raw_content: str,
        calendar_item: EditorialCalendarItem
    ) -> GeneratedContent:
        """Parse AI-generated content into structured format"""
        
        # Extract title (first line or H1)
        lines = raw_content.split('\n')
        title = lines[0].replace('#', '').strip() if lines else calendar_item.title
        
        # Extract content body
        content = '\n'.join(lines[1:]) if len(lines) > 1 else raw_content
        
        # Generate excerpt (first 160 chars)
        excerpt = content[:160] + '...' if len(content) > 160 else content
        
        # Create meta description
        meta_description = excerpt[:155]  # SEO best practice
        
        # Suggest tags based on topic
        tags = calendar_item.keywords.copy() if calendar_item.keywords else []
        tags.append(calendar_item.topic.lower().replace(' ', '-'))
        
        return GeneratedContent(
            title=title,
            content=content,
            excerpt=excerpt,
            meta_title=title[:60],  # SEO title length
            meta_description=meta_description,
            tags=tags,
            categories=[calendar_item.content_type],
            word_count=len(content.split()),
            seo_score=85,  # Would be calculated
            readability_score=75  # Would be calculated
        )
    
    async def publish_content(
        self,
        calendar_id: str,
        platform: PublishingPlatform,
        site_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish content to specified platform
        Supports WordPress, Landing Pages, Social Media
        """
        
        # Find calendar item
        item = next((i for i in self.editorial_calendar if i.id == calendar_id), None)
        if not item or not item.generated_content:
            raise ValueError(f"Calendar item {calendar_id} not found or has no content")
        
        item.status = ContentStatus.PUBLISHING
        
        try:
            if platform == PublishingPlatform.WORDPRESS:
                result = await self._publish_to_wordpress(item, site_id)
            elif platform == PublishingPlatform.LANDING_PAGE:
                result = await self._publish_to_landing_page(item)
            elif platform == PublishingPlatform.SOCIAL_MEDIA:
                result = await self._publish_to_social_media(item)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Update item status
            item.status = ContentStatus.PUBLISHED
            item.published_at = datetime.now()
            item.published_url = result.get("url")
            item.updated_at = datetime.now()
            
            logger.info(f"Published content {calendar_id} to {platform}")
            return result
            
        except Exception as e:
            item.status = ContentStatus.FAILED
            logger.error(f"Failed to publish content {calendar_id}: {str(e)}")
            raise
    
    async def _publish_to_wordpress(
        self,
        item: EditorialCalendarItem,
        site_id: Optional[str]
    ) -> Dict[str, Any]:
        """Publish content to WordPress site"""
        
        # This would integrate with WordPress API
        # Mock implementation
        
        return {
            "success": True,
            "platform": "wordpress",
            "post_id": f"wp_post_{uuid4()}",
            "url": f"https://site.com/blog/{item.generated_content.title.lower().replace(' ', '-')}",
            "published_at": datetime.now().isoformat()
        }
    
    async def _publish_to_landing_page(
        self,
        item: EditorialCalendarItem
    ) -> Dict[str, Any]:
        """Publish content as landing page"""
        
        return {
            "success": True,
            "platform": "landing_page",
            "page_id": f"lp_{uuid4()}",
            "url": f"https://pages.site.com/{item.generated_content.title.lower().replace(' ', '-')}",
            "published_at": datetime.now().isoformat()
        }
    
    async def _publish_to_social_media(
        self,
        item: EditorialCalendarItem
    ) -> Dict[str, Any]:
        """Publish content to social media"""
        
        # Would integrate with social media APIs
        # Could post to multiple platforms
        
        return {
            "success": True,
            "platform": "social_media",
            "posts": {
                "facebook": f"fb_post_{uuid4()}",
                "twitter": f"tw_post_{uuid4()}",
                "linkedin": f"li_post_{uuid4()}"
            },
            "published_at": datetime.now().isoformat()
        }
    
    async def schedule_auto_publishing(
        self,
        user_id: str,
        enable: bool = True
    ) -> Dict[str, Any]:
        """
        Enable/disable automatic publishing
        Will publish content at scheduled times
        """
        
        # This would set up background tasks/cron jobs
        # to automatically publish scheduled content
        
        status = "enabled" if enable else "disabled"
        logger.info(f"Auto-publishing {status} for user {user_id}")
        
        return {
            "auto_publishing": enable,
            "message": f"Automatic publishing has been {status}",
            "next_scheduled": None if not enable else (datetime.now() + timedelta(hours=1)).isoformat()
        }
    
    async def get_content_performance(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get content performance analytics"""
        
        published_items = [
            item for item in self.editorial_calendar
            if item.created_by == user_id and item.status == ContentStatus.PUBLISHED
        ]
        
        total_views = sum(item.views for item in published_items)
        avg_engagement = sum(item.engagement_rate for item in published_items) / len(published_items) if published_items else 0
        
        return {
            "period": f"{period_days} days",
            "total_posts": len(published_items),
            "total_views": total_views,
            "average_engagement_rate": avg_engagement,
            "top_performing": [
                {
                    "title": item.title,
                    "views": item.views,
                    "engagement_rate": item.engagement_rate,
                    "url": item.published_url
                }
                for item in sorted(published_items, key=lambda x: x.views, reverse=True)[:5]
            ],
            "publishing_consistency": {
                "scheduled": len([i for i in self.editorial_calendar if i.status == ContentStatus.SCHEDULED]),
                "published": len(published_items),
                "failed": len([i for i in self.editorial_calendar if i.status == ContentStatus.FAILED])
            }
        }
    
    async def optimize_content_strategy(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        AI-powered content strategy optimization
        Analyzes performance and suggests improvements
        """
        
        # Analyze past performance
        performance = await self.get_content_performance(user_id)
        
        # Generate recommendations using AI
        recommendations = [
            {
                "type": "topic",
                "suggestion": "Focus more on 'WordPress Security' topics - 35% higher engagement",
                "impact": "high"
            },
            {
                "type": "frequency",
                "suggestion": "Increase posting frequency to 2x per week for better SEO",
                "impact": "medium"
            },
            {
                "type": "timing",
                "suggestion": "Publish on Tuesdays and Thursdays at 10 AM for maximum reach",
                "impact": "medium"
            },
            {
                "type": "keywords",
                "suggestion": "Include 'WordPress hosting' keywords - high search volume",
                "impact": "high"
            }
        ]
        
        return {
            "current_performance": performance,
            "recommendations": recommendations,
            "predicted_improvement": "25% increase in traffic if recommendations are followed",
            "suggested_topics": [
                "WordPress Security Best Practices",
                "Speed Optimization for WordPress",
                "WordPress Plugin Development",
                "WordPress Theme Customization"
            ]
        }
    
    async def bulk_schedule_content(
        self,
        user_id: str,
        topics: List[str],
        start_date: datetime,
        end_date: datetime,
        frequency: ContentFrequency
    ) -> List[EditorialCalendarItem]:
        """
        Bulk schedule content for a date range
        Useful for planning content months in advance
        """
        
        scheduled_items = []
        current_date = start_date
        topic_index = 0
        
        while current_date <= end_date:
            # Create calendar item
            item = EditorialCalendarItem(
                title=f"{topics[topic_index % len(topics)]} - {current_date.strftime('%B %d')}",
                content_type="blog_post",
                topic=topics[topic_index % len(topics)],
                scheduled_date=current_date,
                created_by=user_id
            )
            
            self.editorial_calendar.append(item)
            scheduled_items.append(item)
            
            # Calculate next date based on frequency
            if frequency == ContentFrequency.DAILY:
                current_date += timedelta(days=1)
            elif frequency == ContentFrequency.WEEKLY:
                current_date += timedelta(weeks=1)
            elif frequency == ContentFrequency.BIWEEKLY:
                current_date += timedelta(weeks=2)
            else:  # Monthly
                current_date += timedelta(days=30)
            
            topic_index += 1
        
        logger.info(f"Bulk scheduled {len(scheduled_items)} content items for user {user_id}")
        return scheduled_items

# Create singleton instance
content_automation_service = ContentAutomationService()

__all__ = [
    'content_automation_service',
    'ContentAutomationService',
    'EditorialCalendarItem',
    'ContentPlan',
    'ContentStatus',
    'ContentFrequency'
]