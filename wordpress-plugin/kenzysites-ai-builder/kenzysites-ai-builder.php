<?php
/**
 * Plugin Name: KenzySites AI Builder
 * Plugin URI: https://kenzysites.com
 * Description: Plugin para integração do AI Builder do KenzySites com WordPress
 * Version: 1.0.0
 * Author: KenzySites
 * License: GPL v2 or later
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Plugin constants
define('KENZYSITES_AI_VERSION', '1.0.0');
define('KENZYSITES_AI_PATH', plugin_dir_path(__FILE__));
define('KENZYSITES_AI_URL', plugin_dir_url(__FILE__));

/**
 * Main KenzySites AI Builder Class
 */
class KenzySites_AI_Builder {
    
    public function __construct() {
        // Include required files
        $this->includes();
        
        add_action('init', array($this, 'init'));
        add_action('rest_api_init', array($this, 'register_rest_routes'));
    }

    /**
     * Include required files
     */
    private function includes() {
        require_once KENZYSITES_AI_PATH . 'includes/color-manager.php';
    }
    
    /**
     * Initialize plugin
     */
    public function init() {
        // Check if Elementor is active
        if (!did_action('elementor/loaded')) {
            add_action('admin_notices', array($this, 'admin_notice_missing_elementor'));
            return;
        }
    }
    
    /**
     * Register REST API routes
     */
    public function register_rest_routes() {
        register_rest_route('kenzysites/v1', '/elementor/import', array(
            'methods' => 'POST',
            'callback' => array($this, 'import_elementor_template'),
            'permission_callback' => array($this, 'check_permissions')
        ));
        
        register_rest_route('kenzysites/v1', '/elementor/status', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_elementor_status'),
            'permission_callback' => array($this, 'check_permissions')
        ));
        
        register_rest_route('kenzysites/v1', '/site/create', array(
            'methods' => 'POST',
            'callback' => array($this, 'create_site'),
            'permission_callback' => array($this, 'check_permissions')
        ));
        
        register_rest_route('kenzysites/v1', '/elementor/templates', array(
            'methods' => 'GET',
            'callback' => array($this, 'get_elementor_templates'),
            'permission_callback' => array($this, 'check_permissions')
        ));
        
