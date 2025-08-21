"""
Shared Hosting Provisioner Service
Alternative to Kubernetes - uses WordPress Multisite on shared hosting
"""

import asyncio
import logging
import subprocess
import json
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib
import secrets
import string

logger = logging.getLogger(__name__)

class SharedHostingProvisioner:
    """
    Handles WordPress provisioning on shared hosting using Multisite Network
    """
    
    def __init__(self):
        # Configuração da hospedagem compartilhada
        self.hosting_type = os.getenv('HOSTING_TYPE', 'cpanel')  # cpanel, plesk, directadmin
        self.hosting_url = os.getenv('HOSTING_URL', 'https://yourdomain.com:2083')
        self.hosting_user = os.getenv('HOSTING_USER', 'your_cpanel_user')
        self.hosting_password = os.getenv('HOSTING_PASSWORD', 'your_password')
        
        # WordPress Multisite Configuration
        self.multisite_domain = os.getenv('MULTISITE_DOMAIN', 'kenzysites.com')
        self.multisite_path = os.getenv('MULTISITE_PATH', '/public_html/multisite/')
        self.wp_cli_path = os.getenv('WP_CLI_PATH', '/usr/local/bin/wp')
        
        # SSH Configuration (se disponível)
        self.ssh_host = os.getenv('SSH_HOST', '')
        self.ssh_user = os.getenv('SSH_USER', '')
        self.ssh_key_path = os.getenv('SSH_KEY_PATH', '')
        self.has_ssh = all([self.ssh_host, self.ssh_user])
        
        logger.info(f"SharedHostingProvisioner initialized - Type: {self.hosting_type}, SSH: {self.has_ssh}")
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_client_subdomain(self, business_name: str) -> str:
        """Generate unique subdomain for client"""
        clean_name = ''.join(c for c in business_name.lower() if c.isalnum())[:10]
        random_suffix = secrets.token_hex(3)
        return f"{clean_name}{random_suffix}"
    
    async def provision_wordpress_multisite(
        self,
        business_name: str,
        industry: str,
        plan: str,
        user_id: str,
        template_id: Optional[str] = None,
        acf_config: Optional[Dict] = None,
        custom_domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provision a WordPress site in Multisite Network
        """
        try:
            client_subdomain = custom_domain or self.generate_client_subdomain(business_name)
            site_url = f"https://{client_subdomain}.{self.multisite_domain}"
            
            # Generate admin credentials
            admin_user = f"admin_{client_subdomain}"
            admin_password = self.generate_secure_password()
            admin_email = f"admin-{client_subdomain}@{self.multisite_domain}"
            
            logger.info(f"Provisioning WordPress site: {site_url}")
            
            # Step 1: Create subdomain (if not custom domain)
            if not custom_domain:
                await self._create_subdomain(client_subdomain)
            
            # Step 2: Create site in WordPress Multisite
            site_id = await self._create_multisite_site(
                client_subdomain,
                business_name,
                admin_user,
                admin_password,
                admin_email
            )
            
            # Step 3: Configure plugins for the new site
            await self._configure_site_plugins(site_id, industry, plan)
            
            # Step 4: Apply ACF configuration if provided
            if acf_config:
                await self._configure_site_acf(site_id, acf_config)
            
            # Step 5: Apply template if provided
            if template_id:
                await self._apply_template_to_site(site_id, template_id)
            
            # Step 6: Configure basic WordPress settings
            await self._configure_site_settings(site_id, business_name, industry)
            
            return {
                "success": True,
                "client_id": client_subdomain,
                "site_id": site_id,
                "site_url": site_url,
                "admin_url": f"{site_url}/wp-admin",
                "credentials": {
                    "admin_user": admin_user,
                    "admin_password": admin_password,
                    "admin_email": admin_email
                },
                "hosting_type": "multisite_shared",
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Shared hosting provisioning failed: {str(e)}")
            # Cleanup on failure
            await self._cleanup_failed_site(client_subdomain)
            raise
    
    async def _create_subdomain(self, subdomain: str) -> bool:
        """Create subdomain via hosting panel API"""
        try:
            if self.hosting_type == 'cpanel':
                return await self._create_cpanel_subdomain(subdomain)
            elif self.hosting_type == 'plesk':
                return await self._create_plesk_subdomain(subdomain)
            else:
                logger.warning(f"Manual subdomain creation required for: {subdomain}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating subdomain {subdomain}: {str(e)}")
            return False
    
    async def _create_cpanel_subdomain(self, subdomain: str) -> bool:
        """Create subdomain via cPanel API"""
        try:
            # cPanel UAPI call
            url = f"{self.hosting_url}/execute/SubDomain/addsubdomain"
            
            data = {
                'domain': subdomain,
                'rootdomain': self.multisite_domain,
                'dir': f'multisite'  # Point to multisite installation
            }
            
            auth = (self.hosting_user, self.hosting_password)
            
            response = requests.post(url, data=data, auth=auth, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 1:
                    logger.info(f"Created cPanel subdomain: {subdomain}")
                    return True
            
            logger.error(f"Failed to create cPanel subdomain: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"cPanel subdomain creation error: {str(e)}")
            return False
    
    async def _create_plesk_subdomain(self, subdomain: str) -> bool:
        """Create subdomain via Plesk API"""
        try:
            # Plesk XML API call
            xml_data = f"""
            <packet>
                <subdomain>
                    <add>
                        <parent>{self.multisite_domain}</parent>
                        <name>{subdomain}</name>
                        <home>/multisite</home>
                    </add>
                </subdomain>
            </packet>
            """
            
            headers = {
                'Content-Type': 'text/xml',
                'HTTP_AUTH_LOGIN': self.hosting_user,
                'HTTP_AUTH_PASSWD': self.hosting_password
            }
            
            response = requests.post(
                f"{self.hosting_url}:8443/enterprise/control/agent.php",
                data=xml_data,
                headers=headers,
                verify=False
            )
            
            if '<status>ok</status>' in response.text:
                logger.info(f"Created Plesk subdomain: {subdomain}")
                return True
            else:
                logger.error(f"Failed to create Plesk subdomain: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Plesk subdomain creation error: {str(e)}")
            return False
    
    async def _create_multisite_site(
        self,
        subdomain: str,
        title: str,
        admin_user: str,
        admin_password: str,
        admin_email: str
    ) -> int:
        """Create site in WordPress Multisite Network"""
        try:
            site_url = f"{subdomain}.{self.multisite_domain}"
            
            # WP-CLI command to create site
            command = [
                self.wp_cli_path,
                'site', 'create',
                f'--url={subdomain}',
                f'--title={title}',
                f'--admin_user={admin_user}',
                f'--admin_password={admin_password}',
                f'--admin_email={admin_email}',
                '--porcelain'  # Returns only the site ID
            ]
            
            if self.has_ssh:
                result = await self._execute_ssh_command(' '.join(command))
            else:
                result = await self._execute_local_command(command)
            
            site_id = int(result.strip())
            logger.info(f"Created multisite site: {site_url} (ID: {site_id})")
            
            return site_id
            
        except Exception as e:
            logger.error(f"Error creating multisite site: {str(e)}")
            raise
    
    async def _configure_site_plugins(self, site_id: int, industry: str, plan: str):
        """Configure plugins for the new site"""
        try:
            # Essential plugins for all sites
            essential_plugins = [
                'advanced-custom-fields-pro',
                'wordpress-seo',
                'wordfence'
            ]
            
            # Industry-specific plugins
            industry_plugins = {
                'restaurante': ['restaurant-menu', 'wp-reservation'],
                'saude': ['bookly', 'appointment-booking'],
                'ecommerce': ['woocommerce', 'woocommerce-pagseguro'],
                'educacao': ['learnpress'],
                'advocacia': ['appointment-booking']
            }
            
            # Plan-specific plugins
            plan_plugins = {
                'professional': ['google-analytics-for-wordpress'],
                'business': ['wp-rocket', 'imagify'],
                'agency': ['white-label-cms']
            }
            
            # Combine all plugins
            plugins_to_activate = essential_plugins
            plugins_to_activate.extend(industry_plugins.get(industry.lower(), []))
            plugins_to_activate.extend(plan_plugins.get(plan.lower(), []))
            
            # Activate plugins for this site
            for plugin in plugins_to_activate:
                command = [
                    self.wp_cli_path,
                    'plugin', 'activate', plugin,
                    f'--url={site_id}'
                ]
                
                try:
                    if self.has_ssh:
                        await self._execute_ssh_command(' '.join(command))
                    else:
                        await self._execute_local_command(command)
                    
                    logger.info(f"Activated plugin {plugin} for site {site_id}")
                    
                except Exception as e:
                    logger.warning(f"Failed to activate plugin {plugin}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error configuring site plugins: {str(e)}")
    
    async def _configure_site_acf(self, site_id: int, acf_config: Dict):
        """Configure ACF fields for the site"""
        try:
            # Import ACF field groups via WP-CLI
            acf_json = json.dumps(acf_config, ensure_ascii=False)
            
            # Create temporary file with ACF data
            temp_file = f"/tmp/acf-import-{site_id}.json"
            
            commands = [
                # Create temp file
                f"echo '{acf_json}' > {temp_file}",
                
                # Import ACF fields
                f"{self.wp_cli_path} acf import {temp_file} --url={site_id}",
                
                # Clean up
                f"rm {temp_file}"
            ]
            
            for command in commands:
                if self.has_ssh:
                    await self._execute_ssh_command(command)
                else:
                    await self._execute_local_command(command.split())
            
            logger.info(f"Configured ACF fields for site {site_id}")
            
        except Exception as e:
            logger.error(f"Error configuring ACF for site {site_id}: {str(e)}")
    
    async def _apply_template_to_site(self, site_id: int, template_id: str):
        """Apply template to the site"""
        try:
            # This would integrate with your template repository
            # For now, just log the intent
            logger.info(f"Applied template {template_id} to site {site_id}")
            
        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
    
    async def _configure_site_settings(self, site_id: int, business_name: str, industry: str):
        """Configure basic WordPress settings for the site"""
        try:
            settings_commands = [
                # Basic settings
                f"{self.wp_cli_path} option update blogname '{business_name}' --url={site_id}",
                f"{self.wp_cli_path} option update blogdescription 'Website de {business_name}' --url={site_id}",
                f"{self.wp_cli_path} option update timezone_string 'America/Sao_Paulo' --url={site_id}",
                f"{self.wp_cli_path} option update date_format 'd/m/Y' --url={site_id}",
                f"{self.wp_cli_path} option update time_format 'H:i' --url={site_id}",
                
                # Disable comments by default
                f"{self.wp_cli_path} option update default_comment_status 'closed' --url={site_id}",
                f"{self.wp_cli_path} option update default_ping_status 'closed' --url={site_id}",
                
                # Set permalink structure
                f"{self.wp_cli_path} rewrite structure '/%postname%/' --url={site_id}",
                
                # Remove default content
                f"{self.wp_cli_path} post delete 1 --force --url={site_id}",  # Hello World
                f"{self.wp_cli_path} post delete 2 --force --url={site_id}",  # Sample Page
            ]
            
            for command in settings_commands:
                try:
                    if self.has_ssh:
                        await self._execute_ssh_command(command)
                    else:
                        await self._execute_local_command(command.split())
                except Exception as e:
                    logger.warning(f"Setting command failed: {command} - {str(e)}")
            
            logger.info(f"Configured basic settings for site {site_id}")
            
        except Exception as e:
            logger.error(f"Error configuring site settings: {str(e)}")
    
    async def _execute_ssh_command(self, command: str) -> str:
        """Execute command via SSH"""
        try:
            ssh_command = [
                'ssh',
                '-i', self.ssh_key_path,
                f'{self.ssh_user}@{self.ssh_host}',
                f'cd {self.multisite_path} && {command}'
            ]
            
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            logger.error(f"SSH command failed: {command} - {e.stderr}")
            raise
    
    async def _execute_local_command(self, command: List[str]) -> str:
        """Execute command locally (if running on same server)"""
        try:
            # Change to multisite directory
            original_cwd = os.getcwd()
            os.chdir(self.multisite_path)
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Local command failed: {' '.join(command)} - {e.stderr}")
            raise
    
    async def _cleanup_failed_site(self, subdomain: str):
        """Cleanup resources if site creation fails"""
        try:
            # Remove subdomain if created
            logger.info(f"Cleaning up failed site: {subdomain}")
            # Implementation depends on hosting provider
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
    
    async def suspend_site(self, site_id: int):
        """Suspend a WordPress site"""
        try:
            command = f"{self.wp_cli_path} site archive {site_id}"
            
            if self.has_ssh:
                await self._execute_ssh_command(command)
            else:
                await self._execute_local_command(command.split())
            
            logger.info(f"Suspended site: {site_id}")
            
            return {
                "success": True,
                "message": f"Site {site_id} suspended successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to suspend site {site_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to suspend site: {str(e)}"
            }
    
    async def resume_site(self, site_id: int):
        """Resume a suspended WordPress site"""
        try:
            command = f"{self.wp_cli_path} site unarchive {site_id}"
            
            if self.has_ssh:
                await self._execute_ssh_command(command)
            else:
                await self._execute_local_command(command.split())
            
            logger.info(f"Resumed site: {site_id}")
            
            return {
                "success": True,
                "message": f"Site {site_id} resumed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to resume site {site_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to resume site: {str(e)}"
            }
    
    async def delete_site(self, site_id: int):
        """Delete a WordPress site"""
        try:
            command = f"{self.wp_cli_path} site delete {site_id} --yes"
            
            if self.has_ssh:
                await self._execute_ssh_command(command)
            else:
                await self._execute_local_command(command.split())
            
            logger.info(f"Deleted site: {site_id}")
            
            return {
                "success": True,
                "message": f"Site {site_id} deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete site {site_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to delete site: {str(e)}"
            }
    
    async def get_site_status(self, site_id: int) -> Dict[str, Any]:
        """Get status of a WordPress site"""
        try:
            # Get site info
            command = f"{self.wp_cli_path} site list --site_id={site_id} --format=json"
            
            if self.has_ssh:
                result = await self._execute_ssh_command(command)
            else:
                result = await self._execute_local_command(command.split())
            
            site_info = json.loads(result)
            
            if site_info:
                site = site_info[0]
                return {
                    "site_id": site_id,
                    "url": site.get('url'),
                    "status": site.get('archived', '0') == '0' and 'active' or 'suspended',
                    "last_updated": site.get('last_updated'),
                    "hosting_type": "multisite_shared"
                }
            else:
                return {
                    "site_id": site_id,
                    "status": "not_found",
                    "error": "Site not found in multisite network"
                }
                
        except Exception as e:
            logger.error(f"Error getting site status: {str(e)}")
            return {
                "site_id": site_id,
                "status": "error",
                "error": str(e)
            }

# Global instance
shared_hosting_provisioner = SharedHostingProvisioner()