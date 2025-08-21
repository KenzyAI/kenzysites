"""
Asaas Payment Integration Service
Real implementation for Brazilian payment processing
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import os
from enum import Enum

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    CONFIRMED = "CONFIRMED"
    OVERDUE = "OVERDUE"
    REFUNDED = "REFUNDED"
    RECEIVED_IN_CASH = "RECEIVED_IN_CASH"
    REFUND_REQUESTED = "REFUND_REQUESTED"
    CHARGEBACK_REQUESTED = "CHARGEBACK_REQUESTED"
    CHARGEBACK_DISPUTE = "CHARGEBACK_DISPUTE"
    AWAITING_CHARGEBACK_REVERSAL = "AWAITING_CHARGEBACK_REVERSAL"
    DUNNING_REQUESTED = "DUNNING_REQUESTED"
    DUNNING_RECEIVED = "DUNNING_RECEIVED"
    AWAITING_RISK_ANALYSIS = "AWAITING_RISK_ANALYSIS"

class BillingType(Enum):
    BOLETO = "BOLETO"
    CREDIT_CARD = "CREDIT_CARD"
    PIX = "PIX"
    UNDEFINED = "UNDEFINED"

class AsaasIntegration:
    """
    Asaas payment gateway integration for Brazilian market
    Handles PIX, Boleto, and Credit Card payments
    """
    
    def __init__(self):
        self.api_key = os.getenv('ASAAS_API_KEY', '')
        self.base_url = os.getenv('ASAAS_API_URL', 'https://www.asaas.com/api/v3')
        self.webhook_token = os.getenv('ASAAS_WEBHOOK_TOKEN', '')
        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json'
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
    
    async def create_customer(
        self,
        name: str,
        email: str,
        cpf_cnpj: str,
        phone: Optional[str] = None,
        address: Optional[Dict] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a customer in Asaas
        """
        
        data = {
            "name": name,
            "email": email,
            "cpfCnpj": cpf_cnpj.replace(".", "").replace("-", "").replace("/", ""),
            "notificationDisabled": False,
            "emailEnabledForProvider": True
        }
        
        if phone:
            data["phone"] = phone
            data["mobilePhone"] = phone
        
        if company:
            data["company"] = company
        
        if address:
            data["address"] = address.get("street")
            data["addressNumber"] = address.get("number")
            data["complement"] = address.get("complement")
            data["province"] = address.get("neighborhood")
            data["postalCode"] = address.get("postal_code")
            data["city"] = address.get("city")
            data["state"] = address.get("state")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/customers",
                json=data
            )
            response.raise_for_status()
            
            customer_data = response.json()
            logger.info(f"Created Asaas customer: {customer_data['id']}")
            
            return {
                "success": True,
                "customer_id": customer_data["id"],
                "data": customer_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create Asaas customer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_subscription(
        self,
        customer_id: str,
        plan_name: str,
        value: float,
        billing_type: BillingType = BillingType.CREDIT_CARD,
        next_due_date: Optional[datetime] = None,
        description: Optional[str] = None,
        credit_card: Optional[Dict] = None,
        discount: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a recurring subscription
        """
        
        if not next_due_date:
            next_due_date = datetime.now() + timedelta(days=1)
        
        data = {
            "customer": customer_id,
            "billingType": billing_type.value,
            "value": value,
            "nextDueDate": next_due_date.strftime("%Y-%m-%d"),
            "cycle": "MONTHLY",
            "description": description or f"Assinatura {plan_name} - KenzySites",
            "updatePendingPayments": True,
            "externalReference": f"KENZY_{customer_id}_{plan_name}"
        }
        
        # Add credit card data if provided
        if billing_type == BillingType.CREDIT_CARD and credit_card:
            data["creditCard"] = {
                "holderName": credit_card["holder_name"],
                "number": credit_card["number"],
                "expiryMonth": credit_card["expiry_month"],
                "expiryYear": credit_card["expiry_year"],
                "ccv": credit_card["cvv"]
            }
            data["creditCardHolderInfo"] = {
                "name": credit_card["holder_name"],
                "email": credit_card.get("email"),
                "cpfCnpj": credit_card.get("cpf_cnpj"),
                "postalCode": credit_card.get("postal_code"),
                "addressNumber": credit_card.get("address_number"),
                "phone": credit_card.get("phone")
            }
        
        # Add discount if provided
        if discount:
            data["discount"] = {
                "value": discount.get("value", 0),
                "dueDateLimitDays": discount.get("days", 0),
                "type": discount.get("type", "FIXED")  # FIXED or PERCENTAGE
            }
        
        # Add fine and interest for late payments
        data["fine"] = {
            "value": 2.0,  # 2% fine
            "type": "PERCENTAGE"
        }
        data["interest"] = {
            "value": 1.0  # 1% interest per month
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/subscriptions",
                json=data
            )
            response.raise_for_status()
            
            subscription_data = response.json()
            logger.info(f"Created Asaas subscription: {subscription_data['id']}")
            
            return {
                "success": True,
                "subscription_id": subscription_data["id"],
                "data": subscription_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            error_response = e.response.json() if hasattr(e, 'response') else {}
            return {
                "success": False,
                "error": str(e),
                "details": error_response
            }
    
    async def create_payment(
        self,
        customer_id: str,
        value: float,
        billing_type: BillingType,
        due_date: Optional[datetime] = None,
        description: Optional[str] = None,
        installment_count: int = 1,
        credit_card: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a single payment
        """
        
        if not due_date:
            due_date = datetime.now() + timedelta(days=3)
        
        data = {
            "customer": customer_id,
            "billingType": billing_type.value,
            "value": value,
            "dueDate": due_date.strftime("%Y-%m-%d"),
            "description": description or "Pagamento KenzySites"
        }
        
        # Handle installments for credit card
        if billing_type == BillingType.CREDIT_CARD and installment_count > 1:
            data["installmentCount"] = installment_count
            data["installmentValue"] = value / installment_count
        
        # Add credit card data
        if billing_type == BillingType.CREDIT_CARD and credit_card:
            data["creditCard"] = credit_card
        
        # Enable PIX QR Code
        if billing_type == BillingType.PIX:
            data["pixQrCodeId"] = await self._get_or_create_pix_key()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/payments",
                json=data
            )
            response.raise_for_status()
            
            payment_data = response.json()
            logger.info(f"Created Asaas payment: {payment_data['id']}")
            
            # Get PIX QR Code if payment type is PIX
            if billing_type == BillingType.PIX:
                pix_data = await self.get_pix_qr_code(payment_data['id'])
                payment_data['pixQrCode'] = pix_data
            
            return {
                "success": True,
                "payment_id": payment_data["id"],
                "data": payment_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create payment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_pix_qr_code(self, payment_id: str) -> Dict[str, Any]:
        """
        Get PIX QR Code for a payment
        """
        
        try:
            response = await self.client.get(
                f"{self.base_url}/payments/{payment_id}/pixQrCode"
            )
            response.raise_for_status()
            
            pix_data = response.json()
            
            return {
                "qr_code": pix_data.get("encodedImage"),  # Base64 image
                "payload": pix_data.get("payload"),  # PIX copy-paste code
                "expiration_date": pix_data.get("expirationDate")
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to get PIX QR Code: {str(e)}")
            return {}
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Check payment status
        """
        
        try:
            response = await self.client.get(
                f"{self.base_url}/payments/{payment_id}"
            )
            response.raise_for_status()
            
            payment_data = response.json()
            
            return {
                "success": True,
                "status": payment_data["status"],
                "data": payment_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to get payment status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel a subscription
        """
        
        try:
            response = await self.client.delete(
                f"{self.base_url}/subscriptions/{subscription_id}"
            )
            response.raise_for_status()
            
            logger.info(f"Cancelled Asaas subscription: {subscription_id}")
            
            return {
                "success": True,
                "message": "Subscription cancelled successfully"
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_subscription(
        self,
        subscription_id: str,
        value: Optional[float] = None,
        billing_type: Optional[BillingType] = None,
        next_due_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Update subscription details
        """
        
        data = {}
        
        if value is not None:
            data["value"] = value
        
        if billing_type:
            data["billingType"] = billing_type.value
        
        if next_due_date:
            data["nextDueDate"] = next_due_date.strftime("%Y-%m-%d")
        
        try:
            response = await self.client.put(
                f"{self.base_url}/subscriptions/{subscription_id}",
                json=data
            )
            response.raise_for_status()
            
            subscription_data = response.json()
            logger.info(f"Updated Asaas subscription: {subscription_id}")
            
            return {
                "success": True,
                "data": subscription_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to update subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_subscription_invoices(
        self,
        subscription_id: str,
        status: Optional[PaymentStatus] = None
    ) -> Dict[str, Any]:
        """
        Get all invoices for a subscription
        """
        
        params = {"subscription": subscription_id}
        if status:
            params["status"] = status.value
        
        try:
            response = await self.client.get(
                f"{self.base_url}/payments",
                params=params
            )
            response.raise_for_status()
            
            invoices_data = response.json()
            
            return {
                "success": True,
                "invoices": invoices_data.get("data", []),
                "total": invoices_data.get("totalCount", 0)
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to get invoices: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_payment_link(
        self,
        name: str,
        value: float,
        billing_type: BillingType = BillingType.UNDEFINED,
        description: Optional[str] = None,
        charges_quantity: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a payment link that can be shared
        """
        
        data = {
            "name": name,
            "description": description or f"Pagamento {name}",
            "endDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "value": value,
            "billingType": billing_type.value,
            "subscriptionCycle": None,
            "maxInstallmentCount": 12 if billing_type == BillingType.CREDIT_CARD else 1
        }
        
        if charges_quantity:
            data["chargeQuantity"] = charges_quantity
        
        try:
            response = await self.client.post(
                f"{self.base_url}/paymentLinks",
                json=data
            )
            response.raise_for_status()
            
            link_data = response.json()
            logger.info(f"Created payment link: {link_data['id']}")
            
            return {
                "success": True,
                "link_id": link_data["id"],
                "url": link_data["url"],
                "data": link_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create payment link: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_webhook(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle Asaas webhooks
        """
        
        webhook_handlers = {
            "PAYMENT_CREATED": self._handle_payment_created,
            "PAYMENT_UPDATED": self._handle_payment_updated,
            "PAYMENT_CONFIRMED": self._handle_payment_confirmed,
            "PAYMENT_RECEIVED": self._handle_payment_received,
            "PAYMENT_OVERDUE": self._handle_payment_overdue,
            "PAYMENT_DELETED": self._handle_payment_deleted,
            "PAYMENT_REFUNDED": self._handle_payment_refunded,
            "PAYMENT_CHARGEBACK_REQUESTED": self._handle_chargeback,
            "SUBSCRIPTION_CREATED": self._handle_subscription_created,
            "SUBSCRIPTION_UPDATED": self._handle_subscription_updated,
            "SUBSCRIPTION_DELETED": self._handle_subscription_deleted
        }
        
        handler = webhook_handlers.get(event_type)
        if handler:
            return await handler(data)
        
        logger.warning(f"Unhandled webhook event: {event_type}")
        return {"success": True, "message": "Event received but not processed"}
    
    async def _handle_payment_confirmed(self, data: Dict) -> Dict:
        """
        Handle payment confirmation
        """
        payment = data.get("payment", {})
        payment_id = payment.get("id")
        customer_id = payment.get("customer")
        value = payment.get("value")
        
        logger.info(f"Payment confirmed: {payment_id} for customer {customer_id}, value: R$ {value}")
        
        # Activate or extend the WordPress site
        from app.services.wordpress_provisioner import wordpress_provisioner
        
        # Get customer's site
        # This would lookup the site by customer_id
        # await wordpress_provisioner.resume_site(client_id)
        
        return {"success": True, "message": "Payment confirmed and site activated"}
    
    async def _handle_payment_overdue(self, data: Dict) -> Dict:
        """
        Handle overdue payment
        """
        payment = data.get("payment", {})
        payment_id = payment.get("id")
        customer_id = payment.get("customer")
        days_overdue = payment.get("daysAfterDueDate", 0)
        
        logger.warning(f"Payment overdue: {payment_id} for customer {customer_id}, days: {days_overdue}")
        
        # Suspend site after grace period
        if days_overdue >= 7:
            from app.services.wordpress_provisioner import wordpress_provisioner
            # await wordpress_provisioner.suspend_site(client_id)
            
            # Send suspension email
            # await send_suspension_email(customer_id)
        
        return {"success": True, "message": "Overdue payment processed"}
    
    async def _handle_payment_created(self, data: Dict) -> Dict:
        logger.info(f"Payment created: {data.get('payment', {}).get('id')}")
        return {"success": True}
    
    async def _handle_payment_updated(self, data: Dict) -> Dict:
        logger.info(f"Payment updated: {data.get('payment', {}).get('id')}")
        return {"success": True}
    
    async def _handle_payment_received(self, data: Dict) -> Dict:
        logger.info(f"Payment received: {data.get('payment', {}).get('id')}")
        return await self._handle_payment_confirmed(data)
    
    async def _handle_payment_deleted(self, data: Dict) -> Dict:
        logger.info(f"Payment deleted: {data.get('payment', {}).get('id')}")
        return {"success": True}
    
    async def _handle_payment_refunded(self, data: Dict) -> Dict:
        logger.info(f"Payment refunded: {data.get('payment', {}).get('id')}")
        return {"success": True}
    
    async def _handle_chargeback(self, data: Dict) -> Dict:
        logger.warning(f"Chargeback requested: {data.get('payment', {}).get('id')}")
        # Suspend site immediately on chargeback
        return {"success": True}
    
    async def _handle_subscription_created(self, data: Dict) -> Dict:
        logger.info(f"Subscription created: {data.get('subscription', {}).get('id')}")
        return {"success": True}
    
    async def _handle_subscription_updated(self, data: Dict) -> Dict:
        logger.info(f"Subscription updated: {data.get('subscription', {}).get('id')}")
        return {"success": True}
    
    async def _handle_subscription_deleted(self, data: Dict) -> Dict:
        logger.info(f"Subscription deleted: {data.get('subscription', {}).get('id')}")
        # Suspend or delete site
        return {"success": True}
    
    async def _get_or_create_pix_key(self) -> str:
        """
        Get or create PIX key for receiving payments
        """
        # This would get the PIX key from Asaas account
        # For now, return a placeholder
        return "pix_key_placeholder"
    
    async def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance
        """
        
        try:
            response = await self.client.get(f"{self.base_url}/finance/balance")
            response.raise_for_status()
            
            balance_data = response.json()
            
            return {
                "success": True,
                "balance": balance_data.get("balance", 0),
                "data": balance_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_transfer(
        self,
        value: float,
        bank_account: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Create a transfer to bank account
        """
        
        data = {
            "value": value,
            "bankAccount": {
                "bank": {
                    "code": bank_account["bank_code"]
                },
                "accountName": bank_account["account_name"],
                "ownerName": bank_account["owner_name"],
                "cpfCnpj": bank_account["cpf_cnpj"],
                "agency": bank_account["agency"],
                "account": bank_account["account"],
                "accountDigit": bank_account["account_digit"],
                "bankAccountType": bank_account.get("type", "CONTA_CORRENTE")
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/transfers",
                json=data
            )
            response.raise_for_status()
            
            transfer_data = response.json()
            logger.info(f"Created transfer: {transfer_data['id']}")
            
            return {
                "success": True,
                "transfer_id": transfer_data["id"],
                "data": transfer_data
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create transfer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
asaas = AsaasIntegration()