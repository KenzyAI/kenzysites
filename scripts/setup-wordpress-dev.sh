#!/bin/bash

# KenzySites WordPress Development Setup Script
# Sets up WordPress with Astra, Elementor, ACF and other required plugins

echo "🚀 KenzySites WordPress Development Setup"
echo "========================================="

# Wait for WordPress to be ready
echo "⏳ Waiting for WordPress to be ready..."
sleep 10

# Function to run WP-CLI commands
wp_cli() {
    docker-compose -f docker-compose.wordpress-dev.yml run --rm wp-cli "$@"
}

# Check if WordPress is installed
echo "📊 Checking WordPress installation..."
if ! wp_cli core is-installed 2>/dev/null; then
    echo "📦 Installing WordPress..."
    wp_cli core install \
        --url="http://localhost:8090" \
        --title="KenzySites Template Development" \
        --admin_user="admin" \
        --admin_password="admin123" \
        --admin_email="admin@kenzysites.local" \
        --skip-email
else
    echo "✅ WordPress is already installed"
fi

# Update WordPress to latest version
echo "🔄 Updating WordPress core..."
wp_cli core update

# Install required plugins
echo "📦 Installing required plugins..."

# Astra Theme
echo "  • Installing Astra theme..."
wp_cli theme install astra --activate

# Essential FREE plugins that work with our system
PLUGINS=(
    "elementor"                    # Page builder (free version first)
    "advanced-custom-fields"       # ACF free version
    "wordpress-seo"                # Yoast SEO
    "wp-optimize"                  # Performance optimization
    "redis-cache"                  # Redis object cache
    "duplicate-post"               # For template duplication
    "custom-post-type-ui"          # Custom post types
    "wp-mail-smtp"                 # Email configuration
    "all-in-one-wp-migration"      # For export/import
)

for plugin in "${PLUGINS[@]}"; do
    echo "  • Installing $plugin..."
    wp_cli plugin install "$plugin" --activate
done

# Configure WordPress settings
echo "⚙️ Configuring WordPress settings..."

# Set permalink structure
wp_cli rewrite structure '/%postname%/'

# Set timezone to Brazil
wp_cli option update timezone_string 'America/Sao_Paulo'

# Set language to Brazilian Portuguese
echo "🇧🇷 Setting language to Portuguese (Brazil)..."
wp_cli language core install pt_BR
wp_cli site switch-language pt_BR

# Create template categories
echo "📁 Creating template categories..."
wp_cli term create category "Templates Restaurante" --description="Templates para restaurantes"
wp_cli term create category "Templates Saúde" --description="Templates para clínicas e saúde"
wp_cli term create category "Templates E-commerce" --description="Templates para lojas online"
wp_cli term create category "Templates Serviços" --description="Templates para empresas de serviços"
wp_cli term create category "Templates Educação" --description="Templates para instituições educacionais"

# Create required pages
echo "📄 Creating base pages..."
wp_cli post create --post_type=page --post_title="Home Template" --post_status=publish
wp_cli post create --post_type=page --post_title="Sobre Template" --post_status=publish
wp_cli post create --post_type=page --post_title="Serviços Template" --post_status=publish
wp_cli post create --post_type=page --post_title="Contato Template" --post_status=publish
wp_cli post create --post_type=page --post_title="Blog Template" --post_status=publish

# Create ACF field groups for templates
echo "🔧 Setting up ACF field groups..."

# Note: ACF Pro would need manual activation with license
# For now, we'll use the free version and create basic field groups

# Create directories for templates and exports
echo "📁 Creating required directories..."
docker-compose -f docker-compose.wordpress-dev.yml exec -T wordpress-dev bash -c "
    mkdir -p /var/www/html/wp-content/templates
    mkdir -p /var/www/html/wp-content/exports
    mkdir -p /var/www/html/wp-content/uploads
    chown -R www-data:www-data /var/www/html/wp-content/
    chmod -R 755 /var/www/html/wp-content/
"

# Install additional development tools
echo "🛠️ Installing development tools..."
wp_cli plugin install theme-check --activate
wp_cli plugin install query-monitor --activate

