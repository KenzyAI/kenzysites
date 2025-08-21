"""
Template Repository Service
Manages centralized template storage and synchronization with WordPress Master
"""

import json
import logging
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import os

from app.models.template_models import (
    TemplateDefinition, ACFFieldGroup, ACFField, BRAZILIAN_INDUSTRIES
)
from app.services.acf_integration import acf_service

logger = logging.getLogger(__name__)

class TemplateRepository:
    """
    Service for managing WordPress templates in a centralized repository
    """
    
    def __init__(self):
        self.wordpress_master_url = os.getenv('WORDPRESS_MASTER_URL', 'https://master.kenzysites.com')
        self.wp_admin_user = os.getenv('WP_MASTER_USER', 'admin')
        self.wp_admin_password = os.getenv('WP_MASTER_PASSWORD', '')
        self.templates_cache = {}
        self.cache_ttl = timedelta(hours=2)  # Cache for 2 hours
        self.local_repository_path = Path("/app/templates_repository")
        self.local_repository_path.mkdir(exist_ok=True)
        
    async def initialize_repository(self) -> None:
        """Initialize the template repository"""
        try:
            # Create local directories
            (self.local_repository_path / "templates").mkdir(exist_ok=True)
            (self.local_repository_path / "acf_exports").mkdir(exist_ok=True)
            (self.local_repository_path / "assets").mkdir(exist_ok=True)
            
            # Load templates from local storage
            await self._load_local_templates()
            
            logger.info("Template repository initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize template repository: {str(e)}")
    
    async def sync_with_wordpress_master(self) -> Dict[str, Any]:
        """
        Sync templates from WordPress Master instance
        """
        try:
            # Get list of templates from WordPress Master
            templates_data = await self._fetch_wordpress_templates()
            
            synced_count = 0
            failed_count = 0
            
            for template_data in templates_data:
                try:
                    # Process and store template
                    template = await self._process_wordpress_template(template_data)
                    await self._store_template_locally(template)
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync template {template_data.get('id', 'unknown')}: {str(e)}")
                    failed_count += 1
            
            # Update cache
            self._update_templates_cache()
            
            result = {
                "synced_templates": synced_count,
                "failed_templates": failed_count,
                "last_sync": datetime.now().isoformat(),
                "total_templates": len(self.templates_cache)
            }
            
            logger.info(f"Template sync completed: {synced_count} synced, {failed_count} failed")
            return result
            
        except Exception as e:
            logger.error(f"Template sync failed: {str(e)}")
            return {
                "error": str(e),
                "synced_templates": 0,
                "failed_templates": 0
            }
    
    async def _fetch_wordpress_templates(self) -> List[Dict[str, Any]]:
        """Fetch templates from WordPress Master via REST API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Authenticate with WordPress
                auth_response = await client.post(
                    f"{self.wordpress_master_url}/wp-json/jwt-auth/v1/token",
                    json={
                        "username": self.wp_admin_user,
                        "password": self.wp_admin_password
                    }
                )
                
                if auth_response.status_code != 200:
                    raise Exception("Failed to authenticate with WordPress Master")
                
                auth_data = auth_response.json()
                token = auth_data.get('token')
                
                headers = {"Authorization": f"Bearer {token}"}
                
                # Fetch templates (custom post type)
                templates_response = await client.get(
                    f"{self.wordpress_master_url}/wp-json/wp/v2/kz_template",
                    headers=headers,
                    params={"per_page": 100, "status": "publish"}
                )
                
                if templates_response.status_code != 200:
                    raise Exception("Failed to fetch templates from WordPress Master")
                
                templates = templates_response.json()
                
                # Fetch ACF data for each template
                for template in templates:
                    template_id = template['id']
                    
                    # Get ACF fields
                    acf_response = await client.get(
                        f"{self.wordpress_master_url}/wp-json/acf/v3/posts/{template_id}",
                        headers=headers
                    )
                    
                    if acf_response.status_code == 200:
                        template['acf_data'] = acf_response.json()
                    else:
                        template['acf_data'] = {}
                
                return templates
                
        except Exception as e:
            logger.error(f"Error fetching WordPress templates: {str(e)}")
            return []
    
    async def _process_wordpress_template(self, wp_template: Dict[str, Any]) -> TemplateDefinition:
        """Process WordPress template data into our format"""
        try:
            template_id = f"wp_{wp_template['id']}"
            
            # Extract metadata from ACF or post meta
            acf_data = wp_template.get('acf_data', {})
            
            # Create template definition
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
            
            # Generate ACF field groups for this template
            industry = template.industry
            if industry in BRAZILIAN_INDUSTRIES:
                field_groups = acf_service.create_template_fields_for_industry(industry)
                template.acf_field_groups = field_groups
            
            return template
            
        except Exception as e:
            logger.error(f"Error processing WordPress template: {str(e)}")
            raise
    
    async def _store_template_locally(self, template: TemplateDefinition) -> None:
        """Store template in local repository"""
        try:
            template_file = self.local_repository_path / "templates" / f"{template.id}.json"
            
            # Convert template to dict for storage
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "industry": template.industry,
                "style": template.style,
                "preview_url": template.preview_url,
                "thumbnail": template.thumbnail,
                "features": template.features,
                "is_premium": template.is_premium,
                "tags": template.tags,
                "acf_field_groups": [
                    {
                        "key": group.key,
                        "title": group.title,
                        "fields": [
                            {
                                "key": field.key,
                                "label": field.label,
                                "name": field.name,
                                "type": field.type.value,
                                "instructions": field.instructions,
                                "required": field.required,
                                "default_value": field.default_value,
                                "placeholder": field.placeholder,
                                "choices": field.choices
                            }
                            for field in group.fields
                        ],
                        "location": group.location,
                        "menu_order": group.menu_order,
                        "position": group.position
                    }
                    for group in template.acf_field_groups
                ],
                "last_updated": datetime.now().isoformat(),
                "content_hash": self._generate_content_hash(template)
            }
            
            # Write to file
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            # Store ACF export separately
            if template.acf_field_groups:
                acf_export = acf_service.generate_acf_export(template.acf_field_groups)
                acf_file = self.local_repository_path / "acf_exports" / f"{template.id}_acf.json"
                
                with open(acf_file, 'w', encoding='utf-8') as f:
                    json.dump(acf_export, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Template {template.id} stored locally")
            
        except Exception as e:
            logger.error(f"Error storing template {template.id}: {str(e)}")
            raise
    
    def _generate_content_hash(self, template: TemplateDefinition) -> str:
        """Generate hash for template content to detect changes"""
        content = f"{template.name}{template.description}{template.category}{template.industry}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _load_local_templates(self) -> None:
        """Load templates from local storage into cache"""
        try:
            templates_dir = self.local_repository_path / "templates"
            
            for template_file in templates_dir.glob("*.json"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    template_id = template_data['id']
                    self.templates_cache[template_id] = {
                        "data": template_data,
                        "loaded_at": datetime.now()
                    }
                    
                except Exception as e:
                    logger.error(f"Error loading template from {template_file}: {str(e)}")
            
            logger.info(f"Loaded {len(self.templates_cache)} templates from local storage")
            
        except Exception as e:
            logger.error(f"Error loading local templates: {str(e)}")
    
    def _update_templates_cache(self) -> None:
        """Update in-memory cache with latest template data"""
        asyncio.create_task(self._load_local_templates())
    
    async def get_template(self, template_id: str) -> Optional[TemplateDefinition]:
        """Get a specific template by ID"""
        try:
            # Check cache first
            if template_id in self.templates_cache:
                cache_entry = self.templates_cache[template_id]
                if datetime.now() - cache_entry["loaded_at"] < self.cache_ttl:
                    template_data = cache_entry["data"]
                    return self._dict_to_template(template_data)
            
            # Load from file if not in cache or expired
            template_file = self.local_repository_path / "templates" / f"{template_id}.json"
            
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Update cache
                self.templates_cache[template_id] = {
                    "data": template_data,
                    "loaded_at": datetime.now()
                }
                
                return self._dict_to_template(template_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {str(e)}")
            return None
    
    async def list_templates(
        self,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        style: Optional[str] = None,
        is_premium: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TemplateDefinition]:
        """List templates with optional filtering"""
        try:
            templates = []
            
            for template_id, cache_entry in self.templates_cache.items():
                template_data = cache_entry["data"]
                
                # Apply filters
                if category and template_data.get('category') != category:
                    continue
                if industry and template_data.get('industry') != industry:
                    continue
                if style and template_data.get('style') != style:
                    continue
                if is_premium is not None and template_data.get('is_premium') != is_premium:
                    continue
                
                template = self._dict_to_template(template_data)
                templates.append(template)
            
            # Apply pagination
            templates = templates[offset:offset + limit]
            
            return templates
            
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return []
    
    def _dict_to_template(self, template_data: Dict[str, Any]) -> TemplateDefinition:
        """Convert dictionary to TemplateDefinition"""
        # Convert ACF field groups
        acf_field_groups = []
        for group_data in template_data.get('acf_field_groups', []):
            fields = []
            for field_data in group_data.get('fields', []):
                field = ACFField(
                    key=field_data['key'],
                    label=field_data['label'],
                    name=field_data['name'],
                    type=field_data['type'],
                    instructions=field_data.get('instructions', ''),
                    required=field_data.get('required', False),
                    default_value=field_data.get('default_value'),
                    placeholder=field_data.get('placeholder', ''),
                    choices=field_data.get('choices')
                )
                fields.append(field)
            
            group = ACFFieldGroup(
                key=group_data['key'],
                title=group_data['title'],
                fields=fields,
                location=group_data.get('location', []),
                menu_order=group_data.get('menu_order', 0),
                position=group_data.get('position', 'normal')
            )
            acf_field_groups.append(group)
        
        return TemplateDefinition(
            id=template_data['id'],
            name=template_data['name'],
            description=template_data['description'],
            category=template_data['category'],
            industry=template_data['industry'],
            style=template_data['style'],
            acf_field_groups=acf_field_groups,
            preview_url=template_data.get('preview_url'),
            thumbnail=template_data.get('thumbnail'),
            features=template_data.get('features', []),
            is_premium=template_data.get('is_premium', False),
            tags=template_data.get('tags', [])
        )
    
    async def create_template(self, template: TemplateDefinition) -> bool:
        """Create a new template in the repository"""
        try:
            # Store locally
            await self._store_template_locally(template)
            
            # Update cache
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "industry": template.industry,
                "style": template.style,
                "preview_url": template.preview_url,
                "thumbnail": template.thumbnail,
                "features": template.features,
                "is_premium": template.is_premium,
                "tags": template.tags,
                "last_updated": datetime.now().isoformat(),
                "content_hash": self._generate_content_hash(template)
            }
            
            self.templates_cache[template.id] = {
                "data": template_data,
                "loaded_at": datetime.now()
            }
            
            logger.info(f"Template {template.id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating template {template.id}: {str(e)}")
            return False
    
    async def update_template(self, template: TemplateDefinition) -> bool:
        """Update an existing template"""
        try:
            # Check if template exists
            existing = await self.get_template(template.id)
            if not existing:
                logger.warning(f"Template {template.id} not found for update")
                return False
            
            # Store updated version
            await self._store_template_locally(template)
            
            # Update cache
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "industry": template.industry,
                "style": template.style,
                "preview_url": template.preview_url,
                "thumbnail": template.thumbnail,
                "features": template.features,
                "is_premium": template.is_premium,
                "tags": template.tags,
                "last_updated": datetime.now().isoformat(),
                "content_hash": self._generate_content_hash(template)
            }
            
            self.templates_cache[template.id] = {
                "data": template_data,
                "loaded_at": datetime.now()
            }
            
            logger.info(f"Template {template.id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating template {template.id}: {str(e)}")
            return False
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template from the repository"""
        try:
            # Remove files
            template_file = self.local_repository_path / "templates" / f"{template_id}.json"
            acf_file = self.local_repository_path / "acf_exports" / f"{template_id}_acf.json"
            
            if template_file.exists():
                template_file.unlink()
            
            if acf_file.exists():
                acf_file.unlink()
            
            # Remove from cache
            if template_id in self.templates_cache:
                del self.templates_cache[template_id]
            
            logger.info(f"Template {template_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {str(e)}")
            return False
    
    async def get_template_acf_export(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get ACF export data for a template"""
        try:
            acf_file = self.local_repository_path / "acf_exports" / f"{template_id}_acf.json"
            
            if acf_file.exists():
                with open(acf_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting ACF export for template {template_id}: {str(e)}")
            return None
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        try:
            total_templates = len(self.templates_cache)
            
            # Count by category
            categories = {}
            industries = {}
            premium_count = 0
            
            for cache_entry in self.templates_cache.values():
                template_data = cache_entry["data"]
                
                category = template_data.get('category', 'unknown')
                industry = template_data.get('industry', 'unknown')
                
                categories[category] = categories.get(category, 0) + 1
                industries[industry] = industries.get(industry, 0) + 1
                
                if template_data.get('is_premium', False):
                    premium_count += 1
            
            return {
                "total_templates": total_templates,
                "premium_templates": premium_count,
                "free_templates": total_templates - premium_count,
                "categories": categories,
                "industries": industries,
                "last_sync": getattr(self, '_last_sync', None),
                "cache_size": len(self.templates_cache)
            }
            
        except Exception as e:
            logger.error(f"Error getting repository stats: {str(e)}")
            return {}

# Global instance
template_repository = TemplateRepository()