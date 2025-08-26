"""
WordPress Generator Service
Generates actual WordPress sites with Elementor pages
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid
import base64

logger = logging.getLogger(__name__)

class WordPressGenerator:
    """
    Service for generating WordPress sites with Elementor
    """
    
    def __init__(self):
        self.elementor_version = "3.18.0"
        self.wordpress_version = "6.4"
        
    def generate_wordpress_site(
        self,
        site_data: Dict[str, Any],
        template_data: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a complete WordPress site
        
        Args:
            site_data: Business and site information
            template_data: Template structure and content
            personalization_data: Personalized content and settings
            
        Returns:
            Generated WordPress site configuration
        """
        
        logger.info(f"Generating WordPress site for {site_data.get('business_name')}")
        
        # Generate site structure
        site_structure = {
            "site_id": f"wp_{uuid.uuid4().hex[:8]}",
            "wordpress_config": self._generate_wordpress_config(site_data),
            "theme_config": self._generate_theme_config(site_data, personalization_data),
            "pages": self._generate_pages(template_data, personalization_data),
            "menus": self._generate_menus(template_data),
            "widgets": self._generate_widgets(site_data, personalization_data),
            "plugins": self._generate_plugin_configs(site_data),
            "elementor_data": self._generate_elementor_data(template_data, personalization_data),
            "custom_css": self._generate_custom_css(personalization_data),
            "functions_php": self._generate_functions_php(site_data)
        }
        
        return site_structure
    
    def _generate_wordpress_config(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate WordPress configuration"""
        
        return {
            "site_title": site_data.get("business_name", "KenzySites"),
            "tagline": site_data.get("business_description", ""),
            "admin_email": site_data.get("email", "admin@kenzysites.com"),
            "timezone_string": "America/Sao_Paulo",
            "date_format": "d/m/Y",
            "time_format": "H:i",
            "start_of_week": "0",
            "default_language": "pt_BR",
            "permalink_structure": "/%postname%/",
            "users_can_register": False,
            "default_role": "subscriber",
            "blog_public": True,
            "show_on_front": "page",
            "page_on_front": "home",
            "posts_per_page": 10,
            "default_comment_status": "closed",
            "default_ping_status": "closed",
            "thumbnail_size_w": 150,
            "thumbnail_size_h": 150,
            "medium_size_w": 300,
            "medium_size_h": 300,
            "large_size_w": 1024,
            "large_size_h": 1024
        }
    
    def _generate_theme_config(
        self,
        site_data: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate theme configuration"""
        
        colors = personalization_data.get("color_scheme", {})
        typography = personalization_data.get("typography", {})
        
        return {
            "theme_name": "Astra",
            "theme_mods": {
                # Site Identity
                "custom_logo": None,  # Will be set if logo uploaded
                "site_icon": None,  # Favicon
                
                # Colors
                "ast-global-color-0": colors.get("primary", "#0274be"),
                "ast-global-color-1": colors.get("secondary", "#3a3a3a"),
                "ast-global-color-2": colors.get("text", "#3a3a3a"),
                "ast-global-color-3": colors.get("accent", "#0274be"),
                "ast-global-color-4": colors.get("background", "#f5f5f5"),
                "ast-global-color-5": colors.get("white", "#ffffff"),
                "ast-global-color-6": colors.get("black", "#000000"),
                "ast-global-color-7": colors.get("gray", "#666666"),
                "ast-global-color-8": colors.get("light", "#f0f0f0"),
                
                # Typography
                "body-font-family": typography.get("body_font", "'Open Sans', sans-serif"),
                "body-font-weight": typography.get("body_weight", "400"),
                "body-font-size": {
                    "desktop": typography.get("body_size", 16),
                    "tablet": 15,
                    "mobile": 14,
                    "desktop-unit": "px",
                    "tablet-unit": "px",
                    "mobile-unit": "px"
                },
                "headings-font-family": typography.get("heading_font", "'Montserrat', sans-serif"),
                "headings-font-weight": typography.get("heading_weight", "700"),
                
                # Layout
                "site-content-width": 1200,
                "site-sidebar-width": 30,
                "site-sidebar-layout": "no-sidebar",
                
                # Header
                "header-layouts": "header-main-layout-1",
                "header-color-site-title": colors.get("primary", "#0274be"),
                "header-color-site-tagline": colors.get("text", "#3a3a3a"),
                
                # Footer
                "footer-copyright-color": {
                    "desktop": colors.get("text", "#3a3a3a"),
                    "tablet": "",
                    "mobile": ""
                },
                
                # Brazilian Features
                "ast-whatsapp-enabled": site_data.get("whatsapp", False),
                "ast-whatsapp-number": site_data.get("whatsapp_number", ""),
                "ast-pix-enabled": site_data.get("accept_pix", False),
                "ast-pix-key": site_data.get("pix_key", "")
            }
        }
    
    def _generate_pages(
        self,
        template_data: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate WordPress pages"""
        
        pages = []
        placeholder_values = personalization_data.get("placeholder_values", {})
        
        for page_data in template_data.get("pages", []):
            page = {
                "post_title": self._replace_placeholders(
                    page_data.get("title", ""),
                    placeholder_values
                ),
                "post_name": page_data.get("slug", "page"),
                "post_content": "",  # Content will be in Elementor
                "post_status": "publish",
                "post_type": "page",
                "menu_order": page_data.get("order", 0),
                "meta_input": {
                    "_elementor_edit_mode": "builder",
                    "_elementor_template_type": "wp-page",
                    "_elementor_version": self.elementor_version,
                    "_elementor_page_settings": json.dumps({
                        "hide_title": "yes" if page_data.get("hide_title", True) else "no",
                        "layout": "elementor_canvas",
                        "page_title": page_data.get("seo_title", ""),
                        "page_description": page_data.get("seo_description", "")
                    }),
                    "_elementor_data": json.dumps(
                        self._generate_elementor_page_data(page_data, personalization_data)
                    )
                }
            }
            
            pages.append(page)
        
        return pages
    
    def _generate_elementor_page_data(
        self,
        page_data: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate Elementor page data structure"""
        
        elementor_sections = []
        placeholder_values = personalization_data.get("placeholder_values", {})
        
        for section in page_data.get("sections", []):
            elementor_section = {
                "id": self._generate_element_id(),
                "elType": "section",
                "settings": {
                    "layout": section.get("layout", "boxed"),
                    "gap": "default",
                    "height": section.get("height", "default"),
                    "content_width": {"unit": "%", "size": 100},
                    "background_background": section.get("background_type", "classic"),
                },
                "elements": []
            }
            
            # Add background color if specified
            if section.get("background_color"):
                elementor_section["settings"]["background_color"] = section["background_color"]
            
            # Add columns
            for column in section.get("columns", [{"width": 100}]):
                elementor_column = {
                    "id": self._generate_element_id(),
                    "elType": "column",
                    "settings": {
                        "_column_size": column.get("width", 100),
                        "_inline_size": None
                    },
                    "elements": []
                }
                
                # Add widgets to column
                for widget in column.get("widgets", []):
                    elementor_widget = self._create_elementor_widget(
                        widget,
                        placeholder_values
                    )
                    elementor_column["elements"].append(elementor_widget)
                
                elementor_section["elements"].append(elementor_column)
            
            elementor_sections.append(elementor_section)
        
        return elementor_sections
    
    def _create_elementor_widget(
        self,
        widget_data: Dict[str, Any],
        placeholder_values: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create an Elementor widget"""
        
        widget_type = widget_data.get("type", "text-editor")
        
        widget = {
            "id": self._generate_element_id(),
            "elType": "widget",
            "widgetType": widget_type,
            "settings": {}
        }
        
        if widget_type == "heading":
            widget["settings"] = {
                "title": self._replace_placeholders(
                    widget_data.get("content", ""),
                    placeholder_values
                ),
                "header_size": widget_data.get("size", "h2"),
                "align": widget_data.get("align", "left"),
                "title_color": widget_data.get("color", "")
            }
            
        elif widget_type == "text-editor":
            widget["settings"] = {
                "editor": self._replace_placeholders(
                    widget_data.get("content", ""),
                    placeholder_values
                ),
                "align": widget_data.get("align", "left"),
                "text_color": widget_data.get("color", "")
            }
            
        elif widget_type == "button":
            widget["settings"] = {
                "text": self._replace_placeholders(
                    widget_data.get("text", "Click Here"),
                    placeholder_values
                ),
                "link": {
                    "url": widget_data.get("link", "#"),
                    "is_external": widget_data.get("external", False),
                    "nofollow": widget_data.get("nofollow", False)
                },
                "align": widget_data.get("align", "left"),
                "size": widget_data.get("size", "sm"),
                "button_type": widget_data.get("style", "primary")
            }
            
        elif widget_type == "image":
            widget["settings"] = {
                "image": {
                    "url": widget_data.get("url", ""),
                    "id": widget_data.get("id", ""),
                    "alt": self._replace_placeholders(
                        widget_data.get("alt", ""),
                        placeholder_values
                    )
                },
                "image_size": widget_data.get("size", "full"),
                "align": widget_data.get("align", "center"),
                "link_to": widget_data.get("link_to", "none")
            }
            
        elif widget_type == "icon-list":
            items = []
            for item in widget_data.get("items", []):
                items.append({
                    "text": self._replace_placeholders(item.get("text", ""), placeholder_values),
                    "selected_icon": {
                        "value": item.get("icon", "fas fa-check"),
                        "library": "fa-solid"
                    }
                })
            
            widget["settings"] = {
                "icon_list": items,
                "space_between": {"unit": "px", "size": 10},
                "icon_color": widget_data.get("icon_color", ""),
                "text_color": widget_data.get("text_color", "")
            }
            
        elif widget_type == "google_maps":
            widget["settings"] = {
                "address": self._replace_placeholders(
                    widget_data.get("address", ""),
                    placeholder_values
                ),
                "zoom": {"unit": "px", "size": widget_data.get("zoom", 15)},
                "height": {"unit": "px", "size": widget_data.get("height", 400)},
                "view": widget_data.get("view", "roadmap")
            }
            
        elif widget_type == "form":
            # Contact form
            widget["widgetType"] = "form"
            widget["settings"] = {
                "form_name": widget_data.get("name", "Contact Form"),
                "form_fields": self._generate_form_fields(widget_data.get("fields", [])),
                "button_text": widget_data.get("button_text", "Enviar"),
                "email_to": placeholder_values.get("{{email}}", "admin@site.com"),
                "email_subject": f"Contato de {placeholder_values.get('{{business_name}}', 'Site')}"
            }
            
        elif widget_type == "whatsapp-button":
            # Brazilian WhatsApp button
            widget["widgetType"] = "html"
            widget["settings"] = {
                "html": self._generate_whatsapp_button_html(
                    placeholder_values.get("{{whatsapp}}", ""),
                    widget_data.get("message", "Olá! Gostaria de mais informações.")
                )
            }
            
        elif widget_type == "pix-payment":
            # Brazilian PIX payment widget
            widget["widgetType"] = "html"
            widget["settings"] = {
                "html": self._generate_pix_widget_html(
                    placeholder_values.get("{{pix_key}}", ""),
                    widget_data.get("amount", 0)
                )
            }
        
        return widget
    
    def _generate_menus(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate WordPress menus"""
        
        menus = []
        
        # Main navigation menu
        main_menu = {
            "name": "Menu Principal",
            "slug": "main-menu",
            "items": []
        }
        
        for page in template_data.get("pages", []):
            if page.get("in_menu", True):
                main_menu["items"].append({
                    "title": page.get("title", ""),
                    "url": f"/{page.get('slug', '')}",
                    "type": "page",
                    "order": page.get("menu_order", 0)
                })
        
        menus.append(main_menu)
        
        # Footer menu
        footer_menu = {
            "name": "Menu Rodapé",
            "slug": "footer-menu",
            "items": [
                {"title": "Política de Privacidade", "url": "/privacidade", "type": "custom"},
                {"title": "Termos de Uso", "url": "/termos", "type": "custom"},
                {"title": "LGPD", "url": "/lgpd", "type": "custom"}
            ]
        }
        
        menus.append(footer_menu)
        
        return menus
    
    def _generate_widgets(
        self,
        site_data: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate WordPress widgets"""
        
        widgets = []
        placeholder_values = personalization_data.get("placeholder_values", {})
        
        # Business info widget
        widgets.append({
            "id": "business_info",
            "type": "text",
            "title": "Sobre Nós",
            "content": self._replace_placeholders(
                placeholder_values.get("{{about_text}}", ""),
                placeholder_values
            )
        })
        
        # Contact widget
        contact_html = f"""
        <ul class="contact-info">
            <li><i class="fa fa-phone"></i> {placeholder_values.get('{{phone}}', '')}</li>
            <li><i class="fa fa-envelope"></i> {placeholder_values.get('{{email}}', '')}</li>
            <li><i class="fa fa-map-marker"></i> {placeholder_values.get('{{address}}', '')}</li>
        </ul>
        """
        
        widgets.append({
            "id": "contact_info",
            "type": "html",
            "title": "Contato",
            "content": contact_html
        })
        
        # WhatsApp widget if enabled
        if site_data.get("whatsapp"):
            widgets.append({
                "id": "whatsapp_widget",
                "type": "html",
                "title": "WhatsApp",
                "content": self._generate_whatsapp_widget_html(
                    placeholder_values.get("{{whatsapp}}", "")
                )
            })
        
        # Social media widget
        social_links = personalization_data.get("social_links", {})
        if social_links:
            social_html = '<div class="social-links">'
            for platform, url in social_links.items():
                social_html += f'<a href="{url}" target="_blank"><i class="fab fa-{platform}"></i></a>'
            social_html += '</div>'
            
            widgets.append({
                "id": "social_media",
                "type": "html",
                "title": "Redes Sociais",
                "content": social_html
            })
        
        return widgets
    
    def _generate_plugin_configs(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plugin configurations"""
        
        plugins = {
            "elementor": {
                "active": True,
                "settings": {
                    "cpt_support": ["page", "post"],
                    "disable_color_schemes": False,
                    "disable_typography_schemes": False,
                    "viewport_lg": 1025,
                    "viewport_md": 768,
                    "global_image_lightbox": True,
                    "container_width": 1140
                }
            },
            "advanced-custom-fields": {
                "active": True,
                "field_groups": []
            },
            "yoast-seo": {
                "active": True,
                "settings": {
                    "website_name": site_data.get("business_name", ""),
                    "company_or_person": "company",
                    "company_name": site_data.get("business_name", ""),
                    "company_logo": "",
                    "enable_xml_sitemap": True,
                    "enable_breadcrumbs": True
                }
            }
        }
        
        # Brazilian specific plugins
        if site_data.get("whatsapp"):
            plugins["wp-whatsapp-chat"] = {
                "active": True,
                "settings": {
                    "whatsapp_number": site_data.get("whatsapp_number", ""),
                    "default_message": "Olá! Vi seu site e gostaria de mais informações.",
                    "button_text": "Fale Conosco",
                    "position": "bottom-right"
                }
            }
        
        if site_data.get("accept_pix"):
            plugins["woo-pix-gateway"] = {
                "active": False,  # Only if WooCommerce is needed
                "settings": {
                    "pix_key": site_data.get("pix_key", ""),
                    "pix_key_type": "email"  # or cpf, cnpj, phone, random
                }
            }
        
        # LGPD compliance plugin
        plugins["lgpd-compliance-brazil"] = {
            "active": True,
            "settings": {
                "cookie_notice": True,
                "privacy_policy_page": "/privacidade",
                "data_retention_days": 365
            }
        }
        
        return plugins
    
    def _generate_elementor_data(
        self,
        template_data: Dict[str, Any],
        personalization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Elementor global data"""
        
        colors = personalization_data.get("color_scheme", {})
        typography = personalization_data.get("typography", {})
        
        return {
            "system_colors": [
                {
                    "_id": "primary",
                    "title": "Primary",
                    "color": colors.get("primary", "#0274be")
                },
                {
                    "_id": "secondary",
                    "title": "Secondary",
                    "color": colors.get("secondary", "#3a3a3a")
                },
                {
                    "_id": "text",
                    "title": "Text",
                    "color": colors.get("text", "#333333")
                },
                {
                    "_id": "accent",
                    "title": "Accent",
                    "color": colors.get("accent", "#61ce70")
                }
            ],
            "system_typography": [
                {
                    "_id": "primary",
                    "title": "Primary",
                    "typography_typography": "custom",
                    "typography_font_family": typography.get("heading_font", "Montserrat"),
                    "typography_font_weight": typography.get("heading_weight", "700")
                },
                {
                    "_id": "secondary",
                    "title": "Secondary",
                    "typography_typography": "custom",
                    "typography_font_family": typography.get("body_font", "Open Sans"),
                    "typography_font_weight": typography.get("body_weight", "400")
                }
            ],
            "kit_settings": {
                "container_width": {
                    "unit": "px",
                    "size": 1140,
                    "sizes": []
                },
                "space_between_widgets": {
                    "unit": "px",
                    "size": 20,
                    "sizes": []
                }
            }
        }
    
    def _generate_custom_css(self, personalization_data: Dict[str, Any]) -> str:
        """Generate custom CSS"""
        
        colors = personalization_data.get("color_scheme", {})
        
        css = f"""
        /* KenzySites Custom Styles */
        :root {{
            --kenzysites-primary: {colors.get('primary', '#0274be')};
            --kenzysites-secondary: {colors.get('secondary', '#3a3a3a')};
            --kenzysites-accent: {colors.get('accent', '#61ce70')};
            --kenzysites-text: {colors.get('text', '#333333')};
            --kenzysites-bg: {colors.get('background', '#ffffff')};
        }}
        
        /* WhatsApp Button */
        .whatsapp-float {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #25D366;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 9999;
            transition: transform 0.3s;
        }}
        
        .whatsapp-float:hover {{
            transform: scale(1.1);
        }}
        
        /* LGPD Banner */
        .lgpd-banner {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #333;
            color: white;
            padding: 20px;
            text-align: center;
            z-index: 9998;
        }}
        
        .lgpd-banner button {{
            background: var(--kenzysites-primary);
            color: white;
            border: none;
            padding: 10px 20px;
            margin-left: 20px;
            border-radius: 5px;
            cursor: pointer;
        }}
        
        /* Brazilian Features */
        .pix-payment {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .pix-qrcode {{
            margin: 20px auto;
            max-width: 300px;
        }}
        """
        
        return css
    
    def _generate_functions_php(self, site_data: Dict[str, Any]) -> str:
        """Generate functions.php content"""
        
        php_code = """<?php
/**
 * KenzySites Theme Functions
 * Generated for: """ + site_data.get('business_name', 'Site') + """
 */

// Theme Setup
function kenzysites_theme_setup() {
    // Add theme support
    add_theme_support('post-thumbnails');
    add_theme_support('title-tag');
    add_theme_support('custom-logo');
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
    
    // Register menus
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'kenzysites'),
        'footer' => __('Footer Menu', 'kenzysites')
    ));
}
add_action('after_setup_theme', 'kenzysites_theme_setup');

// Brazilian Features
"""
        
        if site_data.get("whatsapp"):
            php_code += """
// WhatsApp Floating Button
function kenzysites_whatsapp_button() {
    $whatsapp = '""" + site_data.get('whatsapp_number', '') + """';
    if ($whatsapp) {
        echo '<a href="https://wa.me/55' . preg_replace('/\D/', '', $whatsapp) . '" class="whatsapp-float" target="_blank">
                <i class="fab fa-whatsapp"></i>
              </a>';
    }
}
add_action('wp_footer', 'kenzysites_whatsapp_button');
"""
        
        if site_data.get("accept_pix"):
            php_code += """
// PIX Payment Integration
function kenzysites_pix_shortcode($atts) {
    $atts = shortcode_atts(array(
        'amount' => '0',
        'description' => 'Pagamento'
    ), $atts);
    
    $pix_key = '""" + site_data.get('pix_key', '') + """';
    
    ob_start();
    ?>
    <div class="pix-payment">
        <h3>Pagamento via PIX</h3>
        <p>Chave PIX: <strong><?php echo esc_html($pix_key); ?></strong></p>
        <div class="pix-qrcode" data-pix="<?php echo esc_attr($pix_key); ?>" data-amount="<?php echo esc_attr($atts['amount']); ?>">
            <!-- QR Code will be generated here -->
        </div>
        <p>Valor: R$ <?php echo number_format($atts['amount'], 2, ',', '.'); ?></p>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('pix_payment', 'kenzysites_pix_shortcode');
"""
        
        php_code += """
// LGPD Compliance
function kenzysites_lgpd_notice() {
    if (!isset($_COOKIE['lgpd_accepted'])) {
        echo '<div class="lgpd-banner" id="lgpd-banner">
                <p>Este site usa cookies para melhorar sua experiência. Ao continuar navegando, você concorda com nossa 
                   <a href="/privacidade" style="color: white; text-decoration: underline;">Política de Privacidade</a>.</p>
                <button onclick="acceptLGPD()">Aceitar e Continuar</button>
              </div>
              <script>
              function acceptLGPD() {
                  document.cookie = "lgpd_accepted=1; max-age=31536000; path=/";
                  document.getElementById("lgpd-banner").style.display = "none";
              }
              </script>';
    }
}
add_action('wp_footer', 'kenzysites_lgpd_notice');

// Custom Scripts
function kenzysites_enqueue_scripts() {
    wp_enqueue_style('font-awesome', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    // Google Fonts
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Open+Sans:wght@400;600&display=swap');
}
add_action('wp_enqueue_scripts', 'kenzysites_enqueue_scripts');

// Security Headers
function kenzysites_security_headers() {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');
}
add_action('send_headers', 'kenzysites_security_headers');

// Disable XML-RPC for security
add_filter('xmlrpc_enabled', '__return_false');

// Remove WordPress version
remove_action('wp_head', 'wp_generator');

?>"""
        
        return php_code
    
    def _generate_whatsapp_button_html(self, whatsapp_number: str, message: str = "") -> str:
        """Generate WhatsApp button HTML"""
        
        # Clean number (remove non-digits)
        clean_number = ''.join(filter(str.isdigit, whatsapp_number))
        
        # Encode message for URL
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        return f"""
        <a href="https://wa.me/55{clean_number}?text={encoded_message}" 
           target="_blank" 
           class="elementor-button elementor-button-success elementor-size-md">
            <span class="elementor-button-content-wrapper">
                <span class="elementor-button-icon elementor-align-icon-left">
                    <i class="fab fa-whatsapp"></i>
                </span>
                <span class="elementor-button-text">Fale Conosco no WhatsApp</span>
            </span>
        </a>
        """
    
    def _generate_whatsapp_widget_html(self, whatsapp_number: str) -> str:
        """Generate WhatsApp widget HTML"""
        
        clean_number = ''.join(filter(str.isdigit, whatsapp_number))
        
        return f"""
        <div class="whatsapp-widget">
            <a href="https://wa.me/55{clean_number}" target="_blank" class="whatsapp-link">
                <i class="fab fa-whatsapp"></i> {whatsapp_number}
            </a>
        </div>
        """
    
    def _generate_pix_widget_html(self, pix_key: str, amount: float = 0) -> str:
        """Generate PIX payment widget HTML"""
        
        # In production, generate actual PIX QR code
        qr_code_data = self._generate_pix_qr_code(pix_key, amount)
        
        return f"""
        <div class="pix-payment-widget">
            <h4>Pagamento via PIX</h4>
            <div class="pix-info">
                <p><strong>Chave PIX:</strong></p>
                <div class="pix-key-display">
                    <code>{pix_key}</code>
                    <button onclick="copyToClipboard('{pix_key}')" class="copy-button">
                        <i class="far fa-copy"></i> Copiar
                    </button>
                </div>
            </div>
            <div class="pix-qrcode">
                <img src="data:image/png;base64,{qr_code_data}" alt="QR Code PIX" />
            </div>
            {f'<p class="pix-amount">Valor: R$ {amount:.2f}</p>' if amount > 0 else ''}
            <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(function() {{
                    alert('Chave PIX copiada!');
                }});
            }}
            </script>
        </div>
        """
    
    def _generate_pix_qr_code(self, pix_key: str, amount: float = 0) -> str:
        """Generate PIX QR Code (placeholder - implement with actual library)"""
        
        # In production, use a library like python-pix or qrcode to generate actual QR code
        # This is a placeholder that returns a base64 encoded 1x1 transparent PNG
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def _generate_form_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate form fields for Elementor form"""
        
        elementor_fields = []
        
        for field in fields:
            elementor_field = {
                "custom_id": field.get("id", ""),
                "field_label": field.get("label", ""),
                "field_type": field.get("type", "text"),
                "required": field.get("required", False),
                "width": field.get("width", "100"),
                "placeholder": field.get("placeholder", "")
            }
            
            if field.get("type") == "select" and field.get("options"):
                elementor_field["field_options"] = "\n".join(field["options"])
            
            elementor_fields.append(elementor_field)
        
        return elementor_fields
    
    def _replace_placeholders(self, text: str, placeholder_values: Dict[str, str]) -> str:
        """Replace placeholders in text"""
        
        if not text:
            return ""
        
        for placeholder, value in placeholder_values.items():
            text = text.replace(placeholder, value)
        
        return text
    
    def _generate_element_id(self) -> str:
        """Generate unique Elementor element ID"""
        
        import random
        import string
        
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# Create singleton instance
wordpress_generator = WordPressGenerator()