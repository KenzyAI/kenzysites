"""
Agno Framework Tools
Specialized tools and functions that agents can use
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import json
import re
from datetime import datetime
import hashlib
import requests
from bs4 import BeautifulSoup

@dataclass
class Tool:
    """Base tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: str
    requires_api_key: bool = False
    rate_limited: bool = False

# Content Generation Tools
class ContentTools:
    """Tools for content generation and manipulation"""
    
    @staticmethod
    def generate_headline(
        topic: str,
        style: str = "engaging",
        max_length: int = 60
    ) -> str:
        """Generate compelling headlines"""
        styles = {
            "engaging": ["Discover", "Unlock", "Master", "Transform"],
            "urgent": ["Now", "Today", "Don't Miss", "Limited Time"],
            "question": ["How to", "Why", "What", "When"],
            "number": ["5 Ways", "10 Tips", "7 Secrets", "3 Steps"]
        }
        
        # Simulate headline generation
        prefix = styles.get(style, styles["engaging"])[0]
        headline = f"{prefix} {topic.title()}"
        
        if len(headline) > max_length:
            headline = headline[:max_length-3] + "..."
        
        return headline
    
    @staticmethod
    def optimize_readability(
        text: str,
        target_grade_level: int = 8
    ) -> Dict[str, Any]:
        """Optimize text readability"""
        sentences = text.split('. ')
        words = text.split()
        
        # Simple readability metrics
        avg_sentence_length = len(words) / max(len(sentences), 1)
        complex_words = sum(1 for w in words if len(w) > 6)
        
        readability_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * (complex_words / len(words))
        
        suggestions = []
        if avg_sentence_length > 20:
            suggestions.append("Break long sentences into shorter ones")
        if complex_words / len(words) > 0.3:
            suggestions.append("Use simpler words where possible")
        
        return {
            "original_text": text,
            "readability_score": round(readability_score, 2),
            "suggestions": suggestions,
            "metrics": {
                "sentence_count": len(sentences),
                "word_count": len(words),
                "avg_sentence_length": round(avg_sentence_length, 1),
                "complex_word_ratio": round(complex_words / len(words), 2)
            }
        }
    
    @staticmethod
    def extract_keywords(
        text: str,
        max_keywords: int = 10
    ) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
                     'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
                     'does', 'did', 'will', 'would', 'could', 'should', 'may',
                     'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        keyword_freq = {}
        for keyword in keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, _ in sorted_keywords[:max_keywords]]

