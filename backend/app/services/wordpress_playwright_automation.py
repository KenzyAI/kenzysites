"""
WordPress Automation with Playwright
Automates WordPress site creation with Astra and Spectra using browser automation
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import os
from pathlib import Path

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class WordPressCredentials(BaseModel):
    """WordPress admin credentials"""
    url: str = "http://localhost:8090"
    username: str = "admin"
    password: str = "admin123"

class SiteConfiguration(BaseModel):
    """Configuration for site creation"""
    site_name: str
    business_type: str
    tagline: Optional[str] = ""
    
    # Astra customization
    primary_color: str = "#0274be"
    secondary_color: str = "#002c5f"
    accent_color: str = "#ff5722"
    
    # Layout options
    site_layout: str = "boxed"  # boxed, full-width, padded
    container_width: int = 1200
    
    # Typography
    body_font: str = "Open Sans"
    heading_font: str = "Montserrat"
    
    # Content
    pages: List[Dict[str, Any]] = []
    menu_items: List[str] = ["Home", "About", "Services", "Contact"]

class SpectraBlockBuilder:
    """Helper class to build Spectra blocks"""
    
    @staticmethod
    def hero_section(title: str, subtitle: str, button_text: str = "Get Started") -> str:
        """Generate hero section block"""
        return f"""
<!-- wp:uagb/section {{"block_id":"hero-section","backgroundType":"color"}} -->
<div class="wp-block-uagb-section uagb-section__wrap">
    <!-- wp:heading {{"level":1}} -->
    <h1>{title}</h1>
    <!-- /wp:heading -->
    
    <!-- wp:paragraph -->
    <p>{subtitle}</p>
    <!-- /wp:paragraph -->
    
    <!-- wp:uagb/buttons -->
    <div class="wp-block-uagb-buttons">
        <!-- wp:uagb/buttons-child -->
        <div class="wp-block-uagb-buttons-child">
            <a class="uagb-button__link" href="#contact">{button_text}</a>
        </div>
        <!-- /wp:uagb/buttons-child -->
    </div>
    <!-- /wp:uagb/buttons -->
</div>
<!-- /wp:uagb/section -->
"""
    
    @staticmethod
    def services_grid(services: List[Dict[str, str]]) -> str:
        """Generate services grid with Spectra columns"""
        columns_html = []
        for service in services:
            columns_html.append(f"""
    <!-- wp:uagb/column -->
    <div class="wp-block-uagb-column uagb-column__wrap">
        <!-- wp:uagb/info-box -->
        <div class="wp-block-uagb-info-box">
            <h3>{service.get('title', 'Service')}</h3>
            <p>{service.get('description', 'Service description')}</p>
        </div>
        <!-- /wp:uagb/info-box -->
    </div>
    <!-- /wp:uagb/column -->""")
        
        return f"""
<!-- wp:uagb/columns {{"block_id":"services-grid","columns":3}} -->
<div class="wp-block-uagb-columns uagb-columns__wrap">
    {''.join(columns_html)}
</div>
<!-- /wp:uagb/columns -->
"""
    
    @staticmethod
    def contact_form() -> str:
        """Generate contact form block"""
        return """
<!-- wp:uagb/forms {"block_id":"contact-form"} -->
<div class="wp-block-uagb-forms">
    <h3>Get in Touch</h3>
    <form>
        <input type="text" placeholder="Your Name" required />
        <input type="email" placeholder="Your Email" required />
        <textarea placeholder="Your Message" rows="5" required></textarea>
        <button type="submit">Send Message</button>
    </form>
