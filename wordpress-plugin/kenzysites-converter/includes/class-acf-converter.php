<?php
/**
 * ACF Converter Class
 * Converts Elementor pages to ACF templates
 */

if (!defined('ABSPATH')) {
    exit;
}

class KenzySites_ACF_Converter {
    
    private $elementor_scanner;
    
    public function __construct() {
        $this->elementor_scanner = new KenzySites_Elementor_Scanner();
    }
    
    /**
     * Convert Elementor page to ACF template
     */
    public function convert_page($page_id, $landing_page_type = 'service_showcase') {
        $page = get_post($page_id);
        if (!$page) {
            throw new Exception(__('Página não encontrada', 'kenzysites-converter'));
        }
        
        // Get page analysis
        $page_data = $this->elementor_scanner->analyze_elementor_page($page_id);
        if (!$page_data) {
            throw new Exception(__('Dados Elementor não encontrados para esta página', 'kenzysites-converter'));
        }
        
        // Extract dynamic content
        $dynamic_content = $this->elementor_scanner->extract_dynamic_content($page_id);
        
        // Generate ACF field groups
        $acf_field_groups = $this->generate_acf_field_groups($landing_page_type, $dynamic_content, $page_data);
        
        // Create template ID
        $template_id = 'elementor_' . $page_id . '_' . time();
        
        // Prepare template data
        $template_data = [
            'template_id' => $template_id,
            'source_page_id' => $page_id,
            'page_title' => $page->post_title,
            'page_url' => get_permalink($page_id),
            'landing_page_type' => $landing_page_type,
            'industry' => $this->detect_industry($page_data),
            'acf_field_groups' => $acf_field_groups,
            'elementor_data' => $this->elementor_scanner->get_elementor_data($page_id),
            'elementor_settings' => $this->elementor_scanner->get_elementor_settings($page_id),
            'dynamic_content' => $dynamic_content,
            'analysis' => $page_data['analysis'],
            'conversion_score' => $page_data['conversion_score'],
            'suggested_customizations' => $this->suggest_customizations($page_data, $dynamic_content),
            'seo_data' => $this->extract_seo_data($page_id),
            'conversion_date' => current_time('mysql')
        ];
        
        // Save to database
        $this->save_converted_template($template_data);
        
        return $template_data;
    }
    
    /**
     * Generate ACF field groups based on landing page type and dynamic content
     */
    private function generate_acf_field_groups($landing_page_type, $dynamic_content, $page_data) {
        $field_groups = [];
        
        // Base field groups for all landing pages
        $field_groups[] = $this->create_hero_section_fields($dynamic_content);
        $field_groups[] = $this->create_contact_info_fields();
        $field_groups[] = $this->create_seo_fields();
        
        // Type-specific field groups
        switch ($landing_page_type) {
            case 'lead_generation':
                $field_groups[] = $this->create_form_fields();
                $field_groups[] = $this->create_testimonials_fields();
                break;
                
            case 'service_showcase':
                $field_groups[] = $this->create_services_fields($dynamic_content);
                $field_groups[] = $this->create_testimonials_fields();
                $field_groups[] = $this->create_form_fields();
                break;
                
            case 'product_launch':
                $field_groups[] = $this->create_product_fields($dynamic_content);
                $field_groups[] = $this->create_pricing_fields();
                break;
                
            case 'event_promotion':
                $field_groups[] = $this->create_event_fields($dynamic_content);
                $field_groups[] = $this->create_form_fields();
                break;
                
            case 'webinar':
                $field_groups[] = $this->create_webinar_fields($dynamic_content);
                $field_groups[] = $this->create_form_fields();
                break;
        }
        
        // Add CTA section for all types
        $field_groups[] = $this->create_cta_fields($dynamic_content);
        
        // Add dynamic content fields if found
        if (!empty($dynamic_content)) {
            $field_groups[] = $this->create_dynamic_content_fields($dynamic_content);
        }
        
        return array_filter($field_groups); // Remove empty groups
    }
    