# SEO Tools
class SEOTools:
    """Tools for SEO optimization"""
    
    @staticmethod
    def generate_meta_tags(
        title: str,
        content: str,
        keywords: List[str]
    ) -> Dict[str, str]:
        """Generate SEO meta tags"""
        description = content[:160] if len(content) > 160 else content
        
        return {
            "title": title[:60],
            "description": description,
            "keywords": ", ".join(keywords[:10]),
            "og:title": title,
            "og:description": description,
            "twitter:title": title[:70],
            "twitter:description": description[:200],
            "robots": "index, follow",
            "canonical": "",
            "author": ""
        }
    
    @staticmethod
    def generate_schema_markup(
        page_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured data schema markup"""
        schemas = {
            "article": {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": data.get("title", ""),
                "description": data.get("description", ""),
                "author": {
                    "@type": "Person",
                    "name": data.get("author", "")
                },
                "datePublished": data.get("date", datetime.now().isoformat()),
                "image": data.get("image", "")
            },
            "product": {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "image": data.get("image", ""),
                "brand": {
                    "@type": "Brand",
                    "name": data.get("brand", "")
                },
                "offers": {
                    "@type": "Offer",
                    "price": data.get("price", ""),
                    "priceCurrency": data.get("currency", "USD")
                }
            },
            "local_business": {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": data.get("street", ""),
                    "addressLocality": data.get("city", ""),
                    "addressRegion": data.get("state", ""),
                    "postalCode": data.get("zip", "")
                },
                "telephone": data.get("phone", "")
            }
        }
        
        return schemas.get(page_type, schemas["article"])
    
    @staticmethod
    def analyze_keyword_density(
        text: str,
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Analyze keyword density in text"""
        text_lower = text.lower()
        word_count = len(text.split())
        
        keyword_analysis = {}
        for keyword in target_keywords:
            count = text_lower.count(keyword.lower())
            density = (count / word_count) * 100 if word_count > 0 else 0
            
            keyword_analysis[keyword] = {
                "count": count,
                "density": round(density, 2),
                "recommendation": "optimal" if 1 <= density <= 3 else "adjust"
            }
        
        return {
            "total_words": word_count,
            "keywords": keyword_analysis,
            "recommendations": [
                f"Adjust '{k}' density" 
                for k, v in keyword_analysis.items() 
                if v["recommendation"] == "adjust"
            ]
        }

# Design Tools
class DesignTools:
    """Tools for design and UI generation"""
    
    @staticmethod
    def generate_color_palette(
        base_color: str,
        scheme: str = "complementary"
    ) -> Dict[str, str]:
        """Generate color palette from base color"""
        # Convert hex to RGB
        base_rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
        
        palettes = {
            "complementary": {
                "primary": base_color,
                "secondary": DesignTools._adjust_color(base_rgb, 180),
                "accent": DesignTools._adjust_color(base_rgb, 60),
                "neutral": "#F5F5F5",
                "dark": "#333333"
            },
            "monochromatic": {
                "primary": base_color,
                "light": DesignTools._lighten_color(base_rgb, 0.3),
                "lighter": DesignTools._lighten_color(base_rgb, 0.6),
                "dark": DesignTools._darken_color(base_rgb, 0.3),
                "darker": DesignTools._darken_color(base_rgb, 0.6)
            },
            "triadic": {
                "primary": base_color,
                "secondary": DesignTools._adjust_color(base_rgb, 120),
                "tertiary": DesignTools._adjust_color(base_rgb, 240),
                "neutral": "#FFFFFF",
                "dark": "#000000"
            }
        }
        
        return palettes.get(scheme, palettes["complementary"])
    
    @staticmethod
    def _adjust_color(rgb: tuple, degrees: int) -> str:
        """Adjust color hue"""
        # Simplified color adjustment
        r, g, b = rgb
        adjusted = (
            min(255, r + degrees // 3),
            min(255, g + degrees // 2),
            min(255, b + degrees)
        )
        return f"#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}"
    
    @staticmethod
    def _lighten_color(rgb: tuple, factor: float) -> str:
        """Lighten color"""
        r, g, b = rgb
        lightened = (
            int(r + (255 - r) * factor),
            int(g + (255 - g) * factor),
            int(b + (255 - b) * factor)
        )
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
    
    @staticmethod
    def _darken_color(rgb: tuple, factor: float) -> str:
        """Darken color"""
        r, g, b = rgb
        darkened = (
            int(r * (1 - factor)),
            int(g * (1 - factor)),
            int(b * (1 - factor))
        )
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    @staticmethod
    def generate_typography_scale(
        base_size: int = 16,
        scale: str = "major_third"
    ) -> Dict[str, str]:
        """Generate typography scale"""
        scales = {
            "minor_second": 1.067,
            "major_second": 1.125,
            "minor_third": 1.2,
            "major_third": 1.25,
            "perfect_fourth": 1.333,
            "golden_ratio": 1.618
        }
        
        ratio = scales.get(scale, scales["major_third"])
        
        return {
            "xs": f"{int(base_size / (ratio * ratio))}px",
            "sm": f"{int(base_size / ratio)}px",
            "base": f"{base_size}px",
            "lg": f"{int(base_size * ratio)}px",
            "xl": f"{int(base_size * ratio * ratio)}px",
            "2xl": f"{int(base_size * ratio * ratio * ratio)}px",
            "3xl": f"{int(base_size * ratio * ratio * ratio * ratio)}px"
        }

# WordPress Tools
class WordPressTools:
    """Tools for WordPress development"""
    
    @staticmethod
    def generate_custom_post_type(
        name: str,
        singular: str,
        plural: str,
        options: Dict[str, Any] = None
    ) -> str:
        """Generate WordPress custom post type code"""
        code = f'''
function create_{name}_post_type() {{
    $labels = array(
        'name' => __('{plural}'),
        'singular_name' => __('{singular}'),
        'add_new' => __('Add New'),
        'add_new_item' => __('Add New {singular}'),
        'edit_item' => __('Edit {singular}'),
        'new_item' => __('New {singular}'),
        'view_item' => __('View {singular}'),
        'search_items' => __('Search {plural}'),
        'not_found' => __('No {plural.lower()} found'),
        'not_found_in_trash' => __('No {plural.lower()} found in Trash'),
    );
    
    $args = array(
        'labels' => $labels,
        'public' => true,
        'has_archive' => true,
        'rewrite' => array('slug' => '{name}'),
        'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
        'show_in_rest' => true,
    );
    
    register_post_type('{name}', $args);
}}
add_action('init', 'create_{name}_post_type');
'''
        return code
    
    @staticmethod
    def generate_shortcode(
        name: str,
        attributes: List[str],
        content: str
    ) -> str:
        """Generate WordPress shortcode"""
        attrs_code = "\n".join([
            f"    '{attr}' => ''," for attr in attributes
        ])
        
        code = f'''
function {name}_shortcode($atts, $content = null) {{
    $atts = shortcode_atts(array(
{attrs_code}
    ), $atts, '{name}');
    
    ob_start();
    ?>
    {content}
    <?php
    return ob_get_clean();
}}
add_shortcode('{name}', '{name}_shortcode');
'''
        return code
    
    @staticmethod
    def generate_widget(
        name: str,
        title: str,
        description: str
    ) -> str:
        """Generate WordPress widget class"""
        class_name = f"{name.title().replace('_', '')}Widget"
        
        code = f'''
class {class_name} extends WP_Widget {{
    
    public function __construct() {{
        parent::__construct(
            '{name}_widget',
            __('{title}'),
            array('description' => __('{description}'))
        );
    }}
    
    public function widget($args, $instance) {{
        echo $args['before_widget'];
        if (!empty($instance['title'])) {{
            echo $args['before_title'] . apply_filters('widget_title', $instance['title']) . $args['after_title'];
        }}
        // Widget content here
        echo $args['after_widget'];
    }}
    
    public function form($instance) {{
        $title = !empty($instance['title']) ? $instance['title'] : '';
        ?>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('title')); ?>">Title:</label>
            <input class="widefat" id="<?php echo esc_attr($this->get_field_id('title')); ?>" 
                   name="<?php echo esc_attr($this->get_field_name('title')); ?>" 
                   type="text" value="<?php echo esc_attr($title); ?>">
        </p>
        <?php
    }}
    
    public function update($new_instance, $old_instance) {{
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? sanitize_text_field($new_instance['title']) : '';
        return $instance;
    }}
}}

function register_{name}_widget() {{
    register_widget('{class_name}');
}}
add_action('widgets_init', 'register_{name}_widget');
'''
        return code

# Validation Tools
class ValidationTools:
    """Tools for content and code validation"""
    
    @staticmethod
    def validate_html(html: str) -> Dict[str, Any]:
        """Validate HTML structure"""
        issues = []
        
        # Check for basic HTML structure
        if not re.search(r'<!DOCTYPE', html, re.IGNORECASE):
            issues.append("Missing DOCTYPE declaration")
        
        # Check for unclosed tags
        open_tags = re.findall(r'<([a-z]+)(?:\s|>)', html, re.IGNORECASE)
        close_tags = re.findall(r'</([a-z]+)>', html, re.IGNORECASE)
        
        unclosed = []
        for tag in open_tags:
            if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
                if open_tags.count(tag) != close_tags.count(tag):
                    unclosed.append(tag)
        
        if unclosed:
            issues.append(f"Unclosed tags: {', '.join(set(unclosed))}")
        
        # Check for alt attributes on images
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        for img in images:
            if 'alt=' not in img:
                issues.append("Image missing alt attribute")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": [
                "Add DOCTYPE declaration" if "DOCTYPE" in str(issues) else None,
                "Close all HTML tags properly" if unclosed else None,
                "Add alt attributes to all images" if "alt attribute" in str(issues) else None
            ]
        }
    
    @staticmethod
    def check_accessibility(html: str) -> Dict[str, Any]:
        """Check accessibility compliance"""
        issues = []
        warnings = []
        
        # Check for heading hierarchy
        headings = re.findall(r'<h([1-6])', html, re.IGNORECASE)
        if headings:
            headings = [int(h) for h in headings]
            for i in range(1, len(headings)):
                if headings[i] - headings[i-1] > 1:
                    warnings.append(f"Heading hierarchy skip: H{headings[i-1]} to H{headings[i]}")
        
        # Check for form labels
        inputs = re.findall(r'<input[^>]*>', html, re.IGNORECASE)
        for input_tag in inputs:
            if 'type="hidden"' not in input_tag:
                input_id = re.search(r'id="([^"]*)"', input_tag)
                if input_id:
                    if f'for="{input_id.group(1)}"' not in html:
                        issues.append(f"Input missing associated label")
        
        # Check for language attribute
        if not re.search(r'<html[^>]*lang=', html, re.IGNORECASE):
            issues.append("Missing language attribute on html element")
        
        return {
            "accessible": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "wcag_level": "AA" if len(issues) == 0 else "Needs improvement"
        }

# Tool Registry
AVAILABLE_TOOLS = {
    "content": {
        "generate_headline": Tool(
            name="generate_headline",
            description="Generate compelling headlines",
            parameters={"topic": "string", "style": "string", "max_length": "int"},
            returns="string"
        ),
        "optimize_readability": Tool(
            name="optimize_readability",
            description="Optimize text for readability",
            parameters={"text": "string", "target_grade_level": "int"},
            returns="dict"
        ),
        "extract_keywords": Tool(
            name="extract_keywords",
            description="Extract keywords from text",
            parameters={"text": "string", "max_keywords": "int"},
            returns="list"
        )
    },
    "seo": {
        "generate_meta_tags": Tool(
            name="generate_meta_tags",
            description="Generate SEO meta tags",
            parameters={"title": "string", "content": "string", "keywords": "list"},
            returns="dict"
        ),
        "generate_schema_markup": Tool(
            name="generate_schema_markup",
            description="Generate structured data schema",
            parameters={"page_type": "string", "data": "dict"},
            returns="dict"
        ),
        "analyze_keyword_density": Tool(
            name="analyze_keyword_density",
            description="Analyze keyword density",
            parameters={"text": "string", "target_keywords": "list"},
            returns="dict"
        )
    },
    "design": {
        "generate_color_palette": Tool(
            name="generate_color_palette",
            description="Generate color palette",
            parameters={"base_color": "string", "scheme": "string"},
            returns="dict"
        ),
        "generate_typography_scale": Tool(
            name="generate_typography_scale",
            description="Generate typography scale",
            parameters={"base_size": "int", "scale": "string"},
            returns="dict"
        )
    },
    "wordpress": {
        "generate_custom_post_type": Tool(
            name="generate_custom_post_type",
            description="Generate custom post type code",
            parameters={"name": "string", "singular": "string", "plural": "string"},
            returns="string"
        ),
        "generate_shortcode": Tool(
            name="generate_shortcode",
            description="Generate WordPress shortcode",
            parameters={"name": "string", "attributes": "list", "content": "string"},
            returns="string"
        ),
        "generate_widget": Tool(
            name="generate_widget",
            description="Generate WordPress widget",
            parameters={"name": "string", "title": "string", "description": "string"},
            returns="string"
        )
    },
    "validation": {
        "validate_html": Tool(
            name="validate_html",
            description="Validate HTML structure",
            parameters={"html": "string"},
            returns="dict"
        ),
        "check_accessibility": Tool(
            name="check_accessibility",
            description="Check accessibility compliance",
            parameters={"html": "string"},
            returns="dict"
        )
    }
}

class ToolExecutor:
    """Execute tools based on agent requests"""
    
    def __init__(self):
        self.tools = {
            "content": ContentTools(),
            "seo": SEOTools(),
            "design": DesignTools(),
            "wordpress": WordPressTools(),
            "validation": ValidationTools()
        }
    
    def execute(
        self,
        category: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute a specific tool"""
        if category not in self.tools:
            raise ValueError(f"Unknown tool category: {category}")
        
        tool_class = self.tools[category]
        if not hasattr(tool_class, tool_name):
            raise ValueError(f"Unknown tool: {tool_name} in category {category}")
        
        tool_method = getattr(tool_class, tool_name)
        return tool_method(**parameters)
    
    def get_available_tools(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get list of available tools"""
        if category:
            return AVAILABLE_TOOLS.get(category, {})
        return AVAILABLE_TOOLS

# Export tool executor instance
tool_executor = ToolExecutor()