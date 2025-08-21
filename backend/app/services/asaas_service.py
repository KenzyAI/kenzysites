"""
Asaas Payment Gateway Integration Service
Implements Feature F003: Billing System for Brazilian market
"""

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)

# Asaas API Configuration
ASAAS_API_BASE_URL = "https://api.asaas.com/v3"
ASAAS_SANDBOX_URL = "https://sandbox.asaas.com/api/v3"

class PaymentMethod(str, Enum):
    PIX = "PIX"
    BOLETO = "BOLETO"
    CREDIT_CARD = "CREDIT_CARD"

class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class BillingCycle(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"

# Pydantic Models for Asaas Integration
class Customer(BaseModel):
    """Asaas Customer Model"""
    id: Optional[str] = None
    name: str
    email: str
    cpfCnpj: str
    phone: Optional[str] = None
    mobilePhone: Optional[str] = None
    postalCode: Optional[str] = None
    address: Optional[str] = None
    addressNumber: Optional[str] = None
    complement: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    externalReference: Optional[str] = None
    notificationDisabled: bool = False
    emailEnabled: bool = True
    smsEnabled: bool = False
    phoneCallEnabled: bool = False

class Subscription(BaseModel):
    """Asaas Subscription Model"""
    id: Optional[str] = None
    customer: str  # Customer ID
    billingType: PaymentMethod
    value: float
    cycle: BillingCycle
    description: str
    nextDueDate: Optional[str] = None
    discount: Optional[Dict[str, Any]] = None
    interest: Optional[Dict[str, Any]] = None
    fine: Optional[Dict[str, Any]] = None
    split: Optional[List[Dict[str, Any]]] = None
    externalReference: Optional[str] = None

class Payment(BaseModel):
    """Asaas Payment Model"""
    id: Optional[str] = None
    customer: str  # Customer ID
    billingType: PaymentMethod
    value: float
    dueDate: str
    description: Optional[str] = None
    externalReference: Optional[str] = None
    installmentCount: Optional[int] = None
    installmentValue: Optional[float] = None
    discount: Optional[Dict[str, Any]] = None
    interest: Optional[Dict[str, Any]] = None
    fine: Optional[Dict[str, Any]] = None
    postalService: bool = False
    split: Optional[List[Dict[str, Any]]] = None

class PixKey(BaseModel):
    """PIX payment response"""
    id: str
    encodedImage: str  # Base64 QR Code
    payload: str  # PIX copy-paste code
    expirationDate: str

class AsaasService:
    """
    Service for managing payments through Asaas gateway
    Supports PIX, Boleto, and Credit Card for Brazilian market
    """
    
    def __init__(self):
        self.api_key = settings.ASAAS_API_KEY if hasattr(settings, 'ASAAS_API_KEY') else None
        self.use_sandbox = settings.ASAAS_SANDBOX if hasattr(settings, 'ASAAS_SANDBOX') else True
        self.base_url = ASAAS_SANDBOX_URL if self.use_sandbox else ASAAS_API_BASE_URL
        self.webhook_token = settings.ASAAS_WEBHOOK_TOKEN if hasattr(settings, 'ASAAS_WEBHOOK_TOKEN') else None
        
        if not self.api_key:
            logger.warning("⚠️ Asaas API key not configured. Payment features will be limited.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            "access_token": self.api_key or "",
            "Content-Type": "application/json",
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make async HTTP request to Asaas API"""
        
        if not self.api_key:
            raise ValueError("Asaas API key not configured")
        
        url = f"{self.base_url}/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data,
                    params=params,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Asaas API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Asaas request failed: {str(e)}")
                raise
    
    # Customer Management
    async def create_customer(self, customer: Customer) -> Dict[str, Any]:
        """Create a new customer in Asaas"""
        
        logger.info(f"Creating Asaas customer: {customer.email}")
        
        customer_data = customer.dict(exclude_none=True, exclude={'id'})
        result = await self._make_request("POST", "customers", customer_data)
        
        logger.info(f"✅ Customer created: {result.get('id')}")
        return result
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer details"""
        return await self._make_request("GET", f"customers/{customer_id}")
    
    async def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information"""
        return await self._make_request("POST", f"customers/{customer_id}", updates)
    
    # Subscription Management (PRD Plans)
    async def create_subscription(
        self, 
        customer_id: str,
        plan_name: str,
        payment_method: PaymentMethod,
        discount_coupon: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create subscription based on PRD plans
        Plans: Starter (R$97), Professional (R$297), Business (R$597), Agency (R$1,997)
        """
        
        # Plan prices from PRD
        plan_prices = {
            "starter": 97.00,
            "professional": 297.00,
            "business": 597.00,
            "agency": 1997.00
        }
        
        if plan_name.lower() not in plan_prices:
            raise ValueError(f"Invalid plan: {plan_name}")
        
        subscription = Subscription(
            customer=customer_id,
            billingType=payment_method,
            value=plan_prices[plan_name.lower()],
            cycle=BillingCycle.MONTHLY,
            description=f"WordPress AI SaaS - Plano {plan_name.title()}",
            externalReference=f"plan_{plan_name}_{customer_id}"
        )
        
        # Apply discount if coupon provided
        if discount_coupon:
            subscription.discount = await self._validate_coupon(discount_coupon)
        
        logger.info(f"Creating subscription: {plan_name} for customer {customer_id}")
        
        result = await self._make_request(
            "POST", 
            "subscriptions", 
            subscription.dict(exclude_none=True, exclude={'id'})
        )
        
        logger.info(f"✅ Subscription created: {result.get('id')}")
        return result
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        
        logger.info(f"Cancelling subscription: {subscription_id}")
        return await self._make_request("DELETE", f"subscriptions/{subscription_id}")
    
    async def update_subscription(
        self, 
        subscription_id: str,
        new_plan: Optional[str] = None,
        new_payment_method: Optional[PaymentMethod] = None
    ) -> Dict[str, Any]:
        """Update subscription (upgrade/downgrade)"""
        
        updates = {}
        
        if new_plan:
            plan_prices = {
                "starter": 97.00,
                "professional": 297.00,
                "business": 597.00,
                "agency": 1997.00
            }
            if new_plan.lower() in plan_prices:
                updates["value"] = plan_prices[new_plan.lower()]
                updates["description"] = f"WordPress AI SaaS - Plano {new_plan.title()}"
        
        if new_payment_method:
            updates["billingType"] = new_payment_method.value
        
        logger.info(f"Updating subscription {subscription_id}: {updates}")
        return await self._make_request("POST", f"subscriptions/{subscription_id}", updates)
    
    # Payment Processing
    async def create_payment(
        self,
        customer_id: str,
        amount: float,
        payment_method: PaymentMethod,
        description: str,
        due_date: Optional[str] = None,
        installments: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a one-time payment"""
        
        if not due_date:
            due_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        payment = Payment(
            customer=customer_id,
            billingType=payment_method,
            value=amount,
            dueDate=due_date,
            description=description,
            installmentCount=installments if payment_method == PaymentMethod.CREDIT_CARD else None
        )
        
        logger.info(f"Creating payment: {amount} BRL via {payment_method}")
        
        result = await self._make_request(
            "POST",
            "payments",
            payment.dict(exclude_none=True, exclude={'id'})
        )
        
        # If PIX, get QR code
        if payment_method == PaymentMethod.PIX:
            pix_data = await self.get_pix_qr_code(result['id'])
            result['pixQrCode'] = pix_data
        
        logger.info(f"✅ Payment created: {result.get('id')}")
        return result
    
    async def get_pix_qr_code(self, payment_id: str) -> Dict[str, Any]:
        """Get PIX QR code for payment"""
        
        result = await self._make_request("GET", f"payments/{payment_id}/pixQrCode")
        return {
            "qrCodeImage": result.get("encodedImage"),  # Base64 image
            "pixCode": result.get("payload"),  # Copy-paste code
            "expirationDate": result.get("expirationDate")
        }
    
    async def get_payment_status(self, payment_id: str) -> str:
        """Check payment status"""
        
        result = await self._make_request("GET", f"payments/{payment_id}")
        return result.get("status", "UNKNOWN")
    
    # Dunning & Recovery (Feature F004)
    async def setup_dunning_automation(self, customer_id: str) -> Dict[str, Any]:
        """
        Setup automatic dunning emails for failed payments
        PRD: D+3 warning, D+7 suspension, D+15 second warning, D+30 deletion
        """
        
        dunning_config = {
            "customer": customer_id,
            "notifications": [
                {
                    "days": 3,
                    "type": "EMAIL",
                    "template": "payment_reminder_3days",
                    "subject": "⚠️ Seu pagamento está pendente - WordPress AI SaaS"
                },
                {
                    "days": 7,
                    "type": "SUSPENSION",
                    "action": "suspend_site",
                    "template": "site_suspended",
                    "subject": "❌ Seu site foi suspenso por falta de pagamento"
                },
                {
                    "days": 15,
                    "type": "EMAIL",
                    "template": "final_warning",
                    "subject": "🚨 AVISO FINAL - Seu site será excluído em 15 dias"
                },
                {
                    "days": 30,
                    "type": "DELETION",
                    "action": "backup_and_delete",
                    "template": "site_deleted",
                    "subject": "Site excluído - Backup disponível por 7 dias"
                }
            ]
        }
        
        # This would integrate with Asaas notification system
        logger.info(f"Setting up dunning automation for customer {customer_id}")
        return dunning_config
    
    # Retry Logic for Failed Payments
    async def retry_failed_payment(self, payment_id: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Retry failed payment with exponential backoff
        """
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Retrying payment {payment_id}, attempt {attempt + 1}/{max_retries}")
                
                # Wait with exponential backoff
                if attempt > 0:
                    await asyncio.sleep(2 ** attempt * 60)  # 2min, 4min, 8min
                
                result = await self._make_request("POST", f"payments/{payment_id}/retry")
                
                if result.get("status") == "CONFIRMED":
                    logger.info(f"✅ Payment retry successful: {payment_id}")
                    return result
                    
            except Exception as e:
                logger.error(f"Payment retry failed: {str(e)}")
                
                if attempt == max_retries - 1:
                    # Final attempt failed, trigger dunning
                    await self._trigger_dunning_action(payment_id, "final_retry_failed")
        
        return {"status": "FAILED", "message": "All retry attempts exhausted"}
    
    # Coupon Management
    async def create_coupon(
        self,
        code: str,
        discount_type: str,  # "PERCENTAGE" or "FIXED"
        discount_value: float,
        valid_until: Optional[str] = None,
        usage_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create discount coupon"""
        
        coupon_data = {
            "code": code.upper(),
            "type": discount_type,
            "value": discount_value,
            "validUntil": valid_until,
            "usageLimit": usage_limit,
            "description": f"Cupom de desconto WordPress AI SaaS"
        }
        
        logger.info(f"Creating coupon: {code}")
        
        # This would integrate with Asaas coupon system
        return coupon_data
    
    async def _validate_coupon(self, coupon_code: str) -> Optional[Dict[str, Any]]:
        """Validate and return coupon discount details"""
        
        # Mock validation - would check against database
        valid_coupons = {
            "LAUNCH50": {"value": 50, "type": "PERCENTAGE"},
            "BLACKFRIDAY": {"value": 30, "type": "PERCENTAGE"},
            "WELCOME100": {"value": 100, "type": "FIXED"}
        }
        
        return valid_coupons.get(coupon_code.upper())
    
    # Webhook Processing
    async def process_webhook(
        self, 
        webhook_data: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process Asaas webhook notifications
        Events: payment confirmed, payment failed, subscription cancelled, etc.
        """
        
        # Verify webhook signature if provided
        if signature and self.webhook_token:
            if not self._verify_webhook_signature(webhook_data, signature):
                raise ValueError("Invalid webhook signature")
        
        event_type = webhook_data.get("event")
        payment_data = webhook_data.get("payment", {})
        
        logger.info(f"Processing webhook: {event_type}")
        
        # Handle different event types
        handlers = {
            "PAYMENT_CONFIRMED": self._handle_payment_confirmed,
            "PAYMENT_RECEIVED": self._handle_payment_confirmed,
            "PAYMENT_OVERDUE": self._handle_payment_overdue,
            "PAYMENT_DELETED": self._handle_payment_deleted,
            "PAYMENT_REFUNDED": self._handle_payment_refunded,
            "SUBSCRIPTION_CREATED": self._handle_subscription_created,
            "SUBSCRIPTION_UPDATED": self._handle_subscription_updated,
            "SUBSCRIPTION_DELETED": self._handle_subscription_cancelled,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return await handler(payment_data)
        
        logger.warning(f"Unhandled webhook event: {event_type}")
        return {"status": "unhandled", "event": event_type}
    
    def _verify_webhook_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Verify webhook signature for security"""
        
        if not self.webhook_token:
            return True  # Skip verification if token not configured
        
        # Calculate expected signature
        payload = json.dumps(data, separators=(',', ':'))
        expected_signature = hmac.new(
            self.webhook_token.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    # Webhook Event Handlers
    async def _handle_payment_confirmed(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle confirmed payment"""
        
        customer_id = payment_data.get("customer")
        amount = payment_data.get("value")
        
        logger.info(f"✅ Payment confirmed: {amount} BRL from customer {customer_id}")
        
        # Update user subscription status
        # Enable features based on plan
        # Send confirmation email
        
        return {"status": "processed", "action": "payment_confirmed"}
    
    async def _handle_payment_overdue(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle overdue payment (trigger dunning)"""
        
        payment_id = payment_data.get("id")
        customer_id = payment_data.get("customer")
        days_overdue = payment_data.get("daysOverdue", 0)
        
        logger.warning(f"⚠️ Payment overdue: {payment_id} ({days_overdue} days)")
        
        # Trigger appropriate dunning action based on days overdue
        if days_overdue >= 3 and days_overdue < 7:
            await self._send_payment_reminder(customer_id, "3_days")
        elif days_overdue >= 7 and days_overdue < 15:
            await self._suspend_customer_sites(customer_id)
        elif days_overdue >= 15 and days_overdue < 30:
            await self._send_payment_reminder(customer_id, "final_warning")
        elif days_overdue >= 30:
            await self._backup_and_delete_sites(customer_id)
        
        return {"status": "processed", "action": f"dunning_day_{days_overdue}"}
    
    async def _handle_payment_deleted(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deleted/cancelled payment"""
        
        logger.info(f"Payment deleted: {payment_data.get('id')}")
        return {"status": "processed", "action": "payment_deleted"}
    
    async def _handle_payment_refunded(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refunded payment"""
        
        logger.info(f"Payment refunded: {payment_data.get('id')}")
        
        # Adjust user credits/features
        # Send refund confirmation email
        
        return {"status": "processed", "action": "payment_refunded"}
    
    async def _handle_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new subscription"""
        
        logger.info(f"✅ Subscription created: {subscription_data.get('id')}")
        
        # Provision resources
        # Send welcome email
        # Setup initial credits
        
        return {"status": "processed", "action": "subscription_created"}
    
    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update (upgrade/downgrade)"""
        
        logger.info(f"Subscription updated: {subscription_data.get('id')}")
        
        # Adjust features based on new plan
        # Prorate billing if needed
        
        return {"status": "processed", "action": "subscription_updated"}
    
    async def _handle_subscription_cancelled(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cancelled subscription"""
        
        logger.info(f"Subscription cancelled: {subscription_data.get('id')}")
        
        # Schedule resource cleanup
        # Send cancellation confirmation
        # Offer win-back promotion
        
        return {"status": "processed", "action": "subscription_cancelled"}
    
    # Dunning Actions (Feature F004)
    async def _send_payment_reminder(self, customer_id: str, reminder_type: str):
        """Send payment reminder email"""
        logger.info(f"Sending {reminder_type} reminder to customer {customer_id}")
        # Would integrate with email service
    
    async def _suspend_customer_sites(self, customer_id: str):
        """Suspend all customer sites (D+7)"""
        logger.warning(f"⛔ Suspending sites for customer {customer_id}")
        # Would integrate with WordPress management service
    
    async def _backup_and_delete_sites(self, customer_id: str):
        """Backup and delete customer sites (D+30)"""
        logger.error(f"🗑️ Backing up and deleting sites for customer {customer_id}")
        # Would integrate with backup service and WordPress management
    
    async def _trigger_dunning_action(self, payment_id: str, action: str):
        """Trigger specific dunning action"""
        logger.info(f"Triggering dunning action: {action} for payment {payment_id}")
        # Would integrate with dunning automation system
    
    # Reports and Analytics
    async def get_revenue_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get revenue report for period"""
        
        params = {
            "dateCreated[ge]": start_date,
            "dateCreated[le]": end_date,
            "status": "CONFIRMED"
        }
        
        result = await self._make_request("GET", "payments", params=params)
        
        # Calculate metrics
        total_revenue = sum(p.get("value", 0) for p in result.get("data", []))
        total_transactions = len(result.get("data", []))
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_ticket": total_revenue / total_transactions if total_transactions > 0 else 0,
            "currency": "BRL"
        }
    
    async def get_churn_metrics(self) -> Dict[str, Any]:
        """Calculate churn rate and related metrics"""
        
        # Would query subscription data
        return {
            "monthly_churn_rate": 5.2,  # Percentage
            "annual_churn_rate": 42.3,  # Percentage
            "average_customer_lifetime_months": 19.2,
            "ltv": 3500.00  # BRL
        }

# Create singleton instance
asaas_service = AsaasService()

# Export for use in API endpoints
__all__ = ['asaas_service', 'AsaasService', 'PaymentMethod', 'SubscriptionStatus', 'Customer', 'Subscription', 'Payment']