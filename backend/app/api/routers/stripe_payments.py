"""
Stripe International Payments API endpoints
Phase 3: Launch Oficial - Global payment processing
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Header
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.services.stripe_service import (
    stripe_service,
    Currency,
    PaymentMethod,
    PlanTier,
    SubscriptionStatus
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication
async def get_current_user():
    return {
        "user_id": "user123",
        "email": "user@example.com",
        "stripe_customer_id": None,
        "country": "BR",
        "locale": "pt-BR"
    }

# Pricing Plans
@router.get("/plans")
async def get_pricing_plans(
    currency: Optional[Currency] = Query(None, description="Currency for pricing"),
    country: Optional[str] = Query(None, description="Country code for auto-currency"),
    locale: Optional[str] = Query("en-US", description="Locale for translations")
):
    """
    Get available pricing plans with international pricing
    Auto-detects currency based on country if not specified
    """
    
    try:
        # Auto-detect currency from country
        if not currency and country:
            currency = stripe_service._get_default_currency(country)
        elif not currency:
            currency = Currency.USD
        
        plans = []
        for plan_key in [PlanTier.STARTER, PlanTier.PROFESSIONAL, PlanTier.BUSINESS, PlanTier.AGENCY]:
            plan = stripe_service.plans.get(plan_key.value)
            if plan:
                plan_data = {
                    "id": plan.id,
                    "tier": plan.tier,
                    "name": plan.name,
                    "description": plan.description,
                    "price": plan.prices.get(currency, plan.prices[Currency.USD]),
                    "currency": currency.value,
                    "interval": plan.interval,
                    "features": plan.features,
                    "trial_days": plan.trial_days,
                    "recommended": plan.tier == PlanTier.PROFESSIONAL
                }
                plans.append(plan_data)
        
        return {
            "currency": currency.value,
            "country": country,
            "plans": plans,
            "payment_methods": _get_available_payment_methods(currency)
        }
        
    except Exception as e:
        logger.error(f"Failed to get pricing plans: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pricing plans: {str(e)}"
        )

def _get_available_payment_methods(currency: Currency) -> List[str]:
    """Get available payment methods for currency"""
    if currency == Currency.BRL:
        return ["card", "pix", "boleto"]
    elif currency == Currency.EUR:
        return ["card", "sepa_debit", "paypal", "apple_pay", "google_pay"]
    elif currency == Currency.USD:
        return ["card", "ach_debit", "paypal", "apple_pay", "google_pay"]
    else:
        return ["card", "paypal", "apple_pay", "google_pay"]

# Customer Management
@router.post("/customers")
async def create_stripe_customer(
    country: str = Body(..., description="Country code (BR, US, GB, etc)"),
    tax_id: Optional[str] = Body(None, description="Tax ID (CPF/CNPJ for Brazil, VAT for EU)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Stripe customer for international billing
    Required before creating subscriptions
    """
    
    try:
        customer = await stripe_service.create_customer(
            email=current_user["email"],
            name=current_user.get("name"),
            country=country,
            tax_id=tax_id,
            metadata={"user_id": current_user["user_id"]}
        )
        
        logger.info(f"Created Stripe customer {customer.id} for user {current_user['user_id']}")
        
        return {
            "success": True,
            "customer_id": customer.id,
            "currency": customer.currency.value,
            "country": customer.country,
            "message": f"Customer created with currency {customer.currency.value}"
        }
        
    except Exception as e:
        logger.error(f"Failed to create Stripe customer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create customer: {str(e)}"
        )

