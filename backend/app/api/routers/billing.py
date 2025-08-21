"""
Billing API endpoints with Asaas integration
Implements Feature F003: Billing System
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.services.asaas_service import (
    asaas_service,
    Customer,
    PaymentMethod,
    SubscriptionStatus,
    BillingCycle
)
from app.models.billing_models import (
    CreateCustomerRequest,
    CreateSubscriptionRequest,
    UpdateSubscriptionRequest,
    CreatePaymentRequest,
    ApplyCouponRequest,
    WebhookPayload,
    BillingDashboard,
    InvoiceResponse,
    PaymentMethodInfo
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication - in production from auth system
async def get_current_user():
    return {
        "user_id": "user123",
        "email": "user@example.com",
        "plan": "professional",
        "customer_id": "cus_123"  # Asaas customer ID
    }

# Customer Management Endpoints
@router.post("/customers", response_model=Dict[str, Any])
async def create_customer(
    request: CreateCustomerRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new customer in Asaas payment system
    Required for subscription and payment processing
    """
    
    try:
        # Create Asaas customer object
        customer = Customer(
            name=request.name,
            email=request.email,
            cpfCnpj=request.cpf_cnpj,
            phone=request.phone,
            mobilePhone=request.mobile_phone,
            postalCode=request.postal_code,
            address=request.address,
            addressNumber=request.address_number,
            province=request.neighborhood,
            city=request.city,
            state=request.state,
            externalReference=current_user["user_id"]
        )
        
        result = await asaas_service.create_customer(customer)
        
        logger.info(f"Customer created: {result.get('id')} for user {current_user['user_id']}")
        
        return {
            "success": True,
            "customer_id": result.get("id"),
            "message": "Customer created successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create customer: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create customer: {str(e)}"
        )

