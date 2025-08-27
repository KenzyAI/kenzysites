<?php
/**
 * Plugin Name: KenzySites Converter
 * Description: Converte landing pages Elementor para templates ACF do sistema KenzySites
 * Version: 1.0.0
 * Author: KenzySites
 * Text Domain: kenzysites-converter
 * Domain Path: /languages
 * Requires at least: 5.0
 * Tested up to: 6.4
 * Requires PHP: 7.4
 * Network: false
 * 
 * @package KenzySitesConverter
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('KENZYSITES_CONVERTER_VERSION', '1.0.0');
define('KENZYSITES_CONVERTER_PLUGIN_URL', plugin_dir_url(__FILE__));
define('KENZYSITES_CONVERTER_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('KENZYSITES_CONVERTER_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * Main Plugin Class
 */
class KenzySitesConverter {
    
    /**
     * Single instance of the class
     */
    private static $instance = null;
    
    /**
     * Plugin components
     */
    public $elementor_scanner;
    public $acf_converter;
    public $api_client;
    public $admin_page;
    public $template_engine;
    
    /**
     * Get single instance
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * Constructor
     */
    private function __construct() {
        $this->init();
    }
    
    /**
     * Initialize plugin
     */
    private function init() {
        // Check if Elementor is active
        add_action('admin_init', [$this, 'check_elementor_dependency']);
        
        // Load plugin textdomain
        add_action('plugins_loaded', [$this, 'load_textdomain']);
        
        // Initialize components
        add_action('plugins_loaded', [$this, 'init_components']);
        
        // Admin hooks
        add_action('admin_menu', [$this, 'add_admin_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_scripts']);
        
        // AJAX hooks
        add_action('wp_ajax_kenzysites_scan_pages', [$this, 'ajax_scan_pages']);
        add_action('wp_ajax_kenzysites_convert_page', [$this, 'ajax_convert_page']);
        add_action('wp_ajax_kenzysites_sync_to_kenzysites', [$this, 'ajax_sync_to_kenzysites']);
        add_action('wp_ajax_kenzysites_test_connection', [$this, 'ajax_test_connection']);
        
        // Plugin activation/deactivation hooks
        register_activation_hook(__FILE__, [$this, 'activate']);
        register_deactivation_hook(__FILE__, [$this, 'deactivate']);
        
        // ACF and template hooks
        add_action('acf/init', [$this, 'load_acf_field_groups']);
        add_filter('template_include', [$this, 'load_acf_template'], 99);
        
        // REST API hooks
        add_action('rest_api_init', [$this, 'register_rest_endpoints']);
    }
    
    /**
     * Check if Elementor is active
     */
    public function check_elementor_dependency() {
        if (!is_plugin_active('elementor/elementor.php')) {
            add_action('admin_notices', function() {
                ?>
                <div class="notice notice-error is-dismissible">
                    <p>
                        <strong>KenzySites Converter:</strong> 
                        Este plugin requer o <strong>Elementor</strong> para funcionar. 
                        <a href="<?php echo admin_url('plugin-install.php?s=elementor&tab=search&type=term'); ?>">
                            Instalar Elementor
                        </a>
                    </p>
                </div>
                <?php
            });
            return false;
        }
        return true;
    }
    
    /**
     * Load plugin textdomain
     */
    public function load_textdomain() {
        load_plugin_textdomain(
            'kenzysites-converter',
            false,
            dirname(KENZYSITES_CONVERTER_PLUGIN_BASENAME) . '/languages'
        );
    }
    
