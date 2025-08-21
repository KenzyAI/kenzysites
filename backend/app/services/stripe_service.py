"""
Stripe International Payment Service
Phase 3: Launch Oficial - International payments
Supports multiple currencies and payment methods
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import json
from decimal import Decimal

logger = logging.getLogger(__name__)

# Enums
class Currency(str, Enum):
    BRL = "brl"  # Brazilian Real
    USD = "usd"  # US Dollar
    EUR = "eur"  # Euro
    GBP = "gbp"  # British Pound
    CAD = "cad"  # Canadian Dollar
    AUD = "aud"  # Australian Dollar
    MXN = "mxn"  # Mexican Peso
    ARS = "ars"  # Argentine Peso

class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    PAYPAL = "paypal"
    SEPA = "sepa_debit"
    ACH = "ach_debit"
    BOLETO = "boleto"  # Brazil
    PIX = "pix"  # Brazil

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"

class PlanTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    AGENCY = "agency"

# Models
class PricingPlan(BaseModel):
    """International pricing plan"""
    id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    tier: PlanTier
    name: str
    description: str
    
    # Multi-currency pricing
    prices: Dict[Currency, float] = Field(default_factory=dict)
    
    # Features based on PRD
    features: Dict[str, Any] = Field(default_factory=dict)
    
    # Billing
    interval: str = "month"  # month or year
    trial_days: int = 7
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    active: bool = True

class Customer(BaseModel):
    """Stripe customer"""
    id: str = Field(default_factory=lambda: f"cus_{uuid.uuid4().hex[:16]}")
    email: str
    name: Optional[str] = None
    
    # Location
    country: str = "BR"
    currency: Currency = Currency.BRL
    locale: str = "pt-BR"
    
    # Payment
    default_payment_method: Optional[str] = None
    payment_methods: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Subscription
    subscription_id: Optional[str] = None
    plan_tier: Optional[PlanTier] = None
    
    # Billing
    balance: float = 0.0
    tax_exempt: bool = False
    tax_id: Optional[str] = None  # CPF/CNPJ for Brazil, VAT for EU
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Subscription(BaseModel):
    """Stripe subscription"""
    id: str = Field(default_factory=lambda: f"sub_{uuid.uuid4().hex[:16]}")
    customer_id: str
    plan_id: str
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    
    # Billing
    currency: Currency
    amount: float
    interval: str = "month"
    
    # Dates
    current_period_start: datetime = Field(default_factory=datetime.now)
    current_period_end: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=30))
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    
    # Payment
    default_payment_method: Optional[str] = None
    latest_invoice_id: Optional[str] = None
    
    # Usage
    usage: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Invoice(BaseModel):
    """Stripe invoice"""
    id: str = Field(default_factory=lambda: f"inv_{uuid.uuid4().hex[:16]}")
    customer_id: str
    subscription_id: Optional[str] = None
    
    # Amount
    currency: Currency
    subtotal: float
    tax: float = 0.0
    total: float
    amount_paid: float = 0.0
    amount_due: float
    
    # Status
    status: str = "open"  # draft, open, paid, void, uncollectible
    paid: bool = False
    attempted: bool = False
    
    # Dates
    created_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # Items
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Payment
    payment_intent_id: Optional[str] = None
    charge_id: Optional[str] = None
    
    # URLs
    hosted_invoice_url: Optional[str] = None
    invoice_pdf: Optional[str] = None

class PaymentIntent(BaseModel):
    """Stripe payment intent"""
    id: str = Field(default_factory=lambda: f"pi_{uuid.uuid4().hex[:16]}")
    customer_id: Optional[str] = None
    
    # Amount
    amount: float
    currency: Currency
    
    # Status
    status: str = "requires_payment_method"  # requires_payment_method, requires_confirmation, succeeded, canceled
    
    # Payment
    payment_method: Optional[str] = None
    payment_method_types: List[PaymentMethod] = Field(default_factory=list)
    
    # Metadata
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class StripeService:
    """Stripe international payment service"""
    
    def __init__(self):
        self.plans: Dict[str, PricingPlan] = {}
        self.customers: Dict[str, Customer] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.payment_intents: Dict[str, PaymentIntent] = {}
        
        # Initialize pricing plans
        self._initialize_plans()
    
    def _initialize_plans(self):
        """Initialize international pricing plans based on PRD"""
        
        # Define multi-currency prices
        starter_prices = {
            Currency.BRL: 97.00,
            Currency.USD: 19.00,
            Currency.EUR: 17.00,
            Currency.GBP: 15.00,
            Currency.CAD: 25.00,
            Currency.AUD: 28.00,
            Currency.MXN: 350.00,
            Currency.ARS: 7500.00
        }
        
        professional_prices = {
            Currency.BRL: 297.00,
            Currency.USD: 59.00,
            Currency.EUR: 53.00,
            Currency.GBP: 47.00,
            Currency.CAD: 75.00,
            Currency.AUD: 85.00,
            Currency.MXN: 1100.00,
            Currency.ARS: 23000.00
        }
        
        business_prices = {
            Currency.BRL: 597.00,
            Currency.USD: 119.00,
            Currency.EUR: 107.00,
            Currency.GBP: 95.00,
            Currency.CAD: 155.00,
            Currency.AUD: 175.00,
            Currency.MXN: 2200.00,
            Currency.ARS: 46000.00
        }
        
        agency_prices = {
            Currency.BRL: 1997.00,
            Currency.USD: 399.00,
            Currency.EUR: 359.00,
            Currency.GBP: 319.00,
            Currency.CAD: 519.00,
            Currency.AUD: 579.00,
            Currency.MXN: 7400.00,
            Currency.ARS: 154000.00
        }
        
        # Create plans
        plans_config = [
            {
                "tier": PlanTier.STARTER,
                "name": "Starter",
                "description": "Perfect for small businesses",
                "prices": starter_prices,
                "features": {
                    "sites_wordpress": 1,
                    "landing_pages": 3,
                    "ai_credits_monthly": 1000,
                    "blog_posts_monthly": 4,
                    "storage_gb": 10,
                    "bandwidth_gb": 100
                }
            },
            {
                "tier": PlanTier.PROFESSIONAL,
                "name": "Professional",
                "description": "For growing businesses",
                "prices": professional_prices,
                "features": {
                    "sites_wordpress": 5,
                    "landing_pages": 15,
                    "ai_credits_monthly": 5000,
                    "blog_posts_monthly": 20,
                    "clones_monthly": 2,
                    "storage_gb": 50,
                    "bandwidth_gb": 500
                }
            },
            {
                "tier": PlanTier.BUSINESS,
                "name": "Business",
                "description": "For established companies",
                "prices": business_prices,
                "features": {
                    "sites_wordpress": 15,
                    "landing_pages": 50,
                    "ai_credits_monthly": 15000,
                    "blog_posts_monthly": 60,
                    "clones_monthly": 10,
                    "storage_gb": 200,
                    "bandwidth_gb": 2000
                }
            },
            {
                "tier": PlanTier.AGENCY,
                "name": "Agency",
                "description": "For agencies and enterprises",
                "prices": agency_prices,
                "features": {
                    "sites_wordpress": -1,  # Unlimited
                    "landing_pages": -1,
                    "ai_credits_monthly": 50000,
                    "blog_posts_monthly": 200,
                    "clones_monthly": -1,
                    "storage_gb": 1000,
                    "bandwidth_gb": -1,
                    "white_label": True,
                    "api_access": True
                }
            }
        ]
        
        for config in plans_config:
            plan = PricingPlan(**config)
            self.plans[plan.id] = plan
            self.plans[config["tier"].value] = plan  # Also store by tier name
    
    # Customer Management
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        country: str = "BR",
        currency: Optional[Currency] = None,
        tax_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Create a Stripe customer"""
        
        # Auto-detect currency based on country
        if not currency:
            currency = self._get_default_currency(country)
        
        customer = Customer(
            email=email,
            name=name,
            country=country,
            currency=currency,
            tax_id=tax_id,
            metadata=metadata or {}
        )
        
        self.customers[customer.id] = customer
        
        logger.info(f"Created Stripe customer {customer.id} from {country}")
        return customer
    
    def _get_default_currency(self, country: str) -> Currency:
        """Get default currency for country"""
        currency_map = {
            "BR": Currency.BRL,
            "US": Currency.USD,
            "GB": Currency.GBP,
            "CA": Currency.CAD,
            "AU": Currency.AUD,
            "MX": Currency.MXN,
            "AR": Currency.ARS,
            # EU countries
            "DE": Currency.EUR,
            "FR": Currency.EUR,
            "ES": Currency.EUR,
            "IT": Currency.EUR,
            "PT": Currency.EUR,
            "NL": Currency.EUR,
            "BE": Currency.EUR,
            "AT": Currency.EUR,
            "IE": Currency.EUR
        }
        return currency_map.get(country, Currency.USD)
    
    # Subscription Management
    async def create_subscription(
        self,
        customer_id: str,
        plan_tier: PlanTier,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None
    ) -> Subscription:
        """Create a subscription"""
        
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        plan = self.plans.get(plan_tier.value)
        if not plan:
            raise ValueError(f"Plan {plan_tier} not found")
        
        # Get price in customer's currency
        price = plan.prices.get(customer.currency, plan.prices[Currency.USD])
        
        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan.id,
            currency=customer.currency,
            amount=price,
            interval=plan.interval,
            default_payment_method=payment_method_id
        )
        
        # Set trial period
        if trial_days or plan.trial_days:
            subscription.trial_end = datetime.now() + timedelta(days=trial_days or plan.trial_days)
            subscription.status = SubscriptionStatus.TRIALING
        
        # Update customer
        customer.subscription_id = subscription.id
        customer.plan_tier = plan_tier
        
        self.subscriptions[subscription.id] = subscription
        
        # Create initial invoice
        await self.create_invoice(customer_id, subscription.id, price)
        
        logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
        return subscription
    
    async def update_subscription(
        self,
        subscription_id: str,
        new_plan_tier: Optional[PlanTier] = None,
        payment_method_id: Optional[str] = None
    ) -> Subscription:
        """Update subscription (upgrade/downgrade)"""
        
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        customer = self.customers.get(subscription.customer_id)
        
        if new_plan_tier:
            # Change plan
            new_plan = self.plans.get(new_plan_tier.value)
            new_price = new_plan.prices.get(customer.currency, new_plan.prices[Currency.USD])
            
            # Calculate proration
            proration = self._calculate_proration(subscription, new_price)
            
            # Update subscription
            subscription.plan_id = new_plan.id
            subscription.amount = new_price
            customer.plan_tier = new_plan_tier
            
            # Create proration invoice if needed
            if proration != 0:
                await self.create_invoice(
                    customer.id,
                    subscription.id,
                    abs(proration),
                    description="Plan change proration"
                )
        
        if payment_method_id:
            subscription.default_payment_method = payment_method_id
        
        logger.info(f"Updated subscription {subscription_id}")
        return subscription
    
    def _calculate_proration(self, subscription: Subscription, new_price: float) -> float:
        """Calculate proration for plan change"""
        
        # Calculate remaining days in current period
        now = datetime.now()
        days_remaining = (subscription.current_period_end - now).days
        days_in_period = (subscription.current_period_end - subscription.current_period_start).days
        
        # Calculate unused amount from current plan
        unused_amount = (subscription.amount * days_remaining) / days_in_period
        
        # Calculate new amount for remaining period
        new_amount = (new_price * days_remaining) / days_in_period
        
        # Return difference (positive = customer owes, negative = credit)
        return new_amount - unused_amount
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Subscription:
        """Cancel subscription"""
        
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if immediately:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.now()
        else:
            # Cancel at end of period
            subscription.canceled_at = subscription.current_period_end
        
        logger.info(f"Canceled subscription {subscription_id}")
        return subscription
    
    # Payment Methods
    async def add_payment_method(
        self,
        customer_id: str,
        payment_method_type: PaymentMethod,
        details: Dict[str, Any],
        set_default: bool = True
    ) -> str:
        """Add payment method to customer"""
        
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        payment_method_id = f"pm_{uuid.uuid4().hex[:16]}"
        
        payment_method = {
            "id": payment_method_id,
            "type": payment_method_type,
            "details": details,
            "created_at": datetime.now().isoformat()
        }
        
        customer.payment_methods.append(payment_method)
        
        if set_default:
            customer.default_payment_method = payment_method_id
        
        logger.info(f"Added payment method {payment_method_id} to customer {customer_id}")
        return payment_method_id
    
    # Invoicing
    async def create_invoice(
        self,
        customer_id: str,
        subscription_id: Optional[str] = None,
        amount: Optional[float] = None,
        description: Optional[str] = None
    ) -> Invoice:
        """Create an invoice"""
        
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get amount from subscription if not provided
        if not amount and subscription_id:
            subscription = self.subscriptions.get(subscription_id)
            amount = subscription.amount
        
        # Calculate tax based on country
        tax_rate = self._get_tax_rate(customer.country)
        tax = amount * tax_rate
        total = amount + tax
        
        invoice = Invoice(
            customer_id=customer_id,
            subscription_id=subscription_id,
            currency=customer.currency,
            subtotal=amount,
            tax=tax,
            total=total,
            amount_due=total,
            due_date=datetime.now() + timedelta(days=7)
        )
        
        # Add line items
        invoice.line_items.append({
            "description": description or "Subscription",
            "amount": amount,
            "currency": customer.currency.value
        })
        
        # Generate URLs
        invoice.hosted_invoice_url = f"https://pay.kenzysites.com/invoice/{invoice.id}"
        invoice.invoice_pdf = f"https://pay.kenzysites.com/invoice/{invoice.id}/pdf"
        
        self.invoices[invoice.id] = invoice
        
        logger.info(f"Created invoice {invoice.id} for {total} {customer.currency.value}")
        return invoice
    
    def _get_tax_rate(self, country: str) -> float:
        """Get tax rate for country"""
        
        tax_rates = {
            "BR": 0.17,  # Brazilian taxes
            "US": 0.08,  # Average US sales tax
            "GB": 0.20,  # UK VAT
            "CA": 0.13,  # Canadian GST/HST
            "AU": 0.10,  # Australian GST
            "MX": 0.16,  # Mexican IVA
            "AR": 0.21,  # Argentine IVA
            # EU VAT rates
            "DE": 0.19,
            "FR": 0.20,
            "ES": 0.21,
            "IT": 0.22,
            "PT": 0.23,
            "NL": 0.21,
            "BE": 0.21,
            "AT": 0.20,
            "IE": 0.23
        }
        
        return tax_rates.get(country, 0.0)
    
    async def pay_invoice(
        self,
        invoice_id: str,
        payment_method_id: str
    ) -> Invoice:
        """Pay an invoice"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        # Process payment (mock)
        invoice.status = "paid"
        invoice.paid = True
        invoice.paid_at = datetime.now()
        invoice.amount_paid = invoice.total
        invoice.amount_due = 0
        
        # Create charge record
        invoice.charge_id = f"ch_{uuid.uuid4().hex[:16]}"
        
        logger.info(f"Paid invoice {invoice_id}")
        return invoice
    
    # Payment Intents (for one-time payments)
    async def create_payment_intent(
        self,
        amount: float,
        currency: Currency,
        customer_id: Optional[str] = None,
        payment_methods: Optional[List[PaymentMethod]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentIntent:
        """Create a payment intent for one-time payment"""
        
        payment_intent = PaymentIntent(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            metadata=metadata or {}
        )
        
        # Set allowed payment methods based on currency/country
        if currency == Currency.BRL:
            payment_intent.payment_method_types = [
                PaymentMethod.CARD,
                PaymentMethod.PIX,
                PaymentMethod.BOLETO
            ]
        elif currency == Currency.EUR:
            payment_intent.payment_method_types = [
                PaymentMethod.CARD,
                PaymentMethod.SEPA,
                PaymentMethod.PAYPAL
            ]
        else:
            payment_intent.payment_method_types = [
                PaymentMethod.CARD,
                PaymentMethod.APPLE_PAY,
                PaymentMethod.GOOGLE_PAY,
                PaymentMethod.PAYPAL
            ]
        
        self.payment_intents[payment_intent.id] = payment_intent
        
        logger.info(f"Created payment intent {payment_intent.id} for {amount} {currency.value}")
        return payment_intent
    
    # Webhooks
    async def handle_webhook(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        logger.info(f"Handling webhook: {event_type}")
        
        handlers = {
            "customer.created": self._handle_customer_created,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "payment_intent.succeeded": self._handle_payment_intent_succeeded
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(event_data)
        
        return {"status": "ignored"}
    
    async def _handle_customer_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer created webhook"""
        logger.info(f"Customer created: {data.get('id')}")
        return {"status": "success"}
    
    async def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created webhook"""
        logger.info(f"Subscription created: {data.get('id')}")
        return {"status": "success"}
    
    async def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated webhook"""
        logger.info(f"Subscription updated: {data.get('id')}")
        return {"status": "success"}
    
    async def _handle_subscription_deleted(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted webhook"""
        logger.info(f"Subscription deleted: {data.get('id')}")
        return {"status": "success"}
    
    async def _handle_payment_succeeded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment succeeded webhook"""
        logger.info(f"Payment succeeded for invoice: {data.get('id')}")
        return {"status": "success"}
    
    async def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment failed webhook"""
        logger.info(f"Payment failed for invoice: {data.get('id')}")
        # Would trigger dunning email here
        return {"status": "success"}
    
    async def _handle_payment_intent_succeeded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment intent succeeded webhook"""
        logger.info(f"Payment intent succeeded: {data.get('id')}")
        return {"status": "success"}
    
    # Reports
    async def get_revenue_report(
        self,
        start_date: datetime,
        end_date: datetime,
        currency: Optional[Currency] = None
    ) -> Dict[str, Any]:
        """Get revenue report for period"""
        
        paid_invoices = [
            inv for inv in self.invoices.values()
            if inv.paid and inv.paid_at >= start_date and inv.paid_at <= end_date
        ]
        
        if currency:
            paid_invoices = [inv for inv in paid_invoices if inv.currency == currency]
        
        # Group by currency
        revenue_by_currency = {}
        for invoice in paid_invoices:
            if invoice.currency not in revenue_by_currency:
                revenue_by_currency[invoice.currency] = 0
            revenue_by_currency[invoice.currency] += invoice.total
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "total_invoices": len(paid_invoices),
            "revenue_by_currency": {
                curr.value: amount 
                for curr, amount in revenue_by_currency.items()
            },
            "total_revenue_usd": self._convert_to_usd(revenue_by_currency)
        }
    
    def _convert_to_usd(self, amounts: Dict[Currency, float]) -> float:
        """Convert amounts to USD for reporting"""
        
        # Simplified exchange rates (would use real API)
        exchange_rates = {
            Currency.BRL: 0.20,
            Currency.USD: 1.00,
            Currency.EUR: 1.10,
            Currency.GBP: 1.25,
            Currency.CAD: 0.75,
            Currency.AUD: 0.65,
            Currency.MXN: 0.055,
            Currency.ARS: 0.0012
        }
        
        total_usd = 0
        for currency, amount in amounts.items():
            rate = exchange_rates.get(currency, 1.0)
            total_usd += amount * rate
        
        return round(total_usd, 2)

# Global instance
stripe_service = StripeService()