"""
Customer Portal Service
Implements self-service customer portal for account management
Phase 2: Beta Público
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import uuid

logger = logging.getLogger(__name__)

# Data Models
class AccountStatus(str, Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELED = "canceled"
    EXPIRED = "expired"

class ResourceType(str, Enum):
    SITE = "site"
    LANDING_PAGE = "landing_page"
    DOMAIN = "domain"
    BACKUP = "backup"
    TEMPLATE = "template"

class SupportTicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class SupportTicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    BILLING = "billing"
    SYSTEM = "system"

# Customer Account Model
class CustomerAccount(BaseModel):
    """Customer account information"""
    user_id: str
    email: str
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    status: AccountStatus = AccountStatus.ACTIVE
    plan: str = "starter"
    trial_ends_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Billing info
    customer_id: Optional[str] = None  # Asaas/Stripe ID
    payment_method: Optional[str] = None
    next_billing_date: Optional[datetime] = None
    
    # Preferences
    language: str = "pt-BR"
    timezone: str = "America/Sao_Paulo"
    email_notifications: bool = True
    sms_notifications: bool = False
    
    # Limits based on plan
    sites_limit: int = 1
    landing_pages_limit: int = 3
    ai_credits_limit: int = 1000
    storage_limit_gb: int = 10
    bandwidth_limit_gb: int = 100

# Resource Model
class Resource(BaseModel):
    """Customer resource (site, landing page, etc)"""
    id: str = Field(default_factory=lambda: f"res_{uuid.uuid4().hex[:8]}")
    user_id: str
    type: ResourceType
    name: str
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Usage metrics
    views: int = 0
    storage_mb: float = 0
    bandwidth_mb: float = 0

# Support Ticket Model
class SupportTicket(BaseModel):
    """Support ticket for customer issues"""
    id: str = Field(default_factory=lambda: f"ticket_{uuid.uuid4().hex[:8]}")
    user_id: str
    subject: str
    description: str
    status: SupportTicketStatus = SupportTicketStatus.OPEN
    priority: SupportTicketPriority = SupportTicketPriority.MEDIUM
    category: str = "general"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    # Support interaction
    assigned_to: Optional[str] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)

# Notification Model
class Notification(BaseModel):
    """User notification"""
    id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:8]}")
    user_id: str
    type: NotificationType
    title: str
    message: str
    read: bool = False
    action_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

# Activity Log Model
class ActivityLog(BaseModel):
    """User activity log entry"""
    id: str = Field(default_factory=lambda: f"log_{uuid.uuid4().hex[:8]}")
    user_id: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class CustomerPortalService:
    """Service for managing customer portal features"""
    
    def __init__(self):
        self.accounts: Dict[str, CustomerAccount] = {}
        self.resources: Dict[str, List[Resource]] = {}
        self.tickets: Dict[str, List[SupportTicket]] = {}
        self.notifications: Dict[str, List[Notification]] = {}
        self.activity_logs: Dict[str, List[ActivityLog]] = {}
        
        # Initialize with mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with sample customer data"""
        # Sample customer account
        account = CustomerAccount(
            user_id="user123",
            email="customer@example.com",
            name="João Silva",
            company="Silva Tech",
            plan="professional",
            sites_limit=5,
            landing_pages_limit=15,
            ai_credits_limit=5000,
            storage_limit_gb=50,
            bandwidth_limit_gb=500
        )
        self.accounts[account.user_id] = account
        
        # Sample resources
        self.resources["user123"] = [
            Resource(
                user_id="user123",
                type=ResourceType.SITE,
                name="Site Principal",
                metadata={"url": "https://example.com", "wordpress_id": "wp_123"},
                views=15234,
                storage_mb=245.5,
                bandwidth_mb=1250.8
            ),
            Resource(
                user_id="user123",
                type=ResourceType.LANDING_PAGE,
                name="Black Friday 2025",
                metadata={"url": "https://promo.example.com"},
                views=8456,
                storage_mb=12.3,
                bandwidth_mb=456.2
            )
        ]
        
        # Sample notifications
        self.notifications["user123"] = [
            Notification(
                user_id="user123",
                type=NotificationType.SUCCESS,
                title="Site Publicado com Sucesso",
                message="Seu site 'Site Principal' foi publicado com sucesso.",
                action_url="/sites/site_123"
            ),
            Notification(
                user_id="user123",
                type=NotificationType.BILLING,
                title="Fatura Disponível",
                message="Sua fatura de R$ 297,00 está disponível para pagamento.",
                action_url="/billing/invoices"
            )
        ]
    
    # Account Management
    async def get_account(self, user_id: str) -> CustomerAccount:
        """Get customer account details"""
        account = self.accounts.get(user_id)
        if not account:
            raise ValueError(f"Account not found for user {user_id}")
        return account
    
    async def update_account(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> CustomerAccount:
        """Update customer account information"""
        account = await self.get_account(user_id)
        
        # Update allowed fields
        allowed_fields = ["name", "company", "phone", "language", "timezone", 
                         "email_notifications", "sms_notifications"]
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(account, field, value)
        
        account.updated_at = datetime.now()
        
        # Log activity
        await self.log_activity(
            user_id=user_id,
            action="account_updated",
            metadata={"updates": updates}
        )
        
        logger.info(f"Updated account for user {user_id}")
        return account
    
    async def get_account_usage(self, user_id: str) -> Dict[str, Any]:
        """Get current usage statistics for account"""
        account = await self.get_account(user_id)
        resources = self.resources.get(user_id, [])
        
        # Calculate usage
        total_sites = len([r for r in resources if r.type == ResourceType.SITE])
        total_landing_pages = len([r for r in resources if r.type == ResourceType.LANDING_PAGE])
        total_storage_mb = sum(r.storage_mb for r in resources)
        total_bandwidth_mb = sum(r.bandwidth_mb for r in resources)
        
        # AI Credits usage (mock)
        ai_credits_used = 2340  # Would query from AI service
        
        return {
            "sites": {
                "used": total_sites,
                "limit": account.sites_limit,
                "percentage": (total_sites / account.sites_limit * 100) if account.sites_limit > 0 else 0
            },
            "landing_pages": {
                "used": total_landing_pages,
                "limit": account.landing_pages_limit,
                "percentage": (total_landing_pages / account.landing_pages_limit * 100) if account.landing_pages_limit > 0 else 0
            },
            "ai_credits": {
                "used": ai_credits_used,
                "limit": account.ai_credits_limit,
                "percentage": (ai_credits_used / account.ai_credits_limit * 100) if account.ai_credits_limit > 0 else 0
            },
            "storage": {
                "used_gb": total_storage_mb / 1024,
                "limit_gb": account.storage_limit_gb,
                "percentage": (total_storage_mb / 1024 / account.storage_limit_gb * 100) if account.storage_limit_gb > 0 else 0
            },
            "bandwidth": {
                "used_gb": total_bandwidth_mb / 1024,
                "limit_gb": account.bandwidth_limit_gb,
                "percentage": (total_bandwidth_mb / 1024 / account.bandwidth_limit_gb * 100) if account.bandwidth_limit_gb > 0 else 0
            }
        }
    
    # Resource Management
    async def get_resources(
        self,
        user_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> List[Resource]:
        """Get customer resources"""
        resources = self.resources.get(user_id, [])
        
        if resource_type:
            resources = [r for r in resources if r.type == resource_type]
        
        return resources
    
    async def create_resource(
        self,
        user_id: str,
        resource_type: ResourceType,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Resource:
        """Create a new resource"""
        resource = Resource(
            user_id=user_id,
            type=resource_type,
            name=name,
            metadata=metadata or {}
        )
        
        if user_id not in self.resources:
            self.resources[user_id] = []
        
        self.resources[user_id].append(resource)
        
        # Log activity
        await self.log_activity(
            user_id=user_id,
            action="resource_created",
            resource_type=resource_type.value,
            resource_id=resource.id
        )
        
        # Send notification
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.SUCCESS,
            title=f"{resource_type.value.replace('_', ' ').title()} Criado",
            message=f"'{name}' foi criado com sucesso.",
            action_url=f"/resources/{resource.id}"
        )
        
        logger.info(f"Created resource {resource.id} for user {user_id}")
        return resource
    
    async def delete_resource(self, user_id: str, resource_id: str) -> bool:
        """Delete a resource"""
        resources = self.resources.get(user_id, [])
        
        for i, resource in enumerate(resources):
            if resource.id == resource_id:
                del resources[i]
                
                # Log activity
                await self.log_activity(
                    user_id=user_id,
                    action="resource_deleted",
                    resource_id=resource_id
                )
                
                logger.info(f"Deleted resource {resource_id} for user {user_id}")
                return True
        
        return False
    
    # Support Tickets
    async def create_ticket(
        self,
        user_id: str,
        subject: str,
        description: str,
        category: str = "general",
        priority: Optional[SupportTicketPriority] = None,
        attachments: Optional[List[str]] = None
    ) -> SupportTicket:
        """Create a support ticket"""
        ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            description=description,
            category=category,
            priority=priority or SupportTicketPriority.MEDIUM,
            attachments=attachments or []
        )
        
        if user_id not in self.tickets:
            self.tickets[user_id] = []
        
        self.tickets[user_id].append(ticket)
        
        # Auto-assign based on priority
        if ticket.priority in [SupportTicketPriority.HIGH, SupportTicketPriority.URGENT]:
            ticket.assigned_to = "senior_support"
        
        # Send notification
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.INFO,
            title="Ticket de Suporte Criado",
            message=f"Ticket #{ticket.id} foi criado. Responderemos em breve.",
            action_url=f"/support/tickets/{ticket.id}"
        )
        
        logger.info(f"Created support ticket {ticket.id} for user {user_id}")
        return ticket
    
    async def get_tickets(
        self,
        user_id: str,
        status: Optional[SupportTicketStatus] = None
    ) -> List[SupportTicket]:
        """Get user support tickets"""
        tickets = self.tickets.get(user_id, [])
        
        if status:
            tickets = [t for t in tickets if t.status == status]
        
        return tickets
    
    async def add_ticket_message(
        self,
        user_id: str,
        ticket_id: str,
        message: str,
        from_support: bool = False
    ) -> SupportTicket:
        """Add message to support ticket"""
        tickets = self.tickets.get(user_id, [])
        
        for ticket in tickets:
            if ticket.id == ticket_id:
                ticket.messages.append({
                    "id": f"msg_{uuid.uuid4().hex[:8]}",
                    "message": message,
                    "from_support": from_support,
                    "timestamp": datetime.now().isoformat()
                })
                
                ticket.updated_at = datetime.now()
                
                if from_support:
                    # Notify user of support response
                    await self.create_notification(
                        user_id=user_id,
                        type=NotificationType.INFO,
                        title="Resposta do Suporte",
                        message=f"Você recebeu uma resposta no ticket #{ticket_id}",
                        action_url=f"/support/tickets/{ticket_id}"
                    )
                
                logger.info(f"Added message to ticket {ticket_id}")
                return ticket
        
        raise ValueError(f"Ticket {ticket_id} not found")
    
    # Notifications
    async def create_notification(
        self,
        user_id: str,
        type: NotificationType,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        expires_in_days: Optional[int] = None
    ) -> Notification:
        """Create a notification for user"""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            action_url=action_url
        )
        
        if expires_in_days:
            notification.expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        self.notifications[user_id].append(notification)
        
        logger.info(f"Created notification for user {user_id}: {title}")
        return notification
    
    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get user notifications"""
        notifications = self.notifications.get(user_id, [])
        
        # Filter expired
        now = datetime.now()
        notifications = [
            n for n in notifications 
            if not n.expires_at or n.expires_at > now
        ]
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        # Sort by date, newest first
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        return notifications
    
    async def mark_notification_read(
        self,
        user_id: str,
        notification_id: str
    ) -> bool:
        """Mark notification as read"""
        notifications = self.notifications.get(user_id, [])
        
        for notification in notifications:
            if notification.id == notification_id:
                notification.read = True
                logger.info(f"Marked notification {notification_id} as read")
                return True
        
        return False
    
    # Activity Logging
    async def log_activity(
        self,
        user_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log user activity"""
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if user_id not in self.activity_logs:
            self.activity_logs[user_id] = []
        
        self.activity_logs[user_id].append(log_entry)
        
        # Keep only last 1000 entries per user
        if len(self.activity_logs[user_id]) > 1000:
            self.activity_logs[user_id] = self.activity_logs[user_id][-1000:]
        
        logger.debug(f"Logged activity for user {user_id}: {action}")
    
    async def get_activity_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get user activity logs"""
        logs = self.activity_logs.get(user_id, [])
        
        # Sort by timestamp, newest first
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        return logs[offset:offset + limit]
    
    # Dashboard Data
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get complete dashboard data for customer portal"""
        account = await self.get_account(user_id)
        usage = await self.get_account_usage(user_id)
        resources = await self.get_resources(user_id)
        recent_tickets = await self.get_tickets(user_id)
        notifications = await self.get_notifications(user_id, unread_only=True)
        recent_activity = await self.get_activity_logs(user_id, limit=10)
        
        # Calculate quick stats
        total_views = sum(r.views for r in resources)
        active_resources = len([r for r in resources if r.status == "active"])
        open_tickets = len([t for t in recent_tickets if t.status in [SupportTicketStatus.OPEN, SupportTicketStatus.IN_PROGRESS]])
        
        return {
            "account": account,
            "usage": usage,
            "quick_stats": {
                "total_views": total_views,
                "active_resources": active_resources,
                "open_tickets": open_tickets,
                "unread_notifications": len(notifications)
            },
            "resources": resources[:5],  # Last 5 resources
            "recent_tickets": recent_tickets[:3],  # Last 3 tickets
            "notifications": notifications[:5],  # Last 5 unread
            "recent_activity": recent_activity,
            "billing_summary": {
                "current_plan": account.plan,
                "next_billing_date": account.next_billing_date,
                "payment_method": account.payment_method,
                "amount_due": 297.00 if account.plan == "professional" else 97.00
            }
        }
    
    # Billing Integration
    async def get_billing_history(
        self,
        user_id: str,
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Get billing history"""
        # Mock billing history
        return [
            {
                "id": f"inv_{i}",
                "date": (datetime.now() - timedelta(days=30*i)).isoformat(),
                "amount": 297.00,
                "status": "paid",
                "payment_method": "pix",
                "download_url": f"/billing/invoices/inv_{i}/download"
            }
            for i in range(min(limit, 6))
        ]
    
    async def update_payment_method(
        self,
        user_id: str,
        payment_method: Dict[str, Any]
    ) -> bool:
        """Update payment method"""
        account = await self.get_account(user_id)
        
        # Would integrate with Asaas/Stripe here
        account.payment_method = payment_method.get("type", "credit_card")
        
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.BILLING,
            title="Método de Pagamento Atualizado",
            message="Seu método de pagamento foi atualizado com sucesso."
        )
        
        logger.info(f"Updated payment method for user {user_id}")
        return True
    
    # Security
    async def get_security_settings(self, user_id: str) -> Dict[str, Any]:
        """Get security settings"""
        return {
            "two_factor_enabled": False,
            "api_keys": [
                {
                    "id": "key_1",
                    "name": "Production API Key",
                    "last_used": datetime.now().isoformat(),
                    "created_at": (datetime.now() - timedelta(days=30)).isoformat()
                }
            ],
            "sessions": [
                {
                    "id": "session_1",
                    "device": "Chrome on Windows",
                    "ip_address": "192.168.1.1",
                    "location": "São Paulo, Brazil",
                    "last_active": datetime.now().isoformat()
                }
            ]
        }
    
    async def enable_two_factor(self, user_id: str) -> Dict[str, Any]:
        """Enable two-factor authentication"""
        # Would implement 2FA setup here
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.SECURITY,
            title="Autenticação de Dois Fatores Ativada",
            message="Sua conta está agora mais segura com 2FA."
        )
        
        return {
            "success": True,
            "qr_code": "data:image/png;base64,...",  # Mock QR code
            "backup_codes": ["ABC123", "DEF456", "GHI789"]
        }

# Global instance
customer_portal_service = CustomerPortalService()