    /**
     * Initialize plugin components
     */
    public function init_components() {
        // Only proceed if Elementor is active
        if (!$this->check_elementor_dependency()) {
            return;
        }
        
        // Load component classes
        require_once KENZYSITES_CONVERTER_PLUGIN_PATH . 'includes/class-elementor-scanner.php';
        require_once KENZYSITES_CONVERTER_PLUGIN_PATH . 'includes/class-acf-converter.php';
        require_once KENZYSITES_CONVERTER_PLUGIN_PATH . 'includes/class-api-client.php';
        require_once KENZYSITES_CONVERTER_PLUGIN_PATH . 'includes/class-admin-page.php';
        require_once KENZYSITES_CONVERTER_PLUGIN_PATH . 'includes/class-template-engine.php';
        
        // Initialize components
        $this->elementor_scanner = new KenzySites_Elementor_Scanner();
        $this->acf_converter = new KenzySites_ACF_Converter();
        $this->api_client = new KenzySites_API_Client();
        $this->admin_page = new KenzySites_Admin_Page();
        $this->template_engine = new KenzySites_Template_Engine();
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_menu_page(
            __('KenzySites Converter', 'kenzysites-converter'),
            __('KenzySites', 'kenzysites-converter'),
            'manage_options',
            'kenzysites-converter',
            [$this, 'admin_dashboard_page'],
            'dashicons-convert',
            30
        );
        
        add_submenu_page(
            'kenzysites-converter',
            __('Dashboard', 'kenzysites-converter'),
            __('Dashboard', 'kenzysites-converter'),
            'manage_options',
            'kenzysites-converter',
            [$this, 'admin_dashboard_page']
        );
        
        add_submenu_page(
            'kenzysites-converter',
            __('Converter', 'kenzysites-converter'),
            __('Converter', 'kenzysites-converter'),
            'manage_options',
            'kenzysites-converter-convert',
            [$this, 'admin_converter_page']
        );
        
        add_submenu_page(
            'kenzysites-converter',
            __('Configurações', 'kenzysites-converter'),
            __('Configurações', 'kenzysites-converter'),
            'manage_options',
            'kenzysites-converter-settings',
            [$this, 'admin_settings_page']
        );
        
        add_submenu_page(
            'kenzysites-converter',
            __('Template Manager', 'kenzysites-converter'),
            __('📝 Templates', 'kenzysites-converter'),
            'manage_options',
            'kenzysites-template-manager',
            [$this, 'admin_template_manager_page']
        );
    }
    
    /**
     * Enqueue admin scripts and styles
     */
    public function enqueue_admin_scripts($hook) {
        // Only load on our plugin pages
        if (strpos($hook, 'kenzysites-converter') === false) {
            return;
        }
        
        wp_enqueue_style(
            'kenzysites-converter-admin',
            KENZYSITES_CONVERTER_PLUGIN_URL . 'admin/css/admin-style.css',
            [],
            KENZYSITES_CONVERTER_VERSION
        );
        
        wp_enqueue_script(
            'kenzysites-converter-admin',
            KENZYSITES_CONVERTER_PLUGIN_URL . 'admin/js/admin-script.js',
            ['jquery'],
            KENZYSITES_CONVERTER_VERSION,
            true
        );
        
        wp_localize_script('kenzysites-converter-admin', 'kenzysitesAjax', [
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('kenzysites_nonce'),
            'strings' => [
                'scanning' => __('Escaneando páginas...', 'kenzysites-converter'),
                'converting' => __('Convertendo...', 'kenzysites-converter'),
                'syncing' => __('Enviando para KenzySites...', 'kenzysites-converter'),
                'success' => __('Sucesso!', 'kenzysites-converter'),
                'error' => __('Erro:', 'kenzysites-converter'),
                'confirm_convert' => __('Tem certeza que deseja converter esta página?', 'kenzysites-converter')
            ]
        ]);
    }
    
    /**
     * Admin dashboard page
     */
    public function admin_dashboard_page() {
        include KENZYSITES_CONVERTER_PLUGIN_PATH . 'admin/views/dashboard.php';
    }
    
    /**
     * Admin converter page
     */
    public function admin_converter_page() {
        include KENZYSITES_CONVERTER_PLUGIN_PATH . 'admin/views/converter.php';
    }
    
    /**
     * Admin settings page
     */
    public function admin_settings_page() {
        include KENZYSITES_CONVERTER_PLUGIN_PATH . 'admin/views/settings.php';
    }
    
    /**
     * Admin template manager page
     */
    public function admin_template_manager_page() {
        include KENZYSITES_CONVERTER_PLUGIN_PATH . 'admin/views/template-manager.php';
    }
    
