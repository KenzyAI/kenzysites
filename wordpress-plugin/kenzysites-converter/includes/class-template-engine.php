<?php
/**
 * Template Engine Class
 * Manages template variables and dynamic content replacement for KenzySites
 */

if (!defined('ABSPATH')) {
    exit;
}

class KenzySites_Template_Engine {
    
    /**
     * Template variables patterns
     */
    private $variable_pattern = '/\{\{([A-Z_]+)\}\}/';
    
    /**
     * Default variables for different template types
     */
    private $default_variables = [
        'medico' => [
            'NOME_MEDICO' => 'Dr. João Silva',
            'ESPECIALIDADE' => 'Clínico Geral',
            'CRM' => '12345',
            'TELEFONE' => '(11) 99999-9999',
            'EMAIL' => 'contato@clinica.com.br',
            'ENDERECO' => 'Rua das Flores, 123 - Centro',
            'CIDADE' => 'São Paulo',
            'ESTADO' => 'SP',
            'CEP' => '01234-567',
            'FOTO_MEDICO' => '',
            'SOBRE_MEDICO' => 'Médico especialista com mais de 10 anos de experiência.',
            'FORMACAO' => 'Universidade de São Paulo',
            'CONSULTORIO' => 'Clínica Médica São Paulo',
            'PRECO_CONSULTA' => 'R$ 200,00',
            'TEMPO_CONSULTA' => '30 minutos',
            'CONVENIOS' => 'Unimed, Bradesco Saúde, SulAmérica',
        ],
        'restaurante' => [
            'NOME_RESTAURANTE' => 'Restaurante Bella Vista',
            'TIPO_COZINHA' => 'Italiana',
            'TELEFONE' => '(11) 99999-9999',
            'EMAIL' => 'contato@bellavista.com.br',
            'ENDERECO' => 'Rua Gastronômica, 456 - Centro',
            'CIDADE' => 'São Paulo',
            'HORARIO_FUNCIONAMENTO' => 'Seg a Dom: 12h às 23h',
            'ENTREGA' => 'Delivery e Balcão',
            'CHEF' => 'Chef Mario Rossi',
            'ESPECIALIDADE' => 'Massas artesanais e vinhos selecionados',
            'PRECO_MEDIO' => 'R$ 45,00 por pessoa',
            'AVALIACAO' => '4.8 estrelas',
            'CAPACIDADE' => '80 pessoas',
        ],
        'academia' => [
            'NOME_ACADEMIA' => 'PowerFit Academia',
            'MODALIDADES' => 'Musculação, Funcional, Spinning, Natação',
            'TELEFONE' => '(11) 99999-9999',
            'EMAIL' => 'contato@powerfit.com.br',
            'ENDERECO' => 'Av. Fitness, 789 - Centro',
            'HORARIO_FUNCIONAMENTO' => 'Seg a Sex: 5h às 24h | Sáb: 7h às 20h',
            'PERSONAL_TRAINER' => 'Personal trainers certificados',
            'PLANOS' => 'Mensal: R$ 89 | Trimestral: R$ 240 | Anual: R$ 890',
            'AREA_TOTAL' => '1.200m²',
            'EQUIPAMENTOS' => 'Mais de 100 equipamentos modernos',
        ]
    ];
    
    /**
     * Initialize template engine
     */
    public function __construct() {
        add_action('init', [$this, 'init_hooks']);
    }
    
    /**
     * Initialize WordPress hooks
     */
    public function init_hooks() {
        // REST API endpoints for template management
        add_action('rest_api_init', [$this, 'register_api_endpoints']);
        
        // Template rendering filter
        add_filter('the_content', [$this, 'process_template_variables'], 999);
        
        // Admin hooks
        add_action('add_meta_boxes', [$this, 'add_template_variables_metabox']);
        add_action('save_post', [$this, 'save_template_variables']);
    }
    
