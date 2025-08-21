"""
Configuration settings for WordPress AI SaaS Backend
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "WordPress AI SaaS"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Providers (Multi-provider as per PRD)
    # Primary: Claude 3.5 Sonnet
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Secondary: GPT-4o
    OPENAI_API_KEY: Optional[str] = None
    
    # Tertiary: Gemini 2.0
    GOOGLE_AI_API_KEY: Optional[str] = None
    
    # Agno Framework Configuration
    AGNO_API_KEY: Optional[str] = None
    AGNO_MODEL_PROVIDER: str = "anthropic"  # Primary provider
    AGNO_MODEL_ID: str = "claude-sonnet-4-20250514"
    
    # AI Credits System (PRD section 6.2)
    AI_CREDITS_ENABLED: bool = True
    AI_CREDITS_REDIS_KEY_PREFIX: str = "ai_credits:"
    
    # Content Generation
    DEFAULT_MAX_TOKENS: int = 4000
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # WordPress Integration
    WP_CLI_PATH: str = "/usr/local/bin/wp"
    WP_SITES_BASE_PATH: str = "/var/www/sites"
    
    # Asaas Payment Gateway (Feature F003)
    ASAAS_API_KEY: Optional[str] = None
    ASAAS_SANDBOX: bool = True  # Use sandbox for development
    ASAAS_WEBHOOK_TOKEN: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Feature Flags (aligned with PRD phases)
    FEATURE_CONTENT_GENERATION: bool = True  # F007
    FEATURE_SITE_CLONING: bool = True        # F006 - Phase 3
    FEATURE_LANDING_PAGES: bool = True       # F005 - Phase 2
    FEATURE_WHITE_LABEL: bool = True         # F009 - Phase 4
    
    # Landing Page Engine Configuration
    LANDING_PAGE_ENGINE: str = "boltdiy"     # "mock" or "boltdiy"
    BOLTDIY_URL: str = "http://localhost:5173"
    BOLTDIY_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# AI Credits costs per action (PRD section 6.2)
AI_CREDITS_COSTS = {
    "generate_site": 100,
    "create_landing_page": 50,
    "clone_site": 150,
    "generate_blog_post": 20,
    "generate_image": 5,
    "redesign_page": 30,
    "seo_optimization": 10,
}

# Plan limits (PRD section 6.1)
PLAN_LIMITS = {
    "starter": {
        "ai_credits_monthly": 1000,
        "sites_wordpress": 1,
        "landing_pages": 3,
        "blog_posts_monthly": 4,
        "cloning_monthly": 0,
        "storage_gb": 10,
        "bandwidth_gb": 100,
        "users": 1,
    },
    "professional": {
        "ai_credits_monthly": 5000,
        "sites_wordpress": 5,
        "landing_pages": 15,
        "blog_posts_monthly": 20,
        "cloning_monthly": 2,
        "storage_gb": 50,
        "bandwidth_gb": 500,
        "users": 3,
    },
    "business": {
        "ai_credits_monthly": 15000,
        "sites_wordpress": 15,
        "landing_pages": 50,
        "blog_posts_monthly": 60,
        "cloning_monthly": 10,
        "storage_gb": 200,
        "bandwidth_gb": 2000,
        "users": 10,
    },
    "agency": {
        "ai_credits_monthly": 50000,
        "sites_wordpress": -1,  # Unlimited
        "landing_pages": -1,    # Unlimited
        "blog_posts_monthly": 200,
        "cloning_monthly": -1,  # Unlimited
        "storage_gb": 1000,
        "bandwidth_gb": -1,     # Unlimited
        "users": -1,            # Unlimited
        "white_label": True,
        "api_access": "complete",
    }
}