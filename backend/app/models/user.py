"""
User Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    """User roles enumeration"""
    ADMIN = "admin"
    USER = "user"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class UserPlan(enum.Enum):
    """User subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255))
    company_name = Column(String(255))
    phone = Column(String(20))
    whatsapp = Column(String(20))
    
    # Brazilian specific fields
    cpf = Column(String(14), unique=True, nullable=True)  # CPF format: 000.000.000-00
    cnpj = Column(String(18), unique=True, nullable=True)  # CNPJ format: 00.000.000/0000-00
    
    # Address
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2))  # Brazilian state code (SP, RJ, etc.)
    zip_code = Column(String(9))  # CEP format: 00000-000
    
    # Account settings
    role = Column(Enum(UserRole), default=UserRole.USER)
    plan = Column(Enum(UserPlan), default=UserPlan.FREE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_brazilian = Column(Boolean, default=True)
    
    # Credits and limits
    ai_credits = Column(Integer, default=10)  # Free credits on signup
    monthly_sites_limit = Column(Integer, default=3)
    sites_created_this_month = Column(Integer, default=0)
    total_sites_created = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0.0)
    storage_limit_mb = Column(Float, default=500.0)  # 500MB for free plan
    
    # Preferences
    preferred_language = Column(String(5), default="pt-BR")
    timezone = Column(String(50), default="America/Sao_Paulo")
    preferred_industries = Column(JSON, default=list)  # List of preferred industries
    notification_settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    email_verified_at = Column(DateTime(timezone=True))
    
    # Subscription details
    subscription_status = Column(String(50))  # active, cancelled, past_due, etc.
    subscription_started_at = Column(DateTime(timezone=True))
    subscription_ends_at = Column(DateTime(timezone=True))
    payment_method = Column(String(50))  # credit_card, pix, boleto
    
    # Security
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # API access
    api_key = Column(String(255), unique=True)
    api_key_created_at = Column(DateTime(timezone=True))
    api_requests_count = Column(Integer, default=0)
    api_requests_limit = Column(Integer, default=1000)
    
    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "company_name": self.company_name,
            "role": self.role.value if self.role else None,
            "plan": self.plan.value if self.plan else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "ai_credits": self.ai_credits,
            "sites_created_this_month": self.sites_created_this_month,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "subscription_status": self.subscription_status
        }
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = {
            UserRole.ADMIN: ["all"],
            UserRole.ENTERPRISE: ["unlimited_sites", "api_access", "white_label", "priority_support"],
            UserRole.PREMIUM: ["unlimited_sites", "api_access", "advanced_features"],
            UserRole.USER: ["basic_features", "limited_sites"]
        }
        
        if self.role == UserRole.ADMIN:
            return True
        
        user_permissions = permissions.get(self.role, [])
        return permission in user_permissions
    
    def can_create_site(self) -> bool:
        """Check if user can create a new site"""
        if self.role in [UserRole.ADMIN, UserRole.ENTERPRISE]:
            return True
        
        if self.plan == UserPlan.FREE:
            return self.sites_created_this_month < 3
        elif self.plan == UserPlan.STARTER:
            return self.sites_created_this_month < 10
        elif self.plan in [UserPlan.PROFESSIONAL, UserPlan.ENTERPRISE]:
            return True
        
        return False
    
    def has_ai_credits(self, required: int = 1) -> bool:
        """Check if user has enough AI credits"""
        if self.role == UserRole.ADMIN:
            return True
        
        if self.plan in [UserPlan.PROFESSIONAL, UserPlan.ENTERPRISE]:
            return True
        
        return self.ai_credits >= required
    
    def deduct_ai_credits(self, amount: int = 1):
        """Deduct AI credits from user account"""
        if self.role != UserRole.ADMIN and self.plan not in [UserPlan.PROFESSIONAL, UserPlan.ENTERPRISE]:
            self.ai_credits = max(0, self.ai_credits - amount)
    
    def reset_monthly_limits(self):
        """Reset monthly limits (should be called by a cron job)"""
        self.sites_created_this_month = 0
        
        # Add bonus credits based on plan
        if self.plan == UserPlan.FREE:
            self.ai_credits = min(10, self.ai_credits + 3)  # Add 3 credits, max 10
        elif self.plan == UserPlan.STARTER:
            self.ai_credits = min(50, self.ai_credits + 10)  # Add 10 credits, max 50
        elif self.plan == UserPlan.PROFESSIONAL:
            self.ai_credits = 500  # Reset to 500 credits
        elif self.plan == UserPlan.ENTERPRISE:
            self.ai_credits = 9999  # Unlimited