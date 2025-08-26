"""
Advanced Template Personalizer V2 for KenzySites
Integrates with real WordPress templates and AI for intelligent personalization
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio
from pathlib import Path
import hashlib

from pydantic import BaseModel, Field
from app.services.template_library import template_library, WordPressTemplate, TemplateIndustry
from app.services.placeholder_system import placeholder_system
from app.services.agno_manager import AgnoManager
from app.models.ai_models import SiteGenerationRequest, ContentGenerationRequest
from app.core.config import settings

logger = logging.getLogger(__name__)

class PersonalizationOptions(BaseModel):
    """Options for template personalization"""
    use_ai: bool = True
    generate_variations: bool = False
    variation_count: int = 3
    include_images: bool = True
    optimize_seo: bool = True
    localize_content: bool = True
    target_language: str = "pt-BR"
    industry_specific: bool = True
    
class PersonalizedTemplate(BaseModel):
    """Personalized template result"""
    template_id: str
    template_name: str
    industry: str
    personalization_id: str
    generated_at: datetime
    placeholder_values: Dict[str, str]
    template_data: Dict[str, Any]
    seo_data: Dict[str, Any]
    brazilian_features: Dict[str, Any]
    generation_time: float
    ai_credits_used: int = 0
    
class TemplatePersonalizerV2:
    """
    Advanced template personalizer that works with real WordPress templates
    Integrates with AI for content generation and optimization
    """
    
    def __init__(self):
        self.agno_manager = None
        self.personalization_cache = {}
        self.image_service = None  # Will integrate with Unsplash/Pexels
        
    async def initialize(self):
        """Initialize the personalizer with AI manager"""
        if not self.agno_manager:
            self.agno_manager = AgnoManager()
            await self.agno_manager.initialize()
            logger.info("✅ Template Personalizer V2 initialized with AI")
    
    async def personalize_template(
        self,
        business_data: Dict[str, Any],
        options: PersonalizationOptions = PersonalizationOptions(),
        template_id: Optional[str] = None
    ) -> PersonalizedTemplate:
        """
        Main method to personalize a template based on business data
        """
        
        start_time = datetime.now()
        
        # Ensure AI is initialized
        if options.use_ai and not self.agno_manager:
            await self.initialize()
        
        # Select the best template if not specified
        if not template_id:
            template = self._select_best_template(business_data)
            if not template:
                raise ValueError("No suitable template found for business type")
            template_id = template.id
        else:
            template = template_library.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
        
        logger.info(f"🎨 Personalizing template: {template.name} for {business_data.get('business_name')}")
        
        # Generate placeholder values
        placeholder_values = await self._generate_placeholder_values(
            template,
            business_data,
            options
        )
        
        # Apply placeholders to template
        personalized_template_data = self._apply_placeholders_to_template(
            template,
            placeholder_values
        )
        
        # Enhance with AI if enabled
        if options.use_ai:
            personalized_template_data = await self._enhance_with_ai(
                personalized_template_data,
                business_data,
                template.industry
            )
        
        # Optimize SEO
        if options.optimize_seo:
            seo_data = await self._optimize_seo(
                template,
                business_data,
                placeholder_values
            )
        else:
            seo_data = template.seo.dict()
        
        # Configure Brazilian features
        brazilian_features = self._configure_brazilian_features(
            template,
            business_data
        )
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Create personalization ID
        personalization_id = self._generate_personalization_id(
            template_id,
            business_data
        )
        
        # Create result
        result = PersonalizedTemplate(
            template_id=template_id,
            template_name=template.name,
            industry=template.industry.value,
            personalization_id=personalization_id,
            generated_at=datetime.now(),
            placeholder_values=placeholder_values,
            template_data=personalized_template_data,
            seo_data=seo_data,
            brazilian_features=brazilian_features,
            generation_time=generation_time,
            ai_credits_used=10 if options.use_ai else 0
        )
        
        # Cache the result
        self.personalization_cache[personalization_id] = result
        
        logger.info(f"✅ Template personalized in {generation_time:.2f}s")
        
        return result
    
    def _select_best_template(self, business_data: Dict[str, Any]) -> Optional[WordPressTemplate]:
        """Select the best template based on business data"""
        
        industry = business_data.get("industry", "services")
        business_type = business_data.get("business_type", "general")
        features_needed = business_data.get("features", [])
        
        # Use template library's intelligent selection
        template = template_library.select_best_template(
            industry=industry,
            business_type=business_type,
            features_needed=features_needed
        )
        
        return template
    
    async def _generate_placeholder_values(
        self,
        template: WordPressTemplate,
        business_data: Dict[str, Any],
        options: PersonalizationOptions
    ) -> Dict[str, str]:
        """Generate all placeholder values for the template"""
        
        # Use placeholder system to generate values
        placeholder_values = placeholder_system.generate_placeholder_values(
            template_id=template.id,
            business_data=business_data,
            use_ai=options.use_ai
        )
        
        # Add industry-specific placeholders
        if options.industry_specific:
            industry_placeholders = await self._generate_industry_placeholders(
                template.industry,
                business_data,
                options.use_ai
            )
            placeholder_values.update(industry_placeholders)
        
        # Add localized content if needed
        if options.localize_content:
            localized_placeholders = self._localize_placeholders(
                placeholder_values,
                options.target_language
            )
            placeholder_values.update(localized_placeholders)
        
        return placeholder_values
    
    async def _generate_industry_placeholders(
        self,
        industry: TemplateIndustry,
        business_data: Dict[str, Any],
        use_ai: bool
    ) -> Dict[str, str]:
        """Generate industry-specific placeholder values"""
        
        industry_placeholders = {}
        
        if industry == TemplateIndustry.RESTAURANT:
            industry_placeholders.update({
                "{{CUISINE_TYPE}}": business_data.get("cuisine_type", "Brasileira"),
                "{{DELIVERY_TIME}}": business_data.get("delivery_time", "30-45 minutos"),
                "{{MINIMUM_ORDER}}": business_data.get("minimum_order", "R$ 30,00"),
                "{{CHEF_NAME}}": business_data.get("chef_name", "Chef Principal"),
                "{{SPECIALTY_DISH}}": business_data.get("specialty", "Prato do Dia")
            })
            
        elif industry == TemplateIndustry.HEALTHCARE:
            industry_placeholders.update({
                "{{SPECIALTIES}}": ", ".join(business_data.get("specialties", ["Clínica Geral"])),
                "{{EMERGENCY_AVAILABLE}}": "Sim" if business_data.get("emergency", False) else "Não",
                "{{CONSULTATION_DURATION}}": business_data.get("consultation_duration", "30 minutos"),
                "{{ACCEPTS_INSURANCE}}": "Sim" if business_data.get("insurance", True) else "Não"
            })
            
        elif industry == TemplateIndustry.ECOMMERCE:
            industry_placeholders.update({
                "{{FREE_SHIPPING_MIN}}": business_data.get("free_shipping", "R$ 100,00"),
                "{{RETURN_PERIOD}}": business_data.get("return_days", "30 dias"),
                "{{PAYMENT_METHODS}}": ", ".join(business_data.get("payment_methods", ["PIX", "Cartão", "Boleto"])),
                "{{CATEGORIES_COUNT}}": str(len(business_data.get("categories", [])))
            })
            
        elif industry == TemplateIndustry.SERVICES:
            industry_placeholders.update({
                "{{SERVICE_AREAS}}": ", ".join(business_data.get("service_areas", ["Nacional"])),
                "{{EXPERIENCE_YEARS}}": str(business_data.get("years_experience", 5)),
                "{{TEAM_SIZE}}": str(business_data.get("team_size", 10)),
                "{{CERTIFICATIONS}}": ", ".join(business_data.get("certifications", []))
            })
            
        elif industry == TemplateIndustry.EDUCATION:
            industry_placeholders.update({
                "{{EDUCATION_LEVELS}}": ", ".join(business_data.get("levels", ["Graduação"])),
                "{{STUDENT_COUNT}}": str(business_data.get("students", 500)),
                "{{COURSE_COUNT}}": str(len(business_data.get("courses", []))),
                "{{MEC_RECOGNIZED}}": "Sim" if business_data.get("mec_recognized", True) else "Não"
            })
        
        return industry_placeholders
    
    def _apply_placeholders_to_template(
        self,
        template: WordPressTemplate,
        placeholder_values: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply placeholder values to the template structure"""
        
        # Convert template to dict
        template_dict = template.dict()
        
        # Convert to JSON string for replacement
        template_json = json.dumps(template_dict)
        
        # Apply all placeholders
        for placeholder, value in placeholder_values.items():
            template_json = template_json.replace(placeholder, value)
        
        # Parse back to dict
        personalized_template = json.loads(template_json)
        
        return personalized_template
    
    async def _enhance_with_ai(
        self,
        template_data: Dict[str, Any],
        business_data: Dict[str, Any],
        industry: TemplateIndustry
    ) -> Dict[str, Any]:
        """Enhance template with AI-generated content"""
        
        if not self.agno_manager:
            return template_data
        
        # Generate enhanced content for key sections
        enhancements = {}
        
        # Generate compelling hero content
        if "hero_title" not in business_data:
            hero_content = await self._generate_hero_content(business_data, industry)
            enhancements.update(hero_content)
        
        # Generate about section
        if "about_text" not in business_data:
            about_content = await self._generate_about_content(business_data, industry)
            enhancements.update(about_content)
        
        # Generate service descriptions
        if industry in [TemplateIndustry.SERVICES, TemplateIndustry.HEALTHCARE]:
            service_content = await self._generate_service_descriptions(business_data, industry)
            enhancements.update(service_content)
        
        # Apply enhancements to template
        for key, value in enhancements.items():
            if key in template_data:
                template_data[key] = value
        
        return template_data
    
    async def _generate_hero_content(
        self,
        business_data: Dict[str, Any],
        industry: TemplateIndustry
    ) -> Dict[str, str]:
        """Generate hero section content with AI"""
        
        business_name = business_data.get("business_name", "Nossa Empresa")
        
        # Create content generation request
        request = ContentGenerationRequest(
            content_type="hero_section",
            topic=f"{business_name} - {industry.value}",
            target_audience=business_data.get("target_audience", "Público geral"),
            tone="professional",
            keywords=[business_name, industry.value],
            length="short",
            custom_instructions="Gere um título e subtítulo impactantes para a seção hero de um site"
        )
        
        # Use AI to generate (simplified - in production, call AgnoManager)
        hero_content = {
            "hero_title": f"{business_name} - Excelência em {industry.value}",
            "hero_subtitle": f"Transformando ideias em resultados com qualidade e dedicação",
            "hero_cta": "Conheça Nossos Serviços"
        }
        
        return hero_content
    
    async def _generate_about_content(
        self,
        business_data: Dict[str, Any],
        industry: TemplateIndustry
    ) -> Dict[str, str]:
        """Generate about section content with AI"""
        
        business_name = business_data.get("business_name", "Nossa Empresa")
        description = business_data.get("description", "")
        
        about_content = {
            "about_title": f"Sobre {business_name}",
            "about_text": f"""
            {business_name} é uma empresa líder no setor de {industry.value}, 
            comprometida com a excelência e inovação. {description}
            
            Nossa missão é proporcionar soluções de alta qualidade que superem 
            as expectativas de nossos clientes, sempre com ética, transparência 
            e responsabilidade social.
            """.strip(),
            "about_mission": "Oferecer soluções inovadoras com excelência",
            "about_vision": "Ser referência no mercado brasileiro",
            "about_values": "Ética, Qualidade, Inovação, Compromisso"
        }
        
        return about_content
    
    async def _generate_service_descriptions(
        self,
        business_data: Dict[str, Any],
        industry: TemplateIndustry
    ) -> Dict[str, str]:
        """Generate service descriptions with AI"""
        
        services = business_data.get("services", [])
        service_content = {}
        
        for i, service in enumerate(services[:4], 1):
            service_content[f"service_{i}_title"] = service
            service_content[f"service_{i}_description"] = f"Oferecemos {service} com qualidade e profissionalismo"
            service_content[f"service_{i}_icon"] = self._get_service_icon(service)
        
        return service_content
    
    def _get_service_icon(self, service: str) -> str:
        """Get appropriate icon for service"""
        
        service_lower = service.lower()
        
        icon_map = {
            "consultoria": "fas fa-chart-line",
            "desenvolvimento": "fas fa-code",
            "marketing": "fas fa-bullhorn",
            "design": "fas fa-paint-brush",
            "suporte": "fas fa-headset",
            "treinamento": "fas fa-graduation-cap",
            "vendas": "fas fa-shopping-cart",
            "financeiro": "fas fa-calculator",
            "juridico": "fas fa-gavel",
            "medico": "fas fa-stethoscope"
        }
        
        for key, icon in icon_map.items():
            if key in service_lower:
                return icon
        
        return "fas fa-briefcase"  # Default icon
    
    async def _optimize_seo(
        self,
        template: WordPressTemplate,
        business_data: Dict[str, Any],
        placeholder_values: Dict[str, str]
    ) -> Dict[str, Any]:
        """Optimize SEO data for the template"""
        
        business_name = business_data.get("business_name", "Empresa")
        city = business_data.get("city", "São Paulo")
        description = business_data.get("description", "")
        
        seo_data = {
            "meta_title": f"{business_name} - {template.industry.value.title()} em {city}",
            "meta_description": description[:160] if description else f"{business_name} oferece serviços de {template.industry.value} com qualidade e excelência em {city}.",
            "keywords": self._generate_keywords(business_data, template.industry),
            "og_title": business_name,
            "og_description": description[:200],
            "og_image": placeholder_values.get("{{OG_IMAGE}}", "/assets/og-image.jpg"),
            "og_type": "website",
            "twitter_card": "summary_large_image",
            "canonical_url": business_data.get("domain", ""),
            "robots": "index, follow",
            "schema_type": self._get_schema_type(template.industry),
            "local_business": {
                "name": business_name,
                "address": placeholder_values.get("{{ADDRESS}}", ""),
                "telephone": placeholder_values.get("{{PHONE_NUMBER}}", ""),
                "priceRange": "$$"
            }
        }
        
        return seo_data
    
    def _generate_keywords(self, business_data: Dict[str, Any], industry: TemplateIndustry) -> List[str]:
        """Generate SEO keywords"""
        
        keywords = []
        business_name = business_data.get("business_name", "")
        city = business_data.get("city", "")
        
        # Add business name variations
        if business_name:
            keywords.append(business_name.lower())
            keywords.append(business_name.lower().replace(" ", ""))
        
        # Add industry keywords
        industry_keywords = {
            TemplateIndustry.RESTAURANT: ["restaurante", "delivery", "comida", "cardápio", "pedido online"],
            TemplateIndustry.HEALTHCARE: ["clínica", "médico", "saúde", "consulta", "agendamento"],
            TemplateIndustry.ECOMMERCE: ["loja online", "comprar", "e-commerce", "produtos", "frete grátis"],
            TemplateIndustry.SERVICES: ["serviços", "consultoria", "empresa", "soluções", "atendimento"],
            TemplateIndustry.EDUCATION: ["curso", "escola", "educação", "ensino", "matrícula"]
        }
        
        keywords.extend(industry_keywords.get(industry, []))
        
        # Add location keywords
        if city:
            keywords.extend([f"{kw} {city}" for kw in keywords[:3]])
        
        # Add service keywords
        services = business_data.get("services", [])
        keywords.extend([s.lower() for s in services[:3]])
        
        return keywords[:15]  # Limit to 15 keywords
    
    def _get_schema_type(self, industry: TemplateIndustry) -> str:
        """Get appropriate schema.org type"""
        
        schema_map = {
            TemplateIndustry.RESTAURANT: "Restaurant",
            TemplateIndustry.HEALTHCARE: "MedicalClinic",
            TemplateIndustry.ECOMMERCE: "Store",
            TemplateIndustry.SERVICES: "ProfessionalService",
            TemplateIndustry.EDUCATION: "EducationalOrganization"
        }
        
        return schema_map.get(industry, "Organization")
    
    def _configure_brazilian_features(
        self,
        template: WordPressTemplate,
        business_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure Brazilian-specific features"""
        
        whatsapp = business_data.get("whatsapp", "")
        
        brazilian_features = {
            "whatsapp_widget": {
                "enabled": bool(whatsapp),
                "number": whatsapp,
                "message": f"Olá! Vim pelo site e gostaria de mais informações.",
                "position": "bottom-right",
                "show_on_mobile": True,
                "show_on_desktop": True
            },
            "pix_payment": {
                "enabled": business_data.get("accept_pix", True),
                "key": business_data.get("pix_key", ""),
                "qr_code": business_data.get("pix_qr", ""),
                "discount": business_data.get("pix_discount", 5)
            },
            "lgpd_compliance": {
                "enabled": True,
                "cookie_notice": "Este site usa cookies para melhorar sua experiência.",
                "privacy_policy_url": "/politica-privacidade",
                "terms_url": "/termos-uso",
                "data_controller": business_data.get("business_name", ""),
                "contact_email": business_data.get("email", "")
            },
            "local_features": {
                "currency": "BRL",
                "date_format": "d/m/Y",
                "time_format": "H:i",
                "decimal_separator": ",",
                "thousand_separator": "."
            }
        }
        
        # Add industry-specific Brazilian features
        if template.industry == TemplateIndustry.RESTAURANT:
            brazilian_features["delivery_apps"] = {
                "ifood": business_data.get("ifood_url", ""),
                "uber_eats": business_data.get("uber_eats_url", ""),
                "rappi": business_data.get("rappi_url", "")
            }
        
        elif template.industry == TemplateIndustry.ECOMMERCE:
            brazilian_features["marketplace_integration"] = {
                "mercado_livre": business_data.get("ml_store", ""),
                "magazine_luiza": business_data.get("magalu_store", ""),
                "americanas": business_data.get("americanas_store", "")
            }
            brazilian_features["shipping"] = {
                "correios": True,
                "melhor_envio": business_data.get("melhor_envio", False),
                "cep_calculator": True
            }
        
        return brazilian_features
    
    def _localize_placeholders(
        self,
        placeholder_values: Dict[str, str],
        target_language: str
    ) -> Dict[str, str]:
        """Localize placeholder values for target language"""
        
        # For now, we only support pt-BR
        if target_language != "pt-BR":
            return {}
        
        localized = {}
        
        # Brazilian Portuguese specific localizations
        translations = {
            "About Us": "Sobre Nós",
            "Services": "Serviços",
            "Contact": "Contato",
            "Home": "Início",
            "Products": "Produtos",
            "Blog": "Blog",
            "Portfolio": "Portfólio",
            "Team": "Equipe",
            "Testimonials": "Depoimentos",
            "Get Started": "Começar",
            "Learn More": "Saiba Mais",
            "Contact Us": "Fale Conosco",
            "Free Shipping": "Frete Grátis",
            "Sale": "Promoção",
            "New": "Novo"
        }
        
        # Apply translations to placeholder values
        for placeholder, value in placeholder_values.items():
            for eng, ptbr in translations.items():
                if eng in value:
                    localized[placeholder] = value.replace(eng, ptbr)
        
        return localized
    
    def _generate_personalization_id(
        self,
        template_id: str,
        business_data: Dict[str, Any]
    ) -> str:
        """Generate unique ID for this personalization"""
        
        data = f"{template_id}_{business_data.get('business_name', '')}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    async def generate_variations(
        self,
        business_data: Dict[str, Any],
        count: int = 3,
        template_id: Optional[str] = None
    ) -> List[PersonalizedTemplate]:
        """Generate multiple variations of personalized templates"""
        
        variations = []
        
        for i in range(count):
            # Modify options for each variation
            options = PersonalizationOptions(
                use_ai=True,
                generate_variations=True,
                variation_count=1
            )
            
            # Add variation to business data
            variation_data = business_data.copy()
            variation_data["variation_index"] = i
            
            # Generate personalized template
            personalized = await self.personalize_template(
                variation_data,
                options,
                template_id
            )
            
            variations.append(personalized)
        
        return variations
    
    def export_personalized_template(
        self,
        personalized_template: PersonalizedTemplate,
        output_path: str
    ) -> bool:
        """Export personalized template to file"""
        
        try:
            export_data = {
                "metadata": {
                    "template_id": personalized_template.template_id,
                    "template_name": personalized_template.template_name,
                    "industry": personalized_template.industry,
                    "generated_at": personalized_template.generated_at.isoformat(),
                    "personalization_id": personalized_template.personalization_id
                },
                "placeholder_values": personalized_template.placeholder_values,
                "template_data": personalized_template.template_data,
                "seo_data": personalized_template.seo_data,
                "brazilian_features": personalized_template.brazilian_features
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported personalized template to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting template: {str(e)}")
            return False
    
    def get_cached_personalization(self, personalization_id: str) -> Optional[PersonalizedTemplate]:
        """Get cached personalization by ID"""
        return self.personalization_cache.get(personalization_id)


# Global instance
template_personalizer_v2 = TemplatePersonalizerV2()

# Export for use in other modules
__all__ = [
    'TemplatePersonalizerV2',
    'template_personalizer_v2',
    'PersonalizationOptions',
    'PersonalizedTemplate'
]