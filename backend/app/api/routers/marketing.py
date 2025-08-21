"""
Marketing Automation API endpoints
Phase 3: Launch Oficial - Growth and marketing tools
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.services.marketing_automation_service import (
    marketing_automation_service,
    CampaignType,
    CampaignStatus,
    AffiliateStatus,
    RewardType
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication
async def get_current_user():
    return {
        "user_id": "admin123",
        "email": "admin@kenzysites.com",
        "role": "admin",
        "is_affiliate": False
    }

async def get_affiliate_user():
    return {
        "user_id": "aff123",
        "email": "affiliate@example.com",
        "role": "affiliate",
        "affiliate_id": "aff_12345678"
    }

# Campaigns
@router.post("/campaigns")
async def create_campaign(
    name: str = Body(..., description="Campaign name"),
    campaign_type: CampaignType = Body(..., description="Campaign type"),
    start_date: str = Body(..., description="Start date (ISO format)"),
    end_date: Optional[str] = Body(None, description="End date (ISO format)"),
    budget: Optional[float] = Body(None, description="Campaign budget"),
    target_metrics: Optional[Dict[str, Any]] = Body(None, description="Target metrics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a marketing campaign
    Track performance across channels
    """
    
    try:
        # Only admins can create campaigns
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date) if end_date else None
        
        campaign = await marketing_automation_service.create_campaign(
            name=name,
            campaign_type=campaign_type,
            start_date=start,
            end_date=end,
            budget=budget,
            target_metrics=target_metrics
        )
        
        logger.info(f"Created campaign {campaign.id}")
        
        return {
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "type": campaign.type.value,
                "status": campaign.status.value,
                "tracking_codes": campaign.tracking_codes,
                "start_date": campaign.start_date.isoformat()
            },
            "message": "Campaign created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create campaign: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create campaign: {str(e)}"
        )

@router.get("/campaigns")
async def list_campaigns(
    status: Optional[CampaignStatus] = Query(None, description="Filter by status"),
    campaign_type: Optional[CampaignType] = Query(None, description="Filter by type"),
    current_user: dict = Depends(get_current_user)
):
    """List all marketing campaigns"""
    
    try:
        campaigns = list(marketing_automation_service.campaigns.values())
        
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        if campaign_type:
            campaigns = [c for c in campaigns if c.type == campaign_type]
        
        return {
            "total": len(campaigns),
            "campaigns": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type.value,
                    "status": c.status.value,
                    "start_date": c.start_date.isoformat(),
                    "budget": c.budget,
                    "spent": c.spent,
                    "conversions": c.conversions,
                    "roi": c.roi
                }
                for c in campaigns
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list campaigns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list campaigns: {str(e)}"
        )

