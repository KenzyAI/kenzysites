<?php
/**
 * Elementor Scanner Class
 * Scans and analyzes Elementor pages
 */

if (!defined('ABSPATH')) {
    exit;
}

class KenzySites_Elementor_Scanner {
    
    /**
     * Scan all Elementor pages
     */
    public function scan_elementor_pages() {
        // Check if Elementor is active
        if (!class_exists('\\Elementor\\Plugin')) {
            throw new Exception(__('Elementor não está ativo', 'kenzysites-converter'));
        }
        
        // Query for pages with Elementor data
        $pages = get_posts([
            'post_type' => 'page',
            'post_status' => 'publish',
            'posts_per_page' => -1,
            'meta_query' => [
                [
                    'key' => '_elementor_edit_mode',
                    'value' => 'builder',
                    'compare' => '='
                ]
            ]
        ]);
        
        $scanned_pages = [];
        
        foreach ($pages as $page) {
            $page_data = $this->analyze_elementor_page($page->ID);
            if ($page_data) {
                $scanned_pages[] = $page_data;
            }
        }
        
        return $scanned_pages;
    }
    
    /**
     * Analyze a specific Elementor page
     */
    public function analyze_elementor_page($page_id) {
        $page = get_post($page_id);
        if (!$page) {
            return null;
        }
        
        // Get Elementor data
        $elementor_data = get_post_meta($page_id, '_elementor_data', true);
        if (empty($elementor_data)) {
            return null;
        }
        
        // Parse Elementor JSON data
        $elements = json_decode($elementor_data, true);
        if (!is_array($elements)) {
            return null;
        }
        
        // Analyze page structure
        $analysis = $this->analyze_page_structure($elements);
        
        // Get page thumbnail
        $thumbnail = get_the_post_thumbnail_url($page_id, 'medium');
        if (!$thumbnail) {
            $thumbnail = KENZYSITES_CONVERTER_PLUGIN_URL . 'assets/images/no-thumbnail.png';
        }
        
        // Check if already converted
        global $wpdb;
        $table_name = $wpdb->prefix . 'kenzysites_converted_templates';
        $is_converted = $wpdb->get_var(
            $wpdb->prepare("SELECT COUNT(*) FROM $table_name WHERE page_id = %d", $page_id)
        );
        
        return [
            'id' => $page_id,
            'title' => $page->post_title,
            'url' => get_permalink($page_id),
            'edit_url' => admin_url("post.php?post={$page_id}&action=edit"),
            'elementor_edit_url' => admin_url("post.php?post={$page_id}&action=elementor"),
            'thumbnail' => $thumbnail,
            'modified' => get_the_modified_date('c', $page_id),
            'status' => $page->post_status,
            'elementor_data_size' => strlen($elementor_data),
            'analysis' => $analysis,
            'is_converted' => $is_converted > 0,
            'suggested_type' => $this->suggest_landing_page_type($analysis),
            'conversion_score' => $this->calculate_conversion_score($analysis)
        ];
    }
    
    /**
     * Analyze page structure from Elementor data
     */
    private function analyze_page_structure($elements) {
        $analysis = [
            'sections' => 0,
            'columns' => 0,
            'widgets' => [],
            'widget_count' => 0,
            'has_hero' => false,
            'has_form' => false,
            'has_testimonials' => false,
            'has_pricing' => false,
            'has_gallery' => false,
            'has_video' => false,
            'cta_buttons' => 0,
            'text_elements' => 0,
            'image_elements' => 0,
            'dynamic_content' => [],
            'complexity_score' => 0
        ];
        
        $this->analyze_elements($elements, $analysis);
        
        // Calculate complexity score
        $analysis['complexity_score'] = $this->calculate_complexity_score($analysis);
        
        return $analysis;
    }
    
    /**
     * Recursively analyze Elementor elements
     */
    private function analyze_elements($elements, &$analysis) {
        foreach ($elements as $element) {
            $element_type = $element['elType'] ?? '';
            $widget_type = $element['widgetType'] ?? '';
            
            switch ($element_type) {
                case 'section':
                    $analysis['sections']++;
                    break;
                    
                case 'column':
                    $analysis['columns']++;
                    break;
                    
                case 'widget':
                    $analysis['widget_count']++;
                    
                    // Track widget types
                    if (!isset($analysis['widgets'][$widget_type])) {
                        $analysis['widgets'][$widget_type] = 0;
                    }
                    $analysis['widgets'][$widget_type]++;
                    
                    // Analyze specific widget types
                    $this->analyze_widget($widget_type, $element, $analysis);
                    break;
            }
            
            // Recursively analyze child elements
            if (!empty($element['elements'])) {
                $this->analyze_elements($element['elements'], $analysis);
            }
        }
    }
    
