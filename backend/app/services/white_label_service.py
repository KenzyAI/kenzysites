"""
White Label Service
Phase 3: Launch Oficial - Basic white label functionality
Allows agencies to customize branding
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
import uuid
import json
import hashlib

logger = logging.getLogger(__name__)

# Enums
class BrandingElement(str, Enum):
    LOGO = "logo"
    FAVICON = "favicon"
    COLORS = "colors"
    FONTS = "fonts"
    EMAIL_TEMPLATES = "email_templates"
    DOMAIN = "domain"
    FOOTER = "footer"
    METADATA = "metadata"

class EmailTemplateType(str, Enum):
    WELCOME = "welcome"
    RESET_PASSWORD = "reset_password"
    INVOICE = "invoice"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELED = "subscription_canceled"
    SITE_CREATED = "site_created"
    SUPPORT_TICKET = "support_ticket"
    PAYMENT_FAILED = "payment_failed"

class WhiteLabelTier(str, Enum):
    NONE = "none"
    BASIC = "basic"  # Agency plan
    ADVANCED = "advanced"  # Future enhancement
    ENTERPRISE = "enterprise"  # Future enhancement

# Models
class BrandColors(BaseModel):
    """Brand color scheme"""
    primary: str = "#007BFF"
    secondary: str = "#6C757D"
    accent: str = "#28A745"
    success: str = "#28A745"
    warning: str = "#FFC107"
    danger: str = "#DC3545"
    info: str = "#17A2B8"
    light: str = "#F8F9FA"
    dark: str = "#343A40"
    text: str = "#212529"
    background: str = "#FFFFFF"

class BrandFonts(BaseModel):
    """Brand typography"""
    heading_font: str = "Inter"
    body_font: str = "Inter"
    code_font: str = "Fira Code"
    heading_weight: int = 700
    body_weight: int = 400
    base_size: int = 16

class EmailTemplate(BaseModel):
    """Customizable email template"""
    id: str = Field(default_factory=lambda: f"tpl_{uuid.uuid4().hex[:8]}")
    type: EmailTemplateType
    subject: str
    html_template: str
    text_template: str
    variables: List[str] = Field(default_factory=list)
    preview_data: Dict[str, Any] = Field(default_factory=dict)
    
class WhiteLabelConfig(BaseModel):
    """White label configuration for an agency"""
    id: str = Field(default_factory=lambda: f"wl_{uuid.uuid4().hex[:8]}")
    agency_id: str
    tier: WhiteLabelTier = WhiteLabelTier.BASIC
    
    # Branding
    brand_name: str
    brand_tagline: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    colors: BrandColors = Field(default_factory=BrandColors)
    fonts: BrandFonts = Field(default_factory=BrandFonts)
    
    # Domain
    custom_domain: Optional[str] = None
    subdomain: Optional[str] = None  # e.g., agency.kenzysites.com
    ssl_enabled: bool = True
    
    # Email
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to_email: Optional[str] = None
    email_templates: Dict[EmailTemplateType, EmailTemplate] = Field(default_factory=dict)
    
    # Footer
    footer_text: Optional[str] = None
    footer_links: List[Dict[str, str]] = Field(default_factory=list)
    hide_powered_by: bool = False
    
    # SEO/Metadata
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: List[str] = Field(default_factory=list)
    og_image: Optional[str] = None
    
    # Custom CSS/JS
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    custom_head_html: Optional[str] = None
    
    # Pricing
    custom_pricing: Optional[Dict[str, Any]] = None
    hide_original_pricing: bool = False
    markup_percentage: float = 0.0  # Agency markup on base prices
    
    # Features
    enabled_features: List[str] = Field(default_factory=list)
    disabled_features: List[str] = Field(default_factory=list)
    
    # Analytics
    google_analytics_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None
    custom_tracking_code: Optional[str] = None
    
    # Status
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ClientWhiteLabel(BaseModel):
    """White label settings applied to a client"""
    client_id: str
    agency_id: str
    white_label_config_id: str
    custom_subdomain: Optional[str] = None  # client.agency.com
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class WhiteLabelService:
    """Service for managing white label configurations"""
    
    def __init__(self):
        self.configs: Dict[str, WhiteLabelConfig] = {}
        self.client_mappings: Dict[str, ClientWhiteLabel] = {}
        self.domain_mappings: Dict[str, str] = {}  # domain -> config_id
        
        # Initialize default email templates
        self.default_templates = self._create_default_templates()
    
    def _create_default_templates(self) -> Dict[EmailTemplateType, EmailTemplate]:
        """Create default email templates"""
        templates = {}
        
        # Welcome email
        templates[EmailTemplateType.WELCOME] = EmailTemplate(
            type=EmailTemplateType.WELCOME,
            subject="Welcome to {{brand_name}}!",
            html_template="""
            <h1>Welcome to {{brand_name}}!</h1>
            <p>Hi {{user_name}},</p>
            <p>Your account has been created successfully. You can now start creating amazing WordPress sites with AI.</p>
            <a href="{{dashboard_url}}" style="background: {{primary_color}}; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a>
            <p>Best regards,<br>{{brand_name}} Team</p>
            """,
            text_template="Welcome to {{brand_name}}! Your account is ready.",
            variables=["brand_name", "user_name", "dashboard_url", "primary_color"]
        )
        
        # Invoice email
        templates[EmailTemplateType.INVOICE] = EmailTemplate(
            type=EmailTemplateType.INVOICE,
            subject="Invoice #{{invoice_number}} from {{brand_name}}",
            html_template="""
            <h2>Invoice #{{invoice_number}}</h2>
            <p>Amount: {{amount}} {{currency}}</p>
            <p>Due Date: {{due_date}}</p>
            <a href="{{invoice_url}}">View Invoice</a>
            """,
            text_template="Invoice #{{invoice_number}} - Amount: {{amount}} {{currency}}",
            variables=["brand_name", "invoice_number", "amount", "currency", "due_date", "invoice_url"]
        )
        
        return templates
    
    async def create_white_label_config(
        self,
        agency_id: str,
        brand_name: str,
        subdomain: str,
        tier: WhiteLabelTier = WhiteLabelTier.BASIC,
        settings: Optional[Dict[str, Any]] = None
    ) -> WhiteLabelConfig:
        """Create a white label configuration for an agency"""
        
        # Check if subdomain is available
        if subdomain in self.domain_mappings:
            raise ValueError(f"Subdomain {subdomain} is already taken")
        
        config = WhiteLabelConfig(
            agency_id=agency_id,
            tier=tier,
            brand_name=brand_name,
            subdomain=subdomain
        )
        
        # Apply additional settings
        if settings:
            if "colors" in settings:
                config.colors = BrandColors(**settings["colors"])
            if "fonts" in settings:
                config.fonts = BrandFonts(**settings["fonts"])
            if "logo_url" in settings:
                config.logo_url = settings["logo_url"]
            if "custom_domain" in settings:
                config.custom_domain = settings["custom_domain"]
        
        # Initialize with default email templates
        config.email_templates = self.default_templates.copy()
        
        # Store configuration
        self.configs[config.id] = config
        self.configs[agency_id] = config  # Also store by agency ID
        self.domain_mappings[subdomain] = config.id
        
        if config.custom_domain:
            self.domain_mappings[config.custom_domain] = config.id
        
        logger.info(f"Created white label config {config.id} for agency {agency_id}")
        return config
    
    async def update_branding(
        self,
        config_id: str,
        element: BrandingElement,
        data: Dict[str, Any]
    ) -> WhiteLabelConfig:
        """Update specific branding element"""
        
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"White label config {config_id} not found")
        
        if element == BrandingElement.LOGO:
            config.logo_url = data.get("logo_url")
            config.favicon_url = data.get("favicon_url", config.favicon_url)
            
        elif element == BrandingElement.COLORS:
            config.colors = BrandColors(**data)
            
        elif element == BrandingElement.FONTS:
            config.fonts = BrandFonts(**data)
            
        elif element == BrandingElement.DOMAIN:
            # Update domain mappings
            if config.custom_domain:
                del self.domain_mappings[config.custom_domain]
            
            config.custom_domain = data.get("custom_domain")
            if config.custom_domain:
                self.domain_mappings[config.custom_domain] = config.id
            
        elif element == BrandingElement.FOOTER:
            config.footer_text = data.get("footer_text")
            config.footer_links = data.get("footer_links", [])
            config.hide_powered_by = data.get("hide_powered_by", False)
            
        elif element == BrandingElement.METADATA:
            config.meta_title = data.get("meta_title")
            config.meta_description = data.get("meta_description")
            config.meta_keywords = data.get("meta_keywords", [])
            config.og_image = data.get("og_image")
        
        config.updated_at = datetime.now()
        
        logger.info(f"Updated {element.value} for white label config {config_id}")
        return config
    
    async def customize_email_template(
        self,
        config_id: str,
        template_type: EmailTemplateType,
        subject: Optional[str] = None,
        html_template: Optional[str] = None,
        text_template: Optional[str] = None
    ) -> EmailTemplate:
        """Customize an email template"""
        
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"White label config {config_id} not found")
        
        # Get or create template
        template = config.email_templates.get(
            template_type,
            self.default_templates.get(template_type)
        )
        
        if not template:
            template = EmailTemplate(
                type=template_type,
                subject=subject or f"{template_type.value} Email",
                html_template=html_template or "",
                text_template=text_template or ""
            )
        
        # Update template
        if subject:
            template.subject = subject
        if html_template:
            template.html_template = html_template
        if text_template:
            template.text_template = text_template
        
        config.email_templates[template_type] = template
        config.updated_at = datetime.now()
        
        logger.info(f"Customized {template_type.value} email template for config {config_id}")
        return template
    
    async def apply_white_label_to_client(
        self,
        client_id: str,
        agency_id: str,
        custom_subdomain: Optional[str] = None
    ) -> ClientWhiteLabel:
        """Apply white label settings to a client"""
        
        # Get agency's white label config
        config = self.configs.get(agency_id)
        if not config:
            raise ValueError(f"No white label config found for agency {agency_id}")
        
        # Create client mapping
        client_wl = ClientWhiteLabel(
            client_id=client_id,
            agency_id=agency_id,
            white_label_config_id=config.id,
            custom_subdomain=custom_subdomain
        )
        
        self.client_mappings[client_id] = client_wl
        
        # Register custom subdomain if provided
        if custom_subdomain:
            full_domain = f"{custom_subdomain}.{config.subdomain}.kenzysites.com"
            self.domain_mappings[full_domain] = config.id
        
        logger.info(f"Applied white label to client {client_id} from agency {agency_id}")
        return client_wl
    
    async def get_config_by_domain(self, domain: str) -> Optional[WhiteLabelConfig]:
        """Get white label config by domain"""
        
        config_id = self.domain_mappings.get(domain)
        if config_id:
            return self.configs.get(config_id)
        
        # Check if it's a subdomain
        parts = domain.split(".")
        if len(parts) > 2:
            # Try agency.kenzysites.com format
            subdomain = parts[0]
            config_id = self.domain_mappings.get(subdomain)
            if config_id:
                return self.configs.get(config_id)
        
        return None
    
    async def get_client_branding(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get branding for a specific client"""
        
        client_wl = self.client_mappings.get(client_id)
        if not client_wl:
            return None
        
        config = self.configs.get(client_wl.white_label_config_id)
        if not config:
            return None
        
        # Return branding data
        return {
            "brand_name": config.brand_name,
            "brand_tagline": config.brand_tagline,
            "logo_url": config.logo_url,
            "favicon_url": config.favicon_url,
            "colors": config.colors.dict(),
            "fonts": config.fonts.dict(),
            "footer_text": config.footer_text,
            "footer_links": config.footer_links,
            "hide_powered_by": config.hide_powered_by,
            "custom_css": config.custom_css,
            "custom_js": config.custom_js
        }
    
    async def render_email_template(
        self,
        config_id: str,
        template_type: EmailTemplateType,
        variables: Dict[str, Any]
    ) -> Dict[str, str]:
        """Render an email template with variables"""
        
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"White label config {config_id} not found")
        
        template = config.email_templates.get(template_type)
        if not template:
            template = self.default_templates.get(template_type)
        
        if not template:
            raise ValueError(f"Template {template_type.value} not found")
        
        # Add branding variables
        variables["brand_name"] = config.brand_name
        variables["primary_color"] = config.colors.primary
        variables["logo_url"] = config.logo_url or ""
        
        # Simple template rendering (in production, use Jinja2 or similar)
        subject = template.subject
        html_body = template.html_template
        text_body = template.text_template
        
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            html_body = html_body.replace(placeholder, str(value))
            text_body = text_body.replace(placeholder, str(value))
        
        return {
            "subject": subject,
            "html_body": html_body,
            "text_body": text_body
        }
    
    async def update_pricing(
        self,
        config_id: str,
        custom_pricing: Dict[str, Any],
        markup_percentage: float = 0.0
    ) -> WhiteLabelConfig:
        """Update custom pricing for white label"""
        
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"White label config {config_id} not found")
        
        config.custom_pricing = custom_pricing
        config.markup_percentage = markup_percentage
        config.hide_original_pricing = True
        config.updated_at = datetime.now()
        
        logger.info(f"Updated pricing for white label config {config_id}")
        return config
    
    async def get_custom_pricing(
        self,
        config_id: str,
        base_price: float
    ) -> float:
        """Calculate custom price with markup"""
        
        config = self.configs.get(config_id)
        if not config:
            return base_price
        
        if config.custom_pricing:
            # Use custom pricing if defined
            return config.custom_pricing.get("price", base_price)
        
        if config.markup_percentage > 0:
            # Apply markup
            return base_price * (1 + config.markup_percentage / 100)
        
        return base_price
    
    async def validate_domain(
        self,
        domain: str,
        config_id: str
    ) -> Dict[str, Any]:
        """Validate custom domain configuration"""
        
        # Check DNS configuration (mock)
        validation = {
            "domain": domain,
            "status": "pending",
            "dns_configured": False,
            "ssl_status": "pending",
            "cname_record": f"wl-{config_id}.kenzysites.com",
            "txt_record": f"kenzysites-verify={hashlib.md5(domain.encode()).hexdigest()[:16]}"
        }
        
        # In production, would check actual DNS records
        # For now, mock as configured
        validation["dns_configured"] = True
        validation["status"] = "active"
        validation["ssl_status"] = "active"
        
        return validation
    
    async def get_analytics(self, config_id: str) -> Dict[str, Any]:
        """Get white label analytics"""
        
        config = self.configs.get(config_id)
        if not config:
            raise ValueError(f"White label config {config_id} not found")
        
        # Count clients using this white label
        client_count = sum(
            1 for client in self.client_mappings.values()
            if client.white_label_config_id == config_id
        )
        
        return {
            "config_id": config_id,
            "agency_id": config.agency_id,
            "brand_name": config.brand_name,
            "tier": config.tier.value,
            "client_count": client_count,
            "custom_domain": config.custom_domain,
            "subdomain": config.subdomain,
            "created_at": config.created_at.isoformat(),
            "last_updated": config.updated_at.isoformat()
        }

# Global instance
white_label_service = WhiteLabelService()