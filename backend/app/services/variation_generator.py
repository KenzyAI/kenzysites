"""
Variation Generator for KenzySites
Creates multiple unique variations of websites from a single template
"""

import json
import logging
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import asyncio
import hashlib

from pydantic import BaseModel, Field
from app.services.template_personalizer_v2 import (
    template_personalizer_v2,
    PersonalizationOptions,
    PersonalizedTemplate
)
from app.services.template_library import template_library, TemplateIndustry

logger = logging.getLogger(__name__)

class VariationType(str, Enum):
    """Types of variations available"""
    COLOR_SCHEME = "color_scheme"
    LAYOUT = "layout"
    CONTENT_TONE = "content_tone"
    TYPOGRAPHY = "typography"
    FEATURES = "features"
    IMAGES = "images"
    COMPLETE = "complete"

class ColorScheme(BaseModel):
    """Color scheme for variations"""
    name: str
    primary: str
    secondary: str
    accent: str
    text: str
    background: str
    
class TypographySet(BaseModel):
    """Typography set for variations"""
    name: str
    heading_font: str
    body_font: str
    base_size: str
    
class ContentTone(BaseModel):
    """Content tone for variations"""
    name: str
    style: str  # formal, casual, friendly, professional
    language_level: str  # simple, moderate, sophisticated
    emoji_usage: bool
    
class SiteVariation(BaseModel):
    """Single site variation"""
    variation_id: str
    variation_index: int
    variation_name: str
    variation_type: VariationType
    personalized_template: PersonalizedTemplate
    color_scheme: ColorScheme
    typography: TypographySet
    content_tone: ContentTone
    layout_style: str
    features_enabled: List[str]
    score: float  # Quality/match score
    thumbnail_url: Optional[str] = None
    
class VariationSet(BaseModel):
    """Set of generated variations"""
    set_id: str
    business_name: str
    industry: str
    base_template_id: str
    variations: List[SiteVariation]
    generated_at: datetime
    generation_time: float
    selected_variation: Optional[int] = None