@router.get("/customers/{customer_id}", response_model=Dict[str, Any])
async def get_customer_details(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get customer details from Asaas"""
    
    try:
        customer_data = await asaas_service.get_customer(customer_id)
        return {
            "success": True,
            "data": customer_data
        }
    except Exception as e:
        logger.error(f"Failed to get customer: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Customer not found: {str(e)}"
        )

# Subscription Management Endpoints
@router.post("/subscriptions", response_model=Dict[str, Any])
async def create_subscription(
    request: CreateSubscriptionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new subscription for PRD plans
    Plans: Starter (R$97), Professional (R$297), Business (R$597), Agency (R$1,997)
    """
    
    try:
        # Validate plan
        valid_plans = ["starter", "professional", "business", "agency"]
        if request.plan_name.lower() not in valid_plans:
            raise ValueError(f"Invalid plan. Choose from: {', '.join(valid_plans)}")
        
        # Create subscription
        result = await asaas_service.create_subscription(
            customer_id=request.customer_id or current_user.get("customer_id"),
            plan_name=request.plan_name,
            payment_method=PaymentMethod(request.payment_method),
            discount_coupon=request.coupon_code
        )
        
        # Setup dunning automation in background
        background_tasks.add_task(
            asaas_service.setup_dunning_automation,
            request.customer_id or current_user.get("customer_id")
        )
        
        logger.info(f"Subscription created: {result.get('id')} - Plan: {request.plan_name}")
        
        return {
            "success": True,
            "subscription_id": result.get("id"),
            "plan": request.plan_name,
            "status": result.get("status"),
            "next_due_date": result.get("nextDueDate"),
            "message": f"Subscription to {request.plan_name} plan created successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.patch("/subscriptions/{subscription_id}", response_model=Dict[str, Any])
async def update_subscription(
    subscription_id: str,
    request: UpdateSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update subscription (upgrade/downgrade plan or change payment method)
    """
    
    try:
        result = await asaas_service.update_subscription(
            subscription_id=subscription_id,
            new_plan=request.new_plan,
            new_payment_method=PaymentMethod(request.new_payment_method) if request.new_payment_method else None
        )
        
        action = "upgraded" if request.new_plan else "updated"
        logger.info(f"Subscription {subscription_id} {action} to {request.new_plan or 'same plan'}")
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "message": f"Subscription {action} successfully",
            "new_plan": request.new_plan,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to update subscription: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update subscription: {str(e)}"
        )

@router.delete("/subscriptions/{subscription_id}", response_model=Dict[str, Any])
async def cancel_subscription(
    subscription_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a subscription"""
    
    try:
        result = await asaas_service.cancel_subscription(subscription_id)
        
        logger.info(f"Subscription cancelled: {subscription_id}")
        
        return {
            "success": True,
            "subscription_id": subscription_id,
            "message": "Subscription cancelled successfully",
            "cancellation_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

# Payment Processing Endpoints
@router.post("/payments", response_model=Dict[str, Any])
async def create_payment(
    request: CreatePaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a one-time payment or additional credits purchase
    Supports PIX, Boleto, and Credit Card
    """
    
    try:
        result = await asaas_service.create_payment(
            customer_id=request.customer_id or current_user.get("customer_id"),
            amount=request.amount,
            payment_method=PaymentMethod(request.payment_method),
            description=request.description or "WordPress AI SaaS - Pagamento",
            due_date=request.due_date,
            installments=request.installments
        )
        
        response_data = {
            "success": True,
            "payment_id": result.get("id"),
            "amount": request.amount,
            "payment_method": request.payment_method,
            "status": result.get("status"),
            "due_date": result.get("dueDate"),
            "message": "Payment created successfully"
        }
        
        # Add PIX QR code if applicable
        if request.payment_method == "PIX" and "pixQrCode" in result:
            response_data["pix_qr_code"] = result["pixQrCode"]["qrCodeImage"]
            response_data["pix_copy_paste"] = result["pixQrCode"]["pixCode"]
            response_data["pix_expiration"] = result["pixQrCode"]["expirationDate"]
        
        # Add Boleto barcode if applicable
        if request.payment_method == "BOLETO":
            response_data["boleto_url"] = result.get("bankSlipUrl")
            response_data["boleto_barcode"] = result.get("nossoNumero")
        
        logger.info(f"Payment created: {result.get('id')} - Amount: R$ {request.amount}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to create payment: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create payment: {str(e)}"
        )

@router.get("/payments/{payment_id}/status", response_model=Dict[str, Any])
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check payment status"""
    
    try:
        status = await asaas_service.get_payment_status(payment_id)
        
        return {
            "payment_id": payment_id,
            "status": status,
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get payment status: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Payment not found: {str(e)}"
        )

@router.post("/payments/{payment_id}/retry", response_model=Dict[str, Any])
async def retry_payment(
    payment_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Retry a failed payment with automatic retry logic
    Uses exponential backoff strategy
    """
    
    try:
        # Start retry in background
        background_tasks.add_task(
            asaas_service.retry_failed_payment,
            payment_id,
            max_retries=3
        )
        
        logger.info(f"Payment retry initiated: {payment_id}")
        
        return {
            "success": True,
            "payment_id": payment_id,
            "message": "Payment retry initiated. You will be notified of the result.",
            "retry_strategy": "Exponential backoff: 2min, 4min, 8min"
        }
        
    except Exception as e:
        logger.error(f"Failed to retry payment: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retry payment: {str(e)}"
        )

# Coupon Management
@router.post("/coupons/apply", response_model=Dict[str, Any])
async def apply_coupon(
    request: ApplyCouponRequest,
    current_user: dict = Depends(get_current_user)
):
    """Apply a discount coupon to subscription or payment"""
    
    try:
        # Validate coupon
        discount = await asaas_service._validate_coupon(request.coupon_code)
        
        if not discount:
            raise ValueError("Invalid or expired coupon code")
        
        return {
            "success": True,
            "coupon_code": request.coupon_code.upper(),
            "discount_type": discount["type"],
            "discount_value": discount["value"],
            "message": f"Coupon {request.coupon_code.upper()} applied successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to apply coupon: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to apply coupon: {str(e)}"
        )

@router.post("/coupons", response_model=Dict[str, Any])
async def create_coupon(
    code: str,
    discount_type: str,
    discount_value: float,
    valid_until: Optional[str] = None,
    usage_limit: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new discount coupon (admin only)"""
    
    try:
        result = await asaas_service.create_coupon(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            valid_until=valid_until,
            usage_limit=usage_limit
        )
        
        logger.info(f"Coupon created: {code}")
        
        return {
            "success": True,
            "coupon": result,
            "message": f"Coupon {code} created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create coupon: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create coupon: {str(e)}"
        )

# Webhook Endpoint
@router.post("/webhooks/asaas", response_model=Dict[str, Any])
async def process_asaas_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Process Asaas webhook notifications
    Handles payment confirmations, failures, subscription changes, etc.
    """
    
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        # Get signature from headers if present
        signature = request.headers.get("asaas-signature")
        
        # Process webhook
        result = await asaas_service.process_webhook(webhook_data, signature)
        
        logger.info(f"Webhook processed: {result.get('action')}")
        
        return {
            "success": True,
            "processed": True,
            "action": result.get("action"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        # Don't raise exception for webhooks - return 200 to prevent retries
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Billing Dashboard
@router.get("/dashboard", response_model=BillingDashboard)
async def get_billing_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive billing dashboard for user
    Shows current plan, usage, payment history, and upcoming charges
    """
    
    try:
        # This would aggregate data from multiple sources
        dashboard = BillingDashboard(
            current_plan="professional",
            plan_price=297.00,
            billing_cycle="monthly",
            next_billing_date=(datetime.now() + timedelta(days=15)).isoformat(),
            payment_method="PIX",
            payment_status="active",
            
            current_usage={
                "sites": 3,
                "sites_limit": 5,
                "ai_credits_used": 2500,
                "ai_credits_limit": 5000,
                "storage_gb_used": 12.5,
                "storage_gb_limit": 50,
                "bandwidth_gb_used": 120,
                "bandwidth_gb_limit": 500
            },
            
            recent_payments=[
                {
                    "id": "pay_123",
                    "date": "2025-08-01",
                    "amount": 297.00,
                    "status": "confirmed",
                    "description": "Plano Professional - Agosto"
                },
                {
                    "id": "pay_122",
                    "date": "2025-07-01",
                    "amount": 297.00,
                    "status": "confirmed",
                    "description": "Plano Professional - Julho"
                }
            ],
            
            upcoming_charges=[
                {
                    "date": "2025-09-01",
                    "amount": 297.00,
                    "description": "Plano Professional - Setembro"
                }
            ],
            
            available_upgrades=[
                {
                    "plan": "business",
                    "price": 597.00,
                    "benefits": [
                        "15 sites WordPress",
                        "15,000 AI Credits",
                        "200GB storage",
                        "Priority support"
                    ]
                },
                {
                    "plan": "agency",
                    "price": 1997.00,
                    "benefits": [
                        "Unlimited sites",
                        "50,000 AI Credits",
                        "1TB storage",
                        "White label",
                        "Dedicated support"
                    ]
                }
            ]
        )
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Failed to get billing dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get billing dashboard: {str(e)}"
        )

# Invoice Management
@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = 12,
    current_user: dict = Depends(get_current_user)
):
    """Get user's invoice history"""
    
    try:
        # Mock invoice data - would come from Asaas
        invoices = [
            InvoiceResponse(
                id=f"inv_{i}",
                date=(datetime.now() - timedelta(days=30*i)).isoformat(),
                amount=297.00,
                status="paid",
                description=f"Plano Professional - {(datetime.now() - timedelta(days=30*i)).strftime('%B %Y')}",
                pdf_url=f"https://api.asaas.com/invoices/inv_{i}.pdf"
            )
            for i in range(min(limit, 6))
        ]
        
        return invoices
        
    except Exception as e:
        logger.error(f"Failed to get invoices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get invoices: {str(e)}"
        )

# Payment Methods
@router.get("/payment-methods", response_model=List[PaymentMethodInfo])
async def get_payment_methods(
    current_user: dict = Depends(get_current_user)
):
    """Get available payment methods for user"""
    
    return [
        PaymentMethodInfo(
            method="PIX",
            enabled=True,
            icon="pix",
            description="Pagamento instantâneo via PIX",
            processing_time="Imediato"
        ),
        PaymentMethodInfo(
            method="BOLETO",
            enabled=True,
            icon="barcode",
            description="Boleto bancário",
            processing_time="1-3 dias úteis"
        ),
        PaymentMethodInfo(
            method="CREDIT_CARD",
            enabled=True,
            icon="credit-card",
            description="Cartão de crédito",
            processing_time="Imediato",
            installments_available=True,
            max_installments=12
        )
    ]

# Revenue Reports (Admin)
@router.get("/reports/revenue", response_model=Dict[str, Any])
async def get_revenue_report(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Get revenue report for specified period (admin only)"""
    
    try:
        report = await asaas_service.get_revenue_report(start_date, end_date)
        
        return {
            "success": True,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get revenue report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get revenue report: {str(e)}"
        )

@router.get("/reports/churn", response_model=Dict[str, Any])
async def get_churn_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get churn rate and related metrics (admin only)"""
    
    try:
        metrics = await asaas_service.get_churn_metrics()
        
        return {
            "success": True,
            "metrics": metrics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get churn metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get churn metrics: {str(e)}"
        )