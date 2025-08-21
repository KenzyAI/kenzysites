"""
Analytics and Business Metrics API endpoints
Provides comprehensive business intelligence dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.services.analytics_service import analytics_service
from app.models.analytics_models import (
    BusinessMetrics,
    ExecutiveDashboard,
    ProductDashboard,
    MarketingDashboard,
    SalesDashboard,
    CustomerSuccessDashboard,
    ChurnAnalysis,
    CohortAnalysis,
    PredictiveAnalytics,
    MetricAlert
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication
async def get_current_user():
    return {
        "user_id": "admin123",
        "role": "admin",
        "permissions": ["view_analytics", "export_data"]
    }

# Main Dashboard Endpoints
@router.get("/dashboard", response_model=BusinessMetrics)
async def get_business_dashboard(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive business metrics dashboard
    Includes all North Star Metrics and KPIs from PRD
    """
    
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else datetime.now() - timedelta(days=30)
        end = datetime.fromisoformat(end_date) if end_date else datetime.now()
        
        # Get business metrics
        metrics = await analytics_service.get_business_dashboard(start, end)
        
        logger.info(f"Business dashboard requested by {current_user['user_id']}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get business dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get business dashboard: {str(e)}"
        )

@router.get("/dashboard/executive", response_model=ExecutiveDashboard)
async def get_executive_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """
    Get executive-level dashboard with key metrics
    Simplified view for C-level executives
    """
    
    try:
        # Get current metrics
        metrics = await analytics_service.get_business_dashboard()
        
        # Extract executive view
        executive_dashboard = ExecutiveDashboard(
            mrr=metrics.revenue_metrics.mrr,
            arr=metrics.revenue_metrics.arr,
            total_customers=metrics.customer_metrics.total_customers,
            churn_rate=metrics.customer_metrics.churn_rate,
            cac=metrics.customer_metrics.cac,
            ltv=metrics.customer_metrics.ltv,
            nps_score=metrics.customer_metrics.nps_score,
            runway_months=metrics.growth_metrics.runway_months,
            
            # Trends
            mrr_trend="up" if metrics.growth_metrics.mrr_growth_rate > 0 else "down",
            customer_trend="up" if metrics.growth_metrics.customer_growth_rate > 0 else "down",
            churn_trend="down" if metrics.customer_metrics.churn_rate < 5 else "up",
            
            # Highlights
            top_achievements=[
                f"MRR reached R$ {metrics.revenue_metrics.mrr:,.2f}",
                f"Customer base grew {metrics.growth_metrics.customer_growth_rate:.1f}%",
                f"NPS score at {metrics.customer_metrics.nps_score:.0f}"
            ],
            key_risks=[
                risk["message"] for risk in metrics.insights 
                if risk.get("type") in ["warning", "critical"]
            ][:3],
            action_items=[
                insight["action"] for insight in metrics.insights
                if insight.get("action")
            ][:3]
        )
        
        return executive_dashboard
        
    except Exception as e:
        logger.error(f"Failed to get executive dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get executive dashboard: {str(e)}"
        )