</div>
<!-- /wp:uagb/forms -->
"""

class WordPressPlaywrightAutomation:
    """
    Automates WordPress operations using Playwright
    Creates sites with Astra theme and Spectra blocks
    """
    
    def __init__(self, credentials: Optional[WordPressCredentials] = None):
        self.credentials = credentials or WordPressCredentials()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.block_builder = SpectraBlockBuilder()
        
    async def initialize(self, headless: bool = True):
        """Initialize Playwright browser"""
        logger.info("🎭 Initializing Playwright browser...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        self.page = await self.context.new_page()
        
        # Set longer timeout for slow operations
        self.page.set_default_timeout(60000)
        
        logger.info("✅ Playwright browser initialized")
        
    async def login_to_wordpress(self) -> bool:
        """Login to WordPress admin panel"""
        try:
            logger.info("🔐 Logging into WordPress...")
            
            # Navigate to login page
            await self.page.goto(f"{self.credentials.url}/wp-login.php")
            
            # Fill login form
            await self.page.fill("#user_login", self.credentials.username)
            await self.page.fill("#user_pass", self.credentials.password)
            
            # Submit form
            await self.page.click("#wp-submit")
            
            # Wait for dashboard to load
            await self.page.wait_for_selector("#wpadminbar", timeout=10000)
            
            logger.info("✅ Successfully logged into WordPress")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to login: {str(e)}")
            return False
    
    async def install_astra_theme(self) -> bool:
        """Install and activate Astra theme"""
        try:
            logger.info("🎨 Installing Astra theme...")
            
            # Navigate to themes page
            await self.page.goto(f"{self.credentials.url}/wp-admin/themes.php")
            
            # Check if Astra is already installed
            astra_installed = await self.page.locator('div[data-slug="astra"]').count() > 0
            
            if not astra_installed:
                # Click "Add New"
                await self.page.click('a.page-title-action')
                
                # Search for Astra
                await self.page.fill('#wp-filter-search-input', 'astra')
                await self.page.wait_for_timeout(2000)
                
                # Install Astra
                await self.page.click('div[data-slug="astra"] button.install-now')
                
                # Wait for installation to complete
                await self.page.wait_for_selector('div[data-slug="astra"] button.activate', timeout=30000)
            
            # Activate Astra if not active
            activate_button = self.page.locator('div[data-slug="astra"] button.activate')
            if await activate_button.count() > 0:
                await activate_button.click()
                await self.page.wait_for_timeout(3000)
            
            logger.info("✅ Astra theme installed and activated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to install Astra: {str(e)}")
            return False
    
    async def install_spectra_plugin(self) -> bool:
        """Install and activate Spectra (Ultimate Addons for Gutenberg)"""
        try:
            logger.info("🔌 Installing Spectra plugin...")
            
            # Navigate to plugins page
            await self.page.goto(f"{self.credentials.url}/wp-admin/plugins.php")
            
            # Check if Spectra is already installed
            spectra_installed = await self.page.locator('tr[data-slug="ultimate-addons-for-gutenberg"]').count() > 0
            
            if not spectra_installed:
                # Click "Add New"
                await self.page.click('a.page-title-action')
                
                # Search for Spectra
                await self.page.fill('#search-plugins', 'spectra')
                await self.page.wait_for_timeout(3000)
                
                # Install Spectra
                install_button = self.page.locator('div[data-slug="ultimate-addons-for-gutenberg"] a.install-now')
                await install_button.click()
                
                # Wait for installation
                await self.page.wait_for_selector('div[data-slug="ultimate-addons-for-gutenberg"] a.activate-now', timeout=30000)
            
            # Activate if not active
            activate_button = self.page.locator('div[data-slug="ultimate-addons-for-gutenberg"] a.activate-now')
            if await activate_button.count() > 0:
                await activate_button.click()
                await self.page.wait_for_timeout(3000)
            
            logger.info("✅ Spectra plugin installed and activated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to install Spectra: {str(e)}")
            return False
    
    async def configure_astra_settings(self, config: SiteConfiguration) -> bool:
        """Configure Astra theme settings"""
        try:
            logger.info("⚙️ Configuring Astra theme settings...")
            
            # Navigate to Astra settings
            await self.page.goto(f"{self.credentials.url}/wp-admin/themes.php?page=astra")
            await self.page.wait_for_timeout(2000)
            
            # Navigate to Global Settings > Colors
            colors_link = self.page.locator('a:has-text("Colors")')
            if await colors_link.count() > 0:
                await colors_link.first.click()
                await self.page.wait_for_timeout(2000)
                
                # Set primary color
                primary_input = self.page.locator('input[data-customize-setting-link="astra-settings[theme-color]"]')
                if await primary_input.count() > 0:
                    await primary_input.fill(config.primary_color)
                
                # Set link color
                link_input = self.page.locator('input[data-customize-setting-link="astra-settings[link-color]"]')
                if await link_input.count() > 0:
                    await link_input.fill(config.accent_color)
            
            # Navigate to Typography
            typography_link = self.page.locator('a:has-text("Typography")')
            if await typography_link.count() > 0:
                await typography_link.first.click()
                await self.page.wait_for_timeout(2000)
                
                # Set body font
                body_font_select = self.page.locator('select[data-customize-setting-link="astra-settings[body-font-family]"]')
                if await body_font_select.count() > 0:
                    await body_font_select.select_option(config.body_font)
                
                # Set heading font
                heading_font_select = self.page.locator('select[data-customize-setting-link="astra-settings[headings-font-family]"]')
                if await heading_font_select.count() > 0:
                    await heading_font_select.select_option(config.heading_font)
            
            # Save settings
            save_button = self.page.locator('button:has-text("Publish")')
            if await save_button.count() > 0:
                await save_button.click()
                await self.page.wait_for_timeout(3000)
            
            logger.info("✅ Astra settings configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to configure Astra: {str(e)}")
            return False
    
    async def create_page_with_spectra(
        self,
        title: str,
        content: str,
        template: str = "default"
    ) -> bool:
        """Create a page with Spectra blocks"""
        try:
            logger.info(f"📄 Creating page: {title}")
            
            # Navigate to create new page
            await self.page.goto(f"{self.credentials.url}/wp-admin/post-new.php?post_type=page")
            await self.page.wait_for_timeout(3000)
            
            # Close welcome guide if present
            close_guide = self.page.locator('button[aria-label="Close dialog"]')
            if await close_guide.count() > 0:
                await close_guide.click()
            
            # Set page title
            title_input = self.page.locator('h1[aria-label="Add title"]')
            if await title_input.count() == 0:
                title_input = self.page.locator('textarea[placeholder="Add title"]')
            await title_input.fill(title)
            
            # Switch to code editor to insert Spectra blocks
            await self.page.keyboard.press("Control+Shift+Alt+M")
            await self.page.wait_for_timeout(2000)
            
            # Find the code editor and insert content
            code_editor = self.page.locator('.editor-post-text-editor')
            if await code_editor.count() > 0:
                await code_editor.fill(content)
            else:
                # Fallback: Try to insert via block editor
                await self.page.keyboard.press("Control+Shift+Alt+M")
                await self.page.wait_for_timeout(1000)
                
                # Click on the main editor area
                await self.page.click('.wp-block-post-content')
                
                # Type /html to insert custom HTML block
                await self.page.keyboard.type("/html")
                await self.page.keyboard.press("Enter")
                
                # Insert the content
                await self.page.keyboard.type(content)
            
            # Publish the page
            publish_button = self.page.locator('button:has-text("Publish")')
            await publish_button.first.click()
            await self.page.wait_for_timeout(2000)
            
            # Confirm publish
            confirm_button = self.page.locator('button:has-text("Publish"):visible')
            if await confirm_button.count() > 0:
                await confirm_button.click()
                await self.page.wait_for_timeout(3000)
            
            logger.info(f"✅ Page '{title}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create page: {str(e)}")
            return False
    
    async def create_menu(self, menu_name: str, items: List[str]) -> bool:
        """Create navigation menu"""
        try:
            logger.info(f"🍔 Creating menu: {menu_name}")
            
            # Navigate to menus
            await self.page.goto(f"{self.credentials.url}/wp-admin/nav-menus.php")
            await self.page.wait_for_timeout(2000)
            
            # Create new menu
            await self.page.fill('#menu-name', menu_name)
            await self.page.click('#save_menu_header')
            await self.page.wait_for_timeout(3000)
            
            # Add pages to menu
            for item in items:
                # Find the page checkbox
                page_checkbox = self.page.locator(f'input[type="checkbox"][value*="{item.lower()}"]')
                if await page_checkbox.count() > 0:
                    await page_checkbox.check()
            
            # Add to menu
            add_button = self.page.locator('input[value="Add to Menu"]')
            if await add_button.count() > 0:
                await add_button.first.click()
                await self.page.wait_for_timeout(2000)
            
            # Save menu
            save_button = self.page.locator('input[value="Save Menu"]')
            if await save_button.count() > 0:
                await save_button.click()
                await self.page.wait_for_timeout(3000)
            
            logger.info(f"✅ Menu '{menu_name}' created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create menu: {str(e)}")
            return False
    
    async def create_site(self, config: SiteConfiguration) -> Dict[str, Any]:
        """
        Create a complete WordPress site with Astra and Spectra
        
        Args:
            config: Site configuration
            
        Returns:
            Result dictionary with site details
        """
        try:
            logger.info(f"🚀 Creating site: {config.site_name}")
            start_time = datetime.now()
            
            # Initialize browser if not already done
            if not self.browser:
                await self.initialize()
            
            # Login to WordPress
            if not await self.login_to_wordpress():
                return {"success": False, "error": "Failed to login"}
            
            # Install and activate Astra theme
            if not await self.install_astra_theme():
                return {"success": False, "error": "Failed to install Astra"}
            
            # Install and activate Spectra plugin
            if not await self.install_spectra_plugin():
                return {"success": False, "error": "Failed to install Spectra"}
            
            # Configure Astra settings
            await self.configure_astra_settings(config)
            
            # Create pages with Spectra blocks
            pages_created = []
            
            # Home page
            home_content = self.block_builder.hero_section(
                config.site_name,
                config.tagline or "Welcome to our website",
                "Get Started"
            )
            if await self.create_page_with_spectra("Home", home_content):
                pages_created.append("Home")
            
            # Services page
            services = [
                {"title": "Service 1", "description": "Our first amazing service"},
                {"title": "Service 2", "description": "Our second amazing service"},
                {"title": "Service 3", "description": "Our third amazing service"}
            ]
            services_content = self.block_builder.services_grid(services)
            if await self.create_page_with_spectra("Services", services_content):
                pages_created.append("Services")
            
            # Contact page
            contact_content = self.block_builder.contact_form()
            if await self.create_page_with_spectra("Contact", contact_content):
                pages_created.append("Contact")
            
            # Create menu
            await self.create_menu("Main Menu", config.menu_items)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "site_name": config.site_name,
                "url": self.credentials.url,
                "admin_url": f"{self.credentials.url}/wp-admin",
                "pages_created": pages_created,
                "theme": "Astra",
                "plugins": ["Spectra"],
                "duration": f"{duration:.2f} seconds"
            }
            
            logger.info(f"✅ Site created successfully in {duration:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create site: {str(e)}")
            return {"success": False, "error": str(e)}
        
    async def create_variations(
        self,
        base_config: SiteConfiguration,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Create multiple variations of a site
        
        Args:
            base_config: Base site configuration
            count: Number of variations to create
            
        Returns:
            List of variation results
        """
        variations = []
        
        # Color schemes for variations
        color_schemes = [
            {"primary": "#007cba", "secondary": "#002c5f", "accent": "#ff6900"},
            {"primary": "#d32f2f", "secondary": "#8b0000", "accent": "#ffc107"},
            {"primary": "#388e3c", "secondary": "#1b5e20", "accent": "#ff5722"},
            {"primary": "#7b1fa2", "secondary": "#4a148c", "accent": "#00bcd4"},
            {"primary": "#f57c00", "secondary": "#e65100", "accent": "#3f51b5"}
        ]
        
        # Typography variations
        typography_options = [
            {"body": "Open Sans", "heading": "Montserrat"},
            {"body": "Lato", "heading": "Playfair Display"},
            {"body": "Source Sans Pro", "heading": "Roboto"},
            {"body": "Inter", "heading": "Poppins"}
        ]
        
        # Layout variations
        layout_options = ["boxed", "full-width", "padded"]
        
        for i in range(count):
            # Create variation config
            variation_config = base_config.copy()
            
            # Apply color scheme
            colors = color_schemes[i % len(color_schemes)]
            variation_config.primary_color = colors["primary"]
            variation_config.secondary_color = colors["secondary"]
            variation_config.accent_color = colors["accent"]
            
            # Apply typography
            typography = typography_options[i % len(typography_options)]
            variation_config.body_font = typography["body"]
            variation_config.heading_font = typography["heading"]
            
            # Apply layout
            variation_config.site_layout = layout_options[i % len(layout_options)]
            
            # Update site name for variation
            variation_config.site_name = f"{base_config.site_name} - Variation {i+1}"
            
            # Create the variation
            result = await self.create_site(variation_config)
            result["variation_index"] = i
            result["variation_name"] = f"Variation {i+1}"
            variations.append(result)
            
            # Small delay between variations
            await asyncio.sleep(2)
        
        return variations
    
    async def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot of the current page"""
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        filepath = f"/tmp/{filename}"
        await self.page.screenshot(path=filepath, full_page=True)
        logger.info(f"📸 Screenshot saved: {filepath}")
        return filepath
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
            logger.info("🧹 Browser cleaned up")


# Global instance
wordpress_automation = WordPressPlaywrightAutomation()