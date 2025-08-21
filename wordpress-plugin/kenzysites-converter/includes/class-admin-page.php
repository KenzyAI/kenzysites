<?php
/**
 * Admin Page Handler Class
 * Manages admin interface functionality
 */

if (!defined('ABSPATH')) {
    exit;
}

class KenzySites_Admin_Page {
    
    private $elementor_scanner;
    private $acf_converter;
    private $api_client;
    
    public function __construct() {
        $this->elementor_scanner = new KenzySites_Elementor_Scanner();
        $this->acf_converter = new KenzySites_ACF_Converter();
        $this->api_client = new KenzySites_API_Client();
        
        // Add additional AJAX actions
        add_action('wp_ajax_kenzysites_sync_all_pending', [$this, 'ajax_sync_all_pending']);
        add_action('wp_ajax_kenzysites_get_template_details', [$this, 'ajax_get_template_details']);
        add_action('wp_ajax_kenzysites_delete_template', [$this, 'ajax_delete_template']);
    }
    
    /**
     * AJAX: Sync all pending templates
     */
    public function ajax_sync_all_pending() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        try {
            $result = $this->api_client->sync_all_pending();
            wp_send_json_success($result);
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * AJAX: Get template details
     */
    public function ajax_get_template_details() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        $template_id = sanitize_text_field($_POST['template_id']);
        
        try {
            $template = $this->acf_converter->get_converted_template($template_id);
            
            if (!$template) {
                wp_send_json_error(__('Template não encontrado', 'kenzysites-converter'));
                return;
            }
            
            // Get additional data
            $page = get_post($template['page_id']);
            $acf_data = json_decode($template['acf_data'], true);
            
            $details = [
                'template' => $template,
                'page' => $page ? [
                    'title' => $page->post_title,
                    'url' => get_permalink($page->ID),
                    'edit_url' => get_edit_post_link($page->ID),
                    'elementor_edit_url' => admin_url("post.php?post={$page->ID}&action=elementor")
                ] : null,
                'acf_groups' => $acf_data,
                'field_count' => is_array($acf_data) ? count($acf_data) : 0,
                'elementor_data_size' => strlen($template['elementor_data']),
                'api_status' => $this->api_client->get_template_status($template_id)
            ];
            
            wp_send_json_success($details);
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * AJAX: Delete template
     */
    public function ajax_delete_template() {
        check_ajax_referer('kenzysites_nonce', 'nonce');
        
        if (!current_user_can('manage_options')) {
            wp_die(__('Acesso negado', 'kenzysites-converter'));
        }
        
        $template_id = sanitize_text_field($_POST['template_id']);
        
        try {
            global $wpdb;
            
            $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
            
            $deleted = $wpdb->delete(
                $table_name,
                ['template_id' => $template_id],
                ['%s']
            );
            
            if ($deleted === false) {
                throw new Exception(__('Erro ao deletar template do banco de dados', 'kenzysites-converter'));
            }
            
            wp_send_json_success([
                'message' => __('Template deletado com sucesso', 'kenzysites-converter'),
                'deleted_count' => $deleted
            ]);
            
        } catch (Exception $e) {
            wp_send_json_error($e->getMessage());
        }
    }
    
    /**
     * Get dashboard statistics
     */
    public function get_dashboard_stats() {
        global $wpdb;
        
        // Basic page counts
        $total_pages = wp_count_posts('page')->publish;
        
        // Elementor pages count
        $elementor_query = new WP_Query([
            'post_type' => 'page',
            'meta_query' => [
                [
                    'key' => '_elementor_edit_mode',
                    'value' => 'builder',
                    'compare' => '='
                ]
            ],
            'posts_per_page' => -1,
            'fields' => 'ids'
        ]);
        $elementor_pages = $elementor_query->found_posts;
        
        // Converted templates stats
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        $converted_templates = 0;
        $synced_templates = 0;
        $pending_templates = 0;
        $error_templates = 0;
        
        if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") == $table_name) {
            $converted_templates = $wpdb->get_var("SELECT COUNT(*) FROM $table_name");
            $synced_templates = $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'synced'");
            $pending_templates = $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'pending'");
            $error_templates = $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'error'");
        }
        
        return [
            'total_pages' => $total_pages,
            'elementor_pages' => $elementor_pages,
            'converted_templates' => $converted_templates,
            'synced_templates' => $synced_templates,
            'pending_templates' => $pending_templates,
            'error_templates' => $error_templates,
            'conversion_rate' => $elementor_pages > 0 ? round(($converted_templates / $elementor_pages) * 100, 1) : 0,
            'sync_rate' => $converted_templates > 0 ? round(($synced_templates / $converted_templates) * 100, 1) : 0
        ];
    }
    
    /**
     * Get recent conversions for dashboard
     */
    public function get_recent_conversions($limit = 5) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") != $table_name) {
            return [];
        }
        