# Create a custom plugin for our template system
echo "🔌 Creating KenzySites template plugin..."
cat > wordpress-plugins/kenzysites-templates/kenzysites-templates.php << 'EOF'
<?php
/**
 * Plugin Name: KenzySites Templates
 * Description: Template management system for KenzySites
 * Version: 1.0.0
 * Author: KenzySites
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('KENZYSITES_VERSION', '1.0.0');
define('KENZYSITES_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('KENZYSITES_PLUGIN_URL', plugin_dir_url(__FILE__));

// Add placeholder support
function kenzysites_add_placeholders() {
    // Register placeholders for dynamic content
    $placeholders = array(
        '{{BUSINESS_NAME}}' => get_option('kenzysites_business_name', 'Nome do Negócio'),
        '{{BUSINESS_DESCRIPTION}}' => get_option('kenzysites_business_description', 'Descrição do negócio'),
        '{{PHONE_NUMBER}}' => get_option('kenzysites_phone', '(11) 9999-9999'),
        '{{WHATSAPP_NUMBER}}' => get_option('kenzysites_whatsapp', '(11) 9999-9999'),
        '{{EMAIL}}' => get_option('kenzysites_email', 'contato@exemplo.com'),
        '{{ADDRESS}}' => get_option('kenzysites_address', 'Rua Exemplo, 123'),
        '{{HERO_TITLE}}' => get_option('kenzysites_hero_title', 'Bem-vindo'),
        '{{HERO_SUBTITLE}}' => get_option('kenzysites_hero_subtitle', 'Sua solução completa'),
        '{{CTA_TEXT}}' => get_option('kenzysites_cta_text', 'Entre em Contato'),
        '{{PRIMARY_COLOR}}' => get_option('kenzysites_primary_color', '#0066FF'),
        '{{SECONDARY_COLOR}}' => get_option('kenzysites_secondary_color', '#00D4FF'),
    );
    
    return $placeholders;
}

// Add admin menu
add_action('admin_menu', 'kenzysites_add_admin_menu');
function kenzysites_add_admin_menu() {
    add_menu_page(
        'KenzySites Templates',
        'KenzySites',
        'manage_options',
        'kenzysites',
        'kenzysites_admin_page',
        'dashicons-layout',
        30
    );
}

// Admin page
function kenzysites_admin_page() {
    ?>
    <div class="wrap">
        <h1>KenzySites Template System</h1>
        <p>Sistema de templates para geração automatizada de sites.</p>
        
        <h2>Placeholders Disponíveis</h2>
        <table class="wp-list-table widefat fixed striped">
            <thead>
                <tr>
                    <th>Placeholder</th>
                    <th>Valor Atual</th>
                    <th>Descrição</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $placeholders = kenzysites_add_placeholders();
                foreach ($placeholders as $key => $value) {
                    echo "<tr>";
                    echo "<td><code>{$key}</code></td>";
                    echo "<td>{$value}</td>";
                    echo "<td>Placeholder para " . str_replace(array('{{', '}}'), '', $key) . "</td>";
                    echo "</tr>";
                }
                ?>
            </tbody>
        </table>
        
        <h2>Templates Criados</h2>
        <p>Use o Elementor para criar templates e exporte-os usando o botão abaixo.</p>
        <button class="button button-primary" onclick="exportTemplates()">Exportar Templates</button>
    </div>
    
    <script>
    function exportTemplates() {
        alert('Função de exportação será implementada em breve!');
    }
    </script>
    <?php
}

// Hook to replace placeholders in content
add_filter('the_content', 'kenzysites_replace_placeholders');
function kenzysites_replace_placeholders($content) {
    $placeholders = kenzysites_add_placeholders();
    
    foreach ($placeholders as $key => $value) {
        $content = str_replace($key, $value, $content);
    }
    
    return $content;
}
EOF

# Copy plugin to WordPress
docker-compose -f docker-compose.wordpress-dev.yml exec -T wordpress-dev bash -c "
    mkdir -p /var/www/html/wp-content/plugins/kenzysites-templates
"
docker cp wordpress-plugins/kenzysites-templates/kenzysites-templates.php \
    kenzysites-wordpress-dev:/var/www/html/wp-content/plugins/kenzysites-templates/

# Activate our custom plugin
wp_cli plugin activate kenzysites-templates

# Display access information
echo ""
echo "✅ WordPress Development Environment Setup Complete!"
echo "===================================================="
echo ""
echo "🌐 WordPress URL: http://localhost:8090"
echo "👤 Admin URL: http://localhost:8090/wp-admin"
echo "📧 Username: admin"
echo "🔑 Password: admin123"
echo ""
echo "🗄️ PHPMyAdmin: http://localhost:8091"
echo "👤 Username: wordpress"
echo "🔑 Password: wordpress_pass"
echo ""
echo "📦 Installed Plugins:"
echo "  • Elementor (Page Builder)"
echo "  • Advanced Custom Fields"
echo "  • Yoast SEO"
echo "  • WP Optimize"
echo "  • KenzySites Templates (Custom)"
echo ""
echo "🎨 Active Theme: Astra"
echo ""
echo "📝 Next Steps:"
echo "  1. Access WordPress admin"
echo "  2. Create templates using Elementor"
echo "  3. Use placeholders like {{BUSINESS_NAME}} in content"
echo "  4. Export templates for use in the system"
echo ""
echo "🚀 Happy template building!"