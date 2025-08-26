"""
WordPress Provisioner V2
Automated WordPress site deployment and configuration
"""

import os
import asyncio
import logging
import subprocess
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import aioftp
import paramiko
import mysql.connector
from jinja2 import Template

logger = logging.getLogger(__name__)

class DeploymentMethod:
    """Deployment methods"""
    LOCAL_DOCKER = "local_docker"
    FTP = "ftp"
    SSH = "ssh"
    MANAGED_HOSTING = "managed_hosting"
    KUBERNETES = "kubernetes"

class WordPressProvisionerV2:
    """
    Advanced WordPress provisioning service with multiple deployment options
    """
    
    def __init__(self):
        self.docker_compose_template = Path("templates/docker/docker-compose.yml.j2")
        self.wp_config_template = Path("templates/wordpress/wp-config.php.j2")
        self.deployment_dir = Path("deployments")
        self.deployment_dir.mkdir(exist_ok=True)
        
        # Load deployment configurations
        self.deploy_configs = self._load_deploy_configs()
        
    def _load_deploy_configs(self) -> Dict[str, Any]:
        """Load deployment configurations from environment"""
        
        return {
            "ftp": {
                "host": os.getenv("FTP_HOST"),
                "user": os.getenv("FTP_USER"),
                "password": os.getenv("FTP_PASSWORD"),
                "port": int(os.getenv("FTP_PORT", "21"))
            },
            "ssh": {
                "host": os.getenv("SSH_HOST"),
                "user": os.getenv("SSH_USER"),
                "key_path": os.getenv("SSH_KEY_PATH"),
                "port": int(os.getenv("SSH_PORT", "22"))
            },
            "database": {
                "host": os.getenv("DB_HOST", "localhost"),
                "user": os.getenv("DB_USER", "wordpress"),
                "password": os.getenv("DB_PASSWORD", "wordpress123"),
                "port": int(os.getenv("DB_PORT", "3306"))
            }
        }
    
    async def provision_site(
        self,
        site_id: str,
        site_data: Dict[str, Any],
        deployment_method: str = DeploymentMethod.LOCAL_DOCKER,
        deployment_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provision a complete WordPress site
        
        Args:
            site_id: Unique site identifier
            site_data: Site configuration and content
            deployment_method: How to deploy the site
            deployment_config: Additional deployment configuration
            
        Returns:
            Deployment result with URLs and credentials
        """
        
        logger.info(f"🚀 Starting WordPress provisioning for {site_id}")
        start_time = datetime.now()
        
        try:
            # Prepare site package
            site_package = await self._prepare_site_package(site_id, site_data)
            
            # Deploy based on method
            if deployment_method == DeploymentMethod.LOCAL_DOCKER:
                result = await self._deploy_local_docker(site_id, site_package)
            elif deployment_method == DeploymentMethod.FTP:
                result = await self._deploy_ftp(site_id, site_package, deployment_config)
            elif deployment_method == DeploymentMethod.SSH:
                result = await self._deploy_ssh(site_id, site_package, deployment_config)
            elif deployment_method == DeploymentMethod.MANAGED_HOSTING:
                result = await self._deploy_managed_hosting(site_id, site_package, deployment_config)
            elif deployment_method == DeploymentMethod.KUBERNETES:
                result = await self._deploy_kubernetes(site_id, site_package, deployment_config)
            else:
                raise ValueError(f"Unknown deployment method: {deployment_method}")
            
            # Post-deployment configuration
            await self._configure_wordpress(result["url"], site_data)
            
            # Calculate deployment time
            deployment_time = (datetime.now() - start_time).total_seconds()
            
            result.update({
                "deployment_time": deployment_time,
                "deployment_method": deployment_method,
                "site_id": site_id,
                "deployed_at": datetime.now().isoformat()
            })
            
            logger.info(f"✅ WordPress site provisioned in {deployment_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Provisioning failed: {str(e)}")
            raise
    
    async def _prepare_site_package(
        self,
        site_id: str,
        site_data: Dict[str, Any]
    ) -> Path:
        """Prepare the site package for deployment"""
        
        package_dir = self.deployment_dir / site_id
        package_dir.mkdir(exist_ok=True)
        
        # Generate WordPress configuration
        wp_config = self._generate_wp_config(site_data)
        (package_dir / "wp-config.php").write_text(wp_config)
        
        # Generate theme files
        theme_dir = package_dir / "wp-content" / "themes" / f"kenzysites-{site_id}"
        theme_dir.mkdir(parents=True, exist_ok=True)
        
        # Create theme files
        self._create_theme_files(theme_dir, site_data)
        
        # Generate plugin configurations
        plugins_dir = package_dir / "wp-content" / "plugins"
        plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Create must-use plugins for custom functionality
        mu_plugins_dir = package_dir / "wp-content" / "mu-plugins"
        mu_plugins_dir.mkdir(parents=True, exist_ok=True)
        self._create_mu_plugins(mu_plugins_dir, site_data)
        
        # Generate database initialization script
        db_script = self._generate_database_script(site_data)
        (package_dir / "init.sql").write_text(db_script)
        
        # Create Docker files if needed
        docker_compose = self._generate_docker_compose(site_id, site_data)
        (package_dir / "docker-compose.yml").write_text(docker_compose)
        
        # Create installation script
        install_script = self._generate_install_script(site_id, site_data)
        (package_dir / "install.sh").write_text(install_script)
        os.chmod(package_dir / "install.sh", 0o755)
        
        logger.info(f"📦 Site package prepared at {package_dir}")
        return package_dir
    
    async def _deploy_local_docker(
        self,
        site_id: str,
        package_dir: Path
    ) -> Dict[str, Any]:
        """Deploy site using local Docker"""
        
        logger.info("🐳 Deploying with Docker...")
        
        # Stop existing containers if any
        subprocess.run(
            ["docker-compose", "down"],
            cwd=package_dir,
            capture_output=True
        )
        
        # Start new containers
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=package_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Docker deployment failed: {result.stderr}")
        
        # Wait for WordPress to be ready
        await self._wait_for_wordpress("http://localhost:8080")
        
        # Run WordPress CLI commands
        wp_commands = [
            "core install --url=http://localhost:8080 --title='KenzySites' --admin_user=admin --admin_password=admin123 --admin_email=admin@kenzysites.com",
            "theme activate kenzysites-" + site_id,
            "plugin activate elementor",
            "plugin activate advanced-custom-fields",
            "rewrite structure '/%postname%/'",
            "option update timezone_string 'America/Sao_Paulo'",
            "option update date_format 'd/m/Y'",
            "option update time_format 'H:i'"
        ]
        
        for cmd in wp_commands:
            subprocess.run(
                ["docker-compose", "exec", "-T", "wordpress", "wp", "--allow-root"] + cmd.split(),
                cwd=package_dir,
                capture_output=True
            )
        
        return {
            "url": "http://localhost:8080",
            "admin_url": "http://localhost:8080/wp-admin",
            "admin_user": "admin",
            "admin_password": "admin123",
            "deployment_path": str(package_dir)
        }
    
    async def _deploy_ftp(
        self,
        site_id: str,
        package_dir: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deploy site via FTP"""
        
        logger.info("📤 Deploying via FTP...")
        
        ftp_config = config or self.deploy_configs["ftp"]
        
        if not ftp_config.get("host"):
            raise ValueError("FTP configuration not provided")
        
        async with aioftp.Client.context(
            ftp_config["host"],
            user=ftp_config.get("user"),
            password=ftp_config.get("password"),
            port=ftp_config.get("port", 21)
        ) as client:
            # Create site directory
            site_path = f"/public_html/{site_id}"
            await client.make_directory(site_path)
            
            # Upload all files
            for file_path in package_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(package_dir)
                    remote_path = f"{site_path}/{relative_path}"
                    
                    # Create parent directories
                    remote_dir = str(Path(remote_path).parent)
                    try:
                        await client.make_directory(remote_dir)
                    except:
                        pass  # Directory might already exist
                    
                    # Upload file
                    await client.upload(file_path, remote_path)
            
            logger.info(f"✅ Files uploaded to FTP")
        
        # Create database via API if available
        if config and config.get("cpanel_api"):
            await self._create_database_cpanel(site_id, config["cpanel_api"])
        
        return {
            "url": f"https://{ftp_config['host']}/{site_id}",
            "admin_url": f"https://{ftp_config['host']}/{site_id}/wp-admin",
            "deployment_path": site_path
        }
    
    async def _deploy_ssh(
        self,
        site_id: str,
        package_dir: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deploy site via SSH"""
        
        logger.info("🔐 Deploying via SSH...")
        
        ssh_config = config or self.deploy_configs["ssh"]
        
        if not ssh_config.get("host"):
            raise ValueError("SSH configuration not provided")
        
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Connect
            if ssh_config.get("key_path"):
                ssh.connect(
                    ssh_config["host"],
                    username=ssh_config.get("user"),
                    key_filename=ssh_config["key_path"],
                    port=ssh_config.get("port", 22)
                )
            else:
                ssh.connect(
                    ssh_config["host"],
                    username=ssh_config.get("user"),
                    password=ssh_config.get("password"),
                    port=ssh_config.get("port", 22)
                )
            
            # Create site directory
            site_path = f"/var/www/{site_id}"
            ssh.exec_command(f"sudo mkdir -p {site_path}")
            
            # Upload files via SFTP
            sftp = ssh.open_sftp()
            
            for file_path in package_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(package_dir)
                    remote_path = f"{site_path}/{relative_path}"
                    
                    # Create parent directories
                    remote_dir = str(Path(remote_path).parent)
                    ssh.exec_command(f"sudo mkdir -p {remote_dir}")
                    
                    # Upload file
                    sftp.put(str(file_path), remote_path)
            
            sftp.close()
            
            # Set permissions
            ssh.exec_command(f"sudo chown -R www-data:www-data {site_path}")
            ssh.exec_command(f"sudo chmod -R 755 {site_path}")
            
            # Create nginx configuration
            nginx_config = self._generate_nginx_config(site_id, site_path)
            stdin, stdout, stderr = ssh.exec_command(
                f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/{site_id}"
            )
            ssh.exec_command(f"sudo ln -s /etc/nginx/sites-available/{site_id} /etc/nginx/sites-enabled/")
            ssh.exec_command("sudo nginx -t && sudo systemctl reload nginx")
            
            # Create database
            db_commands = [
                f"mysql -u root -e 'CREATE DATABASE IF NOT EXISTS wp_{site_id}'",
                f"mysql -u root -e 'CREATE USER IF NOT EXISTS wp_{site_id}@localhost IDENTIFIED BY \"wp_{site_id}_pass\"'",
                f"mysql -u root -e 'GRANT ALL ON wp_{site_id}.* TO wp_{site_id}@localhost'",
                f"mysql -u root wp_{site_id} < {site_path}/init.sql"
            ]
            
            for cmd in db_commands:
                ssh.exec_command(f"sudo {cmd}")
            
            logger.info(f"✅ Site deployed via SSH")
            
        finally:
            ssh.close()
        
        return {
            "url": f"https://{ssh_config['host']}/{site_id}",
            "admin_url": f"https://{ssh_config['host']}/{site_id}/wp-admin",
            "deployment_path": site_path
        }
    
    async def _deploy_managed_hosting(
        self,
        site_id: str,
        package_dir: Path,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy to managed WordPress hosting (WP Engine, Kinsta, etc.)"""
        
        logger.info("☁️ Deploying to managed hosting...")
        
        provider = config.get("provider", "generic")
        
        if provider == "wpengine":
            return await self._deploy_wpengine(site_id, package_dir, config)
        elif provider == "kinsta":
            return await self._deploy_kinsta(site_id, package_dir, config)
        else:
            # Generic managed hosting deployment
            return await self._deploy_generic_managed(site_id, package_dir, config)
    
    async def _deploy_kubernetes(
        self,
        site_id: str,
        package_dir: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deploy to Kubernetes cluster"""
        
        logger.info("☸️ Deploying to Kubernetes...")
        
        # Generate Kubernetes manifests
        k8s_manifests = self._generate_k8s_manifests(site_id, package_dir)
        
        # Apply manifests
        for manifest in k8s_manifests:
            manifest_file = package_dir / f"{manifest['name']}.yaml"
            manifest_file.write_text(yaml.dump(manifest['content']))
            
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(manifest_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Kubernetes deployment failed: {result.stderr}")
        
        # Wait for deployment to be ready
        subprocess.run(
            ["kubectl", "wait", "--for=condition=available", f"deployment/wordpress-{site_id}", "--timeout=300s"],
            capture_output=True
        )
        
        # Get service URL
        result = subprocess.run(
            ["kubectl", "get", f"service/wordpress-{site_id}", "-o", "jsonpath='{.status.loadBalancer.ingress[0].ip}'"],
            capture_output=True,
            text=True
        )
        
        service_ip = result.stdout.strip().replace("'", "")
        
        return {
            "url": f"http://{service_ip}",
            "admin_url": f"http://{service_ip}/wp-admin",
            "deployment_path": f"kubernetes/wordpress-{site_id}"
        }
    
    async def _configure_wordpress(self, site_url: str, site_data: Dict[str, Any]):
        """Configure WordPress after deployment"""
        
        logger.info("⚙️ Configuring WordPress...")
        
        # Wait for site to be accessible
        await self._wait_for_wordpress(site_url)
        
        # Configure via REST API if available
        api_url = f"{site_url}/wp-json/wp/v2"
        
        async with aiohttp.ClientSession() as session:
            # Update site settings
            settings = {
                "title": site_data.get("business_name", "KenzySites"),
                "description": site_data.get("business_description", ""),
                "timezone": "America/Sao_Paulo",
                "date_format": "d/m/Y",
                "time_format": "H:i",
                "start_of_week": 0
            }
            
            try:
                async with session.post(
                    f"{api_url}/settings",
                    json=settings,
                    auth=aiohttp.BasicAuth("admin", "admin123")
                ) as response:
                    if response.status == 200:
                        logger.info("✅ WordPress settings updated")
            except:
                logger.warning("Could not update settings via API")
    
    async def _wait_for_wordpress(self, url: str, timeout: int = 60):
        """Wait for WordPress to be accessible"""
        
        start_time = datetime.now()
        
        async with aiohttp.ClientSession() as session:
            while (datetime.now() - start_time).total_seconds() < timeout:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            logger.info(f"✅ WordPress is accessible at {url}")
                            return
                except:
                    pass
                
                await asyncio.sleep(2)
        
        raise TimeoutError(f"WordPress not accessible after {timeout} seconds")
    
    def _generate_wp_config(self, site_data: Dict[str, Any]) -> str:
        """Generate wp-config.php file"""
        
        template = """<?php
define( 'DB_NAME', '{{ db_name }}' );
define( 'DB_USER', '{{ db_user }}' );
define( 'DB_PASSWORD', '{{ db_password }}' );
define( 'DB_HOST', '{{ db_host }}' );
define( 'DB_CHARSET', 'utf8mb4' );
define( 'DB_COLLATE', '' );

define( 'AUTH_KEY',         '{{ auth_key }}' );
define( 'SECURE_AUTH_KEY',  '{{ secure_auth_key }}' );
define( 'LOGGED_IN_KEY',    '{{ logged_in_key }}' );
define( 'NONCE_KEY',        '{{ nonce_key }}' );
define( 'AUTH_SALT',        '{{ auth_salt }}' );
define( 'SECURE_AUTH_SALT', '{{ secure_auth_salt }}' );
define( 'LOGGED_IN_SALT',   '{{ logged_in_salt }}' );
define( 'NONCE_SALT',       '{{ nonce_salt }}' );

$table_prefix = 'wp_';

define( 'WP_DEBUG', false );
define( 'WP_MEMORY_LIMIT', '256M' );
define( 'WP_MAX_MEMORY_LIMIT', '512M' );
define( 'WPLANG', 'pt_BR' );
define( 'WP_TIMEZONE', 'America/Sao_Paulo' );

/* Brazilian Features */
define( 'KENZYSITES_WHATSAPP', '{{ whatsapp_number }}' );
define( 'KENZYSITES_PIX_KEY', '{{ pix_key }}' );
define( 'KENZYSITES_LGPD', true );

if ( ! defined( 'ABSPATH' ) ) {
    define( 'ABSPATH', __DIR__ . '/' );
}

require_once ABSPATH . 'wp-settings.php';
"""
        
        # Generate random salts
        import secrets
        import string
        
        def generate_salt():
            return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()") for _ in range(64))
        
        config_vars = {
            "db_name": f"wp_{site_data.get('site_id', 'kenzysites')}",
            "db_user": "wordpress",
            "db_password": "wordpress123",
            "db_host": "db",
            "auth_key": generate_salt(),
            "secure_auth_key": generate_salt(),
            "logged_in_key": generate_salt(),
            "nonce_key": generate_salt(),
            "auth_salt": generate_salt(),
            "secure_auth_salt": generate_salt(),
            "logged_in_salt": generate_salt(),
            "nonce_salt": generate_salt(),
            "whatsapp_number": site_data.get("whatsapp", ""),
            "pix_key": site_data.get("pix_key", "")
        }
        
        return Template(template).render(**config_vars)
    
    def _generate_docker_compose(self, site_id: str, site_data: Dict[str, Any]) -> str:
        """Generate docker-compose.yml file"""
        
        return f"""version: '3.8'

services:
  wordpress:
    image: wordpress:latest
    container_name: wp_{site_id}
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress123
      WORDPRESS_DB_NAME: wp_{site_id}
    volumes:
      - ./wp-content:/var/www/html/wp-content
      - ./wp-config.php:/var/www/html/wp-config.php
    networks:
      - wp_network
    depends_on:
      - db

  db:
    image: mysql:8.0
    container_name: db_{site_id}
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: wp_{site_id}
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress123
    volumes:
      - db_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - wp_network

  phpmyadmin:
    image: phpmyadmin:latest
    container_name: pma_{site_id}
    ports:
      - "8081:80"
    environment:
      PMA_HOST: db
      PMA_USER: root
      PMA_PASSWORD: root123
    networks:
      - wp_network
    depends_on:
      - db

networks:
  wp_network:
    driver: bridge

volumes:
  db_data:
"""
    
    def _generate_database_script(self, site_data: Dict[str, Any]) -> str:
        """Generate database initialization script"""
        
        return f"""-- KenzySites Database Initialization
-- Site: {site_data.get('business_name', 'KenzySites')}

-- Create Brazilian feature tables
CREATE TABLE IF NOT EXISTS wp_kenzysites_whatsapp (
  id INT AUTO_INCREMENT PRIMARY KEY,
  phone VARCHAR(20),
  message TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wp_kenzysites_pix (
  id INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id VARCHAR(100) UNIQUE,
  amount DECIMAL(10,2),
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial options
INSERT INTO wp_options (option_name, option_value) VALUES
  ('kenzysites_business_name', '{site_data.get('business_name', '')}'),
  ('kenzysites_industry', '{site_data.get('industry', '')}'),
  ('kenzysites_template', '{site_data.get('template_id', '')}');
"""
    
    def _generate_install_script(self, site_id: str, site_data: Dict[str, Any]) -> str:
        """Generate installation script"""
        
        return f"""#!/bin/bash
# KenzySites WordPress Installation Script
# Site: {site_data.get('business_name', 'KenzySites')}

echo "Installing WordPress site {site_id}..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

# Start containers
docker-compose up -d

# Wait for MySQL to be ready
echo "Waiting for database..."
sleep 10

# Install WordPress
docker-compose exec wordpress wp core install \\
    --url=http://localhost:8080 \\
    --title="{site_data.get('business_name', 'KenzySites')}" \\
    --admin_user=admin \\
    --admin_password=admin123 \\
    --admin_email=admin@kenzysites.com \\
    --allow-root

# Activate theme
docker-compose exec wordpress wp theme activate kenzysites-{site_id} --allow-root

# Install and activate plugins
docker-compose exec wordpress wp plugin install elementor --activate --allow-root
docker-compose exec wordpress wp plugin install advanced-custom-fields --activate --allow-root

echo "Installation complete!"
echo "Access your site at: http://localhost:8080"
echo "Admin panel: http://localhost:8080/wp-admin"
echo "Username: admin"
echo "Password: admin123"
"""
    
    def _create_theme_files(self, theme_dir: Path, site_data: Dict[str, Any]):
        """Create custom theme files"""
        
        # style.css
        style_css = f"""/*
Theme Name: KenzySites {site_data.get('business_name', '')}
Theme URI: https://kenzysites.com
Author: KenzySites
Author URI: https://kenzysites.com
Description: Custom theme for {site_data.get('business_name', '')}
Version: 1.0.0
License: GPL v2 or later
Text Domain: kenzysites
*/
"""
        (theme_dir / "style.css").write_text(style_css)
        
        # functions.php
        functions_php = """<?php
// KenzySites Theme Functions

// Theme Setup
function kenzysites_setup() {
    add_theme_support('post-thumbnails');
    add_theme_support('title-tag');
    add_theme_support('custom-logo');
    
    register_nav_menus(array(
        'primary' => 'Primary Menu',
        'footer' => 'Footer Menu'
    ));
}
add_action('after_setup_theme', 'kenzysites_setup');

// Brazilian Features
function kenzysites_whatsapp_button() {
    $whatsapp = get_option('kenzysites_whatsapp');
    if ($whatsapp) {
        echo '<a href="https://wa.me/55' . $whatsapp . '" class="whatsapp-float" target="_blank">WhatsApp</a>';
    }
}
add_action('wp_footer', 'kenzysites_whatsapp_button');
"""
        (theme_dir / "functions.php").write_text(functions_php)
        
        # index.php
        index_php = """<?php get_header(); ?>

<main id="main" class="site-main">
    <?php
    if (have_posts()) :
        while (have_posts()) : the_post();
            the_content();
        endwhile;
    endif;
    ?>
</main>

<?php get_footer(); ?>
"""
        (theme_dir / "index.php").write_text(index_php)
        
        # header.php
        header_php = """<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<header class="site-header">
    <div class="container">
        <?php if (has_custom_logo()) : ?>
            <?php the_custom_logo(); ?>
        <?php else : ?>
            <h1 class="site-title"><?php bloginfo('name'); ?></h1>
        <?php endif; ?>
        
        <nav class="main-navigation">
            <?php wp_nav_menu(array('theme_location' => 'primary')); ?>
        </nav>
    </div>
</header>
"""
        (theme_dir / "header.php").write_text(header_php)
        
        # footer.php
        footer_php = """<footer class="site-footer">
    <div class="container">
        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. Todos os direitos reservados.</p>
        <p>Criado com <a href="https://kenzysites.com" target="_blank">KenzySites</a></p>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
"""
        (theme_dir / "footer.php").write_text(footer_php)
    
    def _create_mu_plugins(self, mu_plugins_dir: Path, site_data: Dict[str, Any]):
        """Create must-use plugins for custom functionality"""
        
        # Brazilian features plugin
        brazilian_features = """<?php
/**
 * Plugin Name: KenzySites Brazilian Features
 * Description: Adds Brazilian-specific features to WordPress
 * Version: 1.0.0
 * Author: KenzySites
 */

// PIX Payment Integration
add_shortcode('kenzysites_pix', function($atts) {
    $pix_key = get_option('kenzysites_pix_key');
    if (!$pix_key) return '';
    
    return '<div class="pix-payment">
        <h3>Pagamento via PIX</h3>
        <p>Chave PIX: <strong>' . esc_html($pix_key) . '</strong></p>
        <div class="pix-qrcode" data-pix="' . esc_attr($pix_key) . '"></div>
    </div>';
});

// LGPD Compliance
add_action('wp_footer', function() {
    if (!isset($_COOKIE['lgpd_accepted'])) {
        echo '<div class="lgpd-banner">
            <p>Este site usa cookies. Ao continuar navegando, você concorda com nossa política de privacidade.</p>
            <button onclick="document.cookie=\'lgpd_accepted=1;max-age=31536000;path=/\';this.parentElement.remove();">Aceitar</button>
        </div>';
    }
});

// WhatsApp Integration
add_action('wp_footer', function() {
    $whatsapp = get_option('kenzysites_whatsapp');
    if ($whatsapp) {
        echo '<style>
            .whatsapp-float {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #25D366;
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                z-index: 9999;
            }
        </style>';
    }
});
"""
        (mu_plugins_dir / "kenzysites-brazilian.php").write_text(brazilian_features)
    
    def _generate_nginx_config(self, site_id: str, site_path: str) -> str:
        """Generate Nginx configuration"""
        
        return f"""server {{
    listen 80;
    server_name {site_id}.kenzysites.com;
    root {site_path};
    index index.php index.html;
    
    location / {{
        try_files $uri $uri/ /index.php?$args;
    }}
    
    location ~ \\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
    }}
    
    location ~ /\\.ht {{
        deny all;
    }}
    
    # Cache static files
    location ~* \\.(jpg|jpeg|png|gif|ico|css|js)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
    
    def _generate_k8s_manifests(self, site_id: str, package_dir: Path) -> List[Dict[str, Any]]:
        """Generate Kubernetes manifests"""
        
        return [
            {
                "name": "deployment",
                "content": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {
                        "name": f"wordpress-{site_id}"
                    },
                    "spec": {
                        "replicas": 2,
                        "selector": {
                            "matchLabels": {
                                "app": f"wordpress-{site_id}"
                            }
                        },
                        "template": {
                            "metadata": {
                                "labels": {
                                    "app": f"wordpress-{site_id}"
                                }
                            },
                            "spec": {
                                "containers": [{
                                    "name": "wordpress",
                                    "image": "wordpress:latest",
                                    "ports": [{"containerPort": 80}],
                                    "env": [
                                        {"name": "WORDPRESS_DB_HOST", "value": f"mysql-{site_id}"},
                                        {"name": "WORDPRESS_DB_USER", "value": "wordpress"},
                                        {"name": "WORDPRESS_DB_PASSWORD", "value": "wordpress123"},
                                        {"name": "WORDPRESS_DB_NAME", "value": f"wp_{site_id}"}
                                    ]
                                }]
                            }
                        }
                    }
                }
            },
            {
                "name": "service",
                "content": {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {
                        "name": f"wordpress-{site_id}"
                    },
                    "spec": {
                        "type": "LoadBalancer",
                        "ports": [{"port": 80, "targetPort": 80}],
                        "selector": {
                            "app": f"wordpress-{site_id}"
                        }
                    }
                }
            }
        ]

# Create singleton instance
wordpress_provisioner_v2 = WordPressProvisionerV2()