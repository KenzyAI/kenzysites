"""
AI Credits System API endpoints
Implements PRD section 6.2: AI Credits System
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

from app.models.ai_models import (
    AICreditsBalance,
    AICreditsTransaction,
    PlanLimits
)
from app.core.config import settings, AI_CREDITS_COSTS, PLAN_LIMITS

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_current_user():
    """Mock user data - in production from authentication"""
    return {"user_id": "user123", "plan": "professional"}

@router.get("/balance", response_model=AICreditsBalance)
async def get_ai_credits_balance(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current AI Credits balance for user
    Shows monthly limit, current balance, and usage
    """
    
    user_plan = current_user["plan"]
    plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["starter"])
    
    # In production, these would come from Redis/database
    monthly_limit = plan_limits["ai_credits_monthly"]
    used_this_month = 320  # Mock data
    current_balance = monthly_limit - used_this_month
    
    # Calculate reset date (first day of next month)
    now = datetime.now()
    if now.month == 12:
        reset_date = datetime(now.year + 1, 1, 1)
    else:
        reset_date = datetime(now.year, now.month + 1, 1)
    
    return AICreditsBalance(
        user_id=current_user["user_id"],
        plan=user_plan,
        monthly_limit=monthly_limit,
        current_balance=max(0, current_balance),
        used_this_month=used_this_month,
        reset_date=reset_date
    )