    /**
     * Register REST API endpoints for agents
     */
    public function register_api_endpoints() {
        // Update template variables
        register_rest_route('kenzysites/v1', '/templates/(?P<id>\d+)/update', [
            'methods' => 'POST',
            'callback' => [$this, 'update_template_variables'],
            'permission_callback' => [$this, 'check_api_permissions'],
            'args' => [
                'id' => [
                    'validate_callback' => function($param) {
                        return is_numeric($param);
                    }
                ],
                'variables' => [
                    'required' => true,
                    'validate_callback' => function($param) {
                        return is_array($param);
                    }
                ]
            ]
        ]);
        
        // Get template variables
        register_rest_route('kenzysites/v1', '/templates/(?P<id>\d+)/variables', [
            'methods' => 'GET',
            'callback' => [$this, 'get_template_variables'],
            'permission_callback' => [$this, 'check_api_permissions'],
        ]);
        
        // Preview template with variables
        register_rest_route('kenzysites/v1', '/templates/(?P<id>\d+)/preview', [
            'methods' => 'POST',
            'callback' => [$this, 'preview_template'],
            'permission_callback' => [$this, 'check_api_permissions'],
        ]);
        
        // Get available template types and their default variables
        register_rest_route('kenzysites/v1', '/templates/types', [
            'methods' => 'GET',
            'callback' => [$this, 'get_template_types'],
            'permission_callback' => [$this, 'check_api_permissions'],
        ]);
        
        // Upload image and replace in template
        register_rest_route('kenzysites/v1', '/templates/(?P<id>\d+)/upload-image', [
            'methods' => 'POST',
            'callback' => [$this, 'upload_and_replace_image'],
            'permission_callback' => [$this, 'check_api_permissions'],
        ]);
        
        // Get all images used in template
        register_rest_route('kenzysites/v1', '/templates/(?P<id>\d+)/images', [
            'methods' => 'GET',
            'callback' => [$this, 'get_template_images'],
            'permission_callback' => [$this, 'check_api_permissions'],
        ]);
    }
    
    /**
     * Check API permissions
     */
    public function check_api_permissions($request) {
        // Check for API key in header
        $api_key = $request->get_header('X-KenzySites-API-Key');
        
        if (!$api_key) {
            return new WP_Error('missing_api_key', 'API key is required', ['status' => 401]);
        }
        
        // Validate API key
        $stored_api_key = get_option('kenzysites_api_key', '');
        if ($api_key !== $stored_api_key) {
            return new WP_Error('invalid_api_key', 'Invalid API key', ['status' => 401]);
        }
        
        return true;
    }
    
    /**
     * Update template variables via API
     */
    public function update_template_variables($request) {
        $page_id = $request['id'];
        $variables = $request['variables'];
        
        // Validate page exists
        $page = get_post($page_id);
        if (!$page || $page->post_type !== 'page') {
            return new WP_Error('page_not_found', 'Page not found', ['status' => 404]);
        }
        
        // Save variables to post meta
        $current_variables = get_post_meta($page_id, '_kenzysites_template_variables', true) ?: [];
        $updated_variables = array_merge($current_variables, $variables);
        
        update_post_meta($page_id, '_kenzysites_template_variables', $updated_variables);
        
        // Log the update
        $this->log_template_update($page_id, $variables);
        
        return rest_ensure_response([
            'success' => true,
            'message' => 'Template variables updated successfully',
            'page_id' => $page_id,
            'updated_variables' => $variables,
            'total_variables' => count($updated_variables)
        ]);
    }
    
    /**
     * Get template variables via API
     */
    public function get_template_variables($request) {
        $page_id = $request['id'];
        
        $page = get_post($page_id);
        if (!$page || $page->post_type !== 'page') {
            return new WP_Error('page_not_found', 'Page not found', ['status' => 404]);
        }
        
        $variables = get_post_meta($page_id, '_kenzysites_template_variables', true) ?: [];
        $template_type = get_post_meta($page_id, '_kenzysites_template_type', true) ?: 'medico';
        
        // Get available variables from content
        $content = $page->post_content;
        $available_variables = $this->extract_variables_from_content($content);
        
        return rest_ensure_response([
            'page_id' => $page_id,
            'template_type' => $template_type,
            'current_variables' => $variables,
            'available_variables' => $available_variables,
            'default_variables' => $this->default_variables[$template_type] ?? []
        ]);
    }
    
    /**
     * Preview template with variables
     */
    public function preview_template($request) {
        $page_id = $request['id'];
        $variables = $request->get_param('variables') ?: [];
        
        $page = get_post($page_id);
        if (!$page || $page->post_type !== 'page') {
            return new WP_Error('page_not_found', 'Page not found', ['status' => 404]);
        }
        
        // Get current content
        $content = $page->post_content;
        
        // Merge with existing variables
        $current_variables = get_post_meta($page_id, '_kenzysites_template_variables', true) ?: [];
        $all_variables = array_merge($current_variables, $variables);
        
        // Process variables in content
        $processed_content = $this->replace_variables($content, $all_variables);
        
        return rest_ensure_response([
            'page_id' => $page_id,
            'preview_content' => $processed_content,
            'variables_used' => $all_variables
        ]);
    }
    
