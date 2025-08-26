"""
Elementor to ACF Converter Service
Converts existing Elementor landing pages to ACF-enabled templates
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import asyncio

from app.models.template_models import ACFField, ACFFieldGroup, ACFFieldType

logger = logging.getLogger(__name__)

class ElementorToACFConverter:
    """
    Service to convert Elementor landing pages to ACF-enabled templates
    """
    
    def __init__(self):
        self.widget_acf_mappings = self._initialize_widget_mappings()
        self.industry_specific_fields = self._initialize_industry_fields()
        self.common_dynamic_elements = self._initialize_common_elements()
    
    def _initialize_widget_mappings(self) -> Dict[str, Dict]:
        """Initialize mappings between Elementor widgets and ACF fields"""
        return {
            "heading": {
                "acf_type": ACFFieldType.TEXT,
                "priority": "high",
                "common_fields": ["business_name", "hero_title", "section_title"]
            },
            "text-editor": {
                "acf_type": ACFFieldType.TEXTAREA,
                "priority": "high", 
                "common_fields": ["business_description", "content_block", "about_text"]
            },
            "image": {
                "acf_type": ACFFieldType.IMAGE,
                "priority": "medium",
                "common_fields": ["hero_image", "logo", "feature_image"]
            },
            "button": {
                "acf_type": "group",
                "priority": "high",
                "fields": [
                    {"name": "text", "type": ACFFieldType.TEXT},
                    {"name": "url", "type": ACFFieldType.URL},
                    {"name": "style", "type": ACFFieldType.SELECT}
                ]
            },
            "icon-box": {
                "acf_type": "group",
                "priority": "medium",
                "fields": [
                    {"name": "icon", "type": ACFFieldType.TEXT},
                    {"name": "title", "type": ACFFieldType.TEXT},
                    {"name": "description", "type": ACFFieldType.TEXTAREA}
                ]
            },
            "testimonial": {
                "acf_type": "group",
                "priority": "medium",
                "fields": [
                    {"name": "content", "type": ACFFieldType.TEXTAREA},
                    {"name": "author", "type": ACFFieldType.TEXT},
                    {"name": "position", "type": ACFFieldType.TEXT},
                    {"name": "image", "type": ACFFieldType.IMAGE}
                ]
            },
            "form": {
                "acf_type": "group",
                "priority": "high",
                "fields": [
                    {"name": "form_title", "type": ACFFieldType.TEXT},
                    {"name": "submit_text", "type": ACFFieldType.TEXT},
                    {"name": "success_message", "type": ACFFieldType.TEXTAREA},
                    {"name": "redirect_url", "type": ACFFieldType.URL}
                ]
            },
            "price-list": {
                "acf_type": ACFFieldType.REPEATER,
                "priority": "high",
                "fields": [
                    {"name": "item_name", "type": ACFFieldType.TEXT},
                    {"name": "price", "type": ACFFieldType.TEXT},
                    {"name": "description", "type": ACFFieldType.TEXTAREA}
                ]
            },
            "countdown": {
                "acf_type": "group",
                "priority": "high",
                "fields": [
                    {"name": "end_date", "type": ACFFieldType.DATE_TIME_PICKER},
                    {"name": "title", "type": ACFFieldType.TEXT},
                    {"name": "expired_message", "type": ACFFieldType.TEXTAREA}
                ]
            }
        }
    
    def _initialize_industry_fields(self) -> Dict[str, List[Dict]]:
        """Initialize industry-specific field suggestions"""
        return {
            "captura_leads": [
                {"name": "lead_magnet_title", "type": ACFFieldType.TEXT, "label": "Título do Lead Magnet"},
                {"name": "benefits_list", "type": ACFFieldType.TEXTAREA, "label": "Lista de Benefícios"},
                {"name": "form_subtitle", "type": ACFFieldType.TEXT, "label": "Subtítulo do Formulário"}
            ],
            "vendas": [
                {"name": "product_name", "type": ACFFieldType.TEXT, "label": "Nome do Produto"},
                {"name": "price", "type": ACFFieldType.TEXT, "label": "Preço"},
                {"name": "discount_price", "type": ACFFieldType.TEXT, "label": "Preço com Desconto"},
                {"name": "guarantee", "type": ACFFieldType.TEXTAREA, "label": "Garantia"}
            ],
            "servicos": [
                {"name": "service_name", "type": ACFFieldType.TEXT, "label": "Nome do Serviço"},
                {"name": "service_description", "type": ACFFieldType.TEXTAREA, "label": "Descrição do Serviço"},
                {"name": "consultation_link", "type": ACFFieldType.URL, "label": "Link para Consulta"}
            ],
            "eventos": [
                {"name": "event_name", "type": ACFFieldType.TEXT, "label": "Nome do Evento"},
                {"name": "event_date", "type": ACFFieldType.DATE_TIME_PICKER, "label": "Data do Evento"},
                {"name": "location", "type": ACFFieldType.TEXT, "label": "Local"},
                {"name": "speaker_name", "type": ACFFieldType.TEXT, "label": "Nome do Palestrante"}
            ]
        }
    
    def _initialize_common_elements(self) -> List[Dict]:
        """Initialize common dynamic elements found in landing pages"""
        return [
            {"pattern": r"empresa|negócio|business", "field": "business_name", "type": ACFFieldType.TEXT},
            {"pattern": r"telefone|phone|contato", "field": "phone_number", "type": ACFFieldType.TEXT},
            {"pattern": r"whatsapp|wpp", "field": "whatsapp_number", "type": ACFFieldType.TEXT},
            {"pattern": r"email|e-mail", "field": "email_address", "type": ACFFieldType.EMAIL},
            {"pattern": r"endereço|address", "field": "business_address", "type": ACFFieldType.TEXTAREA},
            {"pattern": r"preço|price|valor", "field": "price", "type": ACFFieldType.TEXT},
            {"pattern": r"desconto|discount|promoção", "field": "discount_price", "type": ACFFieldType.TEXT}
        ]
    
    async def generate_elementor_page_from_template(
        self,
        business_data: Dict[str, Any],
        industry: str,
        page_type: str = "home"
    ) -> Dict[str, Any]:
        """
        Generate Elementor page from scratch using business data
        Inspired by ZipWP's instant generation approach
        """
        
        try:
            logger.info(f"🎨 Generating Elementor page for {business_data.get('business_name')} - {page_type}")
            
            # 1. Select appropriate template based on industry and page type
            template_structure = self._get_industry_template(industry, page_type)
            
            # 2. Generate dynamic content for placeholders
            dynamic_content = self._generate_page_content(business_data, industry, page_type)
            
            # 3. Create Elementor JSON structure
            elementor_data = self._build_elementor_structure(template_structure, dynamic_content)
            
            # 4. Generate ACF fields for the page
            acf_fields = self._generate_page_acf_fields(business_data, industry, page_type)
            
            # 5. Create integration code
            integration_code = self._generate_integration_code(elementor_data, acf_fields)
            
            return {
                "generation_id": f"gen_{page_type}_{uuid.uuid4().hex[:8]}",
                "page_type": page_type,
                "industry": industry,
                "elementor_data": elementor_data,
                "acf_fields": acf_fields,
                "integration_code": integration_code,
                "dynamic_content": dynamic_content,
                "template_structure": template_structure,
                "generation_time": datetime.now().isoformat(),
                "ready_to_deploy": True
            }
            
        except Exception as e:
            logger.error(f"Error generating Elementor page: {str(e)}")
            raise
    
    def _get_industry_template(self, industry: str, page_type: str) -> Dict[str, Any]:
        """Get template structure for industry and page type"""
        
        # Industry-specific templates
        industry_templates = {
            "restaurante": {
                "home": {
                    "sections": [
                        {
                            "type": "hero_banner",
                            "elements": ["restaurant_name", "hero_image", "tagline", "cta_button"]
                        },
                        {
                            "type": "featured_menu",
                            "elements": ["menu_title", "featured_items", "view_menu_button"]
                        },
                        {
                            "type": "delivery_info",
                            "elements": ["delivery_title", "delivery_areas", "order_button"]
                        },
                        {
                            "type": "contact_footer",
                            "elements": ["phone", "whatsapp", "address", "hours"]
                        }
                    ]
                }
            },
            "saude": {
                "home": {
                    "sections": [
                        {
                            "type": "hero_banner",
                            "elements": ["clinic_name", "doctor_name", "specialty", "appointment_button"]
                        },
                        {
                            "type": "services",
                            "elements": ["services_title", "service_grid", "benefits_list"]
                        },
                        {
                            "type": "credentials",
                            "elements": ["doctor_photo", "qualifications", "experience"]
                        },
                        {
                            "type": "appointment_booking",
                            "elements": ["booking_title", "contact_form", "emergency_info"]
                        }
                    ]
                }
            },
            "ecommerce": {
                "home": {
                    "sections": [
                        {
                            "type": "hero_banner",
                            "elements": ["store_name", "main_product", "special_offer", "shop_button"]
                        },
                        {
                            "type": "featured_products", 
                            "elements": ["products_title", "product_grid", "categories"]
                        },
                        {
                            "type": "benefits",
                            "elements": ["shipping_info", "payment_methods", "guarantee"]
                        },
                        {
                            "type": "testimonials",
                            "elements": ["reviews_title", "customer_reviews", "rating_display"]
                        }
                    ]
                }
            }
        }
        
        # Default generic template
        generic_template = {
            "home": {
                "sections": [
                    {
                        "type": "hero_banner",
                        "elements": ["business_name", "hero_image", "description", "cta_button"]
                    },
                    {
                        "type": "services",
                        "elements": ["services_title", "services_grid", "service_description"]
                    },
                    {
                        "type": "about",
                        "elements": ["about_title", "about_text", "team_photo"]
                    },
                    {
                        "type": "contact",
                        "elements": ["contact_title", "contact_form", "contact_info"]
                    }
                ]
            }
        }
        
        return industry_templates.get(industry, generic_template).get(page_type, generic_template["home"])
    
    def _generate_page_content(self, business_data: Dict[str, Any], industry: str, page_type: str) -> Dict[str, Any]:
        """Generate content for page based on business data"""
        
        business_name = business_data.get("business_name", "Sua Empresa")
        description = business_data.get("business_description", "")
        services = business_data.get("services", [])
        
        # Industry-specific content generation
        if industry == "restaurante":
            return {
                "restaurant_name": business_name,
                "tagline": "Sabor que você vai amar ❤️",
                "hero_image": "hero-restaurant.jpg",
                "menu_title": "Nosso Cardápio",
                "featured_items": ["Prato do Dia", "Especialidade da Casa", "Sobremesa Especial"],
                "delivery_title": "Delivery",
                "delivery_areas": "Entregamos em toda região central",
                "order_button": "Fazer Pedido",
                "phone": business_data.get("phone_number", "(11) 99999-9999"),
                "whatsapp": business_data.get("whatsapp_number", "(11) 99999-9999"),
                "address": business_data.get("address", "Rua Principal, 123"),
                "hours": "Seg-Dom: 11h às 23h"
            }
        
        elif industry == "saude":
            return {
                "clinic_name": business_name,
                "doctor_name": business_data.get("doctor_name", "Dr. Especialista"),
                "specialty": business_data.get("specialty", "Clínica Geral"),
                "appointment_button": "Agendar Consulta",
                "services_title": "Nossos Serviços",
                "service_grid": services[:4] if services else ["Consulta", "Exames", "Tratamentos"],
                "benefits_list": ["Atendimento personalizado", "Equipamentos modernos", "Profissionais qualificados"],
                "doctor_photo": "doctor-profile.jpg",
                "qualifications": "CRM 12345 - Especialista em " + business_data.get("specialty", "Medicina"),
                "experience": "Mais de 10 anos de experiência",
                "booking_title": "Agende sua Consulta",
                "emergency_info": "Emergências: " + business_data.get("phone_number", "(11) 99999-9999")
            }
        
        elif industry == "ecommerce":
            return {
                "store_name": business_name,
                "main_product": business_data.get("main_product", "Produtos de Qualidade"),
                "special_offer": "🔥 Oferta Especial: 20% OFF",
                "shop_button": "Ver Produtos",
                "products_title": "Produtos em Destaque",
                "product_grid": ["Produto 1", "Produto 2", "Produto 3", "Produto 4"],
                "categories": ["Categoria A", "Categoria B", "Categoria C"],
                "shipping_info": "📦 Frete Grátis acima de R$ 100",
                "payment_methods": "💳 PIX, Cartão, Boleto",
                "guarantee": "✅ 30 dias para troca",
                "reviews_title": "O que nossos clientes dizem",
                "customer_reviews": [
                    {"text": "Excelente qualidade!", "author": "Cliente Satisfeito"},
                    {"text": "Entrega rápida!", "author": "Comprador Feliz"}
                ],
                "rating_display": "⭐⭐⭐⭐⭐ 4.8/5"
            }
        
        # Generic content
        return {
            "business_name": business_name,
            "description": description,
            "hero_image": "hero-generic.jpg",
            "services_title": "Nossos Serviços",
            "services_grid": services[:4] if services else ["Serviço 1", "Serviço 2", "Serviço 3"],
            "service_description": "Oferecemos serviços de alta qualidade",
            "about_title": f"Sobre {business_name}",
            "about_text": description or f"{business_name} oferece soluções profissionais com qualidade e confiança.",
            "team_photo": "team.jpg",
            "contact_title": "Entre em Contato",
            "contact_info": {
                "phone": business_data.get("phone_number", "(11) 99999-9999"),
                "whatsapp": business_data.get("whatsapp_number", "(11) 99999-9999"),
                "email": business_data.get("email", "contato@empresa.com.br")
            }
        }
    
    def _build_elementor_structure(self, template_structure: Dict[str, Any], dynamic_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build complete Elementor JSON structure"""
        
        elementor_sections = []
        
        for section_config in template_structure.get("sections", []):
            section = self._create_elementor_section(section_config, dynamic_content)
            elementor_sections.append(section)
        
        return elementor_sections
    
    def _create_elementor_section(self, section_config: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
        """Create individual Elementor section"""
        
        section_type = section_config.get("type", "generic")
        elements = section_config.get("elements", [])
        
        # Base section structure
        section = {
            "id": f"section_{uuid.uuid4().hex[:8]}",
            "elType": "section",
            "settings": {
                "structure": "20",
                "content_width": "boxed"
            },
            "elements": []
        }
        
        # Create column
        column = {
            "id": f"column_{uuid.uuid4().hex[:8]}",
            "elType": "column",
            "settings": {
                "_column_size": 100,
                "_inline_size": None
            },
            "elements": []
        }
        
        # Add widgets based on section type and elements
        for element_name in elements:
            widget = self._create_elementor_widget(element_name, content.get(element_name))
            if widget:
                column["elements"].append(widget)
        
        section["elements"].append(column)
        return section
    
    def _create_elementor_widget(self, element_name: str, content_value: Any) -> Optional[Dict[str, Any]]:
        """Create Elementor widget based on element type"""
        
        if not content_value:
            return None
        
        widget_id = f"widget_{uuid.uuid4().hex[:8]}"
        
        # Text-based elements
        if any(term in element_name for term in ["title", "name", "tagline"]):
            return {
                "id": widget_id,
                "elType": "widget",
                "widgetType": "heading",
                "settings": {
                    "title": str(content_value),
                    "size": "h1" if "name" in element_name else "h2",
                    "align": "center" if "hero" in element_name else "left"
                }
            }
        
        # Description/text elements
        elif any(term in element_name for term in ["description", "text", "info"]):
            return {
                "id": widget_id,
                "elType": "widget", 
                "widgetType": "text-editor",
                "settings": {
                    "editor": str(content_value),
                    "align": "left"
                }
            }
        
        # Button elements
        elif "button" in element_name:
            return {
                "id": widget_id,
                "elType": "widget",
                "widgetType": "button",
                "settings": {
                    "text": str(content_value),
                    "link": {"url": "#contact"},
                    "align": "center",
                    "size": "md"
                }
            }
        
        # Image elements
        elif "image" in element_name or "photo" in element_name:
            return {
                "id": widget_id,
                "elType": "widget",
                "widgetType": "image",
                "settings": {
                    "image": {"url": f"/images/{content_value}"},
                    "image_size": "medium_large",
                    "align": "center"
                }
            }
        
        # List elements
        elif "grid" in element_name or "list" in element_name:
            if isinstance(content_value, list):
                list_html = "<ul>"
                for item in content_value:
                    list_html += f"<li>{item}</li>"
                list_html += "</ul>"
                
                return {
                    "id": widget_id,
                    "elType": "widget",
                    "widgetType": "text-editor",
                    "settings": {
                        "editor": list_html,
                        "align": "left"
                    }
                }
        
        # Form elements
        elif "form" in element_name:
            return {
                "id": widget_id,
                "elType": "widget",
                "widgetType": "form",
                "settings": {
                    "form_name": "Contact Form",
                    "form_fields": [
                        {"custom_id": "name", "field_type": "text", "field_label": "Nome", "required": True},
                        {"custom_id": "email", "field_type": "email", "field_label": "Email", "required": True},
                        {"custom_id": "phone", "field_type": "tel", "field_label": "Telefone", "required": False},
                        {"custom_id": "message", "field_type": "textarea", "field_label": "Mensagem", "required": True}
                    ],
                    "submit_button_text": "Enviar"
                }
            }
        
        # Fallback to text widget
        return {
            "id": widget_id,
            "elType": "widget",
            "widgetType": "text-editor",
            "settings": {
                "editor": str(content_value),
                "align": "left"
            }
        }
    
    def _generate_page_acf_fields(self, business_data: Dict[str, Any], industry: str, page_type: str) -> List[ACFField]:
        """Generate ACF fields specific to the page"""
        
        fields = []
        
        # Common fields for all pages
        common_fields = [
            ACFField(
                key="field_business_name",
                label="Nome do Negócio",
                name="business_name",
                type=ACFFieldType.TEXT,
                default_value=business_data.get("business_name", ""),
                instructions="Nome principal do seu negócio"
            ),
            ACFField(
                key="field_phone_number",
                label="Telefone",
                name="phone_number", 
                type=ACFFieldType.TEXT,
                default_value=business_data.get("phone_number", ""),
                instructions="Telefone no formato (11) 99999-9999"
            ),
            ACFField(
                key="field_whatsapp_number",
                label="WhatsApp",
                name="whatsapp_number",
                type=ACFFieldType.TEXT,
                default_value=business_data.get("whatsapp_number", ""),
                instructions="WhatsApp no formato (11) 99999-9999"
            )
        ]
        
        fields.extend(common_fields)
        
        # Industry-specific fields
        if industry == "restaurante":
            restaurant_fields = [
                ACFField(
                    key="field_specialty",
                    label="Especialidade Culinária",
                    name="specialty",
                    type=ACFFieldType.TEXT,
                    default_value="Culinária caseira",
                    instructions="Tipo de culinária do restaurante"
                ),
                ACFField(
                    key="field_delivery_area",
                    label="Área de Delivery",
                    name="delivery_area",
                    type=ACFFieldType.TEXT,
                    default_value="Região central",
                    instructions="Áreas onde fazemos delivery"
                ),
                ACFField(
                    key="field_opening_hours",
                    label="Horário de Funcionamento",
                    name="opening_hours",
                    type=ACFFieldType.TEXT,
                    default_value="Seg-Dom: 11h às 23h",
                    instructions="Horários de funcionamento"
                )
            ]
            fields.extend(restaurant_fields)
        
        elif industry == "saude":
            health_fields = [
                ACFField(
                    key="field_doctor_name",
                    label="Nome do Médico",
                    name="doctor_name",
                    type=ACFFieldType.TEXT,
                    default_value="Dr. Especialista",
                    instructions="Nome completo do médico responsável"
                ),
                ACFField(
                    key="field_medical_specialty",
                    label="Especialidade Médica",
                    name="medical_specialty",
                    type=ACFFieldType.TEXT,
                    default_value="Clínica Geral",
                    instructions="Especialidade médica principal"
                ),
                ACFField(
                    key="field_crm_number",
                    label="Número do CRM",
                    name="crm_number",
                    type=ACFFieldType.TEXT,
                    default_value="",
                    instructions="Número do registro no CRM"
                )
            ]
            fields.extend(health_fields)
        
        elif industry == "ecommerce":
            ecommerce_fields = [
                ACFField(
                    key="field_main_product",
                    label="Produto Principal",
                    name="main_product",
                    type=ACFFieldType.TEXT,
                    default_value="Produtos de qualidade",
                    instructions="Categoria ou produto principal"
                ),
                ACFField(
                    key="field_shipping_info",
                    label="Informações de Entrega",
                    name="shipping_info",
                    type=ACFFieldType.TEXT,
                    default_value="Frete grátis acima de R$ 100",
                    instructions="Condições de entrega"
                ),
                ACFField(
                    key="field_payment_methods",
                    label="Formas de Pagamento",
                    name="payment_methods",
                    type=ACFFieldType.TEXT,
                    default_value="PIX, Cartão, Boleto",
                    instructions="Métodos de pagamento aceitos"
                )
            ]
            fields.extend(ecommerce_fields)
        
        return fields
    
    def _generate_integration_code(self, elementor_data: List[Dict], acf_fields: List[ACFField]) -> str:
        """Generate integration code between Elementor and ACF"""
        
        field_mappings = []
        for field in acf_fields:
            field_mappings.append(f"'{field.name}': get_field('{field.name}') ?: '{field.default_value}'")
        
        integration_code = f"""<?php
/**
 * Elementor ACF Integration - Auto Generated
 * KenzySites Dynamic Content System
 */

// ACF Field Mappings
function get_dynamic_content_data() {{
    return [
        {','.join(field_mappings)}
    ];
}}

// Inject dynamic content into page
add_action('wp_footer', 'inject_dynamic_content');
function inject_dynamic_content() {{
    $dynamic_data = get_dynamic_content_data();
    ?>
    <script>
    window.acfDynamicContent = <?php echo json_encode($dynamic_data); ?>;
    
    // Replace placeholders on page load
    document.addEventListener('DOMContentLoaded', function() {{
        const dynamicData = window.acfDynamicContent;
        
        // Replace text placeholders
        Object.keys(dynamicData).forEach(fieldName => {{
            const placeholder = '[' + fieldName.toUpperCase() + ']';
            const value = dynamicData[fieldName];
            
            if (value) {{
                document.querySelectorAll('*').forEach(element => {{
                    if (element.textContent && element.textContent.includes(placeholder)) {{
                        element.textContent = element.textContent.replace(
                            new RegExp('\\\\[' + fieldName.toUpperCase() + '\\\\]', 'g'), 
                            value
                        );
                    }}
                }});
            }}
        }});
        
        // Update contact links
        if (dynamicData.whatsapp_number) {{
            const whatsappLinks = document.querySelectorAll('a[href*="wa.me"]');
            whatsappLinks.forEach(link => {{
                link.href = 'https://wa.me/55' + dynamicData.whatsapp_number.replace(/[^0-9]/g, '');
            }});
        }}
        
        if (dynamicData.phone_number) {{
            const phoneLinks = document.querySelectorAll('a[href*="tel:"]');
            phoneLinks.forEach(link => {{
                link.href = 'tel:' + dynamicData.phone_number.replace(/[^0-9]/g, '');
            }});
        }}
    }});
    </script>
    <?php
}}

// WhatsApp floating button (if WhatsApp number is provided)
add_action('wp_footer', 'add_whatsapp_button');
function add_whatsapp_button() {{
    $whatsapp = get_field('whatsapp_number');
    $business_name = get_field('business_name');
    
    if ($whatsapp) {{
        $clean_whatsapp = preg_replace('/[^0-9]/', '', $whatsapp);
        ?>
        <a href="https://wa.me/55<?php echo $clean_whatsapp; ?>" 
           class="whatsapp-float" 
           target="_blank"
           rel="noopener">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
            </svg>
            <span>Fale conosco</span>
        </a>
        
        <style>
        .whatsapp-float {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #25D366;
            color: white;
            padding: 12px 16px;
            border-radius: 50px;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
            z-index: 9999;
            transition: transform 0.2s;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .whatsapp-float:hover {{
            transform: scale(1.05);
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .whatsapp-float span {{
                display: none;
            }}
            .whatsapp-float {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
                justify-content: center;
                padding: 0;
            }}
        }}
        </style>
        <?php
    }}
}}
?>"""
        
        return integration_code

    async def convert_elementor_page(
        self, 
        page_data: Dict[str, Any],
        landing_page_type: str = "generic",
        preserve_elementor: bool = True
    ) -> Dict[str, Any]:
        """
        Convert Elementor page to ACF-enabled template
        
        Args:
            page_data: Elementor page data (from _elementor_data meta)
            landing_page_type: Type of landing page (captura_leads, vendas, etc.)
            preserve_elementor: Whether to keep Elementor or convert to pure PHP
        """
        try:
            logger.info(f"Converting Elementor page - Type: {landing_page_type}, Preserve: {preserve_elementor}")
            
            # 1. Analyze Elementor structure
            page_analysis = await self._analyze_elementor_structure(page_data)
            
            # 2. Extract dynamic content candidates
            dynamic_elements = await self._extract_dynamic_elements(page_data, landing_page_type)
            
            # 3. Generate ACF fields
            acf_field_groups = await self._generate_acf_fields(dynamic_elements, landing_page_type)
            
            # 4. Generate template code
            if preserve_elementor:
                template_code = await self._generate_hybrid_template(page_data, acf_field_groups)
                template_type = "hybrid"
            else:
                template_code = await self._generate_pure_acf_template(page_analysis, acf_field_groups)
                template_type = "pure_acf"
            
            # 5. Generate conversion report
            conversion_report = await self._generate_conversion_report(
                page_analysis, dynamic_elements, acf_field_groups
            )
            
            return {
                "conversion_id": f"conv_{uuid.uuid4().hex[:8]}",
                "template_type": template_type,
                "landing_page_type": landing_page_type,
                "acf_field_groups": acf_field_groups,
                "template_code": template_code,
                "page_analysis": page_analysis,
                "dynamic_elements_count": len(dynamic_elements),
                "conversion_report": conversion_report,
                "instructions": self._generate_instructions(template_type, acf_field_groups),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error converting Elementor page: {str(e)}")
            raise
    
    async def _analyze_elementor_structure(self, page_data: List[Dict]) -> Dict[str, Any]:
        """Analyze Elementor page structure"""
        try:
            analysis = {
                "sections": 0,
                "columns": 0,
                "widgets": [],
                "widget_types": {},
                "complexity_score": 0,
                "animations": 0,
                "custom_css": False
            }
            
            for section in page_data:
                if section.get('elType') == 'section':
                    analysis["sections"] += 1
                    
                    # Check for custom CSS
                    if section.get('settings', {}).get('_css_classes'):
                        analysis["custom_css"] = True
                    
                    # Analyze columns
                    for column in section.get('elements', []):
                        if column.get('elType') == 'column':
                            analysis["columns"] += 1
                            
                            # Analyze widgets
                            for widget in column.get('elements', []):
                                if widget.get('elType') == 'widget':
                                    widget_type = widget.get('widgetType')
                                    analysis["widgets"].append({
                                        "id": widget.get('id'),
                                        "type": widget_type,
                                        "settings": widget.get('settings', {})
                                    })
                                    
                                    # Count widget types
                                    analysis["widget_types"][widget_type] = \
                                        analysis["widget_types"].get(widget_type, 0) + 1
                                    
                                    # Check for animations
                                    if widget.get('settings', {}).get('_animation'):
                                        analysis["animations"] += 1
            
            # Calculate complexity score
            analysis["complexity_score"] = (
                analysis["sections"] * 2 +
                analysis["widgets"].__len__() +
                analysis["animations"] * 3 +
                (10 if analysis["custom_css"] else 0)
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing Elementor structure: {str(e)}")
            return {}
    
    async def _extract_dynamic_elements(self, page_data: List[Dict], landing_page_type: str) -> List[Dict]:
        """Extract elements that should be dynamic (ACF fields)"""
        try:
            dynamic_elements = []
            element_counter = {}
            
            for section in page_data:
                await self._process_section_for_dynamic_content(
                    section, dynamic_elements, element_counter, landing_page_type
                )
            
            # Add industry-specific fields
            if landing_page_type in self.industry_specific_fields:
                for field_def in self.industry_specific_fields[landing_page_type]:
                    dynamic_elements.append({
                        "source": "industry_specific",
                        "field_name": field_def["name"],
                        "field_type": field_def["type"],
                        "label": field_def["label"],
                        "default_value": "",
                        "priority": "high"
                    })
            
            return dynamic_elements
            
        except Exception as e:
            logger.error(f"Error extracting dynamic elements: {str(e)}")
            return []
    
    async def _process_section_for_dynamic_content(
        self, 
        section: Dict, 
        dynamic_elements: List[Dict],
        element_counter: Dict,
        landing_page_type: str
    ):
        """Process a section to find dynamic content candidates"""
        try:
            if section.get('elType') != 'section':
                return
            
            for column in section.get('elements', []):
                if column.get('elType') != 'column':
                    continue
                    
                for widget in column.get('elements', []):
                    if widget.get('elType') != 'widget':
                        continue
                    
                    widget_type = widget.get('widgetType')
                    widget_settings = widget.get('settings', {})
                    
                    # Process based on widget type
                    if widget_type in self.widget_acf_mappings:
                        dynamic_element = await self._process_widget_to_dynamic_element(
                            widget, widget_type, element_counter, landing_page_type
                        )
                        
                        if dynamic_element:
                            dynamic_elements.append(dynamic_element)
                    
                    # Check for text content that matches common patterns
                    await self._check_text_patterns(
                        widget_settings, dynamic_elements, widget.get('id')
                    )
            
        except Exception as e:
            logger.error(f"Error processing section: {str(e)}")
    
    async def _process_widget_to_dynamic_element(
        self, 
        widget: Dict, 
        widget_type: str,
        element_counter: Dict,
        landing_page_type: str
    ) -> Optional[Dict]:
        """Process a widget to create dynamic element"""
        try:
            mapping = self.widget_acf_mappings[widget_type]
            widget_settings = widget.get('settings', {})
            widget_id = widget.get('id')
            
            # Count elements of this type
            element_counter[widget_type] = element_counter.get(widget_type, 0) + 1
            counter = element_counter[widget_type]
            
            if mapping["acf_type"] == "group":
                # Complex widget with multiple fields
                return {
                    "source": "widget",
                    "widget_id": widget_id,
                    "widget_type": widget_type,
                    "field_type": "group",
                    "field_name": f"{widget_type}_{counter}",
                    "label": f"{widget_type.title().replace('-', ' ')} {counter}",
                    "sub_fields": mapping["fields"],
                    "priority": mapping["priority"],
                    "current_content": self._extract_widget_content(widget_settings, widget_type)
                }
            else:
                # Simple widget
                content = self._extract_widget_content(widget_settings, widget_type)
                
                if content:
                    # Try to match to common fields
                    field_name = self._suggest_field_name(content, widget_type, counter, landing_page_type)
                    
                    return {
                        "source": "widget",
                        "widget_id": widget_id,
                        "widget_type": widget_type,
                        "field_type": mapping["acf_type"],
                        "field_name": field_name,
                        "label": self._generate_field_label(field_name),
                        "default_value": content,
                        "priority": mapping["priority"]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing widget to dynamic element: {str(e)}")
            return None
    
    def _extract_widget_content(self, settings: Dict, widget_type: str) -> str:
        """Extract content from widget settings"""
        content_mappings = {
            "heading": ["title"],
            "text-editor": ["editor"],
            "button": ["text"],
            "image": ["alt_text"],
            "icon-box": ["title_text"],
            "testimonial": ["testimonial_content"]
        }
        
        if widget_type in content_mappings:
            for field in content_mappings[widget_type]:
                if field in settings:
                    content = settings[field]
                    # Clean HTML tags if present
                    if isinstance(content, str):
                        content = re.sub(r'<[^>]+>', '', content)
                        return content.strip()
        
        return ""
    
    async def _check_text_patterns(self, settings: Dict, dynamic_elements: List[Dict], widget_id: str):
        """Check text content against common patterns"""
        try:
            text_fields = ["title", "editor", "text", "description"]
            
            for field_name in text_fields:
                if field_name in settings:
                    text_content = str(settings[field_name])
                    
                    for pattern_def in self.common_dynamic_elements:
                        if re.search(pattern_def["pattern"], text_content, re.IGNORECASE):
                            # Found a match
                            dynamic_elements.append({
                                "source": "pattern_match",
                                "widget_id": widget_id,
                                "field_name": pattern_def["field"],
                                "field_type": pattern_def["type"],
                                "label": self._generate_field_label(pattern_def["field"]),
                                "matched_text": text_content,
                                "pattern": pattern_def["pattern"],
                                "priority": "medium"
                            })
                            break
            
        except Exception as e:
            logger.error(f"Error checking text patterns: {str(e)}")
    
    def _suggest_field_name(self, content: str, widget_type: str, counter: int, landing_page_type: str) -> str:
        """Suggest appropriate field name based on content and context"""
        content_lower = content.lower()
        
        # Common business terms
        if any(term in content_lower for term in ["empresa", "negócio", "business"]):
            return "business_name"
        elif any(term in content_lower for term in ["telefone", "phone", "contato"]):
            return "phone_number"
        elif any(term in content_lower for term in ["whatsapp", "wpp"]):
            return "whatsapp_number"
        elif any(term in content_lower for term in ["email", "e-mail"]):
            return "email_address"
        elif any(term in content_lower for term in ["preço", "price", "valor"]):
            return "price"
        
        # Widget type based naming
        if widget_type == "heading":
            if counter == 1:
                return "hero_title"
            else:
                return f"section_title_{counter}"
        elif widget_type == "text-editor":
            if counter == 1:
                return "hero_description"
            else:
                return f"content_block_{counter}"
        elif widget_type == "button":
            return f"cta_button_{counter}"
        elif widget_type == "image":
            return f"feature_image_{counter}"
        
        # Fallback
        return f"{widget_type}_{counter}"
    
    def _generate_field_label(self, field_name: str) -> str:
        """Generate human-readable label from field name"""
        label_mappings = {
            "business_name": "Nome da Empresa",
            "hero_title": "Título Principal",
            "hero_description": "Descrição Principal",
            "phone_number": "Número de Telefone",
            "whatsapp_number": "Número do WhatsApp",
            "email_address": "Endereço de Email",
            "price": "Preço",
            "discount_price": "Preço com Desconto",
            "cta_button": "Botão de Ação",
            "business_address": "Endereço da Empresa"
        }
        
        if field_name in label_mappings:
            return label_mappings[field_name]
        
        # Generate from field name
        return field_name.replace("_", " ").title()
    
    async def _generate_acf_fields(self, dynamic_elements: List[Dict], landing_page_type: str) -> List[ACFFieldGroup]:
        """Generate ACF field groups from dynamic elements"""
        try:
            # Group fields logically
            field_groups = {
                "business_info": {
                    "title": "Informações do Negócio",
                    "fields": []
                },
                "content": {
                    "title": "Conteúdo da Página",
                    "fields": []
                },
                "contact": {
                    "title": "Informações de Contato", 
                    "fields": []
                },
                "cta": {
                    "title": "Chamadas para Ação",
                    "fields": []
                }
            }
            
            # Categorize fields
            for element in dynamic_elements:
                field_name = element["field_name"]
                group_name = self._categorize_field(field_name)
                
                if element["field_type"] == "group":
                    # Handle group fields
                    sub_fields = []
                    for sub_field_def in element["sub_fields"]:
                        sub_field = ACFField(
                            key=f"field_{field_name}_{sub_field_def['name']}",
                            label=sub_field_def['name'].replace('_', ' ').title(),
                            name=f"{field_name}_{sub_field_def['name']}",
                            type=sub_field_def['type']
                        )
                        sub_fields.append(sub_field)
                    
                    # Group field (simplified for now)
                    field_groups[group_name]["fields"].append(ACFField(
                        key=f"field_{field_name}",
                        label=element["label"],
                        name=field_name,
                        type=ACFFieldType.TEXT,  # Simplified
                        default_value=str(element.get("current_content", ""))
                    ))
                else:
                    # Regular field
                    acf_field = ACFField(
                        key=f"field_{field_name}",
                        label=element["label"],
                        name=field_name,
                        type=element["field_type"],
                        default_value=element.get("default_value", ""),
                        instructions=self._generate_field_instructions(element)
                    )
                    
                    field_groups[group_name]["fields"].append(acf_field)
            
            # Convert to ACFFieldGroup objects
            acf_field_groups = []
            for group_key, group_data in field_groups.items():
                if group_data["fields"]:  # Only add groups with fields
                    field_group = ACFFieldGroup(
                        key=f"group_{group_key}",
                        title=group_data["title"],
                        fields=group_data["fields"],
                        location=[[{
                            "param": "page_template",
                            "operator": "==", 
                            "value": f"landing-page-{landing_page_type}"
                        }]]
                    )
                    acf_field_groups.append(field_group)
            
            return acf_field_groups
            
        except Exception as e:
            logger.error(f"Error generating ACF fields: {str(e)}")
            return []
    
    def _categorize_field(self, field_name: str) -> str:
        """Categorize field into appropriate group"""
        business_fields = ["business_name", "business_description", "logo"]
        contact_fields = ["phone_number", "whatsapp_number", "email_address", "business_address"]
        cta_fields = ["cta_button", "button_text", "button_url"]
        
        if any(term in field_name for term in business_fields):
            return "business_info"
        elif any(term in field_name for term in contact_fields):
            return "contact"
        elif any(term in field_name for term in cta_fields):
            return "cta"
        else:
            return "content"
    
    def _generate_field_instructions(self, element: Dict) -> str:
        """Generate helpful instructions for ACF field"""
        instructions = {
            "business_name": "Digite o nome da sua empresa ou negócio",
            "whatsapp_number": "Digite o número com código do país: 5511999999999",
            "phone_number": "Digite o telefone no formato: (11) 99999-9999",
            "email_address": "Digite o email principal para contato",
            "price": "Digite o preço no formato: R$ 99,90"
        }
        
        field_name = element["field_name"]
        if field_name in instructions:
            return instructions[field_name]
        
        if element.get("source") == "pattern_match":
            return f"Campo identificado automaticamente do texto: {element.get('matched_text', '')[:50]}..."
        
        return f"Personalize este {element['widget_type']} para seu negócio"
    
    async def _generate_hybrid_template(self, page_data: List[Dict], acf_field_groups: List[ACFFieldGroup]) -> str:
        """Generate hybrid template that keeps Elementor but adds ACF integration"""
        try:
            template_parts = []
            
            # PHP header
            template_parts.append("""<?php
/**
 * Landing Page Template - Hybrid (Elementor + ACF)
 * Generated by KenzySites AI
 */

// Get ACF fields
$business_name = get_field('business_name') ?: 'Sua Empresa';
$phone_number = get_field('phone_number') ?: '';
$whatsapp_number = get_field('whatsapp_number') ?: '';
$email_address = get_field('email_address') ?: '';

get_header(); ?>

<div class="landing-page-container">
    <?php
    // Render Elementor content
    if (\\Elementor\\Plugin::instance()->editor->is_edit_mode()) {
        echo '<div class="elementor-editor-notice">Modo Editor Elementor Ativo</div>';
    }
    
    // Main Elementor content
    echo \\Elementor\\Plugin::instance()->frontend->get_builder_content_for_display(get_the_ID());
    ?>
</div>

<!-- WhatsApp Float Button (if WhatsApp number provided) -->
<?php if ($whatsapp_number): ?>
<a href="https://wa.me/55<?php echo preg_replace('/[^0-9]/', '', $whatsapp_number); ?>" 
   class="whatsapp-float" 
   target="_blank"
   rel="noopener">
    <img src="<?php echo get_template_directory_uri(); ?>/assets/whatsapp-icon.svg" alt="WhatsApp">
    <span>Fale com <?php echo $business_name; ?></span>
</a>
<?php endif; ?>

<style>
.whatsapp-float {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #25D366;
    color: white;
    padding: 12px 16px;
    border-radius: 50px;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(37, 211, 102, 0.3);
    z-index: 9999;
    transition: transform 0.2s;
}

.whatsapp-float:hover {
    transform: scale(1.05);
    color: white;
}

.whatsapp-float img {
    width: 24px;
    height: 24px;
}

/* Responsive */
@media (max-width: 768px) {
    .whatsapp-float span {
        display: none;
    }
    
    .whatsapp-float {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        justify-content: center;
        padding: 0;
    }
}
</style>

<script>
// Dynamic content injection for Elementor widgets
document.addEventListener('DOMContentLoaded', function() {
    // Replace placeholder texts with ACF values
    const acfData = <?php echo json_encode([
        'business_name' => $business_name,
        'phone_number' => $phone_number,
        'whatsapp_number' => $whatsapp_number,
        'email_address' => $email_address
    ]); ?>;
    
    // Find and replace common placeholders
    replacePlaceholders(acfData);
});

function replacePlaceholders(data) {
    const placeholders = {
        '[BUSINESS_NAME]': data.business_name,
        '[PHONE]': data.phone_number,
        '[WHATSAPP]': data.whatsapp_number,
        '[EMAIL]': data.email_address
    };
    
    Object.keys(placeholders).forEach(placeholder => {
        const elements = document.querySelectorAll('*');
        elements.forEach(el => {
            if (el.textContent && el.textContent.includes(placeholder)) {
                el.textContent = el.textContent.replace(
                    new RegExp(placeholder, 'g'), 
                    placeholders[placeholder]
                );
            }
        });
    });
}
</script>

<?php get_footer(); ?>""")
            
            return "\n".join(template_parts)
            
        except Exception as e:
            logger.error(f"Error generating hybrid template: {str(e)}")
            return ""
    
    async def _generate_pure_acf_template(self, page_analysis: Dict, acf_field_groups: List[ACFFieldGroup]) -> str:
        """Generate pure ACF template (no Elementor dependency)"""
        # This would be more complex - converting Elementor structure to pure PHP/HTML
        # For now, return a basic template structure
        return """<?php
/**
 * Landing Page Template - Pure ACF
 * Generated by KenzySites AI
 */

get_header(); ?>

<div class="landing-page-pure-acf">
    <section class="hero-section">
        <div class="container">
            <h1><?php the_field('hero_title') ?: 'Título Principal'; ?></h1>
            <p><?php the_field('hero_description') ?: 'Descrição principal do seu negócio'; ?></p>
            
            <?php if (get_field('hero_image')): ?>
            <img src="<?php the_field('hero_image'); ?>" alt="Hero Image" class="hero-image">
            <?php endif; ?>
            
            <?php if (get_field('cta_button_text')): ?>
            <a href="<?php the_field('cta_button_url') ?: '#'; ?>" class="cta-button">
                <?php the_field('cta_button_text'); ?>
            </a>
            <?php endif; ?>
        </div>
    </section>
    
    <!-- Add more sections based on ACF fields -->
</div>

<?php get_footer(); ?>"""
    
    async def _generate_conversion_report(
        self, 
        page_analysis: Dict, 
        dynamic_elements: List[Dict],
        acf_field_groups: List[ACFFieldGroup]
    ) -> Dict[str, Any]:
        """Generate detailed conversion report"""
        try:
            total_widgets = len(page_analysis.get("widgets", []))
            dynamic_widgets = len([e for e in dynamic_elements if e.get("source") == "widget"])
            conversion_percentage = (dynamic_widgets / total_widgets * 100) if total_widgets > 0 else 0
            
            return {
                "conversion_summary": {
                    "total_widgets": total_widgets,
                    "converted_widgets": dynamic_widgets,
                    "conversion_percentage": round(conversion_percentage, 1),
                    "acf_field_groups": len(acf_field_groups),
                    "total_acf_fields": sum(len(group.fields) for group in acf_field_groups)
                },
                "complexity_assessment": {
                    "complexity_score": page_analysis.get("complexity_score", 0),
                    "has_animations": page_analysis.get("animations", 0) > 0,
                    "has_custom_css": page_analysis.get("custom_css", False),
                    "recommended_approach": "hybrid" if page_analysis.get("complexity_score", 0) > 20 else "pure_acf"
                },
                "optimization_suggestions": self._generate_optimization_suggestions(page_analysis, dynamic_elements),
                "manual_review_needed": self._needs_manual_review(page_analysis, dynamic_elements)
            }
            
        except Exception as e:
            logger.error(f"Error generating conversion report: {str(e)}")
            return {}
    
    def _generate_optimization_suggestions(self, page_analysis: Dict, dynamic_elements: List[Dict]) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if page_analysis.get("animations", 0) > 5:
            suggestions.append("Considere reduzir o número de animações para melhor performance")
        
        if page_analysis.get("complexity_score", 0) > 30:
            suggestions.append("Página complexa - recomendado manter modo híbrido com Elementor")
        
        if len(dynamic_elements) < 3:
            suggestions.append("Poucos elementos dinâmicos detectados - considere adicionar mais campos ACF")
        
        widget_types = page_analysis.get("widget_types", {})
        if widget_types.get("form", 0) > 0:
            suggestions.append("Formulários detectados - configure integração com email marketing")
        
        if widget_types.get("button", 0) > 3:
            suggestions.append("Muitos botões detectados - considere consolidar CTAs principais")
        
        return suggestions
    
    def _needs_manual_review(self, page_analysis: Dict, dynamic_elements: List[Dict]) -> bool:
        """Determine if manual review is needed"""
        return (
            page_analysis.get("complexity_score", 0) > 40 or
            page_analysis.get("custom_css", False) or
            len(dynamic_elements) < 2 or
            any(e.get("source") == "pattern_match" for e in dynamic_elements)
        )
    
    def _generate_instructions(self, template_type: str, acf_field_groups: List[ACFFieldGroup]) -> List[str]:
        """Generate instructions for using the converted template"""
        instructions = []
        
        if template_type == "hybrid":
            instructions.extend([
                "1. Importe os campos ACF usando o JSON gerado",
                "2. Aplique o template no WordPress",
                "3. Configure os campos ACF no admin",
                "4. Use o Elementor normalmente para edições visuais",
                "5. O conteúdo dinâmico será preenchido automaticamente"
            ])
        else:
            instructions.extend([
                "1. Importe os campos ACF usando o JSON gerado", 
                "2. Aplique o template PHP no tema",
                "3. Configure os campos ACF no admin",
                "4. Personalize o CSS conforme necessário"
            ])
        
        # Add field-specific instructions
        field_count = sum(len(group.fields) for group in acf_field_groups)
        instructions.append(f"Total de {field_count} campos ACF para personalizar")
        
        return instructions

# Global instance
elementor_converter = ElementorToACFConverter()