    /**
     * AJAX: Scan Elementor pages
     */
    public function ajax_scan_pages() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        try {
            $pages = $this->elementor_scanner->scan_elementor_pages();
            wp_send_json_success($pages);
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * AJAX: Convert page to ACF
     */
    public function ajax_convert_page() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        $page_id = intval($_POST['page_id']);
        $landing_page_type = sanitize_text_field($_POST['landing_page_type'] ?? 'generic');
        
        try {
            $result = $this->acf_converter->convert_page($page_id, $landing_page_type);
            wp_send_json_success($result);
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * AJAX: Sync converted template to KenzySites
     */
    public function ajax_sync_to_kenzysites() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        $template_id = sanitize_text_field($_POST['template_id']);
        
        try {
            $result = $this->api_client->sync_template($template_id);
            wp_send_json_success($result);
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * AJAX: Test API connection
     */
    public function ajax_test_connection() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        try {
            $result = $this->api_client->test_connection();
            wp_send_json_success($result);
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * Plugin activation
     */
    public function activate() {
        // Create database tables if needed
        $this->create_tables();
        
        // Set default options
        add_option('kenzysites_converter_version', KENZYSITES_CONVERTER_VERSION);
        add_option('kenzysites_api_url', 'http://localhost:8000/api');
        add_option('kenzysites_api_key', '');
        add_option('kenzysites_auto_sync', 'yes');
        
        // Clear rewrite rules
        flush_rewrite_rules();
    }
    
    /**
     * Plugin deactivation
     */
    public function deactivate() {
        // Clear scheduled events if any
        wp_clear_scheduled_hook('kenzysites_sync_templates');
        
        // Clear rewrite rules
        flush_rewrite_rules();
    }
    
    /**
     * Load ACF field groups for converted pages
     */
    public function load_acf_field_groups() {
        if (!function_exists('acf_add_local_field_group')) {
            return;
        }
        
        global $wpdb;
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        // Get all converted templates
        $templates = $wpdb->get_results(
            "SELECT page_id, acf_data FROM $table_name",
            ARRAY_A
        );
        
        foreach ($templates as $template) {
            $field_groups = json_decode($template['acf_data'], true);
            
            if (!is_array($field_groups)) {
                continue;
            }
            
            foreach ($field_groups as $field_group) {
                if (is_null($field_group) || !is_array($field_group)) {
                    continue;
                }
                
                // Update location rules to target specific page
                $field_group['location'] = [
                    [
                        [
                            'param' => 'page',
                            'operator' => '==',
                            'value' => $template['page_id']
                        ]
                    ]
                ];
                
                // Add unique prefix to avoid conflicts
                $field_group['key'] = 'kenzysites_page_' . $template['page_id'] . '_' . $field_group['key'];
                
                // Ensure fields have proper keys
                if (isset($field_group['fields'])) {
                    foreach ($field_group['fields'] as &$field) {
                        $field['key'] = 'kenzysites_page_' . $template['page_id'] . '_' . $field['key'];
                    }
                }
                
                // Register the field group
                acf_add_local_field_group($field_group);
            }
        }
    }
    
    /**
     * Load ACF template for converted pages
     */
    public function load_acf_template($template) {
        if (!is_page()) {
            return $template;
        }
        
        $page_id = get_the_ID();
        
        // Check if this page was converted from Elementor to ACF
        if (get_post_meta($page_id, '_kenzysites_acf_mode', true) === '1') {
            $acf_template = KENZYSITES_CONVERTER_PLUGIN_PATH . 'templates/page-kenzysites-acf.php';
            
            if (file_exists($acf_template)) {
                return $acf_template;
            }
        }
        
        return $template;
    }
    
    /**
     * Create database tables
     */
    private function create_tables() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE $table_name (
            id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            page_id bigint(20) unsigned NOT NULL,
            template_id varchar(255) NOT NULL,
            landing_page_type varchar(100) NOT NULL,
            acf_data longtext NOT NULL,
            elementor_data longtext NOT NULL,
            conversion_date datetime DEFAULT CURRENT_TIMESTAMP,
            sync_status varchar(50) DEFAULT 'pending',
            sync_date datetime NULL,
            PRIMARY KEY (id),
            KEY page_id (page_id),
            KEY template_id (template_id),
            KEY sync_status (sync_status)
        ) $charset_collate;";
        
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta($sql);
    }
    
    /**
     * Get plugin option
     */
    public static function get_option($key, $default = '') {
        return get_option('kenzysites_' . $key, $default);
    }
    
    /**
     * Update plugin option
     */
    public static function update_option($key, $value) {
        return update_option('kenzysites_' . $key, $value);
    }
    
    /**
     * Register REST API endpoints
     */
    public function register_rest_endpoints() {
        // Endpoint para receber templates do KenzySites
        register_rest_route('kenzysites/v1', '/templates/receive', [
            'methods' => 'POST',
            'callback' => [$this, 'rest_receive_template'],
            'permission_callback' => [$this, 'rest_permission_check'],
            'args' => [
                'template_data' => [
                    'required' => true,
                    'type' => 'object',
                    'description' => 'Dados do template Elementor'
                ],
                'business_info' => [
                    'required' => true,
                    'type' => 'object',
                    'description' => 'Informações do negócio'
                ],
                'page_title' => [
                    'required' => true,
                    'type' => 'string',
                    'description' => 'Título da página'
                ]
            ]
        ]);
        
        // Endpoint para verificar status de deployment
        register_rest_route('kenzysites/v1', '/templates/status/(?P<id>[a-zA-Z0-9\-]+)', [
            'methods' => 'GET',
            'callback' => [$this, 'rest_get_deployment_status'],
            'permission_callback' => [$this, 'rest_permission_check']
        ]);
    }
    
    /**
     * REST API permission check
     */
    public function rest_permission_check($request) {
        // Verificar API key no header
        $api_key = $request->get_header('X-API-Key');
        $configured_key = self::get_option('api_key', '');
        
        if (empty($configured_key)) {
            // Se não há API key configurada, permitir (modo de desenvolvimento)
            return true;
        }
        
        return $api_key === $configured_key;
    }
    
    /**
     * REST API endpoint: Receive template from KenzySites
     */
    public function rest_receive_template($request) {
        try {
            $template_data = $request->get_param('template_data');
            $business_info = $request->get_param('business_info');
            $page_title = $request->get_param('page_title');
            $page_slug = $request->get_param('page_slug');
            
            // Criar nova página WordPress
            $page_id = wp_insert_post([
                'post_title' => $page_title,
                'post_name' => $page_slug ?: sanitize_title($page_title),
                'post_type' => 'page',
                'post_status' => 'publish',
                'meta_input' => [
                    '_elementor_edit_mode' => 'builder',
                    '_elementor_template_type' => 'wp-page',
                    '_elementor_version' => ELEMENTOR_VERSION,
                    '_elementor_data' => json_encode($template_data['elementor_json']),
                    '_kenzysites_generated' => '1',
                    '_kenzysites_business_info' => json_encode($business_info)
                ]
            ]);
            
            if (is_wp_error($page_id)) {
                throw new Exception($page_id->get_error_message());
            }
            
            // Limpar cache do Elementor
            if (class_exists('\Elementor\Plugin')) {
                \Elementor\Plugin::$instance->files_manager->clear_cache();
            }
            
            return new WP_REST_Response([
                'success' => true,
                'page_id' => $page_id,
                'page_url' => get_permalink($page_id),
                'edit_url' => admin_url("post.php?post={$page_id}&action=elementor"),
                'message' => 'Template criado com sucesso!'
            ], 200);
            
        } catch (Exception $e) {
            return new WP_REST_Response([
                'success' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }
    
    /**
     * REST API endpoint: Get deployment status
     */
    public function rest_get_deployment_status($request) {
        $id = $request->get_param('id');
        
        // Buscar página pelo meta _kenzysites_landing_id
        $pages = get_posts([
            'post_type' => 'page',
            'meta_query' => [
                [
                    'key' => '_kenzysites_landing_id',
                    'value' => $id,
                    'compare' => '='
                ]
            ],
            'posts_per_page' => 1
        ]);
        
        if (empty($pages)) {
            return new WP_REST_Response([
                'success' => false,
                'error' => 'Landing page não encontrada'
            ], 404);
        }
        
        $page = $pages[0];
        
        return new WP_REST_Response([
            'success' => true,
            'status' => 'deployed',
            'page_id' => $page->ID,
            'page_url' => get_permalink($page->ID),
            'edit_url' => admin_url("post.php?post={$page->ID}&action=elementor"),
            'created_at' => $page->post_date
        ], 200);
    }
}

/**
 * Initialize plugin
 */
function kenzysites_converter() {
    return KenzySitesConverter::get_instance();
}

// Start the plugin
kenzysites_converter();

/**
 * Helper function to get converted templates
 */
function kenzysites_get_converted_templates() {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
    
    return $wpdb->get_results(
        "SELECT * FROM $table_name ORDER BY conversion_date DESC",
        ARRAY_A
    );
}

/**
 * Helper function to get template by ID
 */
function kenzysites_get_template_by_id($template_id) {
    global $wpdb;
    
    $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
    
    return $wpdb->get_row(
        $wpdb->prepare("SELECT * FROM $table_name WHERE template_id = %s", $template_id),
        ARRAY_A
    );
}