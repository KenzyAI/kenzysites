"""
White Label API endpoints
Phase 3: Launch Oficial - Basic white label for agencies
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.services.white_label_service import (
    white_label_service,
    WhiteLabelConfig,
    WhiteLabelTier,
    BrandingElement,
    EmailTemplateType,
    BrandColors,
    BrandFonts
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock user authentication
async def get_current_user():
    return {
        "user_id": "agency123",
        "email": "agency@example.com",
        "plan": "agency",
        "is_agency": True
    }

# White Label Configuration
@router.post("/config")
async def create_white_label_config(
    brand_name: str = Body(..., description="Agency brand name"),
    subdomain: str = Body(..., description="Subdomain (e.g., 'agency' for agency.kenzysites.com)"),
    logo_url: Optional[str] = Body(None, description="Logo URL"),
    colors: Optional[Dict[str, str]] = Body(None, description="Brand colors"),
    custom_domain: Optional[str] = Body(None, description="Custom domain (e.g., app.agency.com)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create white label configuration for agency
    Only available for Agency plan
    """
    
    try:
        # Verify agency plan
        if current_user["plan"] != "agency":
            raise HTTPException(
                status_code=403,
                detail="White label is only available for Agency plan"
            )
        
        # Create configuration
        settings = {}
        if logo_url:
            settings["logo_url"] = logo_url
        if colors:
            settings["colors"] = colors
        if custom_domain:
            settings["custom_domain"] = custom_domain
        
        config = await white_label_service.create_white_label_config(
            agency_id=current_user["user_id"],
            brand_name=brand_name,
            subdomain=subdomain,
            tier=WhiteLabelTier.BASIC,
            settings=settings
        )
        
        logger.info(f"Created white label config {config.id} for agency {current_user['user_id']}")
        
        return {
            "success": True,
            "config_id": config.id,
            "subdomain_url": f"https://{subdomain}.kenzysites.com",
            "message": "White label configuration created successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create white label config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create white label configuration: {str(e)}"
        )

@router.get("/config")
async def get_white_label_config(
    current_user: dict = Depends(get_current_user)
):
    """Get agency's white label configuration"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        return {
            "config_id": config.id,
            "brand_name": config.brand_name,
            "brand_tagline": config.brand_tagline,
            "subdomain": config.subdomain,
            "custom_domain": config.custom_domain,
            "logo_url": config.logo_url,
            "favicon_url": config.favicon_url,
            "colors": config.colors.dict(),
            "fonts": config.fonts.dict(),
            "footer_text": config.footer_text,
            "hide_powered_by": config.hide_powered_by,
            "markup_percentage": config.markup_percentage,
            "active": config.active,
            "created_at": config.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get white label config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get white label configuration: {str(e)}"
        )

# Branding Updates
@router.put("/branding/{element}")
async def update_branding_element(
    element: BrandingElement,
    data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Update specific branding element
    Elements: logo, colors, fonts, domain, footer, metadata
    """
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        updated_config = await white_label_service.update_branding(
            config_id=config.id,
            element=element,
            data=data
        )
        
        logger.info(f"Updated {element.value} for agency {current_user['user_id']}")
        
        return {
            "success": True,
            "element": element.value,
            "message": f"{element.value.replace('_', ' ').title()} updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update branding: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update branding: {str(e)}"
        )

# Email Templates
@router.get("/email-templates")
async def get_email_templates(
    current_user: dict = Depends(get_current_user)
):
    """Get all email templates"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        templates = []
        for template_type in EmailTemplateType:
            template = config.email_templates.get(
                template_type,
                white_label_service.default_templates.get(template_type)
            )
            if template:
                templates.append({
                    "type": template_type.value,
                    "subject": template.subject,
                    "variables": template.variables,
                    "preview_available": bool(template.preview_data)
                })
        
        return {
            "total": len(templates),
            "templates": templates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get email templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get email templates: {str(e)}"
        )

@router.put("/email-templates/{template_type}")
async def customize_email_template(
    template_type: EmailTemplateType,
    subject: Optional[str] = Body(None, description="Email subject"),
    html_template: Optional[str] = Body(None, description="HTML template"),
    text_template: Optional[str] = Body(None, description="Plain text template"),
    current_user: dict = Depends(get_current_user)
):
    """Customize an email template"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        template = await white_label_service.customize_email_template(
            config_id=config.id,
            template_type=template_type,
            subject=subject,
            html_template=html_template,
            text_template=text_template
        )
        
        logger.info(f"Customized {template_type.value} template for agency {current_user['user_id']}")
        
        return {
            "success": True,
            "template": {
                "type": template.type.value,
                "subject": template.subject,
                "variables": template.variables
            },
            "message": "Email template customized successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to customize email template: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to customize email template: {str(e)}"
        )

