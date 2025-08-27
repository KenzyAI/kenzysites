<?php
/**
 * KenzySites Color Manager
 * Gerencia cores globais do Elementor via API REST
 */

class KenzySites_Color_Manager {

    public function __construct() {
        add_action('rest_api_init', [$this, 'register_color_endpoints']);
    }

    /**
     * Registrar endpoints da API REST para cores
     */
    public function register_color_endpoints() {
        // Aplicar esquema de cores
        register_rest_route('kenzysites/v1', '/elementor/colors', [
            'methods' => 'POST',
            'callback' => [$this, 'apply_color_scheme'],
            'permission_callback' => [$this, 'check_permissions']
        ]);

        // Obter cores atuais
        register_rest_route('kenzysites/v1', '/elementor/colors/(?P<kit_id>\d+)', [
            'methods' => 'GET', 
            'callback' => [$this, 'get_current_colors'],
            'permission_callback' => [$this, 'check_permissions']
        ]);

        // Gerar cores com IA
        register_rest_route('kenzysites/v1', '/ai/generate-colors', [
            'methods' => 'POST',
            'callback' => [$this, 'generate_ai_colors'], 
            'permission_callback' => [$this, 'check_permissions']
        ]);
    }

    /**
     * Aplicar esquema de cores no Elementor Kit
     */
    public function apply_color_scheme(WP_REST_Request $request) {
        try {
            $kit_id = $request->get_param('kit_id');
            $colors = $request->get_param('colors');

            if (!$kit_id || !$colors) {
                return new WP_Error('missing_params', 'Kit ID e cores são obrigatórios', ['status' => 400]);
            }

            // Verificar se o kit existe
            $kit_post = get_post($kit_id);
            if (!$kit_post || $kit_post->post_type !== 'elementor_library') {
                return new WP_Error('invalid_kit', 'Kit do Elementor não encontrado', ['status' => 404]);
            }

            // Obter configurações atuais do kit
            $current_settings = get_post_meta($kit_id, '_elementor_page_settings', true);
            if (!$current_settings) {
                $current_settings = [];
            }

            // Aplicar novas cores mantendo outras configurações
            $current_settings['system_colors'] = $colors['system_colors'];

            // Salvar configurações atualizadas
            $result = update_post_meta($kit_id, '_elementor_page_settings', $current_settings);

            if ($result === false) {
                return new WP_Error('update_failed', 'Falha ao atualizar cores', ['status' => 500]);
            }

            // Regenerar CSS do Elementor
            $this->regenerate_elementor_css($kit_id);

            // Log da atividade
            error_log("KenzySites: Cores aplicadas ao Kit #{$kit_id}");

            return [
                'success' => true,
                'message' => 'Esquema de cores aplicado com sucesso!',
                'kit_id' => $kit_id,
                'colors_applied' => count($colors['system_colors'])
            ];

        } catch (Exception $e) {
            error_log("KenzySites Color Manager Error: " . $e->getMessage());
            
            return new WP_Error('server_error', 'Erro interno do servidor', [
                'status' => 500,
                'details' => $e->getMessage()
            ]);
        }
    }

    /**
     * Obter cores atuais do kit
     */
    public function get_current_colors(WP_REST_Request $request) {
        $kit_id = $request->get_param('kit_id');
        
        $settings = get_post_meta($kit_id, '_elementor_page_settings', true);
        
        if (!$settings || !isset($settings['system_colors'])) {
            return [
                'success' => false,
                'message' => 'Nenhuma cor definida neste kit'
            ];
        }

        return [
            'success' => true,
            'kit_id' => $kit_id,
            'colors' => $settings['system_colors']
        ];
    }

    /**
     * Gerar cores com IA baseado em informações do negócio
     */
    public function generate_ai_colors(WP_REST_Request $request) {
        $business_info = $request->get_param('business_info');
        
        if (!$business_info || !isset($business_info['industry'])) {
            return new WP_Error('missing_business_info', 'Informações do negócio são obrigatórias', ['status' => 400]);
        }

        // Algoritmo de geração de cores por indústria
        $color_scheme = $this->generate_industry_colors($business_info);

        return [
            'success' => true,
            'color_scheme' => $color_scheme,
            'industry' => $business_info['industry'],
            'generated_at' => current_time('mysql')
        ];
    }

