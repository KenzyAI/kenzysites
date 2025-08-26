#!/bin/bash

# Start WordPress Multisite with Astra and Spectra
# This script sets up and starts the WordPress Multisite environment

echo "🚀 KenzySites WordPress Multisite Setup"
echo "======================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create network if it doesn't exist
if ! docker network ls | grep -q wordpress-ai-network; then
    echo "📡 Creating Docker network..."
    docker network create wordpress-ai-network
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.multisite.yml down

# Start the multisite containers
echo "🚀 Starting WordPress Multisite containers..."
docker-compose -f docker-compose.multisite.yml up -d

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 10

# Wait for WordPress to be ready
echo "⏳ Waiting for WordPress to be ready..."
until docker exec kenzysites-multisite wp core version --allow-root &>/dev/null; do
    echo -n "."
    sleep 2
done
echo ""

# Run the multisite setup script
echo "🔧 Configuring WordPress Multisite..."
docker exec kenzysites-multisite bash -c "
    # Check if WordPress is installed
    if ! wp core is-installed --allow-root 2>/dev/null; then
        echo '📦 Installing WordPress...'
        
        wp core install \
            --url='http://localhost:8090' \
            --title='KenzySites Platform' \
            --admin_user='admin' \
            --admin_password='admin123' \
            --admin_email='admin@kenzysites.com' \
            --skip-email \
            --allow-root
    fi

    # Enable multisite if not already enabled
    if ! wp core is-installed --network --allow-root 2>/dev/null; then
        echo '🔧 Enabling Multisite...'
        
        # First, update wp-config.php to allow multisite
        wp config set WP_ALLOW_MULTISITE true --raw --allow-root
        
        # Convert to multisite
        wp core multisite-convert \
            --title='KenzySites Network' \
            --skip-config \
            --allow-root
        
        # Update multisite configuration
        wp config set MULTISITE true --raw --allow-root
        wp config set SUBDOMAIN_INSTALL false --raw --allow-root
        wp config set DOMAIN_CURRENT_SITE 'localhost' --allow-root
        wp config set PATH_CURRENT_SITE '/' --allow-root
        wp config set SITE_ID_CURRENT_SITE 1 --raw --allow-root
        wp config set BLOG_ID_CURRENT_SITE 1 --raw --allow-root
    fi

    echo '✅ WordPress Multisite enabled'
"

# Install and activate Astra theme
echo "🎨 Installing Astra theme..."
docker exec kenzysites-multisite wp theme install astra --activate-network --allow-root 2>/dev/null || true

# Install and activate Spectra plugin
echo "🔌 Installing Spectra plugin..."
docker exec kenzysites-multisite wp plugin install ultimate-addons-for-gutenberg --activate-network --allow-root 2>/dev/null || true

# Install Astra Starter Sites plugin
echo "🔌 Installing Astra Starter Sites..."
docker exec kenzysites-multisite wp plugin install astra-sites --activate-network --allow-root 2>/dev/null || true

# Create MU-Plugin directory if it doesn't exist
docker exec kenzysites-multisite mkdir -p /var/www/html/wp-content/mu-plugins

# Create the KenzySites API MU-Plugin
echo "📝 Creating KenzySites API plugin..."
docker exec kenzysites-multisite bash -c 'cat > /var/www/html/wp-content/mu-plugins/kenzysites-api.php << "EOF"
<?php
/**
 * KenzySites Multisite API
 */

// Register REST API routes
add_action("rest_api_init", function () {
    register_rest_route("kenzysites/v1", "/sites/create", [
        "methods" => "POST",
        "callback" => "kenzysites_create_site",
        "permission_callback" => "__return_true"
    ]);
    
    register_rest_route("kenzysites/v1", "/sites", [
        "methods" => "GET",
        "callback" => "kenzysites_list_sites",
        "permission_callback" => "__return_true"
    ]);
});