@router.post("/email-templates/{template_type}/preview")
async def preview_email_template(
    template_type: EmailTemplateType,
    variables: Dict[str, Any] = Body(..., description="Template variables"),
    current_user: dict = Depends(get_current_user)
):
    """Preview an email template with sample data"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        rendered = await white_label_service.render_email_template(
            config_id=config.id,
            template_type=template_type,
            variables=variables
        )
        
        return {
            "subject": rendered["subject"],
            "html_preview": rendered["html_body"],
            "text_preview": rendered["text_body"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to preview email template: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview email template: {str(e)}"
        )

# Client Management
@router.post("/clients/{client_id}/apply")
async def apply_white_label_to_client(
    client_id: str,
    custom_subdomain: Optional[str] = Body(None, description="Custom subdomain for client"),
    current_user: dict = Depends(get_current_user)
):
    """Apply white label settings to a client"""
    
    try:
        client_wl = await white_label_service.apply_white_label_to_client(
            client_id=client_id,
            agency_id=current_user["user_id"],
            custom_subdomain=custom_subdomain
        )
        
        logger.info(f"Applied white label to client {client_id}")
        
        access_url = custom_subdomain if custom_subdomain else f"app.{current_user['user_id']}.kenzysites.com"
        
        return {
            "success": True,
            "client_id": client_id,
            "access_url": f"https://{access_url}",
            "message": "White label applied to client successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to apply white label to client: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply white label to client: {str(e)}"
        )

@router.get("/clients/{client_id}/branding")
async def get_client_branding(
    client_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get branding for a specific client"""
    
    try:
        branding = await white_label_service.get_client_branding(client_id)
        
        if not branding:
            raise HTTPException(
                status_code=404,
                detail="No white label branding found for client"
            )
        
        return branding
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get client branding: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get client branding: {str(e)}"
        )

# Pricing
@router.put("/pricing")
async def update_custom_pricing(
    custom_pricing: Optional[Dict[str, Any]] = Body(None, description="Custom pricing structure"),
    markup_percentage: float = Body(0.0, ge=0, le=100, description="Markup percentage on base prices"),
    hide_original: bool = Body(True, description="Hide original pricing"),
    current_user: dict = Depends(get_current_user)
):
    """Update custom pricing for white label"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        updated_config = await white_label_service.update_pricing(
            config_id=config.id,
            custom_pricing=custom_pricing or {},
            markup_percentage=markup_percentage
        )
        
        logger.info(f"Updated pricing for agency {current_user['user_id']}")
        
        return {
            "success": True,
            "markup_percentage": markup_percentage,
            "hide_original_pricing": updated_config.hide_original_pricing,
            "message": "Pricing updated successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update pricing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update pricing: {str(e)}"
        )

@router.post("/pricing/calculate")
async def calculate_custom_price(
    base_price: float = Body(..., gt=0, description="Base price"),
    current_user: dict = Depends(get_current_user)
):
    """Calculate custom price with markup"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            return {
                "base_price": base_price,
                "custom_price": base_price,
                "markup": 0
            }
        
        custom_price = await white_label_service.get_custom_pricing(
            config_id=config.id,
            base_price=base_price
        )
        
        return {
            "base_price": base_price,
            "custom_price": custom_price,
            "markup": custom_price - base_price,
            "markup_percentage": config.markup_percentage
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate custom price: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate custom price: {str(e)}"
        )

# Domain Management
@router.post("/domain/validate")
async def validate_custom_domain(
    domain: str = Body(..., description="Custom domain to validate"),
    current_user: dict = Depends(get_current_user)
):
    """Validate custom domain configuration"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        validation = await white_label_service.validate_domain(
            domain=domain,
            config_id=config.id
        )
        
        return validation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate domain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate domain: {str(e)}"
        )

# Analytics
@router.get("/analytics")
async def get_white_label_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get white label usage analytics"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        analytics = await white_label_service.get_analytics(config.id)
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )

# Preview Mode
@router.get("/preview")
async def preview_white_label(
    domain: Optional[str] = Query(None, description="Domain to preview"),
    current_user: dict = Depends(get_current_user)
):
    """Preview white label configuration"""
    
    try:
        if domain:
            config = await white_label_service.get_config_by_domain(domain)
        else:
            config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        return {
            "preview_url": f"https://{config.subdomain}.kenzysites.com/preview",
            "config": {
                "brand_name": config.brand_name,
                "logo_url": config.logo_url,
                "colors": config.colors.dict(),
                "fonts": config.fonts.dict(),
                "footer_text": config.footer_text,
                "custom_css": config.custom_css
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview white label: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview white label: {str(e)}"
        )

# CSS/JS Customization
@router.put("/custom-code")
async def update_custom_code(
    custom_css: Optional[str] = Body(None, description="Custom CSS"),
    custom_js: Optional[str] = Body(None, description="Custom JavaScript"),
    custom_head_html: Optional[str] = Body(None, description="Custom HTML for <head>"),
    current_user: dict = Depends(get_current_user)
):
    """Update custom CSS/JS code"""
    
    try:
        config = white_label_service.configs.get(current_user["user_id"])
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="No white label configuration found"
            )
        
        if custom_css is not None:
            config.custom_css = custom_css
        if custom_js is not None:
            config.custom_js = custom_js
        if custom_head_html is not None:
            config.custom_head_html = custom_head_html
        
        config.updated_at = datetime.now()
        
        logger.info(f"Updated custom code for agency {current_user['user_id']}")
        
        return {
            "success": True,
            "message": "Custom code updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update custom code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update custom code: {str(e)}"
        )