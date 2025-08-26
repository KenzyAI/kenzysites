<?php
/**
 * Plugin Name: KenzySites Template Manager
 * Description: Advanced template management system for KenzySites with Elementor and ACF integration
 * Version: 2.0.0
 * Author: KenzySites
 * Text Domain: kenzysites
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('KENZYSITES_VERSION', '2.0.0');
define('KENZYSITES_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('KENZYSITES_PLUGIN_URL', plugin_dir_url(__FILE__));
define('KENZYSITES_EXPORT_DIR', WP_CONTENT_DIR . '/exports/');

// Create export directory if it doesn't exist
if (!file_exists(KENZYSITES_EXPORT_DIR)) {
    wp_mkdir_p(KENZYSITES_EXPORT_DIR);
}

/**
 * Main plugin class
 */
class KenzySites_Template_Manager {
    
    /**
     * Available placeholders for dynamic content
     */
    private $placeholders = [
        '{{BUSINESS_NAME}}' => 'Nome do Negócio',
        '{{BUSINESS_DESCRIPTION}}' => 'Descrição completa do negócio',
        '{{BUSINESS_TAGLINE}}' => 'Slogan do negócio',
        '{{PHONE_NUMBER}}' => '(11) 9999-9999',
        '{{WHATSAPP_NUMBER}}' => '(11) 99999-9999',
        '{{EMAIL}}' => 'contato@exemplo.com.br',
        '{{ADDRESS}}' => 'Rua Exemplo, 123 - São Paulo, SP',
        '{{OPENING_HOURS}}' => 'Seg-Sex: 9h às 18h',
        '{{HERO_TITLE}}' => 'Título Principal',
        '{{HERO_SUBTITLE}}' => 'Subtítulo do Hero',
        '{{HERO_IMAGE}}' => '/placeholder-hero.jpg',
        '{{ABOUT_TITLE}}' => 'Sobre Nós',
        '{{ABOUT_TEXT}}' => 'Texto sobre a empresa',
        '{{ABOUT_IMAGE}}' => '/placeholder-about.jpg',
        '{{SERVICE_1_TITLE}}' => 'Serviço 1',
        '{{SERVICE_1_DESC}}' => 'Descrição do serviço 1',
        '{{SERVICE_1_ICON}}' => 'fas fa-star',
        '{{SERVICE_2_TITLE}}' => 'Serviço 2',
        '{{SERVICE_2_DESC}}' => 'Descrição do serviço 2',
        '{{SERVICE_2_ICON}}' => 'fas fa-check',
        '{{SERVICE_3_TITLE}}' => 'Serviço 3',
        '{{SERVICE_3_DESC}}' => 'Descrição do serviço 3',
        '{{SERVICE_3_ICON}}' => 'fas fa-heart',
        '{{CTA_TEXT}}' => 'Entre em Contato',
        '{{CTA_URL}}' => '#contato',
        '{{PRIMARY_COLOR}}' => '#0066FF',
        '{{SECONDARY_COLOR}}' => '#00D4FF',
        '{{ACCENT_COLOR}}' => '#FF6B35',
        '{{TEXT_COLOR}}' => '#333333',
        '{{TESTIMONIAL_1_TEXT}}' => 'Depoimento do cliente 1',
        '{{TESTIMONIAL_1_AUTHOR}}' => 'João Silva',
        '{{TESTIMONIAL_2_TEXT}}' => 'Depoimento do cliente 2',
        '{{TESTIMONIAL_2_AUTHOR}}' => 'Maria Santos',
        '{{INSTAGRAM_URL}}' => 'https://instagram.com/exemplo',
        '{{FACEBOOK_URL}}' => 'https://facebook.com/exemplo',
        '{{LINKEDIN_URL}}' => 'https://linkedin.com/company/exemplo',
        '{{PIX_KEY}}' => 'pix@exemplo.com.br',
        '{{CNPJ}}' => '00.000.000/0001-00'
    ];
    
    /**
     * Industries for templates
     */
    private $industries = [
        'restaurant' => 'Restaurante',
        'healthcare' => 'Saúde',
        'ecommerce' => 'E-commerce',
        'services' => 'Serviços',
        'education' => 'Educação'
    ];
    
