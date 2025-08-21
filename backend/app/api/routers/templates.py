"""
Template Customization API endpoints
Handles template selection and AI-powered customization with ACF support
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import uuid

from app.models.template_models import (
    TemplateDefinition,
    TemplateCustomizationRequest,
    CustomizedTemplate,
    SitePreview,
    TemplateLibrary,
    TemplateSearchFilter,
    BRAZILIAN_INDUSTRIES
)
from app.services.acf_integration import acf_service
from app.services.agno_manager import AgnoManager
from app.services.templates_generator import templates_generator
from app.services.template_repository import template_repository
from app.services.wordpress_sync_service import wordpress_sync_service
from app.services.shared_hosting_provisioner import shared_hosting_provisioner
from app.services.landing_page_service import LandingPageService
from app.services.elementor_to_acf_converter import ElementorToACFConverter
from app.models.landing_page_models import LandingPageType, LandingPageIndustry, LandingPageACFModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
landing_page_service = LandingPageService()
elementor_converter = ElementorToACFConverter()

# In-memory storage for previews (in production, use Redis)
preview_storage = {}

async def get_agno_manager() -> AgnoManager:
    """Dependency to get Agno manager"""
    from main import app
    return app.state.agno_manager

async def get_current_user():
    """Mock user data - in production from authentication"""
    return {"user_id": "user123", "plan": "professional"}

@router.get("/library", response_model=TemplateLibrary)
async def get_template_library():
    """
    Get available templates library
    Returns all templates with categories and industries
    """
    templates = templates_generator.all_templates
    featured = templates_generator.featured_templates
    
    # Get unique categories and industries
    categories = list(set(t["category"] for t in templates))
    industries = list(set(t["industry"] for t in templates))
    
    # Get recent and popular templates
    new_templates = sorted(templates, key=lambda x: x["created_at"], reverse=True)[:10]
    popular_templates = sorted(templates, key=lambda x: x["metrics"]["average_conversion"], reverse=True)[:10]
    
    return TemplateLibrary(
        total_templates=len(templates),
        categories=categories,
        industries=industries,
        featured_templates=[t["id"] for t in featured],
        new_templates=[t["id"] for t in new_templates],
        popular_templates=[t["id"] for t in popular_templates]
    )

@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_templates(
    category: Optional[str] = None,
    industry: Optional[str] = None,
    is_premium: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List templates with filtering
    """
    templates = templates_generator.all_templates
    
    # Apply filters
    if category:
        templates = templates_generator.get_templates_by_category(templates, category)
    
    if industry:
        templates = templates_generator.get_templates_by_industry(templates, industry)
    
    if is_premium is not None:
        templates = [t for t in templates if t["is_premium"] == is_premium]
    
    if search:
        templates = templates_generator.search_templates(templates, search)
    
    # Apply pagination
    templates = templates[offset:offset + limit]
    
    return templates

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_template_details(template_id: str):
    """
    Get detailed information about a specific template
    """
    templates = templates_generator.all_templates
    template = next((t for t in templates if t["id"] == template_id), None)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Add ACF field groups for this template
    industry = template["industry"]
    acf_field_groups = acf_service.create_template_fields_for_industry(industry)
    
    template["acf_field_groups"] = [
        {
            "key": group.key,
            "title": group.title,
            "fields_count": len(group.fields),
            "fields": [
                {
                    "key": field.key,
                    "label": field.label,
                    "name": field.name,
                    "type": field.type.value,
                    "required": field.required
                }
                for field in group.fields[:5]  # Show first 5 fields
            ]
        }
        for group in acf_field_groups
    ]
    
    return template