@router.get("/dashboard/product", response_model=ProductDashboard)
async def get_product_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get product team dashboard with feature metrics"""
    
    try:
        metrics = await analytics_service.get_business_dashboard()
        
        # Extract product metrics
        product_dashboard = ProductDashboard(
            feature_adoption=metrics.usage_metrics.feature_adoption_rates,
            time_to_value_minutes=5.0,  # Mock data
            user_engagement_score=7.8,  # Mock data
            
            most_used_features=["site_generation", "content_automation", "seo_optimization"],
            least_used_features=["site_cloning", "white_label"],
            
            bug_count=12,
            feature_requests=28,
            average_bug_resolution_days=2.5,
            
            active_experiments=3,
            completed_experiments=[
                {
                    "name": "New onboarding flow",
                    "winner": "variant_b",
                    "improvement": "15% better activation"
                }
            ]
        )
        
        return product_dashboard
        
    except Exception as e:
        logger.error(f"Failed to get product dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product dashboard: {str(e)}"
        )

# Detailed Analytics Endpoints
@router.get("/revenue", response_model=Dict[str, Any])
async def get_revenue_analytics(
    period_days: int = Query(30, description="Period in days"),
    breakdown_by: Optional[str] = Query(None, description="Breakdown by: plan, method, daily"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed revenue analytics"""
    
    try:
        start_date = datetime.now() - timedelta(days=period_days)
        end_date = datetime.now()
        
        revenue = await analytics_service.get_revenue_metrics(start_date, end_date)
        
        result = {
            "period": f"{period_days} days",
            "metrics": revenue.dict(),
            "summary": {
                "total_revenue": f"R$ {revenue.total_revenue:,.2f}",
                "mrr": f"R$ {revenue.mrr:,.2f}",
                "growth_rate": f"{revenue.growth_rate:.1f}%",
                "average_ticket": f"R$ {revenue.average_transaction_value:,.2f}"
            }
        }
        
        if breakdown_by == "plan":
            result["breakdown"] = revenue.revenue_by_plan
        elif breakdown_by == "method":
            result["breakdown"] = revenue.revenue_by_payment_method
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get revenue analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get revenue analytics: {str(e)}"
        )