    public function __construct() {
        add_action('admin_menu', [$this, 'add_admin_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_admin_scripts']);
        add_action('wp_ajax_kenzysites_export_template', [$this, 'ajax_export_template']);
        add_action('wp_ajax_kenzysites_export_all_templates', [$this, 'ajax_export_all_templates']);
        add_filter('the_content', [$this, 'replace_placeholders']);
        add_action('init', [$this, 'register_template_post_type']);
        
        // Elementor hooks
        if (did_action('elementor/loaded')) {
            add_action('elementor/editor/after_save', [$this, 'save_elementor_template_data'], 10, 2);
        }
    }
    
    /**
     * Register custom post type for templates
     */
    public function register_template_post_type() {
        register_post_type('kenzysites_template', [
            'labels' => [
                'name' => 'KenzySites Templates',
                'singular_name' => 'Template',
                'add_new' => 'Add New Template',
                'add_new_item' => 'Add New Template',
                'edit_item' => 'Edit Template',
                'new_item' => 'New Template',
                'view_item' => 'View Template',
                'search_items' => 'Search Templates',
                'not_found' => 'No templates found',
                'not_found_in_trash' => 'No templates found in trash'
            ],
            'public' => true,
            'has_archive' => true,
            'supports' => ['title', 'editor', 'thumbnail', 'custom-fields'],
            'menu_icon' => 'dashicons-layout',
            'show_in_rest' => true
        ]);
        
        // Register taxonomy for industries
        register_taxonomy('template_industry', 'kenzysites_template', [
            'labels' => [
                'name' => 'Industries',
                'singular_name' => 'Industry',
                'add_new_item' => 'Add New Industry',
                'new_item_name' => 'New Industry Name'
            ],
            'hierarchical' => true,
            'show_in_rest' => true
        ]);
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_menu_page(
            'KenzySites Templates',
            'KenzySites',
            'manage_options',
            'kenzysites',
            [$this, 'admin_page'],
            'dashicons-layout',
            30
        );
        
        add_submenu_page(
            'kenzysites',
            'Export Templates',
            'Export Templates',
            'manage_options',
            'kenzysites-export',
            [$this, 'export_page']
        );
        
        add_submenu_page(
            'kenzysites',
            'Placeholders',
            'Placeholders',
            'manage_options',
            'kenzysites-placeholders',
            [$this, 'placeholders_page']
        );
    }
    
    /**
     * Enqueue admin scripts
     */
    public function enqueue_admin_scripts($hook) {
        if (strpos($hook, 'kenzysites') !== false) {
            wp_enqueue_script(
                'kenzysites-admin',
                KENZYSITES_PLUGIN_URL . 'admin.js',
                ['jquery'],
                KENZYSITES_VERSION,
                true
            );
            
            wp_localize_script('kenzysites-admin', 'kenzysites_ajax', [
                'ajax_url' => admin_url('admin-ajax.php'),
                'nonce' => wp_create_nonce('kenzysites_ajax')
            ]);
            
            wp_enqueue_style(
                'kenzysites-admin',
                KENZYSITES_PLUGIN_URL . 'admin.css',
                [],
                KENZYSITES_VERSION
            );
        }
    }
    
