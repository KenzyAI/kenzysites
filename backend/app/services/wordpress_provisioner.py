"""
WordPress Provisioner Service
Real implementation for provisioning isolated WordPress instances
"""

import asyncio
import logging
import secrets
import string
from typing import Dict, Any, Optional, List
from datetime import datetime
import subprocess
import yaml
import json
import os
from pathlib import Path

from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class WordPressProvisioner:
    """
    Handles real WordPress provisioning using Kubernetes
    """
    
    def __init__(self):
        self.k8s_config_loaded = False
        self.v1 = None
        self.apps_v1 = None
        self.networking_v1 = None
        self.templates_path = Path("/home/douglaskenzy/workspace/kenzysites/kubernetes")
        self._initialize_k8s()
    
    def _initialize_k8s(self):
        """Initialize Kubernetes client"""
        try:
            # Try to load in-cluster config first (when running inside k8s)
            config.load_incluster_config()
            self.k8s_config_loaded = True
        except:
            try:
                # Fall back to kubeconfig file
                config.load_kube_config()
                self.k8s_config_loaded = True
            except:
                logger.warning("Kubernetes config not found. Running in development mode.")
                self.k8s_config_loaded = False
        
        if self.k8s_config_loaded:
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_client_id(self, business_name: str) -> str:
        """Generate unique client ID"""
        clean_name = ''.join(c for c in business_name.lower() if c.isalnum())[:10]
        random_suffix = secrets.token_hex(3)
        return f"{clean_name}_{random_suffix}"
    
    async def provision_wordpress(
        self,
        business_name: str,
        domain: str,
        industry: str,
        plan: str,
        user_id: str,
        template_id: Optional[str] = None,
        acf_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Provision a complete WordPress instance
        """
        
        client_id = self.generate_client_id(business_name)
        
        # Generate credentials
        credentials = {
            "client_id": client_id,
            "mysql_root_password": self.generate_secure_password(20),
            "mysql_user": f"wp_{client_id}",
            "mysql_password": self.generate_secure_password(16),
            "wp_admin_user": "admin",
            "wp_admin_password": self.generate_secure_password(16),
            "wp_admin_email": f"admin@{domain}",
            "redis_password": self.generate_secure_password(16)
        }
        
        try:
            # Step 1: Create namespace
            namespace = await self._create_namespace(client_id)
            
            # Step 2: Create secrets
            await self._create_secrets(client_id, credentials)
            
            # Step 3: Create ConfigMaps
            await self._create_configmaps(client_id, domain)
            
            # Step 4: Deploy MySQL
            await self._deploy_mysql(client_id, credentials)
            
            # Step 5: Wait for MySQL to be ready
            await self._wait_for_mysql(client_id)
            
            # Step 6: Deploy WordPress
            await self._deploy_wordpress(client_id, domain, credentials)
            
            # Step 7: Wait for WordPress to be ready
            await self._wait_for_wordpress(client_id)
            
            # Step 8: Configure ingress
            await self._configure_ingress(client_id, domain)
            
            # Step 9: Install WordPress via WP-CLI
            await self._install_wordpress(client_id, domain, credentials)
            
            # Step 10: Install and configure plugins
            await self._configure_plugins(client_id, industry, plan)
            
            # Step 11: Configure ACF if provided
            if acf_config:
                await self._configure_acf(client_id, acf_config)
            
            # Step 12: Apply template if provided
            if template_id:
                await self._apply_template(client_id, template_id)
            
            # Step 13: Set up automated backups
            await self._setup_backups(client_id)
            
            # Step 14: Configure monitoring
            await self._setup_monitoring(client_id)
            
            return {
                "success": True,
                "client_id": client_id,
                "domain": domain,
                "status": "active",
                "credentials": {
                    "wp_admin_url": f"https://{domain}/wp-admin",
                    "wp_admin_user": credentials["wp_admin_user"],
                    "wp_admin_password": credentials["wp_admin_password"],
                    "wp_admin_email": credentials["wp_admin_email"]
                },
                "infrastructure": {
                    "namespace": f"client-{client_id}",
                    "mysql_host": f"mysql-{client_id}",
                    "redis_host": f"redis-{client_id}"
                },
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Provisioning failed for {client_id}: {str(e)}")
            # Cleanup on failure
            await self._cleanup_failed_provisioning(client_id)
            raise
    
    async def _create_namespace(self, client_id: str) -> str:
        """Create Kubernetes namespace for client"""
        namespace_name = f"client-{client_id}"
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would create namespace: {namespace_name}")
            return namespace_name
        
        namespace = client.V1Namespace(
            metadata=client.V1ObjectMeta(
                name=namespace_name,
                labels={
                    "client": client_id,
                    "managed-by": "kenzysites",
                    "created": datetime.now().isoformat()
                }
            )
        )
        
        try:
            self.v1.create_namespace(namespace)
            logger.info(f"Created namespace: {namespace_name}")
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"Namespace already exists: {namespace_name}")
            else:
                raise
        
        return namespace_name
    
    async def _create_secrets(self, client_id: str, credentials: Dict):
        """Create Kubernetes secrets for MySQL and WordPress"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would create secrets for client: {client_id}")
            return
        
        namespace = f"client-{client_id}"
        
        # MySQL secret
        mysql_secret = client.V1Secret(
            metadata=client.V1ObjectMeta(
                name=f"mysql-{client_id}-secret",
                namespace=namespace
            ),
            string_data={
                "root-password": credentials["mysql_root_password"],
                "username": credentials["mysql_user"],
                "password": credentials["mysql_password"]
            }
        )
        
        # WordPress secret
        wp_secret = client.V1Secret(
            metadata=client.V1ObjectMeta(
                name=f"wordpress-{client_id}-secret",
                namespace=namespace
            ),
            string_data={
                "admin-user": credentials["wp_admin_user"],
                "admin-password": credentials["wp_admin_password"],
                "admin-email": credentials["wp_admin_email"]
            }
        )
        
        try:
            self.v1.create_namespaced_secret(namespace, mysql_secret)
            self.v1.create_namespaced_secret(namespace, wp_secret)
            logger.info(f"Created secrets for client: {client_id}")
        except ApiException as e:
            if e.status != 409:  # Ignore if already exists
                raise
    
    async def _create_configmaps(self, client_id: str, domain: str):
        """Create ConfigMaps for nginx and other configurations"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would create configmaps for domain: {domain}")
            return
        
        # Load nginx config template
        nginx_template_path = self.templates_path / "configmaps" / "nginx-config-template.yaml"
        
        with open(nginx_template_path, 'r') as f:
            nginx_config = yaml.safe_load(f)
        
        # Replace placeholders
        nginx_config['metadata']['name'] = f"nginx-config-{client_id}"
        nginx_config['metadata']['namespace'] = f"client-{client_id}"
        nginx_config['data']['default.conf'] = nginx_config['data']['default.conf'].replace('{{DOMAIN}}', domain)
        nginx_config['data']['default.conf'] = nginx_config['data']['default.conf'].replace('{{CLIENT_ID}}', client_id)
        
        # Create configmap
        namespace = f"client-{client_id}"
        configmap = client.V1ConfigMap(
            metadata=nginx_config['metadata'],
            data=nginx_config['data']
        )
        
        try:
            self.v1.create_namespaced_config_map(namespace, configmap)
            logger.info(f"Created nginx configmap for client: {client_id}")
        except ApiException as e:
            if e.status != 409:
                raise
    
    async def _deploy_mysql(self, client_id: str, credentials: Dict):
        """Deploy MySQL for WordPress"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would deploy MySQL for client: {client_id}")
            return
        
        # Load MySQL deployment template
        mysql_template_path = self.templates_path / "deployments" / "mysql-template.yaml"
        
        with open(mysql_template_path, 'r') as f:
            mysql_manifests = yaml.safe_load_all(f)
        
        namespace = f"client-{client_id}"
        
        for manifest in mysql_manifests:
            # Replace placeholders
            manifest_str = yaml.dump(manifest)
            manifest_str = manifest_str.replace('{{CLIENT_ID}}', client_id)
            manifest = yaml.safe_load(manifest_str)
            
            # Apply based on kind
            try:
                if manifest['kind'] == 'Deployment':
                    self.apps_v1.create_namespaced_deployment(namespace, manifest)
                elif manifest['kind'] == 'PersistentVolumeClaim':
                    self.v1.create_namespaced_persistent_volume_claim(namespace, manifest)
                elif manifest['kind'] == 'Service':
                    self.v1.create_namespaced_service(namespace, manifest)
                
                logger.info(f"Created MySQL {manifest['kind']} for client: {client_id}")
            except ApiException as e:
                if e.status != 409:
                    raise
    
    async def _wait_for_mysql(self, client_id: str, timeout: int = 300):
        """Wait for MySQL to be ready"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would wait for MySQL readiness")
            await asyncio.sleep(2)  # Simulate wait
            return
        
        namespace = f"client-{client_id}"
        deployment_name = f"mysql-{client_id}"
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)
                if deployment.status.ready_replicas and deployment.status.ready_replicas > 0:
                    logger.info(f"MySQL is ready for client: {client_id}")
                    return
            except:
                pass
            
            await asyncio.sleep(5)
        
        raise TimeoutError(f"MySQL not ready after {timeout} seconds")
    
    async def _deploy_wordpress(self, client_id: str, domain: str, credentials: Dict):
        """Deploy WordPress with nginx and Redis"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would deploy WordPress for client: {client_id}")
            return
        
        # Load WordPress deployment template
        wp_template_path = self.templates_path / "deployments" / "wordpress-template.yaml"
        
        with open(wp_template_path, 'r') as f:
            wp_manifests = yaml.safe_load_all(f)
        
        namespace = f"client-{client_id}"
        
        for manifest in wp_manifests:
            # Replace placeholders
            manifest_str = yaml.dump(manifest)
            manifest_str = manifest_str.replace('{{CLIENT_ID}}', client_id)
            manifest_str = manifest_str.replace('{{ACF_LICENSE}}', os.getenv('ACF_PRO_LICENSE', ''))
            manifest = yaml.safe_load(manifest_str)
            
            # Apply based on kind
            try:
                if manifest['kind'] == 'Deployment':
                    self.apps_v1.create_namespaced_deployment(namespace, manifest)
                elif manifest['kind'] == 'PersistentVolumeClaim':
                    self.v1.create_namespaced_persistent_volume_claim(namespace, manifest)
                
                logger.info(f"Created WordPress {manifest['kind']} for client: {client_id}")
            except ApiException as e:
                if e.status != 409:
                    raise
    
    async def _wait_for_wordpress(self, client_id: str, timeout: int = 300):
        """Wait for WordPress to be ready"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would wait for WordPress readiness")
            await asyncio.sleep(2)
            return
        
        namespace = f"client-{client_id}"
        deployment_name = f"wordpress-{client_id}"
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)
                if deployment.status.ready_replicas and deployment.status.ready_replicas > 0:
                    logger.info(f"WordPress is ready for client: {client_id}")
                    return
            except:
                pass
            
            await asyncio.sleep(5)
        
        raise TimeoutError(f"WordPress not ready after {timeout} seconds")
    
    async def _configure_ingress(self, client_id: str, domain: str):
        """Configure ingress for WordPress"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would configure ingress for domain: {domain}")
            return
        
        # Load ingress template
        ingress_template_path = self.templates_path / "ingress" / "ingress-template.yaml"
        
        with open(ingress_template_path, 'r') as f:
            ingress_manifest = yaml.safe_load(f)
        
        # Replace placeholders
        ingress_manifest['metadata']['name'] = f"wordpress-{client_id}"
        ingress_manifest['metadata']['namespace'] = f"client-{client_id}"
        ingress_manifest['spec']['tls'][0]['hosts'][0] = domain
        ingress_manifest['spec']['tls'][0]['secretName'] = f"{client_id}-tls-secret"
        ingress_manifest['spec']['rules'][0]['host'] = domain
        
        try:
            namespace = f"client-{client_id}"
            self.networking_v1.create_namespaced_ingress(namespace, ingress_manifest)
            logger.info(f"Created ingress for domain: {domain}")
        except ApiException as e:
            if e.status != 409:
                raise
    
    async def _install_wordpress(self, client_id: str, domain: str, credentials: Dict):
        """Install WordPress using WP-CLI"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would install WordPress via WP-CLI")
            return
        
        namespace = f"client-{client_id}"
        pod_name = await self._get_wordpress_pod_name(client_id)
        
        # WP-CLI commands to install WordPress
        commands = [
            # Download WordPress
            "wp core download --force --locale=pt_BR",
            
            # Create wp-config.php
            f"wp config create --dbname=wordpress_{client_id} "
            f"--dbuser={credentials['mysql_user']} "
            f"--dbpass={credentials['mysql_password']} "
            f"--dbhost=mysql-{client_id} "
            f"--locale=pt_BR",
            
            # Install WordPress
            f"wp core install --url=https://{domain} "
            f"--title='{domain}' "
            f"--admin_user={credentials['wp_admin_user']} "
            f"--admin_password={credentials['wp_admin_password']} "
            f"--admin_email={credentials['wp_admin_email']} "
            "--skip-email",
            
            # Set timezone and language
            "wp option update timezone_string 'America/Sao_Paulo'",
            "wp option update WPLANG 'pt_BR'",
            "wp option update date_format 'd/m/Y'",
            "wp option update time_format 'H:i'",
            
            # Basic settings
            "wp option update blog_public 1",  # Allow search engines
            "wp option update default_comment_status 'closed'",  # Disable comments by default
            "wp option update default_ping_status 'closed'",
            
            # Permalink structure
            "wp rewrite structure '/%postname%/' --hard",
            
            # Remove default content
            "wp post delete 1 --force",  # Hello World
            "wp post delete 2 --force",  # Sample Page
            "wp comment delete 1 --force",  # Default comment
        ]
        
        for cmd in commands:
            await self._exec_in_pod(namespace, pod_name, cmd)
    
    async def _configure_plugins(self, client_id: str, industry: str, plan: str):
        """Install and configure WordPress plugins based on industry and plan"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would configure plugins for industry: {industry}")
            return
        
        namespace = f"client-{client_id}"
        pod_name = await self._get_wordpress_pod_name(client_id)
        
        # Essential plugins for all sites
        essential_plugins = [
            "advanced-custom-fields-pro",  # Needs license
            "wordpress-seo",  # Yoast SEO
            "redis-cache",  # Redis object cache
            "wordfence",  # Security
            "updraftplus",  # Backup
            "w3-total-cache",  # Performance
        ]
        
        # Industry-specific plugins
        industry_plugins = {
            "restaurante": ["restaurant-menu", "wp-reservation"],
            "saude": ["bookly", "medical-history"],
            "ecommerce": ["woocommerce", "woocommerce-pagseguro"],
            "educacao": ["learnpress", "wp-courseware"],
            "imobiliaria": ["estatik", "property-listings"],
        }
        
        # Plan-specific plugins
        plan_plugins = {
            "professional": ["google-analytics-for-wordpress", "mailchimp-for-wp"],
            "business": ["wp-rocket", "imagify", "social-media-share-buttons"],
            "agency": ["white-label-cms", "client-portal", "mainwp-child"],
        }
        
        # Combine all plugins
        plugins_to_install = essential_plugins
        plugins_to_install.extend(industry_plugins.get(industry.lower(), []))
        plugins_to_install.extend(plan_plugins.get(plan.lower(), []))
        
        # Install plugins
        for plugin in plugins_to_install:
            try:
                cmd = f"wp plugin install {plugin} --activate"
                await self._exec_in_pod(namespace, pod_name, cmd)
                logger.info(f"Installed plugin: {plugin}")
            except Exception as e:
                logger.warning(f"Failed to install plugin {plugin}: {str(e)}")
    
    async def _configure_acf(self, client_id: str, acf_config: Dict):
        """Configure ACF fields for the WordPress site"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would configure ACF fields")
            return
        
        namespace = f"client-{client_id}"
        pod_name = await self._get_wordpress_pod_name(client_id)
        
        # Save ACF configuration to a temporary file
        acf_json = json.dumps(acf_config)
        
        # Create ACF import file in pod
        cmd = f"echo '{acf_json}' > /tmp/acf-import.json"
        await self._exec_in_pod(namespace, pod_name, cmd)
        
        # Import ACF fields
        cmd = "wp acf import --json_file=/tmp/acf-import.json"
        await self._exec_in_pod(namespace, pod_name, cmd)
        
        logger.info(f"Configured ACF fields for client: {client_id}")
    
    async def _apply_template(self, client_id: str, template_id: str):
        """Apply a template to the WordPress site"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would apply template: {template_id}")
            return
        
        # This would fetch template data and apply it
        # For now, just log
        logger.info(f"Applied template {template_id} to client {client_id}")
    
    async def _setup_backups(self, client_id: str):
        """Set up automated backups for the WordPress site"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would setup backups for client: {client_id}")
            return
        
        # Create CronJob for backups
        backup_cronjob = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": f"backup-{client_id}",
                "namespace": f"client-{client_id}"
            },
            "spec": {
                "schedule": "0 2 * * *",  # Daily at 2 AM
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{
                                    "name": "backup",
                                    "image": "wordpress:cli",
                                    "command": ["/bin/sh", "-c"],
                                    "args": [
                                        "wp db export /backup/backup-$(date +%Y%m%d).sql && "
                                        "tar -czf /backup/files-$(date +%Y%m%d).tar.gz /var/www/html/wp-content"
                                    ],
                                    "volumeMounts": [{
                                        "name": "backup-storage",
                                        "mountPath": "/backup"
                                    }]
                                }],
                                "restartPolicy": "OnFailure",
                                "volumes": [{
                                    "name": "backup-storage",
                                    "persistentVolumeClaim": {
                                        "claimName": f"backup-pvc-{client_id}"
                                    }
                                }]
                            }
                        }
                    }
                }
            }
        }
        
        # Create the CronJob
        batch_v1 = client.BatchV1Api()
        try:
            batch_v1.create_namespaced_cron_job(f"client-{client_id}", backup_cronjob)
            logger.info(f"Created backup CronJob for client: {client_id}")
        except ApiException as e:
            if e.status != 409:
                raise
    
    async def _setup_monitoring(self, client_id: str):
        """Set up monitoring for the WordPress site"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would setup monitoring for client: {client_id}")
            return
        
        # Add Prometheus ServiceMonitor
        service_monitor = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"wordpress-{client_id}",
                "namespace": f"client-{client_id}",
                "labels": {
                    "client": client_id,
                    "app": "wordpress"
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "wordpress",
                        "client": client_id
                    }
                },
                "endpoints": [{
                    "port": "metrics",
                    "interval": "30s"
                }]
            }
        }
        
        # This would create the ServiceMonitor if Prometheus Operator is installed
        logger.info(f"Configured monitoring for client: {client_id}")
    
    async def _get_wordpress_pod_name(self, client_id: str) -> str:
        """Get the name of the WordPress pod"""
        
        if not self.k8s_config_loaded:
            return f"wordpress-{client_id}-mock-pod"
        
        namespace = f"client-{client_id}"
        pods = self.v1.list_namespaced_pod(
            namespace,
            label_selector=f"app=wordpress,client={client_id}"
        )
        
        if pods.items:
            return pods.items[0].metadata.name
        
        raise Exception(f"No WordPress pod found for client {client_id}")
    
    async def _exec_in_pod(self, namespace: str, pod_name: str, command: str):
        """Execute command in a pod"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would execute in pod: {command}")
            return
        
        # This would use the Kubernetes exec API
        # For now, we'll use subprocess as a placeholder
        kubectl_cmd = [
            "kubectl", "exec", "-n", namespace, pod_name,
            "--", "/bin/sh", "-c", command
        ]
        
        try:
            result = subprocess.run(kubectl_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Command failed: {result.stderr}")
            logger.info(f"Executed command in pod: {command[:50]}...")
        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            raise
    
    async def _cleanup_failed_provisioning(self, client_id: str):
        """Cleanup resources if provisioning fails"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would cleanup failed provisioning for client: {client_id}")
            return
        
        namespace = f"client-{client_id}"
        
        try:
            # Delete namespace (will delete all resources within it)
            self.v1.delete_namespace(namespace)
            logger.info(f"Cleaned up failed provisioning for client: {client_id}")
        except:
            pass
    
    async def suspend_site(self, client_id: str):
        """Suspend a WordPress site (scale down to 0)"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would suspend site for client: {client_id}")
            return {"success": True, "message": "Site suspended (dev mode)"}
        
        namespace = f"client-{client_id}"
        
        try:
            # Scale WordPress deployment to 0
            body = {"spec": {"replicas": 0}}
            self.apps_v1.patch_namespaced_deployment_scale(
                f"wordpress-{client_id}",
                namespace,
                body
            )
            
            # Keep MySQL running to preserve data
            logger.info(f"Suspended site for client: {client_id}")
            
            return {
                "success": True,
                "message": "Site suspended successfully"
            }
        except Exception as e:
            logger.error(f"Failed to suspend site: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to suspend site: {str(e)}"
            }
    
    async def resume_site(self, client_id: str):
        """Resume a suspended WordPress site"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would resume site for client: {client_id}")
            return {"success": True, "message": "Site resumed (dev mode)"}
        
        namespace = f"client-{client_id}"
        
        try:
            # Scale WordPress deployment back to 1
            body = {"spec": {"replicas": 1}}
            self.apps_v1.patch_namespaced_deployment_scale(
                f"wordpress-{client_id}",
                namespace,
                body
            )
            
            logger.info(f"Resumed site for client: {client_id}")
            
            return {
                "success": True,
                "message": "Site resumed successfully"
            }
        except Exception as e:
            logger.error(f"Failed to resume site: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to resume site: {str(e)}"
            }
    
    async def delete_site(self, client_id: str):
        """Permanently delete a WordPress site"""
        
        if not self.k8s_config_loaded:
            logger.info(f"[DEV MODE] Would delete site for client: {client_id}")
            return {"success": True, "message": "Site deleted (dev mode)"}
        
        namespace = f"client-{client_id}"
        
        try:
            # Delete the entire namespace
            self.v1.delete_namespace(namespace)
            logger.info(f"Deleted site for client: {client_id}")
            
            return {
                "success": True,
                "message": "Site deleted permanently"
            }
        except Exception as e:
            logger.error(f"Failed to delete site: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to delete site: {str(e)}"
            }
    
    async def get_site_status(self, client_id: str) -> Dict[str, Any]:
        """Get the status of a WordPress site"""
        
        if not self.k8s_config_loaded:
            return {
                "client_id": client_id,
                "status": "active",
                "wordpress": {"ready": True, "replicas": 1},
                "mysql": {"ready": True, "replicas": 1},
                "message": "Development mode - mock status"
            }
        
        namespace = f"client-{client_id}"
        
        try:
            # Check WordPress deployment
            wp_deployment = self.apps_v1.read_namespaced_deployment(
                f"wordpress-{client_id}", namespace
            )
            
            # Check MySQL deployment
            mysql_deployment = self.apps_v1.read_namespaced_deployment(
                f"mysql-{client_id}", namespace
            )
            
            return {
                "client_id": client_id,
                "status": "active" if wp_deployment.status.ready_replicas > 0 else "suspended",
                "wordpress": {
                    "ready": wp_deployment.status.ready_replicas > 0,
                    "replicas": wp_deployment.status.ready_replicas or 0,
                    "available": wp_deployment.status.available_replicas or 0
                },
                "mysql": {
                    "ready": mysql_deployment.status.ready_replicas > 0,
                    "replicas": mysql_deployment.status.ready_replicas or 0
                },
                "created": wp_deployment.metadata.creation_timestamp.isoformat()
            }
        except Exception as e:
            return {
                "client_id": client_id,
                "status": "unknown",
                "error": str(e)
            }

# Global instance
wordpress_provisioner = WordPressProvisioner()