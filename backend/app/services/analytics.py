"""
Analytics Service for KenzySites
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
import hashlib
import user_agents
from pydantic import BaseModel

class AnalyticsEvent(BaseModel):
    """Analytics event model"""
    event_type: str
    site_id: str
    user_id: Optional[str] = None
    session_id: str
    page_url: str
    referrer: Optional[str] = None
    user_agent: str
    ip_address: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime

class PageView(BaseModel):
    """Page view analytics"""
    url: str
    title: str
    views: int
    unique_visitors: int
    avg_time_on_page: float
    bounce_rate: float
    exit_rate: float

class VisitorInfo(BaseModel):
    """Visitor information"""
    visitor_id: str
    first_seen: datetime
    last_seen: datetime
    total_visits: int
    total_pageviews: int
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: str
    browser: str
    os: str
    referrer_source: Optional[str] = None

class SiteMetrics(BaseModel):
    """Site-wide metrics"""
    total_pageviews: int
    unique_visitors: int
    avg_session_duration: float
    bounce_rate: float
    pages_per_session: float
    new_vs_returning: Dict[str, int]
    top_pages: List[PageView]
    top_referrers: List[Dict[str, Any]]
    devices: Dict[str, int]
    browsers: Dict[str, int]
    countries: Dict[str, int]

class ConversionMetrics(BaseModel):
    """Conversion tracking metrics"""
    total_conversions: int
    conversion_rate: float
    conversion_value: float
    top_converting_pages: List[Dict[str, Any]]
    conversion_funnel: List[Dict[str, Any]]

class AnalyticsService:
    """Service for tracking and analyzing site metrics"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.geoip_reader = None  # Initialize with GeoIP database if available
        
    def track_event(self, event: AnalyticsEvent) -> bool:
        """Track an analytics event"""
        try:
            # Parse user agent
            ua = user_agents.parse(event.user_agent)
            
            # Get geolocation (if GeoIP database is available)
            location = self._get_location(event.ip_address)
            
            # Hash IP for privacy
            hashed_ip = hashlib.sha256(event.ip_address.encode()).hexdigest()
            
            # Store event in database
            event_data = {
                "event_type": event.event_type,
                "site_id": event.site_id,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "page_url": event.page_url,
                "referrer": event.referrer,
                "user_agent": event.user_agent,
                "hashed_ip": hashed_ip,
                "device_type": self._get_device_type(ua),
                "browser": ua.browser.family,
                "browser_version": ua.browser.version_string,
                "os": ua.os.family,
                "os_version": ua.os.version_string,
                "country": location.get("country") if location else None,
                "city": location.get("city") if location else None,
                "metadata": json.dumps(event.metadata),
                "timestamp": event.timestamp
            }
            
            # In a real implementation, save to database
            # self.db.add(AnalyticsEventModel(**event_data))
            # self.db.commit()
            
            return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            return False
    
    def track_pageview(
        self,
        site_id: str,
        page_url: str,
        page_title: str,
        session_id: str,
        user_agent: str,
        ip_address: str,
        referrer: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Track a page view"""
        event = AnalyticsEvent(
            event_type="pageview",
            site_id=site_id,
            user_id=user_id,
            session_id=session_id,
            page_url=page_url,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            metadata={"title": page_title},
            timestamp=datetime.now(timezone.utc)
        )
        return self.track_event(event)
    
    def track_conversion(
        self,
        site_id: str,
        conversion_type: str,
        conversion_value: float,
        session_id: str,
        page_url: str,
        user_agent: str,
        ip_address: str,
        metadata: Dict[str, Any] = {}
    ) -> bool:
        """Track a conversion event"""
        event = AnalyticsEvent(
            event_type="conversion",
            site_id=site_id,
            session_id=session_id,
            page_url=page_url,
            user_agent=user_agent,
            ip_address=ip_address,
            metadata={
                "conversion_type": conversion_type,
                "conversion_value": conversion_value,
                **metadata
            },
            timestamp=datetime.now(timezone.utc)
        )
        return self.track_event(event)
    
    def get_site_metrics(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> SiteMetrics:
        """Get comprehensive site metrics"""
        # In a real implementation, query from database
        # For now, return sample data
        
        return SiteMetrics(
            total_pageviews=15234,
            unique_visitors=3421,
            avg_session_duration=245.5,  # seconds
            bounce_rate=42.3,
            pages_per_session=3.2,
            new_vs_returning={"new": 2100, "returning": 1321},
            top_pages=[
                PageView(
                    url="/",
                    title="Home",
                    views=5234,
                    unique_visitors=2341,
                    avg_time_on_page=120.5,
                    bounce_rate=35.2,
                    exit_rate=28.4
                ),
                PageView(
                    url="/produtos",
                    title="Produtos",
                    views=3421,
                    unique_visitors=1823,
                    avg_time_on_page=180.3,
                    bounce_rate=25.1,
                    exit_rate=45.2
                )
            ],
            top_referrers=[
                {"source": "google", "visits": 1523, "percentage": 44.5},
                {"source": "direct", "visits": 892, "percentage": 26.1},
                {"source": "facebook", "visits": 567, "percentage": 16.6}
            ],
            devices={"desktop": 1823, "mobile": 1342, "tablet": 256},
            browsers={"Chrome": 1892, "Safari": 823, "Firefox": 456, "Edge": 250},
            countries={"BR": 2890, "US": 234, "PT": 156, "Others": 141}
        )
    
    def get_realtime_visitors(self, site_id: str) -> Dict[str, Any]:
        """Get real-time visitor data"""
        # In a real implementation, query active sessions from last 5 minutes
        now = datetime.now(timezone.utc)
        five_minutes_ago = now - timedelta(minutes=5)
        
        return {
            "active_visitors": 42,
            "pages_being_viewed": [
                {"url": "/", "visitors": 12},
                {"url": "/produtos", "visitors": 8},
                {"url": "/contato", "visitors": 5}
            ],
            "top_referrers": [
                {"source": "google", "visitors": 15},
                {"source": "direct", "visitors": 12}
            ],
            "locations": [
                {"country": "Brazil", "city": "São Paulo", "visitors": 18},
                {"country": "Brazil", "city": "Rio de Janeiro", "visitors": 8}
            ]
        }
    
    def get_traffic_sources(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze traffic sources"""
        return {
            "organic_search": {
                "visits": 5234,
                "percentage": 42.3,
                "keywords": [
                    {"keyword": "restaurante são paulo", "visits": 234},
                    {"keyword": "delivery comida", "visits": 189}
                ]
            },
            "direct": {
                "visits": 3421,
                "percentage": 27.6
            },
            "social": {
                "visits": 2345,
                "percentage": 18.9,
                "networks": [
                    {"network": "Facebook", "visits": 1234},
                    {"network": "Instagram", "visits": 789},
                    {"network": "WhatsApp", "visits": 322}
                ]
            },
            "referral": {
                "visits": 1389,
                "percentage": 11.2,
                "sites": [
                    {"site": "blog.exemplo.com", "visits": 456},
                    {"site": "parceiro.com.br", "visits": 234}
                ]
            }
        }
    
    def get_user_behavior(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        return {
            "user_flow": [
                {
                    "path": ["home", "produtos", "checkout"],
                    "users": 234,
                    "conversion_rate": 45.2
                },
                {
                    "path": ["home", "sobre", "contato"],
                    "users": 189,
                    "conversion_rate": 23.4
                }
            ],
            "engagement": {
                "avg_time_on_site": 245.5,
                "pages_per_session": 3.2,
                "scroll_depth": {
                    "25%": 89.2,
                    "50%": 67.3,
                    "75%": 45.1,
                    "100%": 23.4
                }
            },
            "interactions": {
                "clicks": [
                    {"element": "cta-button", "clicks": 456},
                    {"element": "whatsapp-button", "clicks": 234}
                ],
                "forms": [
                    {"form": "contact", "submissions": 123, "completion_rate": 67.2}
                ]
            }
        }
    
    def get_conversion_metrics(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> ConversionMetrics:
        """Get conversion metrics"""
        return ConversionMetrics(
            total_conversions=234,
            conversion_rate=3.4,
            conversion_value=45678.90,
            top_converting_pages=[
                {"page": "/produtos/item-1", "conversions": 45, "rate": 5.2},
                {"page": "/promocoes", "conversions": 34, "rate": 4.1}
            ],
            conversion_funnel=[
                {"step": "Página Inicial", "users": 1000, "dropoff": 0},
                {"step": "Produtos", "users": 650, "dropoff": 35.0},
                {"step": "Carrinho", "users": 320, "dropoff": 50.8},
                {"step": "Checkout", "users": 180, "dropoff": 43.8},
                {"step": "Confirmação", "users": 150, "dropoff": 16.7}
            ]
        )
    
    def get_performance_metrics(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get site performance metrics"""
        return {
            "page_load_times": {
                "avg": 2.3,
                "median": 2.1,
                "p95": 4.5,
                "by_page": [
                    {"page": "/", "avg_load_time": 1.8},
                    {"page": "/produtos", "avg_load_time": 2.5}
                ]
            },
            "core_web_vitals": {
                "lcp": {"value": 2.1, "rating": "good"},  # Largest Contentful Paint
                "fid": {"value": 45, "rating": "good"},   # First Input Delay
                "cls": {"value": 0.08, "rating": "good"}  # Cumulative Layout Shift
            },
            "errors": {
                "js_errors": 23,
                "404_errors": 45,
                "500_errors": 2
            },
            "uptime": 99.95
        }
    
    def get_audience_insights(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get audience demographic insights"""
        return {
            "demographics": {
                "age_groups": {
                    "18-24": 15.2,
                    "25-34": 28.4,
                    "35-44": 25.1,
                    "45-54": 18.3,
                    "55+": 13.0
                },
                "gender": {
                    "male": 48.2,
                    "female": 51.8
                },
                "interests": [
                    {"category": "Tecnologia", "percentage": 34.2},
                    {"category": "Comida", "percentage": 28.1},
                    {"category": "Viagens", "percentage": 19.4}
                ]
            },
            "geography": {
                "countries": [
                    {"country": "Brazil", "visitors": 8234, "percentage": 82.3},
                    {"country": "Portugal", "visitors": 823, "percentage": 8.2}
                ],
                "cities": [
                    {"city": "São Paulo", "visitors": 2345, "percentage": 23.4},
                    {"city": "Rio de Janeiro", "visitors": 1234, "percentage": 12.3}
                ]
            },
            "technology": {
                "devices": {
                    "desktop": 45.2,
                    "mobile": 48.3,
                    "tablet": 6.5
                },
                "browsers": {
                    "Chrome": 52.3,
                    "Safari": 23.1,
                    "Firefox": 12.4,
                    "Edge": 8.2,
                    "Others": 4.0
                },
                "os": {
                    "Windows": 35.2,
                    "Android": 28.4,
                    "iOS": 21.3,
                    "macOS": 12.1,
                    "Linux": 3.0
                },
                "screen_resolutions": [
                    {"resolution": "1920x1080", "percentage": 23.4},
                    {"resolution": "1366x768", "percentage": 18.2},
                    {"resolution": "375x812", "percentage": 15.3}
                ]
            }
        }
    
    def get_seo_metrics(
        self,
        site_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get SEO performance metrics"""
        return {
            "organic_traffic": {
                "visits": 5234,
                "growth": 12.3,
                "top_landing_pages": [
                    {"page": "/blog/artigo-1", "visits": 523},
                    {"page": "/produtos", "visits": 412}
                ]
            },
            "keywords": {
                "total": 234,
                "top_performing": [
                    {"keyword": "produto exemplo", "position": 3, "clicks": 234},
                    {"keyword": "serviço cidade", "position": 5, "clicks": 189}
                ],
                "opportunities": [
                    {"keyword": "nova palavra", "current_position": 11, "potential_traffic": 456}
                ]
            },
            "backlinks": {
                "total": 456,
                "new_this_period": 23,
                "lost_this_period": 5,
                "domain_authority": 42
            },
            "technical_seo": {
                "indexed_pages": 123,
                "crawl_errors": 5,
                "mobile_friendly": True,
                "avg_page_speed": 2.3,
                "structured_data": True
            }
        }
    
    def get_custom_dashboard(
        self,
        site_id: str,
        widgets: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get custom dashboard data based on selected widgets"""
        dashboard_data = {}
        
        widget_mapping = {
            "overview": lambda: self.get_site_metrics(site_id, start_date, end_date),
            "realtime": lambda: self.get_realtime_visitors(site_id),
            "traffic": lambda: self.get_traffic_sources(site_id, start_date, end_date),
            "behavior": lambda: self.get_user_behavior(site_id, start_date, end_date),
            "conversions": lambda: self.get_conversion_metrics(site_id, start_date, end_date),
            "performance": lambda: self.get_performance_metrics(site_id, start_date, end_date),
            "audience": lambda: self.get_audience_insights(site_id, start_date, end_date),
            "seo": lambda: self.get_seo_metrics(site_id, start_date, end_date)
        }
        
        for widget in widgets:
            if widget in widget_mapping:
                dashboard_data[widget] = widget_mapping[widget]()
        
        return dashboard_data
    
    def generate_report(
        self,
        site_id: str,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        format: str = "json"
    ) -> Any:
        """Generate analytics report"""
        # Collect all metrics
        report_data = {
            "site_id": site_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "overview": self.get_site_metrics(site_id, start_date, end_date).dict(),
                "traffic": self.get_traffic_sources(site_id, start_date, end_date),
                "behavior": self.get_user_behavior(site_id, start_date, end_date),
                "conversions": self.get_conversion_metrics(site_id, start_date, end_date).dict(),
                "performance": self.get_performance_metrics(site_id, start_date, end_date),
                "audience": self.get_audience_insights(site_id, start_date, end_date),
                "seo": self.get_seo_metrics(site_id, start_date, end_date)
            }
        }
        
        if format == "json":
            return report_data
        elif format == "csv":
            # Convert to CSV format
            pass
        elif format == "pdf":
            # Generate PDF report
            pass
        
        return report_data
    
    def _get_device_type(self, ua) -> str:
        """Determine device type from user agent"""
        if ua.is_mobile:
            return "mobile"
        elif ua.is_tablet:
            return "tablet"
        elif ua.is_pc:
            return "desktop"
        else:
            return "other"
    
    def _get_location(self, ip_address: str) -> Optional[Dict[str, str]]:
        """Get location from IP address"""
        # In a real implementation, use GeoIP database
        # For now, return None
        return None
    
    def track_goal(
        self,
        site_id: str,
        goal_id: str,
        goal_value: float,
        session_id: str,
        metadata: Dict[str, Any] = {}
    ) -> bool:
        """Track goal completion"""
        # Implementation for goal tracking
        return True
    
    def get_ab_test_results(
        self,
        site_id: str,
        test_id: str
    ) -> Dict[str, Any]:
        """Get A/B test results"""
        return {
            "test_id": test_id,
            "status": "running",
            "variants": [
                {
                    "name": "Control",
                    "visitors": 1234,
                    "conversions": 123,
                    "conversion_rate": 10.0
                },
                {
                    "name": "Variant A",
                    "visitors": 1256,
                    "conversions": 145,
                    "conversion_rate": 11.5
                }
            ],
            "confidence": 95.2,
            "winner": "Variant A"
        }
    
    def get_heatmap_data(
        self,
        site_id: str,
        page_url: str
    ) -> Dict[str, Any]:
        """Get heatmap data for a page"""
        return {
            "page_url": page_url,
            "click_map": [
                {"x": 234, "y": 456, "clicks": 123},
                {"x": 567, "y": 234, "clicks": 89}
            ],
            "scroll_map": {
                "25%": 92.3,
                "50%": 71.2,
                "75%": 45.6,
                "100%": 23.1
            },
            "attention_map": [
                {"element": "#hero", "attention_time": 4.5},
                {"element": "#cta-button", "attention_time": 2.3}
            ]
        }