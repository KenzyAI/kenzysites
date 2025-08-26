"""
Payment and Subscription Models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .user import Base

class PaymentStatus(enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class PaymentMethod(enum.Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BOLETO = "boleto"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    PAGSEGURO = "pagseguro"
    MERCADOPAGO = "mercadopago"

class SubscriptionStatus(enum.Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"

class PlanType(enum.Enum):
    """Plan type enumeration"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="BRL")
    description = Column(String(500))
    
    # Payment method
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_method_details = Column(JSON)  # Card last 4, PIX key, etc.
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    status_reason = Column(String(255))
    
    # Gateway information
    gateway = Column(String(50))  # stripe, pagseguro, mercadopago
    gateway_payment_id = Column(String(255))  # External payment ID
    gateway_response = Column(JSON)  # Full gateway response
    
    # Brazilian specific
    nfe_number = Column(String(50))  # Nota Fiscal number
    cpf_cnpj = Column(String(18))  # Customer tax ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))
    
    # Refund information
    refund_amount = Column(Float, default=0.0)
    refund_reason = Column(String(255))
    
    # Metadata
    metadata = Column(JSON)
    
    def __repr__(self):
        return f"<Payment {self.payment_id} - {self.amount} {self.currency}>"
    
    def to_dict(self):
        """Convert payment to dictionary"""
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status.value if self.status else None,
            "payment_method": self.payment_method.value if self.payment_method else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None
        }

class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Plan information
    plan_type = Column(Enum(PlanType), nullable=False)
    plan_name = Column(String(100))
    
    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="BRL")
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    
    # Status
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    cancel_reason = Column(String(255))
    
    # Gateway information
    gateway = Column(String(50))  # stripe, pagseguro, mercadopago
    gateway_subscription_id = Column(String(255))
    gateway_customer_id = Column(String(255))
    
    # Dates
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    # Usage limits
    sites_limit = Column(Integer, default=3)
    ai_credits_limit = Column(Integer, default=10)
    storage_limit_gb = Column(Float, default=0.5)
    
    # Usage tracking
    sites_used = Column(Integer, default=0)
    ai_credits_used = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0.0)
    
    # Payment method
    default_payment_method = Column(String(100))
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Subscription {self.subscription_id} - {self.plan_type.value}>"
    
    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            "id": self.id,
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "plan_type": self.plan_type.value if self.plan_type else None,
            "price": self.price,
            "status": self.status.value if self.status else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "sites_limit": self.sites_limit,
            "sites_used": self.sites_used,
            "ai_credits_limit": self.ai_credits_limit,
            "ai_credits_used": self.ai_credits_used
        }
    
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    def can_create_site(self) -> bool:
        """Check if user can create more sites"""
        if self.plan_type == PlanType.ENTERPRISE:
            return True
        return self.sites_used < self.sites_limit
    
    def has_ai_credits(self, required: int = 1) -> bool:
        """Check if subscription has enough AI credits"""
        if self.plan_type == PlanType.ENTERPRISE:
            return True
        return self.ai_credits_used + required <= self.ai_credits_limit

class Plan(Base):
    """Plan configuration model"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Plan details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(PlanType), nullable=False)
    
    # Pricing
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=False)
    currency = Column(String(3), default="BRL")
    
    # Limits
    sites_limit = Column(Integer, default=3)
    ai_credits_monthly = Column(Integer, default=10)
    storage_gb = Column(Float, default=0.5)
    team_members = Column(Integer, default=1)
    
    # Features
    features = Column(JSON)  # List of feature strings
    
    # Gateway IDs
    stripe_price_id_monthly = Column(String(100))
    stripe_price_id_yearly = Column(String(100))
    pagseguro_plan_id = Column(String(100))
    mercadopago_plan_id = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Display
    display_order = Column(Integer, default=0)
    badge_text = Column(String(50))  # "Most Popular", "Best Value"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Plan {self.name} ({self.type.value})>"
    
    def to_dict(self):
        """Convert plan to dictionary"""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value if self.type else None,
            "price_monthly": self.price_monthly,
            "price_yearly": self.price_yearly,
            "currency": self.currency,
            "sites_limit": self.sites_limit,
            "ai_credits_monthly": self.ai_credits_monthly,
            "storage_gb": self.storage_gb,
            "features": self.features,
            "is_featured": self.is_featured,
            "badge_text": self.badge_text
        }

class Invoice(Base):
    """Invoice model"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    payment_id = Column(Integer, ForeignKey("payments.id"))
    
    # Invoice details
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    currency = Column(String(3), default="BRL")
    
    # Status
    status = Column(String(20), default="pending")  # pending, paid, void, uncollectible
    
    # Billing information
    billing_name = Column(String(255))
    billing_email = Column(String(255))
    billing_cpf_cnpj = Column(String(18))
    billing_address = Column(JSON)
    
    # Dates
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    paid_date = Column(DateTime(timezone=True))
    
    # PDF
    pdf_url = Column(String(500))
    
    # Line items
    line_items = Column(JSON)  # Array of items
    
    # Metadata
    metadata = Column(JSON)
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.total} {self.currency}>"

class PaymentMethod(Base):
    """Saved payment methods"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Method details
    type = Column(String(50), nullable=False)  # card, pix, bank_account
    is_default = Column(Boolean, default=False)
    
    # Card details (encrypted)
    card_brand = Column(String(20))  # visa, mastercard, etc.
    card_last4 = Column(String(4))
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)
    card_holder_name = Column(String(255))
    
    # PIX details
    pix_key = Column(String(255))
    pix_key_type = Column(String(20))  # cpf, cnpj, email, phone, random
    
    # Bank account
    bank_name = Column(String(100))
    bank_agency = Column(String(10))
    bank_account = Column(String(20))
    
    # Gateway tokens
    stripe_payment_method_id = Column(String(255))
    pagseguro_token = Column(String(255))
    mercadopago_token = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<PaymentMethod {self.type} - User {self.user_id}>"

class Coupon(Base):
    """Discount coupons"""
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Discount
    discount_type = Column(String(20), nullable=False)  # percentage, fixed
    discount_value = Column(Float, nullable=False)
    currency = Column(String(3), default="BRL")
    
    # Applicability
    applies_to = Column(JSON)  # List of plan IDs
    minimum_amount = Column(Float, default=0.0)
    
    # Usage limits
    max_uses = Column(Integer)
    max_uses_per_user = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    
    # Validity
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Coupon {self.code} - {self.discount_value}>"
    
    def is_valid(self) -> bool:
        """Check if coupon is valid"""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        
        return True