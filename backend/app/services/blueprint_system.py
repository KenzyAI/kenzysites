"""
Blueprint System
Complete website blueprints with templates, configurations, and deployment instructions
"""

import json
import logging
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
import hashlib

logger = logging.getLogger(__name__)

class BlueprintComponent(BaseModel):
    """Single component in a blueprint"""
    name: str
    type: str  # 'page', 'post', 'template', 'setting', 'plugin', 'theme'
    content: Optional[str] = None
    meta: Dict[str, Any] = {}
    dependencies: List[str] = []
    priority: int = 0  # Deployment order

class BlueprintConfiguration(BaseModel):
    """Blueprint configuration settings"""
    site_title: str
    site_description: str
    theme: str = "astra"
    plugins: List[str] = []
    menus: Dict[str, List[str]] = {}
    widgets: Dict[str, Any] = {}
    customizer: Dict[str, Any] = {}

class SiteBlueprint(BaseModel):
    """Complete website blueprint"""
    id: str
    name: str
    description: str
    industry: str
    style: str
    version: str = "1.0.0"
    created_at: datetime
    components: List[BlueprintComponent]
    configuration: BlueprintConfiguration
    preview_images: List[str] = []
    tags: List[str] = []
    difficulty: str = "easy"  # easy, medium, hard
    estimated_setup_time: int = 300  # seconds

