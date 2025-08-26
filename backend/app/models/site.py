"""
Site Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .user import Base
import enum

class SiteStatus(enum.Enum):
    """Site status enumeration"""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    DEPLOYED = "deployed"
    SUSPENDED = "suspended"

class Site(Base):
    """Site model"""
    __tablename__ = "sites"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Business information
    business_name = Column(String(255), nullable=False)
    business_description = Column(Text)
    industry = Column(String(50), nullable=False)
    business_type = Column(String(50))
    
    # Contact information
    phone = Column(String(20))
    whatsapp = Column(String(20))
    email = Column(String(255))
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2))
    zip_code = Column(String(9))
    
    # Brazilian features
    accept_pix = Column(Boolean, default=True)
    pix_key = Column(String(255))
    cnpj = Column(String(18))
    
    # Template and customization
    template_id = Column(String(100))
    template_name = Column(String(255))
    color_scheme = Column(JSON)  # Primary, secondary, accent colors
    typography = Column(JSON)  # Font choices
    
    # Generation details
    status = Column(Enum(SiteStatus), default=SiteStatus.DRAFT)
    generation_time = Column(Float)  # Time in seconds
    ai_credits_used = Column(Integer, default=0)
    variations_count = Column(Integer, default=0)
    selected_variation = Column(Integer)
    
    # URLs and deployment
    preview_url = Column(String(500))
    wordpress_url = Column(String(500))
    domain = Column(String(255))
    deployment_method = Column(String(50))  # docker, ftp, ssh, etc.
    deployment_path = Column(String(500))
    
    # Content and features
    pages = Column(JSON)  # List of pages
    features = Column(JSON)  # List of enabled features
    plugins = Column(JSON)  # List of WordPress plugins
    keywords = Column(JSON)  # SEO keywords
    
    # SEO data
    seo_title = Column(String(255))
    seo_description = Column(Text)
    seo_keywords = Column(JSON)
    
    # Performance metrics
    lighthouse_score = Column(Integer)
    page_speed_score = Column(Integer)
    seo_score = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deployed_at = Column(DateTime(timezone=True))
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Statistics
    visits_count = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    conversions_count = Column(Integer, default=0)
    
    # Export data
    export_formats = Column(JSON)  # Available export formats
    last_exported_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Site {self.business_name} ({self.site_id})>"
    
    def to_dict(self):
        """Convert site to dictionary"""
        return {
            "id": self.id,
            "site_id": self.site_id,
            "user_id": self.user_id,
            "business_name": self.business_name,
            "industry": self.industry,
            "status": self.status.value if self.status else None,
            "template_name": self.template_name,
            "generation_time": self.generation_time,
            "variations_count": self.variations_count,
            "preview_url": self.preview_url,
            "wordpress_url": self.wordpress_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ai_credits_used": self.ai_credits_used
        }

class SiteGeneration(Base):
    """Site generation history model"""
    __tablename__ = "site_generations"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Generation request
    request_data = Column(JSON)  # Original request data
    personalization_id = Column(String(100), unique=True)
    
    # Template and variations
    template_id = Column(String(100))
    variations = Column(JSON)  # Generated variations data
    selected_variation = Column(Integer)
    
    # Performance
    generation_start = Column(DateTime(timezone=True))
    generation_end = Column(DateTime(timezone=True))
    total_time = Column(Float)
    
    # Steps timing
    template_selection_time = Column(Float)
    personalization_time = Column(Float)
    variation_generation_time = Column(Float)
    image_fetching_time = Column(Float)
    deployment_time = Column(Float)
    
    # Resources used
    ai_model = Column(String(50))
    ai_tokens_used = Column(Integer)
    ai_credits_used = Column(Integer)
    images_fetched = Column(Integer)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Output
    output_data = Column(JSON)  # Generated content
    export_data = Column(JSON)  # Export package info
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SiteGeneration {self.personalization_id}>"