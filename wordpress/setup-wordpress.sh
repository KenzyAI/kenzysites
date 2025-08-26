#!/bin/bash

# WordPress Setup Script for KenzySites Development
# This script automates the WordPress installation and plugin setup

set -e

echo "🚀 Starting WordPress Setup for KenzySites..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
WP_URL="http://localhost:8080"
WP_TITLE="KenzySites Development"
WP_ADMIN_USER="admin"
WP_ADMIN_PASSWORD="admin123"
WP_ADMIN_EMAIL="admin@kenzysites.local"

# Wait for WordPress to be ready
echo -e "${YELLOW}Waiting for WordPress to be ready...${NC}"
until docker-compose exec -T wordpress wp --info > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}WordPress is ready!${NC}"

# Install WP-CLI if not present
echo -e "${YELLOW}Setting up WP-CLI...${NC}"
docker-compose exec -T wordpress bash -c "
    if ! command -v wp &> /dev/null; then
        curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
        chmod +x wp-cli.phar
        mv wp-cli.phar /usr/local/bin/wp
    fi
"

# Check if WordPress is already installed
if docker-compose exec -T wordpress wp core is-installed --allow-root 2>/dev/null; then
    echo -e "${YELLOW}WordPress is already installed. Skipping installation...${NC}"
else
    echo -e "${YELLOW}Installing WordPress...${NC}"
    docker-compose exec -T wordpress wp core install \
        --url="$WP_URL" \
        --title="$WP_TITLE" \
        --admin_user="$WP_ADMIN_USER" \
        --admin_password="$WP_ADMIN_PASSWORD" \
        --admin_email="$WP_ADMIN_EMAIL" \
        --skip-email \
        --allow-root
    echo -e "${GREEN}WordPress installed successfully!${NC}"
fi

# Update WordPress settings
echo -e "${YELLOW}Configuring WordPress settings...${NC}"
docker-compose exec -T wordpress bash -c "
    wp option update blogdescription 'Plataforma de criação de sites com IA' --allow-root
    wp option update timezone_string 'America/Sao_Paulo' --allow-root
    wp option update date_format 'd/m/Y' --allow-root
    wp option update time_format 'H:i' --allow-root
    wp option update start_of_week '0' --allow-root
    wp option update default_comment_status 'closed' --allow-root
    wp option update default_ping_status 'closed' --allow-root
    wp rewrite structure '/%postname%/' --allow-root
    wp language core install pt_BR --allow-root
    wp site switch-language pt_BR --allow-root
"

# Install required plugins
echo -e "${YELLOW}Installing plugins...${NC}"

# Elementor
if ! docker-compose exec -T wordpress wp plugin is-installed elementor --allow-root; then
    docker-compose exec -T wordpress wp plugin install elementor --activate --allow-root
    echo -e "${GREEN}✓ Elementor installed${NC}"
else
    docker-compose exec -T wordpress wp plugin activate elementor --allow-root 2>/dev/null || true
    echo -e "${GREEN}✓ Elementor already installed${NC}"
fi

# Advanced Custom Fields
if ! docker-compose exec -T wordpress wp plugin is-installed advanced-custom-fields --allow-root; then
    docker-compose exec -T wordpress wp plugin install advanced-custom-fields --activate --allow-root
    echo -e "${GREEN}✓ ACF installed${NC}"
else
    docker-compose exec -T wordpress wp plugin activate advanced-custom-fields --allow-root 2>/dev/null || true
    echo -e "${GREEN}✓ ACF already installed${NC}"
fi

# Custom Post Type UI
if ! docker-compose exec -T wordpress wp plugin is-installed custom-post-type-ui --allow-root; then
    docker-compose exec -T wordpress wp plugin install custom-post-type-ui --activate --allow-root
    echo -e "${GREEN}✓ Custom Post Type UI installed${NC}"
else
    docker-compose exec -T wordpress wp plugin activate custom-post-type-ui --allow-root 2>/dev/null || true
    echo -e "${GREEN}✓ Custom Post Type UI already installed${NC}"
fi

# JWT Authentication
if ! docker-compose exec -T wordpress wp plugin is-installed jwt-authentication-for-wp-rest-api --allow-root; then
    docker-compose exec -T wordpress wp plugin install jwt-authentication-for-wp-rest-api --allow-root
    echo -e "${GREEN}✓ JWT Authentication installed${NC}"
else
    echo -e "${GREEN}✓ JWT Authentication already installed${NC}"
fi

# Activate KenzySites Converter Plugin
echo -e "${YELLOW}Activating KenzySites Converter plugin...${NC}"
docker-compose exec -T wordpress wp plugin activate kenzysites-converter --allow-root 2>/dev/null || {
    echo -e "${YELLOW}KenzySites Converter plugin not found. Make sure it's in the plugins directory.${NC}"
}

# Create sample pages with Elementor
echo -e "${YELLOW}Creating sample Elementor pages...${NC}"

