#!/bin/bash

# WordPress Multisite Setup Script
# Configures WordPress Multisite with Astra theme and Spectra plugin

echo "🚀 Starting WordPress Multisite Setup..."

# Wait for WordPress to be ready
until wp core version --allow-root &>/dev/null; do
    echo "⏳ Waiting for WordPress to be ready..."
    sleep 5
done

# Check if WordPress is already installed
if ! wp core is-installed --allow-root 2>/dev/null; then
    echo "📦 Installing WordPress..."
    
    wp core install \
        --url="http://localhost:8090" \
        --title="KenzySites Platform" \
        --admin_user="admin" \
        --admin_password="admin123" \
        --admin_email="admin@kenzysites.com" \
        --skip-email \
        --allow-root
        
    echo "✅ WordPress installed successfully"
else
    echo "✅ WordPress already installed"
fi

# Enable Multisite if not already enabled
if ! wp core is-installed --network --allow-root 2>/dev/null; then
    echo "🔧 Converting to Multisite..."
    
    # Enable multisite
    wp core multisite-convert \
        --title="KenzySites Network" \
        --subdomains \
        --allow-root
        
    echo "✅ Multisite enabled"
else
    echo "✅ Multisite already enabled"
fi

# Install and activate Astra theme
echo "🎨 Installing Astra theme..."
if ! wp theme is-installed astra --allow-root; then
    wp theme install astra --allow-root
fi

# Make Astra the default theme for new sites
wp theme enable astra --network --activate --allow-root
echo "✅ Astra theme installed and activated"

# Install essential plugins
echo "🔌 Installing essential plugins..."

# Spectra - Gutenberg Blocks
if ! wp plugin is-installed ultimate-addons-for-gutenberg --allow-root; then
    wp plugin install ultimate-addons-for-gutenberg --allow-root
fi
wp plugin activate ultimate-addons-for-gutenberg --network --allow-root

# Starter Templates (Astra Sites)
if ! wp plugin is-installed astra-sites --allow-root; then
    wp plugin install astra-sites --allow-root
fi
wp plugin activate astra-sites --network --allow-root

# WP REST API Controller (for better API control)
if ! wp plugin is-installed wp-rest-api-controller --allow-root; then
    wp plugin install wp-rest-api-controller --allow-root
fi
wp plugin activate wp-rest-api-controller --network --allow-root

# Redis Object Cache (performance)
if ! wp plugin is-installed redis-cache --allow-root; then
    wp plugin install redis-cache --allow-root
fi

echo "✅ Essential plugins installed"

