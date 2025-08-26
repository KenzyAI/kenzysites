"""
Template Library Service - Manages WordPress templates for AI generation
Handles template loading, selection, and placeholder management
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import hashlib
from enum import Enum

from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

class TemplateIndustry(str, Enum):
    """Available template industries"""
    RESTAURANT = "restaurant"
    HEALTHCARE = "healthcare" 
    ECOMMERCE = "ecommerce"
    SERVICES = "services"
    EDUCATION = "education"
    GENERAL = "general"

class TemplateComplexity(str, Enum):
    """Template complexity levels"""
    SIMPLE = "simple"      # 3-4 pages, basic features
    STANDARD = "standard"  # 5-7 pages, moderate features
    ADVANCED = "advanced"  # 8+ pages, full features

class TemplatePage(BaseModel):
    """Individual page in a template"""
    slug: str
    title: str
    template: str = "elementor"
    sections: List[Dict[str, Any]]
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class TemplateDesign(BaseModel):
    """Design configuration for template"""
    colors: Dict[str, str]
    typography: Dict[str, str]
    spacing: Dict[str, str]
    animations: Optional[Dict[str, Any]] = None

class TemplateSEO(BaseModel):
    """SEO configuration for template"""
    meta_title: str
    meta_description: str
    keywords: List[str]
    og_image: Optional[str] = None
    schema_type: str = "Organization"

class BrazilianFeatures(BaseModel):
    """Brazilian-specific features configuration"""
    whatsapp_widget: Dict[str, Any]
    pix_payment: Dict[str, Any]
    lgpd_notice: Dict[str, Any]
    delivery_integrations: Optional[Dict[str, str]] = None
    social_links: Optional[Dict[str, str]] = None

class WordPressTemplate(BaseModel):
    """Complete WordPress template structure"""
    id: str
    name: str
    industry: TemplateIndustry
    version: str = "1.0.0"
    description: str
    language: str = "pt-BR"
    complexity: TemplateComplexity = TemplateComplexity.STANDARD
    features: List[str]
    pages: List[TemplatePage]
    navigation: Dict[str, Any]
    design: TemplateDesign
    seo: TemplateSEO
    brazilian_features: BrazilianFeatures
    plugins_required: List[str]
    acf_fields: List[Dict[str, Any]]
    placeholders: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    usage_count: int = 0
    rating: float = 0.0

class TemplateLibrary:
    """
    Central template library manager
    Handles loading, caching, and selection of WordPress templates
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_cache: Dict[str, WordPressTemplate] = {}
        self.loaded = False
        self._load_templates()
        
    def _load_templates(self):
        """Load all templates from the templates directory"""
        try:
            logger.info(f"Loading templates from {self.templates_dir}")
            
            # Scan all industry directories
            for industry_dir in self.templates_dir.iterdir():
                if industry_dir.is_dir() and not industry_dir.name.startswith('.'):
                    template_file = industry_dir / "template.json"
                    
                    if template_file.exists():
                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                template_data = json.load(f)
                                
                            # Convert to WordPressTemplate model
                            template = self._parse_template(template_data)
                            
                            # Cache the template
                            self.templates_cache[template.id] = template
                            
                            logger.info(f"✅ Loaded template: {template.id} ({template.name})")
                            
                        except Exception as e:
                            logger.error(f"Error loading template from {template_file}: {str(e)}")
            
            self.loaded = True
            logger.info(f"Loaded {len(self.templates_cache)} templates successfully")
            
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
    
    def _parse_template(self, data: Dict[str, Any]) -> WordPressTemplate:
        """Parse raw template data into WordPressTemplate model"""
        
        # Parse pages
        pages = []
        for page_data in data.get('pages', []):
            page = TemplatePage(
                slug=page_data['slug'],
                title=page_data['title'],
                template=page_data.get('template', 'elementor'),
                sections=page_data.get('sections', []),
                meta_title=page_data.get('meta_title'),
                meta_description=page_data.get('meta_description')
            )
            pages.append(page)
        
        # Parse design
        design = TemplateDesign(**data.get('design', {
            'colors': {'primary': '#0066FF', 'secondary': '#00D4FF'},
            'typography': {'heading_font': 'Inter', 'body_font': 'Inter'},
            'spacing': {'section_padding': '80px', 'container_width': '1200px'}
        }))
        
        # Parse SEO
        seo = TemplateSEO(**data.get('seo', {
            'meta_title': data.get('name', 'Website'),
            'meta_description': data.get('description', ''),
            'keywords': []
        }))
        
        # Parse Brazilian features
        brazilian_features = BrazilianFeatures(**data.get('brazilian_features', {
            'whatsapp_widget': {'enabled': True, 'position': 'bottom-right'},
            'pix_payment': {'enabled': True},
            'lgpd_notice': {'enabled': True, 'text': 'Este site usa cookies.'}
        }))
        
        # Determine complexity based on pages count
        page_count = len(pages)
        if page_count <= 4:
            complexity = TemplateComplexity.SIMPLE
        elif page_count <= 7:
            complexity = TemplateComplexity.STANDARD
        else:
            complexity = TemplateComplexity.ADVANCED
        
        # Create template object
        template = WordPressTemplate(
            id=data['id'],
            name=data['name'],
            industry=TemplateIndustry(data.get('industry', 'general')),
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            language=data.get('language', 'pt-BR'),
            complexity=complexity,
            features=data.get('features', []),
            pages=pages,
            navigation=data.get('navigation', {}),
            design=design,
            seo=seo,
            brazilian_features=brazilian_features,
            plugins_required=data.get('plugins_required', []),
            acf_fields=data.get('acf_fields', []),
            placeholders=data.get('placeholders', []),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return template
    
    def get_template(self, template_id: str) -> Optional[WordPressTemplate]:
        """Get a specific template by ID"""
        return self.templates_cache.get(template_id)
    
    def get_templates_by_industry(self, industry: TemplateIndustry) -> List[WordPressTemplate]:
        """Get all templates for a specific industry"""
        return [
            template for template in self.templates_cache.values()
            if template.industry == industry
        ]
    
    def get_all_templates(self) -> List[WordPressTemplate]:
        """Get all available templates"""
        return list(self.templates_cache.values())
    
    def select_best_template(
        self, 
        industry: str, 
        business_type: str,
        features_needed: List[str] = None,
        complexity: TemplateComplexity = TemplateComplexity.STANDARD
    ) -> Optional[WordPressTemplate]:
        """
        Select the best template based on business requirements
        Uses scoring algorithm to find best match
        """
        
        candidates = self.get_templates_by_industry(TemplateIndustry(industry.lower()))
        
        if not candidates:
            # Fallback to general templates
            candidates = self.get_templates_by_industry(TemplateIndustry.GENERAL)
        
        if not candidates:
            logger.warning(f"No templates found for industry: {industry}")
            return None
        
        # Score each candidate
        best_template = None
        best_score = 0
        
        for template in candidates:
            score = 0
            
            # Match complexity
            if template.complexity == complexity:
                score += 30
            elif abs(list(TemplateComplexity).index(template.complexity) - 
                    list(TemplateComplexity).index(complexity)) == 1:
                score += 15
            
            # Match features
            if features_needed:
                matched_features = set(template.features) & set(features_needed)
                score += len(matched_features) * 10
            
            # Prefer higher rated templates
            score += template.rating * 5
            
            # Prefer more recently updated
            if template.updated_at:
                days_old = (datetime.now() - template.updated_at).days
                if days_old < 30:
                    score += 10
                elif days_old < 90:
                    score += 5
            
            # Check business type compatibility
            if business_type.lower() in template.description.lower():
                score += 20
            
            if score > best_score:
                best_score = score
                best_template = template
        
        logger.info(f"Selected template: {best_template.id} with score: {best_score}")
        return best_template
    
    def get_template_placeholders(self, template_id: str) -> List[str]:
        """Get all placeholders used in a template"""
        template = self.get_template(template_id)
        if template:
            return template.placeholders
        return []
    
    def generate_placeholder_values(
        self, 
        template: WordPressTemplate,
        business_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate default values for template placeholders
        based on business data
        """
        
        placeholder_values = {}
        
        # Basic business information
        placeholder_values['{{BUSINESS_NAME}}'] = business_data.get('business_name', 'Minha Empresa')
        placeholder_values['{{BUSINESS_DESCRIPTION}}'] = business_data.get('description', 'Descrição do negócio')
        placeholder_values['{{BUSINESS_TAGLINE}}'] = business_data.get('tagline', 'Seu slogan aqui')
        
        # Contact information
        placeholder_values['{{PHONE_NUMBER}}'] = business_data.get('phone', '(11) 1234-5678')
        placeholder_values['{{WHATSAPP_NUMBER}}'] = business_data.get('whatsapp', '(11) 91234-5678')
        placeholder_values['{{EMAIL}}'] = business_data.get('email', 'contato@exemplo.com.br')
        placeholder_values['{{ADDRESS}}'] = business_data.get('address', 'Rua Exemplo, 123 - São Paulo, SP')
        placeholder_values['{{CITY}}'] = business_data.get('city', 'São Paulo')
        
        # Business hours
        placeholder_values['{{OPENING_HOURS}}'] = business_data.get('opening_hours', 'Seg-Sex: 9h às 18h')
        
        # Hero section
        placeholder_values['{{HERO_TITLE}}'] = business_data.get('hero_title', f"Bem-vindo à {business_data.get('business_name', 'Nossa Empresa')}")
        placeholder_values['{{HERO_SUBTITLE}}'] = business_data.get('hero_subtitle', 'Qualidade e excelência em nossos serviços')
        
        # About section
        placeholder_values['{{ABOUT_TITLE}}'] = business_data.get('about_title', 'Sobre Nós')
        placeholder_values['{{ABOUT_TEXT}}'] = business_data.get('about_text', 'Somos uma empresa dedicada a oferecer os melhores serviços.')
        
        # Design colors
        placeholder_values['{{PRIMARY_COLOR}}'] = business_data.get('primary_color', template.design.colors.get('primary', '#0066FF'))
        placeholder_values['{{SECONDARY_COLOR}}'] = business_data.get('secondary_color', template.design.colors.get('secondary', '#00D4FF'))
        placeholder_values['{{ACCENT_COLOR}}'] = business_data.get('accent_color', template.design.colors.get('accent', '#FF6B35'))
        
        # Payment and integrations
        placeholder_values['{{PIX_KEY}}'] = business_data.get('pix_key', 'pix@exemplo.com.br')
        placeholder_values['{{CNPJ}}'] = business_data.get('cnpj', '00.000.000/0001-00')
        
        # Social media
        placeholder_values['{{INSTAGRAM_USERNAME}}'] = business_data.get('instagram', '@exemplo')
        placeholder_values['{{FACEBOOK_URL}}'] = business_data.get('facebook', 'https://facebook.com/exemplo')
        
        # Industry-specific placeholders
        if template.industry == TemplateIndustry.RESTAURANT:
            placeholder_values.update(self._generate_restaurant_placeholders(business_data))
        elif template.industry == TemplateIndustry.HEALTHCARE:
            placeholder_values.update(self._generate_healthcare_placeholders(business_data))
        elif template.industry == TemplateIndustry.ECOMMERCE:
            placeholder_values.update(self._generate_ecommerce_placeholders(business_data))
        
        return placeholder_values
    
    def _generate_restaurant_placeholders(self, business_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate restaurant-specific placeholder values"""
        return {
            '{{CHEF_NAME}}': business_data.get('chef_name', 'Chef Principal'),
            '{{CUISINE_TYPE}}': business_data.get('cuisine_type', 'Brasileira'),
            '{{DELIVERY_AREAS}}': business_data.get('delivery_areas', 'Centro, Zona Sul, Zona Norte'),
            '{{MENU_ITEM_1_NAME}}': 'Prato do Dia',
            '{{MENU_ITEM_1_DESC}}': 'Delicioso prato preparado diariamente',
            '{{MENU_ITEM_1_PRICE}}': 'R$ 25,00',
            '{{IFOOD_LINK}}': business_data.get('ifood_link', '#'),
            '{{UBER_EATS_LINK}}': business_data.get('uber_eats_link', '#'),
            '{{YEARS_EXPERIENCE}}': business_data.get('years_experience', '10')
        }
    
    def _generate_healthcare_placeholders(self, business_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate healthcare-specific placeholder values"""
        return {
            '{{DOCTOR_NAME}}': business_data.get('doctor_name', 'Dr. Exemplo'),
            '{{SPECIALTIES}}': business_data.get('specialties', 'Clínica Geral, Pediatria'),
            '{{INSURANCE_ACCEPTED}}': business_data.get('insurance', 'Unimed, Bradesco, SulAmérica'),
            '{{EMERGENCY_PHONE}}': business_data.get('emergency_phone', '(11) 9999-9999'),
            '{{APPOINTMENT_LINK}}': business_data.get('appointment_link', '#agendar')
        }
    
    def _generate_ecommerce_placeholders(self, business_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate e-commerce-specific placeholder values"""
        return {
            '{{SHIPPING_INFO}}': business_data.get('shipping_info', 'Frete grátis acima de R$ 100'),
            '{{RETURN_POLICY}}': business_data.get('return_policy', '30 dias para troca ou devolução'),
            '{{PAYMENT_METHODS}}': business_data.get('payment_methods', 'Cartão, PIX, Boleto'),
            '{{FEATURED_PRODUCTS}}': business_data.get('featured_products', 'Produtos em destaque'),
            '{{PROMO_BANNER}}': business_data.get('promo_banner', 'Promoção especial!')
        }
    
    def apply_placeholders(
        self, 
        template: WordPressTemplate,
        placeholder_values: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Apply placeholder values to template content
        Returns processed template ready for WordPress generation
        """
        
        # Deep copy template data
        import copy
        processed_template = copy.deepcopy(template.dict())
        
        # Convert to JSON string for replacement
        template_json = json.dumps(processed_template)
        
        # Replace all placeholders
        for placeholder, value in placeholder_values.items():
            template_json = template_json.replace(placeholder, value)
        
        # Parse back to dict
        processed_template = json.loads(template_json)
        
        # Add generation metadata
        processed_template['generation_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'template_id': template.id,
            'placeholders_replaced': len(placeholder_values),
            'hash': hashlib.md5(template_json.encode()).hexdigest()
        }
        
        return processed_template
    
    def validate_template(self, template: WordPressTemplate) -> Dict[str, Any]:
        """
        Validate template structure and completeness
        Returns validation report
        """
        
        validation_report = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check required fields
        if not template.id:
            validation_report['errors'].append('Template ID is missing')
            validation_report['valid'] = False
        
        if not template.name:
            validation_report['errors'].append('Template name is missing')
            validation_report['valid'] = False
        
        if not template.pages or len(template.pages) == 0:
            validation_report['errors'].append('Template has no pages')
            validation_report['valid'] = False
        
        # Check pages
        required_pages = ['home', 'contato']
        existing_slugs = [page.slug for page in template.pages]
        
        for required_page in required_pages:
            if required_page not in existing_slugs:
                validation_report['warnings'].append(f'Missing recommended page: {required_page}')
        
        # Check placeholders
        if len(template.placeholders) == 0:
            validation_report['warnings'].append('Template has no placeholders defined')
        
        # Check Brazilian features
        if not template.brazilian_features.whatsapp_widget.get('enabled'):
            validation_report['info'].append('WhatsApp widget is disabled')
        
        # Check plugins
        essential_plugins = ['elementor', 'advanced-custom-fields']
        for plugin in essential_plugins:
            if plugin not in template.plugins_required:
                validation_report['warnings'].append(f'Missing essential plugin: {plugin}')
        
        # Calculate validation score
        score = 100
        score -= len(validation_report['errors']) * 20
        score -= len(validation_report['warnings']) * 5
        validation_report['score'] = max(0, score)
        
        return validation_report
    
    def export_template(self, template_id: str, output_path: str) -> bool:
        """Export template to JSON file"""
        template = self.get_template(template_id)
        
        if not template:
            logger.error(f"Template {template_id} not found")
            return False
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    template.dict(), 
                    f, 
                    indent=2, 
                    ensure_ascii=False,
                    default=str
                )
            
            logger.info(f"Template exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting template: {str(e)}")
            return False
    
    def import_template(self, json_path: str) -> Optional[WordPressTemplate]:
        """Import template from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template = self._parse_template(template_data)
            
            # Add to cache
            self.templates_cache[template.id] = template
            
            logger.info(f"Template {template.id} imported successfully")
            return template
            
        except Exception as e:
            logger.error(f"Error importing template: {str(e)}")
            return None
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about available templates"""
        
        templates = self.get_all_templates()
        
        stats = {
            'total_templates': len(templates),
            'by_industry': {},
            'by_complexity': {},
            'average_pages': 0,
            'total_placeholders': set(),
            'most_used_plugins': {}
        }
        
        total_pages = 0
        
        for template in templates:
            # Count by industry
            industry = template.industry.value
            stats['by_industry'][industry] = stats['by_industry'].get(industry, 0) + 1
            
            # Count by complexity
            complexity = template.complexity.value
            stats['by_complexity'][complexity] = stats['by_complexity'].get(complexity, 0) + 1
            
            # Count pages
            total_pages += len(template.pages)
            
            # Collect placeholders
            stats['total_placeholders'].update(template.placeholders)
            
            # Count plugins
            for plugin in template.plugins_required:
                stats['most_used_plugins'][plugin] = stats['most_used_plugins'].get(plugin, 0) + 1
        
        if templates:
            stats['average_pages'] = total_pages / len(templates)
        
        stats['total_placeholders'] = len(stats['total_placeholders'])
        
        # Sort plugins by usage
        stats['most_used_plugins'] = dict(
            sorted(stats['most_used_plugins'].items(), key=lambda x: x[1], reverse=True)
        )
        
        return stats


# Global instance
template_library = TemplateLibrary()

# Export for use in other modules
__all__ = [
    'TemplateLibrary',
    'template_library',
    'WordPressTemplate',
    'TemplateIndustry',
    'TemplateComplexity',
    'TemplatePage',
    'TemplateDesign',
    'TemplateSEO',
    'BrazilianFeatures'
]