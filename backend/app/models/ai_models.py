"""
AI-related models for WordPress AI SaaS
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ContentGenerationRequest(BaseModel):
    content_type: str
    topic: str
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    keywords: Optional[List[str]] = None
    length: Optional[str] = None
    custom_instructions: Optional[str] = None

class SiteGenerationRequest(BaseModel):
    business_name: str
    industry: str
    business_type: str
    business_description: str
    target_audience: Optional[str] = None
    location: Optional[str] = None
    services: Optional[List[str]] = None
    unique_selling_points: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

class AIResponse(BaseModel):
    success: bool
    content: Optional[Any] = None
    message: str
    credits_used: int
    model_used: Optional[str] = None

class AICreditsBalance(BaseModel):
    user_id: str
    credits_available: int
    credits_used: int
    credits_total: int
    reset_date: datetime