"""
Analytics and Business Metrics Service
Provides comprehensive business intelligence for WordPress AI SaaS
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import statistics

from app.core.config import settings, PLAN_LIMITS
from app.models.analytics_models import (
    BusinessMetrics,
    RevenueMetrics,
    UsageMetrics,
    CustomerMetrics,
    GrowthMetrics,
    PerformanceMetrics,
    ChurnAnalysis,
    CohortAnalysis,
    PredictiveAnalytics
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """
    Service for tracking and analyzing business metrics
    Provides real-time and historical analytics data
    """
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache
        self._metrics_cache = {}
        
    async def get_business_dashboard(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BusinessMetrics:
        """
        Get comprehensive business metrics dashboard
        Includes all KPIs from PRD
        """
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Gather all metrics in parallel
        tasks = [
            self.get_revenue_metrics(start_date, end_date),
            self.get_usage_metrics(start_date, end_date),
            self.get_customer_metrics(start_date, end_date),
            self.get_growth_metrics(start_date, end_date),
            self.get_performance_metrics(),
        ]
        
        results = await asyncio.gather(*tasks)
        
        revenue, usage, customers, growth, performance = results
        
        # Calculate North Star Metrics (PRD)
        mrr = revenue.mrr
        active_sites = usage.total_sites_generated
        nps_score = customers.nps_score
        
        return BusinessMetrics(
            period_start=start_date,
            period_end=end_date,
            
            # North Star Metrics (PRD)
            north_star_metrics={
                "mrr": mrr,
                "active_sites_generated": active_sites,
                "nps_score": nps_score
            },
            
            # Business KPIs (PRD targets)
            business_kpis={
                "mrr_target": 50000 if (end_date - start_date).days <= 180 else 200000,
                "mrr_actual": mrr,
                "mrr_achievement": (mrr / 50000) * 100,
                "active_customers_target": 200 if (end_date - start_date).days <= 180 else 800,
                "active_customers_actual": customers.total_customers,
                "churn_rate_target": 5.0,
                "churn_rate_actual": customers.churn_rate,
                "cac_target": 150,
                "cac_actual": customers.cac,
                "ltv_target": 3500,
                "ltv_actual": customers.ltv,
                "nps_target": 70,
                "nps_actual": nps_score
            },
            
            # Detailed metrics
            revenue_metrics=revenue,
            usage_metrics=usage,
            customer_metrics=customers,
            growth_metrics=growth,
            performance_metrics=performance,
            
            # Summary insights
            insights=await self._generate_insights(revenue, usage, customers, growth)
        )
    
    async def get_revenue_metrics(
        self, 
        start_date: datetime,
        end_date: datetime
    ) -> RevenueMetrics:
        """Calculate revenue metrics"""
        
        # Mock data - would query from database
        total_revenue = 45000.00
        transactions = 150
        
        # Breakdown by plan (PRD pricing)
        revenue_by_plan = {
            "starter": 9700.00,      # 100 customers * R$97
            "professional": 20790.00, # 70 customers * R$297
            "business": 11940.00,     # 20 customers * R$597
            "agency": 3990.00         # 2 customers * R$1,997
        }
        
        # Breakdown by payment method
        revenue_by_method = {
            "PIX": 27000.00,         # 60% PIX (Brazilian preference)
            "CREDIT_CARD": 13500.00, # 30% Credit Card
            "BOLETO": 4500.00        # 10% Boleto
        }
        
        # Calculate MRR and ARR
        mrr = sum(revenue_by_plan.values())
        arr = mrr * 12
        
        # Growth calculations
        previous_month_revenue = 38000.00  # Mock
        growth_rate = ((total_revenue - previous_month_revenue) / previous_month_revenue) * 100
        
        return RevenueMetrics(
            total_revenue=total_revenue,
            recurring_revenue=mrr,
            mrr=mrr,
            arr=arr,
            average_revenue_per_user=total_revenue / 192 if 192 > 0 else 0,  # ARPU
            revenue_by_plan=revenue_by_plan,
            revenue_by_payment_method=revenue_by_method,
            total_transactions=transactions,
            average_transaction_value=total_revenue / transactions if transactions > 0 else 0,
            growth_rate=growth_rate,
            refunds=850.00,  # Mock refunds
            net_revenue=total_revenue - 850.00
        )
    
    async def get_usage_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> UsageMetrics:
        """Calculate usage metrics"""
        
        # Mock usage data - would query from database
        return UsageMetrics(
            total_sites_generated=243,
            sites_by_plan={
                "starter": 100,
                "professional": 105,
                "business": 35,
                "agency": 3
            },
            total_ai_credits_used=125000,
            ai_credits_by_feature={
                "site_generation": 24300,     # 243 sites * 100 credits
                "content_generation": 80000,   # 4000 posts * 20 credits
                "seo_optimization": 15000,     # 1500 optimizations * 10 credits
                "image_generation": 5700       # 1140 images * 5 credits
            },
            total_content_generated=4000,
            content_by_type={
                "blog_posts": 2800,
                "pages": 800,
                "product_descriptions": 300,
                "social_media": 100
            },
            total_storage_used_gb=850.5,
            total_bandwidth_used_gb=12500.75,
            api_calls_total=45000,
            api_calls_by_endpoint={
                "/generate": 15000,
                "/sites/generate": 243,
                "/optimize-seo": 1500,
                "/ai-credits/balance": 28257
            },
            average_generation_time_seconds=4.2,
            peak_usage_hour=14,  # 2 PM
            feature_adoption_rates={
                "site_generation": 95.5,
                "content_automation": 78.2,
                "seo_optimization": 62.4,
                "landing_pages": 45.3,
                "site_cloning": 12.1
            }
        )
    
    async def get_customer_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> CustomerMetrics:
        """Calculate customer metrics"""
        
        # Mock customer data - would query from database
        total_customers = 192
        new_customers = 28
        churned_customers = 10
        
        # Distribution by plan
        customers_by_plan = {
            "starter": 100,
            "professional": 70,
            "business": 20,
            "agency": 2
        }
        
        # Calculate metrics
        churn_rate = (churned_customers / total_customers) * 100 if total_customers > 0 else 0
        retention_rate = 100 - churn_rate
        
        # Customer Acquisition Cost (CAC)
        marketing_spend = 5000.00
        cac = marketing_spend / new_customers if new_customers > 0 else 0
        
        # Lifetime Value (LTV)
        average_revenue_per_customer = 234.00
        average_customer_lifetime_months = 19.2
        ltv = average_revenue_per_customer * average_customer_lifetime_months
        
        # NPS calculation (mock survey data)
        nps_promoters = 65
        nps_detractors = 15
        nps_total_responses = 100
        nps_score = ((nps_promoters - nps_detractors) / nps_total_responses) * 100
        
        return CustomerMetrics(
            total_customers=total_customers,
            new_customers=new_customers,
            churned_customers=churned_customers,
            customers_by_plan=customers_by_plan,
            churn_rate=churn_rate,
            retention_rate=retention_rate,
            cac=cac,
            ltv=ltv,
            ltv_to_cac_ratio=ltv / cac if cac > 0 else 0,
            nps_score=nps_score,
            customer_satisfaction_score=8.2,  # Out of 10
            support_tickets_total=45,
            support_tickets_resolved=42,
            average_resolution_time_hours=3.5,
            activation_rate=82.5,  # % of signups that become active
            expansion_revenue=5200.00,  # From upgrades
            contraction_revenue=1800.00  # From downgrades
        )
    
    async def get_growth_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> GrowthMetrics:
        """Calculate growth metrics"""
        
        # Mock growth data
        return GrowthMetrics(
            revenue_growth_rate=18.4,
            customer_growth_rate=14.6,
            mrr_growth_rate=15.2,
            
            # Compound metrics
            cmgr=15.2,  # Compound Monthly Growth Rate
            quick_ratio=3.2,  # (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
            
            # Efficiency metrics
            burn_rate=35000.00,
            runway_months=18,
            gross_margin=75.2,
            
            # Funnel metrics
            visitor_to_signup_rate=3.5,
            signup_to_paid_rate=22.4,
            trial_to_paid_rate=65.8,
            
            # Viral metrics
            viral_coefficient=0.4,
            referral_rate=12.3,
            
            # Market metrics
            market_share_estimate=0.8,  # % of TAM
            competitive_win_rate=42.5
        )
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate technical performance metrics"""
        
        return PerformanceMetrics(
            uptime_percentage=99.92,
            average_response_time_ms=142,
            p95_response_time_ms=285,
            p99_response_time_ms=520,
            error_rate=0.08,
            
            # AI Performance
            ai_success_rate=98.5,
            average_generation_time_seconds=4.2,
            ai_fallback_rate=2.1,  # % of requests using fallback model
            
            # Infrastructure
            cpu_utilization=42.5,
            memory_utilization=58.2,
            disk_utilization=35.8,
            
            # Database
            database_connections_active=24,
            database_query_time_avg_ms=18,
            cache_hit_rate=94.5,
            
            # CDN & Storage
            cdn_bandwidth_gb=8500,
            storage_used_gb=850,
            
            # Deployments
            deployment_frequency_per_week=12,
            deployment_success_rate=98.5,
            mean_time_to_recovery_minutes=8.5
        )
    
    async def get_churn_analysis(
        self,
        period_days: int = 30
    ) -> ChurnAnalysis:
        """Detailed churn analysis"""
        
        # Mock churn data
        return ChurnAnalysis(
            period_days=period_days,
            total_churned=10,
            churn_rate=5.2,
            
            # Churn by plan
            churn_by_plan={
                "starter": 7,
                "professional": 2,
                "business": 1,
                "agency": 0
            },
            
            # Churn reasons
            churn_reasons={
                "price": 4,
                "features": 2,
                "support": 1,
                "competition": 2,
                "no_longer_needed": 1
            },
            
            # Churn indicators
            average_lifetime_before_churn_days=145,
            warning_signs={
                "low_usage": 6,
                "support_complaints": 2,
                "payment_failures": 2
            },
            
            # Recovery
            win_back_attempts=8,
            win_back_success=2,
            win_back_rate=25.0
        )
    
    async def get_cohort_analysis(
        self,
        cohort_months: int = 6
    ) -> CohortAnalysis:
        """Cohort retention analysis"""
        
        # Mock cohort data
        cohorts = []
        for i in range(cohort_months):
            month = datetime.now() - timedelta(days=30 * i)
            cohort_name = month.strftime("%Y-%m")
            
            # Mock retention data
            retention_curve = [100]  # Start with 100%
            for j in range(1, min(i + 1, 12)):
                # Simulate retention decay
                retention_curve.append(max(65, 100 - (j * 5) + (i * 2)))
            
            cohorts.append({
                "cohort": cohort_name,
                "initial_customers": 30 - (i * 2),
                "retention_curve": retention_curve,
                "ltv": 3500 - (i * 100)
            })
        
        return CohortAnalysis(
            cohorts=cohorts,
            average_retention_month_1=85.0,
            average_retention_month_3=72.0,
            average_retention_month_6=65.0,
            average_retention_month_12=58.0,
            best_performing_cohort="2025-06",
            worst_performing_cohort="2025-03"
        )
    
    async def get_predictive_analytics(self) -> PredictiveAnalytics:
        """Predictive analytics and forecasting"""
        
        # Mock predictions based on current trends
        return PredictiveAnalytics(
            # Revenue predictions
            predicted_mrr_next_month=52000.00,
            predicted_mrr_3_months=68000.00,
            predicted_mrr_6_months=95000.00,
            confidence_level=78.5,
            
            # Customer predictions
            predicted_customers_next_month=215,
            predicted_churn_next_month=11,
            at_risk_customers=18,
            
            # Usage predictions
            predicted_ai_credits_usage_next_month=145000,
            predicted_sites_generated_next_month=280,
            
            # Recommendations
            recommendations=[
                {
                    "type": "retention",
                    "priority": "high",
                    "action": "Implement proactive customer success for at-risk accounts",
                    "potential_impact": "Reduce churn by 2%"
                },
                {
                    "type": "growth",
                    "priority": "medium",
                    "action": "Launch referral program",
                    "potential_impact": "Increase new customers by 15%"
                },
                {
                    "type": "revenue",
                    "priority": "high",
                    "action": "Optimize pricing for Professional plan",
                    "potential_impact": "Increase ARPU by R$30"
                }
            ]
        )
    
    async def _generate_insights(
        self,
        revenue: RevenueMetrics,
        usage: UsageMetrics,
        customers: CustomerMetrics,
        growth: GrowthMetrics
    ) -> List[Dict[str, Any]]:
        """Generate actionable insights from metrics"""
        
        insights = []
        
        # Revenue insights
        if revenue.growth_rate > 15:
            insights.append({
                "type": "positive",
                "category": "revenue",
                "message": f"Revenue growing strongly at {revenue.growth_rate:.1f}%",
                "action": "Maintain growth momentum with increased marketing"
            })
        elif revenue.growth_rate < 10:
            insights.append({
                "type": "warning",
                "category": "revenue",
                "message": f"Revenue growth slowing at {revenue.growth_rate:.1f}%",
                "action": "Review pricing strategy and customer acquisition channels"
            })
        
        # Churn insights
        if customers.churn_rate > 5:
            insights.append({
                "type": "critical",
                "category": "retention",
                "message": f"Churn rate {customers.churn_rate:.1f}% exceeds target of 5%",
                "action": "Implement retention program and customer success initiatives"
            })
        
        # Usage insights
        if usage.feature_adoption_rates.get("content_automation", 0) < 60:
            insights.append({
                "type": "opportunity",
                "category": "product",
                "message": "Content automation adoption below 60%",
                "action": "Create educational content and onboarding for this feature"
            })
        
        # CAC/LTV insights
        if customers.ltv_to_cac_ratio < 3:
            insights.append({
                "type": "warning",
                "category": "economics",
                "message": f"LTV:CAC ratio of {customers.ltv_to_cac_ratio:.1f} is below healthy threshold",
                "action": "Optimize acquisition costs or increase customer lifetime value"
            })
        
        # Performance insights
        ai_credits_utilization = (usage.total_ai_credits_used / 150000) * 100  # Assuming total allocation
        if ai_credits_utilization > 80:
            insights.append({
                "type": "info",
                "category": "usage",
                "message": f"AI Credits utilization at {ai_credits_utilization:.1f}%",
                "action": "Consider optimizing AI usage or adjusting credit allocations"
            })
        
        return insights
    
    async def export_metrics(
        self,
        format: str = "json",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Any:
        """Export metrics in various formats"""
        
        metrics = await self.get_business_dashboard(start_date, end_date)
        
        if format == "json":
            return metrics.dict()
        elif format == "csv":
            # Convert to CSV format
            # Implementation would go here
            pass
        elif format == "pdf":
            # Generate PDF report
            # Implementation would go here
            pass
        
        return metrics.dict()
    
    # Real-time metrics methods
    async def track_event(
        self,
        event_type: str,
        user_id: str,
        properties: Dict[str, Any]
    ):
        """Track custom events for analytics"""
        
        event = {
            "type": event_type,
            "user_id": user_id,
            "properties": properties,
            "timestamp": datetime.now().isoformat()
        }
        
        # Would send to analytics pipeline (e.g., Kafka, Redis Stream)
        logger.info(f"Event tracked: {event_type} for user {user_id}")
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics (last 5 minutes)"""
        
        return {
            "active_users": 42,
            "sites_being_generated": 3,
            "content_being_generated": 8,
            "api_requests_per_minute": 125,
            "average_response_time_ms": 145,
            "error_rate": 0.05,
            "timestamp": datetime.now().isoformat()
        }

# Create singleton instance
analytics_service = AnalyticsService()

__all__ = ['analytics_service', 'AnalyticsService']