    /**
     * Create Hero Section Fields
     */
    private function create_hero_section_fields($dynamic_content) {
        $fields = [
            [
                'key' => 'field_hero_headline',
                'name' => 'hero_headline',
                'label' => 'Título Principal',
                'type' => 'text',
                'instructions' => 'Título principal que aparece na seção hero',
                'required' => 1,
                'placeholder' => $this->extract_placeholder_from_dynamic('heading', $dynamic_content, 'Transforme Seu Negócio'),
                'maxlength' => 80
            ],
            [
                'key' => 'field_hero_subtitle',
                'name' => 'hero_subtitle',
                'label' => 'Subtítulo',
                'type' => 'textarea',
                'instructions' => 'Descrição complementar do título principal',
                'required' => 1,
                'placeholder' => $this->extract_placeholder_from_dynamic('text', $dynamic_content, 'Aumente suas vendas com nossa solução'),
                'rows' => 3,
                'maxlength' => 200
            ],
            [
                'key' => 'field_hero_cta_text',
                'name' => 'hero_cta_text',
                'label' => 'Texto do Botão Principal',
                'type' => 'text',
                'instructions' => 'Texto do call-to-action principal',
                'required' => 1,
                'placeholder' => $this->extract_placeholder_from_dynamic('button', $dynamic_content, 'Começar Agora'),
                'maxlength' => 30
            ],
            [
                'key' => 'field_hero_cta_link',
                'name' => 'hero_cta_link',
                'label' => 'Link do Botão Principal',
                'type' => 'url',
                'instructions' => 'URL para onde o botão principal direciona',
                'required' => 1,
                'placeholder' => 'https://exemplo.com/contato'
            ],
            [
                'key' => 'field_hero_background_image',
                'name' => 'hero_background_image',
                'label' => 'Imagem de Fundo',
                'type' => 'image',
                'instructions' => 'Imagem de fundo da seção hero (1920x1080px recomendado)',
                'required' => 0,
                'return_format' => 'url',
                'preview_size' => 'medium'
            ]
        ];
        
        return [
            'key' => 'group_hero_section',
            'title' => 'Seção Hero/Banner',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 0,
            'position' => 'normal',
            'style' => 'default'
        ];
    }
    
    /**
     * Create Contact Info Fields
     */
    private function create_contact_info_fields() {
        $fields = [
            [
                'key' => 'field_business_name',
                'name' => 'business_name',
                'label' => 'Nome do Negócio',
                'type' => 'text',
                'instructions' => 'Nome da empresa/negócio',
                'required' => 1,
                'maxlength' => 100
            ],
            [
                'key' => 'field_contact_phone',
                'name' => 'contact_phone',
                'label' => 'Telefone',
                'type' => 'text',
                'instructions' => 'Número de telefone para contato',
                'placeholder' => '(11) 99999-9999'
            ],
            [
                'key' => 'field_contact_email',
                'name' => 'contact_email',
                'label' => 'E-mail',
                'type' => 'email',
                'instructions' => 'E-mail para contato',
                'placeholder' => 'contato@empresa.com.br'
            ],
            [
                'key' => 'field_contact_whatsapp',
                'name' => 'contact_whatsapp',
                'label' => 'WhatsApp',
                'type' => 'text',
                'instructions' => 'Número do WhatsApp (apenas números)',
                'placeholder' => '5511999999999'
            ],
            [
                'key' => 'field_contact_address',
                'name' => 'contact_address',
                'label' => 'Endereço',
                'type' => 'textarea',
                'instructions' => 'Endereço completo',
                'rows' => 3
            ],
            [
                'key' => 'field_business_logo',
                'name' => 'business_logo',
                'label' => 'Logo da Empresa',
                'type' => 'image',
                'instructions' => 'Logo da empresa (PNG com fundo transparente recomendado)',
                'return_format' => 'url'
            ]
        ];
        
        return [
            'key' => 'group_contact_info',
            'title' => 'Informações de Contato',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 1
        ];
    }
    
    /**
     * Create Services Fields
     */
    private function create_services_fields($dynamic_content) {
        $fields = [
            [
                'key' => 'field_services_title',
                'name' => 'services_title',
                'label' => 'Título da Seção',
                'type' => 'text',
                'placeholder' => 'Nossos Serviços',
                'maxlength' => 60
            ],
            [
                'key' => 'field_services_list',
                'name' => 'services_list',
                'label' => 'Lista de Serviços',
                'type' => 'repeater',
                'instructions' => 'Adicione os serviços oferecidos',
                'min' => 1,
                'max' => 6,
                'layout' => 'row',
                'sub_fields' => [
                    [
                        'key' => 'field_service_icon',
                        'name' => 'service_icon',
                        'label' => 'Ícone',
                        'type' => 'image',
                        'return_format' => 'url'
                    ],
                    [
                        'key' => 'field_service_title',
                        'name' => 'service_title',
                        'label' => 'Título do Serviço',
                        'type' => 'text',
                        'required' => 1,
                        'maxlength' => 50
                    ],
                    [
                        'key' => 'field_service_description',
                        'name' => 'service_description',
                        'label' => 'Descrição',
                        'type' => 'textarea',
                        'rows' => 3,
                        'maxlength' => 150
                    ]
                ]
            ]
        ];
        
        return [
            'key' => 'group_services',
            'title' => 'Seção de Serviços',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 2
        ];
    }
    