    /**
     * Get available template types
     */
    public function get_template_types($request) {
        return rest_ensure_response([
            'template_types' => array_keys($this->default_variables),
            'default_variables' => $this->default_variables
        ]);
    }
    
    /**
     * Process template variables in content
     */
    public function process_template_variables($content) {
        global $post;
        
        if (!$post || !is_singular('page')) {
            return $content;
        }
        
        // Check if this page uses template variables
        $variables = get_post_meta($post->ID, '_kenzysites_template_variables', true);
        if (!$variables || !is_array($variables)) {
            return $content;
        }
        
        return $this->replace_variables($content, $variables);
    }
    
    /**
     * Replace variables in content
     */
    public function replace_variables($content, $variables) {
        return preg_replace_callback($this->variable_pattern, function($matches) use ($variables) {
            $variable_name = $matches[1];
            return isset($variables[$variable_name]) ? $variables[$variable_name] : $matches[0];
        }, $content);
    }
    
    /**
     * Extract variables from content
     */
    public function extract_variables_from_content($content) {
        preg_match_all($this->variable_pattern, $content, $matches);
        return array_unique($matches[1]);
    }
    
    /**
     * Convert existing content to template with variables
     */
    public function convert_to_template($content, $template_type = 'medico') {
        $defaults = $this->default_variables[$template_type] ?? $this->default_variables['medico'];
        
        foreach ($defaults as $variable => $default_value) {
            // Simple replacement for common patterns
            $patterns = $this->get_replacement_patterns($variable, $default_value);
            
            foreach ($patterns as $pattern) {
                if (stripos($content, $pattern) !== false) {
                    $content = str_ireplace($pattern, '{{' . $variable . '}}', $content);
                }
            }
        }
        
        return $content;
    }
    
    /**
     * Get replacement patterns for variables
     */
    private function get_replacement_patterns($variable, $default_value) {
        $patterns = [$default_value];
        
        // Add specific patterns based on variable type
        switch ($variable) {
            case 'NOME_MEDICO':
                $patterns[] = 'Dr. ';
                $patterns[] = 'Dra. ';
                break;
            case 'TELEFONE':
                $patterns[] = '(11) ';
                $patterns[] = 'Telefone: ';
                break;
            case 'EMAIL':
                $patterns[] = '@';
                break;
        }
        
        return $patterns;
    }
    
    /**
     * Add template variables metabox
     */
    public function add_template_variables_metabox() {
        add_meta_box(
            'kenzysites_template_variables',
            'Template Variables - KenzySites',
            [$this, 'template_variables_metabox_callback'],
            'page',
            'normal',
            'high'
        );
    }
    