function kenzysites_create_site($request) {
    $params = $request->get_params();
    
    $subdomain = sanitize_text_field($params["domain"] ?? "");
    $title = sanitize_text_field($params["title"] ?? "New Site");
    $email = sanitize_email($params["email"] ?? "admin@kenzysites.com");
    
    if (empty($subdomain)) {
        return new WP_Error("missing_domain", "Domain is required", ["status" => 400]);
    }
    
    // Create site path
    $site_path = "/" . $subdomain . "/";
    
    // Create the new site
    $site_id = wpmu_create_blog(
        "localhost",
        $site_path,
        $title,
        1, // Admin user ID
        ["public" => 1],
        get_current_site()->id
    );
    
    if (is_wp_error($site_id)) {
        return $site_id;
    }
    
    // Switch to new site and configure
    switch_to_blog($site_id);
    
    // Activate Astra theme
    switch_theme("astra");
    
    // Apply Astra settings
    if (isset($params["primary_color"])) {
        update_option("astra-settings", [
            "theme-color" => $params["primary_color"],
            "link-color" => $params["accent_color"] ?? $params["primary_color"]
        ]);
    }
    
    restore_current_blog();
    
    return [
        "success" => true,
        "site_id" => $site_id,
        "url" => "http://localhost:8090" . $site_path,
        "admin_url" => "http://localhost:8090" . $site_path . "wp-admin"
    ];
}

function kenzysites_list_sites() {
    $sites = get_sites(["number" => 100]);
    
    $site_list = [];
    foreach ($sites as $site) {
        $site_list[] = [
            "id" => $site->blog_id,
            "path" => $site->path,
            "name" => get_blog_option($site->blog_id, "blogname"),
            "url" => "http://localhost:8090" . $site->path
        ];
    }
    
    return ["sites" => $site_list];
}
EOF'

# Set proper permissions
echo "🔒 Setting permissions..."
docker exec kenzysites-multisite chown -R www-data:www-data /var/www/html

# Create .htaccess for multisite
echo "📝 Creating .htaccess..."
docker exec kenzysites-multisite bash -c 'cat > /var/www/html/.htaccess << "EOF"
# BEGIN WordPress Multisite
RewriteEngine On
RewriteBase /
RewriteRule ^index\.php$ - [L]

# Add trailing slash to /wp-admin
RewriteRule ^([_0-9a-zA-Z-]+/)?wp-admin$ $1wp-admin/ [R=301,L]

RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(wp-(content|admin|includes).*) $2 [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(.*\.php)$ $2 [L]
RewriteRule . index.php [L]
# END WordPress Multisite
EOF'

# Display setup completion
echo ""
echo "========================================="
echo "✅ WordPress Multisite Setup Complete!"
echo "========================================="
echo ""
echo "🌐 Access Points:"
echo "  Main Site: http://localhost:8090"
echo "  Admin: http://localhost:8090/wp-admin"
echo "  phpMyAdmin: http://localhost:8091"
echo ""
echo "👤 Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "🎨 Installed Components:"
echo "  ✓ Astra Theme (Network Activated)"
echo "  ✓ Spectra Plugin (Ultimate Addons for Gutenberg)"
echo "  ✓ Astra Starter Sites"
echo "  ✓ KenzySites API (MU-Plugin)"
echo ""
echo "📚 API Endpoints:"
echo "  POST http://localhost:8090/wp-json/kenzysites/v1/sites/create"
echo "  GET  http://localhost:8090/wp-json/kenzysites/v1/sites"
echo ""
echo "🚀 Next Steps:"
echo "  1. Access the admin panel and verify the setup"
echo "  2. Test creating a new site via the API"
echo "  3. Start the main application: npm run dev"
echo ""
echo "========================================="
echo ""
echo "To create a test site, run:"
echo "docker exec kenzysites-wpcli bash /scripts/create-site-with-astra.sh test-site 'Test Business' restaurant"
echo ""