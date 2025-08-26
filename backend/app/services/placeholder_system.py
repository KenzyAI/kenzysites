"""
Dynamic Placeholder System for KenzySites Templates
Handles intelligent placeholder replacement with AI-generated content
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib

from pydantic import BaseModel, Field
from app.core.config import settings
from app.services.template_library import template_library, TemplateIndustry

logger = logging.getLogger(__name__)

class PlaceholderCategory(BaseModel):
    """Categories for placeholder types"""
    BUSINESS = "business"
    CONTACT = "contact"
    CONTENT = "content"
    VISUAL = "visual"
    FEATURES = "features"
    PRICING = "pricing"
    TESTIMONIAL = "testimonial"
    TEAM = "team"
    PRODUCT = "product"
    META = "meta"

class PlaceholderRule(BaseModel):
    """Rules for placeholder generation"""
    placeholder: str
    category: str
    required: bool = True
    default_value: str = ""
    ai_generated: bool = False
    validation_regex: Optional[str] = None
    max_length: Optional[int] = None
    dependencies: List[str] = []
    industry_specific: Optional[List[str]] = None

class DynamicPlaceholderSystem:
    """
    Advanced placeholder system with AI content generation
    and intelligent value mapping
    """
    
    def __init__(self):
        self.placeholder_rules = self._initialize_rules()
        self.placeholder_cache = {}
        self.content_patterns = self._load_content_patterns()
        
    def _initialize_rules(self) -> Dict[str, PlaceholderRule]:
        """Initialize placeholder rules and categories"""
        
        rules = {
            # Business Information
            "{{BUSINESS_NAME}}": PlaceholderRule(
                placeholder="{{BUSINESS_NAME}}",
                category=PlaceholderCategory.BUSINESS,
                required=True,
                max_length=100
            ),
            "{{BUSINESS_DESCRIPTION}}": PlaceholderRule(
                placeholder="{{BUSINESS_DESCRIPTION}}",
                category=PlaceholderCategory.BUSINESS,
                required=True,
                ai_generated=True,
                max_length=500
            ),
            "{{BUSINESS_TAGLINE}}": PlaceholderRule(
                placeholder="{{BUSINESS_TAGLINE}}",
                category=PlaceholderCategory.BUSINESS,
                ai_generated=True,
                max_length=100
            ),
            
            # Contact Information
            "{{PHONE_NUMBER}}": PlaceholderRule(
                placeholder="{{PHONE_NUMBER}}",
                category=PlaceholderCategory.CONTACT,
                validation_regex=r"^\(\d{2}\)\s?\d{4,5}-?\d{4}$",
                default_value="(11) 9999-9999"
            ),
            "{{WHATSAPP_NUMBER}}": PlaceholderRule(
                placeholder="{{WHATSAPP_NUMBER}}",
                category=PlaceholderCategory.CONTACT,
                validation_regex=r"^\(\d{2}\)\s?\d{5}-?\d{4}$",
                dependencies=["{{PHONE_NUMBER}}"]
            ),
            "{{EMAIL}}": PlaceholderRule(
                placeholder="{{EMAIL}}",
                category=PlaceholderCategory.CONTACT,
                validation_regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                default_value="contato@exemplo.com.br"
            ),
            "{{ADDRESS}}": PlaceholderRule(
                placeholder="{{ADDRESS}}",
                category=PlaceholderCategory.CONTACT,
                max_length=200
            ),
            
            # Content Placeholders
            "{{HERO_TITLE}}": PlaceholderRule(
                placeholder="{{HERO_TITLE}}",
                category=PlaceholderCategory.CONTENT,
                ai_generated=True,
                max_length=100
            ),
            "{{HERO_SUBTITLE}}": PlaceholderRule(
                placeholder="{{HERO_SUBTITLE}}",
                category=PlaceholderCategory.CONTENT,
                ai_generated=True,
                max_length=200
            ),
            "{{ABOUT_TEXT}}": PlaceholderRule(
                placeholder="{{ABOUT_TEXT}}",
                category=PlaceholderCategory.CONTENT,
                ai_generated=True,
                max_length=1000
            ),
            
            # Visual Elements
            "{{HERO_IMAGE}}": PlaceholderRule(
                placeholder="{{HERO_IMAGE}}",
                category=PlaceholderCategory.VISUAL,
                default_value="/assets/images/hero-default.jpg"
            ),
            "{{LOGO}}": PlaceholderRule(
                placeholder="{{LOGO}}",
                category=PlaceholderCategory.VISUAL,
                default_value="/assets/images/logo-placeholder.png"
            ),
            
            # Brazilian Specific
            "{{PIX_KEY}}": PlaceholderRule(
                placeholder="{{PIX_KEY}}",
                category=PlaceholderCategory.FEATURES,
                required=False,
                industry_specific=["restaurant", "ecommerce", "services"]
            ),
            "{{CNPJ}}": PlaceholderRule(
                placeholder="{{CNPJ}}",
                category=PlaceholderCategory.BUSINESS,
                validation_regex=r"^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$",
                default_value="00.000.000/0001-00"
            ),
            "{{CPF}}": PlaceholderRule(
                placeholder="{{CPF}}",
                category=PlaceholderCategory.BUSINESS,
                validation_regex=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$",
                required=False
            )
        }
        
        return rules
    
    def _load_content_patterns(self) -> Dict[str, List[str]]:
        """Load content generation patterns for different industries"""
        
        patterns = {
            "restaurant": {
                "hero_titles": [
                    "Sabor que você vai amar",
                    "A melhor experiência gastronômica",
                    "Tradição e sabor em cada prato",
                    "Onde cada refeição é especial"
                ],
                "hero_subtitles": [
                    "Pratos preparados com ingredientes selecionados",
                    "Delivery rápido e comida quentinha",
                    "Venha conhecer nosso cardápio especial",
                    "Do tradicional ao contemporâneo"
                ],
                "cta_texts": [
                    "Peça Agora",
                    "Ver Cardápio",
                    "Fazer Reserva",
                    "Delivery Online"
                ]
            },
            "healthcare": {
                "hero_titles": [
                    "Cuidando da sua saúde",
                    "Excelência em atendimento médico",
                    "Sua saúde em primeiro lugar",
                    "Medicina humanizada e moderna"
                ],
                "hero_subtitles": [
                    "Equipe médica especializada e equipamentos modernos",
                    "Agende sua consulta online",
                    "Atendimento personalizado para toda família",
                    "Tecnologia e cuidado humanizado"
                ],
                "cta_texts": [
                    "Agendar Consulta",
                    "Falar com Especialista",
                    "Ver Especialidades",
                    "Marcar Exame"
                ]
            },
            "ecommerce": {
                "hero_titles": [
                    "As melhores ofertas estão aqui",
                    "Qualidade e preço justo",
                    "Sua loja online completa",
                    "Compre com segurança e comodidade"
                ],
                "hero_subtitles": [
                    "Frete grátis para todo Brasil",
                    "Parcelamento em até 12x sem juros",
                    "Entrega rápida e segura",
                    "Os melhores produtos com garantia"
                ],
                "cta_texts": [
                    "Ver Ofertas",
                    "Comprar Agora",
                    "Conferir Promoções",
                    "Explorar Categorias"
                ]
            },
            "services": {
                "hero_titles": [
                    "Soluções sob medida para seu negócio",
                    "Excelência em serviços profissionais",
                    "Transformando ideias em resultados",
                    "Seu parceiro de confiança"
                ],
                "hero_subtitles": [
                    "Consultoria especializada com resultados comprovados",
                    "Mais de 10 anos de experiência no mercado",
                    "Atendimento personalizado para sua empresa",
                    "Qualidade e compromisso em cada projeto"
                ],
                "cta_texts": [
                    "Solicitar Orçamento",
                    "Falar com Consultor",
                    "Conhecer Serviços",
                    "Agendar Reunião"
                ]
            },
            "education": {
                "hero_titles": [
                    "Educação que transforma vidas",
                    "Seu futuro começa aqui",
                    "Conhecimento e oportunidades",
                    "Formação de excelência"
                ],
                "hero_subtitles": [
                    "Cursos reconhecidos pelo MEC",
                    "Professores qualificados e infraestrutura moderna",
                    "Matrículas abertas com condições especiais",
                    "Do básico ao avançado, temos o curso ideal"
                ],
                "cta_texts": [
                    "Fazer Matrícula",
                    "Ver Cursos",
                    "Falar com Coordenação",
                    "Agendar Visita"
                ]
            }
        }
        
        return patterns
    
    def generate_placeholder_values(
        self,
        template_id: str,
        business_data: Dict[str, Any],
        use_ai: bool = True
    ) -> Dict[str, str]:
        """
        Generate all placeholder values for a template
        Combines user data with AI-generated content
        """
        
        template = template_library.get_template(template_id)
        if not template:
            logger.error(f"Template {template_id} not found")
            return {}
        
        placeholder_values = {}
        industry = template.industry.value
        
        # Process each placeholder in the template
        for placeholder in template.placeholders:
            value = self._generate_single_placeholder(
                placeholder,
                business_data,
                industry,
                use_ai
            )
            placeholder_values[placeholder] = value
        
        # Apply dependency resolution
        placeholder_values = self._resolve_dependencies(placeholder_values, business_data)
        
        # Validate all values
        self._validate_placeholders(placeholder_values)
        
        # Cache the results
        cache_key = self._generate_cache_key(template_id, business_data)
        self.placeholder_cache[cache_key] = placeholder_values
        
        return placeholder_values
    
    def _generate_single_placeholder(
        self,
        placeholder: str,
        business_data: Dict[str, Any],
        industry: str,
        use_ai: bool
    ) -> str:
        """Generate value for a single placeholder"""
        
        # Check if user provided the value
        clean_key = placeholder.replace("{{", "").replace("}}", "").lower()
        if clean_key in business_data:
            return str(business_data[clean_key])
        
        # Get rule for this placeholder
        rule = self.placeholder_rules.get(placeholder)
        if not rule:
            # Unknown placeholder, return as-is or empty
            return placeholder if not use_ai else ""
        
        # Check industry-specific rules
        if rule.industry_specific and industry not in rule.industry_specific:
            return ""
        
        # Generate based on category and AI flag
        if rule.ai_generated and use_ai:
            return self._generate_ai_content(placeholder, business_data, industry)
        
        # Use pattern-based generation
        if placeholder in ["{{HERO_TITLE}}", "{{HERO_SUBTITLE}}", "{{CTA_TEXT}}"]:
            return self._generate_from_pattern(placeholder, industry, business_data)
        
        # Return default value
        return rule.default_value
    
    def _generate_from_pattern(
        self,
        placeholder: str,
        industry: str,
        business_data: Dict[str, Any]
    ) -> str:
        """Generate content from predefined patterns"""
        
        patterns = self.content_patterns.get(industry, {})
        business_name = business_data.get("business_name", "Nossa Empresa")
        
        if placeholder == "{{HERO_TITLE}}":
            titles = patterns.get("hero_titles", ["Bem-vindo"])
            # Select based on business name hash for consistency
            index = hash(business_name) % len(titles)
            return titles[index]
        
        elif placeholder == "{{HERO_SUBTITLE}}":
            subtitles = patterns.get("hero_subtitles", ["Qualidade e excelência"])
            index = hash(business_name) % len(subtitles)
            return subtitles[index]
        
        elif placeholder == "{{CTA_TEXT}}":
            ctas = patterns.get("cta_texts", ["Saiba Mais"])
            index = hash(business_name) % len(ctas)
            return ctas[index]
        
        return ""
    
    def _generate_ai_content(
        self,
        placeholder: str,
        business_data: Dict[str, Any],
        industry: str
    ) -> str:
        """
        Generate content using AI (placeholder for actual AI integration)
        In production, this would call the AgnoManager
        """
        
        # This is a simplified version
        # In production, integrate with AgnoManager for real AI generation
        
        business_name = business_data.get("business_name", "Empresa")
        business_description = business_data.get("description", "")
        
        ai_prompts = {
            "{{BUSINESS_DESCRIPTION}}": f"Descrição profissional para {business_name} no ramo de {industry}",
            "{{BUSINESS_TAGLINE}}": f"Slogan criativo para {business_name}",
            "{{ABOUT_TEXT}}": f"Texto 'Sobre Nós' para {business_name}: {business_description}",
            "{{HERO_TITLE}}": f"Título principal impactante para {business_name}",
            "{{HERO_SUBTITLE}}": f"Subtítulo descritivo para {business_name}"
        }
        
        # For now, return contextual defaults
        defaults = {
            "{{BUSINESS_DESCRIPTION}}": f"{business_name} é uma empresa líder no setor de {industry}, oferecendo serviços de alta qualidade com foco na satisfação do cliente.",
            "{{BUSINESS_TAGLINE}}": f"Qualidade e confiança em {industry}",
            "{{ABOUT_TEXT}}": f"Com anos de experiência no mercado, {business_name} se destaca pela excelência em seus serviços e pelo compromisso com seus clientes.",
            "{{HERO_TITLE}}": f"Bem-vindo à {business_name}",
            "{{HERO_SUBTITLE}}": f"Sua melhor escolha em {industry}"
        }
        
        return defaults.get(placeholder, "")
    
    def _resolve_dependencies(
        self,
        placeholder_values: Dict[str, str],
        business_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Resolve placeholder dependencies"""
        
        # Example: If no WhatsApp provided, use phone number
        if not placeholder_values.get("{{WHATSAPP_NUMBER}}") and placeholder_values.get("{{PHONE_NUMBER}}"):
            placeholder_values["{{WHATSAPP_NUMBER}}"] = placeholder_values["{{PHONE_NUMBER}}"]
        
        # If no email domain matches business name
        if "{{EMAIL}}" in placeholder_values and placeholder_values["{{EMAIL}}"] == "contato@exemplo.com.br":
            business_name = business_data.get("business_name", "empresa")
            domain = business_name.lower().replace(" ", "").replace(".", "")
            placeholder_values["{{EMAIL}}"] = f"contato@{domain}.com.br"
        
        # Generate related placeholders
        if "{{PRIMARY_COLOR}}" not in placeholder_values:
            # Industry-based color schemes
            color_schemes = {
                "restaurant": {"primary": "#D32F2F", "secondary": "#FFC107", "accent": "#4CAF50"},
                "healthcare": {"primary": "#2196F3", "secondary": "#03A9F4", "accent": "#00BCD4"},
                "ecommerce": {"primary": "#FF6B35", "secondary": "#F7931E", "accent": "#27AE60"},
                "services": {"primary": "#0066FF", "secondary": "#00D4FF", "accent": "#FF6B35"},
                "education": {"primary": "#4CAF50", "secondary": "#8BC34A", "accent": "#FFC107"}
            }
            
            industry = business_data.get("industry", "services")
            colors = color_schemes.get(industry, color_schemes["services"])
            
            placeholder_values["{{PRIMARY_COLOR}}"] = colors["primary"]
            placeholder_values["{{SECONDARY_COLOR}}"] = colors["secondary"]
            placeholder_values["{{ACCENT_COLOR}}"] = colors["accent"]
        
        return placeholder_values
    
    def _validate_placeholders(self, placeholder_values: Dict[str, str]) -> bool:
        """Validate all placeholder values against rules"""
        
        for placeholder, value in placeholder_values.items():
            rule = self.placeholder_rules.get(placeholder)
            if not rule:
                continue
            
            # Check required fields
            if rule.required and not value:
                logger.warning(f"Required placeholder {placeholder} is empty")
            
            # Validate regex
            if rule.validation_regex and value:
                if not re.match(rule.validation_regex, value):
                    logger.warning(f"Placeholder {placeholder} value '{value}' doesn't match pattern")
            
            # Check max length
            if rule.max_length and len(value) > rule.max_length:
                logger.warning(f"Placeholder {placeholder} exceeds max length of {rule.max_length}")
                placeholder_values[placeholder] = value[:rule.max_length]
        
        return True
    
    def apply_placeholders_to_content(
        self,
        content: str,
        placeholder_values: Dict[str, str]
    ) -> str:
        """Apply placeholder values to content string"""
        
        processed_content = content
        
        # Sort placeholders by length (longest first) to avoid partial replacements
        sorted_placeholders = sorted(
            placeholder_values.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for placeholder, value in sorted_placeholders:
            if placeholder in processed_content:
                processed_content = processed_content.replace(placeholder, value)
                logger.debug(f"Replaced {placeholder} with {value[:50]}...")
        
        return processed_content
    
    def extract_placeholders_from_content(self, content: str) -> List[str]:
        """Extract all placeholders from content"""
        
        # Pattern to match {{PLACEHOLDER_NAME}}
        pattern = r'\{\{[A-Z_0-9]+\}\}'
        placeholders = re.findall(pattern, content)
        
        return list(set(placeholders))  # Remove duplicates
    
    def generate_placeholder_documentation(self) -> Dict[str, Any]:
        """Generate documentation for all placeholders"""
        
        docs = {
            "total_placeholders": len(self.placeholder_rules),
            "categories": {},
            "placeholders": []
        }
        
        # Group by category
        for placeholder, rule in self.placeholder_rules.items():
            category = rule.category
            if category not in docs["categories"]:
                docs["categories"][category] = []
            
            placeholder_doc = {
                "placeholder": placeholder,
                "category": category,
                "required": rule.required,
                "ai_generated": rule.ai_generated,
                "default": rule.default_value,
                "max_length": rule.max_length,
                "validation": rule.validation_regex,
                "industries": rule.industry_specific
            }
            
            docs["categories"][category].append(placeholder)
            docs["placeholders"].append(placeholder_doc)
        
        return docs
    
    def _generate_cache_key(self, template_id: str, business_data: Dict[str, Any]) -> str:
        """Generate cache key for placeholder values"""
        
        # Create a stable hash from template and business data
        data_str = f"{template_id}_{json.dumps(business_data, sort_keys=True)}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_industry_specific_placeholders(self, industry: str) -> List[str]:
        """Get placeholders specific to an industry"""
        
        industry_placeholders = []
        
        for placeholder, rule in self.placeholder_rules.items():
            if rule.industry_specific and industry in rule.industry_specific:
                industry_placeholders.append(placeholder)
        
        return industry_placeholders
    
    def validate_business_data(
        self,
        business_data: Dict[str, Any],
        industry: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate if business data has required fields
        Returns (is_valid, missing_fields)
        """
        
        required_fields = ["business_name"]
        missing_fields = []
        
        # Add industry-specific required fields
        industry_requirements = {
            "restaurant": ["cuisine_type", "delivery_areas"],
            "healthcare": ["specialties", "doctor_names"],
            "ecommerce": ["product_categories", "shipping_info"],
            "services": ["service_types", "target_market"],
            "education": ["courses", "education_level"]
        }
        
        if industry in industry_requirements:
            required_fields.extend(industry_requirements[industry])
        
        for field in required_fields:
            if field not in business_data or not business_data[field]:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields


# Global instance
placeholder_system = DynamicPlaceholderSystem()

# Export for use in other modules
__all__ = [
    'DynamicPlaceholderSystem',
    'placeholder_system',
    'PlaceholderCategory',
    'PlaceholderRule'
]