    /**
     * Analyze specific widget types
     */
    private function analyze_widget($widget_type, $element, &$analysis) {
        $settings = $element['settings'] ?? [];
        
        switch ($widget_type) {
            case 'heading':
                $text = $settings['title'] ?? '';
                if (strlen($text) > 50) {
                    $analysis['has_hero'] = true;
                }
                $analysis['text_elements']++;
                
                // Check for dynamic content
                if (strpos($text, '{{') !== false || strpos($text, '[') !== false) {
                    $analysis['dynamic_content'][] = [
                        'type' => 'heading',
                        'content' => $text
                    ];
                }
                break;
                
            case 'text-editor':
            case 'textpath':
                $analysis['text_elements']++;
                break;
                
            case 'button':
                $analysis['cta_buttons']++;
                
                $button_text = $settings['text'] ?? '';
                if (strpos($button_text, '{{') !== false) {
                    $analysis['dynamic_content'][] = [
                        'type' => 'button',
                        'content' => $button_text
                    ];
                }
                break;
                
            case 'image':
                $analysis['image_elements']++;
                
                $image_url = $settings['image']['url'] ?? '';
                if (strpos($image_url, '{{') !== false) {
                    $analysis['dynamic_content'][] = [
                        'type' => 'image',
                        'content' => $image_url
                    ];
                }
                break;
                
            case 'form':
            case 'contact-form-7':
            case 'wpforms':
                $analysis['has_form'] = true;
                break;
                
            case 'testimonial':
            case 'reviews':
                $analysis['has_testimonials'] = true;
                break;
                
            case 'price-list':
            case 'price-table':
            case 'pricing':
                $analysis['has_pricing'] = true;
                break;
                
            case 'gallery':
            case 'image-gallery':
                $analysis['has_gallery'] = true;
                break;
                
            case 'video':
            case 'youtube':
            case 'vimeo':
                $analysis['has_video'] = true;
                break;
        }
    }
    
    /**
     * Calculate complexity score (0-100)
     */
    private function calculate_complexity_score($analysis) {
        $score = 0;
        
        // Base structure points
        $score += min($analysis['sections'] * 5, 25);
        $score += min($analysis['widget_count'] * 2, 30);
        $score += min(count($analysis['widgets']) * 3, 15);
        
        // Feature bonus points
        if ($analysis['has_hero']) $score += 5;
        if ($analysis['has_form']) $score += 5;
        if ($analysis['has_testimonials']) $score += 5;
        if ($analysis['has_pricing']) $score += 5;
        if ($analysis['has_gallery']) $score += 3;
        if ($analysis['has_video']) $score += 3;
        
        // Dynamic content bonus
        $score += min(count($analysis['dynamic_content']) * 2, 10);
        
        return min($score, 100);
    }
    
    /**
     * Suggest landing page type based on analysis
     */
    private function suggest_landing_page_type($analysis) {
        // Lead generation indicators
        if ($analysis['has_form'] && $analysis['cta_buttons'] >= 2) {
            return 'lead_generation';
        }
        
        // Service showcase indicators
        if ($analysis['has_testimonials'] && $analysis['widget_count'] > 10) {
            return 'service_showcase';
        }
        
        // Product launch indicators  
        if ($analysis['has_pricing'] && $analysis['has_gallery']) {
            return 'product_launch';
        }
        
        // Event promotion indicators
        if ($analysis['has_video'] && $analysis['cta_buttons'] >= 1) {
            return 'event_promotion';
        }
        
        // Webinar indicators
        if ($analysis['has_video'] && $analysis['has_form']) {
            return 'webinar';
        }
        
        // Coming soon indicators
        if ($analysis['widget_count'] < 5 && $analysis['has_form']) {
            return 'coming_soon';
        }
        
        // Thank you indicators
        if ($analysis['widget_count'] < 3 && $analysis['text_elements'] > 0) {
            return 'thank_you';
        }
        
        // Download indicators
        if ($analysis['cta_buttons'] >= 1 && $analysis['has_form']) {
            return 'download';
        }
        
        // Newsletter indicators
        if ($analysis['has_form'] && $analysis['widget_count'] < 8) {
            return 'newsletter';
        }
        
        // Default to service showcase
        return 'service_showcase';
    }
    
    /**
     * Calculate conversion score based on best practices
     */
    private function calculate_conversion_score($analysis) {
        $score = 0;
        
        // Hero section (20 points)
        if ($analysis['has_hero']) {
            $score += 20;
        }
        
        // Clear CTA (25 points)
        if ($analysis['cta_buttons'] >= 1) {
            $score += 15;
            if ($analysis['cta_buttons'] >= 2) {
                $score += 10; // Multiple CTAs bonus
            }
        }
        
        // Lead capture form (20 points)
        if ($analysis['has_form']) {
            $score += 20;
        }
        
        // Social proof (15 points)
        if ($analysis['has_testimonials']) {
            $score += 15;
        }
        
        // Visual elements (10 points)
        if ($analysis['image_elements'] >= 2) {
            $score += 5;
        }
        if ($analysis['has_video']) {
            $score += 5;
        }
        
        // Content balance (10 points)
        $text_to_visual_ratio = $analysis['image_elements'] > 0 ? 
            $analysis['text_elements'] / $analysis['image_elements'] : 
            $analysis['text_elements'];
            
        if ($text_to_visual_ratio >= 1 && $text_to_visual_ratio <= 3) {
            $score += 10;
        }
        
        return min($score, 100);
    }
    