        $results = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM $table_name ORDER BY conversion_date DESC LIMIT %d",
                $limit
            ),
            ARRAY_A
        );
        
        // Enrich with page data
        foreach ($results as &$result) {
            $page = get_post($result['page_id']);
            $result['page_title'] = $page ? $page->post_title : __('Página removida', 'kenzysites-converter');
            $result['page_url'] = $page ? get_permalink($result['page_id']) : null;
            $result['page_edit_url'] = $page ? get_edit_post_link($result['page_id']) : null;
        }
        
        return $results;
    }
    
    /**
     * Get conversion analytics
     */
    public function get_conversion_analytics($days = 30) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") != $table_name) {
            return [
                'daily_conversions' => [],
                'type_distribution' => [],
                'sync_status_distribution' => []
            ];
        }
        
        $date_limit = date('Y-m-d H:i:s', strtotime("-$days days"));
        
        // Daily conversions
        $daily_conversions = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT DATE(conversion_date) as date, COUNT(*) as count 
                 FROM $table_name 
                 WHERE conversion_date >= %s 
                 GROUP BY DATE(conversion_date) 
                 ORDER BY date ASC",
                $date_limit
            ),
            ARRAY_A
        );
        
        // Type distribution
        $type_distribution = $wpdb->get_results(
            "SELECT landing_page_type as type, COUNT(*) as count 
             FROM $table_name 
             GROUP BY landing_page_type 
             ORDER BY count DESC",
            ARRAY_A
        );
        
        // Sync status distribution
        $sync_status_distribution = $wpdb->get_results(
            "SELECT sync_status as status, COUNT(*) as count 
             FROM $table_name 
             GROUP BY sync_status",
            ARRAY_A
        );
        
        return [
            'daily_conversions' => $daily_conversions,
            'type_distribution' => $type_distribution,
            'sync_status_distribution' => $sync_status_distribution
        ];
    }
    
    /**
     * Export templates data
     */
    public function export_templates_data($format = 'json') {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") != $table_name) {
            return null;
        }
        
        $templates = $wpdb->get_results("SELECT * FROM $table_name ORDER BY conversion_date DESC", ARRAY_A);
        
        // Enrich with page data
        foreach ($templates as &$template) {
            $page = get_post($template['page_id']);
            $template['page_title'] = $page ? $page->post_title : 'Página removida';
            $template['page_url'] = $page ? get_permalink($template['page_id']) : null;
            
            // Remove large data for export
            unset($template['elementor_data']);
            unset($template['acf_data']);
        }
        
        switch ($format) {
            case 'csv':
                return $this->array_to_csv($templates);
            case 'xml':
                return $this->array_to_xml($templates);
            default:
                return json_encode($templates, JSON_PRETTY_PRINT);
        }
    }
    
    /**
     * Convert array to CSV
     */
    private function array_to_csv($array) {
        if (empty($array)) {
            return '';
        }
        
        $output = fopen('php://temp', 'r+');
        
        // Write header
        fputcsv($output, array_keys($array[0]));
        
        // Write data
        foreach ($array as $row) {
            fputcsv($output, $row);
        }
        
        rewind($output);
        $csv = stream_get_contents($output);
        fclose($output);
        
        return $csv;
    }
    
    /**
     * Convert array to XML
     */
    private function array_to_xml($array, $root = 'templates') {
        $xml = new SimpleXMLElement("<$root/>");
        
        foreach ($array as $item) {
            $template_node = $xml->addChild('template');
            foreach ($item as $key => $value) {
                $template_node->addChild($key, htmlspecialchars($value));
            }
        }
        
        return $xml->asXML();
    }
    
    /**
     * Clean up old data
     */
    public function cleanup_old_data($days_old = 90) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        if ($wpdb->get_var("SHOW TABLES LIKE '$table_name'") != $table_name) {
            return 0;
        }
        
        $date_limit = date('Y-m-d H:i:s', strtotime("-$days_old days"));
        
        // Only clean up successfully synced templates
        $deleted = $wpdb->query(
            $wpdb->prepare(
                "DELETE FROM $table_name 
                 WHERE conversion_date < %s 
                 AND sync_status = 'synced'",
                $date_limit
            )
        );
        
        return $deleted;
    }
    
    /**
     * Get system health check
     */
    public function get_system_health() {
        $health = [
            'status' => 'healthy',
            'checks' => []
        ];
        
        // Check WordPress version
        $wp_version = get_bloginfo('version');
        $health['checks']['wordpress'] = [
            'name' => 'WordPress Version',
            'status' => version_compare($wp_version, '5.0', '>=') ? 'pass' : 'warning',
            'message' => "WordPress {$wp_version}",
            'recommendation' => version_compare($wp_version, '5.0', '<') ? 'Update WordPress to version 5.0 or higher' : null
        ];
        
        // Check Elementor
        $elementor_active = is_plugin_active('elementor/elementor.php');
        $health['checks']['elementor'] = [
            'name' => 'Elementor Plugin',
            'status' => $elementor_active ? 'pass' : 'critical',
            'message' => $elementor_active ? 'Active' : 'Not installed or inactive',
            'recommendation' => !$elementor_active ? 'Install and activate Elementor plugin' : null
        ];
        
        // Check PHP version
        $php_version = PHP_VERSION;
        $health['checks']['php'] = [
            'name' => 'PHP Version',
            'status' => version_compare($php_version, '7.4', '>=') ? 'pass' : 'warning',
            'message' => "PHP {$php_version}",
            'recommendation' => version_compare($php_version, '7.4', '<') ? 'Upgrade PHP to version 7.4 or higher' : null
        ];
        
        // Check database
        global $wpdb;
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        $table_exists = $wpdb->get_var("SHOW TABLES LIKE '$table_name'") == $table_name;
        
        $health['checks']['database'] = [
            'name' => 'Database Table',
            'status' => $table_exists ? 'pass' : 'critical',
            'message' => $table_exists ? 'Table exists' : 'Table missing',
            'recommendation' => !$table_exists ? 'Deactivate and reactivate the plugin to create table' : null
        ];
        
        // Check API connection
        try {
            $this->api_client->test_connection();
            $health['checks']['api'] = [
                'name' => 'API Connection',
                'status' => 'pass',
                'message' => 'Connected',
                'recommendation' => null
            ];
        } catch (Exception $e) {
            $health['checks']['api'] = [
                'name' => 'API Connection',
                'status' => 'warning',
                'message' => 'Connection failed',
                'recommendation' => 'Check API settings in plugin configuration'
            ];
        }
        
        // Determine overall health
        $critical_count = 0;
        $warning_count = 0;
        
        foreach ($health['checks'] as $check) {
            if ($check['status'] === 'critical') {
                $critical_count++;
            } elseif ($check['status'] === 'warning') {
                $warning_count++;
            }
        }
        
        if ($critical_count > 0) {
            $health['status'] = 'critical';
        } elseif ($warning_count > 0) {
            $health['status'] = 'warning';
        }
        
        return $health;
    }
    
    /**
     * Log admin action
     */
    public function log_admin_action($action, $details = []) {
        $log_entry = [
            'timestamp' => current_time('mysql'),
            'user_id' => get_current_user_id(),
            'user_login' => wp_get_current_user()->user_login,
            'action' => $action,
            'details' => $details,
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
        ];
        
        // Store in transient for now (could be moved to database table)
        $logs = get_transient('kenzysites_admin_logs') ?: [];
        $logs[] = $log_entry;
        
        // Keep only last 100 entries
        $logs = array_slice($logs, -100);
        
        set_transient('kenzysites_admin_logs', $logs, DAY_IN_SECONDS);
        
        return $log_entry;
    }
    
    /**
     * Get admin logs
     */
    public function get_admin_logs($limit = 50) {
        $logs = get_transient('kenzysites_admin_logs') ?: [];
        return array_slice(array_reverse($logs), 0, $limit);
    }
}