class BlueprintSystem:
    """
    Manages website blueprints - complete pre-configured sites
    """
    
    def __init__(self):
        self.blueprints_dir = Path("blueprints")
        self.blueprints_dir.mkdir(exist_ok=True)
        
        # Cache for loaded blueprints
        self._blueprint_cache = {}
        
        # Blueprint registry
        self._blueprint_registry = {
            "restaurant": {
                "classic": "restaurant_classic",
                "modern": "restaurant_modern", 
                "pizzeria": "restaurant_pizzeria",
                "cafe": "restaurant_cafe"
            },
            "healthcare": {
                "clinic": "healthcare_clinic",
                "dentist": "healthcare_dentist",
                "psychology": "healthcare_psychology",
                "veterinary": "healthcare_veterinary"
            },
            "ecommerce": {
                "fashion": "ecommerce_fashion",
                "electronics": "ecommerce_electronics",
                "home": "ecommerce_home",
                "books": "ecommerce_books"
            },
            "services": {
                "consulting": "services_consulting",
                "law": "services_law",
                "accounting": "services_accounting",
                "marketing": "services_marketing"
            },
            "education": {
                "school": "education_school",
                "online_course": "education_online",
                "university": "education_university",
                "training": "education_training"
            }
        }
    
    def generate_all_blueprints(self) -> Dict[str, Any]:
        """Generate all industry blueprints"""
        
        logger.info("🏗️ Generating all blueprints...")
        
        generated_blueprints = []
        
        for industry, styles in self._blueprint_registry.items():
            for style, blueprint_id in styles.items():
                try:
                    blueprint = self._generate_blueprint(industry, style, blueprint_id)
                    self._save_blueprint(blueprint)
                    generated_blueprints.append(blueprint.dict())
                    logger.info(f"✅ Generated blueprint: {blueprint.name}")
                except Exception as e:
                    logger.error(f"❌ Failed to generate {industry}/{style} blueprint: {str(e)}")
        
        logger.info(f"✅ Generated {len(generated_blueprints)} blueprints")
        
        return {
            "success": True,
            "blueprints_generated": len(generated_blueprints),
            "blueprints": generated_blueprints
        }
    
    def _generate_blueprint(self, industry: str, style: str, blueprint_id: str) -> SiteBlueprint:
        """Generate a single blueprint"""
        
        if industry == "restaurant":
            return self._generate_restaurant_blueprint(style, blueprint_id)
        elif industry == "healthcare":
            return self._generate_healthcare_blueprint(style, blueprint_id)
        elif industry == "ecommerce":
            return self._generate_ecommerce_blueprint(style, blueprint_id)
        elif industry == "services":
            return self._generate_services_blueprint(style, blueprint_id)
        elif industry == "education":
            return self._generate_education_blueprint(style, blueprint_id)
        else:
            raise ValueError(f"Unknown industry: {industry}")
    
    def _generate_restaurant_blueprint(self, style: str, blueprint_id: str) -> SiteBlueprint:
        """Generate restaurant blueprint"""
        
        if style == "classic":
            components = [
                BlueprintComponent(
                    name="Home Page",
                    type="page",
                    content=self._get_restaurant_home_content("classic"),
                    meta={"is_front_page": True, "template": "page-home.php"},
                    priority=1
                ),
                BlueprintComponent(
                    name="Menu Page",
                    type="page",
                    content=self._get_restaurant_menu_content("classic"),
                    meta={"slug": "cardapio", "template": "page-menu.php"},
                    priority=2
                ),
                BlueprintComponent(
                    name="About Page", 
                    type="page",
                    content=self._get_restaurant_about_content("classic"),
                    meta={"slug": "sobre", "template": "page.php"},
                    priority=3
                ),
                BlueprintComponent(
                    name="Contact Page",
                    type="page",
                    content=self._get_contact_content(),
                    meta={"slug": "contato", "template": "page-contact.php"},
                    priority=4
                ),
                BlueprintComponent(
                    name="Gallery Page",
                    type="page",
                    content=self._get_restaurant_gallery_content(),
                    meta={"slug": "galeria", "template": "page-gallery.php"},
                    priority=5
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[RESTAURANT_NAME] - Restaurante",
                site_description="O melhor da culinária [CUISINE_TYPE] na cidade",
                theme="astra",
                plugins=[
                    "elementor",
                    "contact-form-7", 
                    "instagram-feed",
                    "restaurant-reservations",
                    "wp-restaurant-listings"
                ],
                menus={
                    "primary": ["Home", "Cardápio", "Sobre", "Galeria", "Contato"],
                    "footer": ["Política de Privacidade", "Termos de Uso"]
                },
                customizer={
                    "colors": {
                        "primary": "#8B4513",
                        "secondary": "#D2691E", 
                        "accent": "#CD853F"
                    },
                    "fonts": {
                        "heading": "Playfair Display",
                        "body": "Open Sans"
                    }
                }
            )
            
        elif style == "modern":
            components = [
                BlueprintComponent(
                    name="Modern Home",
                    type="page",
                    content=self._get_restaurant_home_content("modern"),
                    meta={"is_front_page": True, "template": "page-modern-home.php"},
                    priority=1
                ),
                BlueprintComponent(
                    name="Interactive Menu",
                    type="page", 
                    content=self._get_restaurant_menu_content("modern"),
                    meta={"slug": "menu", "template": "page-interactive-menu.php"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Chef's Story",
                    type="page",
                    content=self._get_restaurant_chef_content(),
                    meta={"slug": "chef", "template": "page-chef.php"},
                    priority=3
                ),
                BlueprintComponent(
                    name="Reservations",
                    type="page",
                    content=self._get_restaurant_reservations_content(),
                    meta={"slug": "reservas", "template": "page-reservations.php"},
                    priority=4
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[RESTAURANT_NAME] - Modern Dining",
                site_description="Experiência gastronômica moderna e sofisticada",
                theme="astra",
                plugins=[
                    "elementor",
                    "elementor-pro",
                    "restaurant-reservations",
                    "woocommerce",
                    "advanced-custom-fields"
                ],
                customizer={
                    "colors": {
                        "primary": "#2C3E50",
                        "secondary": "#E74C3C",
                        "accent": "#F39C12"
                    },
                    "fonts": {
                        "heading": "Montserrat",
                        "body": "Lato"
                    }
                }
            )
        
        else:  # pizzeria
            components = [
                BlueprintComponent(
                    name="Pizzeria Home",
                    type="page",
                    content=self._get_pizzeria_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Pizza Menu",
                    type="page",
                    content=self._get_pizzeria_menu_content(),
                    meta={"slug": "pizzas"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Order Online",
                    type="page",
                    content=self._get_pizzeria_order_content(),
                    meta={"slug": "pedidos"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[RESTAURANT_NAME] - Pizzaria Artesanal",
                site_description="As melhores pizzas artesanais da cidade",
                theme="astra",
                plugins=["elementor", "woocommerce", "delivery-drivers-for-woocommerce"],
                customizer={
                    "colors": {
                        "primary": "#C8102E",
                        "secondary": "#228B22",
                        "accent": "#FFD700"
                    }
                }
            )
        
        return SiteBlueprint(
            id=blueprint_id,
            name=f"Restaurante {style.title()}",
            description=f"Blueprint completo para restaurante estilo {style}",
            industry="restaurant",
            style=style,
            created_at=datetime.now(),
            components=components,
            configuration=configuration,
            tags=["restaurante", "comida", style],
            estimated_setup_time=300
        )
    
    def _generate_healthcare_blueprint(self, style: str, blueprint_id: str) -> SiteBlueprint:
        """Generate healthcare blueprint"""
        
        if style == "clinic":
            components = [
                BlueprintComponent(
                    name="Clinic Home",
                    type="page",
                    content=self._get_clinic_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Specialties",
                    type="page",
                    content=self._get_clinic_specialties_content(),
                    meta={"slug": "especialidades"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Doctors",
                    type="page",
                    content=self._get_clinic_doctors_content(),
                    meta={"slug": "medicos"},
                    priority=3
                ),
                BlueprintComponent(
                    name="Appointments",
                    type="page",
                    content=self._get_clinic_appointments_content(),
                    meta={"slug": "agendamento"},
                    priority=4
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="Clínica [CLINIC_NAME]",
                site_description="Cuidados médicos de excelência",
                theme="astra",
                plugins=[
                    "elementor",
                    "advanced-custom-fields",
                    "appointment-booking",
                    "medical-forms"
                ],
                customizer={
                    "colors": {
                        "primary": "#0077BE",
                        "secondary": "#00A651",
                        "accent": "#FFA500"
                    },
                    "fonts": {
                        "heading": "Source Sans Pro",
                        "body": "Open Sans"
                    }
                }
            )
            
        elif style == "dentist":
            components = [
                BlueprintComponent(
                    name="Dental Home",
                    type="page",
                    content=self._get_dental_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Services",
                    type="page",
                    content=self._get_dental_services_content(),
                    meta={"slug": "servicos"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Smile Gallery",
                    type="page",
                    content=self._get_dental_gallery_content(),
                    meta={"slug": "sorrisos"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="Dr. [DOCTOR_NAME] - Odontologia",
                site_description="Cuidado completo para seu sorriso",
                theme="astra",
                plugins=["elementor", "before-after-gallery", "appointment-booking"],
                customizer={
                    "colors": {
                        "primary": "#4A90E2",
                        "secondary": "#50E3C2",
                        "accent": "#F5A623"
                    }
                }
            )
        
        else:  # psychology
            components = [
                BlueprintComponent(
                    name="Psychology Home",
                    type="page", 
                    content=self._get_psychology_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Therapy Types",
                    type="page",
                    content=self._get_psychology_therapy_content(),
                    meta={"slug": "terapias"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Online Sessions",
                    type="page",
                    content=self._get_psychology_online_content(),
                    meta={"slug": "online"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[PSYCHOLOGIST_NAME] - Psicologia",
                site_description="Cuidado psicológico com abordagem humanizada",
                theme="astra",
                plugins=["elementor", "appointment-booking", "testimonials-widget"],
                customizer={
                    "colors": {
                        "primary": "#6B73FF",
                        "secondary": "#9013FE",
                        "accent": "#00BCD4"
                    }
                }
            )
        
        return SiteBlueprint(
            id=blueprint_id,
            name=f"Saúde - {style.title()}",
            description=f"Blueprint para área da saúde - {style}",
            industry="healthcare",
            style=style,
            created_at=datetime.now(),
            components=components,
            configuration=configuration,
            tags=["saude", "medico", style],
            estimated_setup_time=240
        )
    
    def _generate_ecommerce_blueprint(self, style: str, blueprint_id: str) -> SiteBlueprint:
        """Generate e-commerce blueprint"""
        
        if style == "fashion":
            components = [
                BlueprintComponent(
                    name="Fashion Home",
                    type="page",
                    content=self._get_fashion_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Shop",
                    type="page", 
                    content="[woocommerce_shop]",
                    meta={"slug": "loja", "template": "page-shop.php"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Collections",
                    type="page",
                    content=self._get_fashion_collections_content(),
                    meta={"slug": "colecoes"},
                    priority=3
                ),
                BlueprintComponent(
                    name="Size Guide",
                    type="page",
                    content=self._get_fashion_size_guide_content(),
                    meta={"slug": "guia-tamanhos"},
                    priority=4
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[STORE_NAME] - Moda & Estilo",
                site_description="As últimas tendências da moda",
                theme="storefront",
                plugins=[
                    "woocommerce",
                    "elementor",
                    "woocommerce-payments",
                    "mailchimp-for-woocommerce"
                ],
                customizer={
                    "colors": {
                        "primary": "#FF6B6B",
                        "secondary": "#4ECDC4",
                        "accent": "#45B7D1"
                    }
                }
            )
            
        elif style == "electronics":
            components = [
                BlueprintComponent(
                    name="Electronics Home",
                    type="page",
                    content=self._get_electronics_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Categories",
                    type="page",
                    content=self._get_electronics_categories_content(),
                    meta={"slug": "categorias"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Tech Support",
                    type="page",
                    content=self._get_electronics_support_content(),
                    meta={"slug": "suporte"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[STORE_NAME] Eletrônicos",
                site_description="Tecnologia de ponta com os melhores preços",
                theme="storefront",
                plugins=["woocommerce", "product-comparison", "live-chat"],
                customizer={
                    "colors": {
                        "primary": "#2C3E50",
                        "secondary": "#3498DB", 
                        "accent": "#E74C3C"
                    }
                }
            )
            
        else:  # home
            components = [
                BlueprintComponent(
                    name="Home & Garden",
                    type="page",
                    content=self._get_home_garden_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Room Designer",
                    type="page",
                    content=self._get_room_designer_content(),
                    meta={"slug": "designer"},
                    priority=2
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[STORE_NAME] - Casa & Jardim",
                site_description="Tudo para deixar sua casa mais bonita",
                theme="storefront",
                plugins=["woocommerce", "product-gallery", "home-design-tools"],
                customizer={
                    "colors": {
                        "primary": "#27AE60",
                        "secondary": "#F39C12",
                        "accent": "#8E44AD"
                    }
                }
            )
        
        return SiteBlueprint(
            id=blueprint_id,
            name=f"E-commerce {style.title()}",
            description=f"Loja online completa para {style}",
            industry="ecommerce",
            style=style,
            created_at=datetime.now(),
            components=components,
            configuration=configuration,
            tags=["ecommerce", "loja", style],
            estimated_setup_time=480
        )
    
    def _generate_services_blueprint(self, style: str, blueprint_id: str) -> SiteBlueprint:
        """Generate services blueprint"""
        
        if style == "consulting":
            components = [
                BlueprintComponent(
                    name="Consulting Home",
                    type="page",
                    content=self._get_consulting_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Services",
                    type="page",
                    content=self._get_consulting_services_content(),
                    meta={"slug": "servicos"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Case Studies",
                    type="page",
                    content=self._get_consulting_cases_content(),
                    meta={"slug": "casos"},
                    priority=3
                ),
                BlueprintComponent(
                    name="Free Consultation",
                    type="page",
                    content=self._get_consulting_consultation_content(),
                    meta={"slug": "consultoria-gratuita"},
                    priority=4
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="[COMPANY_NAME] Consultoria",
                site_description="Soluções estratégicas para seu negócio",
                theme="astra",
                plugins=["elementor", "testimonials", "lead-generation"],
                customizer={
                    "colors": {
                        "primary": "#34495E",
                        "secondary": "#3498DB",
                        "accent": "#E74C3C"
                    }
                }
            )
            
        elif style == "law":
            components = [
                BlueprintComponent(
                    name="Law Firm Home",
                    type="page",
                    content=self._get_law_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Practice Areas",
                    type="page",
                    content=self._get_law_areas_content(),
                    meta={"slug": "areas-atuacao"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Lawyers",
                    type="page",
                    content=self._get_law_lawyers_content(),
                    meta={"slug": "advogados"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="Advocacia [LAWYER_NAME]",
                site_description="Defesa de seus direitos com experiência",
                theme="astra",
                plugins=["elementor", "case-management", "appointment-booking"],
                customizer={
                    "colors": {
                        "primary": "#1A237E",
                        "secondary": "#303F9F",
                        "accent": "#FF5722"
                    }
                }
            )
            
        else:  # accounting
            components = [
                BlueprintComponent(
                    name="Accounting Home",
                    type="page",
                    content=self._get_accounting_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Services",
                    type="page",
                    content=self._get_accounting_services_content(),
                    meta={"slug": "servicos"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Client Portal",
                    type="page",
                    content=self._get_accounting_portal_content(),
                    meta={"slug": "portal"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="Contabilidade [COMPANY_NAME]",
                site_description="Gestão contábil completa para sua empresa",
                theme="astra", 
                plugins=["elementor", "client-portal", "document-management"],
                customizer={
                    "colors": {
                        "primary": "#2E7D32",
                        "secondary": "#388E3C",
                        "accent": "#FFC107"
                    }
                }
            )
        
        return SiteBlueprint(
            id=blueprint_id,
            name=f"Serviços - {style.title()}",
            description=f"Blueprint para serviços - {style}",
            industry="services",
            style=style,
            created_at=datetime.now(),
            components=components,
            configuration=configuration,
            tags=["servicos", style],
            estimated_setup_time=360
        )
    
    def _generate_education_blueprint(self, style: str, blueprint_id: str) -> SiteBlueprint:
        """Generate education blueprint"""
        
        if style == "school":
            components = [
                BlueprintComponent(
                    name="School Home",
                    type="page",
                    content=self._get_school_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Programs",
                    type="page",
                    content=self._get_school_programs_content(),
                    meta={"slug": "cursos"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Admissions",
                    type="page",
                    content=self._get_school_admissions_content(),
                    meta={"slug": "matriculas"},
                    priority=3
                ),
                BlueprintComponent(
                    name="Events",
                    type="page",
                    content=self._get_school_events_content(),
                    meta={"slug": "eventos"},
                    priority=4
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="Escola [SCHOOL_NAME]",
                site_description="Educação de qualidade para formar o futuro",
                theme="astra",
                plugins=["elementor", "events-calendar", "student-management"],
                customizer={
                    "colors": {
                        "primary": "#1976D2",
                        "secondary": "#42A5F5",
                        "accent": "#FF9800"
                    }
                }
            )
            
        else:  # online_course
            components = [
                BlueprintComponent(
                    name="Course Home",
                    type="page",
                    content=self._get_course_home_content(),
                    meta={"is_front_page": True},
                    priority=1
                ),
                BlueprintComponent(
                    name="Curriculum",
                    type="page",
                    content=self._get_course_curriculum_content(),
                    meta={"slug": "conteudo"},
                    priority=2
                ),
                BlueprintComponent(
                    name="Enrollment",
                    type="page",
                    content=self._get_course_enrollment_content(),
                    meta={"slug": "inscricao"},
                    priority=3
                )
            ]
            
            configuration = BlueprintConfiguration(
                site_title="Curso [COURSE_NAME]",
                site_description="Aprenda no seu ritmo com qualidade",
                theme="astra",
                plugins=["elementor", "learndash", "woocommerce"],
                customizer={
                    "colors": {
                        "primary": "#9C27B0",
                        "secondary": "#BA68C8", 
                        "accent": "#4CAF50"
                    }
                }
            )
        
        return SiteBlueprint(
            id=blueprint_id,
            name=f"Educação - {style.title()}",
            description=f"Blueprint para educação - {style}",
            industry="education",
            style=style,
            created_at=datetime.now(),
            components=components,
            configuration=configuration,
            tags=["educacao", style],
            estimated_setup_time=300
        )
    
    # Content generation methods (simplified versions)
    def _get_restaurant_home_content(self, style: str) -> str:
        if style == "classic":
            return """
            <!-- wp:cover {"url":"restaurant-hero.jpg"} -->
            <div class="wp-block-cover">
                <h1>Bem-vindos ao [RESTAURANT_NAME]</h1>
                <p>Sabores autênticos da nossa tradição culinária</p>
            </div>
            <!-- /wp:cover -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Nossa História</h2>
                    <p>Há [YEARS] anos servindo os melhores pratos da culinária [CUISINE_TYPE].</p>
                </div>
                <div class="wp-block-column">
                    <h2>Especialidades</h2>
                    <p>Pratos únicos preparados com ingredientes frescos e receitas tradicionais.</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
        else:  # modern
            return """
            <!-- wp:cover {"url":"modern-restaurant.jpg"} -->
            <div class="wp-block-cover">
                <h1>[RESTAURANT_NAME]</h1>
                <p>Experiência gastronômica moderna</p>
            </div>
            <!-- /wp:cover -->
            """
    
    def _get_restaurant_menu_content(self, style: str) -> str:
        return """
        <!-- wp:heading {"level":1} -->
        <h1>Nosso Cardápio</h1>
        <!-- /wp:heading -->
        
        <!-- wp:columns -->
        <div class="wp-block-columns">
            <div class="wp-block-column">
                <h2>Entradas</h2>
                <ul>
                    <li>Entrada Especial - R$ [PRICE1]</li>
                    <li>Aperitivo da Casa - R$ [PRICE2]</li>
                </ul>
            </div>
            <div class="wp-block-column">
                <h2>Pratos Principais</h2>
                <ul>
                    <li>Prato Especial - R$ [PRICE3]</li>
                    <li>Especialidade do Chef - R$ [PRICE4]</li>
                </ul>
            </div>
        </div>
        <!-- /wp:columns -->
        """
    
    def _get_contact_content(self) -> str:
        return """
        <!-- wp:heading {"level":1} -->
        <h1>Entre em Contato</h1>
        <!-- /wp:heading -->
        
        <!-- wp:columns -->
        <div class="wp-block-columns">
            <div class="wp-block-column">
                <h2>Informações</h2>
                <p>📞 [PHONE]<br>📧 [EMAIL]<br>📍 [ADDRESS]</p>
            </div>
            <div class="wp-block-column">
                <h2>Horários</h2>
                <p>[OPENING_HOURS]</p>
            </div>
        </div>
        <!-- /wp:columns -->
        
        <!-- wp:contact-form-7/contact-form-selector -->
        [contact-form-7 id="1" title="Contact form 1"]
        <!-- /wp:contact-form-7/contact-form-selector -->
        """
    
    # Placeholder content methods for all other industry/style combinations
    def _get_restaurant_about_content(self, style: str) -> str:
        return "<!-- Restaurant about content placeholder -->"
    
    def _get_restaurant_gallery_content(self) -> str:
        return "<!-- Restaurant gallery content placeholder -->"
    
    def _get_restaurant_chef_content(self) -> str:
        return "<!-- Restaurant chef content placeholder -->"
    
    def _get_restaurant_reservations_content(self) -> str:
        return "<!-- Restaurant reservations content placeholder -->"
    
    def _get_pizzeria_home_content(self) -> str:
        return "<!-- Pizzeria home content placeholder -->"
    
    def _get_pizzeria_menu_content(self) -> str:
        return "<!-- Pizzeria menu content placeholder -->"
    
    def _get_pizzeria_order_content(self) -> str:
        return "<!-- Pizzeria order content placeholder -->"
    
    # Healthcare content placeholders
    def _get_clinic_home_content(self) -> str:
        return "<!-- Clinic home content placeholder -->"
    
    def _get_clinic_specialties_content(self) -> str:
        return "<!-- Clinic specialties content placeholder -->"
    
    def _get_clinic_doctors_content(self) -> str:
        return "<!-- Clinic doctors content placeholder -->"
    
    def _get_clinic_appointments_content(self) -> str:
        return "<!-- Clinic appointments content placeholder -->"
    
    def _get_dental_home_content(self) -> str:
        return "<!-- Dental home content placeholder -->"
    
    def _get_dental_services_content(self) -> str:
        return "<!-- Dental services content placeholder -->"
    
    def _get_dental_gallery_content(self) -> str:
        return "<!-- Dental gallery content placeholder -->"
    
    def _get_psychology_home_content(self) -> str:
        return "<!-- Psychology home content placeholder -->"
    
    def _get_psychology_therapy_content(self) -> str:
        return "<!-- Psychology therapy content placeholder -->"
    
    def _get_psychology_online_content(self) -> str:
        return "<!-- Psychology online content placeholder -->"
    
    # E-commerce content placeholders  
    def _get_fashion_home_content(self) -> str:
        return "<!-- Fashion home content placeholder -->"
    
    def _get_fashion_collections_content(self) -> str:
        return "<!-- Fashion collections content placeholder -->"
    
    def _get_fashion_size_guide_content(self) -> str:
        return "<!-- Fashion size guide content placeholder -->"
    
    def _get_electronics_home_content(self) -> str:
        return "<!-- Electronics home content placeholder -->"
    
    def _get_electronics_categories_content(self) -> str:
        return "<!-- Electronics categories content placeholder -->"
    
    def _get_electronics_support_content(self) -> str:
        return "<!-- Electronics support content placeholder -->"
    
    def _get_home_garden_content(self) -> str:
        return "<!-- Home garden content placeholder -->"
    
    def _get_room_designer_content(self) -> str:
        return "<!-- Room designer content placeholder -->"
    
    # Services content placeholders
    def _get_consulting_home_content(self) -> str:
        return "<!-- Consulting home content placeholder -->"
    
    def _get_consulting_services_content(self) -> str:
        return "<!-- Consulting services content placeholder -->"
    
    def _get_consulting_cases_content(self) -> str:
        return "<!-- Consulting cases content placeholder -->"
    
    def _get_consulting_consultation_content(self) -> str:
        return "<!-- Consulting consultation content placeholder -->"
    
    def _get_law_home_content(self) -> str:
        return "<!-- Law home content placeholder -->"
    
    def _get_law_areas_content(self) -> str:
        return "<!-- Law areas content placeholder -->"
    
    def _get_law_lawyers_content(self) -> str:
        return "<!-- Law lawyers content placeholder -->"
    
    def _get_accounting_home_content(self) -> str:
        return "<!-- Accounting home content placeholder -->"
    
    def _get_accounting_services_content(self) -> str:
        return "<!-- Accounting services content placeholder -->"
    
    def _get_accounting_portal_content(self) -> str:
        return "<!-- Accounting portal content placeholder -->"
    
    # Education content placeholders
    def _get_school_home_content(self) -> str:
        return "<!-- School home content placeholder -->"
    
    def _get_school_programs_content(self) -> str:
        return "<!-- School programs content placeholder -->"
    
    def _get_school_admissions_content(self) -> str:
        return "<!-- School admissions content placeholder -->"
    
    def _get_school_events_content(self) -> str:
        return "<!-- School events content placeholder -->"
    
    def _get_course_home_content(self) -> str:
        return "<!-- Course home content placeholder -->"
    
    def _get_course_curriculum_content(self) -> str:
        return "<!-- Course curriculum content placeholder -->"
    
    def _get_course_enrollment_content(self) -> str:
        return "<!-- Course enrollment content placeholder -->"
    
    def get_blueprint(self, blueprint_id: str) -> Optional[SiteBlueprint]:
        """Get a specific blueprint"""
        
        if blueprint_id in self._blueprint_cache:
            return self._blueprint_cache[blueprint_id]
        
        blueprint_file = self.blueprints_dir / f"{blueprint_id}.json"
        
        if blueprint_file.exists():
            try:
                with open(blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint_data = json.load(f)
                    blueprint = SiteBlueprint(**blueprint_data)
                    self._blueprint_cache[blueprint_id] = blueprint
                    return blueprint
            except Exception as e:
                logger.error(f"Error loading blueprint {blueprint_id}: {str(e)}")
        
        return None
    
    def list_blueprints(self) -> List[Dict[str, Any]]:
        """List all available blueprints"""
        
        blueprints = []
        
        for blueprint_file in self.blueprints_dir.glob("*.json"):
            try:
                with open(blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint_data = json.load(f)
                    blueprints.append({
                        "id": blueprint_data["id"],
                        "name": blueprint_data["name"],
                        "description": blueprint_data["description"],
                        "industry": blueprint_data["industry"],
                        "style": blueprint_data["style"],
                        "tags": blueprint_data.get("tags", []),
                        "estimated_setup_time": blueprint_data.get("estimated_setup_time", 300)
                    })
            except Exception as e:
                logger.warning(f"Could not load blueprint from {blueprint_file}: {str(e)}")
        
        return blueprints
    
    def _save_blueprint(self, blueprint: SiteBlueprint):
        """Save blueprint to disk"""
        
        blueprint_file = self.blueprints_dir / f"{blueprint.id}.json"
        
        try:
            with open(blueprint_file, 'w', encoding='utf-8') as f:
                json.dump(blueprint.dict(), f, indent=2, default=str, ensure_ascii=False)
            
            # Cache the blueprint
            self._blueprint_cache[blueprint.id] = blueprint
            
        except Exception as e:
            logger.error(f"Error saving blueprint {blueprint.id}: {str(e)}")

# Global instance
blueprint_system = BlueprintSystem()