    /**
     * Get Elementor raw data for a page
     */
    public function get_elementor_data($page_id) {
        return get_post_meta($page_id, '_elementor_data', true);
    }
    
    /**
     * Get Elementor settings for a page
     */
    public function get_elementor_settings($page_id) {
        return get_post_meta($page_id, '_elementor_page_settings', true);
    }
    
    /**
     * Extract dynamic content candidates from page
     */
    public function extract_dynamic_content($page_id) {
        $elementor_data = $this->get_elementor_data($page_id);
        if (empty($elementor_data)) {
            return [];
        }
        
        $elements = json_decode($elementor_data, true);
        if (!is_array($elements)) {
            return [];
        }
        
        $dynamic_content = [];
        $this->find_dynamic_content($elements, $dynamic_content);
        
        return $dynamic_content;
    }
    
    /**
     * Recursively find dynamic content
     */
    private function find_dynamic_content($elements, &$dynamic_content) {
        foreach ($elements as $element) {
            $widget_type = $element['widgetType'] ?? '';
            $settings = $element['settings'] ?? [];
            
            // Look for common dynamic content patterns
            foreach ($settings as $key => $value) {
                if (is_string($value) && $this->is_likely_dynamic_content($value)) {
                    $dynamic_content[] = [
                        'widget_type' => $widget_type,
                        'setting_key' => $key,
                        'content' => $value,
                        'acf_field_suggestion' => $this->suggest_acf_field_type($key, $value, $widget_type)
                    ];
                }
            }
            
            // Recursively check child elements
            if (!empty($element['elements'])) {
                $this->find_dynamic_content($element['elements'], $dynamic_content);
            }
        }
    }
    
    /**
     * Check if content is likely dynamic
     */
    private function is_likely_dynamic_content($content) {
        // Check for placeholder patterns
        $patterns = [
            '/\{\{.*\}\}/',           // {{placeholder}}
            '/\[.*\]/',               // [shortcode]
            '/\{.*\}/',               // {variable}
            '/Your Company Name/i',    // Common placeholder text
            '/Lorem ipsum/i',         // Lorem ipsum text
            '/Sample.*Text/i',        // Sample text
            '/Example.*Company/i',    // Example company
            '/placeholder/i',         // Direct placeholder mentions
        ];
        
        foreach ($patterns as $pattern) {
            if (preg_match($pattern, $content)) {
                return true;
            }
        }
        
        // Check for generic business terms that are likely placeholders
        $generic_terms = [
            'your business', 'our company', 'company name', 'business name',
            'your service', 'our service', 'your product', 'contact us',
            'phone number', 'email address', 'your address'
        ];
        
        $content_lower = strtolower($content);
        foreach ($generic_terms as $term) {
            if (strpos($content_lower, $term) !== false) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Suggest ACF field type based on content and context
     */
    private function suggest_acf_field_type($setting_key, $content, $widget_type) {
        // URL fields
        if (filter_var($content, FILTER_VALIDATE_URL) || 
            in_array($setting_key, ['url', 'link', 'href'])) {
            return 'url';
        }
        
        // Email fields
        if (filter_var($content, FILTER_VALIDATE_EMAIL) || 
            strpos($setting_key, 'email') !== false) {
            return 'email';
        }
        
        // Phone fields
        if (preg_match('/\(?\d{2,3}\)?[-\s]?\d{4,5}[-\s]?\d{4}/', $content) ||
            strpos($setting_key, 'phone') !== false) {
            return 'text'; // ACF doesn't have phone type, use text
        }
        
        // Image fields
        if ($widget_type === 'image' || 
            strpos($setting_key, 'image') !== false ||
            preg_match('/\.(jpg|jpeg|png|gif|svg)$/i', $content)) {
            return 'image';
        }
        
        // Color fields
        if (preg_match('/^#[a-f0-9]{6}$/i', $content) ||
            strpos($setting_key, 'color') !== false) {
            return 'color_picker';
        }
        
        // Textarea for long content
        if (strlen($content) > 100 || 
            strpos($content, "\n") !== false ||
            in_array($setting_key, ['description', 'content', 'text'])) {
            return 'textarea';
        }
        
        // Number fields
        if (is_numeric($content) && !preg_match('/^\d{4,}$/', $content)) {
            return 'number';
        }
        
        // Default to text
        return 'text';
    }
}