@router.post("/customize", response_model=CustomizedTemplate)
async def customize_template(
    request: TemplateCustomizationRequest,
    current_user: dict = Depends(get_current_user),
    agno_manager: AgnoManager = Depends(get_agno_manager)
):
    """
    Customize a template with AI based on business information
    Costs 50 AI Credits (template customization)
    """
    
    try:
        start_time = asyncio.get_event_loop().time()
        logger.info(f"Template customization request from user {current_user['user_id']}")
        logger.info(f"Template: {request.template_id}, Business: {request.business_name}")
        
        # Get template
        templates = templates_generator.all_templates
        template = next((t for t in templates if t["id"] == request.template_id), None)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if Brazilian industry
        brazilian_template = None
        if request.industry.lower() in BRAZILIAN_INDUSTRIES:
            brazilian_template = BRAZILIAN_INDUSTRIES[request.industry.lower()]
        
        # Generate ACF fields for the industry
        acf_field_groups = acf_service.create_template_fields_for_industry(
            industry=request.industry,
            business_type="service"  # Could be determined from request
        )
        
        # Personalize fields with business data
        business_data = {
            "name": request.business_name,
            "description": request.business_description,
            "industry": request.industry
        }
        
        for field_group in acf_field_groups:
            acf_service.personalize_fields_with_ai(field_group, business_data)
        
        # Generate customized content with AI
        customized_content = await _generate_customized_content(
            agno_manager,
            template,
            request,
            acf_field_groups,
            brazilian_template
        )
        
        # Generate ACF export
        acf_export = acf_service.generate_acf_export(acf_field_groups)
        
        # Create customization record
        customization_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        customized_template = CustomizedTemplate(
            template_id=request.template_id,
            customization_id=customization_id,
            business_name=request.business_name,
            customized_fields=customized_content["fields"],
            generated_content=customized_content["content"],
            suggested_images=customized_content.get("suggested_images", []),
            generated_images=customized_content.get("generated_images", []),
            acf_export_data=acf_export,
            ai_credits_used=50,  # Template customization cost
            processing_time=processing_time
        )
        
        logger.info(f"Template customized successfully in {processing_time:.2f}s")
        
        return customized_template
        
    except Exception as e:
        logger.error(f"Template customization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Template customization failed: {str(e)}"
        )