    /**
     * Template variables metabox callback
     */
    public function template_variables_metabox_callback($post) {
        wp_nonce_field('kenzysites_template_variables_nonce', 'kenzysites_template_variables_nonce');
        
        $variables = get_post_meta($post->ID, '_kenzysites_template_variables', true) ?: [];
        $template_type = get_post_meta($post->ID, '_kenzysites_template_type', true) ?: 'medico';
        $available_variables = $this->extract_variables_from_content($post->post_content);
        
        ?>
        <div class="kenzysites-template-variables">
            <h4>Tipo de Template</h4>
            <select name="kenzysites_template_type" id="kenzysites_template_type">
                <?php foreach ($this->default_variables as $type => $defaults): ?>
                    <option value="<?php echo esc_attr($type); ?>" <?php selected($template_type, $type); ?>>
                        <?php echo esc_html(ucfirst($type)); ?>
                    </option>
                <?php endforeach; ?>
            </select>
            
            <h4>Variáveis Disponíveis no Conteúdo</h4>
            <?php if ($available_variables): ?>
                <p><strong>Variáveis encontradas:</strong> {{<?php echo implode('}}, {{', $available_variables); ?>}}</p>
            <?php else: ?>
                <p><em>Nenhuma variável encontrada no conteúdo. Use {{NOME_VARIAVEL}} para criar variáveis.</em></p>
            <?php endif; ?>
            
            <h4>Valores das Variáveis</h4>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th>Variável</th>
                        <th>Valor Atual</th>
                        <th>Valor Padrão</th>
                    </tr>
                </thead>
                <tbody>
                    <?php 
                    $defaults = $this->default_variables[$template_type] ?? [];
                    $all_vars = array_unique(array_merge($available_variables, array_keys($defaults)));
                    
                    foreach ($all_vars as $var_name): 
                        $current_value = $variables[$var_name] ?? '';
                        $default_value = $defaults[$var_name] ?? '';
                    ?>
                    <tr>
                        <td><strong>{{<?php echo esc_html($var_name); ?>}}</strong></td>
                        <td>
                            <input type="text" 
                                   name="kenzysites_variables[<?php echo esc_attr($var_name); ?>]" 
                                   value="<?php echo esc_attr($current_value); ?>" 
                                   class="regular-text" 
                                   placeholder="<?php echo esc_attr($default_value); ?>">
                        </td>
                        <td><?php echo esc_html($default_value); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            
            <h4>Instruções para Agentes</h4>
            <div class="notice notice-info">
                <p><strong>Endpoint da API:</strong> <code>POST /wp-json/kenzysites/v1/templates/<?php echo $post->ID; ?>/update</code></p>
                <p><strong>Header necessário:</strong> <code>X-KenzySites-API-Key: sua_api_key</code></p>
                <p><strong>Exemplo de payload:</strong></p>
                <pre>{
  "variables": {
    "NOME_MEDICO": "Dr. João Silva",
    "ESPECIALIDADE": "Cardiologia",
    "TELEFONE": "(11) 99999-9999"
  }
}</pre>
            </div>
        </div>
        
        <style>
        .kenzysites-template-variables h4 {
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .kenzysites-template-variables pre {
            background: #f1f1f1;
            padding: 10px;
            border-left: 4px solid #0073aa;
            overflow-x: auto;
        }
        </style>
        <?php
    }
    
    /**
     * Save template variables
     */
    public function save_template_variables($post_id) {
        if (!isset($_POST['kenzysites_template_variables_nonce']) || 
            !wp_verify_nonce($_POST['kenzysites_template_variables_nonce'], 'kenzysites_template_variables_nonce')) {
            return;
        }
        
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }
        
        if (!current_user_can('edit_page', $post_id)) {
            return;
        }
        
        // Save template type
        if (isset($_POST['kenzysites_template_type'])) {
            update_post_meta($post_id, '_kenzysites_template_type', sanitize_text_field($_POST['kenzysites_template_type']));
        }
        
        // Save variables
        if (isset($_POST['kenzysites_variables']) && is_array($_POST['kenzysites_variables'])) {
            $variables = [];
            foreach ($_POST['kenzysites_variables'] as $key => $value) {
                $variables[sanitize_text_field($key)] = sanitize_text_field($value);
            }
            update_post_meta($post_id, '_kenzysites_template_variables', $variables);
        }
    }
    
    /**
     * Log template update
     */
    private function log_template_update($page_id, $variables) {
        $log_entry = [
            'timestamp' => current_time('mysql'),
            'page_id' => $page_id,
            'variables' => $variables,
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown',
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? 'Unknown'
        ];
        
        $logs = get_option('kenzysites_template_update_logs', []);
        $logs[] = $log_entry;
        
        // Keep only last 100 logs
        if (count($logs) > 100) {
            $logs = array_slice($logs, -100);
        }
        
        update_option('kenzysites_template_update_logs', $logs);
    }
    
    /**
     * Get update logs
     */
    public function get_update_logs($page_id = null) {
        $logs = get_option('kenzysites_template_update_logs', []);
        
        if ($page_id) {
            $logs = array_filter($logs, function($log) use ($page_id) {
                return $log['page_id'] == $page_id;
            });
        }
        
        return array_reverse($logs); // Most recent first
    }
    
