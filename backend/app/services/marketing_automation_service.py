"""
Marketing Automation Service
Phase 3: Launch Oficial - Marketing automation and growth tools
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
import uuid
import json
import hashlib
import random

logger = logging.getLogger(__name__)

# Enums
class CampaignType(str, Enum):
    PRODUCT_HUNT = "product_hunt"
    AFFILIATE = "affiliate"
    REFERRAL = "referral"
    EMAIL = "email"
    SOCIAL = "social"
    LIFETIME_DEAL = "lifetime_deal"
    INFLUENCER = "influencer"
    CONTENT = "content"
    WEBINAR = "webinar"
    PARTNERSHIP = "partnership"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class AffiliateStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    ACTIVE = "active"

class RewardType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    RECURRING = "recurring"
    TIERED = "tiered"
    CREDITS = "credits"

class LeadSource(str, Enum):
    ORGANIC = "organic"
    PAID_ADS = "paid_ads"
    AFFILIATE = "affiliate"
    REFERRAL = "referral"
    SOCIAL = "social"
    EMAIL = "email"
    DIRECT = "direct"
    PRODUCT_HUNT = "product_hunt"

# Models
class Campaign(BaseModel):
    """Marketing campaign"""
    id: str = Field(default_factory=lambda: f"campaign_{uuid.uuid4().hex[:8]}")
    name: str
    type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    description: Optional[str] = None
    
    # Timing
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Targeting
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    target_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Budget
    budget: Optional[float] = None
    spent: float = 0.0
    currency: str = "USD"
    
    # Performance
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    roi: float = 0.0
    
    # Content
    assets: List[Dict[str, Any]] = Field(default_factory=list)
    landing_page_url: Optional[str] = None
    tracking_codes: Dict[str, str] = Field(default_factory=dict)

class Affiliate(BaseModel):
    """Affiliate partner"""
    id: str = Field(default_factory=lambda: f"aff_{uuid.uuid4().hex[:8]}")
    user_id: Optional[str] = None
    email: str
    name: str
    company: Optional[str] = None
    website: Optional[str] = None
    
    # Status
    status: AffiliateStatus = AffiliateStatus.PENDING
    approved_at: Optional[datetime] = None
    tier: str = "bronze"  # bronze, silver, gold, platinum
    
    # Tracking
    affiliate_code: str = Field(default_factory=lambda: uuid.uuid4().hex[:8].upper())
    tracking_link: Optional[str] = None
    cookie_duration_days: int = 30
    
    # Commission
    commission_type: RewardType = RewardType.PERCENTAGE
    commission_rate: float = 30.0  # 30% default
    minimum_payout: float = 100.0
    
    # Performance
    clicks: int = 0
    signups: int = 0
    conversions: int = 0
    total_sales: float = 0.0
    total_commissions: float = 0.0
    paid_commissions: float = 0.0
    pending_commissions: float = 0.0
    
    # Payment
    payment_method: Optional[str] = None
    payment_details: Dict[str, Any] = Field(default_factory=dict)
    last_payout_date: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

class ReferralProgram(BaseModel):
    """Referral program configuration"""
    id: str = Field(default_factory=lambda: f"ref_{uuid.uuid4().hex[:8]}")
    name: str = "Customer Referral Program"
    active: bool = True
    
    # Rewards
    referrer_reward_type: RewardType = RewardType.CREDITS
    referrer_reward_amount: float = 500  # 500 AI credits
    referee_reward_type: RewardType = RewardType.PERCENTAGE
    referee_reward_amount: float = 20  # 20% discount
    
    # Conditions
    minimum_purchase: float = 0.0
    require_payment: bool = True  # Referee must make payment
    max_referrals_per_user: int = -1  # Unlimited
    
    # Tracking
    cookie_duration_days: int = 30
    attribution_window_days: int = 60
    
    # Stats
    total_referrals: int = 0
    successful_referrals: int = 0
    total_rewards_given: float = 0.0

class ProductHuntLaunch(BaseModel):
    """Product Hunt launch campaign"""
    id: str = Field(default_factory=lambda: f"ph_{uuid.uuid4().hex[:8]}")
    launch_date: datetime
    product_name: str = "KenzySites - AI WordPress Builder"
    tagline: str = "Create WordPress sites in 60 seconds with AI"
    description: str
    
    # Assets
    thumbnail_url: Optional[str] = None
    gallery_urls: List[str] = Field(default_factory=list)
    demo_url: Optional[str] = None
    
    # Hunters
    hunters: List[Dict[str, str]] = Field(default_factory=list)
    maker_twitter: Optional[str] = None
    
    # Offer
    launch_offer: Dict[str, Any] = Field(default_factory=dict)
    promo_code: Optional[str] = None
    
    # Performance
    upvotes: int = 0
    comments: int = 0
    rank: Optional[int] = None
    featured: bool = False
    
    # Tracking
    visits_from_ph: int = 0
    signups_from_ph: int = 0
    conversions_from_ph: int = 0

class LifetimeDeal(BaseModel):
    """Lifetime deal offering"""
    id: str = Field(default_factory=lambda: f"ltd_{uuid.uuid4().hex[:8]}")
    name: str
    platform: str  # AppSumo, StackSocial, PitchGround, etc.
    
    # Pricing
    regular_price: float
    deal_price: float
    discount_percentage: float
    commission_rate: float = 30.0  # Platform commission
    
    # Limits
    total_available: int = 500
    sold: int = 0
    max_per_customer: int = 3
    
    # Features
    plan_equivalent: str = "professional"
    features: List[str] = Field(default_factory=list)
    restrictions: List[str] = Field(default_factory=list)
    
    # Timing
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Performance
    revenue: float = 0.0
    net_revenue: float = 0.0
    customers: List[str] = Field(default_factory=list)

class EmailAutomation(BaseModel):
    """Email automation sequence"""
    id: str = Field(default_factory=lambda: f"email_{uuid.uuid4().hex[:8]}")
    name: str
    trigger: str  # signup, purchase, abandoned_cart, etc.
    
    # Sequence
    emails: List[Dict[str, Any]] = Field(default_factory=list)
    delay_between_emails_hours: int = 24
    
    # Targeting
    segment: Dict[str, Any] = Field(default_factory=dict)
    exclude_segments: List[str] = Field(default_factory=list)
    
    # Performance
    sent: int = 0
    opened: int = 0
    clicked: int = 0
    converted: int = 0
    unsubscribed: int = 0
    
    # Status
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class GrowthMetrics(BaseModel):
    """Growth and marketing metrics"""
    date: datetime
    
    # Acquisition
    visitors: int = 0
    signups: int = 0
    trials_started: int = 0
    conversions: int = 0
    
    # Activation
    activated_users: int = 0
    first_site_created: int = 0
    
    # Revenue
    mrr: float = 0.0
    arr: float = 0.0
    ltv: float = 0.0
    cac: float = 0.0
    
    # Retention
    churn_rate: float = 0.0
    retention_rate: float = 0.0
    
    # Referral
    referrals: int = 0
    viral_coefficient: float = 0.0
    
    # Channel performance
    channel_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class MarketingAutomationService:
    """Service for marketing automation and growth tools"""
    
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.affiliates: Dict[str, Affiliate] = {}
        self.referral_program = self._initialize_referral_program()
        self.product_hunt_launch: Optional[ProductHuntLaunch] = None
        self.lifetime_deals: Dict[str, LifetimeDeal] = {}
        self.email_automations: Dict[str, EmailAutomation] = {}
        self.growth_metrics: List[GrowthMetrics] = []
        
        # Initialize with sample data
        self._initialize_sample_campaigns()
    
    def _initialize_referral_program(self) -> ReferralProgram:
        """Initialize default referral program"""
        return ReferralProgram(
            name="KenzySites Referral Program",
            referrer_reward_type=RewardType.CREDITS,
            referrer_reward_amount=500,
            referee_reward_type=RewardType.PERCENTAGE,
            referee_reward_amount=20
        )
    
    def _initialize_sample_campaigns(self):
        """Initialize sample marketing campaigns"""
        
        # Product Hunt Launch
        self.product_hunt_launch = ProductHuntLaunch(
            launch_date=datetime.now() + timedelta(days=7),
            description="Create stunning WordPress sites in 60 seconds with AI. No coding required.",
            launch_offer={
                "discount": 50,
                "duration": "lifetime",
                "code": "PRODUCTHUNT50"
            },
            promo_code="PRODUCTHUNT50"
        )
        
        # Lifetime Deal
        ltd = LifetimeDeal(
            name="KenzySites Lifetime Deal",
            platform="AppSumo",
            regular_price=3564,  # $297/mo * 12
            deal_price=69,
            discount_percentage=98,
            plan_equivalent="professional",
            features=[
                "5 WordPress Sites",
                "15 Landing Pages",
                "5,000 AI Credits/month",
                "All Future Updates",
                "Priority Support"
            ],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=60)
        )
        self.lifetime_deals[ltd.id] = ltd
    
    # Campaign Management
    async def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        budget: Optional[float] = None,
        target_metrics: Optional[Dict[str, Any]] = None
    ) -> Campaign:
        """Create a marketing campaign"""
        
        campaign = Campaign(
            name=name,
            type=campaign_type,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            target_metrics=target_metrics or {}
        )
        
        # Generate tracking codes
        campaign.tracking_codes = {
            "utm_source": campaign_type.value,
            "utm_medium": "campaign",
            "utm_campaign": campaign.id,
            "ref": campaign.id
        }
        
        self.campaigns[campaign.id] = campaign
        
        logger.info(f"Created campaign {campaign.id}: {name}")
        return campaign
    
    async def update_campaign_status(
        self,
        campaign_id: str,
        status: CampaignStatus
    ) -> Campaign:
        """Update campaign status"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        campaign.status = status
        campaign.updated_at = datetime.now()
        
        logger.info(f"Updated campaign {campaign_id} status to {status.value}")
        return campaign
    
    # Affiliate Program
    async def create_affiliate(
        self,
        email: str,
        name: str,
        company: Optional[str] = None,
        website: Optional[str] = None,
        commission_rate: float = 30.0
    ) -> Affiliate:
        """Create an affiliate partner"""
        
        affiliate = Affiliate(
            email=email,
            name=name,
            company=company,
            website=website,
            commission_rate=commission_rate
        )
        
        # Generate tracking link
        affiliate.tracking_link = f"https://kenzysites.com/?ref={affiliate.affiliate_code}"
        
        self.affiliates[affiliate.id] = affiliate
        self.affiliates[affiliate.affiliate_code] = affiliate  # Also store by code
        
        logger.info(f"Created affiliate {affiliate.id}: {name}")
        return affiliate
    
    async def approve_affiliate(
        self,
        affiliate_id: str,
        tier: str = "bronze",
        commission_rate: Optional[float] = None
    ) -> Affiliate:
        """Approve an affiliate application"""
        
        affiliate = self.affiliates.get(affiliate_id)
        if not affiliate:
            raise ValueError(f"Affiliate {affiliate_id} not found")
        
        affiliate.status = AffiliateStatus.APPROVED
        affiliate.approved_at = datetime.now()
        affiliate.tier = tier
        
        if commission_rate:
            affiliate.commission_rate = commission_rate
        
        # Set tier-based commission rates
        tier_rates = {
            "bronze": 30,
            "silver": 35,
            "gold": 40,
            "platinum": 45
        }
        
        if not commission_rate:
            affiliate.commission_rate = tier_rates.get(tier, 30)
        
        logger.info(f"Approved affiliate {affiliate_id} as {tier}")
        return affiliate
    
    async def track_affiliate_conversion(
        self,
        affiliate_code: str,
        order_amount: float,
        customer_id: str
    ) -> Dict[str, Any]:
        """Track an affiliate conversion"""
        
        affiliate = self.affiliates.get(affiliate_code)
        if not affiliate:
            return {"success": False, "error": "Invalid affiliate code"}
        
        # Calculate commission
        if affiliate.commission_type == RewardType.PERCENTAGE:
            commission = order_amount * (affiliate.commission_rate / 100)
        else:
            commission = affiliate.commission_rate
        
        # Update affiliate stats
        affiliate.conversions += 1
        affiliate.total_sales += order_amount
        affiliate.total_commissions += commission
        affiliate.pending_commissions += commission
        
        logger.info(f"Tracked conversion for affiliate {affiliate_code}: ${order_amount}")
        
        return {
            "success": True,
            "affiliate_id": affiliate.id,
            "commission": commission,
            "total_commissions": affiliate.total_commissions
        }
    
    async def process_affiliate_payout(
        self,
        affiliate_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Process affiliate payout"""
        
        affiliate = self.affiliates.get(affiliate_id)
        if not affiliate:
            raise ValueError(f"Affiliate {affiliate_id} not found")
        
        if amount > affiliate.pending_commissions:
            raise ValueError(f"Payout amount exceeds pending commissions")
        
        affiliate.paid_commissions += amount
        affiliate.pending_commissions -= amount
        affiliate.last_payout_date = datetime.now()
        
        logger.info(f"Processed payout of ${amount} for affiliate {affiliate_id}")
        
        return {
            "affiliate_id": affiliate_id,
            "amount_paid": amount,
            "remaining_pending": affiliate.pending_commissions,
            "total_paid": affiliate.paid_commissions
        }
    
    # Referral Program
    async def create_referral(
        self,
        referrer_id: str,
        referee_email: str
    ) -> Dict[str, Any]:
        """Create a referral"""
        
        referral_code = f"REF{uuid.uuid4().hex[:8].upper()}"
        referral_link = f"https://kenzysites.com/?ref={referral_code}"
        
        # Track referral (would store in database)
        self.referral_program.total_referrals += 1
        
        logger.info(f"Created referral {referral_code} from user {referrer_id}")
        
        return {
            "referral_code": referral_code,
            "referral_link": referral_link,
            "referrer_reward": {
                "type": self.referral_program.referrer_reward_type.value,
                "amount": self.referral_program.referrer_reward_amount
            },
            "referee_reward": {
                "type": self.referral_program.referee_reward_type.value,
                "amount": self.referral_program.referee_reward_amount
            }
        }
    
    async def process_referral_conversion(
        self,
        referral_code: str,
        referee_id: str,
        order_amount: float
    ) -> Dict[str, Any]:
        """Process a successful referral conversion"""
        
        self.referral_program.successful_referrals += 1
        
        # Calculate rewards
        referrer_reward = self.referral_program.referrer_reward_amount
        
        if self.referral_program.referee_reward_type == RewardType.PERCENTAGE:
            referee_discount = order_amount * (self.referral_program.referee_reward_amount / 100)
        else:
            referee_discount = self.referral_program.referee_reward_amount
        
        self.referral_program.total_rewards_given += referrer_reward + referee_discount
        
        logger.info(f"Processed referral conversion {referral_code}")
        
        return {
            "success": True,
            "referrer_reward": referrer_reward,
            "referee_discount": referee_discount,
            "total_successful_referrals": self.referral_program.successful_referrals
        }
    
    # Product Hunt Launch
    async def update_product_hunt_stats(
        self,
        upvotes: int,
        comments: int,
        rank: Optional[int] = None,
        featured: bool = False
    ) -> ProductHuntLaunch:
        """Update Product Hunt launch stats"""
        
        if not self.product_hunt_launch:
            raise ValueError("No Product Hunt launch configured")
        
        self.product_hunt_launch.upvotes = upvotes
        self.product_hunt_launch.comments = comments
        self.product_hunt_launch.rank = rank
        self.product_hunt_launch.featured = featured
        
        logger.info(f"Updated Product Hunt stats: {upvotes} upvotes, rank #{rank}")
        return self.product_hunt_launch
    
    async def track_product_hunt_conversion(
        self,
        promo_code: str,
        customer_id: str
    ) -> bool:
        """Track conversion from Product Hunt"""
        
        if not self.product_hunt_launch:
            return False
        
        if promo_code == self.product_hunt_launch.promo_code:
            self.product_hunt_launch.conversions_from_ph += 1
            logger.info(f"Tracked Product Hunt conversion for customer {customer_id}")
            return True
        
        return False
    
    # Lifetime Deals
    async def process_lifetime_deal_purchase(
        self,
        deal_id: str,
        customer_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """Process a lifetime deal purchase"""
        
        deal = self.lifetime_deals.get(deal_id)
        if not deal:
            raise ValueError(f"Lifetime deal {deal_id} not found")
        
        if deal.sold + quantity > deal.total_available:
            raise ValueError("Not enough deals available")
        
        if quantity > deal.max_per_customer:
            raise ValueError(f"Maximum {deal.max_per_customer} per customer")
        
        # Process purchase
        total_amount = deal.deal_price * quantity
        platform_commission = total_amount * (deal.commission_rate / 100)
        net_amount = total_amount - platform_commission
        
        deal.sold += quantity
        deal.revenue += total_amount
        deal.net_revenue += net_amount
        deal.customers.append(customer_id)
        
        logger.info(f"Processed LTD purchase {deal_id} for customer {customer_id}")
        
        return {
            "deal_id": deal_id,
            "quantity": quantity,
            "total_amount": total_amount,
            "net_amount": net_amount,
            "remaining": deal.total_available - deal.sold
        }
    
    # Email Automation
    async def create_email_automation(
        self,
        name: str,
        trigger: str,
        emails: List[Dict[str, Any]]
    ) -> EmailAutomation:
        """Create an email automation sequence"""
        
        automation = EmailAutomation(
            name=name,
            trigger=trigger,
            emails=emails
        )
        
        self.email_automations[automation.id] = automation
        
        logger.info(f"Created email automation {automation.id}: {name}")
        return automation
    
    async def trigger_email_automation(
        self,
        trigger: str,
        user_data: Dict[str, Any]
    ) -> List[str]:
        """Trigger email automations based on event"""
        
        triggered = []
        
        for automation in self.email_automations.values():
            if automation.active and automation.trigger == trigger:
                # Check segment criteria
                # Would queue emails for sending
                automation.sent += 1
                triggered.append(automation.id)
                
                logger.info(f"Triggered automation {automation.id} for {trigger}")
        
        return triggered
    
    # Analytics and Reporting
    async def get_campaign_performance(
        self,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Calculate metrics
        ctr = (campaign.clicks / campaign.impressions * 100) if campaign.impressions > 0 else 0
        conversion_rate = (campaign.conversions / campaign.clicks * 100) if campaign.clicks > 0 else 0
        cpa = (campaign.spent / campaign.conversions) if campaign.conversions > 0 else 0
        roi = ((campaign.revenue - campaign.spent) / campaign.spent * 100) if campaign.spent > 0 else 0
        
        return {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "type": campaign.type.value,
            "status": campaign.status.value,
            "metrics": {
                "impressions": campaign.impressions,
                "clicks": campaign.clicks,
                "conversions": campaign.conversions,
                "revenue": campaign.revenue,
                "spent": campaign.spent,
                "ctr": round(ctr, 2),
                "conversion_rate": round(conversion_rate, 2),
                "cpa": round(cpa, 2),
                "roi": round(roi, 2)
            }
        }
    
    async def get_growth_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get growth metrics for period"""
        
        metrics = [
            m for m in self.growth_metrics
            if start_date <= m.date <= end_date
        ]
        
        if not metrics:
            return {"error": "No metrics for period"}
        
        # Aggregate metrics
        total_signups = sum(m.signups for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        avg_cac = sum(m.cac for m in metrics) / len(metrics)
        avg_ltv = sum(m.ltv for m in metrics) / len(metrics)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "acquisition": {
                "visitors": sum(m.visitors for m in metrics),
                "signups": total_signups,
                "conversions": total_conversions,
                "conversion_rate": (total_conversions / total_signups * 100) if total_signups > 0 else 0
            },
            "revenue": {
                "mrr": metrics[-1].mrr if metrics else 0,
                "arr": metrics[-1].arr if metrics else 0,
                "ltv": avg_ltv,
                "cac": avg_cac,
                "ltv_cac_ratio": (avg_ltv / avg_cac) if avg_cac > 0 else 0
            },
            "retention": {
                "churn_rate": sum(m.churn_rate for m in metrics) / len(metrics),
                "retention_rate": sum(m.retention_rate for m in metrics) / len(metrics)
            },
            "viral": {
                "referrals": sum(m.referrals for m in metrics),
                "viral_coefficient": sum(m.viral_coefficient for m in metrics) / len(metrics)
            }
        }
    
    async def get_affiliate_leaderboard(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing affiliates"""
        
        affiliates = sorted(
            self.affiliates.values(),
            key=lambda x: x.total_sales,
            reverse=True
        )[:limit]
        
        return [
            {
                "rank": i + 1,
                "name": aff.name,
                "company": aff.company,
                "tier": aff.tier,
                "conversions": aff.conversions,
                "total_sales": aff.total_sales,
                "total_commissions": aff.total_commissions
            }
            for i, aff in enumerate(affiliates)
        ]

# Global instance
marketing_automation_service = MarketingAutomationService()