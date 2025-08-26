"""
Blueprint Management System
Inspired by ZipWP's template system for reusable site structures
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from enum import Enum

logger = logging.getLogger(__name__)

class BlueprintType(str, Enum):
    """Types of blueprints available"""
    LANDING_PAGE = "landing_page"
    BUSINESS_WEBSITE = "business_website"
    ECOMMERCE = "ecommerce"
    RESTAURANT = "restaurant"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    CONSULTING = "consulting"

class BlueprintCategory(str, Enum):
    """Blueprint categories"""
    INDUSTRY_SPECIFIC = "industry_specific"
    GENERIC = "generic"
    SEASONAL = "seasonal"
    PROMOTIONAL = "promotional"

class BlueprintComplexity(str, Enum):
    """Complexity levels"""
    SIMPLE = "simple"      # 1-3 pages, basic features
    STANDARD = "standard"  # 4-8 pages, medium features
    ADVANCED = "advanced"  # 8+ pages, complex features

class Blueprint(BaseModel):
    """Blueprint model for reusable templates"""
    
    id: str
    name: str
    description: str
    type: BlueprintType
    category: BlueprintCategory
    complexity: BlueprintComplexity
    industry: str
    target_audience: List[str]
    
    # Structure definition
    pages: List[Dict[str, Any]]
    navigation: Dict[str, Any]
    features: List[str]
    
    # Content requirements
    required_fields: List[str]
    optional_fields: List[str]
    placeholder_mappings: Dict[str, str]
    
    # Technical configuration
    wordpress_theme: str
    required_plugins: List[str]
    elementor_templates: List[Dict[str, Any]]
    acf_field_groups: List[Dict[str, Any]]
    
    # Brazilian market features
    brazilian_features: Dict[str, Any]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: str
    author: str
    usage_count: int = 0
    rating: float = 0.0
    
    # Generation settings
    estimated_generation_time: int  # seconds
    credits_cost: int

class BlueprintManager:
    """Manages blueprint templates for instant site generation"""
    
    def __init__(self):
        self.blueprints: Dict[str, Blueprint] = {}
        self._load_default_blueprints()
    
    def _load_default_blueprints(self):
        """Load default blueprint templates"""
        
        # Restaurant Blueprint
        restaurant_blueprint = self._create_restaurant_blueprint()
        self.blueprints[restaurant_blueprint.id] = restaurant_blueprint
        
        # Healthcare Blueprint
        healthcare_blueprint = self._create_healthcare_blueprint()
        self.blueprints[healthcare_blueprint.id] = healthcare_blueprint
        
        # E-commerce Blueprint
        ecommerce_blueprint = self._create_ecommerce_blueprint()
        self.blueprints[ecommerce_blueprint.id] = ecommerce_blueprint
        
        # Generic Business Blueprint
        business_blueprint = self._create_business_blueprint()
        self.blueprints[business_blueprint.id] = business_blueprint
        
        logger.info(f"✅ Loaded {len(self.blueprints)} default blueprints")
    
    def _create_restaurant_blueprint(self) -> Blueprint:
        """Create restaurant industry blueprint"""
        
        return Blueprint(
            id="restaurant_complete_2025",
            name="Restaurante Completo 2025",
            description="Blueprint completo para restaurantes com delivery, cardápio digital e integração WhatsApp/PIX",
            type=BlueprintType.RESTAURANT,
            category=BlueprintCategory.INDUSTRY_SPECIFIC,
            complexity=BlueprintComplexity.STANDARD,
            industry="restaurante",
            target_audience=["restaurantes", "lanchonetes", "delivery", "food trucks"],
            
            pages=[
                {
                    "title": "Home",
                    "slug": "/",
                    "template": "restaurant_home",
                    "sections": ["hero_banner", "featured_menu", "delivery_info", "about", "contact"],
                    "required": True
                },
                {
                    "title": "Cardápio",
                    "slug": "/cardapio",
                    "template": "restaurant_menu",
                    "sections": ["menu_categories", "featured_items", "prices", "allergen_info"],
                    "required": True
                },
                {
                    "title": "Delivery",
                    "slug": "/delivery",
                    "template": "restaurant_delivery",
                    "sections": ["delivery_areas", "order_form", "delivery_times", "contact"],
                    "required": True
                },
                {
                    "title": "Sobre",
                    "slug": "/sobre",
                    "template": "restaurant_about",
                    "sections": ["restaurant_story", "chef_info", "location", "hours"],
                    "required": False
                },
                {
                    "title": "Contato",
                    "slug": "/contato",
                    "template": "restaurant_contact",
                    "sections": ["contact_form", "location_map", "hours", "social_media"],
                    "required": True
                }
            ],
            
            navigation={
                "primary": ["Home", "Cardápio", "Delivery", "Sobre", "Contato"],
                "footer": ["Política de Privacidade", "Termos de Uso", "Alergênicos"],
                "mobile": ["Home", "Cardápio", "Delivery", "WhatsApp"]
            },
            
            features=[
                "Cardápio digital responsivo",
                "Sistema de pedidos WhatsApp",
                "Integração PIX para pagamento",
                "Área de delivery configurável",
                "Informações nutricionais",
                "Botão flutuante WhatsApp",
                "Google Maps integrado",
                "Galeria de pratos",
                "Avaliações de clientes",
                "Redes sociais integradas"
            ],
            
            required_fields=[
                "restaurant_name",
                "phone_number",
                "whatsapp_number",
                "address",
                "opening_hours",
                "specialty"
            ],
            
            optional_fields=[
                "chef_name",
                "instagram_url",
                "facebook_url",
                "delivery_fee",
                "minimum_order",
                "about_text"
            ],
            
            placeholder_mappings={
                "[RESTAURANT_NAME]": "restaurant_name",
                "[PHONE]": "phone_number",
                "[WHATSAPP]": "whatsapp_number",
                "[ADDRESS]": "address",
                "[HOURS]": "opening_hours",
                "[SPECIALTY]": "specialty",
                "[CHEF_NAME]": "chef_name"
            },
            
            wordpress_theme="astra",
            required_plugins=[
                "elementor",
                "advanced-custom-fields-pro",
                "yoast-seo",
                "woocommerce",
                "restaurant-reservations",
                "wp-food-manager"
            ],
            
            elementor_templates=[
                {
                    "name": "Restaurant Hero",
                    "type": "section",
                    "category": "hero",
                    "widgets": ["heading", "text", "image", "button"]
                },
                {
                    "name": "Menu Grid",
                    "type": "section", 
                    "category": "menu",
                    "widgets": ["image", "heading", "text", "price"]
                },
                {
                    "name": "Delivery Areas",
                    "type": "section",
                    "category": "delivery",
                    "widgets": ["map", "text", "list"]
                }
            ],
            
            acf_field_groups=[
                {
                    "title": "Restaurant Information",
                    "fields": [
                        {"name": "restaurant_name", "type": "text", "required": True},
                        {"name": "specialty", "type": "text", "required": True},
                        {"name": "phone_number", "type": "text", "required": True},
                        {"name": "whatsapp_number", "type": "text", "required": True},
                        {"name": "address", "type": "textarea", "required": True},
                        {"name": "opening_hours", "type": "textarea", "required": True}
                    ]
                },
                {
                    "title": "Menu Configuration",
                    "fields": [
                        {"name": "featured_dishes", "type": "repeater", "required": False},
                        {"name": "menu_categories", "type": "select", "required": False},
                        {"name": "allergen_info", "type": "checkbox", "required": False}
                    ]
                },
                {
                    "title": "Delivery Settings",
                    "fields": [
                        {"name": "delivery_areas", "type": "textarea", "required": True},
                        {"name": "delivery_fee", "type": "number", "required": False},
                        {"name": "minimum_order", "type": "number", "required": False},
                        {"name": "delivery_time", "type": "text", "required": False}
                    ]
                }
            ],
            
            brazilian_features={
                "whatsapp_integration": {
                    "enabled": True,
                    "floating_button": True,
                    "order_integration": True,
                    "menu_sharing": True
                },
                "pix_payment": {
                    "enabled": True,
                    "qr_code": True,
                    "payment_links": True
                },
                "delivery_integration": {
                    "ifood": True,
                    "uber_eats": True,
                    "rappi": True
                },
                "lgpd_compliance": {
                    "cookie_notice": True,
                    "privacy_policy": True,
                    "data_consent": True
                }
            },
            
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="2.0.0",
            author="KenzySites AI",
            usage_count=0,
            rating=4.8,
            estimated_generation_time=45,
            credits_cost=150
        )
    
    def _create_healthcare_blueprint(self) -> Blueprint:
        """Create healthcare industry blueprint"""
        
        return Blueprint(
            id="healthcare_clinic_2025",
            name="Clínica Médica 2025",
            description="Blueprint para clínicas médicas com agendamento online, informações dos médicos e compliance LGPD",
            type=BlueprintType.HEALTHCARE,
            category=BlueprintCategory.INDUSTRY_SPECIFIC,
            complexity=BlueprintComplexity.STANDARD,
            industry="saude",
            target_audience=["clínicas", "médicos", "dentistas", "psicólogos", "fisioterapeutas"],
            
            pages=[
                {
                    "title": "Home",
                    "slug": "/",
                    "template": "clinic_home",
                    "sections": ["hero_banner", "services", "doctors", "appointment_cta", "testimonials"],
                    "required": True
                },
                {
                    "title": "Serviços",
                    "slug": "/servicos",
                    "template": "clinic_services",
                    "sections": ["services_grid", "service_details", "benefits", "pricing"],
                    "required": True
                },
                {
                    "title": "Médicos",
                    "slug": "/medicos",
                    "template": "clinic_doctors",
                    "sections": ["doctors_grid", "qualifications", "experience", "specialties"],
                    "required": True
                },
                {
                    "title": "Agendamento",
                    "slug": "/agendamento",
                    "template": "clinic_appointment",
                    "sections": ["appointment_form", "available_times", "insurance_info", "contact"],
                    "required": True
                },
                {
                    "title": "Sobre",
                    "slug": "/sobre",
                    "template": "clinic_about",
                    "sections": ["clinic_history", "mission_vision", "facilities", "team"],
                    "required": False
                },
                {
                    "title": "Contato",
                    "slug": "/contato",
                    "template": "clinic_contact",
                    "sections": ["contact_form", "location", "emergency_info", "insurance"],
                    "required": True
                }
            ],
            
            navigation={
                "primary": ["Home", "Serviços", "Médicos", "Agendamento", "Sobre", "Contato"],
                "footer": ["Política de Privacidade", "Termos de Uso", "Emergências", "Convênios"],
                "mobile": ["Home", "Serviços", "Agendamento", "WhatsApp"]
            },
            
            features=[
                "Agendamento online integrado",
                "Perfis detalhados dos médicos",
                "Lista de convênios aceitos",
                "Informações de emergência",
                "Compliance LGPD completo",
                "Integração WhatsApp para agendamentos",
                "Galeria das instalações",
                "Depoimentos de pacientes",
                "Horários disponíveis em tempo real",
                "Sistema de lembretes automáticos"
            ],
            
            required_fields=[
                "clinic_name",
                "main_specialty",
                "phone_number",
                "whatsapp_number",
                "address",
                "consultation_hours",
                "crm_number"
            ],
            
            optional_fields=[
                "doctor_name",
                "doctor_photo",
                "qualifications",
                "experience_years",
                "insurance_accepted",
                "emergency_phone"
            ],
            
            placeholder_mappings={
                "[CLINIC_NAME]": "clinic_name",
                "[SPECIALTY]": "main_specialty",
                "[DOCTOR_NAME]": "doctor_name",
                "[PHONE]": "phone_number",
                "[WHATSAPP]": "whatsapp_number",
                "[ADDRESS]": "address",
                "[HOURS]": "consultation_hours",
                "[CRM]": "crm_number"
            },
            
            wordpress_theme="astra",
            required_plugins=[
                "elementor",
                "advanced-custom-fields-pro",
                "yoast-seo",
                "appointment-booking-calendar",
                "medical-wp",
                "gdpr-compliance"
            ],
            
            elementor_templates=[
                {
                    "name": "Medical Hero",
                    "type": "section",
                    "category": "hero",
                    "widgets": ["heading", "text", "image", "appointment_button"]
                },
                {
                    "name": "Services Grid",
                    "type": "section",
                    "category": "services", 
                    "widgets": ["icon", "heading", "text", "link"]
                },
                {
                    "name": "Doctor Profile",
                    "type": "section",
                    "category": "doctors",
                    "widgets": ["image", "heading", "text", "credentials"]
                }
            ],
            
            acf_field_groups=[
                {
                    "title": "Clinic Information",
                    "fields": [
                        {"name": "clinic_name", "type": "text", "required": True},
                        {"name": "main_specialty", "type": "text", "required": True},
                        {"name": "phone_number", "type": "text", "required": True},
                        {"name": "whatsapp_number", "type": "text", "required": True},
                        {"name": "address", "type": "textarea", "required": True},
                        {"name": "consultation_hours", "type": "textarea", "required": True}
                    ]
                },
                {
                    "title": "Medical Staff",
                    "fields": [
                        {"name": "doctors", "type": "repeater", "required": False},
                        {"name": "specialties", "type": "select", "required": False},
                        {"name": "qualifications", "type": "textarea", "required": False}
                    ]
                },
                {
                    "title": "Services & Insurance",
                    "fields": [
                        {"name": "services_offered", "type": "repeater", "required": True},
                        {"name": "insurance_accepted", "type": "checkbox", "required": False},
                        {"name": "emergency_contact", "type": "text", "required": False}
                    ]
                }
            ],
            
            brazilian_features={
                "whatsapp_integration": {
                    "enabled": True,
                    "appointment_booking": True,
                    "patient_communication": True,
                    "emergency_contact": True
                },
                "pix_payment": {
                    "enabled": True,
                    "consultation_fees": True,
                    "exam_payments": True
                },
                "lgpd_compliance": {
                    "patient_data_protection": True,
                    "medical_privacy": True,
                    "consent_forms": True,
                    "data_retention_policies": True
                },
                "cfm_compliance": {
                    "medical_advertising": True,
                    "ethical_guidelines": True,
                    "crm_display": True
                }
            },
            
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="2.0.0",
            author="KenzySites AI",
            usage_count=0,
            rating=4.9,
            estimated_generation_time=50,
            credits_cost=180
        )
    
    def _create_ecommerce_blueprint(self) -> Blueprint:
        """Create e-commerce blueprint"""
        
        return Blueprint(
            id="ecommerce_store_2025",
            name="Loja Virtual Completa 2025",
            description="Blueprint completo para e-commerce com WooCommerce, PIX, marketplace e compliance brasileiro",
            type=BlueprintType.ECOMMERCE,
            category=BlueprintCategory.INDUSTRY_SPECIFIC,
            complexity=BlueprintComplexity.ADVANCED,
            industry="ecommerce",
            target_audience=["lojas online", "varejo", "produtos físicos", "marketplace"],
            
            pages=[
                {
                    "title": "Home",
                    "slug": "/",
                    "template": "store_home",
                    "sections": ["hero_banner", "featured_products", "categories", "benefits", "testimonials"],
                    "required": True
                },
                {
                    "title": "Produtos",
                    "slug": "/produtos",
                    "template": "store_products",
                    "sections": ["product_grid", "filters", "sorting", "pagination"],
                    "required": True
                },
                {
                    "title": "Sobre",
                    "slug": "/sobre",
                    "template": "store_about",
                    "sections": ["company_story", "mission", "team", "guarantees"],
                    "required": True
                },
                {
                    "title": "Entrega",
                    "slug": "/entrega",
                    "template": "store_shipping",
                    "sections": ["shipping_info", "delivery_areas", "return_policy", "tracking"],
                    "required": True
                },
                {
                    "title": "Contato",
                    "slug": "/contato",
                    "template": "store_contact",
                    "sections": ["contact_form", "support_info", "faq", "social_media"],
                    "required": True
                },
                {
                    "title": "Minha Conta",
                    "slug": "/minha-conta",
                    "template": "store_account",
                    "sections": ["login_form", "order_history", "wishlist", "account_info"],
                    "required": True
                },
                {
                    "title": "Carrinho",
                    "slug": "/carrinho",
                    "template": "store_cart",
                    "sections": ["cart_items", "shipping_calculator", "checkout_button", "related_products"],
                    "required": True
                },
                {
                    "title": "Checkout",
                    "slug": "/checkout",
                    "template": "store_checkout",
                    "sections": ["billing_form", "shipping_options", "payment_methods", "order_review"],
                    "required": True
                }
            ],
            
            navigation={
                "primary": ["Home", "Produtos", "Sobre", "Entrega", "Contato"],
                "footer": ["Política de Privacidade", "Termos de Uso", "Trocas e Devoluções", "Frete"],
                "mobile": ["Home", "Produtos", "Carrinho", "Conta"],
                "account": ["Meus Pedidos", "Favoritos", "Endereços", "Dados"]
            },
            
            features=[
                "WooCommerce completo configurado",
                "Integração PIX automática",
                "Cálculo de frete Correios",
                "Múltiplas formas de pagamento",
                "Sistema de avaliações",
                "Wishlist e comparação",
                "Cupons de desconto",
                "Programa de fidelidade",
                "Integração com marketplaces",
                "Abandoned cart recovery",
                "Email marketing integrado",
                "Analytics e relatórios",
                "Compliance CDC e Procon"
            ],
            
            required_fields=[
                "store_name",
                "main_category",
                "phone_number",
                "whatsapp_number",
                "email",
                "cnpj",
                "address"
            ],
            
            optional_fields=[
                "company_description",
                "shipping_policy",
                "return_policy",
                "instagram_url",
                "facebook_url",
                "marketplace_links"
            ],
            
            placeholder_mappings={
                "[STORE_NAME]": "store_name",
                "[CATEGORY]": "main_category",
                "[PHONE]": "phone_number",
                "[WHATSAPP]": "whatsapp_number",
                "[EMAIL]": "email",
                "[CNPJ]": "cnpj",
                "[ADDRESS]": "address"
            },
            
            wordpress_theme="astra",
            required_plugins=[
                "woocommerce",
                "elementor",
                "advanced-custom-fields-pro",
                "yoast-seo",
                "woocommerce-correios",
                "woocommerce-mercadopago",
                "mailchimp-for-wp",
                "yith-woocommerce-wishlist"
            ],
            
            elementor_templates=[
                {
                    "name": "E-commerce Hero",
                    "type": "section",
                    "category": "hero",
                    "widgets": ["heading", "text", "product_carousel", "cta_button"]
                },
                {
                    "name": "Product Grid",
                    "type": "section",
                    "category": "products",
                    "widgets": ["product_grid", "filters", "sorting"]
                },
                {
                    "name": "Benefits Section",
                    "type": "section",
                    "category": "benefits",
                    "widgets": ["icon", "heading", "text", "benefits_grid"]
                }
            ],
            
            acf_field_groups=[
                {
                    "title": "Store Information",
                    "fields": [
                        {"name": "store_name", "type": "text", "required": True},
                        {"name": "main_category", "type": "text", "required": True},
                        {"name": "cnpj", "type": "text", "required": True},
                        {"name": "phone_number", "type": "text", "required": True},
                        {"name": "whatsapp_number", "type": "text", "required": True},
                        {"name": "email", "type": "email", "required": True}
                    ]
                },
                {
                    "title": "Shipping & Returns",
                    "fields": [
                        {"name": "shipping_areas", "type": "textarea", "required": True},
                        {"name": "return_policy", "type": "textarea", "required": True},
                        {"name": "warranty_info", "type": "textarea", "required": False}
                    ]
                },
                {
                    "title": "Payment & Promotions",
                    "fields": [
                        {"name": "payment_methods", "type": "checkbox", "required": True},
                        {"name": "active_promotions", "type": "repeater", "required": False},
                        {"name": "loyalty_program", "type": "true_false", "required": False}
                    ]
                }
            ],
            
            brazilian_features={
                "whatsapp_integration": {
                    "enabled": True,
                    "product_sharing": True,
                    "customer_support": True,
                    "order_updates": True
                },
                "pix_payment": {
                    "enabled": True,
                    "instant_payment": True,
                    "installment_options": True,
                    "discount_for_pix": True
                },
                "marketplace_integration": {
                    "mercado_livre": True,
                    "magazine_luiza": True,
                    "amazon_brasil": True
                },
                "shipping_integration": {
                    "correios": True,
                    "local_delivery": True,
                    "pickup_points": True
                },
                "compliance": {
                    "cdc_compliance": True,
                    "procon_requirements": True,
                    "invoice_generation": True,
                    "tax_calculation": True
                },
                "lgpd_compliance": {
                    "customer_data_protection": True,
                    "purchase_history_privacy": True,
                    "marketing_consent": True
                }
            },
            
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="2.0.0",
            author="KenzySites AI",
            usage_count=0,
            rating=4.7,
            estimated_generation_time=90,
            credits_cost=250
        )
    
    def _create_business_blueprint(self) -> Blueprint:
        """Create generic business blueprint"""
        
        return Blueprint(
            id="business_generic_2025",
            name="Site Empresarial Genérico 2025",
            description="Blueprint versátil para empresas de serviços gerais com foco em conversão",
            type=BlueprintType.BUSINESS_WEBSITE,
            category=BlueprintCategory.GENERIC,
            complexity=BlueprintComplexity.SIMPLE,
            industry="geral",
            target_audience=["empresas de serviços", "consultoria", "freelancers", "startups"],
            
            pages=[
                {
                    "title": "Home",
                    "slug": "/",
                    "template": "business_home",
                    "sections": ["hero_banner", "services", "about", "testimonials", "contact_cta"],
                    "required": True
                },
                {
                    "title": "Serviços",
                    "slug": "/servicos",
                    "template": "business_services",
                    "sections": ["services_grid", "service_details", "pricing", "portfolio"],
                    "required": True
                },
                {
                    "title": "Sobre",
                    "slug": "/sobre",
                    "template": "business_about",
                    "sections": ["company_story", "team", "mission_vision", "values"],
                    "required": True
                },
                {
                    "title": "Portfólio",
                    "slug": "/portfolio",
                    "template": "business_portfolio",
                    "sections": ["project_grid", "case_studies", "client_logos", "results"],
                    "required": False
                },
                {
                    "title": "Blog",
                    "slug": "/blog",
                    "template": "business_blog",
                    "sections": ["recent_posts", "categories", "newsletter", "popular_posts"],
                    "required": False
                },
                {
                    "title": "Contato",
                    "slug": "/contato",
                    "template": "business_contact",
                    "sections": ["contact_form", "office_info", "map", "social_media"],
                    "required": True
                }
            ],
            
            navigation={
                "primary": ["Home", "Serviços", "Sobre", "Portfólio", "Blog", "Contato"],
                "footer": ["Política de Privacidade", "Termos de Uso", "Trabalhe Conosco"],
                "mobile": ["Home", "Serviços", "Contato", "WhatsApp"]
            },
            
            features=[
                "Design responsivo profissional",
                "Formulário de contato inteligente",
                "Integração com Google Analytics",
                "SEO otimizado",
                "Blog integrado",
                "Portfólio de projetos",
                "Depoimentos de clientes",
                "Integração redes sociais",
                "WhatsApp Business API",
                "Newsletter signup",
                "Schema markup"
            ],
            
            required_fields=[
                "business_name",
                "business_description",
                "phone_number",
                "whatsapp_number",
                "email",
                "address"
            ],
            
            optional_fields=[
                "services_list",
                "team_members",
                "company_history",
                "mission_statement",
                "social_media_links"
            ],
            
            placeholder_mappings={
                "[BUSINESS_NAME]": "business_name",
                "[DESCRIPTION]": "business_description",
                "[PHONE]": "phone_number",
                "[WHATSAPP]": "whatsapp_number",
                "[EMAIL]": "email",
                "[ADDRESS]": "address"
            },
            
            wordpress_theme="astra",
            required_plugins=[
                "elementor",
                "advanced-custom-fields-pro",
                "yoast-seo",
                "contact-form-7",
                "mailchimp-for-wp"
            ],
            
            elementor_templates=[
                {
                    "name": "Business Hero",
                    "type": "section",
                    "category": "hero",
                    "widgets": ["heading", "text", "image", "cta_button"]
                },
                {
                    "name": "Services Grid",
                    "type": "section",
                    "category": "services",
                    "widgets": ["icon", "heading", "text", "link"]
                },
                {
                    "name": "About Section",
                    "type": "section",
                    "category": "about",
                    "widgets": ["image", "heading", "text", "team_grid"]
                }
            ],
            
            acf_field_groups=[
                {
                    "title": "Business Information",
                    "fields": [
                        {"name": "business_name", "type": "text", "required": True},
                        {"name": "business_description", "type": "textarea", "required": True},
                        {"name": "phone_number", "type": "text", "required": True},
                        {"name": "whatsapp_number", "type": "text", "required": True},
                        {"name": "email", "type": "email", "required": True},
                        {"name": "address", "type": "textarea", "required": True}
                    ]
                },
                {
                    "title": "Services & Team",
                    "fields": [
                        {"name": "services_offered", "type": "repeater", "required": True},
                        {"name": "team_members", "type": "repeater", "required": False},
                        {"name": "company_values", "type": "textarea", "required": False}
                    ]
                }
            ],
            
            brazilian_features={
                "whatsapp_integration": {
                    "enabled": True,
                    "business_communication": True,
                    "lead_generation": True
                },
                "lgpd_compliance": {
                    "enabled": True,
                    "contact_form_consent": True,
                    "newsletter_consent": True
                },
                "local_seo": {
                    "google_my_business": True,
                    "local_schema": True,
                    "brazilian_address_format": True
                }
            },
            
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="2.0.0",
            author="KenzySites AI",
            usage_count=0,
            rating=4.5,
            estimated_generation_time=30,
            credits_cost=100
        )
    
    def get_blueprint(self, blueprint_id: str) -> Optional[Blueprint]:
        """Get blueprint by ID"""
        return self.blueprints.get(blueprint_id)
    
    def list_blueprints(
        self,
        blueprint_type: Optional[BlueprintType] = None,
        industry: Optional[str] = None,
        complexity: Optional[BlueprintComplexity] = None
    ) -> List[Blueprint]:
        """List blueprints with optional filters"""
        
        blueprints = list(self.blueprints.values())
        
        if blueprint_type:
            blueprints = [b for b in blueprints if b.type == blueprint_type]
        
        if industry:
            blueprints = [b for b in blueprints if b.industry == industry]
        
        if complexity:
            blueprints = [b for b in blueprints if b.complexity == complexity]
        
        # Sort by rating and usage count
        blueprints.sort(key=lambda x: (x.rating, x.usage_count), reverse=True)
        
        return blueprints
    
    def get_recommended_blueprint(self, industry: str, business_type: str) -> Optional[Blueprint]:
        """Get recommended blueprint based on industry and business type"""
        
        # Priority mapping for recommendations
        industry_priority = {
            "restaurante": "restaurant_complete_2025",
            "saude": "healthcare_clinic_2025", 
            "ecommerce": "ecommerce_store_2025"
        }
        
        # Check for exact industry match
        if industry in industry_priority:
            blueprint_id = industry_priority[industry]
            return self.blueprints.get(blueprint_id)
        
        # Fallback to generic business blueprint
        return self.blueprints.get("business_generic_2025")
    
    def increment_usage(self, blueprint_id: str):
        """Increment usage count for blueprint"""
        if blueprint_id in self.blueprints:
            self.blueprints[blueprint_id].usage_count += 1
    
    def get_blueprint_summary(self, blueprint_id: str) -> Dict[str, Any]:
        """Get blueprint summary for quick preview"""
        
        blueprint = self.get_blueprint(blueprint_id)
        if not blueprint:
            return {}
        
        return {
            "id": blueprint.id,
            "name": blueprint.name,
            "description": blueprint.description,
            "type": blueprint.type,
            "industry": blueprint.industry,
            "complexity": blueprint.complexity,
            "estimated_time": blueprint.estimated_generation_time,
            "credits_cost": blueprint.credits_cost,
            "features_count": len(blueprint.features),
            "pages_count": len(blueprint.pages),
            "rating": blueprint.rating,
            "usage_count": blueprint.usage_count,
            "brazilian_features": list(blueprint.brazilian_features.keys())
        }

# Global instance
blueprint_manager = BlueprintManager()