# Create sample pages
docker-compose exec -T wordpress bash -c "
    # Landing Page - Restaurante
    if ! wp post list --post_type=page --title='Restaurante Italiano' --allow-root --format=ids | grep -q .; then
        wp post create --post_type=page --post_title='Restaurante Italiano' \
            --post_content='Landing page para restaurante italiano com delivery' \
            --post_status=publish --allow-root
        echo '✓ Página Restaurante criada'
    fi

    # Landing Page - Clínica
    if ! wp post list --post_type=page --title='Clínica Odontológica' --allow-root --format=ids | grep -q .; then
        wp post create --post_type=page --post_title='Clínica Odontológica' \
            --post_content='Landing page para clínica odontológica' \
            --post_status=publish --allow-root
        echo '✓ Página Clínica criada'
    fi

    # Landing Page - Academia
    if ! wp post list --post_type=page --title='Academia Fitness' --allow-root --format=ids | grep -q .; then
        wp post create --post_type=page --post_title='Academia Fitness' \
            --post_content='Landing page para academia e personal trainer' \
            --post_status=publish --allow-root
        echo '✓ Página Academia criada'
    fi

    # Landing Page - Advogado
    if ! wp post list --post_type=page --title='Escritório de Advocacia' --allow-root --format=ids | grep -q .; then
        wp post create --post_type=page --post_title='Escritório de Advocacia' \
            --post_content='Landing page para escritório de advocacia' \
            --post_status=publish --allow-root
        echo '✓ Página Advocacia criada'
    fi

    # Landing Page - E-commerce
    if ! wp post list --post_type=page --title='Loja Virtual' --allow-root --format=ids | grep -q .; then
        wp post create --post_type=page --post_title='Loja Virtual' \
            --post_content='Landing page para e-commerce' \
            --post_status=publish --allow-root
        echo '✓ Página E-commerce criada'
    fi
"

# Create custom post type for templates
echo -e "${YELLOW}Creating Template custom post type...${NC}"
docker-compose exec -T wordpress bash -c "
    wp post-type create kz_template 'KenzySites Templates' --public --show_in_rest --supports=title,editor,custom-fields,excerpt --allow-root 2>/dev/null || true
"

# Configure JWT Authentication
echo -e "${YELLOW}Configuring JWT Authentication...${NC}"
docker-compose exec -T wordpress bash -c "
    # Add JWT secret key to wp-config.php if not present
    if ! grep -q 'JWT_AUTH_SECRET_KEY' /var/www/html/wp-config.php; then
        sed -i \"s/\\/\\* That's all, stop editing! Happy publishing. \\*\\//define('JWT_AUTH_SECRET_KEY', 'your-secret-key-here');\\n\\/\\* That's all, stop editing! Happy publishing. \\*\\//\" /var/www/html/wp-config.php
        sed -i \"s/\\/\\* That's all, stop editing! Happy publishing. \\*\\//define('JWT_AUTH_CORS_ENABLE', true);\\n\\/\\* That's all, stop editing! Happy publishing. \\*\\//\" /var/www/html/wp-config.php
    fi
"

# Create .htaccess for JWT
docker-compose exec -T wordpress bash -c "
    if [ ! -f /var/www/html/.htaccess ]; then
        cat > /var/www/html/.htaccess << 'EOF'
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^index\\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress

# BEGIN JWT Authentication
<IfModule mod_rewrite.c>
RewriteEngine on
RewriteCond %{HTTP:Authorization} ^(.*)
RewriteRule ^(.*) - [E=HTTP_AUTHORIZATION:%1]
</IfModule>
# END JWT Authentication
EOF
    fi
"

# Set proper permissions
echo -e "${YELLOW}Setting permissions...${NC}"
docker-compose exec -T wordpress bash -c "
    chown -R www-data:www-data /var/www/html/wp-content/uploads 2>/dev/null || true
    chown -R www-data:www-data /var/www/html/wp-content/plugins/kenzysites-converter 2>/dev/null || true
    chmod -R 755 /var/www/html/wp-content/uploads 2>/dev/null || true
"

# Display summary
echo -e "\n${GREEN}==============================================
✅ WordPress Setup Complete!
===============================================${NC}"
echo -e "${GREEN}WordPress URL:${NC} $WP_URL"
echo -e "${GREEN}Admin URL:${NC} $WP_URL/wp-admin"
echo -e "${GREEN}Username:${NC} $WP_ADMIN_USER"
echo -e "${GREEN}Password:${NC} $WP_ADMIN_PASSWORD"
echo -e "${GREEN}phpMyAdmin:${NC} http://localhost:8081"
echo -e "\n${GREEN}Installed Plugins:${NC}"
echo "  ✓ Elementor"
echo "  ✓ Advanced Custom Fields"
echo "  ✓ Custom Post Type UI"
echo "  ✓ JWT Authentication"
echo "  ✓ KenzySites Converter"
echo -e "\n${GREEN}Sample Pages Created:${NC}"
echo "  ✓ Restaurante Italiano"
echo "  ✓ Clínica Odontológica"
echo "  ✓ Academia Fitness"
echo "  ✓ Escritório de Advocacia"
echo "  ✓ Loja Virtual"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Access WordPress admin and edit pages with Elementor"
echo "2. Use KenzySites Converter to scan and convert pages"
echo "3. Test the ACF integration"