    /**
     * Gerar cores baseado na indústria e mood
     */
    private function generate_industry_colors($business_info) {
        $industry = $business_info['industry'] ?? 'business';
        $mood = $business_info['mood'] ?? 'professional';

        // Cores base por indústria (HSL)
        $industry_colors = [
            'medical' => ['hue' => 200, 'saturation' => 70, 'lightness' => 45],
            'business' => ['hue' => 220, 'saturation' => 80, 'lightness' => 40], 
            'restaurant' => ['hue' => 25, 'saturation' => 85, 'lightness' => 50],
            'tech' => ['hue' => 260, 'saturation' => 75, 'lightness' => 55],
            'education' => ['hue' => 120, 'saturation' => 60, 'lightness' => 45],
            'default' => ['hue' => 200, 'saturation' => 65, 'lightness' => 50]
        ];

        // Ajustes por mood
        $mood_adjustments = [
            'professional' => ['saturation' => -10, 'lightness' => -5],
            'friendly' => ['saturation' => 15, 'lightness' => 10],
            'modern' => ['saturation' => 5, 'lightness' => 5],
            'classic' => ['saturation' => -15, 'lightness' => -10],
            'creative' => ['saturation' => 20, 'lightness' => 15]
        ];

        $base = $industry_colors[$industry] ?? $industry_colors['default'];
        $adjustment = $mood_adjustments[$mood] ?? ['saturation' => 0, 'lightness' => 0];

        // Calcular cores finais
        $primary_hsl = [
            'h' => $base['hue'],
            's' => max(0, min(100, $base['saturation'] + $adjustment['saturation'])),
            'l' => max(0, min(100, $base['lightness'] + $adjustment['lightness']))
        ];

        return [
            'primary' => $this->hsl_to_hex($primary_hsl['h'], $primary_hsl['s'], $primary_hsl['l']),
            'secondary' => $this->hsl_to_hex(($primary_hsl['h'] + 30) % 360, max(0, $primary_hsl['s'] - 20), max(0, $primary_hsl['l'] + 20)),
            'accent' => $this->hsl_to_hex(($primary_hsl['h'] + 180) % 360, min(100, $primary_hsl['s'] + 10), max(0, $primary_hsl['l'] - 10)),
            'text' => '#333333',
            'background' => '#ffffff'
        ];
    }

    /**
     * Converter HSL para HEX
     */
    private function hsl_to_hex($h, $s, $l) {
        $h /= 360;
        $s /= 100;
        $l /= 100;

        if ($s == 0) {
            $r = $g = $b = $l; // achromatic
        } else {
            $hue2rgb = function($p, $q, $t) {
                if ($t < 0) $t += 1;
                if ($t > 1) $t -= 1;
                if ($t < 1/6) return $p + ($q - $p) * 6 * $t;
                if ($t < 1/2) return $q;
                if ($t < 2/3) return $p + ($q - $p) * (2/3 - $t) * 6;
                return $p;
            };

            $q = $l < 0.5 ? $l * (1 + $s) : $l + $s - $l * $s;
            $p = 2 * $l - $q;
            $r = $hue2rgb($p, $q, $h + 1/3);
            $g = $hue2rgb($p, $q, $h);
            $b = $hue2rgb($p, $q, $h - 1/3);
        }

        return sprintf("#%02x%02x%02x", round($r * 255), round($g * 255), round($b * 255));
    }

    /**
     * Regenerar CSS do Elementor
     */
    private function regenerate_elementor_css($kit_id) {
        // Verificar se o Elementor está ativo
        if (!class_exists('Elementor\Plugin')) {
            return false;
        }

        try {
            // Clear do cache CSS do Elementor
            if (method_exists('Elementor\Plugin', 'instance')) {
                $elementor = \Elementor\Plugin::instance();
                
                if (method_exists($elementor->files_manager, 'clear_cache')) {
                    $elementor->files_manager->clear_cache();
                }
                
                if (method_exists($elementor->css_file, 'update')) {
                    $elementor->css_file->update();
                }
            }

            return true;

        } catch (Exception $e) {
            error_log("KenzySites: Erro ao regenerar CSS - " . $e->getMessage());
            return false;
        }
    }

    /**
     * Verificar permissões
     */
    public function check_permissions() {
        // Verificar se é admin ou tem capacidade de editar
        if (current_user_can('manage_options') || current_user_can('edit_posts')) {
            return true;
        }

        // Verificar authentication header (para API externa)
        $auth_header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        if ($auth_header && $this->validate_api_key($auth_header)) {
            return true;
        }

        return false;
    }

    /**
     * Validar API key para acesso externo
     */
    private function validate_api_key($auth_header) {
        // Extrair key do header "Bearer YOUR_API_KEY"
        if (!preg_match('/Bearer\s+(.+)/', $auth_header, $matches)) {
            return false;
        }

        $provided_key = $matches[1];
        $valid_key = get_option('kenzysites_api_key', '');

        return hash_equals($valid_key, $provided_key);
    }
}

// Inicializar o gerenciador de cores
new KenzySites_Color_Manager();