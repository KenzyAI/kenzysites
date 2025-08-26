"""
WordPress Integration Service
Connects KenzySites AI generation with real WordPress instance
"""

import asyncio
import logging
import json
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import hashlib

logger = logging.getLogger(__name__)

class WordPressIntegration:
    """
    Real WordPress integration for KenzySites
    Connects to running WordPress instance via REST API
    """
    
    def __init__(self):
        # WordPress instance running at localhost:8085
        self.wp_base_url = "http://localhost:8085"
        self.wp_api_url = f"{self.wp_base_url}/wp-json/wp/v2"
        self.wp_admin_user = "admin"
        self.wp_admin_password = "admin123"
        
        # Authentication
        self.auth_token = None
        self.session = None
        
    async def initialize(self):
        """Initialize WordPress connection"""
        
        self.session = aiohttp.ClientSession()
        
        try:
            # Test WordPress connection
            async with self.session.get(f"{self.wp_base_url}/wp-json") as response:
                if response.status == 200:
                    wp_info = await response.json()
                    logger.info(f"✅ Connected to WordPress: {wp_info.get('name', 'Unknown')}")
                    return True
                else:
                    logger.error(f"❌ WordPress not accessible: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ WordPress connection failed: {str(e)}")
            return False
    
    async def create_site_from_variations(
        self, 
        variation_data: Dict[str, Any], 
        selected_variation_index: int = 0
    ) -> Dict[str, Any]:
        """
        Create WordPress site from generated variations
        """
        
        if not self.session:
            await self.initialize()
        
        try:
            variation = variation_data['variations'][selected_variation_index]
            business_name = variation_data.get('business_name', 'Site Gerado')
            industry = variation_data.get('industry', 'general')
            
            logger.info(f"🎨 Creating WordPress site for: {business_name}")
            
            # 1. Create Home Page
            home_page = await self._create_home_page(variation, business_name, industry)
            
            # 2. Create About Page  
            about_page = await self._create_about_page(variation, business_name, industry)
            
            # 3. Create Contact Page
            contact_page = await self._create_contact_page(variation, business_name, industry)
            
            # 4. Create Services/Products Page (based on industry)
            services_page = await self._create_services_page(variation, business_name, industry)
            
            # 5. Update site settings
            await self._update_site_settings(variation, business_name)
            
            # 6. Set homepage
            if home_page:
                await self._set_homepage(home_page['id'])
            
            result = {
                'success': True,
                'site_url': self.wp_base_url,
                'admin_url': f"{self.wp_base_url}/wp-admin",
                'pages_created': [
                    {'title': 'Home', 'id': home_page.get('id') if home_page else None, 'url': self.wp_base_url},
                    {'title': 'Sobre', 'id': about_page.get('id') if about_page else None, 'url': f"{self.wp_base_url}/sobre"},
                    {'title': 'Contato', 'id': contact_page.get('id') if contact_page else None, 'url': f"{self.wp_base_url}/contato"},
                    {'title': 'Serviços', 'id': services_page.get('id') if services_page else None, 'url': f"{self.wp_base_url}/servicos"}
                ],
                'variation_used': selected_variation_index,
                'color_scheme': variation.get('color_scheme', {}),
                'typography': variation.get('typography', {}),
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ WordPress site created successfully for {business_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to create WordPress site: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'site_url': None
            }
    
    async def _create_home_page(self, variation: Dict, business_name: str, industry: str) -> Optional[Dict]:
        """Create homepage with variation styling"""
        
        colors = variation.get('color_scheme', {})
        typography = variation.get('typography', {})
        features = variation.get('features', [])
        
        # Generate industry-specific content
        if industry == 'restaurant':
            headline = f"Sabores Autênticos da Nossa Cozinha - {business_name}"
            description = "Descubra pratos únicos preparados com ingredientes frescos e técnicas tradicionais."
            cta_text = "Ver Cardápio"
        elif industry == 'healthcare':
            headline = f"Cuidando da Sua Saúde com Excelência - {business_name}"
            description = "Atendimento médico especializado com tecnologia de ponta e cuidado humanizado."
            cta_text = "Agendar Consulta"
        elif industry == 'ecommerce':
            headline = f"Produtos Premium para Você - {business_name}"
            description = "Encontre os melhores produtos com qualidade garantida e entrega rápida."
            cta_text = "Ver Produtos"
        else:
            headline = f"Soluções Profissionais de Qualidade - {business_name}"
            description = "Serviços especializados para atender às suas necessidades com excelência."
            cta_text = "Saiba Mais"
        
        # Create WordPress page content with styling
        content = f'''
        <!-- wp:cover {{"url":"","dimRatio":0,"overlayColor":"{colors.get('primary', '#2196F3')}"}} -->
        <div class="wp-block-cover" style="background: linear-gradient(135deg, {colors.get('primary', '#2196F3')}15, {colors.get('secondary', '#03A9F4')}10); padding: 4rem 2rem;">
            <div class="wp-block-cover__inner-container" style="text-align: center; max-width: 800px; margin: 0 auto;">
                <!-- wp:heading {{"level":1,"style":{{"color":{{"text":"{colors.get('primary', '#2196F3')}"}},"typography":{{"fontSize":"3rem","fontFamily":"{typography.get('heading_font', 'Inter')}"}}}}}} -->
                <h1 style="color: {colors.get('primary', '#2196F3')}; font-family: {typography.get('heading_font', 'Inter')}; font-size: 3rem; margin-bottom: 1rem;">
                    {headline}
                </h1>
                <!-- /wp:heading -->
                
                <!-- wp:paragraph {{"style":{{"typography":{{"fontSize":"1.2rem","fontFamily":"{typography.get('body_font', 'Inter')}"}}}}}} -->
                <p style="font-family: {typography.get('body_font', 'Inter')}; font-size: 1.2rem; margin-bottom: 2rem; line-height: 1.6;">
                    {description}
                </p>
                <!-- /wp:paragraph -->
                
                <!-- wp:buttons {{"layout":{{"type":"flex","justifyContent":"center"}}}} -->
                <div class="wp-block-buttons">
                    <!-- wp:button {{"backgroundColor":"primary","style":{{"color":{{"background":"{colors.get('primary', '#2196F3')}"}}}}}} -->
                    <div class="wp-block-button">
                        <a class="wp-block-button__link" style="background-color: {colors.get('primary', '#2196F3')}; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none;">
                            {cta_text}
                        </a>
                    </div>
                    <!-- /wp:button -->
                </div>
                <!-- /wp:buttons -->
            </div>
        </div>
        <!-- /wp:cover -->
        
        <!-- wp:columns {{"style":{{"spacing":{{"padding":{{"top":"3rem","bottom":"3rem"}}}}}}}} -->
        <div class="wp-block-columns" style="padding-top: 3rem; padding-bottom: 3rem;">
            {self._generate_features_columns(features[:3], colors)}
        </div>
        <!-- /wp:columns -->
        
        <!-- wp:paragraph {{"align":"center","style":{{"typography":{{"fontSize":"1rem"}}}}}} -->
        <p style="text-align: center; font-size: 1rem; padding: 2rem; background-color: {colors.get('background', '#FFFFFF')};">
            Criado com ❤️ pela <strong>KenzySites AI</strong> - Tecnologia que transforma ideias em realidade.
        </p>
        <!-- /wp:paragraph -->
        '''
        
        page_data = {
            'title': 'Home',
            'content': content,
            'status': 'publish',
            'type': 'page',
            'slug': 'home'
        }
        
        return await self._create_wp_page(page_data)
    
    async def _create_about_page(self, variation: Dict, business_name: str, industry: str) -> Optional[Dict]:
        """Create about page"""
        
        colors = variation.get('color_scheme', {})
        typography = variation.get('typography', {})
        
        if industry == 'restaurant':
            content_text = f"O {business_name} nasceu da paixão pela culinária e do desejo de oferecer uma experiência gastronômica única. Nossa história começou com a vontade de preservar sabores autênticos e criar novos momentos especiais para nossos clientes."
        elif industry == 'healthcare':
            content_text = f"A {business_name} foi fundada com o compromisso de oferecer cuidados médicos de excelência. Nossa equipe de profissionais especializados trabalha dedicadamente para proporcionar o melhor atendimento e cuidado humanizado."
        else:
            content_text = f"A {business_name} é uma empresa comprometida com a excelência e inovação. Trabalhamos incansavelmente para oferecer soluções de qualidade que superem as expectativas de nossos clientes."
        
        content = f'''
        <!-- wp:heading {{"level":1,"style":{{"color":{{"text":"{colors.get('primary', '#2196F3')}"}}}}}} -->
        <h1 style="color: {colors.get('primary', '#2196F3')};">Sobre Nós</h1>
        <!-- /wp:heading -->
        
        <!-- wp:paragraph -->
        <p style="font-size: 1.1rem; line-height: 1.7; margin-bottom: 2rem;">
            {content_text}
        </p>
        <!-- /wp:paragraph -->
        
        <!-- wp:heading {{"level":2}} -->
        <h2>Nossa Missão</h2>
        <!-- /wp:heading -->
        
        <!-- wp:paragraph -->
        <p>Proporcionar experiências excepcionais através de serviços de alta qualidade, sempre priorizando a satisfação e bem-estar de nossos clientes.</p>
        <!-- /wp:paragraph -->
        
        <!-- wp:heading {{"level":2}} -->
        <h2>Nossos Valores</h2>
        <!-- /wp:heading -->
        
        <!-- wp:list -->
        <ul>
            <li>Excelência em tudo que fazemos</li>
            <li>Comprometimento com nossos clientes</li>
            <li>Inovação constante</li>
            <li>Transparência e confiabilidade</li>
        </ul>
        <!-- /wp:list -->
        '''
        
        page_data = {
            'title': 'Sobre Nós',
            'content': content,
            'status': 'publish',
            'type': 'page',
            'slug': 'sobre'
        }
        
        return await self._create_wp_page(page_data)
    
    async def _create_contact_page(self, variation: Dict, business_name: str, industry: str) -> Optional[Dict]:
        """Create contact page"""
        
        colors = variation.get('color_scheme', {})
        
        content = f'''
        <!-- wp:heading {{"level":1,"style":{{"color":{{"text":"{colors.get('primary', '#2196F3')}"}}}}}} -->
        <h1 style="color: {colors.get('primary', '#2196F3')};">Entre em Contato</h1>
        <!-- /wp:heading -->
        
        <!-- wp:paragraph -->
        <p>Estamos aqui para ajudar! Entre em contato conosco através dos canais abaixo:</p>
        <!-- /wp:paragraph -->
        
        <!-- wp:columns -->
        <div class="wp-block-columns">
            <!-- wp:column -->
            <div class="wp-block-column">
                <!-- wp:heading {{"level":3}} -->
                <h3>📞 Telefone</h3>
                <!-- /wp:heading -->
                
                <!-- wp:paragraph -->
                <p>(11) 99999-9999</p>
                <!-- /wp:paragraph -->
            </div>
            <!-- /wp:column -->
            
            <!-- wp:column -->
            <div class="wp-block-column">
                <!-- wp:heading {{"level":3}} -->
                <h3>📧 Email</h3>
                <!-- /wp:heading -->
                
                <!-- wp:paragraph -->
                <p>contato@{business_name.lower().replace(' ', '')}.com.br</p>
                <!-- /wp:paragraph -->
            </div>
            <!-- /wp:column -->
            
            <!-- wp:column -->
            <div class="wp-block-column">
                <!-- wp:heading {{"level":3}} -->
                <h3>💬 WhatsApp</h3>
                <!-- /wp:heading -->
                
                <!-- wp:paragraph -->
                <p>
                    <a href="https://wa.me/5511999999999" style="color: {colors.get('primary', '#2196F3')}; text-decoration: none;">
                        Fale conosco no WhatsApp
                    </a>
                </p>
                <!-- /wp:paragraph -->
            </div>
            <!-- /wp:column -->
        </div>
        <!-- /wp:columns -->
        
        <!-- wp:separator -->
        <hr class="wp-block-separator"/>
        <!-- /wp:separator -->
        
        <!-- wp:paragraph -->
        <p><strong>Horário de Atendimento:</strong><br>
        Segunda a Sexta: 8h às 18h<br>
        Sábado: 8h às 12h</p>
        <!-- /wp:paragraph -->
        '''
        
        page_data = {
            'title': 'Contato',
            'content': content,
            'status': 'publish',
            'type': 'page',
            'slug': 'contato'
        }
        
        return await self._create_wp_page(page_data)
    
    async def _create_services_page(self, variation: Dict, business_name: str, industry: str) -> Optional[Dict]:
        """Create services/products page based on industry"""
        
        colors = variation.get('color_scheme', {})
        
        if industry == 'restaurant':
            title = "Cardápio"
            slug = "cardapio"
            content = f'''
            <!-- wp:heading {{"level":1,"style":{{"color":{{"text":"{colors.get('primary', '#2196F3')}"}}}}}} -->
            <h1 style="color: {colors.get('primary', '#2196F3')};">Nosso Cardápio</h1>
            <!-- /wp:heading -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <!-- wp:column -->
                <div class="wp-block-column">
                    <!-- wp:heading {{"level":2}} -->
                    <h2>Pratos Principais</h2>
                    <!-- /wp:heading -->
                    
                    <!-- wp:list -->
                    <ul>
                        <li>Prato Especial da Casa - R$ 35,00</li>
                        <li>Grelhados Selecionados - R$ 28,00</li>
                        <li>Massa Artesanal - R$ 22,00</li>
                    </ul>
                    <!-- /wp:list -->
                </div>
                <!-- /wp:column -->
                
                <!-- wp:column -->
                <div class="wp-block-column">
                    <!-- wp:heading {{"level":2}} -->
                    <h2>Bebidas</h2>
                    <!-- /wp:heading -->
                    
                    <!-- wp:list -->
                    <ul>
                        <li>Sucos Naturais - R$ 8,00</li>
                        <li>Refrigerantes - R$ 6,00</li>
                        <li>Cafés Especiais - R$ 12,00</li>
                    </ul>
                    <!-- /wp:list -->
                </div>
                <!-- /wp:column -->
            </div>
            <!-- /wp:columns -->
            '''
        elif industry == 'healthcare':
            title = "Serviços"
            slug = "servicos"
            content = f'''
            <!-- wp:heading {{"level":1,"style":{{"color":{{"text":"{colors.get('primary', '#2196F3')}"}}}}}} -->
            <h1 style="color: {colors.get('primary', '#2196F3')};">Nossos Serviços</h1>
            <!-- /wp:heading -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <!-- wp:column -->
                <div class="wp-block-column">
                    <!-- wp:heading {{"level":2}} -->
                    <h2>Consultas</h2>
                    <!-- /wp:heading -->
                    
                    <!-- wp:list -->
                    <ul>
                        <li>Consulta Geral</li>
                        <li>Consulta Especializada</li>
                        <li>Telemedicina</li>
                    </ul>
                    <!-- /wp:list -->
                </div>
                <!-- /wp:column -->
                
                <!-- wp:column -->
                <div class="wp-block-column">
                    <!-- wp:heading {{"level":2}} -->
                    <h2>Exames</h2>
                    <!-- /wp:heading -->
                    
                    <!-- wp:list -->
                    <ul>
                        <li>Exames Laboratoriais</li>
                        <li>Exames de Imagem</li>
                        <li>Check-up Completo</li>
                    </ul>
                    <!-- /wp:list -->
                </div>
                <!-- /wp:column -->
            </div>
            <!-- /wp:columns -->
            '''
        else:
            title = "Serviços"
            slug = "servicos"
            content = f'''
            <!-- wp:heading {{"level":1,"style":{{"color":{{"text":"{colors.get('primary', '#2196F3')}"}}}}}} -->
            <h1 style="color: {colors.get('primary', '#2196F3')};">Nossos Serviços</h1>
            <!-- /wp:heading -->
            
            <!-- wp:paragraph -->
            <p>Oferecemos soluções completas e personalizadas para atender às suas necessidades:</p>
            <!-- /wp:paragraph -->
            
            <!-- wp:columns -->
            <div class="wp-block-columns">
                <!-- wp:column -->
                <div class="wp-block-column">
                    <!-- wp:heading {{"level":2}} -->
                    <h2>Serviço Premium</h2>
                    <!-- /wp:heading -->
                    
                    <!-- wp:paragraph -->
                    <p>Atendimento personalizado com as melhores soluções do mercado.</p>
                    <!-- /wp:paragraph -->
                </div>
                <!-- /wp:column -->
                
                <!-- wp:column -->
                <div class="wp-block-column">
                    <!-- wp:heading {{"level":2}} -->
                    <h2>Consultoria</h2>
                    <!-- /wp:heading -->
                    
                    <!-- wp:paragraph -->
                    <p>Análise especializada para otimizar seus processos e resultados.</p>
                    <!-- /wp:paragraph -->
                </div>
                <!-- /wp:column -->
            </div>
            <!-- /wp:columns -->
            '''
        
        page_data = {
            'title': title,
            'content': content,
            'status': 'publish',
            'type': 'page',
            'slug': slug
        }
        
        return await self._create_wp_page(page_data)
    
    def _generate_features_columns(self, features: List[str], colors: Dict) -> str:
        """Generate features columns HTML"""
        
        if not features:
            features = ["Qualidade", "Confiança", "Excelência"]
        
        columns_html = ""
        for i, feature in enumerate(features):
            columns_html += f'''
            <!-- wp:column -->
            <div class="wp-block-column">
                <div style="text-align: center; padding: 1.5rem;">
                    <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {colors.get('accent', '#FFC107')}20; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center;">
                        <div style="width: 24px; height: 24px; border-radius: 4px; background-color: {colors.get('accent', '#FFC107')};"></div>
                    </div>
                    
                    <!-- wp:heading {{"level":3,"style":{{"color":{{"text":"{colors.get('text', '#2C3E50')}"}}}}}} -->
                    <h3 style="color: {colors.get('text', '#2C3E50')};">{feature}</h3>
                    <!-- /wp:heading -->
                    
                    <!-- wp:paragraph -->
                    <p>Descrição do {feature.lower()} que oferecemos com excelência e dedicação.</p>
                    <!-- /wp:paragraph -->
                </div>
            </div>
            <!-- /wp:column -->
            '''
        
        return columns_html
    
    async def _create_wp_page(self, page_data: Dict) -> Optional[Dict]:
        """Create page in WordPress via REST API"""
        
        try:
            # Use basic auth (for local development)
            auth_string = base64.b64encode(f"{self.wp_admin_user}:{self.wp_admin_password}".encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(
                f"{self.wp_api_url}/pages", 
                headers=headers, 
                json=page_data
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"✅ Created page: {page_data['title']} (ID: {result.get('id')})")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create page {page_data['title']}: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating page {page_data['title']}: {str(e)}")
            return None
    
    async def _update_site_settings(self, variation: Dict, business_name: str):
        """Update WordPress site settings"""
        
        try:
            # Update site title
            settings_data = {
                'title': business_name,
                'description': f'Site criado pela KenzySites AI - {business_name}'
            }
            
            auth_string = base64.b64encode(f"{self.wp_admin_user}:{self.wp_admin_password}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(
                f"{self.wp_api_url}/settings",
                headers=headers,
                json=settings_data
            ) as response:
                if response.status in [200, 201]:
                    logger.info(f"✅ Updated site settings for {business_name}")
                else:
                    logger.warning(f"⚠️ Could not update site settings: {response.status}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error updating site settings: {str(e)}")
    
    async def _set_homepage(self, page_id: int):
        """Set page as homepage"""
        
        try:
            # Set show_on_front to 'page' and page_on_front to our page ID
            settings_data = {
                'show_on_front': 'page',
                'page_on_front': page_id
            }
            
            auth_string = base64.b64encode(f"{self.wp_admin_user}:{self.wp_admin_password}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(
                f"{self.wp_api_url}/settings",
                headers=headers,
                json=settings_data
            ) as response:
                if response.status in [200, 201]:
                    logger.info(f"✅ Set page {page_id} as homepage")
                else:
                    logger.warning(f"⚠️ Could not set homepage: {response.status}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Error setting homepage: {str(e)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# Global instance
wordpress_integration = WordPressIntegration()