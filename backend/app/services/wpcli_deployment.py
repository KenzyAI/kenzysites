"""
WP-CLI Deployment System
Automated WordPress deployment using WP-CLI commands
"""

import asyncio
import subprocess
import logging
import json
import tempfile
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class WPCLIDeployment:
    """
    WordPress deployment using WP-CLI for professional-grade automation
    """
    
    def __init__(self):
        self.wp_container = "kenzysites-wordpress"  # Docker container name
        self.wp_path = "/var/www/html"  # WordPress path inside container
        
        # WP-CLI command templates
        self.wp_cli_base = f"docker exec {self.wp_container} wp --path={self.wp_path}"
        
        # Deployment settings
        self.default_admin_user = "admin"
        self.default_admin_pass = "admin123"
        self.default_admin_email = "admin@kenzysites.local"
        
    async def deploy_blueprint(
        self, 
        blueprint_data: Dict[str, Any], 
        site_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy complete blueprint using WP-CLI
        """
        
        logger.info(f"🚀 Starting WP-CLI deployment for {blueprint_data.get('name')}")
        start_time = datetime.now()
        
        deployment_result = {
            "success": False,
            "steps_completed": [],
            "errors": [],
            "deployment_time": 0,
            "site_url": f"http://localhost:8085",
            "admin_url": f"http://localhost:8085/wp-admin"
        }
        
        try:
            # Step 1: Verify WordPress installation
            await self._verify_wordpress()
            deployment_result["steps_completed"].append("WordPress verification")
            
            # Step 2: Configure site basics
            await self._configure_site_basics(site_config)
            deployment_result["steps_completed"].append("Site configuration")
            
            # Step 3: Install and activate required plugins
            await self._install_required_plugins(blueprint_data.get("configuration", {}).get("plugins", []))
            deployment_result["steps_completed"].append("Plugin installation")
            
            # Step 4: Install and activate theme
            theme = blueprint_data.get("configuration", {}).get("theme", "astra")
            await self._setup_theme(theme)
            deployment_result["steps_completed"].append("Theme setup")
            
            # Step 5: Import content and pages
            await self._import_content(blueprint_data.get("components", []), site_config)
            deployment_result["steps_completed"].append("Content import")
            
            # Step 6: Configure menus
            menus = blueprint_data.get("configuration", {}).get("menus", {})
            await self._setup_menus(menus)
            deployment_result["steps_completed"].append("Menu configuration")
            
            # Step 7: Apply customizer settings
            customizer = blueprint_data.get("configuration", {}).get("customizer", {})
            await self._apply_customizer_settings(customizer)
            deployment_result["steps_completed"].append("Customizer settings")
            
            # Step 8: Optimize and finalize
            await self._finalize_deployment()
            deployment_result["steps_completed"].append("Finalization")
            
            deployment_result["success"] = True
            deployment_time = (datetime.now() - start_time).total_seconds()
            deployment_result["deployment_time"] = round(deployment_time, 2)
            
            logger.info(f"✅ WP-CLI deployment completed in {deployment_time:.2f}s")
            
        except Exception as e:
            error_msg = f"Deployment failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            deployment_result["errors"].append(error_msg)
        
        return deployment_result
    
    async def _verify_wordpress(self):
        """Verify WordPress installation and WP-CLI access"""
        
        try:
            # Check if WordPress is installed
            result = await self._run_wp_command("core is-installed")
            
            if result.returncode != 0:
                # Install WordPress if not installed
                await self._install_fresh_wordpress()
            
            # Verify WP-CLI is working
            version_result = await self._run_wp_command("core version")
            logger.info(f"WordPress version: {version_result.stdout.strip()}")
            
        except Exception as e:
            raise Exception(f"WordPress verification failed: {str(e)}")
    
    async def _install_fresh_wordpress(self):
        """Install fresh WordPress using WP-CLI"""
        
        logger.info("🔧 Installing fresh WordPress...")
        
        # Download WordPress core
        await self._run_wp_command("core download --force")
        
        # Create wp-config.php
        await self._run_wp_command(
            "config create "
            "--dbname=wordpress_local "
            "--dbuser=wp_user "
            "--dbpass=wp_pass "
            "--dbhost=wordpress-db:3306"
        )
        
        # Install WordPress
        await self._run_wp_command(
            f"core install "
            f"--url=http://localhost:8085 "
            f"--title='KenzySites Generated Site' "
            f"--admin_user={self.default_admin_user} "
            f"--admin_password={self.default_admin_pass} "
            f"--admin_email={self.default_admin_email}"
        )
        
        logger.info("✅ Fresh WordPress installed")
    
    async def _configure_site_basics(self, site_config: Dict[str, Any]):
        """Configure basic site settings"""
        
        site_title = site_config.get("site_title", "KenzySites Generated Site")
        site_description = site_config.get("site_description", "Powered by AI")
        
        logger.info(f"⚙️ Configuring site: {site_title}")
        
        # Update site title and tagline
        await self._run_wp_command(f"option update blogname '{site_title}'")
        await self._run_wp_command(f"option update blogdescription '{site_description}'")
        
        # Configure permalinks
        await self._run_wp_command("rewrite structure '/%postname%/' --hard")
        
        # Set timezone
        await self._run_wp_command("option update timezone_string 'America/Sao_Paulo'")
        
        # Configure date/time format (Brazilian)
        await self._run_wp_command("option update date_format 'j/m/Y'")
        await self._run_wp_command("option update time_format 'H:i'")
        
        # Disable default comments
        await self._run_wp_command("option update default_comment_status 'closed'")
        
        logger.info("✅ Site basics configured")
    
    async def _install_required_plugins(self, plugins: List[str]):
        """Install and activate required plugins"""
        
        if not plugins:
            return
        
        logger.info(f"📦 Installing {len(plugins)} plugins...")
        
        # Essential plugins mapping (slug -> name)
        plugin_mapping = {
            "elementor": "elementor",
            "advanced-custom-fields": "advanced-custom-fields", 
            "contact-form-7": "contact-form-7",
            "yoast-seo": "wordpress-seo",
            "woocommerce": "woocommerce",
            "astra-sites": "astra-sites",
            "restaurant-reservations": "restaurant-reservations",
            "appointment-booking": "simply-schedule-appointments",
            "testimonials": "testimonials-widget"
        }
        
        for plugin_slug in plugins:
            try:
                # Map to actual plugin slug
                actual_slug = plugin_mapping.get(plugin_slug, plugin_slug)
                
                # Check if plugin is already installed
                check_result = await self._run_wp_command(f"plugin is-installed {actual_slug}")
                
                if check_result.returncode != 0:
                    # Install plugin
                    logger.info(f"Installing plugin: {plugin_slug}")
                    await self._run_wp_command(f"plugin install {actual_slug}")
                
                # Activate plugin
                await self._run_wp_command(f"plugin activate {actual_slug}")
                logger.info(f"✅ Plugin activated: {plugin_slug}")
                
                # Special configurations for specific plugins
                if plugin_slug == "elementor":
                    await self._configure_elementor()
                elif plugin_slug == "woocommerce":
                    await self._configure_woocommerce()
                
            except Exception as e:
                logger.warning(f"⚠️ Could not install plugin {plugin_slug}: {str(e)}")
    
    async def _configure_elementor(self):
        """Configure Elementor plugin"""
        
        try:
            # Disable Elementor color schemes
            await self._run_wp_command("option update elementor_disable_color_schemes 'yes'")
            
            # Disable Elementor typography schemes  
            await self._run_wp_command("option update elementor_disable_typography_schemes 'yes'")
            
            # Set CSS print method
            await self._run_wp_command("option update elementor_css_print_method 'internal'")
            
            # Disable tracking
            await self._run_wp_command("option update elementor_allow_tracking ''")
            
            logger.info("✅ Elementor configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Elementor configuration failed: {str(e)}")
    
    async def _configure_woocommerce(self):
        """Configure WooCommerce plugin"""
        
        try:
            # Skip WooCommerce setup wizard
            await self._run_wp_command("option update woocommerce_onboarding_opt_in 'no'")
            
            # Set currency to Brazilian Real
            await self._run_wp_command("option update woocommerce_currency 'BRL'")
            
            # Set country/region
            await self._run_wp_command("option update woocommerce_default_country 'BR:SP'")
            
            # Enable guest checkout
            await self._run_wp_command("option update woocommerce_enable_guest_checkout 'yes'")
            
            logger.info("✅ WooCommerce configured for Brazil")
            
        except Exception as e:
            logger.warning(f"⚠️ WooCommerce configuration failed: {str(e)}")
    
    async def _setup_theme(self, theme_slug: str):
        """Install and activate theme"""
        
        logger.info(f"🎨 Setting up theme: {theme_slug}")
        
        try:
            # Check if theme is already installed
            check_result = await self._run_wp_command(f"theme is-installed {theme_slug}")
            
            if check_result.returncode != 0:
                # Install theme
                await self._run_wp_command(f"theme install {theme_slug}")
            
            # Activate theme
            await self._run_wp_command(f"theme activate {theme_slug}")
            
            # Special configuration for Astra theme
            if theme_slug == "astra":
                await self._configure_astra_theme()
            
            logger.info(f"✅ Theme {theme_slug} activated")
            
        except Exception as e:
            logger.warning(f"⚠️ Theme setup failed: {str(e)}")
    
    async def _configure_astra_theme(self):
        """Configure Astra theme settings"""
        
        try:
            # Enable Elementor support
            await self._run_wp_command("option update astra-settings[page-builder-support] 'elementor'")
            
            # Set layout
            await self._run_wp_command("option update astra-settings[site-layout] 'ast-full-width-layout'")
            
            # Configure header
            await self._run_wp_command("option update astra-settings[header-layouts] 'header-main-layout-1'")
            
            logger.info("✅ Astra theme configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Astra configuration failed: {str(e)}")
    
    async def _import_content(self, components: List[Dict[str, Any]], site_config: Dict[str, Any]):
        """Import content and pages from blueprint"""
        
        logger.info(f"📄 Importing {len(components)} pages...")
        
        # Sort components by priority
        sorted_components = sorted(components, key=lambda x: x.get('priority', 0))
        
        home_page_id = None
        
        for component in sorted_components:
            if component.get('type') != 'page':
                continue
            
            try:
                page_title = component.get('name', 'Untitled Page')
                page_content = self._personalize_content(component.get('content', ''), site_config)
                page_slug = component.get('meta', {}).get('slug', '')
                
                # Create page using WP-CLI
                create_cmd = f"post create --post_type=page --post_title='{page_title}' --post_content='{page_content}' --post_status=publish"
                
                if page_slug:
                    create_cmd += f" --post_name='{page_slug}'"
                
                result = await self._run_wp_command(create_cmd)
                
                if result.returncode == 0:
                    # Extract page ID from output
                    page_id = result.stdout.strip().split()[-1] if result.stdout else None
                    
                    # Set as front page if specified
                    if component.get('meta', {}).get('is_front_page'):
                        home_page_id = page_id
                    
                    logger.info(f"✅ Created page: {page_title}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to create page {page_title}: {str(e)}")
        
        # Set front page
        if home_page_id:
            await self._run_wp_command("option update show_on_front 'page'")
            await self._run_wp_command(f"option update page_on_front {home_page_id}")
            logger.info(f"✅ Set homepage: {home_page_id}")
    
    def _personalize_content(self, content: str, site_config: Dict[str, Any]) -> str:
        """Replace placeholders in content with actual values"""
        
        placeholders = {
            '[RESTAURANT_NAME]': site_config.get('business_name', 'Meu Restaurante'),
            '[CLINIC_NAME]': site_config.get('business_name', 'Minha Clínica'),
            '[STORE_NAME]': site_config.get('business_name', 'Minha Loja'),
            '[COMPANY_NAME]': site_config.get('business_name', 'Minha Empresa'),
            '[SCHOOL_NAME]': site_config.get('business_name', 'Minha Escola'),
            '[PHONE]': site_config.get('phone_number', '(11) 99999-9999'),
            '[WHATSAPP]': site_config.get('whatsapp_number', '(11) 99999-9999'),
            '[EMAIL]': site_config.get('email_address', 'contato@exemplo.com.br'),
            '[ADDRESS]': site_config.get('address', 'Rua Exemplo, 123 - São Paulo, SP'),
            '[OPENING_HOURS]': site_config.get('opening_hours', 'Seg-Sex: 8h às 18h'),
            '[CUISINE_TYPE]': site_config.get('cuisine_type', 'brasileira'),
            '[YEARS]': site_config.get('years_experience', '10'),
            '[DELIVERY_AREA]': site_config.get('delivery_area', 'região central')
        }
        
        personalized_content = content
        for placeholder, value in placeholders.items():
            personalized_content = personalized_content.replace(placeholder, value)
        
        return personalized_content
    
    async def _setup_menus(self, menus: Dict[str, List[str]]):
        """Create and assign menus"""
        
        if not menus:
            return
        
        logger.info(f"🧭 Setting up {len(menus)} menus...")
        
        for menu_location, menu_items in menus.items():
            try:
                menu_name = f"{menu_location.title()} Menu"
                
                # Create menu
                await self._run_wp_command(f"menu create '{menu_name}'")
                
                # Add items to menu
                for item in menu_items:
                    # Find page by title
                    page_result = await self._run_wp_command(f"post list --post_type=page --title='{item}' --format=ids")
                    
                    if page_result.returncode == 0 and page_result.stdout.strip():
                        page_id = page_result.stdout.strip()
                        await self._run_wp_command(f"menu item add-post '{menu_name}' {page_id}")
                
                # Assign menu to location
                await self._run_wp_command(f"menu location assign '{menu_name}' {menu_location}")
                
                logger.info(f"✅ Created menu: {menu_name}")
                
            except Exception as e:
                logger.warning(f"⚠️ Menu creation failed for {menu_location}: {str(e)}")
    
    async def _apply_customizer_settings(self, customizer: Dict[str, Any]):
        """Apply customizer/theme settings"""
        
        if not customizer:
            return
        
        logger.info("🎨 Applying customizer settings...")
        
        try:
            # Apply color settings
            colors = customizer.get('colors', {})
            for color_name, color_value in colors.items():
                option_name = f"astra-settings[{color_name}-color]"
                await self._run_wp_command(f"option update '{option_name}' '{color_value}'")
            
            # Apply font settings
            fonts = customizer.get('fonts', {})
            for font_type, font_family in fonts.items():
                option_name = f"astra-settings[{font_type}-font-family]"
                await self._run_wp_command(f"option update '{option_name}' '{font_family}'")
            
            logger.info("✅ Customizer settings applied")
            
        except Exception as e:
            logger.warning(f"⚠️ Customizer configuration failed: {str(e)}")
    
    async def _finalize_deployment(self):
        """Final optimization and cleanup"""
        
        logger.info("🔧 Finalizing deployment...")
        
        try:
            # Flush rewrite rules
            await self._run_wp_command("rewrite flush --hard")
            
            # Update permalink structure
            await self._run_wp_command("rewrite structure '/%postname%/' --hard")
            
            # Clear any caches
            await self._run_wp_command("cache flush", ignore_errors=True)
            
            # Generate thumbnails for images
            await self._run_wp_command("media regenerate --yes", ignore_errors=True)
            
            # Update search index
            await self._run_wp_command("search-replace 'http://localhost' 'http://localhost:8085' --dry-run", ignore_errors=True)
            
            logger.info("✅ Deployment finalized")
            
        except Exception as e:
            logger.warning(f"⚠️ Finalization warning: {str(e)}")
    
    async def _run_wp_command(self, command: str, ignore_errors: bool = False) -> subprocess.CompletedProcess:
        """Run WP-CLI command in Docker container"""
        
        full_command = f"{self.wp_cli_base} {command}"
        
        logger.debug(f"Running: {full_command}")
        
        try:
            # Run command asynchronously
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/"
            )
            
            stdout, stderr = await process.communicate()
            
            result = subprocess.CompletedProcess(
                args=full_command,
                returncode=process.returncode,
                stdout=stdout.decode('utf-8') if stdout else '',
                stderr=stderr.decode('utf-8') if stderr else ''
            )
            
            if result.returncode != 0 and not ignore_errors:
                logger.warning(f"WP-CLI command failed: {command}")
                logger.warning(f"Error: {result.stderr}")
            
            return result
            
        except Exception as e:
            if not ignore_errors:
                raise Exception(f"WP-CLI command execution failed: {str(e)}")
            
            return subprocess.CompletedProcess(
                args=full_command,
                returncode=1,
                stdout='',
                stderr=str(e)
            )
    
    async def export_site(self, export_path: str) -> Dict[str, Any]:
        """Export WordPress site using WP-CLI"""
        
        logger.info(f"📦 Exporting site to {export_path}")
        
        try:
            # Export database
            db_file = f"{export_path}/database.sql"
            await self._run_wp_command(f"db export {db_file}")
            
            # Export uploads
            uploads_cmd = f"docker cp {self.wp_container}:{self.wp_path}/wp-content/uploads {export_path}/"
            await asyncio.create_subprocess_shell(uploads_cmd)
            
            # Export themes
            themes_cmd = f"docker cp {self.wp_container}:{self.wp_path}/wp-content/themes {export_path}/"
            await asyncio.create_subprocess_shell(themes_cmd)
            
            # Export plugins
            plugins_cmd = f"docker cp {self.wp_container}:{self.wp_path}/wp-content/plugins {export_path}/"
            await asyncio.create_subprocess_shell(plugins_cmd)
            
            # Generate site info
            site_info = {
                "exported_at": datetime.now().isoformat(),
                "wp_version": await self._get_wp_version(),
                "active_theme": await self._get_active_theme(),
                "active_plugins": await self._get_active_plugins()
            }
            
            with open(f"{export_path}/site_info.json", 'w') as f:
                json.dump(site_info, f, indent=2)
            
            logger.info("✅ Site exported successfully")
            
            return {
                "success": True,
                "export_path": export_path,
                "files_exported": ["database.sql", "uploads/", "themes/", "plugins/", "site_info.json"]
            }
            
        except Exception as e:
            logger.error(f"❌ Site export failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_wp_version(self) -> str:
        """Get WordPress version"""
        try:
            result = await self._run_wp_command("core version")
            return result.stdout.strip()
        except:
            return "unknown"
    
    async def _get_active_theme(self) -> str:
        """Get active theme"""
        try:
            result = await self._run_wp_command("theme list --status=active --field=name")
            return result.stdout.strip()
        except:
            return "unknown"
    
    async def _get_active_plugins(self) -> List[str]:
        """Get active plugins"""
        try:
            result = await self._run_wp_command("plugin list --status=active --field=name")
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        except:
            return []

# Global instance
wpcli_deployment = WPCLIDeployment()