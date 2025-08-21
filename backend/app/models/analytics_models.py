"""
Analytics Models and Schemas for Business Metrics
Aligned with PRD KPIs and North Star Metrics
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Metric Categories
class MetricCategory(str, Enum):
    REVENUE = "revenue"
    USAGE = "usage"
    CUSTOMER = "customer"
    GROWTH = "growth"
    PERFORMANCE = "performance"
    PRODUCT = "product"

class InsightType(str, Enum):
    POSITIVE = "positive"
    WARNING = "warning"
    CRITICAL = "critical"
    OPPORTUNITY = "opportunity"
    INFO = "info"

# Revenue Metrics
class RevenueMetrics(BaseModel):
    """Revenue and financial metrics"""
    total_revenue: float = Field(..., description="Total revenue in period")
    recurring_revenue: float = Field(..., description="Recurring revenue")
    mrr: float = Field(..., description="Monthly Recurring Revenue")
    arr: float = Field(..., description="Annual Recurring Revenue")
    average_revenue_per_user: float = Field(..., description="ARPU")
    
    # Breakdowns
    revenue_by_plan: Dict[str, float] = Field(default_factory=dict)
    revenue_by_payment_method: Dict[str, float] = Field(default_factory=dict)
    
    # Transactions
    total_transactions: int = 0
    average_transaction_value: float = 0
    
    # Growth
    growth_rate: float = 0
    refunds: float = 0
    net_revenue: float = 0

# Usage Metrics
class UsageMetrics(BaseModel):
    """Platform usage and adoption metrics"""
    # Sites
    total_sites_generated: int = 0
    sites_by_plan: Dict[str, int] = Field(default_factory=dict)
    
    # AI Credits
    total_ai_credits_used: int = 0
    ai_credits_by_feature: Dict[str, int] = Field(default_factory=dict)
    
    # Content
    total_content_generated: int = 0
    content_by_type: Dict[str, int] = Field(default_factory=dict)
    
    # Resources
    total_storage_used_gb: float = 0
    total_bandwidth_used_gb: float = 0
    
    # API Usage
    api_calls_total: int = 0
    api_calls_by_endpoint: Dict[str, int] = Field(default_factory=dict)
    
    # Performance
    average_generation_time_seconds: float = 0
    peak_usage_hour: int = 0  # Hour of day (0-23)
    
    # Feature Adoption
    feature_adoption_rates: Dict[str, float] = Field(default_factory=dict)

# Customer Metrics
class CustomerMetrics(BaseModel):
    """Customer-related metrics"""
    # Customer counts
    total_customers: int = 0
    new_customers: int = 0
    churned_customers: int = 0
    customers_by_plan: Dict[str, int] = Field(default_factory=dict)
    
    # Retention & Churn
    churn_rate: float = 0
    retention_rate: float = 0
    
    # Economics
    cac: float = Field(0, description="Customer Acquisition Cost")
    ltv: float = Field(0, description="Customer Lifetime Value")
    ltv_to_cac_ratio: float = 0
    
    # Satisfaction
    nps_score: float = Field(0, description="Net Promoter Score")
    customer_satisfaction_score: float = 0
    
    # Support
    support_tickets_total: int = 0
    support_tickets_resolved: int = 0
    average_resolution_time_hours: float = 0
    
    # Revenue movements
    activation_rate: float = 0
    expansion_revenue: float = 0
    contraction_revenue: float = 0

# Growth Metrics
class GrowthMetrics(BaseModel):
    """Growth and efficiency metrics"""
    # Growth rates
    revenue_growth_rate: float = 0
    customer_growth_rate: float = 0
    mrr_growth_rate: float = 0
    
    # Compound metrics
    cmgr: float = Field(0, description="Compound Monthly Growth Rate")
    quick_ratio: float = 0
    
    # Efficiency
    burn_rate: float = 0
    runway_months: float = 0
    gross_margin: float = 0
    
    # Funnel
    visitor_to_signup_rate: float = 0
    signup_to_paid_rate: float = 0
    trial_to_paid_rate: float = 0
    
    # Viral
    viral_coefficient: float = 0
    referral_rate: float = 0
    
    # Market
    market_share_estimate: float = 0
    competitive_win_rate: float = 0

# Performance Metrics
class PerformanceMetrics(BaseModel):
    """Technical performance metrics"""
    # Availability
    uptime_percentage: float = 99.9
    average_response_time_ms: float = 0
    p95_response_time_ms: float = 0
    p99_response_time_ms: float = 0
    error_rate: float = 0
    
    # AI Performance
    ai_success_rate: float = 0
    average_generation_time_seconds: float = 0
    ai_fallback_rate: float = 0
    
    # Infrastructure
    cpu_utilization: float = 0
    memory_utilization: float = 0
    disk_utilization: float = 0
    
    # Database
    database_connections_active: int = 0
    database_query_time_avg_ms: float = 0
    cache_hit_rate: float = 0
    
    # CDN & Storage
    cdn_bandwidth_gb: float = 0
    storage_used_gb: float = 0
    
    # Deployments
    deployment_frequency_per_week: float = 0
    deployment_success_rate: float = 0
    mean_time_to_recovery_minutes: float = 0

# Churn Analysis
class ChurnAnalysis(BaseModel):
    """Detailed churn analysis"""
    period_days: int
    total_churned: int
    churn_rate: float
    
    # Breakdown
    churn_by_plan: Dict[str, int] = Field(default_factory=dict)
    churn_reasons: Dict[str, int] = Field(default_factory=dict)
    
    # Patterns
    average_lifetime_before_churn_days: float
    warning_signs: Dict[str, int] = Field(default_factory=dict)
    
    # Recovery
    win_back_attempts: int = 0
    win_back_success: int = 0
    win_back_rate: float = 0

# Cohort Analysis
class CohortAnalysis(BaseModel):
    """Cohort retention analysis"""
    cohorts: List[Dict[str, Any]] = Field(default_factory=list)
    average_retention_month_1: float
    average_retention_month_3: float
    average_retention_month_6: float
    average_retention_month_12: float
    best_performing_cohort: str
    worst_performing_cohort: str

# Predictive Analytics
class PredictiveAnalytics(BaseModel):
    """Predictive analytics and forecasting"""
    # Revenue predictions
    predicted_mrr_next_month: float
    predicted_mrr_3_months: float
    predicted_mrr_6_months: float
    confidence_level: float
    
    # Customer predictions
    predicted_customers_next_month: int
    predicted_churn_next_month: int
    at_risk_customers: int
    
    # Usage predictions
    predicted_ai_credits_usage_next_month: int
    predicted_sites_generated_next_month: int
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)

# Main Business Metrics Dashboard
class BusinessMetrics(BaseModel):
    """Comprehensive business metrics dashboard"""
    period_start: datetime
    period_end: datetime
    
    # North Star Metrics (PRD)
    north_star_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Primary: MRR, Secondary: Active Sites, Tertiary: NPS"
    )
    
    # Business KPIs (PRD targets)
    business_kpis: Dict[str, Any] = Field(default_factory=dict)
    
    # Detailed metrics
    revenue_metrics: RevenueMetrics
    usage_metrics: UsageMetrics
    customer_metrics: CustomerMetrics
    growth_metrics: GrowthMetrics
    performance_metrics: PerformanceMetrics
    
    # Insights
    insights: List[Dict[str, Any]] = Field(default_factory=list)

# Dashboard Views
class ExecutiveDashboard(BaseModel):
    """Executive-level dashboard view"""
    mrr: float
    arr: float
    total_customers: int
    churn_rate: float
    cac: float
    ltv: float
    nps_score: float
    runway_months: float
    
    # Key trends
    mrr_trend: str  # "up", "down", "stable"
    customer_trend: str
    churn_trend: str
    
    # Highlights
    top_achievements: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)

class ProductDashboard(BaseModel):
    """Product team dashboard view"""
    feature_adoption: Dict[str, float] = Field(default_factory=dict)
    time_to_value_minutes: float
    user_engagement_score: float
    
    # Usage patterns
    most_used_features: List[str] = Field(default_factory=list)
    least_used_features: List[str] = Field(default_factory=list)
    
    # Quality metrics
    bug_count: int = 0
    feature_requests: int = 0
    average_bug_resolution_days: float = 0
    
    # A/B tests
    active_experiments: int = 0
    completed_experiments: List[Dict[str, Any]] = Field(default_factory=list)

class MarketingDashboard(BaseModel):
    """Marketing team dashboard view"""
    # Acquisition
    website_visitors: int = 0
    signups: int = 0
    conversion_rate: float = 0
    
    # Channels
    traffic_by_source: Dict[str, int] = Field(default_factory=dict)
    conversions_by_source: Dict[str, int] = Field(default_factory=dict)
    cac_by_channel: Dict[str, float] = Field(default_factory=dict)
    
    # Campaigns
    active_campaigns: int = 0
    campaign_performance: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Content
    blog_posts_published: int = 0
    email_subscribers: int = 0
    email_open_rate: float = 0
    email_click_rate: float = 0

class SalesDashboard(BaseModel):
    """Sales team dashboard view"""
    # Pipeline
    leads_total: int = 0
    qualified_leads: int = 0
    opportunities: int = 0
    deals_closed: int = 0
    
    # Performance
    conversion_rate: float = 0
    average_deal_size: float = 0
    sales_cycle_days: float = 0
    
    # Forecast
    pipeline_value: float = 0
    forecast_current_month: float = 0
    forecast_next_month: float = 0
    
    # Team
    sales_by_rep: Dict[str, float] = Field(default_factory=dict)
    activities_completed: int = 0

class CustomerSuccessDashboard(BaseModel):
    """Customer Success team dashboard view"""
    # Health
    healthy_accounts: int = 0
    at_risk_accounts: int = 0
    churned_accounts: int = 0
    
    # Engagement
    average_login_frequency_days: float = 0
    feature_usage_depth: float = 0
    
    # Support
    tickets_open: int = 0
    tickets_resolved: int = 0
    average_response_time_hours: float = 0
    csat_score: float = 0
    
    # Success metrics
    onboarding_completion_rate: float = 0
    time_to_first_value_days: float = 0
    expansion_opportunities: int = 0
    renewal_rate: float = 0

# Alert Models
class MetricAlert(BaseModel):
    """Alert for metric thresholds"""
    alert_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    alert_type: str  # "above", "below", "equals"
    severity: str  # "info", "warning", "critical"
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    auto_resolved: bool = False

class AnomalyDetection(BaseModel):
    """Anomaly detection results"""
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_percentage: float
    is_anomaly: bool
    confidence: float
    possible_causes: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)