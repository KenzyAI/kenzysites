"""
WordPress Multisite Manager
Manages WordPress Multisite installations with Astra and Spectra
"""

import logging
import httpx
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import base64
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class MultisiteConfig(BaseModel):
    """WordPress Multisite configuration"""
    main_url: str = "http://localhost:8090"
    admin_user: str = "admin"
    admin_password: str = "admin123"
    db_host: str = "multisite-db:3306"
    db_name: str = "wordpress_multisite"
    db_user: str = "wp_multisite"
    db_password: str = "wp_multisite_pass"

class SiteConfig(BaseModel):
    """Configuration for a new WordPress site"""
    subdomain: str
    title: str
    business_type: str
    description: Optional[str] = ""
    admin_email: Optional[str] = "admin@kenzysites.com"
    
    # Astra theme settings
    primary_color: str = "#0274be"
    secondary_color: str = "#002c5f"
    accent_color: str = "#ff5722"
    text_color: str = "#3a3a3a"
    background_color: str = "#ffffff"
    
    # Layout settings
    site_layout: str = "ast-box-layout"  # or ast-full-width-layout
    container_width: int = 1140
    header_layout: str = "header-main-layout-1"
    footer_layout: str = "footer-sml-layout-1"
    
    # Typography
    body_font: str = "Open Sans"
    heading_font: str = "Montserrat"
    
    # Features
    enable_blog: bool = False
    enable_shop: bool = False
    enable_portfolio: bool = False

class SpectraBlock(BaseModel):
    """Spectra block configuration"""
    block_type: str  # section, container, info-box, buttons, etc
    block_id: str
    attributes: Dict[str, Any] = {}
    inner_blocks: List[Dict[str, Any]] = []
    content: str = ""

class PageTemplate(BaseModel):
    """Page template with Spectra blocks"""
    title: str
    slug: str
    template_type: str  # home, about, services, contact, etc
    blocks: List[SpectraBlock]
    meta: Dict[str, Any] = {}