    /**
     * Create Form Fields
     */
    private function create_form_fields() {
        $fields = [
            [
                'key' => 'field_form_title',
                'name' => 'form_title',
                'label' => 'Título do Formulário',
                'type' => 'text',
                'placeholder' => 'Entre em Contato',
                'maxlength' => 40
            ],
            [
                'key' => 'field_form_description',
                'name' => 'form_description',
                'label' => 'Descrição do Formulário',
                'type' => 'textarea',
                'rows' => 2,
                'maxlength' => 100
            ],
            [
                'key' => 'field_form_button_text',
                'name' => 'form_button_text',
                'label' => 'Texto do Botão',
                'type' => 'text',
                'default_value' => 'Enviar',
                'maxlength' => 25
            ],
            [
                'key' => 'field_form_success_message',
                'name' => 'form_success_message',
                'label' => 'Mensagem de Sucesso',
                'type' => 'textarea',
                'default_value' => 'Obrigado! Entraremos em contato em breve.',
                'rows' => 2
            ]
        ];
        
        return [
            'key' => 'group_contact_form',
            'title' => 'Formulário de Contato',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 3
        ];
    }
    
    /**
     * Create Testimonials Fields
     */
    private function create_testimonials_fields() {
        $fields = [
            [
                'key' => 'field_testimonials_title',
                'name' => 'testimonials_title',
                'label' => 'Título da Seção',
                'type' => 'text',
                'placeholder' => 'O Que Nossos Clientes Dizem',
                'maxlength' => 60
            ],
            [
                'key' => 'field_testimonials_list',
                'name' => 'testimonials_list',
                'label' => 'Depoimentos',
                'type' => 'repeater',
                'min' => 1,
                'max' => 6,
                'layout' => 'row',
                'sub_fields' => [
                    [
                        'key' => 'field_testimonial_content',
                        'name' => 'testimonial_content',
                        'label' => 'Depoimento',
                        'type' => 'textarea',
                        'required' => 1,
                        'rows' => 4,
                        'maxlength' => 300
                    ],
                    [
                        'key' => 'field_testimonial_author',
                        'name' => 'testimonial_author',
                        'label' => 'Nome do Cliente',
                        'type' => 'text',
                        'required' => 1,
                        'maxlength' => 50
                    ],
                    [
                        'key' => 'field_testimonial_role',
                        'name' => 'testimonial_role',
                        'label' => 'Cargo/Empresa',
                        'type' => 'text',
                        'placeholder' => 'CEO, Empresa XYZ',
                        'maxlength' => 80
                    ],
                    [
                        'key' => 'field_testimonial_avatar',
                        'name' => 'testimonial_avatar',
                        'label' => 'Foto do Cliente',
                        'type' => 'image',
                        'return_format' => 'url'
                    ]
                ]
            ]
        ];
        
        return [
            'key' => 'group_testimonials',
            'title' => 'Seção de Depoimentos',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 4
        ];
    }
    
    /**
     * Create CTA Fields
     */
    private function create_cta_fields($dynamic_content) {
        $fields = [
            [
                'key' => 'field_cta_headline',
                'name' => 'cta_headline',
                'label' => 'Título do CTA',
                'type' => 'text',
                'placeholder' => $this->extract_placeholder_from_dynamic('heading', $dynamic_content, 'Pronto Para Começar?'),
                'maxlength' => 50
            ],
            [
                'key' => 'field_cta_description',
                'name' => 'cta_description',
                'label' => 'Descrição do CTA',
                'type' => 'textarea',
                'rows' => 2,
                'placeholder' => 'Entre em contato e transforme seu negócio hoje mesmo!',
                'maxlength' => 150
            ],
            [
                'key' => 'field_cta_button_text',
                'name' => 'cta_button_text',
                'label' => 'Texto do Botão',
                'type' => 'text',
                'placeholder' => $this->extract_placeholder_from_dynamic('button', $dynamic_content, 'Falar Conosco'),
                'maxlength' => 25
            ],
            [
                'key' => 'field_cta_button_link',
                'name' => 'cta_button_link',
                'label' => 'Link do Botão',
                'type' => 'url',
                'placeholder' => '#contato'
            ]
        ];
        
        return [
            'key' => 'group_cta_section',
            'title' => 'Seção Call-to-Action',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 5
        ];
    }
    
