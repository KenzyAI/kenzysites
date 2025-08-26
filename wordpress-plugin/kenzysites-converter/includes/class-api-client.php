<?php
/**
 * API Client Class
 * Handles communication with KenzySites system
 */

if (!defined('ABSPATH')) {
    exit;
}

class KenzySites_API_Client {
    
    private $api_url;
    private $api_key;
    private $timeout;
    
    public function __construct() {
        $this->api_url = rtrim(KenzySitesConverter::get_option('api_url', 'http://localhost:8000/api'), '/');
        $this->api_key = KenzySitesConverter::get_option('api_key', '');
        $this->timeout = 30;
    }
    
    /**
     * Test API connection
     */
    public function test_connection() {
        $response = $this->make_request('GET', '/health', []);
        
        if (is_wp_error($response)) {
            throw new Exception($response->get_error_message());
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (wp_remote_retrieve_response_code($response) !== 200) {
            throw new Exception($data['message'] ?? __('Erro desconhecido na API', 'kenzysites-converter'));
        }
        
        return $data;
    }
    
    /**
     * Sync converted template to KenzySites
     */
    public function sync_template($template_id) {
        // Get template data from database
        global $wpdb;
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        $template = $wpdb->get_row(
            $wpdb->prepare("SELECT * FROM $table_name WHERE template_id = %s", $template_id),
            ARRAY_A
        );
        
        if (!$template) {
            throw new Exception(__('Template não encontrado', 'kenzysites-converter'));
        }
        
        // Get original page data
        $page = get_post($template['page_id']);
        if (!$page) {
            throw new Exception(__('Página original não encontrada', 'kenzysites-converter'));
        }
        
        // Prepare template data for API
        $template_data = $this->prepare_template_for_api($template, $page);
        
        // Send to KenzySites API
        $response = $this->make_request('POST', '/templates/elementor/convert', $template_data);
        
        if (is_wp_error($response)) {
            $this->update_sync_status($template_id, 'error', $response->get_error_message());
            throw new Exception($response->get_error_message());
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        $response_code = wp_remote_retrieve_response_code($response);
        
        if ($response_code >= 400) {
            $error_message = $data['detail'] ?? $data['message'] ?? __('Erro desconhecido', 'kenzysites-converter');
            $this->update_sync_status($template_id, 'error', $error_message);
            throw new Exception($error_message);
        }
        
        if (!$data['success']) {
            $error_message = $data['error'] ?? __('Falha na conversão', 'kenzysites-converter');
            $this->update_sync_status($template_id, 'error', $error_message);
            throw new Exception($error_message);
        }
        
        // Update sync status to success
        $this->update_sync_status($template_id, 'synced');
        
        return $data;
    }
    
    /**
     * Get available landing page types from API
     */
    public function get_landing_page_types() {
        $response = $this->make_request('GET', '/templates/landing-pages/types', []);
        
        if (is_wp_error($response)) {
            // Return default types if API is unavailable
            return $this->get_default_landing_page_types();
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (wp_remote_retrieve_response_code($response) !== 200 || !$data['success']) {
            return $this->get_default_landing_page_types();
        }
        
        return $data['landing_page_types'];
    }
    
    /**
     * Get template status from KenzySites
     */
    public function get_template_status($template_id) {
        $response = $this->make_request('GET', "/templates/landing-pages/{$template_id}", []);
        
        if (is_wp_error($response)) {
            return null;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (wp_remote_retrieve_response_code($response) !== 200) {
            return null;
        }
        
        return $data;
    }
    
    /**
     * Prepare template data for API submission
     */
    private function prepare_template_for_api($template, $page) {
        // Get additional page metadata
        $page_url = get_permalink($template['page_id']);
        $thumbnail = get_the_post_thumbnail_url($template['page_id'], 'large');
        
        // Parse ACF data
        $acf_data = json_decode($template['acf_data'], true);
        
        // Get Elementor settings
        $elementor_settings = get_post_meta($template['page_id'], '_elementor_page_settings', true);
        
        // Get site information
        $site_info = [
            'name' => get_bloginfo('name'),
            'url' => get_site_url(),
            'description' => get_bloginfo('description'),
            'admin_email' => get_option('admin_email'),
            'wp_version' => get_bloginfo('version'),
            'elementor_version' => defined('ELEMENTOR_VERSION') ? ELEMENTOR_VERSION : 'unknown'
        ];
        
        return [
            'page_data' => [
                'id' => $template['page_id'],
                'title' => $page->post_title,
                'slug' => $page->post_name,
                'url' => $page_url,
                'content' => $page->post_content,
                'excerpt' => $page->post_excerpt,
                'status' => $page->post_status,
                'date_created' => $page->post_date,
                'date_modified' => $page->post_modified,
                'thumbnail' => $thumbnail,
                'elementor_data' => $template['elementor_data'],
                'elementor_settings' => $elementor_settings,
                'meta_data' => get_post_meta($template['page_id'])
            ],
            'template_data' => [
                'template_id' => $template['template_id'],
                'landing_page_type' => $template['landing_page_type'],
                'conversion_date' => $template['conversion_date'],
                'acf_field_groups' => $acf_data
            ],
            'site_info' => $site_info,
            'landing_page_type' => $template['landing_page_type'],
            'preserve_elementor' => true,
            'source' => 'wordpress_plugin'
        ];
    }
    
    /**
     * Make HTTP request to API
     */
    private function make_request($method, $endpoint, $data = []) {
        $url = $this->api_url . $endpoint;
        
        $headers = [
            'Content-Type' => 'application/json',
            'Accept' => 'application/json',
            'User-Agent' => 'KenzySites-Converter/' . KENZYSITES_CONVERTER_VERSION
        ];
        
        // Add API key if configured
        if (!empty($this->api_key)) {
            $headers['Authorization'] = 'Bearer ' . $this->api_key;
            $headers['X-API-Key'] = $this->api_key;
        }
        
        $args = [
            'method' => strtoupper($method),
            'headers' => $headers,
            'timeout' => $this->timeout,
            'sslverify' => false, // Para desenvolvimento local
            'data_format' => 'body'
        ];
        
        if ($method !== 'GET' && !empty($data)) {
            $args['body'] = json_encode($data);
        }
        
        // Log request for debugging
        $this->log_api_request($method, $url, $data);
        
        $response = wp_remote_request($url, $args);
        
        // Log response for debugging  
        $this->log_api_response($response);
        
        return $response;
    }
    
    /**
     * Update template sync status in database
     */
    private function update_sync_status($template_id, $status, $error_message = '') {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        $update_data = [
            'sync_status' => $status,
            'sync_date' => current_time('mysql')
        ];
        
        if (!empty($error_message)) {
            $update_data['sync_error'] = $error_message;
        }
        
        $wpdb->update(
            $table_name,
            $update_data,
            ['template_id' => $template_id],
            ['%s', '%s', '%s'],
            ['%s']
        );
    }
    
    /**
     * Get default landing page types (fallback)
     */
    private function get_default_landing_page_types() {
        return [
            [
                'value' => 'lead_generation',
                'label' => 'Geração de Leads',
                'description' => 'Landing page otimizada para capturar leads'
            ],
            [
                'value' => 'service_showcase',
                'label' => 'Showcase de Serviços',
                'description' => 'Apresenta serviços e gera leads'
            ],
            [
                'value' => 'product_launch',
                'label' => 'Lançamento de Produto',
                'description' => 'Para lançar novos produtos'
            ],
            [
                'value' => 'event_promotion',
                'label' => 'Promoção de Evento',
                'description' => 'Promove eventos e inscrições'
            ],
            [
                'value' => 'webinar',
                'label' => 'Webinar',
                'description' => 'Inscrições para webinars'
            ],
            [
                'value' => 'coming_soon',
                'label' => 'Em Breve',
                'description' => 'Página de lançamento em breve'
            ],
            [
                'value' => 'thank_you',
                'label' => 'Obrigado',
                'description' => 'Página de agradecimento'
            ],
            [
                'value' => 'download',
                'label' => 'Download',
                'description' => 'Para downloads de materiais'
            ]
        ];
    }
    
    /**
     * Sync all pending templates
     */
    public function sync_all_pending() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        $pending_templates = $wpdb->get_results(
            "SELECT template_id FROM $table_name WHERE sync_status = 'pending'",
            ARRAY_A
        );
        
        $results = [
            'success' => 0,
            'errors' => 0,
            'details' => []
        ];
        
        foreach ($pending_templates as $template) {
            try {
                $this->sync_template($template['template_id']);
                $results['success']++;
                $results['details'][] = [
                    'template_id' => $template['template_id'],
                    'status' => 'success'
                ];
            } catch (Exception $e) {
                $results['errors']++;
                $results['details'][] = [
                    'template_id' => $template['template_id'],
                    'status' => 'error',
                    'message' => $e->getMessage()
                ];
            }
        }
        
        return $results;
    }
    
    /**
     * Get sync statistics
     */
    public function get_sync_stats() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        return [
            'total' => $wpdb->get_var("SELECT COUNT(*) FROM $table_name"),
            'synced' => $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'synced'"),
            'pending' => $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'pending'"),
            'errors' => $wpdb->get_var("SELECT COUNT(*) FROM $table_name WHERE sync_status = 'error'"),
            'last_sync' => $wpdb->get_var("SELECT MAX(sync_date) FROM $table_name WHERE sync_status = 'synced'")
        ];
    }
    
    /**
     * Log API request for debugging
     */
    private function log_api_request($method, $url, $data) {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            error_log("KenzySites API Request: {$method} {$url}");
            if (!empty($data)) {
                error_log("Request Data: " . json_encode($data));
            }
        }
    }
    
    /**
     * Log API response for debugging
     */
    private function log_api_response($response) {
        if (defined('WP_DEBUG') && WP_DEBUG) {
            if (is_wp_error($response)) {
                error_log("KenzySites API Error: " . $response->get_error_message());
            } else {
                $code = wp_remote_retrieve_response_code($response);
                $body = wp_remote_retrieve_body($response);
                error_log("KenzySites API Response: {$code}");
                error_log("Response Body: " . substr($body, 0, 500) . "...");
            }
        }
    }
    
    /**
     * Clear error logs
     */
    public function clear_error_logs() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        return $wpdb->query(
            "UPDATE $table_name SET sync_error = NULL WHERE sync_error IS NOT NULL"
        );
    }
    