@router.get("/customers/{customer_id}")
async def get_customer_details(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get Stripe customer details"""
    
    try:
        customer = stripe_service.customers.get(customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} not found"
            )
        
        return {
            "customer_id": customer.id,
            "email": customer.email,
            "country": customer.country,
            "currency": customer.currency.value,
            "subscription": {
                "id": customer.subscription_id,
                "plan": customer.plan_tier.value if customer.plan_tier else None
            } if customer.subscription_id else None,
            "payment_methods": customer.payment_methods,
            "balance": customer.balance,
            "created_at": customer.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer: {str(e)}"
        )

# Subscription Management
@router.post("/subscriptions")
async def create_subscription(
    customer_id: str = Body(..., description="Stripe customer ID"),
    plan_tier: PlanTier = Body(..., description="Plan tier to subscribe"),
    payment_method_id: Optional[str] = Body(None, description="Payment method ID"),
    trial_days: Optional[int] = Body(None, description="Override trial period"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a subscription for a customer
    Supports multi-currency based on customer's country
    """
    
    try:
        subscription = await stripe_service.create_subscription(
            customer_id=customer_id,
            plan_tier=plan_tier,
            payment_method_id=payment_method_id,
            trial_days=trial_days
        )
        
        logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
        
        return {
            "success": True,
            "subscription": {
                "id": subscription.id,
                "status": subscription.status.value,
                "plan": plan_tier.value,
                "amount": subscription.amount,
                "currency": subscription.currency.value,
                "interval": subscription.interval,
                "current_period_end": subscription.current_period_end.isoformat(),
                "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None
            },
            "message": f"Subscription created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.put("/subscriptions/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    new_plan_tier: Optional[PlanTier] = Body(None, description="New plan tier"),
    payment_method_id: Optional[str] = Body(None, description="New payment method"),
    current_user: dict = Depends(get_current_user)
):
    """
    Update subscription (upgrade/downgrade plan)
    Handles proration automatically
    """
    
    try:
        subscription = await stripe_service.update_subscription(
            subscription_id=subscription_id,
            new_plan_tier=new_plan_tier,
            payment_method_id=payment_method_id
        )
        
        logger.info(f"Updated subscription {subscription_id}")
        
        return {
            "success": True,
            "subscription": {
                "id": subscription.id,
                "status": subscription.status.value,
                "amount": subscription.amount,
                "currency": subscription.currency.value
            },
            "message": "Subscription updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update subscription: {str(e)}"
        )

@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    immediately: bool = Query(False, description="Cancel immediately vs end of period"),
    current_user: dict = Depends(get_current_user)
):
    """Cancel a subscription"""
    
    try:
        subscription = await stripe_service.cancel_subscription(
            subscription_id=subscription_id,
            immediately=immediately
        )
        
        logger.info(f"Canceled subscription {subscription_id}")
        
        return {
            "success": True,
            "message": f"Subscription will be canceled {'immediately' if immediately else 'at period end'}",
            "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

# Payment Methods
@router.post("/payment-methods")
async def add_payment_method(
    customer_id: str = Body(..., description="Stripe customer ID"),
    payment_method_type: PaymentMethod = Body(..., description="Payment method type"),
    details: Dict[str, Any] = Body(..., description="Payment method details"),
    set_default: bool = Body(True, description="Set as default payment method"),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a payment method to customer
    Supports cards, bank accounts, wallets, PIX, Boleto
    """
    
    try:
        # Validate payment method for customer's country
        customer = stripe_service.customers.get(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        available_methods = _get_available_payment_methods(customer.currency)
        if payment_method_type.value not in available_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Payment method {payment_method_type.value} not available for {customer.currency.value}"
            )
        
        payment_method_id = await stripe_service.add_payment_method(
            customer_id=customer_id,
            payment_method_type=payment_method_type,
            details=details,
            set_default=set_default
        )
        
        logger.info(f"Added payment method {payment_method_id} to customer {customer_id}")
        
        return {
            "success": True,
            "payment_method_id": payment_method_id,
            "message": f"Payment method added successfully"
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add payment method: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add payment method: {str(e)}"
        )

# Invoices
@router.get("/invoices")
async def list_invoices(
    customer_id: str = Query(..., description="Stripe customer ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, le=100, description="Maximum invoices to return"),
    current_user: dict = Depends(get_current_user)
):
    """List customer invoices"""
    
    try:
        invoices = [
            inv for inv in stripe_service.invoices.values()
            if inv.customer_id == customer_id
        ]
        
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
        
        # Sort by date, newest first
        invoices.sort(key=lambda x: x.created_at, reverse=True)
        invoices = invoices[:limit]
        
        return {
            "total": len(invoices),
            "invoices": [
                {
                    "id": inv.id,
                    "amount": inv.total,
                    "currency": inv.currency.value,
                    "status": inv.status,
                    "paid": inv.paid,
                    "due_date": inv.due_date.isoformat() if inv.due_date else None,
                    "invoice_url": inv.hosted_invoice_url,
                    "pdf_url": inv.invoice_pdf
                }
                for inv in invoices
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list invoices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list invoices: {str(e)}"
        )

@router.post("/invoices/{invoice_id}/pay")
async def pay_invoice(
    invoice_id: str,
    payment_method_id: str = Body(..., description="Payment method to use"),
    current_user: dict = Depends(get_current_user)
):
    """Pay an invoice"""
    
    try:
        invoice = await stripe_service.pay_invoice(
            invoice_id=invoice_id,
            payment_method_id=payment_method_id
        )
        
        logger.info(f"Paid invoice {invoice_id}")
        
        return {
            "success": True,
            "invoice": {
                "id": invoice.id,
                "status": invoice.status,
                "paid": invoice.paid,
                "charge_id": invoice.charge_id
            },
            "message": "Invoice paid successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to pay invoice: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pay invoice: {str(e)}"
        )

# One-time Payments
@router.post("/payment-intents")
async def create_payment_intent(
    amount: float = Body(..., gt=0, description="Amount to charge"),
    currency: Currency = Body(..., description="Currency"),
    description: Optional[str] = Body(None, description="Payment description"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a payment intent for one-time payment
    Used for add-ons, credits, etc.
    """
    
    try:
        # Get or create customer
        customer_id = current_user.get("stripe_customer_id")
        
        payment_intent = await stripe_service.create_payment_intent(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            metadata={
                "user_id": current_user["user_id"],
                "description": description
            }
        )
        
        logger.info(f"Created payment intent {payment_intent.id}")
        
        return {
            "payment_intent_id": payment_intent.id,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency.value,
            "client_secret": f"{payment_intent.id}_secret_test",  # Mock client secret
            "payment_methods": [pm.value for pm in payment_intent.payment_method_types]
        }
        
    except Exception as e:
        logger.error(f"Failed to create payment intent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment intent: {str(e)}"
        )

# Webhooks
@router.post("/webhooks")
async def handle_stripe_webhook(
    event_type: str = Body(..., description="Stripe event type"),
    event_data: Dict[str, Any] = Body(..., description="Event data"),
    stripe_signature: Optional[str] = Header(None)
):
    """
    Handle Stripe webhook events
    Processes payment confirmations, subscription changes, etc.
    """
    
    try:
        # In production, verify webhook signature
        if stripe_signature:
            # Verify signature with Stripe webhook secret
            pass
        
        result = await stripe_service.handle_webhook(event_type, event_data)
        
        logger.info(f"Processed webhook: {event_type}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to process webhook: {str(e)}")
        # Return 200 to acknowledge receipt even on error
        return {"status": "error", "message": str(e)}

# Revenue Reports
@router.get("/reports/revenue")
async def get_revenue_report(
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    currency: Optional[Currency] = Query(None, description="Filter by currency"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get revenue report for date range
    Shows revenue by currency with USD conversion
    """
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        report = await stripe_service.get_revenue_report(
            start_date=start,
            end_date=end,
            currency=currency
        )
        
        return report
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        logger.error(f"Failed to get revenue report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get revenue report: {str(e)}"
        )

# Tax Calculation
@router.post("/calculate-tax")
async def calculate_tax(
    amount: float = Body(..., gt=0, description="Amount before tax"),
    country: str = Body(..., description="Country code"),
    tax_id: Optional[str] = Body(None, description="Tax ID for validation")
):
    """
    Calculate tax for a given amount and country
    Supports VAT, GST, sales tax
    """
    
    try:
        tax_rate = stripe_service._get_tax_rate(country)
        tax_amount = amount * tax_rate
        total = amount + tax_amount
        
        return {
            "country": country,
            "tax_rate": tax_rate,
            "subtotal": amount,
            "tax_amount": round(tax_amount, 2),
            "total": round(total, 2),
            "tax_id_valid": tax_id is not None  # Would validate format
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate tax: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate tax: {str(e)}"
        )

# Currency Conversion
@router.get("/exchange-rates")
async def get_exchange_rates(
    base_currency: Currency = Query(Currency.USD, description="Base currency")
):
    """Get current exchange rates for display purposes"""
    
    # Mock exchange rates - would use real API
    rates = {
        Currency.BRL: 5.00,
        Currency.USD: 1.00,
        Currency.EUR: 0.91,
        Currency.GBP: 0.80,
        Currency.CAD: 1.33,
        Currency.AUD: 1.54,
        Currency.MXN: 18.20,
        Currency.ARS: 833.33
    }
    
    if base_currency != Currency.USD:
        base_rate = rates[base_currency]
        rates = {
            curr: rate / base_rate
            for curr, rate in rates.items()
        }
    
    return {
        "base": base_currency.value,
        "rates": {curr.value: rate for curr, rate in rates.items()},
        "updated_at": datetime.now().isoformat()
    }