@router.post("/preview", response_model=SitePreview)
async def create_preview(
    customization_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a preview of the customized site
    Preview is available for 24 hours
    """
    
    # Generate preview ID
    preview_id = f"preview_{uuid.uuid4().hex[:8]}"
    
    # Create preview URL (in production, this would deploy to a staging server)
    preview_url = f"https://preview.kenzysites.com/{preview_id}"
    
    # Set expiration (24 hours)
    expires_at = datetime.now() + timedelta(hours=24)
    
    # Create preview record
    preview = SitePreview(
        preview_id=preview_id,
        customization_id=customization_id,
        preview_url=preview_url,
        expires_at=expires_at,
        is_published=False
    )
    
    # Store preview (in production, use Redis)
    preview_storage[preview_id] = preview
    
    logger.info(f"Preview created: {preview_id} for customization {customization_id}")
    
    return preview

@router.post("/preview/{preview_id}/publish")
async def publish_preview(
    preview_id: str,
    domain: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Publish a preview as a live WordPress site
    This triggers the actual WordPress provisioning
    """
    
    # Get preview
    preview = preview_storage.get(preview_id)
    if not preview:
        raise HTTPException(status_code=404, detail="Preview not found")
    
    if preview.is_published:
        raise HTTPException(status_code=400, detail="Preview already published")
    
    # Check if preview expired
    if datetime.now() > preview.expires_at:
        raise HTTPException(status_code=400, detail="Preview has expired")
    
    # Trigger WordPress provisioning
    # This would integrate with the provisioning service
    site_data = {
        "preview_id": preview_id,
        "customization_id": preview.customization_id,
        "domain": domain,
        "user_id": current_user["user_id"],
        "status": "provisioning"
    }
    
    # Mark preview as published
    preview.is_published = True
    preview_storage[preview_id] = preview
    
    logger.info(f"Publishing preview {preview_id} to domain {domain}")
    
    return {
        "message": "Site is being provisioned",
        "domain": domain,
        "estimated_time": "5-10 minutes",
        "status": "provisioning"
    }

@router.get("/brazilian-industries")
async def get_brazilian_industries():
    """
    Get list of Brazilian industry templates with specific features
    """
    industries = []
    
    for key, template in BRAZILIAN_INDUSTRIES.items():
        industries.append({
            "key": template.industry_key,
            "name": template.industry_name,
            "description": template.description,
            "features": {
                "whatsapp": template.whatsapp_integration,
                "pix": template.pix_payment,
                "lgpd": template.lgpd_notice,
                "cnpj": template.cnpj_field,
                "cpf": template.cpf_field,
                "delivery": template.delivery_areas,
                "specific": template.specific_features
            }
        })
    
    return industries

async def _generate_customized_content(
    agno_manager: AgnoManager,
    template: Dict[str, Any],
    request: TemplateCustomizationRequest,
    acf_field_groups: list,
    brazilian_template=None
) -> Dict[str, Any]:
    """
    Generate customized content using AI
    """
    
    # Build prompt for content generation
    prompt = f"""
    Customize the template for the following business:
    
    Business Name: {request.business_name}
    Industry: {request.industry}
    Description: {request.business_description}
    Target Audience: {request.target_audience}
    Services/Products: {', '.join(request.services_products)}
    USPs: {', '.join(request.unique_selling_points)}
    
    Template: {template['name']}
    Category: {template['category']}
    Style: {template['style']}
    
    Tone of Voice: {request.tone_of_voice}
    Language: {request.primary_language}
    
    Generate customized content for all ACF fields and pages.
    Content should be in {request.primary_language}.
    """
    
    if brazilian_template:
        prompt += f"""
    Include Brazilian-specific content:
    - WhatsApp contact button
    - PIX payment information
    - LGPD compliance text
    - Brazilian cultural references
    """
    
    # Use Agno to generate content
    agent = agno_manager.agents.get("content_generator")
    if agent:
        response = await agent.arun(prompt)
        content = response.content
    else:
        # Fallback content
        content = {
            "hero_title": f"Bem-vindo à {request.business_name}",
            "hero_subtitle": request.business_description,
            "about_text": f"A {request.business_name} é líder em {request.industry}.",
            "services_text": "Oferecemos os melhores serviços do mercado."
        }
    
    # Generate field values based on ACF structure
    customized_fields = {}
    for group in acf_field_groups:
        for field in group.fields:
            if field.default_value:
                value = field.default_value
                # Replace placeholders
                if isinstance(value, str):
                    value = value.replace("{{business_name}}", request.business_name)
                    value = value.replace("{{business_description}}", request.business_description)
                customized_fields[field.name] = value
    
    # Add custom field values from request
    if request.custom_fields:
        customized_fields.update(request.custom_fields)
    
    return {
        "fields": customized_fields,
        "content": content if isinstance(content, dict) else {"generated": content},
        "suggested_images": [
            f"https://source.unsplash.com/800x600/?{request.industry},business",
            f"https://source.unsplash.com/800x600/?{request.industry},office",
            f"https://source.unsplash.com/800x600/?{request.industry},team"
        ]
    }

# Template Repository Management Endpoints

@router.post("/repository/sync")
async def sync_template_repository(
    current_user: dict = Depends(get_current_user)
):
    """
    Sync templates from WordPress Master
    Admin only endpoint
    """
    # Check if user is admin (implement proper auth)
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = await template_repository.sync_with_wordpress_master()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "message": "Template repository synced successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Repository sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/repository/stats")
async def get_repository_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get template repository statistics
    """
    try:
        stats = await template_repository.get_repository_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting repository stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get repository stats")

@router.get("/repository/templates", response_model=List[Dict[str, Any]])
async def list_repository_templates(
    category: Optional[str] = None,
    industry: Optional[str] = None,
    style: Optional[str] = None,
    is_premium: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """
    List templates from repository with filtering
    """
    try:
        templates = await template_repository.list_templates(
            category=category,
            industry=industry,
            style=style,
            is_premium=is_premium,
            limit=limit,
            offset=offset
        )
        
        # Convert to dict format
        template_dicts = []
        for template in templates:
            template_dict = {
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
                "acf_field_groups_count": len(template.acf_field_groups)
            }
            template_dicts.append(template_dict)
        
        return template_dicts
        
    except Exception as e:
        logger.error(f"Error listing repository templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list templates")

@router.get("/repository/templates/{template_id}")
async def get_repository_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed template from repository
    """
    try:
        template = await template_repository.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
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
                    "fields_count": len(group.fields),
                    "fields": [
                        {
                            "key": field.key,
                            "label": field.label,
                            "name": field.name,
                            "type": field.type.value,
                            "required": field.required,
                            "default_value": field.default_value,
                            "placeholder": field.placeholder
                        }
                        for field in group.fields
                    ]
                }
                for group in template.acf_field_groups
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting repository template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get template")

