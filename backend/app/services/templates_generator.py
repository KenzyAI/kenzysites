"""
Templates Generator Service
Generates additional 500+ templates for Landing Page Builder
Phase 2: Beta Público - 10+ templates adicionais
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid
import random

logger = logging.getLogger(__name__)

class TemplatesGenerator:
    """Generate diverse landing page templates"""
    
    def __init__(self):
        self.industries = [
            "SaaS", "E-commerce", "Consultoria", "Educação", "Saúde",
            "Fitness", "Restaurante", "Imobiliária", "Advocacia", "Marketing",
            "Tecnologia", "Finanças", "Turismo", "Eventos", "Beleza",
            "Automotivo", "Construção", "Varejo", "B2B", "Startup"
        ]
        
        self.categories = [
            "hero", "product", "service", "lead-capture", "webinar",
            "sales", "coming-soon", "maintenance", "thank-you", "pricing",
            "about", "contact", "portfolio", "blog", "landing",
            "app", "ebook", "course", "event", "newsletter"
        ]
        
        self.styles = [
            "modern", "classic", "minimal", "bold", "elegant",
            "playful", "professional", "creative", "tech", "corporate"
        ]
        
        self.color_schemes = [
            {"primary": "#007BFF", "secondary": "#6C757D", "accent": "#28A745"},
            {"primary": "#DC3545", "secondary": "#FFC107", "accent": "#17A2B8"},
            {"primary": "#6F42C1", "secondary": "#E83E8C", "accent": "#20C997"},
            {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#45B7D1"},
            {"primary": "#2ECC71", "secondary": "#3498DB", "accent": "#9B59B6"},
            {"primary": "#1ABC9C", "secondary": "#34495E", "accent": "#E74C3C"},
            {"primary": "#F39C12", "secondary": "#D35400", "accent": "#C0392B"},
            {"primary": "#00D2FF", "secondary": "#3A7BD5", "accent": "#00D2FF"},
            {"primary": "#667EEA", "secondary": "#764BA2", "accent": "#F093FB"},
            {"primary": "#FA709A", "secondary": "#FEE140", "accent": "#FA709A"}
        ]
        
        self.components_sets = {
            "hero": ["hero_section", "navigation", "cta_button"],
            "features": ["features_grid", "features_list", "features_carousel"],
            "testimonials": ["testimonials_slider", "testimonials_grid", "testimonials_single"],
            "pricing": ["pricing_table", "pricing_cards", "pricing_comparison"],
            "cta": ["cta_section", "cta_banner", "cta_popup"],
            "footer": ["footer_simple", "footer_extended", "footer_minimal"]
        }
    
    def generate_template(
        self,
        template_id: str,
        name: str,
        category: str,
        industry: str,
        style: str,
        preview_index: int
    ) -> Dict[str, Any]:
        """Generate a single template"""
        
        # Select color scheme
        color_scheme = random.choice(self.color_schemes)
        
        # Generate component structure based on category
        components = self._generate_components(category, style)
        
        # Generate SEO metadata
        seo_data = self._generate_seo_data(name, category, industry)
        
        # Generate conversion elements
        conversion_elements = self._generate_conversion_elements(category)
        
        template = {
            "id": template_id,
            "name": name,
            "category": category,
            "industry": industry,
            "style": style,
            "preview_url": f"https://templates.kenzysites.com/preview/{template_id}",
            "thumbnail": f"https://cdn.kenzysites.com/templates/thumb_{preview_index}.jpg",
            "description": f"Template {style} para {industry} - {category}",
            "features": [
                "100% Responsivo",
                "SEO Otimizado",
                f"Estilo {style.title()}",
                "Carregamento Rápido",
                "Conversão Otimizada"
            ],
            "color_scheme": color_scheme,
            "components": components,
            "seo": seo_data,
            "conversion_elements": conversion_elements,
            "metrics": {
                "average_conversion": round(random.uniform(5, 25), 1),
                "page_speed_score": random.randint(85, 99),
                "mobile_score": random.randint(90, 100)
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "is_premium": random.choice([True, False, False]),  # 33% premium
            "tags": self._generate_tags(category, industry, style)
        }
        
        return template
    
    def _generate_components(self, category: str, style: str) -> List[Dict[str, Any]]:
        """Generate component structure for template"""
        components = []
        
        # Base structure based on category
        if category in ["hero", "landing", "product", "service"]:
            components.extend([
                {"type": "navigation", "variant": f"nav_{style}"},
                {"type": "hero", "variant": f"hero_{style}_1"},
                {"type": "features", "variant": "features_grid_3"},
                {"type": "testimonials", "variant": "testimonials_slider"},
                {"type": "cta", "variant": "cta_section_1"},
                {"type": "footer", "variant": f"footer_{style}"}
            ])
        elif category in ["lead-capture", "newsletter", "ebook"]:
            components.extend([
                {"type": "hero", "variant": f"hero_form_{style}"},
                {"type": "benefits", "variant": "benefits_list"},
                {"type": "social_proof", "variant": "logos_strip"},
                {"type": "form", "variant": "form_embedded"},
                {"type": "footer", "variant": "footer_minimal"}
            ])
        elif category == "pricing":
            components.extend([
                {"type": "navigation", "variant": "nav_centered"},
                {"type": "hero", "variant": "hero_pricing"},
                {"type": "pricing", "variant": "pricing_cards_3"},
                {"type": "faq", "variant": "faq_accordion"},
                {"type": "cta", "variant": "cta_banner"},
                {"type": "footer", "variant": "footer_extended"}
            ])
        elif category == "webinar":
            components.extend([
                {"type": "countdown", "variant": "countdown_hero"},
                {"type": "registration", "variant": "form_webinar"},
                {"type": "speakers", "variant": "speakers_grid"},
                {"type": "agenda", "variant": "agenda_timeline"},
                {"type": "footer", "variant": "footer_simple"}
            ])
        else:
            # Default structure
            components.extend([
                {"type": "navigation", "variant": "nav_default"},
                {"type": "hero", "variant": "hero_default"},
                {"type": "content", "variant": "content_blocks"},
                {"type": "cta", "variant": "cta_default"},
                {"type": "footer", "variant": "footer_default"}
            ])
        
        # Add style-specific enhancements
        for component in components:
            component["settings"] = {
                "animation": "fade-in" if style == "elegant" else "slide-up",
                "spacing": "large" if style == "minimal" else "medium",
                "corners": "rounded" if style in ["modern", "playful"] else "sharp"
            }
        
        return components
    
    def _generate_seo_data(self, name: str, category: str, industry: str) -> Dict[str, Any]:
        """Generate SEO metadata for template"""
        return {
            "title_template": f"{{business_name}} - {industry} {category.title()}",
            "description_template": f"{{business_description}} - Especialista em {industry}",
            "keywords": [
                industry.lower(),
                category.lower(),
                f"{industry.lower()} {category.lower()}",
                "serviços",
                "produtos",
                "soluções"
            ],
            "og_type": "website",
            "schema_type": "Organization" if category == "about" else "Product",
            "robots": "index, follow",
            "canonical": "auto"
        }
    
    def _generate_conversion_elements(self, category: str) -> List[Dict[str, Any]]:
        """Generate conversion optimization elements"""
        elements = []
        
        # Category-specific conversion elements
        if category in ["lead-capture", "newsletter", "ebook"]:
            elements.append({
                "type": "exit_intent_popup",
                "trigger": "exit",
                "delay": 0,
                "message": "Não perca esta oportunidade!"
            })
        
        if category in ["product", "service", "pricing"]:
            elements.append({
                "type": "sticky_cta",
                "position": "bottom",
                "show_after": 30,
                "text": "Comece Agora"
            })
        
        if category == "webinar":
            elements.append({
                "type": "countdown_timer",
                "urgency": "high",
                "format": "DD:HH:MM:SS"
            })
        
        # Common conversion elements
        elements.extend([
            {
                "type": "social_proof",
                "variant": "notification",
                "frequency": 45,
                "messages": [
                    "João de São Paulo acabou de se inscrever",
                    "Maria do Rio conseguiu 50% de desconto",
                    "15 pessoas estão vendo esta página agora"
                ]
            },
            {
                "type": "trust_badges",
                "position": "footer",
                "badges": ["ssl", "garantia", "suporte24h"]
            }
        ])
        
        return elements
    
    def _generate_tags(self, category: str, industry: str, style: str) -> List[str]:
        """Generate searchable tags for template"""
        tags = [
            category.lower(),
            industry.lower(),
            style.lower(),
            f"{industry.lower()}-{category.lower()}",
            "responsivo",
            "conversão"
        ]
        
        # Add specific tags based on attributes
        if style in ["modern", "minimal"]:
            tags.append("clean")
        if style in ["bold", "playful"]:
            tags.append("colorful")
        if category in ["lead-capture", "newsletter"]:
            tags.append("formulário")
        if category == "pricing":
            tags.append("planos")
        if industry in ["SaaS", "Tecnologia"]:
            tags.append("tech")
        
        return tags
    
    def generate_templates_batch(self, count: int = 500) -> List[Dict[str, Any]]:
        """Generate a batch of templates"""
        templates = []
        template_index = 0
        
        # Generate templates for each combination
        for industry in self.industries:
            for category in self.categories:
                for style in self.styles[:3]:  # Use top 3 styles for each combo
                    if template_index >= count:
                        break
                    
                    template_id = f"tpl_{uuid.uuid4().hex[:8]}"
                    name = f"{industry} {category.title()} {style.title()}"
                    
                    template = self.generate_template(
                        template_id=template_id,
                        name=name,
                        category=category,
                        industry=industry,
                        style=style,
                        preview_index=template_index % 50  # Cycle through 50 preview images
                    )
                    
                    templates.append(template)
                    template_index += 1
                
                if template_index >= count:
                    break
            
            if template_index >= count:
                break
        
        logger.info(f"Generated {len(templates)} templates")
        return templates
    
    def get_featured_templates(self, templates: List[Dict[str, Any]], count: int = 10) -> List[Dict[str, Any]]:
        """Get featured templates with high conversion rates"""
        # Sort by conversion rate and return top templates
        sorted_templates = sorted(
            templates,
            key=lambda x: x["metrics"]["average_conversion"],
            reverse=True
        )
        
        featured = sorted_templates[:count]
        
        # Mark as featured
        for template in featured:
            template["is_featured"] = True
            template["badge"] = "Popular"
        
        return featured
    
    def get_templates_by_industry(
        self,
        templates: List[Dict[str, Any]],
        industry: str
    ) -> List[Dict[str, Any]]:
        """Filter templates by industry"""
        return [t for t in templates if t["industry"] == industry]
    
    def get_templates_by_category(
        self,
        templates: List[Dict[str, Any]],
        category: str
    ) -> List[Dict[str, Any]]:
        """Filter templates by category"""
        return [t for t in templates if t["category"] == category]
    
    def search_templates(
        self,
        templates: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """Search templates by query"""
        query_lower = query.lower()
        results = []
        
        for template in templates:
            # Search in multiple fields
            searchable = [
                template["name"].lower(),
                template["description"].lower(),
                template["industry"].lower(),
                template["category"].lower(),
                template["style"].lower(),
                " ".join(template["tags"])
            ]
            
            if any(query_lower in field for field in searchable):
                results.append(template)
        
        return results

# Global instance
templates_generator = TemplatesGenerator()

# Generate initial batch of templates
all_templates = templates_generator.generate_templates_batch(500)
featured_templates = templates_generator.get_featured_templates(all_templates, 20)