    /**
     * Create SEO Fields
     */
    private function create_seo_fields() {
        $fields = [
            [
                'key' => 'field_seo_title',
                'name' => 'seo_title',
                'label' => 'Título SEO',
                'type' => 'text',
                'instructions' => 'Título para mecanismos de busca (50-60 caracteres)',
                'maxlength' => 60
            ],
            [
                'key' => 'field_seo_description',
                'name' => 'seo_description',
                'label' => 'Meta Descrição',
                'type' => 'textarea',
                'instructions' => 'Descrição para mecanismos de busca (150-160 caracteres)',
                'rows' => 3,
                'maxlength' => 160
            ],
            [
                'key' => 'field_seo_keywords',
                'name' => 'seo_keywords',
                'label' => 'Palavras-chave',
                'type' => 'text',
                'instructions' => 'Palavras-chave separadas por vírgula'
            ]
        ];
        
        return [
            'key' => 'group_seo_settings',
            'title' => 'Configurações SEO',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 10,
            'position' => 'side'
        ];
    }
    
    /**
     * Create Dynamic Content Fields from detected content
     */
    private function create_dynamic_content_fields($dynamic_content) {
        if (empty($dynamic_content)) {
            return null;
        }
        
        $fields = [];
        $processed = [];
        
        foreach ($dynamic_content as $index => $item) {
            $field_key = 'field_dynamic_' . md5($item['content']);
            
            // Avoid duplicates
            if (in_array($field_key, $processed)) {
                continue;
            }
            $processed[] = $field_key;
            
            $field_name = 'dynamic_' . $index;
            $field_label = $this->generate_field_label($item);
            
            $field = [
                'key' => $field_key,
                'name' => $field_name,
                'label' => $field_label,
                'type' => $item['acf_field_suggestion'],
                'instructions' => 'Campo extraído automaticamente: ' . $item['widget_type'],
                'placeholder' => strlen($item['content']) > 50 ? substr($item['content'], 0, 50) . '...' : $item['content']
            ];
            
            // Add type-specific properties
            if ($item['acf_field_suggestion'] === 'textarea') {
                $field['rows'] = 3;
            } elseif ($item['acf_field_suggestion'] === 'image') {
                $field['return_format'] = 'url';
            }
            
            $fields[] = $field;
        }
        
        if (empty($fields)) {
            return null;
        }
        
        return [
            'key' => 'group_dynamic_content',
            'title' => 'Conteúdo Dinâmico Detectado',
            'fields' => $fields,
            'location' => [
                [
                    [
                        'param' => 'post_type',
                        'operator' => '==',
                        'value' => 'page'
                    ]
                ]
            ],
            'menu_order' => 6,
            'description' => 'Campos extraídos automaticamente do template Elementor'
        ];
    }
    
    /**
     * Extract placeholder from dynamic content
     */
    private function extract_placeholder_from_dynamic($type, $dynamic_content, $default) {
        foreach ($dynamic_content as $item) {
            if ($item['widget_type'] === $type || 
                strpos($item['widget_type'], $type) !== false) {
                return $item['content'];
            }
        }
        return $default;
    }
    
    /**
     * Generate field label from dynamic content item
     */
    private function generate_field_label($item) {
        $widget_labels = [
            'heading' => 'Título',
            'text-editor' => 'Texto', 
            'button' => 'Botão',
            'image' => 'Imagem',
            'icon' => 'Ícone'
        ];
        
        $base_label = $widget_labels[$item['widget_type']] ?? ucfirst($item['widget_type']);
        
        // Try to make it more specific
        if ($item['setting_key']) {
            $key_labels = [
                'title' => 'Título',
                'text' => 'Texto',
                'url' => 'URL',
                'link' => 'Link'
            ];
            
            if (isset($key_labels[$item['setting_key']])) {
                $base_label .= ' - ' . $key_labels[$item['setting_key']];
            }
        }
        
        return $base_label;
    }
    