    /**
     * Main admin page
     */
    public function admin_page() {
        ?>
        <div class="wrap">
            <h1>KenzySites Template System</h1>
            <p>Sistema avançado de templates para geração automatizada de sites WordPress.</p>
            
            <div class="kenzysites-dashboard">
                <div class="kenzysites-card">
                    <h2>📊 Status do Sistema</h2>
                    <ul>
                        <li>✅ Elementor: <?php echo did_action('elementor/loaded') ? 'Ativo' : '❌ Inativo'; ?></li>
                        <li>✅ ACF: <?php echo class_exists('ACF') ? 'Ativo' : '⚠️ Não instalado'; ?></li>
                        <li>✅ Astra Theme: <?php echo wp_get_theme()->get('Name') == 'Astra' ? 'Ativo' : '⚠️ Outro tema ativo'; ?></li>
                    </ul>
                </div>
                
                <div class="kenzysites-card">
                    <h2>🎨 Templates Criados</h2>
                    <?php
                    $templates = get_posts([
                        'post_type' => 'kenzysites_template',
                        'posts_per_page' => -1
                    ]);
                    
                    if ($templates) {
                        echo '<ul>';
                        foreach ($templates as $template) {
                            $industry = wp_get_post_terms($template->ID, 'template_industry');
                            $industry_name = $industry ? $industry[0]->name : 'Geral';
                            echo '<li>' . esc_html($template->post_title) . ' (' . esc_html($industry_name) . ')</li>';
                        }
                        echo '</ul>';
                    } else {
                        echo '<p>Nenhum template criado ainda.</p>';
                    }
                    ?>
                    <a href="<?php echo admin_url('post-new.php?post_type=kenzysites_template'); ?>" class="button button-primary">Criar Novo Template</a>
                </div>
                
                <div class="kenzysites-card">
                    <h2>🚀 Ações Rápidas</h2>
                    <p>
                        <a href="<?php echo admin_url('admin.php?page=kenzysites-export'); ?>" class="button">Exportar Templates</a>
                        <a href="<?php echo admin_url('admin.php?page=kenzysites-placeholders'); ?>" class="button">Ver Placeholders</a>
                    </p>
                </div>
            </div>
        </div>
        <?php
    }
    
    /**
     * Export page
     */
    public function export_page() {
        ?>
        <div class="wrap">
            <h1>Exportar Templates</h1>
            <p>Exporte seus templates para uso no sistema KenzySites.</p>
            
            <div class="kenzysites-export-section">
                <h2>Templates Disponíveis para Exportação</h2>
                
                <?php
                $templates = get_posts([
                    'post_type' => 'kenzysites_template',
                    'posts_per_page' => -1
                ]);
                
                if ($templates) {
                    ?>
                    <table class="wp-list-table widefat fixed striped">
                        <thead>
                            <tr>
                                <th>Template</th>
                                <th>Indústria</th>
                                <th>Última Modificação</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($templates as $template): ?>
                            <tr>
                                <td><?php echo esc_html($template->post_title); ?></td>
                                <td>
                                    <?php
                                    $industry = wp_get_post_terms($template->ID, 'template_industry');
                                    echo $industry ? esc_html($industry[0]->name) : 'Geral';
                                    ?>
                                </td>
                                <td><?php echo get_the_modified_date('d/m/Y H:i', $template->ID); ?></td>
                                <td>
                                    <button class="button export-template" data-template-id="<?php echo $template->ID; ?>">
                                        Exportar
                                    </button>
                                </td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                    
                    <p style="margin-top: 20px;">
                        <button class="button button-primary" id="export-all-templates">
                            Exportar Todos os Templates
                        </button>
                    </p>
                    <?php
                } else {
                    echo '<p>Nenhum template disponível para exportação.</p>';
                }
                ?>
            </div>
            
            <div id="export-result" style="margin-top: 20px;"></div>
        </div>
        <?php
    }
    
    /**
     * Placeholders page
     */
    public function placeholders_page() {
        ?>
        <div class="wrap">
            <h1>Placeholders Disponíveis</h1>
            <p>Use estes placeholders em seus templates. Eles serão substituídos dinamicamente pelo conteúdo real.</p>
            
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th style="width: 30%;">Placeholder</th>
                        <th style="width: 30%;">Valor de Exemplo</th>
                        <th style="width: 40%;">Descrição</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($this->placeholders as $key => $value): ?>
                    <tr>
                        <td><code><?php echo esc_html($key); ?></code></td>
                        <td><?php echo esc_html($value); ?></td>
                        <td><?php echo esc_html($this->get_placeholder_description($key)); ?></td>
                    </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            
            <div style="margin-top: 20px; padding: 15px; background: #f0f0f0; border-left: 4px solid #0066FF;">
                <h3>Como usar:</h3>
                <ol>
                    <li>Ao criar conteúdo no Elementor ou editor padrão, use os placeholders exatamente como mostrado</li>
                    <li>Por exemplo: "Bem-vindo à {{BUSINESS_NAME}}"</li>
                    <li>Os placeholders serão substituídos automaticamente quando o site for gerado</li>
                    <li>Use placeholders de cores no CSS customizado do Elementor</li>
                </ol>
            </div>
        </div>
        <?php
    }
    
    /**
     * Get placeholder description
     */
    private function get_placeholder_description($placeholder) {
        $descriptions = [
            '{{BUSINESS_NAME}}' => 'Nome principal do negócio',
            '{{BUSINESS_DESCRIPTION}}' => 'Descrição completa do negócio',
            '{{BUSINESS_TAGLINE}}' => 'Slogan ou frase de efeito',
            '{{PHONE_NUMBER}}' => 'Telefone fixo para contato',
            '{{WHATSAPP_NUMBER}}' => 'WhatsApp para contato rápido',
            '{{EMAIL}}' => 'E-mail principal de contato',
            '{{ADDRESS}}' => 'Endereço completo do negócio',
            '{{OPENING_HOURS}}' => 'Horário de funcionamento',
            '{{HERO_TITLE}}' => 'Título principal da página inicial',
            '{{HERO_SUBTITLE}}' => 'Subtítulo ou descrição breve',
            '{{HERO_IMAGE}}' => 'Imagem principal do hero section',
            '{{ABOUT_TITLE}}' => 'Título da seção Sobre',
            '{{ABOUT_TEXT}}' => 'Texto completo sobre a empresa',
            '{{ABOUT_IMAGE}}' => 'Imagem da seção Sobre',
            '{{SERVICE_1_TITLE}}' => 'Nome do primeiro serviço',
            '{{SERVICE_1_DESC}}' => 'Descrição do primeiro serviço',
            '{{SERVICE_1_ICON}}' => 'Ícone do primeiro serviço',
            '{{CTA_TEXT}}' => 'Texto do botão de call-to-action',
            '{{CTA_URL}}' => 'Link do botão CTA',
            '{{PRIMARY_COLOR}}' => 'Cor primária do site',
            '{{SECONDARY_COLOR}}' => 'Cor secundária do site',
            '{{ACCENT_COLOR}}' => 'Cor de destaque/acento',
            '{{PIX_KEY}}' => 'Chave PIX para pagamentos',
            '{{CNPJ}}' => 'CNPJ da empresa'
        ];
        
        return isset($descriptions[$placeholder]) ? $descriptions[$placeholder] : 'Placeholder dinâmico';
    }
    