@router.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed campaign performance metrics"""
    
    try:
        performance = await marketing_automation_service.get_campaign_performance(campaign_id)
        return performance
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get campaign performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get campaign performance: {str(e)}"
        )

# Affiliate Program
@router.post("/affiliates/apply")
async def apply_as_affiliate(
    name: str = Body(..., description="Full name"),
    company: Optional[str] = Body(None, description="Company name"),
    website: Optional[str] = Body(None, description="Website URL"),
    email: str = Body(..., description="Email address")
):
    """Apply to become an affiliate partner"""
    
    try:
        affiliate = await marketing_automation_service.create_affiliate(
            email=email,
            name=name,
            company=company,
            website=website
        )
        
        logger.info(f"Affiliate application created: {affiliate.id}")
        
        return {
            "success": True,
            "affiliate_id": affiliate.id,
            "affiliate_code": affiliate.affiliate_code,
            "status": affiliate.status.value,
            "message": "Application submitted. We'll review and get back to you soon."
        }
        
    except Exception as e:
        logger.error(f"Failed to create affiliate application: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create affiliate application: {str(e)}"
        )

@router.put("/affiliates/{affiliate_id}/approve")
async def approve_affiliate(
    affiliate_id: str,
    tier: str = Body("bronze", description="Affiliate tier"),
    commission_rate: Optional[float] = Body(None, description="Custom commission rate"),
    current_user: dict = Depends(get_current_user)
):
    """Approve an affiliate application (admin only)"""
    
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        affiliate = await marketing_automation_service.approve_affiliate(
            affiliate_id=affiliate_id,
            tier=tier,
            commission_rate=commission_rate
        )
        
        logger.info(f"Approved affiliate {affiliate_id}")
        
        return {
            "success": True,
            "affiliate": {
                "id": affiliate.id,
                "name": affiliate.name,
                "tier": affiliate.tier,
                "commission_rate": affiliate.commission_rate,
                "tracking_link": affiliate.tracking_link
            },
            "message": "Affiliate approved successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve affiliate: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve affiliate: {str(e)}"
        )

@router.get("/affiliates/dashboard")
async def get_affiliate_dashboard(
    current_user: dict = Depends(get_affiliate_user)
):
    """Get affiliate dashboard with stats and earnings"""
    
    try:
        affiliate_id = current_user.get("affiliate_id")
        affiliate = marketing_automation_service.affiliates.get(affiliate_id)
        
        if not affiliate:
            raise HTTPException(status_code=404, detail="Affiliate not found")
        
        return {
            "affiliate": {
                "name": affiliate.name,
                "tier": affiliate.tier,
                "status": affiliate.status.value,
                "affiliate_code": affiliate.affiliate_code,
                "tracking_link": affiliate.tracking_link
            },
            "stats": {
                "clicks": affiliate.clicks,
                "signups": affiliate.signups,
                "conversions": affiliate.conversions,
                "conversion_rate": (affiliate.conversions / affiliate.clicks * 100) if affiliate.clicks > 0 else 0
            },
            "earnings": {
                "total_sales": affiliate.total_sales,
                "total_commissions": affiliate.total_commissions,
                "pending_payout": affiliate.pending_commissions,
                "paid_out": affiliate.paid_commissions,
                "commission_rate": affiliate.commission_rate
            },
            "resources": {
                "banners": [
                    {"size": "728x90", "url": f"https://cdn.kenzysites.com/affiliates/banner-728x90.png"},
                    {"size": "300x250", "url": f"https://cdn.kenzysites.com/affiliates/banner-300x250.png"},
                    {"size": "160x600", "url": f"https://cdn.kenzysites.com/affiliates/banner-160x600.png"}
                ],
                "email_templates": True,
                "landing_pages": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get affiliate dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get affiliate dashboard: {str(e)}"
        )

@router.post("/affiliates/track-conversion")
async def track_affiliate_conversion(
    affiliate_code: str = Body(..., description="Affiliate code"),
    order_amount: float = Body(..., description="Order amount"),
    customer_id: str = Body(..., description="Customer ID")
):
    """Track an affiliate conversion (internal use)"""
    
    try:
        result = await marketing_automation_service.track_affiliate_conversion(
            affiliate_code=affiliate_code,
            order_amount=order_amount,
            customer_id=customer_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track affiliate conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track conversion: {str(e)}"
        )

@router.get("/affiliates/leaderboard")
async def get_affiliate_leaderboard(
    limit: int = Query(10, le=50, description="Number of affiliates to show")
):
    """Get top performing affiliates"""
    
    try:
        leaderboard = await marketing_automation_service.get_affiliate_leaderboard(limit)
        
        return {
            "total": len(leaderboard),
            "leaderboard": leaderboard
        }
        
    except Exception as e:
        logger.error(f"Failed to get affiliate leaderboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get leaderboard: {str(e)}"
        )

# Referral Program
@router.post("/referrals/create")
async def create_referral(
    referee_email: str = Body(..., description="Email of person being referred"),
    current_user: dict = Depends(get_current_user)
):
    """Create a referral link for current user"""
    
    try:
        referral = await marketing_automation_service.create_referral(
            referrer_id=current_user["user_id"],
            referee_email=referee_email
        )
        
        logger.info(f"Created referral for user {current_user['user_id']}")
        
        return {
            "success": True,
            "referral": referral,
            "message": "Share your referral link to earn rewards!"
        }
        
    except Exception as e:
        logger.error(f"Failed to create referral: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create referral: {str(e)}"
        )

@router.get("/referrals/program")
async def get_referral_program_details():
    """Get referral program details and rewards"""
    
    program = marketing_automation_service.referral_program
    
    return {
        "program": {
            "name": program.name,
            "active": program.active,
            "referrer_reward": {
                "type": program.referrer_reward_type.value,
                "amount": program.referrer_reward_amount,
                "description": f"Earn {program.referrer_reward_amount} AI Credits for each successful referral"
            },
            "referee_reward": {
                "type": program.referee_reward_type.value,
                "amount": program.referee_reward_amount,
                "description": f"Your friend gets {program.referee_reward_amount}% off their first purchase"
            },
            "terms": {
                "cookie_duration_days": program.cookie_duration_days,
                "attribution_window_days": program.attribution_window_days,
                "require_payment": program.require_payment
            }
        },
        "stats": {
            "total_referrals": program.total_referrals,
            "successful_referrals": program.successful_referrals,
            "total_rewards_given": program.total_rewards_given
        }
    }

# Product Hunt Launch
@router.get("/product-hunt/launch")
async def get_product_hunt_launch():
    """Get Product Hunt launch details"""
    
    try:
        launch = marketing_automation_service.product_hunt_launch
        
        if not launch:
            raise HTTPException(status_code=404, detail="No Product Hunt launch configured")
        
        return {
            "launch": {
                "launch_date": launch.launch_date.isoformat(),
                "product_name": launch.product_name,
                "tagline": launch.tagline,
                "description": launch.description,
                "offer": launch.launch_offer,
                "promo_code": launch.promo_code
            },
            "performance": {
                "upvotes": launch.upvotes,
                "comments": launch.comments,
                "rank": launch.rank,
                "featured": launch.featured,
                "conversions": launch.conversions_from_ph
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Product Hunt launch: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Product Hunt launch: {str(e)}"
        )

@router.post("/product-hunt/update-stats")
async def update_product_hunt_stats(
    upvotes: int = Body(..., description="Number of upvotes"),
    comments: int = Body(..., description="Number of comments"),
    rank: Optional[int] = Body(None, description="Current rank"),
    featured: bool = Body(False, description="Is featured"),
    current_user: dict = Depends(get_current_user)
):
    """Update Product Hunt launch stats (admin only)"""
    
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        launch = await marketing_automation_service.update_product_hunt_stats(
            upvotes=upvotes,
            comments=comments,
            rank=rank,
            featured=featured
        )
        
        logger.info(f"Updated Product Hunt stats")
        
        return {
            "success": True,
            "stats": {
                "upvotes": launch.upvotes,
                "comments": launch.comments,
                "rank": launch.rank,
                "featured": launch.featured
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update Product Hunt stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update Product Hunt stats: {str(e)}"
        )

# Lifetime Deals
@router.get("/lifetime-deals")
async def get_lifetime_deals():
    """Get available lifetime deals"""
    
    try:
        deals = list(marketing_automation_service.lifetime_deals.values())
        
        return {
            "total": len(deals),
            "deals": [
                {
                    "id": deal.id,
                    "name": deal.name,
                    "platform": deal.platform,
                    "regular_price": deal.regular_price,
                    "deal_price": deal.deal_price,
                    "discount_percentage": deal.discount_percentage,
                    "available": deal.total_available - deal.sold,
                    "sold": deal.sold,
                    "features": deal.features,
                    "end_date": deal.end_date.isoformat() if deal.end_date else None
                }
                for deal in deals
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get lifetime deals: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get lifetime deals: {str(e)}"
        )

@router.post("/lifetime-deals/{deal_id}/purchase")
async def purchase_lifetime_deal(
    deal_id: str,
    quantity: int = Body(1, ge=1, le=10, description="Number of licenses"),
    current_user: dict = Depends(get_current_user)
):
    """Purchase a lifetime deal"""
    
    try:
        result = await marketing_automation_service.process_lifetime_deal_purchase(
            deal_id=deal_id,
            customer_id=current_user["user_id"],
            quantity=quantity
        )
        
        logger.info(f"Processed LTD purchase for user {current_user['user_id']}")
        
        return {
            "success": True,
            "purchase": result,
            "message": f"Successfully purchased {quantity} lifetime license(s)"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process LTD purchase: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process purchase: {str(e)}"
        )

# Email Automation
@router.post("/email-automation")
async def create_email_automation(
    name: str = Body(..., description="Automation name"),
    trigger: str = Body(..., description="Trigger event"),
    emails: List[Dict[str, Any]] = Body(..., description="Email sequence"),
    current_user: dict = Depends(get_current_user)
):
    """Create an email automation sequence (admin only)"""
    
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        automation = await marketing_automation_service.create_email_automation(
            name=name,
            trigger=trigger,
            emails=emails
        )
        
        logger.info(f"Created email automation {automation.id}")
        
        return {
            "success": True,
            "automation": {
                "id": automation.id,
                "name": automation.name,
                "trigger": automation.trigger,
                "emails_count": len(automation.emails),
                "active": automation.active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create email automation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create email automation: {str(e)}"
        )

# Growth Metrics
@router.get("/growth-metrics")
async def get_growth_metrics(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    current_user: dict = Depends(get_current_user)
):
    """Get growth and marketing metrics (admin only)"""
    
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        metrics = await marketing_automation_service.get_growth_metrics(start, end)
        
        return metrics
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get growth metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get growth metrics: {str(e)}"
        )

# Partner Program
@router.post("/partners/apply")
async def apply_as_partner(
    company: str = Body(..., description="Company name"),
    contact_name: str = Body(..., description="Contact person"),
    email: str = Body(..., description="Email address"),
    partnership_type: str = Body(..., description="Type of partnership"),
    proposal: str = Body(..., description="Partnership proposal")
):
    """Apply for partnership program"""
    
    try:
        # Create partnership campaign
        campaign = await marketing_automation_service.create_campaign(
            name=f"Partnership - {company}",
            campaign_type=CampaignType.PARTNERSHIP,
            start_date=datetime.now(),
            target_metrics={
                "company": company,
                "contact": contact_name,
                "email": email,
                "type": partnership_type,
                "proposal": proposal
            }
        )
        
        logger.info(f"Partnership application created for {company}")
        
        return {
            "success": True,
            "application_id": campaign.id,
            "message": "Partnership application received. We'll review and contact you soon."
        }
        
    except Exception as e:
        logger.error(f"Failed to create partnership application: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create partnership application: {str(e)}"
        )