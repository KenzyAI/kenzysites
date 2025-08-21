"""
Customer Portal API endpoints
Self-service portal for customers to manage accounts and resources
Phase 2: Beta Público
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.services.customer_portal_service import (
    customer_portal_service,
    CustomerAccount,
    Resource,
    ResourceType,
    SupportTicket,
    SupportTicketStatus,
    SupportTicketPriority,
    Notification,
    NotificationType,
    ActivityLog
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication with request tracking
async def get_current_user(request: Request):
    return {
        "user_id": "user123",
        "email": "customer@example.com",
        "plan": "professional",
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }

# Account Management
@router.get("/account")
async def get_account_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user account information
    Returns complete account details and preferences
    """
    try:
        account = await customer_portal_service.get_account(current_user["user_id"])
        return account
        
    except Exception as e:
        logger.error(f"Failed to get account info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get account information: {str(e)}"
        )

@router.put("/account")
async def update_account_info(
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Update account information
    Allowed fields: name, company, phone, language, timezone, notifications
    """
    try:
        account = await customer_portal_service.update_account(
            user_id=current_user["user_id"],
            updates=updates
        )
        
        logger.info(f"Updated account for user {current_user['user_id']}")
        
        return {
            "success": True,
            "account": account,
            "message": "Account updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update account: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update account: {str(e)}"
        )

@router.get("/account/usage")
async def get_account_usage(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current resource usage and limits
    Shows sites, landing pages, AI credits, storage, bandwidth
    """
    try:
        usage = await customer_portal_service.get_account_usage(
            current_user["user_id"]
        )
        return usage
        
    except Exception as e:
        logger.error(f"Failed to get account usage: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get account usage: {str(e)}"
        )

# Dashboard
@router.get("/dashboard")
async def get_dashboard_data(
    current_user: dict = Depends(get_current_user)
):
    """
    Get complete dashboard data for customer portal
    Includes account, usage, resources, tickets, notifications
    """
    try:
        dashboard = await customer_portal_service.get_dashboard_data(
            current_user["user_id"]
        )
        return dashboard
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

# Resource Management
@router.get("/resources")
async def get_resources(
    resource_type: Optional[ResourceType] = Query(None, description="Filter by type"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all customer resources
    Includes sites, landing pages, domains, backups
    """
    try:
        resources = await customer_portal_service.get_resources(
            user_id=current_user["user_id"],
            resource_type=resource_type
        )
        
        return {
            "total": len(resources),
            "resources": resources
        }
        
    except Exception as e:
        logger.error(f"Failed to get resources: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resources: {str(e)}"
        )

@router.post("/resources")
async def create_resource(
    resource_type: ResourceType = Body(..., description="Type of resource"),
    name: str = Body(..., description="Resource name"),
    metadata: Optional[Dict[str, Any]] = Body(None, description="Additional metadata"),
    request: Request = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new resource"""
    try:
        # Log activity with IP
        await customer_portal_service.log_activity(
            user_id=current_user["user_id"],
            action="create_resource_attempt",
            resource_type=resource_type.value,
            ip_address=current_user.get("ip_address"),
            user_agent=current_user.get("user_agent")
        )
        
        resource = await customer_portal_service.create_resource(
            user_id=current_user["user_id"],
            resource_type=resource_type,
            name=name,
            metadata=metadata
        )
        
        return {
            "success": True,
            "resource": resource,
            "message": f"{resource_type.value} created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create resource: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create resource: {str(e)}"
        )

@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a resource"""
    try:
        success = await customer_portal_service.delete_resource(
            user_id=current_user["user_id"],
            resource_id=resource_id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Resource {resource_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Resource {resource_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resource: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete resource: {str(e)}"
        )

# Support Tickets
@router.post("/support/tickets")
async def create_support_ticket(
    subject: str = Body(..., description="Ticket subject"),
    description: str = Body(..., description="Issue description"),
    category: str = Body("general", description="Ticket category"),
    priority: Optional[SupportTicketPriority] = Body(None, description="Priority level"),
    attachments: Optional[List[str]] = Body(None, description="Attachment URLs"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new support ticket
    High/Urgent priority tickets are auto-assigned to senior support
    """
    try:
        ticket = await customer_portal_service.create_ticket(
            user_id=current_user["user_id"],
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            attachments=attachments
        )
        
        logger.info(f"Created support ticket {ticket.id} for user {current_user['user_id']}")
        
        return {
            "success": True,
            "ticket": ticket,
            "message": f"Ticket #{ticket.id} created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create support ticket: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create support ticket: {str(e)}"
        )

@router.get("/support/tickets")
async def get_support_tickets(
    status: Optional[SupportTicketStatus] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """Get all support tickets for current user"""
    try:
        tickets = await customer_portal_service.get_tickets(
            user_id=current_user["user_id"],
            status=status
        )
        
        return {
            "total": len(tickets),
            "tickets": tickets
        }
        
    except Exception as e:
        logger.error(f"Failed to get support tickets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get support tickets: {str(e)}"
        )

@router.post("/support/tickets/{ticket_id}/messages")
async def add_ticket_message(
    ticket_id: str,
    message: str = Body(..., description="Message content"),
    current_user: dict = Depends(get_current_user)
):
    """Add a message to a support ticket"""
    try:
        ticket = await customer_portal_service.add_ticket_message(
            user_id=current_user["user_id"],
            ticket_id=ticket_id,
            message=message,
            from_support=False
        )
        
        return {
            "success": True,
            "ticket": ticket,
            "message": "Message added successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add ticket message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add ticket message: {str(e)}"
        )

# Notifications
@router.get("/notifications")
async def get_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        notifications = await customer_portal_service.get_notifications(
            user_id=current_user["user_id"],
            unread_only=unread_only
        )
        
        return {
            "total": len(notifications),
            "unread": len([n for n in notifications if not n.read]),
            "notifications": notifications
        }
        
    except Exception as e:
        logger.error(f"Failed to get notifications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        success = await customer_portal_service.mark_notification_read(
            user_id=current_user["user_id"],
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Notification {notification_id} not found"
            )
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

# Activity Logs
@router.get("/activity")
async def get_activity_logs(
    limit: int = Query(100, le=1000, description="Maximum logs to return"),
    offset: int = Query(0, description="Pagination offset"),
    current_user: dict = Depends(get_current_user)
):
    """Get user activity logs"""
    try:
        logs = await customer_portal_service.get_activity_logs(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(logs),
            "limit": limit,
            "offset": offset,
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"Failed to get activity logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get activity logs: {str(e)}"
        )

# Billing
@router.get("/billing/history")
async def get_billing_history(
    limit: int = Query(12, description="Number of invoices to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get billing history and invoices"""
    try:
        history = await customer_portal_service.get_billing_history(
            user_id=current_user["user_id"],
            limit=limit
        )
        
        return {
            "total": len(history),
            "invoices": history
        }
        
    except Exception as e:
        logger.error(f"Failed to get billing history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get billing history: {str(e)}"
        )

@router.put("/billing/payment-method")
async def update_payment_method(
    payment_method: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update payment method"""
    try:
        # Log activity
        await customer_portal_service.log_activity(
            user_id=current_user["user_id"],
            action="payment_method_updated",
            metadata={"method": payment_method.get("type")},
            ip_address=current_user.get("ip_address"),
            user_agent=current_user.get("user_agent")
        )
        
        success = await customer_portal_service.update_payment_method(
            user_id=current_user["user_id"],
            payment_method=payment_method
        )
        
        return {
            "success": success,
            "message": "Payment method updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update payment method: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update payment method: {str(e)}"
        )

# Security
@router.get("/security")
async def get_security_settings(
    current_user: dict = Depends(get_current_user)
):
    """Get security settings and active sessions"""
    try:
        settings = await customer_portal_service.get_security_settings(
            current_user["user_id"]
        )
        return settings
        
    except Exception as e:
        logger.error(f"Failed to get security settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get security settings: {str(e)}"
        )

@router.post("/security/2fa/enable")
async def enable_two_factor(
    current_user: dict = Depends(get_current_user)
):
    """Enable two-factor authentication"""
    try:
        # Log security change
        await customer_portal_service.log_activity(
            user_id=current_user["user_id"],
            action="2fa_enabled",
            ip_address=current_user.get("ip_address"),
            user_agent=current_user.get("user_agent")
        )
        
        result = await customer_portal_service.enable_two_factor(
            current_user["user_id"]
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to enable 2FA: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enable 2FA: {str(e)}"
        )

# Quick Actions
@router.post("/quick-actions/change-plan")
async def change_plan(
    new_plan: str = Body(..., description="New plan to switch to"),
    current_user: dict = Depends(get_current_user)
):
    """Quick action to change subscription plan"""
    try:
        # Would integrate with billing service
        await customer_portal_service.create_notification(
            user_id=current_user["user_id"],
            type=NotificationType.BILLING,
            title="Plano Alterado",
            message=f"Seu plano foi alterado para {new_plan}.",
            action_url="/billing"
        )
        
        # Log activity
        await customer_portal_service.log_activity(
            user_id=current_user["user_id"],
            action="plan_changed",
            metadata={"new_plan": new_plan, "old_plan": current_user["plan"]},
            ip_address=current_user.get("ip_address"),
            user_agent=current_user.get("user_agent")
        )
        
        return {
            "success": True,
            "message": f"Plan changed to {new_plan} successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to change plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to change plan: {str(e)}"
        )

@router.post("/quick-actions/request-callback")
async def request_callback(
    phone: str = Body(..., description="Phone number for callback"),
    preferred_time: Optional[str] = Body(None, description="Preferred callback time"),
    current_user: dict = Depends(get_current_user)
):
    """Request a callback from support team"""
    try:
        # Create high priority ticket
        ticket = await customer_portal_service.create_ticket(
            user_id=current_user["user_id"],
            subject="Callback Request",
            description=f"Customer requested callback at {phone}. Preferred time: {preferred_time or 'ASAP'}",
            category="callback",
            priority=SupportTicketPriority.HIGH
        )
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "message": "Callback request submitted. We'll contact you soon."
        }
        
    except Exception as e:
        logger.error(f"Failed to request callback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to request callback: {str(e)}"
        )

# Help Center Integration
@router.get("/help/articles")
async def get_help_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query")
):
    """Get help center articles"""
    # Mock help articles
    articles = [
        {
            "id": "article_1",
            "title": "Como criar seu primeiro site com IA",
            "category": "getting-started",
            "views": 1542,
            "helpful": 89,
            "url": "/help/articles/article_1"
        },
        {
            "id": "article_2",
            "title": "Guia de otimização SEO",
            "category": "seo",
            "views": 987,
            "helpful": 78,
            "url": "/help/articles/article_2"
        },
        {
            "id": "article_3",
            "title": "Como usar o Landing Page Builder",
            "category": "features",
            "views": 2103,
            "helpful": 92,
            "url": "/help/articles/article_3"
        }
    ]
    
    if category:
        articles = [a for a in articles if a["category"] == category]
    
    if search:
        articles = [a for a in articles if search.lower() in a["title"].lower()]
    
    return {
        "total": len(articles),
        "articles": articles
    }

# Feedback
@router.post("/feedback")
async def submit_feedback(
    rating: int = Body(..., ge=1, le=10, description="NPS rating 1-10"),
    feedback: str = Body(..., description="Feedback text"),
    category: str = Body("general", description="Feedback category"),
    current_user: dict = Depends(get_current_user)
):
    """Submit customer feedback (NPS)"""
    try:
        # Create feedback ticket
        ticket = await customer_portal_service.create_ticket(
            user_id=current_user["user_id"],
            subject=f"Customer Feedback - NPS {rating}",
            description=feedback,
            category=f"feedback_{category}",
            priority=SupportTicketPriority.LOW if rating >= 7 else SupportTicketPriority.MEDIUM
        )
        
        # Thank you notification
        await customer_portal_service.create_notification(
            user_id=current_user["user_id"],
            type=NotificationType.SUCCESS,
            title="Obrigado pelo Feedback!",
            message="Sua opinião é muito importante para nós."
        )
        
        return {
            "success": True,
            "message": "Thank you for your feedback!"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )