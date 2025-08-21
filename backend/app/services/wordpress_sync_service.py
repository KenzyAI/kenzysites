"""
WordPress Master Synchronization Service
Handles real-time sync with WordPress Master instance via webhooks and scheduled tasks
"""

import asyncio
import logging
import json
import httpx
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import os
from dataclasses import dataclass
from enum import Enum

from app.services.template_repository import template_repository
from app.services.acf_integration import acf_service
from app.models.template_models import TemplateDefinition, BRAZILIAN_INDUSTRIES

logger = logging.getLogger(__name__)

class SyncEventType(str, Enum):
    """Types of sync events"""
    TEMPLATE_CREATED = "template_created"
    TEMPLATE_UPDATED = "template_updated"
    TEMPLATE_DELETED = "template_deleted"
    ACF_UPDATED = "acf_updated"
    MEDIA_UPDATED = "media_updated"
    FULL_SYNC = "full_sync"

@dataclass
class SyncEvent:
    """Represents a sync event"""
    event_type: SyncEventType
    template_id: Optional[str]
    data: Dict[str, Any]
    timestamp: datetime
    processed: bool = False
    retry_count: int = 0
    error_message: Optional[str] = None

class WordPressSyncService:
    """
    Service for synchronizing with WordPress Master instance
    Supports webhooks, scheduled sync, and real-time updates
    """
    
    def __init__(self):
        self.wordpress_master_url = os.getenv('WORDPRESS_MASTER_URL', 'https://master.kenzysites.com')
        self.webhook_secret = os.getenv('WP_WEBHOOK_SECRET', 'your-secret-key')
        self.sync_interval = int(os.getenv('SYNC_INTERVAL_MINUTES', '30'))  # Default 30 minutes
        self.max_retries = int(os.getenv('SYNC_MAX_RETRIES', '3'))
        
        # Event queue for processing sync events
        self.event_queue: List[SyncEvent] = []
        self.webhook_handlers: Dict[str, Callable] = {}
        self.is_running = False
        self.last_full_sync = None
        
        # Register webhook handlers
        self._register_webhook_handlers()
    
    def _register_webhook_handlers(self):
        """Register webhook event handlers"""
        self.webhook_handlers = {
            "post_updated": self._handle_template_updated,
            "post_created": self._handle_template_created,
            "post_deleted": self._handle_template_deleted,
            "acf_updated": self._handle_acf_updated,
            "media_updated": self._handle_media_updated
        }
    
    async def start_sync_service(self):
        """Start the background sync service"""
        if self.is_running:
            logger.warning("Sync service is already running")
            return
        
        self.is_running = True
        logger.info("Starting WordPress sync service")
        
        # Start background tasks
        asyncio.create_task(self._process_event_queue())
        asyncio.create_task(self._scheduled_sync_task())
        
        # Initial full sync if needed
        if not self.last_full_sync or (datetime.now() - self.last_full_sync) > timedelta(hours=24):
            await self.queue_full_sync()
    
    async def stop_sync_service(self):
        """Stop the background sync service"""
        self.is_running = False
        logger.info("WordPress sync service stopped")
    
    async def _process_event_queue(self):
        """Process sync events from the queue"""
        while self.is_running:
            try:
                if self.event_queue:
                    event = self.event_queue.pop(0)
                    await self._process_sync_event(event)
                else:
                    await asyncio.sleep(1)  # Wait if queue is empty
                    
            except Exception as e:
                logger.error(f"Error processing event queue: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _scheduled_sync_task(self):
        """Periodic sync task"""
        while self.is_running:
            try:
                await asyncio.sleep(self.sync_interval * 60)  # Convert to seconds
                await self.queue_incremental_sync()
                
            except Exception as e:
                logger.error(f"Error in scheduled sync: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _process_sync_event(self, event: SyncEvent):
        """Process a single sync event"""
        try:
            logger.info(f"Processing sync event: {event.event_type} for template {event.template_id}")
            
            if event.event_type == SyncEventType.TEMPLATE_CREATED:
                await self._sync_template_created(event.data)
            elif event.event_type == SyncEventType.TEMPLATE_UPDATED:
                await self._sync_template_updated(event.data)
            elif event.event_type == SyncEventType.TEMPLATE_DELETED:
                await self._sync_template_deleted(event.template_id)
            elif event.event_type == SyncEventType.ACF_UPDATED:
                await self._sync_acf_updated(event.template_id, event.data)
            elif event.event_type == SyncEventType.MEDIA_UPDATED:
                await self._sync_media_updated(event.template_id, event.data)
            elif event.event_type == SyncEventType.FULL_SYNC:
                await self._perform_full_sync()
            
            event.processed = True
            logger.info(f"Successfully processed sync event: {event.event_type}")
            
        except Exception as e:
            event.retry_count += 1
            event.error_message = str(e)
            
            if event.retry_count < self.max_retries:
                logger.warning(f"Event processing failed, retrying ({event.retry_count}/{self.max_retries}): {str(e)}")
                # Re-queue for retry
                self.event_queue.append(event)
            else:
                logger.error(f"Event processing failed after {self.max_retries} retries: {str(e)}")
    
    async def _sync_template_created(self, template_data: Dict[str, Any]):
        """Sync a newly created template"""
        try:
            # Fetch full template data from WordPress
            full_data = await self._fetch_template_from_wordpress(template_data['id'])
            
            if full_data:
                template = await self._process_wordpress_template(full_data)
                success = await template_repository.create_template(template)
                
                if success:
                    logger.info(f"Template created: {template.id}")
                else:
                    raise Exception("Failed to create template in repository")
                    
        except Exception as e:
            logger.error(f"Error syncing created template: {str(e)}")
            raise
    
    async def _sync_template_updated(self, template_data: Dict[str, Any]):
        """Sync an updated template"""
        try:
            # Fetch full template data from WordPress
            full_data = await self._fetch_template_from_wordpress(template_data['id'])
            
            if full_data:
                template = await self._process_wordpress_template(full_data)
                success = await template_repository.update_template(template)
                
                if success:
                    logger.info(f"Template updated: {template.id}")
                else:
                    raise Exception("Failed to update template in repository")
                    
        except Exception as e:
            logger.error(f"Error syncing updated template: {str(e)}")
            raise
    
    async def _sync_template_deleted(self, template_id: str):
        """Sync a deleted template"""
        try:
            wp_template_id = f"wp_{template_id}"
            success = await template_repository.delete_template(wp_template_id)
            
            if success:
                logger.info(f"Template deleted: {wp_template_id}")
            else:
                logger.warning(f"Template not found for deletion: {wp_template_id}")
                
        except Exception as e:
            logger.error(f"Error syncing deleted template: {str(e)}")
            raise
    
    async def _sync_acf_updated(self, template_id: str, acf_data: Dict[str, Any]):
        """Sync updated ACF fields"""
        try:
            wp_template_id = f"wp_{template_id}"
            template = await template_repository.get_template(wp_template_id)
            
            if template:
                # Regenerate ACF fields based on updated data
                field_groups = acf_service.create_template_fields_for_industry(
                    template.industry
                )
                template.acf_field_groups = field_groups
                
                success = await template_repository.update_template(template)
                
                if success:
                    logger.info(f"ACF fields updated for template: {wp_template_id}")
                else:
                    raise Exception("Failed to update ACF fields")
            else:
                logger.warning(f"Template not found for ACF update: {wp_template_id}")
                
        except Exception as e:
            logger.error(f"Error syncing ACF update: {str(e)}")
            raise
    
    async def _sync_media_updated(self, template_id: str, media_data: Dict[str, Any]):
        """Sync updated media (thumbnails, previews)"""
        try:
            wp_template_id = f"wp_{template_id}"
            template = await template_repository.get_template(wp_template_id)
            
            if template:
                # Update media URLs
                if 'thumbnail' in media_data:
                    template.thumbnail = media_data['thumbnail']
                if 'preview_url' in media_data:
                    template.preview_url = media_data['preview_url']
                
                success = await template_repository.update_template(template)
                
                if success:
                    logger.info(f"Media updated for template: {wp_template_id}")
                else:
                    raise Exception("Failed to update media")
            else:
                logger.warning(f"Template not found for media update: {wp_template_id}")
                
        except Exception as e:
            logger.error(f"Error syncing media update: {str(e)}")
            raise
    
    async def _perform_full_sync(self):
        """Perform a full synchronization"""
        try:
            logger.info("Starting full sync with WordPress Master")
            result = await template_repository.sync_with_wordpress_master()
            
            self.last_full_sync = datetime.now()
            
            logger.info(f"Full sync completed: {result}")
            
        except Exception as e:
            logger.error(f"Error during full sync: {str(e)}")
            raise
    
    async def _fetch_template_from_wordpress(self, wp_template_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single template from WordPress Master"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Authenticate
                auth_response = await client.post(
                    f"{self.wordpress_master_url}/wp-json/jwt-auth/v1/token",
                    json={
                        "username": os.getenv('WP_MASTER_USER'),
                        "password": os.getenv('WP_MASTER_PASSWORD')
                    }
                )
                
                if auth_response.status_code != 200:
                    raise Exception("Failed to authenticate with WordPress Master")
                
                token = auth_response.json().get('token')
                headers = {"Authorization": f"Bearer {token}"}
                
                # Fetch template
                template_response = await client.get(
                    f"{self.wordpress_master_url}/wp-json/wp/v2/kz_template/{wp_template_id}",
                    headers=headers
                )
                
                if template_response.status_code == 200:
                    template_data = template_response.json()
                    
                    # Get ACF data
                    acf_response = await client.get(
                        f"{self.wordpress_master_url}/wp-json/acf/v3/posts/{wp_template_id}",
                        headers=headers
                    )
                    
                    if acf_response.status_code == 200:
                        template_data['acf_data'] = acf_response.json()
                    
                    return template_data
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching template {wp_template_id}: {str(e)}")
            return None
    
    async def _process_wordpress_template(self, wp_template: Dict[str, Any]) -> TemplateDefinition:
        """Process WordPress template data into our format"""
        template_id = f"wp_{wp_template['id']}"
        acf_data = wp_template.get('acf_data', {})
        
        template = TemplateDefinition(
            id=template_id,
            name=wp_template['title']['rendered'],
            description=wp_template['excerpt']['rendered'] or wp_template['content']['rendered'][:200],
            category=acf_data.get('template_category', 'general'),
            industry=acf_data.get('template_industry', 'generic'),
            style=acf_data.get('template_style', 'modern'),
            preview_url=acf_data.get('preview_url', ''),
            thumbnail=acf_data.get('thumbnail_url', ''),
            features=acf_data.get('features', []),
            is_premium=acf_data.get('is_premium', False),
            tags=acf_data.get('tags', [])
        )
        
        # Generate ACF field groups
        if template.industry in BRAZILIAN_INDUSTRIES:
            field_groups = acf_service.create_template_fields_for_industry(template.industry)
            template.acf_field_groups = field_groups
        
        return template
    
    # Webhook handling methods
    
    async def _handle_template_created(self, webhook_data: Dict[str, Any]):
        """Handle template created webhook"""
        event = SyncEvent(
            event_type=SyncEventType.TEMPLATE_CREATED,
            template_id=str(webhook_data.get('post_id')),
            data=webhook_data,
            timestamp=datetime.now()
        )
        self.event_queue.append(event)
        logger.info(f"Queued template created event: {event.template_id}")
    
    async def _handle_template_updated(self, webhook_data: Dict[str, Any]):
        """Handle template updated webhook"""
        event = SyncEvent(
            event_type=SyncEventType.TEMPLATE_UPDATED,
            template_id=str(webhook_data.get('post_id')),
            data=webhook_data,
            timestamp=datetime.now()
        )
        self.event_queue.append(event)
        logger.info(f"Queued template updated event: {event.template_id}")
    
    async def _handle_template_deleted(self, webhook_data: Dict[str, Any]):
        """Handle template deleted webhook"""
        event = SyncEvent(
            event_type=SyncEventType.TEMPLATE_DELETED,
            template_id=str(webhook_data.get('post_id')),
            data=webhook_data,
            timestamp=datetime.now()
        )
        self.event_queue.append(event)
        logger.info(f"Queued template deleted event: {event.template_id}")
    
    async def _handle_acf_updated(self, webhook_data: Dict[str, Any]):
        """Handle ACF updated webhook"""
        event = SyncEvent(
            event_type=SyncEventType.ACF_UPDATED,
            template_id=str(webhook_data.get('post_id')),
            data=webhook_data,
            timestamp=datetime.now()
        )
        self.event_queue.append(event)
        logger.info(f"Queued ACF updated event: {event.template_id}")
    
    async def _handle_media_updated(self, webhook_data: Dict[str, Any]):
        """Handle media updated webhook"""
        event = SyncEvent(
            event_type=SyncEventType.MEDIA_UPDATED,
            template_id=str(webhook_data.get('post_id')),
            data=webhook_data,
            timestamp=datetime.now()
        )
        self.event_queue.append(event)
        logger.info(f"Queued media updated event: {event.template_id}")
    
    # Public API methods
    
    async def handle_webhook(self, event_type: str, data: Dict[str, Any], signature: str = None) -> bool:
        """
        Handle incoming webhook from WordPress Master
        """
        try:
            # Verify webhook signature if provided
            if signature and not self._verify_webhook_signature(data, signature):
                logger.warning("Invalid webhook signature")
                return False
            
            # Get handler for event type
            handler = self.webhook_handlers.get(event_type)
            if not handler:
                logger.warning(f"No handler for webhook event: {event_type}")
                return False
            
            # Process webhook
            await handler(data)
            logger.info(f"Processed webhook: {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling webhook {event_type}: {str(e)}")
            return False
    
    def _verify_webhook_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """Verify webhook signature"""
        try:
            payload = json.dumps(data, sort_keys=True)
            expected_signature = hashlib.sha256(
                (self.webhook_secret + payload).encode()
            ).hexdigest()
            
            return signature == expected_signature
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False
    
    async def queue_full_sync(self):
        """Queue a full synchronization"""
        event = SyncEvent(
            event_type=SyncEventType.FULL_SYNC,
            template_id=None,
            data={},
            timestamp=datetime.now()
        )
        self.event_queue.append(event)
        logger.info("Queued full sync event")
    
    async def queue_incremental_sync(self):
        """Queue incremental sync (only changed templates)"""
        try:
            # Get templates modified since last sync
            since = self.last_full_sync or (datetime.now() - timedelta(hours=24))
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Authenticate
                auth_response = await client.post(
                    f"{self.wordpress_master_url}/wp-json/jwt-auth/v1/token",
                    json={
                        "username": os.getenv('WP_MASTER_USER'),
                        "password": os.getenv('WP_MASTER_PASSWORD')
                    }
                )
                
                if auth_response.status_code != 200:
                    raise Exception("Failed to authenticate for incremental sync")
                
                token = auth_response.json().get('token')
                headers = {"Authorization": f"Bearer {token}"}
                
                # Get modified templates
                modified_response = await client.get(
                    f"{self.wordpress_master_url}/wp-json/wp/v2/kz_template",
                    headers=headers,
                    params={
                        "modified_after": since.isoformat(),
                        "per_page": 100
                    }
                )
                
                if modified_response.status_code == 200:
                    modified_templates = modified_response.json()
                    
                    for template_data in modified_templates:
                        event = SyncEvent(
                            event_type=SyncEventType.TEMPLATE_UPDATED,
                            template_id=str(template_data['id']),
                            data=template_data,
                            timestamp=datetime.now()
                        )
                        self.event_queue.append(event)
                    
                    logger.info(f"Queued {len(modified_templates)} templates for incremental sync")
                    
        except Exception as e:
            logger.error(f"Error queuing incremental sync: {str(e)}")
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync service status"""
        return {
            "is_running": self.is_running,
            "last_full_sync": self.last_full_sync.isoformat() if self.last_full_sync else None,
            "queue_size": len(self.event_queue),
            "pending_events": [
                {
                    "event_type": event.event_type.value,
                    "template_id": event.template_id,
                    "timestamp": event.timestamp.isoformat(),
                    "retry_count": event.retry_count,
                    "processed": event.processed
                }
                for event in self.event_queue[:10]  # Show only first 10
            ],
            "sync_interval_minutes": self.sync_interval,
            "max_retries": self.max_retries
        }

# Global instance
wordpress_sync_service = WordPressSyncService()