@router.get("/usage", response_model=Dict[str, Any])
async def get_usage_analytics(
    period_days: int = Query(30, description="Period in days"),
    feature: Optional[str] = Query(None, description="Filter by feature"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed usage analytics"""
    
    try:
        start_date = datetime.now() - timedelta(days=period_days)
        end_date = datetime.now()
        
        usage = await analytics_service.get_usage_metrics(start_date, end_date)
        
        result = {
            "period": f"{period_days} days",
            "metrics": usage.dict(),
            "summary": {
                "total_sites": usage.total_sites_generated,
                "total_content": usage.total_content_generated,
                "ai_credits_used": usage.total_ai_credits_used,
                "average_generation_time": f"{usage.average_generation_time_seconds:.1f}s"
            }
        }
        
        if feature:
            result["feature_detail"] = {
                "adoption_rate": usage.feature_adoption_rates.get(feature, 0),
                "ai_credits": usage.ai_credits_by_feature.get(feature, 0)
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get usage analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage analytics: {str(e)}"
        )

@router.get("/customers", response_model=Dict[str, Any])
async def get_customer_analytics(
    period_days: int = Query(30, description="Period in days"),
    segment: Optional[str] = Query(None, description="Customer segment"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed customer analytics"""
    
    try:
        start_date = datetime.now() - timedelta(days=period_days)
        end_date = datetime.now()
        
        customers = await analytics_service.get_customer_metrics(start_date, end_date)
        
        result = {
            "period": f"{period_days} days",
            "metrics": customers.dict(),
            "summary": {
                "total_customers": customers.total_customers,
                "churn_rate": f"{customers.churn_rate:.1f}%",
                "nps_score": customers.nps_score,
                "ltv_cac_ratio": f"{customers.ltv_to_cac_ratio:.1f}x"
            },
            "health": {
                "status": "healthy" if customers.churn_rate < 5 else "at_risk",
                "recommendation": "Focus on retention" if customers.churn_rate > 5 else "Scale acquisition"
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get customer analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer analytics: {str(e)}"
        )

@router.get("/churn", response_model=ChurnAnalysis)
async def get_churn_analysis(
    period_days: int = Query(30, description="Period in days"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed churn analysis"""
    
    try:
        analysis = await analytics_service.get_churn_analysis(period_days)
        return analysis
        
    except Exception as e:
        logger.error(f"Failed to get churn analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get churn analysis: {str(e)}"
        )

@router.get("/cohorts", response_model=CohortAnalysis)
async def get_cohort_analysis(
    months: int = Query(6, description="Number of cohort months"),
    current_user: dict = Depends(get_current_user)
):
    """Get cohort retention analysis"""
    
    try:
        analysis = await analytics_service.get_cohort_analysis(months)
        return analysis
        
    except Exception as e:
        logger.error(f"Failed to get cohort analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cohort analysis: {str(e)}"
        )

@router.get("/predictions", response_model=PredictiveAnalytics)
async def get_predictive_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get predictive analytics and forecasts"""
    
    try:
        predictions = await analytics_service.get_predictive_analytics()
        return predictions
        
    except Exception as e:
        logger.error(f"Failed to get predictive analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get predictive analytics: {str(e)}"
        )

# Real-time Metrics
@router.get("/realtime", response_model=Dict[str, Any])
async def get_realtime_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get real-time metrics (last 5 minutes)"""
    
    try:
        metrics = await analytics_service.get_real_time_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get real-time metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get real-time metrics: {str(e)}"
        )

# Export Endpoints
@router.get("/export")
async def export_analytics(
    format: str = Query("json", description="Export format: json, csv, pdf"),
    start_date: Optional[str] = Query(None, description="Start date"),
    end_date: Optional[str] = Query(None, description="End date"),
    current_user: dict = Depends(get_current_user)
):
    """Export analytics data in various formats"""
    
    try:
        # Check permissions
        if "export_data" not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=403,
                detail="User doesn't have export permissions"
            )
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Export data
        data = await analytics_service.export_metrics(format, start, end)
        
        logger.info(f"Analytics exported by {current_user['user_id']} in {format} format")
        
        return data
        
    except Exception as e:
        logger.error(f"Failed to export analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export analytics: {str(e)}"
        )

# Event Tracking
@router.post("/track")
async def track_event(
    event_type: str,
    properties: Dict[str, Any] = {},
    current_user: dict = Depends(get_current_user)
):
    """Track custom analytics events"""
    
    try:
        await analytics_service.track_event(
            event_type=event_type,
            user_id=current_user["user_id"],
            properties=properties
        )
        
        return {
            "success": True,
            "message": f"Event {event_type} tracked successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to track event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track event: {str(e)}"
        )

# Alerts and Monitoring
@router.get("/alerts", response_model=List[MetricAlert])
async def get_metric_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: info, warning, critical"),
    current_user: dict = Depends(get_current_user)
):
    """Get active metric alerts"""
    
    try:
        # Mock alerts - would come from monitoring system
        alerts = [
            MetricAlert(
                alert_id="alert_001",
                metric_name="churn_rate",
                current_value=5.8,
                threshold_value=5.0,
                alert_type="above",
                severity="warning",
                message="Churn rate exceeds target threshold"
            ),
            MetricAlert(
                alert_id="alert_002",
                metric_name="api_response_time",
                current_value=285,
                threshold_value=200,
                alert_type="above",
                severity="info",
                message="API response time slightly elevated"
            )
        ]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alerts: {str(e)}"
        )

# Benchmarks
@router.get("/benchmarks", response_model=Dict[str, Any])
async def get_industry_benchmarks(
    current_user: dict = Depends(get_current_user)
):
    """Get industry benchmarks for comparison"""
    
    return {
        "saas_benchmarks": {
            "churn_rate": {
                "excellent": 3.0,
                "good": 5.0,
                "average": 7.0,
                "poor": 10.0,
                "our_value": 5.2
            },
            "ltv_cac_ratio": {
                "excellent": 5.0,
                "good": 3.0,
                "average": 2.0,
                "poor": 1.0,
                "our_value": 3.2
            },
            "nps_score": {
                "excellent": 70,
                "good": 50,
                "average": 30,
                "poor": 0,
                "our_value": 65
            },
            "gross_margin": {
                "excellent": 80,
                "good": 70,
                "average": 60,
                "poor": 50,
                "our_value": 75.2
            }
        },
        "comparison": {
            "overall_health": "good",
            "strengths": ["Customer satisfaction", "Product-market fit"],
            "improvements": ["Reduce churn rate", "Increase viral coefficient"]
        }
    }