class VariationGenerator:
    """
    Generates multiple unique variations of websites
    Each variation has different colors, layouts, content tone, etc.
    """
    
    def __init__(self):
        self.color_schemes = self._load_color_schemes()
        self.typography_sets = self._load_typography_sets()
        self.content_tones = self._load_content_tones()
        self.layout_styles = self._load_layout_styles()
        self.variation_cache = {}
        
    def _load_color_schemes(self) -> Dict[str, List[ColorScheme]]:
        """Load predefined color schemes by industry"""
        
        schemes = {
            "restaurant": [
                ColorScheme(
                    name="Warm & Inviting",
                    primary="#D32F2F",
                    secondary="#FFC107",
                    accent="#4CAF50",
                    text="#333333",
                    background="#FFFFFF"
                ),
                ColorScheme(
                    name="Elegant Dark",
                    primary="#1A1A1A",
                    secondary="#D4AF37",
                    accent="#8B0000",
                    text="#FFFFFF",
                    background="#0A0A0A"
                ),
                ColorScheme(
                    name="Fresh & Natural",
                    primary="#4CAF50",
                    secondary="#8BC34A",
                    accent="#FF9800",
                    text="#2E7D32",
                    background="#F1F8E9"
                )
            ],
            "healthcare": [
                ColorScheme(
                    name="Trust Blue",
                    primary="#2196F3",
                    secondary="#03A9F4",
                    accent="#00BCD4",
                    text="#333333",
                    background="#FFFFFF"
                ),
                ColorScheme(
                    name="Calming Green",
                    primary="#4CAF50",
                    secondary="#81C784",
                    accent="#2196F3",
                    text="#1B5E20",
                    background="#F5F5F5"
                ),
                ColorScheme(
                    name="Professional Purple",
                    primary="#673AB7",
                    secondary="#9C27B0",
                    accent="#E91E63",
                    text="#311B92",
                    background="#FAFAFA"
                )
            ],
            "ecommerce": [
                ColorScheme(
                    name="Bold Orange",
                    primary="#FF6B35",
                    secondary="#F7931E",
                    accent="#27AE60",
                    text="#333333",
                    background="#FFFFFF"
                ),
                ColorScheme(
                    name="Modern Minimal",
                    primary="#000000",
                    secondary="#666666",
                    accent="#FF0000",
                    text="#333333",
                    background="#FFFFFF"
                ),
                ColorScheme(
                    name="Vibrant Purple",
                    primary="#8E24AA",
                    secondary="#AB47BC",
                    accent="#FFD600",
                    text="#4A148C",
                    background="#F3E5F5"
                )
            ],
            "services": [
                ColorScheme(
                    name="Corporate Blue",
                    primary="#0066FF",
                    secondary="#00D4FF",
                    accent="#FF6B35",
                    text="#333333",
                    background="#FFFFFF"
                ),
                ColorScheme(
                    name="Tech Dark",
                    primary="#0A0E27",
                    secondary="#1E3A8A",
                    accent="#00D4FF",
                    text="#FFFFFF",
                    background="#0A0E27"
                ),
                ColorScheme(
                    name="Creative Pink",
                    primary="#E91E63",
                    secondary="#F06292",
                    accent="#00BCD4",
                    text="#880E4F",
                    background="#FCE4EC"
                )
            ],
            "education": [
                ColorScheme(
                    name="Academic Green",
                    primary="#4CAF50",
                    secondary="#8BC34A",
                    accent="#FFC107",
                    text="#1B5E20",
                    background="#FFFFFF"
                ),
                ColorScheme(
                    name="Knowledge Blue",
                    primary="#1976D2",
                    secondary="#2196F3",
                    accent="#FF9800",
                    text="#0D47A1",
                    background="#E3F2FD"
                ),
                ColorScheme(
                    name="Youthful Orange",
                    primary="#FF9800",
                    secondary="#FFB74D",
                    accent="#4CAF50",
                    text="#E65100",
                    background="#FFF3E0"
                )
            ]
        }
        
        # Add a general set for any industry
        schemes["general"] = [
            ColorScheme(
                name="Classic Blue",
                primary="#2196F3",
                secondary="#64B5F6",
                accent="#FF5722",
                text="#333333",
                background="#FFFFFF"
            ),
            ColorScheme(
                name="Earth Tones",
                primary="#795548",
                secondary="#A1887F",
                accent="#FF9800",
                text="#3E2723",
                background="#EFEBE9"
            ),
            ColorScheme(
                name="Monochrome",
                primary="#424242",
                secondary="#757575",
                accent="#2196F3",
                text="#212121",
                background="#FAFAFA"
            )
        ]
        
        return schemes
    
    def _load_typography_sets(self) -> List[TypographySet]:
        """Load typography combinations"""
        
        return [
            TypographySet(
                name="Modern Sans",
                heading_font="Inter",
                body_font="Inter",
                base_size="16px"
            ),
            TypographySet(
                name="Classic Serif",
                heading_font="Playfair Display",
                body_font="Open Sans",
                base_size="16px"
            ),
            TypographySet(
                name="Tech Mono",
                heading_font="Roboto",
                body_font="Roboto",
                base_size="15px"
            ),
            TypographySet(
                name="Elegant Mix",
                heading_font="Montserrat",
                body_font="Lato",
                base_size="17px"
            ),
            TypographySet(
                name="Friendly Round",
                heading_font="Poppins",
                body_font="Nunito",
                base_size="16px"
            )
        ]
    
    def _load_content_tones(self) -> List[ContentTone]:
        """Load content tone variations"""
        
        return [
            ContentTone(
                name="Professional",
                style="formal",
                language_level="sophisticated",
                emoji_usage=False
            ),
            ContentTone(
                name="Friendly",
                style="casual",
                language_level="simple",
                emoji_usage=True
            ),
            ContentTone(
                name="Corporate",
                style="formal",
                language_level="moderate",
                emoji_usage=False
            ),
            ContentTone(
                name="Approachable",
                style="friendly",
                language_level="moderate",
                emoji_usage=False
            ),
            ContentTone(
                name="Enthusiastic",
                style="casual",
                language_level="simple",
                emoji_usage=True
            )
        ]
    
    def _load_layout_styles(self) -> List[str]:
        """Load layout style options"""
        
        return [
            "classic",
            "modern",
            "minimal",
            "bold",
            "elegant",
            "playful",
            "corporate",
            "creative"
        ]
    
    async def generate_variations(
        self,
        business_data: Dict[str, Any],
        count: int = 3,
        variation_types: List[VariationType] = None,
        template_id: Optional[str] = None
    ) -> VariationSet:
        """
        Generate multiple variations of a website
        """
        
        start_time = datetime.now()
        
        if variation_types is None:
            variation_types = [VariationType.COMPLETE]
        
        # Get base template
        if not template_id:
            template = template_library.select_best_template(
                industry=business_data.get("industry", "services"),
                business_type=business_data.get("business_type", "general")
            )
            if template:
                template_id = template.id
        
        industry = business_data.get("industry", "general")
        
        logger.info(f"🎨 Generating {count} variations for {business_data.get('business_name')}")
        
        variations = []
        
        # Generate each variation
        for i in range(count):
            variation = await self._generate_single_variation(
                business_data,
                template_id,
                industry,
                i,
                variation_types
            )
            variations.append(variation)
            logger.info(f"  ✅ Variation {i+1}/{count} generated: {variation.variation_name}")
        
        # Sort variations by score
        variations.sort(key=lambda x: x.score, reverse=True)
        
        # Create variation set
        generation_time = (datetime.now() - start_time).total_seconds()
        
        variation_set = VariationSet(
            set_id=self._generate_set_id(business_data),
            business_name=business_data.get("business_name", ""),
            industry=industry,
            base_template_id=template_id,
            variations=variations,
            generated_at=datetime.now(),
            generation_time=generation_time
        )
        
        # Cache the result
        self.variation_cache[variation_set.set_id] = variation_set
        
        logger.info(f"✅ Generated {count} variations in {generation_time:.2f}s")
        
        return variation_set
    
    async def _generate_single_variation(
        self,
        business_data: Dict[str, Any],
        template_id: str,
        industry: str,
        index: int,
        variation_types: List[VariationType]
    ) -> SiteVariation:
        """Generate a single variation"""
        
        # Select variation components
        color_scheme = self._select_color_scheme(industry, index)
        typography = self._select_typography(index)
        content_tone = self._select_content_tone(index)
        layout_style = self._select_layout_style(index)
        
        # Modify business data for this variation
        variation_data = business_data.copy()
        
        # Apply color scheme
        variation_data["primary_color"] = color_scheme.primary
        variation_data["secondary_color"] = color_scheme.secondary
        variation_data["accent_color"] = color_scheme.accent
        
        # Apply content tone modifications
        if content_tone.style == "casual":
            variation_data["hero_title"] = self._make_casual(
                variation_data.get("hero_title", f"Bem-vindo à {business_data.get('business_name', 'Nossa Empresa')}")
            )
        elif content_tone.style == "formal":
            variation_data["hero_title"] = self._make_formal(
                variation_data.get("hero_title", f"Bem-vindo à {business_data.get('business_name', 'Nossa Empresa')}")
            )
        
        # Generate personalized template
        options = PersonalizationOptions(
            use_ai=VariationType.COMPLETE in variation_types,
            generate_variations=False,
            optimize_seo=True,
            localize_content=True
        )
        
        personalized_template = await template_personalizer_v2.personalize_template(
            variation_data,
            options,
            template_id
        )
        
        # Apply typography to template
        if personalized_template.template_data.get("design"):
            personalized_template.template_data["design"]["typography"] = {
                "heading_font": typography.heading_font,
                "body_font": typography.body_font,
                "base_size": typography.base_size
            }
        
        # Calculate variation score
        score = self._calculate_variation_score(
            personalized_template,
            business_data,
            index
        )
        
        # Generate variation name
        variation_name = self._generate_variation_name(
            color_scheme,
            typography,
            content_tone,
            layout_style
        )
        
        # Determine enabled features
        features_enabled = self._select_features(industry, index)
        
        return SiteVariation(
            variation_id=self._generate_variation_id(business_data, index),
            variation_index=index,
            variation_name=variation_name,
            variation_type=VariationType.COMPLETE,
            personalized_template=personalized_template,
            color_scheme=color_scheme,
            typography=typography,
            content_tone=content_tone,
            layout_style=layout_style,
            features_enabled=features_enabled,
            score=score
        )
    
    def _select_color_scheme(self, industry: str, index: int) -> ColorScheme:
        """Select color scheme for variation"""
        
        schemes = self.color_schemes.get(industry, self.color_schemes["general"])
        return schemes[index % len(schemes)]
    
    def _select_typography(self, index: int) -> TypographySet:
        """Select typography for variation"""
        
        return self.typography_sets[index % len(self.typography_sets)]
    
    def _select_content_tone(self, index: int) -> ContentTone:
        """Select content tone for variation"""
        
        return self.content_tones[index % len(self.content_tones)]
    
    def _select_layout_style(self, index: int) -> str:
        """Select layout style for variation"""
        
        return self.layout_styles[index % len(self.layout_styles)]
    
    def _select_features(self, industry: str, index: int) -> List[str]:
        """Select features to enable for variation"""
        
        all_features = {
            "restaurant": [
                "online_menu", "delivery", "reservations", "whatsapp_order",
                "instagram_feed", "reviews", "loyalty_program"
            ],
            "healthcare": [
                "online_appointment", "telemedicine", "patient_portal",
                "emergency_contact", "insurance_info", "health_tips"
            ],
            "ecommerce": [
                "shopping_cart", "wishlist", "product_reviews", "live_chat",
                "size_guide", "related_products", "quick_view"
            ],
            "services": [
                "portfolio", "case_studies", "quote_calculator", "booking",
                "testimonials", "team_profiles", "blog"
            ],
            "education": [
                "course_catalog", "online_enrollment", "student_portal",
                "events_calendar", "library", "parent_portal", "certificates"
            ]
        }
        
        features = all_features.get(industry, [])
        
        # Vary the number of features enabled
        if index == 0:
            # First variation: all features
            return features
        elif index == 1:
            # Second variation: essential features only
            return features[:4]
        else:
            # Other variations: random selection
            num_features = random.randint(3, len(features))
            return random.sample(features, min(num_features, len(features)))
    
    def _make_casual(self, text: str) -> str:
        """Make text more casual"""
        
        replacements = {
            "Bem-vindo": "Olá! Seja bem-vindo",
            "Nossa Empresa": "a gente",
            "Oferecemos": "Temos",
            "Excelência": "Qualidade top",
            "Profissional": "Expert"
        }
        
        result = text
        for formal, casual in replacements.items():
            result = result.replace(formal, casual)
        
        return result
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal"""
        
        replacements = {
            "Olá": "Prezado cliente",
            "a gente": "nossa empresa",
            "Temos": "Oferecemos",
            "top": "superior",
            "Expert": "Especialista"
        }
        
        result = text
        for casual, formal in replacements.items():
            result = result.replace(casual, formal)
        
        return result
    
    def _calculate_variation_score(
        self,
        personalized_template: PersonalizedTemplate,
        business_data: Dict[str, Any],
        index: int
    ) -> float:
        """Calculate quality score for variation"""
        
        score = 80.0  # Base score
        
        # Add points for features
        if personalized_template.brazilian_features.get("whatsapp_widget", {}).get("enabled"):
            score += 5
        
        if personalized_template.seo_data.get("keywords"):
            score += 5
        
        # Vary score by index to create diversity
        score += (2 - index) * 3
        
        # Add randomness
        score += random.uniform(-5, 5)
        
        return min(100, max(0, score))
    
    def _generate_variation_name(
        self,
        color_scheme: ColorScheme,
        typography: TypographySet,
        content_tone: ContentTone,
        layout_style: str
    ) -> str:
        """Generate descriptive name for variation"""
        
        return f"{layout_style.title()} {color_scheme.name}"
    
    def _generate_variation_id(self, business_data: Dict[str, Any], index: int) -> str:
        """Generate unique ID for variation"""
        
        data = f"{business_data.get('business_name', '')}_{index}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _generate_set_id(self, business_data: Dict[str, Any]) -> str:
        """Generate unique ID for variation set"""
        
        data = f"{business_data.get('business_name', '')}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def get_variation_set(self, set_id: str) -> Optional[VariationSet]:
        """Get cached variation set"""
        
        return self.variation_cache.get(set_id)
    
    def select_variation(self, set_id: str, variation_index: int) -> Optional[SiteVariation]:
        """Select a specific variation from a set"""
        
        variation_set = self.get_variation_set(set_id)
        if variation_set and 0 <= variation_index < len(variation_set.variations):
            variation_set.selected_variation = variation_index
            return variation_set.variations[variation_index]
        
        return None
    
    async def regenerate_variation(
        self,
        set_id: str,
        variation_index: int,
        modifications: Dict[str, Any] = None
    ) -> Optional[SiteVariation]:
        """Regenerate a specific variation with modifications"""
        
        variation_set = self.get_variation_set(set_id)
        if not variation_set:
            return None
        
        if variation_index >= len(variation_set.variations):
            return None
        
        # Get original business data (would need to store this)
        # For now, we'll use a simplified approach
        business_data = {
            "business_name": variation_set.business_name,
            "industry": variation_set.industry
        }
        
        # Apply modifications
        if modifications:
            business_data.update(modifications)
        
        # Generate new variation
        new_variation = await self._generate_single_variation(
            business_data,
            variation_set.base_template_id,
            variation_set.industry,
            variation_index,
            [VariationType.COMPLETE]
        )
        
        # Replace in set
        variation_set.variations[variation_index] = new_variation
        
        return new_variation
    
    def export_variation(
        self,
        variation: SiteVariation,
        output_path: str
    ) -> bool:
        """Export a variation to file"""
        
        try:
            export_data = {
                "variation_id": variation.variation_id,
                "variation_name": variation.variation_name,
                "color_scheme": variation.color_scheme.dict(),
                "typography": variation.typography.dict(),
                "content_tone": variation.content_tone.dict(),
                "layout_style": variation.layout_style,
                "features_enabled": variation.features_enabled,
                "score": variation.score,
                "template_data": variation.personalized_template.template_data,
                "seo_data": variation.personalized_template.seo_data,
                "brazilian_features": variation.personalized_template.brazilian_features
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported variation to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting variation: {str(e)}")
            return False


# Global instance
variation_generator = VariationGenerator()

# Export for use in other modules
__all__ = [
    'VariationGenerator',
    'variation_generator',
    'VariationType',
    'ColorScheme',
    'TypographySet',
    'ContentTone',
    'SiteVariation',
    'VariationSet'
]