        register_rest_route('kenzysites/v1', '/elementor/export/(?P<id>\\d+)', array(
            'methods' => 'GET',
            'callback' => array($this, 'export_elementor_template'),
            'permission_callback' => array($this, 'check_permissions')
        ));
    }
    
    /**
     * Check user permissions
     */
    public function check_permissions($request) {
        return current_user_can('edit_posts');
    }
    
    /**
     * Import Elementor template
     */
    public function import_elementor_template($request) {
        if (!class_exists('Elementor\Plugin')) {
            return new WP_Error('elementor_not_found', 'Elementor plugin is not active', array('status' => 400));
        }
        
        $params = $request->get_json_params();
        
        if (empty($params['title']) || empty($params['content'])) {
            return new WP_Error('missing_data', 'Title and content are required', array('status' => 400));
        }
        
        try {
            // Create the page
            $page_data = array(
                'post_title'    => sanitize_text_field($params['title']),
                'post_type'     => isset($params['type']) ? sanitize_text_field($params['type']) : 'page',
                'post_status'   => isset($params['status']) ? sanitize_text_field($params['status']) : 'publish',
                'post_content'  => '', // Elementor will handle the content
            );
            
            $page_id = wp_insert_post($page_data);
            
            if (is_wp_error($page_id)) {
                return new WP_Error('page_creation_failed', $page_id->get_error_message(), array('status' => 500));
            }
            
            // Set Elementor data
            update_post_meta($page_id, '_elementor_edit_mode', 'builder');
            update_post_meta($page_id, '_elementor_template_type', 'wp-page');
            update_post_meta($page_id, '_elementor_version', ELEMENTOR_VERSION);
            
            // Handle content - it can be array, object, or JSON string
            $elementor_data = null;
            
            if (is_array($params['content'])) {
                // Already an array, use as-is
                $elementor_data = $params['content'];
            } elseif (is_string($params['content'])) {
                // JSON string, decode it
                $elementor_data = json_decode($params['content'], true);
                if (json_last_error() !== JSON_ERROR_NONE) {
                    wp_delete_post($page_id, true);
                    return new WP_Error('invalid_json', 'Invalid JSON content: ' . json_last_error_msg(), array('status' => 400));
                }
            } else {
                // Invalid format
                wp_delete_post($page_id, true);
                return new WP_Error('invalid_content', 'Content must be array or JSON string', array('status' => 400));
            }
            
            // Save Elementor data
            update_post_meta($page_id, '_elementor_data', $elementor_data);
            
            // Clear Elementor cache
            if (class_exists('Elementor\Plugin')) {
                \Elementor\Plugin::$instance->files_manager->clear_cache();
            }
            
            return array(
                'success' => true,
                'page_id' => $page_id,
                'page_url' => get_permalink($page_id),
                'edit_url' => admin_url('post.php?post=' . $page_id . '&action=elementor'),
                'message' => 'Template imported successfully'
            );
            
        } catch (Exception $e) {
            return new WP_Error('import_failed', $e->getMessage(), array('status' => 500));
        }
    }
    
    /**
     * Get Elementor status
     */
    public function get_elementor_status($request) {
        $elementor_active = class_exists('Elementor\Plugin');
        $elementor_version = $elementor_active ? ELEMENTOR_VERSION : null;
        $elementor_pro_active = class_exists('ElementorPro\Plugin');
        
        return array(
            'elementor_active' => $elementor_active,
            'elementor_version' => $elementor_version,
            'elementor_pro_active' => $elementor_pro_active,
            'wordpress_version' => get_bloginfo('version'),
            'php_version' => PHP_VERSION,
            'can_import' => $elementor_active && current_user_can('edit_posts')
        );
    }
    
    /**
     * Create new site (for multisite)
     */
    public function create_site($request) {
        if (!is_multisite()) {
            return new WP_Error('not_multisite', 'This is not a multisite installation', array('status' => 400));
        }
        
        if (!current_user_can('manage_network')) {
            return new WP_Error('insufficient_permissions', 'You do not have permission to create sites', array('status' => 403));
        }
        
        $params = $request->get_json_params();
        
        if (empty($params['domain']) || empty($params['title'])) {
            return new WP_Error('missing_data', 'Domain and title are required', array('status' => 400));
        }
        
        $domain = sanitize_text_field($params['domain']);
        $title = sanitize_text_field($params['title']);
        $path = isset($params['path']) ? sanitize_text_field($params['path']) : '/';
        $user_id = get_current_user_id();
        
        $site_id = wpmu_create_blog($domain, $path, $title, $user_id);
        
        if (is_wp_error($site_id)) {
            return new WP_Error('site_creation_failed', $site_id->get_error_message(), array('status' => 500));
        }
        
        return array(
            'success' => true,
            'site_id' => $site_id,
            'site_url' => get_site_url($site_id),
            'admin_url' => get_admin_url($site_id),
            'message' => 'Site created successfully'
        );
    }
    
    /**
     * Admin notice for missing Elementor
     */
    public function admin_notice_missing_elementor() {
        if (isset($_GET['activate'])) {
            unset($_GET['activate']);
        }
        
        $message = sprintf(
            esc_html__('KenzySites AI Builder requires %1$s to be installed and activated.', 'kenzysites'),
            '<strong>' . esc_html__('Elementor', 'kenzysites') . '</strong>'
        );
        
        printf('<div class="notice notice-warning is-dismissible"><p>%1$s</p></div>', $message);
    }
    
    /**
     * Get Elementor templates
     */
    public function get_elementor_templates($request) {
        if (!class_exists('Elementor\Plugin')) {
            return new WP_Error('elementor_not_found', 'Elementor plugin is not active', array('status' => 400));
        }
        
        // Get all Elementor library posts
        $templates = get_posts(array(
            'post_type' => 'elementor_library',
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'meta_query' => array(
                array(
                    'key' => '_elementor_data',
                    'compare' => 'EXISTS'
                )
            )
        ));
        
        $template_list = array();
        
        foreach ($templates as $template) {
            $template_type = get_post_meta($template->ID, '_elementor_template_type', true);
            $template_list[] = array(
                'id' => $template->ID,
                'title' => $template->post_title,
                'type' => $template_type,
                'date' => $template->post_date,
                'modified' => $template->post_modified,
                'export_url' => rest_url('kenzysites/v1/elementor/export/' . $template->ID)
            );
        }
        
        return array(
            'success' => true,
            'templates' => $template_list,
            'total' => count($template_list)
        );
    }
    
    /**
     * Export Elementor template
     */
    public function export_elementor_template($request) {
        if (!class_exists('Elementor\Plugin')) {
            return new WP_Error('elementor_not_found', 'Elementor plugin is not active', array('status' => 400));
        }
        
        $template_id = $request['id'];
        $template = get_post($template_id);
        
        if (!$template || $template->post_type !== 'elementor_library') {
            return new WP_Error('template_not_found', 'Template not found', array('status' => 404));
        }
        
        // Get Elementor data
        $elementor_data = get_post_meta($template_id, '_elementor_data', true);
        $template_type = get_post_meta($template_id, '_elementor_template_type', true);
        
        if (empty($elementor_data)) {
            return new WP_Error('no_data', 'No Elementor data found for this template', array('status' => 404));
        }
        
        // Prepare template data in our format
        $ai_template = array(
            'id' => 'custom-' . $template_id,
            'title' => $template->post_title,
            'type' => 'page',
            'category' => array('custom', 'elementor'),
            'tags' => array('custom', 'user-created', $template_type),
            'content' => is_string($elementor_data) ? json_decode($elementor_data, true) : $elementor_data,
            'thumbnail' => get_the_post_thumbnail_url($template_id),
            'requiredPlugins' => array('elementor'),
            'customizable' => array(
                'colors' => true,
                'fonts' => true,
                'content' => true,
                'images' => true
            ),
            'originalId' => $template_id,
            'originalType' => $template_type,
            'exportDate' => current_time('c')
        );
        
        return array(
            'success' => true,
            'template' => $ai_template,
            'message' => 'Template exported successfully'
        );
    }
}

// Initialize plugin
new KenzySites_AI_Builder();