# Create MU-Plugin for site generation API
echo "📝 Creating MU-Plugin for KenzySites API..."
cat > /var/www/html/wp-content/mu-plugins/kenzysites-api.php << 'EOF'
<?php
/**
 * KenzySites API
 * MU-Plugin for site generation and management
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Register REST API routes
add_action('rest_api_init', function () {
    // Create new site endpoint
    register_rest_route('kenzysites/v1', '/sites/create', [
        'methods' => 'POST',
        'callback' => 'kenzysites_create_site',
        'permission_callback' => 'kenzysites_check_permissions'
    ]);
    
    // List sites endpoint
    register_rest_route('kenzysites/v1', '/sites', [
        'methods' => 'GET',
        'callback' => 'kenzysites_list_sites',
        'permission_callback' => 'kenzysites_check_permissions'
    ]);
    
    // Configure site endpoint
    register_rest_route('kenzysites/v1', '/sites/(?P<id>\d+)/configure', [
        'methods' => 'POST',
        'callback' => 'kenzysites_configure_site',
        'permission_callback' => 'kenzysites_check_permissions'
    ]);
});

// Check API permissions
function kenzysites_check_permissions() {
    // For now, allow all requests (configure authentication later)
    return true;
}

// Create new site
function kenzysites_create_site($request) {
    $params = $request->get_params();
    
    $domain = sanitize_text_field($params['domain'] ?? '');
    $title = sanitize_text_field($params['title'] ?? 'New Site');
    $email = sanitize_email($params['email'] ?? 'admin@kenzysites.com');
    
    if (empty($domain)) {
        return new WP_Error('missing_domain', 'Domain is required', ['status' => 400]);
    }
    
    // Create subdomain site
    $site_domain = $domain . '.localhost';
    $site_path = '/';
    
    // Create the new site
    $site_id = wpmu_create_blog(
        $site_domain,
        $site_path,
        $title,
        get_current_user_id(),
        ['public' => 1],
        get_current_site()->id
    );
    
    if (is_wp_error($site_id)) {
        return $site_id;
    }
    
    // Switch to new site context
    switch_to_blog($site_id);
    
    // Activate Astra theme
    switch_theme('astra');
    
    // Configure Astra settings
    update_option('astra-settings', [
        'theme-color' => $params['primary_color'] ?? '#0274be',
        'link-color' => $params['accent_color'] ?? '#0274be',
        'text-color' => '#3a3a3a',
        'header-bg-color' => '#ffffff',
        'footer-bg-color' => '#f8f9fa',
    ]);
    
    // Restore original site context
    restore_current_blog();
    
    return [
        'success' => true,
        'site_id' => $site_id,
        'url' => 'http://' . $site_domain . ':8090',
        'admin_url' => 'http://' . $site_domain . ':8090/wp-admin',
        'message' => 'Site created successfully'
    ];
}

// List all sites
function kenzysites_list_sites() {
    $sites = get_sites([
        'number' => 100,
        'orderby' => 'id',
        'order' => 'DESC'
    ]);
    
    $site_list = [];
    foreach ($sites as $site) {
        $site_list[] = [
            'id' => $site->blog_id,
            'domain' => $site->domain,
            'path' => $site->path,
            'name' => get_blog_option($site->blog_id, 'blogname'),
            'url' => 'http://' . $site->domain . ':8090' . $site->path,
            'admin_url' => 'http://' . $site->domain . ':8090' . $site->path . 'wp-admin'
        ];
    }
    
    return ['sites' => $site_list];
}

// Configure existing site
function kenzysites_configure_site($request) {
    $site_id = intval($request['id']);
    $params = $request->get_params();
    
    // Switch to site context
    switch_to_blog($site_id);
    
    // Update site configuration based on params
    if (isset($params['title'])) {
        update_option('blogname', sanitize_text_field($params['title']));
    }
    
    if (isset($params['tagline'])) {
        update_option('blogdescription', sanitize_text_field($params['tagline']));
    }
    
    // Update Astra settings if provided
    if (isset($params['astra_settings'])) {
        update_option('astra-settings', $params['astra_settings']);
    }
    
    // Create pages if provided
    if (isset($params['pages']) && is_array($params['pages'])) {
        foreach ($params['pages'] as $page_data) {
            wp_insert_post([
                'post_title' => $page_data['title'],
                'post_content' => $page_data['content'],
                'post_status' => 'publish',
                'post_type' => 'page',
                'meta_input' => $page_data['meta'] ?? []
            ]);
        }
    }
    
    // Restore original context
    restore_current_blog();
    
    return [
        'success' => true,
        'message' => 'Site configured successfully'
    ];
}
EOF

echo "✅ MU-Plugin created"

# Set proper permissions
echo "🔒 Setting permissions..."
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html

# Create .htaccess for multisite
echo "📝 Creating .htaccess for multisite..."
cat > /var/www/html/.htaccess << 'EOF'
RewriteEngine On
RewriteBase /
RewriteRule ^index\.php$ - [L]

# add a trailing slash to /wp-admin
RewriteRule ^wp-admin$ wp-admin/ [R=301,L]

RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
RewriteRule ^(wp-(content|admin|includes).*) $1 [L]
RewriteRule ^(.*\.php)$ $1 [L]
RewriteRule . index.php [L]
EOF

echo "✅ .htaccess created"

# Display setup information
echo ""
echo "========================================="
echo "✅ WordPress Multisite Setup Complete!"
echo "========================================="
echo ""
echo "🌐 Main Site URL: http://localhost:8090"
echo "👤 Admin Username: admin"
echo "🔑 Admin Password: admin123"
echo ""
echo "📚 API Endpoints:"
echo "  - Create Site: POST http://localhost:8090/wp-json/kenzysites/v1/sites/create"
echo "  - List Sites: GET http://localhost:8090/wp-json/kenzysites/v1/sites"
echo "  - Configure Site: POST http://localhost:8090/wp-json/kenzysites/v1/sites/{id}/configure"
echo ""
echo "🎨 Installed Theme: Astra"
echo "🔌 Installed Plugins:"
echo "  - Spectra (Ultimate Addons for Gutenberg)"
echo "  - Astra Starter Sites"
echo "  - WP REST API Controller"
echo ""
echo "========================================="