@router.get("/transactions", response_model=List[AICreditsTransaction])
async def get_ai_credits_transactions(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI Credits transaction history
    Shows detailed usage breakdown
    """
    
    # Mock transaction data - in production from database
    transactions = [
        AICreditsTransaction(
            user_id=current_user["user_id"],
            action="generate_blog_post",
            credits_used=20,
            remaining_balance=2980,
            timestamp=datetime.now() - timedelta(hours=2),
            details={"topic": "WordPress SEO Best Practices", "content_type": "blog_post"}
        ),
        AICreditsTransaction(
            user_id=current_user["user_id"],
            action="generate_site",
            credits_used=100,
            remaining_balance=3000,
            timestamp=datetime.now() - timedelta(days=1),
            details={"business_name": "Clínica Dental Santos", "industry": "Healthcare"}
        ),
        AICreditsTransaction(
            user_id=current_user["user_id"],
            action="seo_optimization",
            credits_used=10,
            remaining_balance=3100,
            timestamp=datetime.now() - timedelta(days=2),
            details={"content_length": 800, "keywords_optimized": 5}
        ),
        AICreditsTransaction(
            user_id=current_user["user_id"],
            action="generate_image",
            credits_used=5,
            remaining_balance=3110,
            timestamp=datetime.now() - timedelta(days=3),
            details={"prompt": "Professional business team", "size": "1024x1024"}
        )
    ]
    
    return transactions[:limit]

@router.get("/costs", response_model=Dict[str, int])
async def get_ai_credits_costs():
    """
    Get AI Credits costs for different actions
    Based on PRD section 6.2
    """
    
    return AI_CREDITS_COSTS

@router.get("/usage-stats", response_model=Dict[str, Any])
async def get_usage_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed usage statistics and analytics
    """
    
    return {
        "user_id": current_user["user_id"],
        "plan": current_user["plan"],
        "current_month": {
            "total_credits_used": 320,
            "actions_breakdown": {
                "generate_blog_post": {"count": 12, "credits": 240},
                "generate_site": {"count": 2, "credits": 200},
                "seo_optimization": {"count": 8, "credits": 80},
                "generate_image": {"count": 4, "credits": 20}
            },
            "daily_usage": [
                {"date": "2025-08-19", "credits": 45},
                {"date": "2025-08-18", "credits": 20}, 
                {"date": "2025-08-17", "credits": 35},
                {"date": "2025-08-16", "credits": 10},
                {"date": "2025-08-15", "credits": 55}
            ]
        },
        "predictions": {
            "estimated_monthly_usage": 380,
            "will_exceed_limit": False,
            "recommended_plan": current_user["plan"],
            "savings_with_annual": "20%"
        }
    }

@router.get("/plan-comparison", response_model=List[Dict[str, Any]])
async def get_plan_comparison():
    """
    Compare AI Credits across different plans
    Based on PRD section 6.1
    """
    
    plans = []
    for plan_name, limits in PLAN_LIMITS.items():
        plan_data = {
            "plan_name": plan_name.title(),
            "ai_credits_monthly": limits["ai_credits_monthly"],
            "price_brl_monthly": {
                "starter": "R$ 97",
                "professional": "R$ 297", 
                "business": "R$ 597",
                "agency": "R$ 1.997"
            }.get(plan_name, "Contact"),
            "price_usd_monthly": {
                "starter": "$19",
                "professional": "$59",
                "business": "$119", 
                "agency": "$399"
            }.get(plan_name, "Contact"),
            "estimated_usage": {
                "blog_posts": limits.get("blog_posts_monthly", 0),
                "sites": limits.get("sites_wordpress", 0),
                "landing_pages": limits.get("landing_pages", 0)
            },
            "best_for": {
                "starter": "Freelancers and small blogs",
                "professional": "Small agencies and consultants",
                "business": "Growing agencies and businesses",
                "agency": "Large agencies and enterprises"
            }.get(plan_name, "Custom needs")
        }
        plans.append(plan_data)
    
    return plans

@router.post("/purchase-credits", response_model=Dict[str, Any])
async def purchase_additional_credits(
    credits_amount: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Purchase additional AI Credits (one-time purchase)
    For users who exceed their monthly limit
    """
    
    if credits_amount < 100 or credits_amount > 10000:
        raise HTTPException(
            status_code=400,
            detail="Credits amount must be between 100 and 10,000"
        )
    
    # Calculate price (mock pricing - R$ 0.10 per credit)
    price_brl = credits_amount * 0.10
    price_usd = credits_amount * 0.02
    
    # In production, this would integrate with payment gateway
    transaction_id = f"cr_{current_user['user_id']}_{int(datetime.now().timestamp())}"
    
    return {
        "transaction_id": transaction_id,
        "credits_purchased": credits_amount,
        "price_brl": f"R$ {price_brl:.2f}",
        "price_usd": f"$ {price_usd:.2f}",
        "status": "pending_payment",
        "payment_url": f"https://pay.example.com/checkout/{transaction_id}",
        "expires_at": datetime.now() + timedelta(minutes=15)
    }

@router.get("/recommendations", response_model=Dict[str, Any])
async def get_usage_recommendations(
    current_user: dict = Depends(get_current_user)
):
    """
    Get personalized recommendations for optimizing AI Credits usage
    """
    
    user_plan = current_user["plan"]
    
    # Mock analysis based on usage patterns
    recommendations = {
        "user_id": current_user["user_id"],
        "current_plan": user_plan,
        "analysis": {
            "usage_efficiency": 85,  # percentage
            "most_used_feature": "generate_blog_post",
            "least_used_feature": "generate_image",
            "peak_usage_time": "Tuesday mornings"
        },
        "recommendations": [
            {
                "type": "optimization",
                "title": "Batch Content Generation",
                "description": "Use batch processing to generate multiple posts at once for better efficiency",
                "potential_savings": "15% credits"
            },
            {
                "type": "feature",
                "title": "SEO Optimization",
                "description": "You're not using SEO optimization enough. It can improve content quality significantly",
                "cost": "10 credits per optimization"
            },
            {
                "type": "upgrade",
                "title": "Consider Business Plan",
                "description": "Your usage pattern suggests you might benefit from the Business plan",
                "savings": "R$ 50/month with your current usage"
            }
        ]
    }
    
    return recommendations

@router.get("/limits", response_model=PlanLimits)
async def get_plan_limits(
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed plan limits for current user
    """
    
    user_plan = current_user["plan"]
    limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["starter"])
    
    return PlanLimits(
        plan_name=user_plan,
        **limits
    )