    /**
     * Upload and replace image in template
     */
    public function upload_and_replace_image($request) {
        $page_id = $request['id'];
        
        // Check if page exists
        $page = get_post($page_id);
        if (!$page || $page->post_type !== 'page') {
            return new WP_Error('page_not_found', 'Page not found', ['status' => 404]);
        }
        
        // Handle file upload
        if (!isset($_FILES['image']) || $_FILES['image']['error'] !== UPLOAD_ERR_OK) {
            return new WP_Error('upload_error', 'Image upload failed', ['status' => 400]);
        }
        
        // Get image variable name (which image to replace)
        $image_variable = $request->get_param('variable');
        if (!$image_variable) {
            return new WP_Error('missing_variable', 'Image variable name is required', ['status' => 400]);
        }
        
        // Upload the image
        require_once ABSPATH . 'wp-admin/includes/image.php';
        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/media.php';
        
        $file = $_FILES['image'];
        
        // Validate image type
        $allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        if (!in_array($file['type'], $allowed_types)) {
            return new WP_Error('invalid_type', 'Invalid image type. Allowed: JPEG, PNG, GIF, WebP', ['status' => 400]);
        }
        
        // Upload the file
        $upload_overrides = [
            'test_form' => false,
            'unique_filename_callback' => function($dir, $name, $ext) use ($page_id, $image_variable) {
                return "kenzysites_{$page_id}_{$image_variable}_{$name}";
            }
        ];
        
        $uploaded_file = wp_handle_upload($file, $upload_overrides);
        
        if (isset($uploaded_file['error'])) {
            return new WP_Error('upload_failed', $uploaded_file['error'], ['status' => 500]);
        }
        
        // Create attachment
        $attachment = [
            'post_mime_type' => $uploaded_file['type'],
            'post_title' => sanitize_file_name($file['name']),
            'post_content' => '',
            'post_status' => 'inherit'
        ];
        
        $attachment_id = wp_insert_attachment($attachment, $uploaded_file['file'], $page_id);
        
        if (is_wp_error($attachment_id)) {
            return new WP_Error('attachment_failed', 'Failed to create attachment', ['status' => 500]);
        }
        
        // Generate attachment metadata
        $attachment_data = wp_generate_attachment_metadata($attachment_id, $uploaded_file['file']);
        wp_update_attachment_metadata($attachment_id, $attachment_data);
        
        // Update template variables with new image URL
        $variables = get_post_meta($page_id, '_kenzysites_template_variables', true) ?: [];
        $variables[$image_variable] = $uploaded_file['url'];
        update_post_meta($page_id, '_kenzysites_template_variables', $variables);
        
        // Log the upload
        $this->log_image_upload($page_id, $image_variable, $attachment_id, $uploaded_file['url']);
        
        return rest_ensure_response([
            'success' => true,
            'message' => 'Image uploaded and template updated successfully',
            'attachment_id' => $attachment_id,
            'image_url' => $uploaded_file['url'],
            'variable' => $image_variable,
            'page_id' => $page_id
        ]);
    }
    
    /**
     * Get all images used in template
     */
    public function get_template_images($request) {
        $page_id = $request['id'];
        
        $page = get_post($page_id);
        if (!$page || $page->post_type !== 'page') {
            return new WP_Error('page_not_found', 'Page not found', ['status' => 404]);
        }
        
        $variables = get_post_meta($page_id, '_kenzysites_template_variables', true) ?: [];
        $content = $page->post_content;
        
        // Find image variables in content
        $image_variables = [];
        preg_match_all('/\{\{([A-Z_]*(?:FOTO|IMAGE|IMG|BANNER)[A-Z_]*)\}\}/', $content, $matches);
        
        foreach ($matches[1] as $var) {
            $image_variables[$var] = [
                'variable' => $var,
                'current_url' => $variables[$var] ?? '',
                'has_image' => !empty($variables[$var])
            ];
        }
        
        // Get attached images
        $attachments = get_attached_media('image', $page_id);
        $attached_images = [];
        
        foreach ($attachments as $attachment) {
            $attached_images[] = [
                'id' => $attachment->ID,
                'url' => wp_get_attachment_url($attachment->ID),
                'title' => $attachment->post_title,
                'alt' => get_post_meta($attachment->ID, '_wp_attachment_image_alt', true),
                'sizes' => wp_get_attachment_metadata($attachment->ID)['sizes'] ?? []
            ];
        }
        
        return rest_ensure_response([
            'page_id' => $page_id,
            'image_variables' => $image_variables,
            'attached_images' => $attached_images,
            'upload_endpoint' => rest_url('kenzysites/v1/templates/' . $page_id . '/upload-image')
        ]);
    }
    
    /**
     * Log image upload
     */
    private function log_image_upload($page_id, $variable, $attachment_id, $url) {
        $log_entry = [
            'timestamp' => current_time('mysql'),
            'page_id' => $page_id,
            'variable' => $variable,
            'attachment_id' => $attachment_id,
            'image_url' => $url,
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown',
            'ip_address' => $_SERVER['REMOTE_ADDR'] ?? 'Unknown'
        ];
        
        $logs = get_option('kenzysites_image_upload_logs', []);
        $logs[] = $log_entry;
        
        // Keep only last 50 logs
        if (count($logs) > 50) {
            $logs = array_slice($logs, -50);
        }
        
        update_option('kenzysites_image_upload_logs', $logs);
    }
    
    /**
     * Get image upload logs
     */
    public function get_image_upload_logs($page_id = null) {
        $logs = get_option('kenzysites_image_upload_logs', []);
        
        if ($page_id) {
            $logs = array_filter($logs, function($log) use ($page_id) {
                return $log['page_id'] == $page_id;
            });
        }
        
        return array_reverse($logs); // Most recent first
    }
}

// Initialize the template engine
new KenzySites_Template_Engine();