    /**
     * Detect industry from page content
     */
    private function detect_industry($page_data) {
        $title = strtolower($page_data['title']);
        $analysis = $page_data['analysis'];
        
        // Industry keywords mapping
        $industries = [
            'restaurante' => ['restaurante', 'pizzaria', 'comida', 'delivery', 'cardápio', 'chef'],
            'dentista' => ['dentista', 'odonto', 'dental', 'sorriso', 'dente', 'clareamento'],
            'advogado' => ['advogado', 'juridico', 'direito', 'advocacia', 'legal', 'tribunal'],
            'clinica_estetica' => ['estetica', 'beleza', 'botox', 'laser', 'harmonização', 'procedimento'],
            'academia' => ['academia', 'fitness', 'musculação', 'personal', 'treino', 'exercicio'],
            'imobiliaria' => ['imovel', 'casa', 'apartamento', 'venda', 'aluguel', 'corretor'],
            'consultoria' => ['consultoria', 'consultor', 'estrategia', 'gestão', 'negócios', 'empresarial'],
            'saas' => ['software', 'sistema', 'plataforma', 'app', 'tecnologia', 'digital'],
            'educacao' => ['curso', 'escola', 'ensino', 'aula', 'professor', 'aprender']
        ];
        
        foreach ($industries as $industry => $keywords) {
            foreach ($keywords as $keyword) {
                if (strpos($title, $keyword) !== false) {
                    return $industry;
                }
            }
        }
        
        // Default fallback based on features
        if ($analysis['has_form'] && $analysis['has_testimonials']) {
            return 'consultoria';
        } elseif ($analysis['has_pricing']) {
            return 'saas';
        } else {
            return 'consultoria'; // Default
        }
    }
    
    /**
     * Extract SEO data from page
     */
    private function extract_seo_data($page_id) {
        $page = get_post($page_id);
        
        return [
            'current_title' => $page->post_title,
            'current_excerpt' => $page->post_excerpt,
            'yoast_title' => get_post_meta($page_id, '_yoast_wpseo_title', true),
            'yoast_description' => get_post_meta($page_id, '_yoast_wpseo_metadesc', true),
            'suggested_title' => $page->post_title . ' - Solução Completa',
            'suggested_description' => substr(strip_tags($page->post_content), 0, 150) . '...'
        ];
    }
    
    /**
     * Suggest customizations based on analysis
     */
    private function suggest_customizations($page_data, $dynamic_content) {
        $suggestions = [];
        
        $analysis = $page_data['analysis'];
        
        // CTA suggestions
        if ($analysis['cta_buttons'] < 2) {
            $suggestions[] = [
                'type' => 'cta',
                'priority' => 'high',
                'message' => 'Adicionar mais botões de call-to-action para aumentar conversões'
            ];
        }
        
        // Form suggestions
        if (!$analysis['has_form']) {
            $suggestions[] = [
                'type' => 'form',
                'priority' => 'high',
                'message' => 'Adicionar formulário de captura de leads'
            ];
        }
        
        // Social proof suggestions
        if (!$analysis['has_testimonials']) {
            $suggestions[] = [
                'type' => 'testimonials',
                'priority' => 'medium',
                'message' => 'Adicionar seção de depoimentos para gerar confiança'
            ];
        }
        
        // Content suggestions
        if (count($dynamic_content) < 5) {
            $suggestions[] = [
                'type' => 'content',
                'priority' => 'low',
                'message' => 'Adicionar mais conteúdo personalizável para diferentes clientes'
            ];
        }
        
        return $suggestions;
    }
    
    /**
     * Save converted template to database
     */
    private function save_converted_template($template_data) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        $result = $wpdb->insert(
            $table_name,
            [
                'page_id' => $template_data['source_page_id'],
                'template_id' => $template_data['template_id'],
                'landing_page_type' => $template_data['landing_page_type'],
                'acf_data' => json_encode($template_data['acf_field_groups']),
                'elementor_data' => $template_data['elementor_data'],
                'conversion_date' => $template_data['conversion_date'],
                'sync_status' => 'pending'
            ],
            ['%d', '%s', '%s', '%s', '%s', '%s', '%s']
        );
        
        if ($result === false) {
            throw new Exception(__('Erro ao salvar template convertido no banco de dados', 'kenzysites-converter'));
        }
        
        return $wpdb->insert_id;
    }
    
    /**
     * Get converted template by ID
     */
    public function get_converted_template($template_id) {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        return $wpdb->get_row(
            $wpdb->prepare("SELECT * FROM $table_name WHERE template_id = %s", $template_id),
            ARRAY_A
        );
    }
    
    /**
     * Update sync status
     */
    public function update_sync_status($template_id, $status, $error_message = '') {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        
        $update_data = [
            'sync_status' => $status,
            'sync_date' => current_time('mysql')
        ];
        
        if (!empty($error_message)) {
            $update_data['sync_error'] = $error_message;
        }
        
        return $wpdb->update(
            $table_name,
            $update_data,
            ['template_id' => $template_id],
            ['%s', '%s', '%s'],
            ['%s']
        );
    }
}