class WordPressMultisiteManager:
    """
    Manages WordPress Multisite with Astra and Spectra
    Creates and configures sites programmatically
    """
    
    def __init__(self, config: Optional[MultisiteConfig] = None):
        self.config = config or MultisiteConfig()
        self.api_base = f"{self.config.main_url}/wp-json"
        self.auth_header = self._create_auth_header()
        
    def _create_auth_header(self) -> str:
        """Create basic auth header"""
        credentials = f"{self.config.admin_user}:{self.config.admin_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    async def create_site(self, site_config: SiteConfig) -> Dict[str, Any]:
        """
        Create a new WordPress site with Astra and Spectra configured
        
        Args:
            site_config: Configuration for the new site
            
        Returns:
            Site creation result with URLs and credentials
        """
        logger.info(f"🚀 Creating WordPress site: {site_config.subdomain}")
        
        try:
            # Step 1: Create site via REST API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/kenzysites/v1/sites/create",
                    json={
                        "domain": site_config.subdomain,
                        "title": site_config.title,
                        "email": site_config.admin_email,
                        "primary_color": site_config.primary_color,
                        "accent_color": site_config.accent_color
                    },
                    headers={"Authorization": self.auth_header},
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to create site: {response.text}")
                    return {"success": False, "error": response.text}
                
                result = response.json()
                site_id = result.get("site_id")
                
            logger.info(f"✅ Site created with ID: {site_id}")
            
            # Step 2: Configure Astra theme settings
            await self._configure_astra_theme(site_id, site_config)
            
            # Step 3: Create pages with Spectra blocks
            await self._create_pages_with_spectra(site_id, site_config)
            
            # Step 4: Configure menus and settings
            await self._configure_site_settings(site_id, site_config)
            
            return {
                "success": True,
                "site_id": site_id,
                "url": f"http://{site_config.subdomain}.localhost:8090",
                "admin_url": f"http://{site_config.subdomain}.localhost:8090/wp-admin",
                "credentials": {
                    "username": self.config.admin_user,
                    "password": self.config.admin_password
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating site: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _configure_astra_theme(self, site_id: int, site_config: SiteConfig):
        """Configure Astra theme settings for the site"""
        
        astra_settings = {
            # Colors
            "theme-color": site_config.primary_color,
            "link-color": site_config.accent_color,
            "text-color": site_config.text_color,
            "header-bg-color": site_config.background_color,
            "footer-bg-color": "#f8f9fa",
            
            # Layout
            "site-layout": site_config.site_layout,
            "container-width": site_config.container_width,
            "header-layouts": site_config.header_layout,
            "footer-sml-layout": site_config.footer_layout,
            
            # Typography
            "body-font-family": site_config.body_font,
            "headings-font-family": site_config.heading_font,
            "font-size-body": 16,
            "line-height-body": 1.6,
            
            # Features based on business type
            "blog-post-structure": ["title", "featured-image", "content"] if site_config.enable_blog else [],
            "shop-product-structure": ["title", "price", "add-to-cart"] if site_config.enable_shop else [],
        }
        
        # Apply settings via API
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.api_base}/kenzysites/v1/sites/{site_id}/configure",
                json={"astra_settings": astra_settings},
                headers={"Authorization": self.auth_header},
                timeout=30.0
            )
        
        logger.info(f"✅ Astra theme configured for site {site_id}")
    
    async def _create_pages_with_spectra(self, site_id: int, site_config: SiteConfig):
        """Create pages using Spectra blocks"""
        
        # Get page templates based on business type
        templates = self._get_business_templates(site_config.business_type)
        
        pages_data = []
        for template in templates:
            # Generate Spectra blocks content
            content = self._generate_spectra_content(template, site_config)
            
            pages_data.append({
                "title": template.title,
                "content": content,
                "meta": template.meta
            })
        
        # Create pages via API
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.api_base}/kenzysites/v1/sites/{site_id}/configure",
                json={"pages": pages_data},
                headers={"Authorization": self.auth_header},
                timeout=30.0
            )
        
        logger.info(f"✅ Created {len(pages_data)} pages with Spectra blocks")
    
    def _get_business_templates(self, business_type: str) -> List[PageTemplate]:
        """Get page templates for specific business type"""
        
        templates_map = {
            "restaurant": self._get_restaurant_templates(),
            "healthcare": self._get_healthcare_templates(),
            "ecommerce": self._get_ecommerce_templates(),
            "services": self._get_services_templates(),
        }
        
        return templates_map.get(business_type, self._get_default_templates())
    
    def _get_restaurant_templates(self) -> List[PageTemplate]:
        """Restaurant-specific page templates"""
        
        return [
            PageTemplate(
                title="Home",
                slug="home",
                template_type="home",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/section",
                        block_id="hero-section",
                        attributes={
                            "backgroundType": "image",
                            "backgroundImage": "restaurant-hero.jpg",
                            "overlayOpacity": 0.6
                        },
                        content="Welcome to Our Restaurant"
                    ),
                    SpectraBlock(
                        block_type="uagb/info-box",
                        block_id="hours-info",
                        attributes={"iconPosition": "left"},
                        content="Open Daily: 11:00 AM - 10:00 PM"
                    ),
                    SpectraBlock(
                        block_type="uagb/buttons",
                        block_id="cta-buttons",
                        inner_blocks=[
                            {"label": "View Menu", "link": "/menu"},
                            {"label": "Book a Table", "link": "/reservations"}
                        ]
                    )
                ]
            ),
            PageTemplate(
                title="Menu",
                slug="menu",
                template_type="menu",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/tabs",
                        block_id="menu-tabs",
                        inner_blocks=[
                            {"title": "Appetizers", "content": "Menu items..."},
                            {"title": "Main Courses", "content": "Menu items..."},
                            {"title": "Desserts", "content": "Menu items..."},
                            {"title": "Beverages", "content": "Menu items..."}
                        ]
                    )
                ]
            ),
            PageTemplate(
                title="Reservations",
                slug="reservations",
                template_type="contact",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/forms",
                        block_id="reservation-form",
                        attributes={"formType": "reservation"}
                    )
                ]
            )
        ]
    
    def _get_healthcare_templates(self) -> List[PageTemplate]:
        """Healthcare-specific page templates"""
        
        return [
            PageTemplate(
                title="Home",
                slug="home",
                template_type="home",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/section",
                        block_id="hero-section",
                        attributes={"backgroundType": "gradient"},
                        content="Your Health, Our Priority"
                    ),
                    SpectraBlock(
                        block_type="uagb/icon-list",
                        block_id="services-list",
                        inner_blocks=[
                            {"icon": "heart", "text": "Cardiology"},
                            {"icon": "brain", "text": "Neurology"},
                            {"icon": "tooth", "text": "Dentistry"}
                        ]
                    )
                ]
            ),
            PageTemplate(
                title="Services",
                slug="services",
                template_type="services",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/post-grid",
                        block_id="services-grid",
                        attributes={"columns": 3, "postType": "service"}
                    )
                ]
            ),
            PageTemplate(
                title="Appointment",
                slug="appointment",
                template_type="booking",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/forms",
                        block_id="appointment-form",
                        attributes={"formType": "appointment"}
                    )
                ]
            )
        ]
    
    def _get_ecommerce_templates(self) -> List[PageTemplate]:
        """E-commerce specific templates"""
        
        return [
            PageTemplate(
                title="Home",
                slug="home",
                template_type="home",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/section",
                        block_id="hero-slider",
                        attributes={"enableSlider": True}
                    ),
                    SpectraBlock(
                        block_type="uagb/post-carousel",
                        block_id="featured-products",
                        attributes={"postType": "product", "columns": 4}
                    )
                ]
            ),
            PageTemplate(
                title="Shop",
                slug="shop",
                template_type="shop",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/post-grid",
                        block_id="products-grid",
                        attributes={"postType": "product", "columns": 3}
                    )
                ]
            )
        ]
    
    def _get_services_templates(self) -> List[PageTemplate]:
        """Generic services templates"""
        
        return [
            PageTemplate(
                title="Home",
                slug="home",
                template_type="home",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/section",
                        block_id="hero-section",
                        content="Professional Services You Can Trust"
                    )
                ]
            ),
            PageTemplate(
                title="Services",
                slug="services",
                template_type="services",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/columns",
                        block_id="services-columns",
                        attributes={"columns": 3}
                    )
                ]
            )
        ]
    
    def _get_default_templates(self) -> List[PageTemplate]:
        """Default templates for any business"""
        
        return [
            PageTemplate(
                title="Home",
                slug="home",
                template_type="home",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/section",
                        block_id="hero",
                        content="Welcome to Our Business"
                    )
                ]
            ),
            PageTemplate(
                title="About",
                slug="about",
                template_type="about",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/info-box",
                        block_id="about-info",
                        content="About Our Company"
                    )
                ]
            ),
            PageTemplate(
                title="Contact",
                slug="contact",
                template_type="contact",
                blocks=[
                    SpectraBlock(
                        block_type="uagb/forms",
                        block_id="contact-form",
                        attributes={"formType": "contact"}
                    )
                ]
            )
        ]
    
    def _generate_spectra_content(self, template: PageTemplate, site_config: SiteConfig) -> str:
        """Generate WordPress Gutenberg + Spectra blocks content"""
        
        content_parts = []
        
        for block in template.blocks:
            block_html = self._generate_spectra_block(block, site_config)
            content_parts.append(block_html)
        
        return "\n\n".join(content_parts)
    
    def _generate_spectra_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate individual Spectra block HTML"""
        
        # Map block types to their HTML structure
        block_generators = {
            "uagb/section": self._generate_section_block,
            "uagb/container": self._generate_container_block,
            "uagb/info-box": self._generate_info_box_block,
            "uagb/buttons": self._generate_buttons_block,
            "uagb/columns": self._generate_columns_block,
            "uagb/forms": self._generate_forms_block,
            "uagb/icon-list": self._generate_icon_list_block,
            "uagb/tabs": self._generate_tabs_block,
            "uagb/post-grid": self._generate_post_grid_block,
            "uagb/post-carousel": self._generate_post_carousel_block,
        }
        
        generator = block_generators.get(block.block_type, self._generate_generic_block)
        return generator(block, site_config)
    
    def _generate_section_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra section block"""
        
        attributes = json.dumps(block.attributes) if block.attributes else ""
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}","attributes":{attributes}}} -->
<div class="wp-block-uagb-section uagb-section__wrap uagb-section__{block.block_id}">
    <div class="uagb-section__inner-wrap">
        <!-- wp:heading {{"level":1}} -->
        <h1>{block.content or site_config.title}</h1>
        <!-- /wp:heading -->
        
        <!-- wp:paragraph -->
        <p>{site_config.description or 'Welcome to our website'}</p>
        <!-- /wp:paragraph -->
    </div>
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_container_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra container block"""
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}"}} -->
<div class="wp-block-uagb-container uagb-container__wrap">
    {block.content}
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_info_box_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra info box block"""
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}"}} -->
<div class="wp-block-uagb-info-box uagb-infobox__wrap">
    <div class="uagb-infobox__content-wrap">
        <h3 class="uagb-infobox__title">{block.content}</h3>
        <p class="uagb-infobox__desc">Professional services tailored to your needs.</p>
    </div>
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_buttons_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra buttons block"""
        
        buttons_html = []
        for btn in block.inner_blocks:
            buttons_html.append(f"""
        <!-- wp:uagb/buttons-child -->
        <div class="wp-block-uagb-buttons-child">
            <a class="uagb-button__link" href="{btn.get('link', '#')}">{btn.get('label', 'Click Here')}</a>
        </div>
        <!-- /wp:uagb/buttons-child -->""")
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}"}} -->
<div class="wp-block-uagb-buttons uagb-buttons__wrap">
    {''.join(buttons_html)}
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_columns_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra columns block"""
        
        columns = block.attributes.get("columns", 3)
        
        columns_html = []
        for i in range(columns):
            columns_html.append(f"""
    <!-- wp:uagb/column -->
    <div class="wp-block-uagb-column uagb-column__wrap">
        <!-- wp:heading {{"level":3}} -->
        <h3>Service {i+1}</h3>
        <!-- /wp:heading -->
        
        <!-- wp:paragraph -->
        <p>Description of service {i+1}</p>
        <!-- /wp:paragraph -->
    </div>
    <!-- /wp:uagb/column -->""")
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}","columns":{columns}}} -->
<div class="wp-block-uagb-columns uagb-columns__wrap">
    {''.join(columns_html)}
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_forms_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra forms block"""
        
        form_type = block.attributes.get("formType", "contact")
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}","formType":"{form_type}"}} -->
<div class="wp-block-uagb-forms uagb-forms__wrap">
    <form class="uagb-forms__form">
        <div class="uagb-forms__field">
            <input type="text" placeholder="Your Name" required />
        </div>
        <div class="uagb-forms__field">
            <input type="email" placeholder="Your Email" required />
        </div>
        <div class="uagb-forms__field">
            <textarea placeholder="Your Message" rows="5" required></textarea>
        </div>
        <div class="uagb-forms__field">
            <button type="submit" class="uagb-forms__submit">Send Message</button>
        </div>
    </form>
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_icon_list_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra icon list block"""
        
        items_html = []
        for item in block.inner_blocks:
            items_html.append(f"""
        <li class="uagb-icon-list__item">
            <span class="uagb-icon-list__icon">{item.get('icon', '✓')}</span>
            <span class="uagb-icon-list__text">{item.get('text', 'Item')}</span>
        </li>""")
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}"}} -->
<div class="wp-block-uagb-icon-list uagb-icon-list__wrap">
    <ul class="uagb-icon-list__list">
        {''.join(items_html)}
    </ul>
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_tabs_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra tabs block"""
        
        tabs_nav = []
        tabs_content = []
        
        for i, tab in enumerate(block.inner_blocks):
            active = "active" if i == 0 else ""
            tabs_nav.append(f'<li class="uagb-tabs__tab {active}">{tab.get("title", f"Tab {i+1}")}</li>')
            tabs_content.append(f"""
        <div class="uagb-tabs__panel {active}">
            {tab.get("content", f"Content for tab {i+1}")}
        </div>""")
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}"}} -->
<div class="wp-block-uagb-tabs uagb-tabs__wrap">
    <ul class="uagb-tabs__nav">
        {''.join(tabs_nav)}
    </ul>
    <div class="uagb-tabs__content">
        {''.join(tabs_content)}
    </div>
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_post_grid_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra post grid block"""
        
        post_type = block.attributes.get("postType", "post")
        columns = block.attributes.get("columns", 3)
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}","postType":"{post_type}","columns":{columns}}} -->
<div class="wp-block-uagb-post-grid uagb-post-grid__wrap">
    <!-- Dynamic content will be loaded here -->
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_post_carousel_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate Spectra post carousel block"""
        
        post_type = block.attributes.get("postType", "post")
        columns = block.attributes.get("columns", 4)
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}","postType":"{post_type}","columns":{columns},"enableSlider":true}} -->
<div class="wp-block-uagb-post-carousel uagb-post-carousel__wrap">
    <!-- Dynamic carousel content will be loaded here -->
</div>
<!-- /wp:{block.block_type} -->"""
    
    def _generate_generic_block(self, block: SpectraBlock, site_config: SiteConfig) -> str:
        """Generate generic Spectra block"""
        
        return f"""<!-- wp:{block.block_type} {{"block_id":"{block.block_id}"}} -->
<div class="wp-block-{block.block_type.replace('/', '-')}">
    {block.content}
</div>
<!-- /wp:{block.block_type} -->"""
    
    async def _configure_site_settings(self, site_id: int, site_config: SiteConfig):
        """Configure additional site settings"""
        
        settings = {
            "blogname": site_config.title,
            "blogdescription": site_config.description,
            "show_on_front": "page",
            "page_on_front": "home",
            "posts_per_page": 10,
            "default_comment_status": "closed",
            "default_ping_status": "closed"
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.api_base}/kenzysites/v1/sites/{site_id}/configure",
                json=settings,
                headers={"Authorization": self.auth_header},
                timeout=30.0
            )
        
        logger.info(f"✅ Site settings configured for site {site_id}")
    
    async def list_sites(self) -> List[Dict[str, Any]]:
        """List all sites in the multisite network"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/kenzysites/v1/sites",
                    headers={"Authorization": self.auth_header},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json().get("sites", [])
                else:
                    logger.error(f"Failed to list sites: {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing sites: {str(e)}")
            return []
    
    async def delete_site(self, site_id: int) -> bool:
        """Delete a site from the multisite network"""
        
        try:
            # Use WP-CLI to delete site (safer than API)
            result = subprocess.run(
                ["docker", "exec", "kenzysites-wpcli", 
                 "wp", "site", "delete", str(site_id), 
                 "--yes", "--allow-root"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Site {site_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete site: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting site: {str(e)}")
            return False
    
    async def export_site(self, site_id: int) -> Optional[bytes]:
        """Export a site as a WordPress export file"""
        
        try:
            # Use WP-CLI to export
            result = subprocess.run(
                ["docker", "exec", "kenzysites-wpcli",
                 "wp", f"--url={site_id}", "export",
                 "--stdout", "--allow-root"],
                capture_output=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Site {site_id} exported successfully")
                return result.stdout
            else:
                logger.error(f"Failed to export site: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting site: {str(e)}")
            return None
    
    async def generate_variations(
        self,
        base_config: SiteConfig,
        variation_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple site variations with different themes and layouts
        
        Args:
            base_config: Base configuration for the site
            variation_count: Number of variations to generate
            
        Returns:
            List of variation configurations
        """
        
        variations = []
        
        # Color schemes for variations
        color_schemes = [
            {"primary": "#007cba", "accent": "#ff6900"},  # WordPress blue
            {"primary": "#d32f2f", "accent": "#ffc107"},  # Red & amber
            {"primary": "#388e3c", "accent": "#ff5722"},  # Green & orange
            {"primary": "#7b1fa2", "accent": "#00bcd4"},  # Purple & cyan
            {"primary": "#f57c00", "accent": "#3f51b5"},  # Orange & indigo
        ]
        
        # Layout variations
        layout_options = [
            {"layout": "ast-box-layout", "width": 1140},
            {"layout": "ast-full-width-layout", "width": 1200},
            {"layout": "ast-padded-layout", "width": 1280},
        ]
        
        # Typography variations
        typography_options = [
            {"heading": "Montserrat", "body": "Open Sans"},
            {"heading": "Playfair Display", "body": "Lato"},
            {"heading": "Roboto", "body": "Source Sans Pro"},
            {"heading": "Poppins", "body": "Inter"},
        ]
        
        for i in range(variation_count):
            # Create variation config
            variation_config = base_config.copy()
            
            # Apply color scheme
            colors = color_schemes[i % len(color_schemes)]
            variation_config.primary_color = colors["primary"]
            variation_config.accent_color = colors["accent"]
            
            # Apply layout
            layout = layout_options[i % len(layout_options)]
            variation_config.site_layout = layout["layout"]
            variation_config.container_width = layout["width"]
            
            # Apply typography
            typography = typography_options[i % len(typography_options)]
            variation_config.heading_font = typography["heading"]
            variation_config.body_font = typography["body"]
            
            # Generate variation
            variation_config.subdomain = f"{base_config.subdomain}-v{i+1}"
            
            variations.append({
                "index": i,
                "name": f"Variation {i+1}",
                "config": variation_config.dict(),
                "preview_url": f"http://{variation_config.subdomain}.localhost:8090"
            })
        
        logger.info(f"✅ Generated {len(variations)} site variations")
        return variations


# Global instance
wordpress_multisite_manager = WordPressMultisiteManager()