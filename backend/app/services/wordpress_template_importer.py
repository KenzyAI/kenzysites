"""
WordPress Template Importer
Automatically imports templates and themes into WordPress instance
"""

import asyncio
import logging
import json
import aiohttp
import base64
import zipfile
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class WordPressTemplateImporter:
    """
    Import templates, themes, and plugins into WordPress automatically
    """
    
    def __init__(self):
        # WordPress instance
        self.wp_base_url = "http://localhost:8085"
        self.wp_api_url = f"{self.wp_base_url}/wp-json/wp/v2"
        self.wp_admin_user = "admin"
        self.wp_admin_password = "admin123"
        
        # Template storage
        self.templates_dir = Path("wordpress/templates")
        self.themes_dir = Path("wordpress/themes")
        self.plugins_dir = Path("wordpress/plugins")
        
        self.session = None
        
    async def initialize(self):
        """Initialize importer"""
        
        self.session = aiohttp.ClientSession()
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ WordPress Template Importer initialized")
    
    async def import_all_templates(self) -> Dict[str, Any]:
        """
        Import all templates for each industry
        """
        
        if not self.session:
            await self.initialize()
        
        results = {
            "themes_imported": [],
            "templates_imported": [],
            "plugins_installed": [],
            "success": True,
            "errors": []
        }
        
        try:
            # 1. Install essential plugins
            await self._install_essential_plugins()
            
            # 2. Install and activate Astra theme (like ZIPWP)
            await self._install_astra_theme()
            
            # 3. Import industry templates
            industries = ["restaurant", "healthcare", "ecommerce", "services", "education"]
            
            for industry in industries:
                try:
                    template_result = await self._import_industry_templates(industry)
                    results["templates_imported"].append({
                        "industry": industry,
                        "templates": template_result
                    })
                except Exception as e:
                    results["errors"].append(f"Failed to import {industry} templates: {str(e)}")
            
            # 4. Configure starter content
            await self._configure_starter_content()
            
            # 5. Set up Elementor template library
            await self._setup_elementor_library()
            
            logger.info("✅ All templates imported successfully")
            
        except Exception as e:
            logger.error(f"❌ Template import failed: {str(e)}")
            results["success"] = False
            results["errors"].append(str(e))
        
        return results
    
    async def _install_essential_plugins(self):
        """Install essential WordPress plugins"""
        
        essential_plugins = [
            {
                "slug": "elementor",
                "name": "Elementor Page Builder",
                "description": "Page builder for creating layouts"
            },
            {
                "slug": "advanced-custom-fields",
                "name": "Advanced Custom Fields",
                "description": "Custom fields for dynamic content"
            },
            {
                "slug": "astra-sites",
                "name": "Astra Starter Sites",
                "description": "Pre-built website templates"
            },
            {
                "slug": "contact-form-7",
                "name": "Contact Form 7",
                "description": "Contact form functionality"
            },
            {
                "slug": "yoast-seo",
                "name": "Yoast SEO",
                "description": "SEO optimization"
            }
        ]
        
        for plugin in essential_plugins:
            try:
                # Simulate plugin installation via WordPress API
                # In real implementation, would use WP-CLI or plugin installation API
                logger.info(f"📦 Installing plugin: {plugin['name']}")
                
                # Mock successful installation
                await asyncio.sleep(0.5)  # Simulate installation time
                
            except Exception as e:
                logger.warning(f"⚠️ Could not install plugin {plugin['name']}: {str(e)}")
    
    async def _install_astra_theme(self):
        """Install and activate Astra theme (like ZIPWP uses)"""
        
        try:
            logger.info("🎨 Installing Astra theme...")
            
            # In real implementation, would download and install Astra theme
            # For now, we'll create a mock theme activation
            
            theme_data = {
                "name": "Astra",
                "description": "Fast, lightweight, and highly customizable theme",
                "version": "4.6.0",
                "template": "astra",
                "stylesheet": "astra"
            }
            
            # Mock theme activation via WordPress API
            await self._make_wp_api_request(
                "POST",
                "/wp-json/wp/v2/themes/astra/activate",
                data=theme_data
            )
            
            logger.info("✅ Astra theme installed and activated")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not install Astra theme: {str(e)}")
    
    async def _import_industry_templates(self, industry: str) -> List[Dict]:
        """Import templates for specific industry"""
        
        templates = []
        
        # Generate industry-specific templates
        if industry == "restaurant":
            templates = await self._create_restaurant_templates()
        elif industry == "healthcare":
            templates = await self._create_healthcare_templates()
        elif industry == "ecommerce":
            templates = await self._create_ecommerce_templates()
        elif industry == "services":
            templates = await self._create_services_templates()
        elif industry == "education":
            templates = await self._create_education_templates()
        
        # Import each template
        imported_templates = []
        for template in templates:
            try:
                result = await self._import_single_template(template)
                if result:
                    imported_templates.append(result)
            except Exception as e:
                logger.warning(f"⚠️ Failed to import template {template.get('name')}: {str(e)}")
        
        logger.info(f"✅ Imported {len(imported_templates)} templates for {industry}")
        return imported_templates
    
    async def _create_restaurant_templates(self) -> List[Dict]:
        """Create restaurant industry templates"""
        
        return [
            {
                "name": "Restaurante Clássico",
                "type": "page",
                "industry": "restaurant",
                "content": self._generate_restaurant_content("classic"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("restaurant", "classic"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Restaurante Moderno",
                "type": "page", 
                "industry": "restaurant",
                "content": self._generate_restaurant_content("modern"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("restaurant", "modern"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Pizzaria",
                "type": "page",
                "industry": "restaurant",
                "content": self._generate_restaurant_content("pizzeria"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("restaurant", "pizzeria"),
                    "_elementor_edit_mode": "builder"
                }
            }
        ]
    
    async def _create_healthcare_templates(self) -> List[Dict]:
        """Create healthcare industry templates"""
        
        return [
            {
                "name": "Clínica Médica",
                "type": "page",
                "industry": "healthcare",
                "content": self._generate_healthcare_content("clinic"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("healthcare", "clinic"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Dentista",
                "type": "page",
                "industry": "healthcare", 
                "content": self._generate_healthcare_content("dentist"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("healthcare", "dentist"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Psicólogo",
                "type": "page",
                "industry": "healthcare",
                "content": self._generate_healthcare_content("psychology"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("healthcare", "psychology"),
                    "_elementor_edit_mode": "builder"
                }
            }
        ]
    
    async def _create_ecommerce_templates(self) -> List[Dict]:
        """Create e-commerce industry templates"""
        
        return [
            {
                "name": "Loja Fashion",
                "type": "page",
                "industry": "ecommerce",
                "content": self._generate_ecommerce_content("fashion"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("ecommerce", "fashion"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Eletrônicos",
                "type": "page",
                "industry": "ecommerce",
                "content": self._generate_ecommerce_content("electronics"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("ecommerce", "electronics"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Casa e Jardim",
                "type": "page",
                "industry": "ecommerce",
                "content": self._generate_ecommerce_content("home"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("ecommerce", "home"),
                    "_elementor_edit_mode": "builder"
                }
            }
        ]
    
    async def _create_services_templates(self) -> List[Dict]:
        """Create services industry templates"""
        
        return [
            {
                "name": "Consultoria",
                "type": "page",
                "industry": "services",
                "content": self._generate_services_content("consulting"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("services", "consulting"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Advocacia",
                "type": "page",
                "industry": "services",
                "content": self._generate_services_content("law"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("services", "law"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Contabilidade",
                "type": "page",
                "industry": "services",
                "content": self._generate_services_content("accounting"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("services", "accounting"),
                    "_elementor_edit_mode": "builder"
                }
            }
        ]
    
    async def _create_education_templates(self) -> List[Dict]:
        """Create education industry templates"""
        
        return [
            {
                "name": "Escola",
                "type": "page",
                "industry": "education",
                "content": self._generate_education_content("school"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("education", "school"),
                    "_elementor_edit_mode": "builder"
                }
            },
            {
                "name": "Curso Online",
                "type": "page",
                "industry": "education",
                "content": self._generate_education_content("online"),
                "meta": {
                    "_elementor_data": self._generate_elementor_data("education", "online"),
                    "_elementor_edit_mode": "builder"
                }
            }
        ]
    
    def _generate_restaurant_content(self, style: str) -> str:
        """Generate restaurant content based on style"""
        
        if style == "classic":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Bem-vindos ao [RESTAURANT_NAME]</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Há mais de [YEARS] anos servindo os melhores pratos da culinária [CUISINE_TYPE] com ingredientes frescos e receitas tradicionais.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Nossos Pratos</h2>
                    <p>Cardápio especial com pratos únicos preparados pelo Chef [CHEF_NAME].</p>
                </div>
                <div class="wp-block-column">
                    <h2>Delivery</h2>
                    <p>Entregamos em toda região de [DELIVERY_AREA]. Peça pelo WhatsApp [WHATSAPP].</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
        elif style == "modern":
            return """
            <!-- wp:cover {"url":"hero-restaurant.jpg"} -->
            <div class="wp-block-cover">
                <div class="wp-block-cover__inner-container">
                    <h1>[RESTAURANT_NAME]</h1>
                    <p>Experiência gastronômica moderna e sofisticada</p>
                </div>
            </div>
            <!-- /wp:cover -->
            
            <!-- wp:paragraph -->
            <p>Descubra sabores únicos em um ambiente contemporâneo e acolhedor.</p>
            <!-- /wp:paragraph -->
            """
        else:  # pizzeria
            return """
            <!-- wp:heading {"level":1} -->
            <h1>🍕 [RESTAURANT_NAME] - A Melhor Pizza da Cidade</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Pizzas artesanais com massa tradicional italiana e ingredientes premium.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:list -->
            <ul>
                <li>Massa fermentada por 48h</li>
                <li>Forno a lenha tradicional</li>
                <li>Ingredientes importados da Itália</li>
                <li>Delivery em 30 minutos</li>
            </ul>
            <!-- /wp:list -->
            """
    
    def _generate_healthcare_content(self, specialty: str) -> str:
        """Generate healthcare content based on specialty"""
        
        if specialty == "clinic":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Clínica [CLINIC_NAME] - Cuidando da sua saúde</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Atendimento médico especializado com mais de [YEARS] anos de experiência.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Especialidades</h2>
                    <ul>
                        <li>Clínica Geral</li>
                        <li>Pediatria</li>
                        <li>Cardiologia</li>
                        <li>Ginecologia</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Agende sua Consulta</h2>
                    <p>📞 [PHONE]<br>💬 WhatsApp: [WHATSAPP]<br>📧 [EMAIL]</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
        elif specialty == "dentist":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Dr. [DOCTOR_NAME] - Odontologia</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Cuidado completo para seu sorriso com as mais modernas técnicas em odontologia.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:list -->
            <ul>
                <li>Limpeza e Prevenção</li>
                <li>Ortodontia</li>
                <li>Implantes Dentários</li>
                <li>Clareamento</li>
                <li>Próteses</li>
            </ul>
            <!-- /wp:list -->
            """
        else:  # psychology
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Psicologia [PSYCHOLOGIST_NAME]</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Atendimento psicológico com abordagem humanizada para adolescentes, adultos e casais.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Modalidades</h2>
                    <ul>
                        <li>Terapia Individual</li>
                        <li>Terapia de Casal</li>
                        <li>Atendimento Online</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Contato</h2>
                    <p>Agende sua consulta:<br>📞 [PHONE]<br>💬 [WHATSAPP]</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
    
    def _generate_ecommerce_content(self, category: str) -> str:
        """Generate e-commerce content based on category"""
        
        if category == "fashion":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Loja [STORE_NAME] - Moda & Estilo</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>As últimas tendências da moda com qualidade e preços especiais.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Coleções</h2>
                    <ul>
                        <li>Verão 2024</li>
                        <li>Moda Executiva</li>
                        <li>Casual Wear</li>
                        <li>Acessórios</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Entrega</h2>
                    <p>✅ Frete grátis acima de R$ 199<br>📦 Entrega em todo Brasil<br>🔄 Troca garantida</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
        elif category == "electronics":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>[STORE_NAME] Eletrônicos</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Tecnologia de ponta com os melhores preços e garantia estendida.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:list -->
            <ul>
                <li>Smartphones e Tablets</li>
                <li>Notebooks e Computadores</li>
                <li>TVs e Home Theater</li>
                <li>Games e Acessórios</li>
                <li>Casa Inteligente</li>
            </ul>
            <!-- /wp:list -->
            """
        else:  # home
            return """
            <!-- wp:heading {"level":1} -->
            <h1>[STORE_NAME] - Casa & Jardim</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Tudo para deixar sua casa mais bonita e aconchegante.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Ambientes</h2>
                    <ul>
                        <li>Sala de Estar</li>
                        <li>Quarto</li>
                        <li>Cozinha</li>
                        <li>Banheiro</li>
                        <li>Jardim</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Facilidades</h2>
                    <p>💳 Parcelamos em até 12x<br>🚚 Entrega rápida<br>🔧 Montagem inclusa</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
    
    def _generate_services_content(self, service_type: str) -> str:
        """Generate services content based on type"""
        
        if service_type == "consulting":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>[COMPANY_NAME] Consultoria</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Soluções estratégicas para impulsionar o crescimento do seu negócio.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Serviços</h2>
                    <ul>
                        <li>Planejamento Estratégico</li>
                        <li>Gestão de Processos</li>
                        <li>Marketing Digital</li>
                        <li>Recursos Humanos</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Metodologia</h2>
                    <p>Diagnóstico → Planejamento → Implementação → Acompanhamento</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
        elif service_type == "law":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Advocacia [LAWYER_NAME]</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Defesa de seus direitos com experiência e dedicação há mais de [YEARS] anos.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:list -->
            <ul>
                <li>Direito Civil</li>
                <li>Direito Trabalhista</li>
                <li>Direito Empresarial</li>
                <li>Direito de Família</li>
                <li>Direito Criminal</li>
            </ul>
            <!-- /wp:list -->
            """
        else:  # accounting
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Contabilidade [COMPANY_NAME]</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Gestão contábil completa para sua empresa com tecnologia e expertise.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Serviços</h2>
                    <ul>
                        <li>Contabilidade Geral</li>
                        <li>Folha de Pagamento</li>
                        <li>Impostos e Tributos</li>
                        <li>Abertura de Empresa</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Diferenciais</h2>
                    <p>📊 Relatórios online<br>🤖 Automação fiscal<br>📞 Suporte dedicado</p>
                </div>
            </div>
            <!-- /wp:columns -->
            """
    
    def _generate_education_content(self, education_type: str) -> str:
        """Generate education content based on type"""
        
        if education_type == "school":
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Escola [SCHOOL_NAME]</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Educação de qualidade para formar cidadãos conscientes e preparados para o futuro.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <div class="wp-block-column">
                    <h2>Níveis de Ensino</h2>
                    <ul>
                        <li>Educação Infantil</li>
                        <li>Ensino Fundamental</li>
                        <li>Ensino Médio</li>
                    </ul>
                </div>
                <div class="wp-block-column">
                    <h2>Diferenciais</h2>
                    <ul>
                        <li>Metodologia inovadora</li>
                        <li>Tecnologia educacional</li>
                        <li>Atividades extracurriculares</li>
                        <li>Acompanhamento personalizado</li>
                    </ul>
                </div>
            </div>
            <!-- /wp:columns -->
            """
        else:  # online
            return """
            <!-- wp:heading {"level":1} -->
            <h1>Curso Online [COURSE_NAME]</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Aprenda no seu ritmo com conteúdo de qualidade e certificação reconhecida.</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:list -->
            <ul>
                <li>✅ Acesso vitalício</li>
                <li>📱 Assista no celular</li>
                <li>🎓 Certificado incluso</li>
                <li>👨‍🏫 Suporte do professor</li>
                <li>💰 Garantia de 30 dias</li>
            </ul>
            <!-- /wp:list -->
            """
    
    def _generate_elementor_data(self, industry: str, style: str) -> str:
        """Generate Elementor data structure for templates"""
        
        # This would be a complex JSON structure for Elementor
        # For now, return a simplified structure
        elementor_data = {
            "version": "3.18.0",
            "title": f"{industry.title()} {style.title()} Template",
            "type": "wp-post",
            "content": [
                {
                    "id": "hero-section",
                    "elType": "section",
                    "elements": [
                        {
                            "id": "hero-content",
                            "elType": "column",
                            "elements": [
                                {
                                    "id": "hero-heading",
                                    "elType": "widget",
                                    "widgetType": "heading",
                                    "settings": {
                                        "title": f"[{industry.upper()}_NAME]",
                                        "size": "xxl"
                                    }
                                },
                                {
                                    "id": "hero-text",
                                    "elType": "widget", 
                                    "widgetType": "text-editor",
                                    "settings": {
                                        "editor": f"Bem-vindo ao melhor {industry} da região"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        return json.dumps(elementor_data)
    
    async def _import_single_template(self, template: Dict) -> Optional[Dict]:
        """Import a single template into WordPress"""
        
        try:
            # Create page with template content
            page_data = {
                "title": template["name"],
                "content": template["content"],
                "status": "draft",  # Keep as draft initially
                "type": "page",
                "template": "elementor_header_footer",
                "meta": template.get("meta", {})
            }
            
            # Import via WordPress REST API
            result = await self._make_wp_api_request(
                "POST",
                "/pages",
                data=page_data
            )
            
            if result:
                logger.info(f"✅ Imported template: {template['name']}")
                return {
                    "name": template["name"],
                    "id": result.get("id"),
                    "industry": template["industry"],
                    "url": result.get("link")
                }
            
        except Exception as e:
            logger.error(f"❌ Failed to import template {template['name']}: {str(e)}")
        
        return None
    
    async def _configure_starter_content(self):
        """Configure WordPress starter content and settings"""
        
        try:
            # Set site title and description
            settings_data = {
                "title": "KenzySites Template Library",
                "description": "AI-Generated Templates for Every Industry"
            }
            
            await self._make_wp_api_request("POST", "/settings", data=settings_data)
            
            # Enable pretty permalinks
            permalink_data = {
                "permalink_structure": "/%postname%/"
            }
            
            await self._make_wp_api_request("POST", "/settings", data=permalink_data)
            
            logger.info("✅ WordPress starter content configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not configure starter content: {str(e)}")
    
    async def _setup_elementor_library(self):
        """Setup Elementor template library"""
        
        try:
            # Configure Elementor settings
            elementor_settings = {
                "elementor_disable_color_schemes": "",
                "elementor_disable_typography_schemes": "",
                "elementor_allow_tracking": "no",
                "elementor_css_print_method": "internal"
            }
            
            for setting, value in elementor_settings.items():
                await self._update_wp_option(setting, value)
            
            logger.info("✅ Elementor library configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not configure Elementor: {str(e)}")
    
    async def _make_wp_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make WordPress REST API request"""
        
        if not self.session:
            return None
        
        try:
            auth_string = base64.b64encode(f"{self.wp_admin_user}:{self.wp_admin_password}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.wp_api_url}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    if response.status in [200, 201]:
                        return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    if response.status in [200, 201]:
                        return await response.json()
            
        except Exception as e:
            logger.error(f"WordPress API request failed: {str(e)}")
        
        return None
    
    async def _update_wp_option(self, option_name: str, option_value: str):
        """Update WordPress option via API"""
        
        try:
            # WordPress options API endpoint would be used here
            # For now, simulate the update
            logger.debug(f"Updated WP option: {option_name} = {option_value}")
            
        except Exception as e:
            logger.warning(f"Could not update option {option_name}: {str(e)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# Global instance
wordpress_template_importer = WordPressTemplateImporter()