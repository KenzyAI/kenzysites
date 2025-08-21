"""
Billing Models and Schemas for Asaas Integration
Aligned with PRD Feature F003 and F004
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class PaymentMethodEnum(str, Enum):
    PIX = "PIX"
    BOLETO = "BOLETO"
    CREDIT_CARD = "CREDIT_CARD"

class PlanType(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    AGENCY = "agency"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    RECEIVED = "RECEIVED"
    OVERDUE = "OVERDUE"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

class SubscriptionStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

# Request Models
class CreateCustomerRequest(BaseModel):
    """Request to create a new customer"""
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email")
    cpf_cnpj: str = Field(..., description="CPF or CNPJ (Brazilian tax ID)")
    phone: Optional[str] = Field(None, description="Phone number")
    mobile_phone: Optional[str] = Field(None, description="Mobile phone")
    postal_code: Optional[str] = Field(None, description="CEP (Brazilian postal code)")
    address: Optional[str] = Field(None, description="Street address")
    address_number: Optional[str] = Field(None, description="Address number")
    complement: Optional[str] = Field(None, description="Address complement")
    neighborhood: Optional[str] = Field(None, description="Neighborhood/District")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State (2 letters)")
    
    @validator('cpf_cnpj')
    def validate_cpf_cnpj(cls, v):
        # Remove non-digits
        cleaned = ''.join(filter(str.isdigit, v))
        # Check if it's CPF (11 digits) or CNPJ (14 digits)
        if len(cleaned) not in [11, 14]:
            raise ValueError('CPF must have 11 digits or CNPJ must have 14 digits')
        return cleaned

class CreateSubscriptionRequest(BaseModel):
    """Request to create a subscription"""
    customer_id: Optional[str] = Field(None, description="Asaas customer ID")
    plan_name: PlanType = Field(..., description="Plan name (starter, professional, business, agency)")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method")
    coupon_code: Optional[str] = Field(None, description="Discount coupon code")
    billing_cycle: Optional[str] = Field("MONTHLY", description="Billing cycle (MONTHLY, QUARTERLY, YEARLY)")

class UpdateSubscriptionRequest(BaseModel):
    """Request to update subscription (upgrade/downgrade)"""
    new_plan: Optional[PlanType] = Field(None, description="New plan to switch to")
    new_payment_method: Optional[PaymentMethodEnum] = Field(None, description="New payment method")
    apply_immediately: bool = Field(True, description="Apply changes immediately or at next cycle")

class CreatePaymentRequest(BaseModel):
    """Request to create a payment"""
    customer_id: Optional[str] = Field(None, description="Asaas customer ID")
    amount: float = Field(..., gt=0, description="Payment amount in BRL")
    payment_method: PaymentMethodEnum = Field(..., description="Payment method")
    description: Optional[str] = Field(None, description="Payment description")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    installments: Optional[int] = Field(None, ge=1, le=12, description="Number of installments (credit card only)")
    
    @validator('installments')
    def validate_installments(cls, v, values):
        if v and values.get('payment_method') != PaymentMethodEnum.CREDIT_CARD:
            raise ValueError('Installments only available for credit card payments')
        return v

class ApplyCouponRequest(BaseModel):
    """Request to apply a discount coupon"""
    coupon_code: str = Field(..., description="Discount coupon code")
    subscription_id: Optional[str] = Field(None, description="Apply to specific subscription")

class WebhookPayload(BaseModel):
    """Asaas webhook payload"""
    event: str = Field(..., description="Event type")
    payment: Optional[Dict[str, Any]] = Field(None, description="Payment data")
    subscription: Optional[Dict[str, Any]] = Field(None, description="Subscription data")
    customer: Optional[Dict[str, Any]] = Field(None, description="Customer data")

# Response Models
class CustomerResponse(BaseModel):
    """Customer information response"""
    id: str
    name: str
    email: str
    cpf_cnpj: str
    phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    created_at: str
    external_reference: Optional[str] = None

class SubscriptionResponse(BaseModel):
    """Subscription information response"""
    id: str
    customer_id: str
    plan: PlanType
    price: float
    billing_cycle: str
    payment_method: PaymentMethodEnum
    status: SubscriptionStatusEnum
    next_due_date: str
    created_at: str
    updated_at: Optional[str] = None
    cancelled_at: Optional[str] = None

class PaymentResponse(BaseModel):
    """Payment information response"""
    id: str
    customer_id: str
    amount: float
    payment_method: PaymentMethodEnum
    status: PaymentStatus
    due_date: str
    paid_at: Optional[str] = None
    description: Optional[str] = None
    
    # PIX specific
    pix_qr_code: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    pix_expiration: Optional[str] = None
    
    # Boleto specific
    boleto_url: Optional[str] = None
    boleto_barcode: Optional[str] = None
    
    # Credit card specific
    installments: Optional[int] = None
    installment_value: Optional[float] = None

class InvoiceResponse(BaseModel):
    """Invoice information"""
    id: str
    date: str
    amount: float
    status: str
    description: str
    pdf_url: Optional[str] = None
    payment_id: Optional[str] = None

class BillingDashboard(BaseModel):
    """Comprehensive billing dashboard"""
    # Current plan info
    current_plan: PlanType
    plan_price: float
    billing_cycle: str
    next_billing_date: str
    payment_method: str
    payment_status: str
    
    # Usage metrics
    current_usage: Dict[str, Any] = Field(default_factory=dict)
    
    # Payment history
    recent_payments: List[Dict[str, Any]] = Field(default_factory=list)
    upcoming_charges: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Available actions
    available_upgrades: List[Dict[str, Any]] = Field(default_factory=list)
    can_downgrade: bool = True
    can_cancel: bool = True

class PaymentMethodInfo(BaseModel):
    """Payment method information"""
    method: PaymentMethodEnum
    enabled: bool
    icon: str
    description: str
    processing_time: str
    installments_available: bool = False
    max_installments: Optional[int] = None

class CouponInfo(BaseModel):
    """Coupon information"""
    code: str
    discount_type: str  # PERCENTAGE or FIXED
    discount_value: float
    valid_until: Optional[str] = None
    usage_limit: Optional[int] = None
    usage_count: int = 0
    is_valid: bool = True

class RevenueReport(BaseModel):
    """Revenue report data"""
    period: str
    total_revenue: float
    total_transactions: int
    average_ticket: float
    currency: str = "BRL"
    
    # Breakdown by payment method
    revenue_by_method: Dict[str, float] = Field(default_factory=dict)
    
    # Breakdown by plan
    revenue_by_plan: Dict[str, float] = Field(default_factory=dict)
    
    # Growth metrics
    growth_rate: Optional[float] = None
    mrr: Optional[float] = None  # Monthly Recurring Revenue
    arr: Optional[float] = None  # Annual Recurring Revenue

class ChurnMetrics(BaseModel):
    """Churn and retention metrics"""
    monthly_churn_rate: float
    annual_churn_rate: float
    average_customer_lifetime_months: float
    ltv: float  # Lifetime Value in BRL
    retention_rate: float
    
    # Cohort analysis
    cohort_retention: Optional[Dict[str, float]] = None
    
    # Churn reasons
    churn_reasons: Optional[Dict[str, int]] = None

class DunningStatus(BaseModel):
    """Dunning process status for Feature F004"""
    customer_id: str
    payment_id: str
    days_overdue: int
    current_stage: str  # "reminder_3d", "suspended_7d", "final_warning_15d", "scheduled_deletion_30d"
    actions_taken: List[str] = Field(default_factory=list)
    next_action: Optional[str] = None
    next_action_date: Optional[str] = None
    can_recover: bool = True

class SuspensionInfo(BaseModel):
    """Site suspension information"""
    customer_id: str
    sites_affected: List[str] = Field(default_factory=list)
    suspension_reason: str
    suspended_at: str
    will_be_deleted_at: Optional[str] = None
    payment_required: float
    payment_url: str

class PlanLimitsInfo(BaseModel):
    """Plan limits and usage information"""
    plan: PlanType
    
    # Limits (from PRD)
    sites_wordpress_limit: int  # -1 for unlimited
    landing_pages_limit: int
    ai_credits_monthly_limit: int
    blog_posts_monthly_limit: int
    cloning_monthly_limit: int
    storage_gb_limit: int
    bandwidth_gb_limit: int
    users_limit: int
    
    # Current usage
    sites_wordpress_used: int = 0
    landing_pages_used: int = 0
    ai_credits_used: int = 0
    blog_posts_used: int = 0
    cloning_used: int = 0
    storage_gb_used: float = 0
    bandwidth_gb_used: float = 0
    users_used: int = 0
    
    # Features
    white_label_enabled: bool = False
    api_access_level: Optional[str] = None  # None, "basic", "complete"
    
    @property
    def sites_remaining(self) -> int:
        if self.sites_wordpress_limit == -1:
            return -1  # Unlimited
        return max(0, self.sites_wordpress_limit - self.sites_wordpress_used)
    
    @property
    def ai_credits_remaining(self) -> int:
        return max(0, self.ai_credits_monthly_limit - self.ai_credits_used)
    
    @property
    def storage_percentage_used(self) -> float:
        if self.storage_gb_limit == 0:
            return 0
        return (self.storage_gb_used / self.storage_gb_limit) * 100

class UpgradeRecommendation(BaseModel):
    """Plan upgrade recommendation"""
    current_plan: PlanType
    recommended_plan: PlanType
    reason: str
    potential_savings: Optional[float] = None
    additional_features: List[str] = Field(default_factory=list)
    upgrade_incentive: Optional[str] = None  # Special offer or discount

# Error Models
class BillingError(BaseModel):
    """Billing error response"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    recovery_action: Optional[str] = None
    support_ticket_id: Optional[str] = None