    /**
     * Validate API credentials
     */
    public function validate_credentials() {
        if (empty($this->api_url)) {
            return [
                'valid' => false,
                'message' => __('URL da API não configurada', 'kenzysites-converter')
            ];
        }
        
        if (empty($this->api_key)) {
            return [
                'valid' => false,
                'message' => __('API Key não configurada', 'kenzysites-converter')
            ];
        }
        
        try {
            $this->test_connection();
            return [
                'valid' => true,
                'message' => __('Credenciais válidas', 'kenzysites-converter')
            ];
        } catch (Exception $e) {
            return [
                'valid' => false,
                'message' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Get API health status
     */
    public function get_health_status() {
        try {
            $response = $this->make_request('GET', '/health', []);
            
            if (is_wp_error($response)) {
                return [
                    'status' => 'error',
                    'message' => $response->get_error_message(),
                    'timestamp' => current_time('mysql')
                ];
            }
            
            $code = wp_remote_retrieve_response_code($response);
            $body = json_decode(wp_remote_retrieve_body($response), true);
            
            return [
                'status' => $code === 200 ? 'healthy' : 'unhealthy',
                'response_code' => $code,
                'message' => $body['message'] ?? 'API Response received',
                'timestamp' => current_time('mysql')
            ];
            
        } catch (Exception $e) {
            return [
                'status' => 'error',
                'message' => $e->getMessage(),
                'timestamp' => current_time('mysql')
            ];
        }
    }
}