    /**
     * Export template via AJAX
     */
    public function ajax_export_template() {
        check_ajax_referer('kenzysites_ajax', 'nonce');
        
        $template_id = intval($_POST['template_id']);
        $template = get_post($template_id);
        
        if (!$template) {
            wp_send_json_error('Template não encontrado');
        }
        
        $export_data = $this->prepare_template_export($template_id);
        
        // Save to file
        $filename = 'template_' . sanitize_title($template->post_title) . '_' . date('Y-m-d_H-i-s') . '.json';
        $filepath = KENZYSITES_EXPORT_DIR . $filename;
        
        file_put_contents($filepath, json_encode($export_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        
        wp_send_json_success([
            'message' => 'Template exportado com sucesso!',
            'filename' => $filename,
            'download_url' => content_url('exports/' . $filename)
        ]);
    }
    
    /**
     * Export all templates via AJAX
     */
    public function ajax_export_all_templates() {
        check_ajax_referer('kenzysites_ajax', 'nonce');
        
        $templates = get_posts([
            'post_type' => 'kenzysites_template',
            'posts_per_page' => -1
        ]);
        
        $export_data = [
            'version' => KENZYSITES_VERSION,
            'export_date' => date('Y-m-d H:i:s'),
            'site_url' => get_site_url(),
            'templates' => []
        ];
        
        foreach ($templates as $template) {
            $export_data['templates'][] = $this->prepare_template_export($template->ID);
        }
        
        $filename = 'all_templates_' . date('Y-m-d_H-i-s') . '.json';
        $filepath = KENZYSITES_EXPORT_DIR . $filename;
        
        file_put_contents($filepath, json_encode($export_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        
        wp_send_json_success([
            'message' => count($templates) . ' templates exportados com sucesso!',
            'filename' => $filename,
            'download_url' => content_url('exports/' . $filename)
        ]);
    }
    
    /**
     * Prepare template for export
     */
    private function prepare_template_export($template_id) {
        $template = get_post($template_id);
        $industry = wp_get_post_terms($template_id, 'template_industry');
        
        $export_data = [
            'id' => $template->post_name,
            'title' => $template->post_title,
            'industry' => $industry ? $industry[0]->slug : 'general',
            'industry_name' => $industry ? $industry[0]->name : 'Geral',
            'content' => $template->post_content,
            'excerpt' => $template->post_excerpt,
            'created_date' => $template->post_date,
            'modified_date' => $template->post_modified,
            'placeholders_used' => $this->extract_placeholders($template->post_content),
            'meta_data' => []
        ];
        
        // Get Elementor data if available
        if (did_action('elementor/loaded')) {
            $elementor_data = get_post_meta($template_id, '_elementor_data', true);
            if ($elementor_data) {
                $export_data['elementor_data'] = json_decode($elementor_data, true);
                $export_data['elementor_version'] = get_post_meta($template_id, '_elementor_version', true);
                $export_data['elementor_template_type'] = get_post_meta($template_id, '_elementor_template_type', true);
                $export_data['elementor_page_settings'] = get_post_meta($template_id, '_elementor_page_settings', true);
            }
        }
        
        // Get ACF fields if available
        if (function_exists('get_field_objects')) {
            $fields = get_field_objects($template_id);
            if ($fields) {
                $export_data['acf_fields'] = [];
                foreach ($fields as $field) {
                    $export_data['acf_fields'][$field['name']] = [
                        'label' => $field['label'],
                        'type' => $field['type'],
                        'value' => $field['value']
                    ];
                }
            }
        }
        
        // Get custom CSS
        $custom_css = get_post_meta($template_id, '_wp_page_template_css', true);
        if ($custom_css) {
            $export_data['custom_css'] = $custom_css;
        }
        
        // Get featured image
        if (has_post_thumbnail($template_id)) {
            $thumbnail_id = get_post_thumbnail_id($template_id);
            $export_data['featured_image'] = wp_get_attachment_url($thumbnail_id);
        }
        
        return $export_data;
    }
    
    /**
     * Extract placeholders from content
     */
    private function extract_placeholders($content) {
        $placeholders_found = [];
        
        foreach ($this->placeholders as $placeholder => $default_value) {
            if (strpos($content, $placeholder) !== false) {
                $placeholders_found[] = $placeholder;
            }
        }
        
        // Also check in Elementor data
        if (did_action('elementor/loaded')) {
            // This would need to recursively search through Elementor JSON
            // For now, we'll do a simple string search
            $content_string = json_encode($content);
            foreach ($this->placeholders as $placeholder => $default_value) {
                if (strpos($content_string, $placeholder) !== false && !in_array($placeholder, $placeholders_found)) {
                    $placeholders_found[] = $placeholder;
                }
            }
        }
        
        return $placeholders_found;
    }
    
    /**
     * Replace placeholders in content
     */
    public function replace_placeholders($content) {
        // Only replace on frontend, not in admin
        if (is_admin()) {
            return $content;
        }
        
        foreach ($this->placeholders as $placeholder => $default_value) {
            $value = get_option('kenzysites_' . strtolower(str_replace(['{{', '}}', ' '], ['', '', '_'], $placeholder)), $default_value);
            $content = str_replace($placeholder, $value, $content);
        }
        
        return $content;
    }
    
    /**
     * Save Elementor template data
     */
    public function save_elementor_template_data($post_id, $editor_data) {
        // Additional processing when Elementor template is saved
        update_post_meta($post_id, '_kenzysites_has_elementor', true);
        
        // Extract and save placeholders used
        $content_string = json_encode($editor_data);
        $placeholders_used = [];
        
        foreach ($this->placeholders as $placeholder => $default) {
            if (strpos($content_string, $placeholder) !== false) {
                $placeholders_used[] = $placeholder;
            }
        }
        
        update_post_meta($post_id, '_kenzysites_placeholders', $placeholders_used);
    }
}

// Initialize the plugin
new KenzySites_Template_Manager();