@router.post("/repository/templates")
async def create_repository_template(
    template_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new template in repository
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Create template object from data
        template = TemplateDefinition(
            id=template_data["id"],
            name=template_data["name"],
            description=template_data["description"],
            category=template_data["category"],
            industry=template_data["industry"],
            style=template_data["style"],
            preview_url=template_data.get("preview_url"),
            thumbnail=template_data.get("thumbnail"),
            features=template_data.get("features", []),
            is_premium=template_data.get("is_premium", False),
            tags=template_data.get("tags", [])
        )
        
        # Generate ACF fields for industry
        field_groups = acf_service.create_template_fields_for_industry(
            template.industry
        )
        template.acf_field_groups = field_groups
        
        success = await template_repository.create_template(template)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create template")
        
        return {
            "message": "Template created successfully",
            "template_id": template.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

@router.put("/repository/templates/{template_id}")
async def update_repository_template(
    template_id: str,
    template_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing template in repository
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Get existing template
        existing = await template_repository.get_template(template_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update template object
        template = TemplateDefinition(
            id=template_id,
            name=template_data.get("name", existing.name),
            description=template_data.get("description", existing.description),
            category=template_data.get("category", existing.category),
            industry=template_data.get("industry", existing.industry),
            style=template_data.get("style", existing.style),
            preview_url=template_data.get("preview_url", existing.preview_url),
            thumbnail=template_data.get("thumbnail", existing.thumbnail),
            features=template_data.get("features", existing.features),
            is_premium=template_data.get("is_premium", existing.is_premium),
            tags=template_data.get("tags", existing.tags)
        )
        
        # Regenerate ACF fields if industry changed
        if template.industry != existing.industry:
            field_groups = acf_service.create_template_fields_for_industry(
                template.industry
            )
            template.acf_field_groups = field_groups
        else:
            template.acf_field_groups = existing.acf_field_groups
        
        success = await template_repository.update_template(template)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update template")
        
        return {
            "message": "Template updated successfully",
            "template_id": template.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")

@router.delete("/repository/templates/{template_id}")
async def delete_repository_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a template from repository
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        success = await template_repository.delete_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Template not found or failed to delete")
        
        return {
            "message": "Template deleted successfully",
            "template_id": template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")

@router.get("/repository/templates/{template_id}/acf-export")
async def get_template_acf_export(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get ACF export data for a template
    """
    try:
        acf_export = await template_repository.get_template_acf_export(template_id)
        
        if not acf_export:
            raise HTTPException(status_code=404, detail="ACF export not found for template")
        
        return acf_export
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ACF export for template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ACF export")

@router.post("/repository/templates/{template_id}/generate-acf")
async def regenerate_template_acf(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Regenerate ACF fields for a template
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        template = await template_repository.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Regenerate ACF fields
        field_groups = acf_service.create_template_fields_for_industry(
            template.industry
        )
        template.acf_field_groups = field_groups
        
        # Update template
        success = await template_repository.update_template(template)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update template with new ACF fields")
        
        return {
            "message": "ACF fields regenerated successfully",
            "template_id": template_id,
            "field_groups_count": len(field_groups)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating ACF for template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate ACF: {str(e)}")

@router.get("/industries/brazilian-enhanced", response_model=List[Dict[str, Any]])
async def get_brazilian_industries_enhanced():
    """
    Get enhanced list of Brazilian industry templates with ACF information
    """
    try:
        industries = []
        
        for key, template in BRAZILIAN_INDUSTRIES.items():
            # Generate ACF preview for this industry
            field_groups = acf_service.create_template_fields_for_industry(key)
            
            industry_info = {
                "key": template.industry_key,
                "name": template.industry_name,
                "description": template.description,
                "features": {
                    "whatsapp": template.whatsapp_integration,
                    "pix": template.pix_payment,
                    "lgpd": template.lgpd_notice,
                    "cnpj": template.cnpj_field,
                    "cpf": template.cpf_field,
                    "delivery": template.delivery_areas,
                    "specific": template.specific_features
                },
                "acf_field_groups": [
                    {
                        "title": group.title,
                        "fields_count": len(group.fields),
                        "key_fields": [
                            {
                                "label": field.label,
                                "name": field.name,
                                "type": field.type.value
                            }
                            for field in group.fields[:3]  # Show first 3 fields
                        ]
                    }
                    for group in field_groups[:2]  # Show first 2 groups
                ]
            }
            
            industries.append(industry_info)
        
        return industries
        
    except Exception as e:
        logger.error(f"Error getting enhanced Brazilian industries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get Brazilian industries")

# WordPress Sync Service Endpoints

@router.post("/sync/webhook")
async def handle_wordpress_webhook(
    event_type: str,
    webhook_data: Dict[str, Any],
    x_signature: Optional[str] = None
):
    """
    Handle incoming webhooks from WordPress Master
    Public endpoint for WordPress to call
    """
    try:
        success = await wordpress_sync_service.handle_webhook(
            event_type=event_type,
            data=webhook_data,
            signature=x_signature
        )
        
        if success:
            return {"message": "Webhook processed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to process webhook")
            
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.get("/sync/status")
async def get_sync_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get WordPress sync service status
    """
    try:
        status = await wordpress_sync_service.get_sync_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@router.post("/sync/start")
async def start_sync_service(
    current_user: dict = Depends(get_current_user)
):
    """
    Start the WordPress sync service
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        await wordpress_sync_service.start_sync_service()
        
        return {
            "message": "WordPress sync service started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting sync service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start sync service: {str(e)}")

@router.post("/sync/stop")
async def stop_sync_service(
    current_user: dict = Depends(get_current_user)
):
    """
    Stop the WordPress sync service
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        await wordpress_sync_service.stop_sync_service()
        
        return {
            "message": "WordPress sync service stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping sync service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop sync service: {str(e)}")

@router.post("/sync/manual/full")
async def trigger_full_sync(
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger a manual full sync
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        await wordpress_sync_service.queue_full_sync()
        
        return {
            "message": "Full sync queued successfully"
        }
        
    except Exception as e:
        logger.error(f"Error triggering full sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger full sync: {str(e)}")

@router.post("/sync/manual/incremental")
async def trigger_incremental_sync(
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger a manual incremental sync
    Admin only endpoint
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        await wordpress_sync_service.queue_incremental_sync()
        
        return {
            "message": "Incremental sync queued successfully"
        }
        
    except Exception as e:
        logger.error(f"Error triggering incremental sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger incremental sync: {str(e)}")

@router.get("/sync/health")
async def sync_health_check():
    """
    Health check for sync service
    Public endpoint for monitoring
    """
    try:
        status = await wordpress_sync_service.get_sync_status()
        
        health_status = {
            "status": "healthy" if status["is_running"] else "stopped",
            "service_running": status["is_running"],
            "queue_size": status["queue_size"],
            "last_sync": status["last_full_sync"]
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in sync health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Shared Hosting Provisioning Endpoints

@router.post("/provision/shared-hosting")
async def provision_shared_hosting_site(
    business_name: str,
    industry: str,
    plan: str = "basic",
    template_id: Optional[str] = None,
    custom_domain: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Provision WordPress site on shared hosting using Multisite
    Alternative to Kubernetes for cost-effective hosting
    """
    try:
        # Get user ID from current user
        user_id = current_user.get("user_id", "unknown")
        
        # Generate ACF configuration for the industry
        acf_field_groups = acf_service.create_template_fields_for_industry(industry)
        acf_config = acf_service.generate_acf_export(acf_field_groups) if acf_field_groups else None
        
        # Provision the site
        result = await shared_hosting_provisioner.provision_wordpress_multisite(
            business_name=business_name,
            industry=industry,
            plan=plan,
            user_id=user_id,
            template_id=template_id,
            acf_config=acf_config,
            custom_domain=custom_domain
        )
        
        return {
            "message": "WordPress site provisioned successfully on shared hosting",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Shared hosting provisioning error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Provisioning failed: {str(e)}")

@router.get("/provision/shared-hosting/{site_id}/status")
async def get_shared_hosting_site_status(
    site_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of a shared hosting site
    """
    try:
        status = await shared_hosting_provisioner.get_site_status(site_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting site status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get site status")

@router.post("/provision/shared-hosting/{site_id}/suspend")
async def suspend_shared_hosting_site(
    site_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Suspend a shared hosting site
    """
    # Check if user has permission to manage this site
    # (implement proper authorization logic)
    
    try:
        result = await shared_hosting_provisioner.suspend_site(site_id)
        return result
        
    except Exception as e:
        logger.error(f"Error suspending site: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to suspend site")


# =============================================================================
# LANDING PAGES API ENDPOINTS - Sistema de conversão Elementor para ACF
# =============================================================================

@router.get("/landing-pages", response_model=List[Dict[str, Any]])
async def list_available_landing_pages(
    industry: Optional[str] = None,
    business_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lista landing pages disponíveis do portfólio Elementor
    Convertidas automaticamente para templates ACF
    """
    try:
        landing_pages = await landing_page_service.list_available_landing_pages(
            industry=industry,
            business_type=business_type
        )
        
        return {
            "success": True,
            "landing_pages": landing_pages,
            "total": len(landing_pages),
            "filters_applied": {
                "industry": industry,
                "business_type": business_type
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing landing pages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list landing pages")

@router.get("/landing-pages/{template_id}", response_model=Dict[str, Any])
async def get_landing_page_details(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém detalhes completos de uma landing page específica
    Inclui configurações ACF, dados Elementor e especificações técnicas
    """
    try:
        details = await landing_page_service.get_landing_page_details(template_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Landing page not found")
            
        return {
            "success": True,
            "landing_page": details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting landing page details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get landing page details")

@router.post("/landing-pages/provision", response_model=Dict[str, Any])
async def provision_landing_page(
    template_id: str,
    business_data: Dict[str, Any],
    client_domain: str,
    keep_elementor: bool = True,
    customizations: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Provisiona uma landing page personalizada para cliente
    Combina template Elementor com campos ACF personalizados
    """
    try:
        # Validar dados obrigatórios
        required_fields = ["business_name", "industry"]
        for field in required_fields:
            if field not in business_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required field: {field}"
                )
        
        # Provisionar landing page
        result = await landing_page_service.provision_landing_page(
            template_id=template_id,
            business_data=business_data,
            client_domain=client_domain,
            keep_elementor=keep_elementor,
            customizations=customizations
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to provision landing page")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error provisioning landing page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Provisioning failed: {str(e)}")

@router.post("/landing-pages/clone", response_model=Dict[str, Any])
async def clone_landing_page(
    source_template_id: str,
    new_business_data: Dict[str, Any],
    modifications: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Clona uma landing page existente para novo cliente
    Permite modificações específicas no template
    """
    try:
        result = await landing_page_service.clone_landing_page(
            source_template_id=source_template_id,
            new_business_data=new_business_data,
            modifications=modifications
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to clone landing page")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cloning landing page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cloning failed: {str(e)}")

@router.get("/landing-pages/analytics/{site_id}", response_model=Dict[str, Any])
async def get_landing_page_analytics(
    site_id: str,
    date_range: str = "30d",
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém analytics de uma landing page provisionada
    Inclui métricas de conversão, tráfego e performance
    """
    try:
        # Obter informações do site (mock - implementar busca real)
        site_info = {
            "id": site_id,
            "url": f"https://{site_id}.exemplo.com"
        }
        
        analytics = await landing_page_service.get_landing_page_analytics(
            site_info=site_info,
            date_range=date_range
        )
        
        return {
            "success": True,
            "analytics": analytics,
            "site_id": site_id
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.post("/elementor/convert", response_model=Dict[str, Any])
async def convert_elementor_page_to_acf(
    page_data: Dict[str, Any],
    landing_page_type: str = "generic",
    preserve_elementor: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Converte uma página Elementor existente para template ACF
    Permite modo híbrido mantendo Elementor + ACF
    """
    try:
        # Verificar se user tem permissão (implementar lógica de autorização)
        if current_user.get("plan") not in ["professional", "enterprise"]:
            raise HTTPException(
                status_code=403,
                detail="Professional plan required for Elementor conversion"
            )
        
        # Converter página Elementor
        conversion_result = await elementor_converter.convert_elementor_page(
            page_data=page_data,
            landing_page_type=landing_page_type,
            preserve_elementor=preserve_elementor
        )
        
        return {
            "success": True,
            "conversion_result": conversion_result,
            "template_id": conversion_result.get("template_id"),
            "acf_fields_created": len(conversion_result.get("acf_field_groups", [])),
            "elementor_preserved": preserve_elementor
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting Elementor page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@router.get("/landing-pages/types", response_model=Dict[str, Any])
async def get_landing_page_types():
    """
    Lista todos os tipos de landing pages disponíveis
    E indústrias suportadas para conversão
    """
    try:
        return {
            "success": True,
            "landing_page_types": [
                {
                    "value": lp_type.value,
                    "label": lp_type.value.replace("_", " ").title(),
                    "description": f"Landing page otimizada para {lp_type.value.replace('_', ' ')}"
                }
                for lp_type in LandingPageType
            ],
            "industries": [
                {
                    "value": industry.value,
                    "label": industry.value.replace("_", " ").title(),
                    "description": f"Templates específicos para {industry.value.replace('_', ' ')}"
                }
                for industry in LandingPageIndustry
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting landing page types: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get types")

@router.post("/landing-pages/field-groups", response_model=Dict[str, Any])
async def get_acf_field_groups_for_landing_page(
    landing_page_type: str,
    industry: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém grupos de campos ACF específicos para tipo de landing page
    Customizados por indústria quando fornecida
    """
    try:
        from app.models.landing_page_models import get_field_groups_by_landing_page_type
        
        # Validar tipo de landing page
        try:
            lp_type = LandingPageType(landing_page_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid landing page type: {landing_page_type}"
            )
        
        # Obter grupos de campos
        field_groups = get_field_groups_by_landing_page_type(lp_type)
        
        # Serializar para resposta
        serialized_groups = []
        for group in field_groups:
            serialized_groups.append({
                "key": group.key,
                "title": group.title,
                "fields": [
                    {
                        "key": field.key,
                        "name": field.name,
                        "label": field.label,
                        "type": field.type.value,
                        "instructions": field.instructions,
                        "required": field.required,
                        "placeholder": getattr(field, 'placeholder', None),
                        "character_limit": getattr(field, 'character_limit', None)
                    }
                    for field in group.fields
                ],
                "location": group.location,
                "menu_order": group.menu_order
            })
        
        return {
            "success": True,
            "landing_page_type": landing_page_type,
            "industry": industry,
            "field_groups": serialized_groups,
            "total_groups": len(serialized_groups),
            "total_fields": sum(len(group["fields"]) for group in serialized_groups)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting field groups: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get field groups")

@router.post("/provision/shared-hosting/{site_id}/resume")
async def resume_shared_hosting_site(
    site_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Resume a suspended shared hosting site
    """
    try:
        result = await shared_hosting_provisioner.resume_site(site_id)
        return result
        
    except Exception as e:
        logger.error(f"Error resuming site: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resume site")

@router.delete("/provision/shared-hosting/{site_id}")
async def delete_shared_hosting_site(
    site_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a shared hosting site
    """
    if current_user.get("role") not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        result = await shared_hosting_provisioner.delete_site(site_id)
        return result
        
    except Exception as e:
        logger.error(f"Error deleting site: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete site")

@router.get("/provision/modes")
async def get_provisioning_modes():
    """
    Get available provisioning modes and their capabilities
    """
    return {
        "kubernetes": {
            "name": "Kubernetes (Isolado)",
            "description": "Cada cliente tem sua infraestrutura isolada",
            "advantages": [
                "Isolamento total",
                "Escalabilidade automática", 
                "Performance dedicada",
                "SLA de 99.9%"
            ],
            "disadvantages": [
                "Custo mais alto",
                "Complexidade técnica"
            ],
            "cost_per_site": "R$ 25-50/mês",
            "ideal_for": "Clientes com tráfego médio/alto"
        },
        "shared_hosting": {
            "name": "Hospedagem Compartilhada (Multisite)",
            "description": "Múltiplos sites em uma instalação WordPress",
            "advantages": [
                "Custo baixíssimo",
                "Setup rápido",
                "Gestão centralizada",
                "Templates ACF funcionam"
            ],
            "disadvantages": [
                "Recursos compartilhados",
                "Menos isolamento",
                "Limitações de escala"
            ],
            "cost_per_site": "R$ 5-15/mês",
            "ideal_for": "Clientes com baixo tráfego, MVPs"
        }
    }