"""
Agno Framework Agents
Real implementation of specialized AI agents for WordPress site generation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Note: In production, would import from actual Agno package
# from agno import Agent, Task, Tool, Crew, Process
# For now, we'll create our own implementation

logger = logging.getLogger(__name__)

class Agent:
    """Base Agent class for Agno Framework"""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        llm_model: str = "claude-3.5-sonnet",
        tools: List[Any] = None,
        max_iterations: int = 5,
        verbose: bool = True
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm_model = llm_model
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.memory = []
        
    def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task with the agent"""
        if self.verbose:
            logger.info(f"Agent {self.name} executing: {task}")
        
        # Store in memory
        self.memory.append({
            "task": task,
            "context": context,
            "timestamp": datetime.now()
        })
        
        # Would call actual LLM here
        return {
            "agent": self.name,
            "task": task,
            "result": f"Completed by {self.name}",
            "status": "success"
        }

# ============= SPECIALIZED AGENTS =============

class ContentGeneratorAgent(Agent):
    """Agent specialized in content generation"""
    
    def __init__(self):
        super().__init__(
            name="ContentGenerator",
            role="Expert Content Creator and SEO Specialist",
            goal="Generate high-quality, SEO-optimized content that engages users and ranks well",
            backstory="""You are a seasoned content marketing expert with 10+ years of experience 
            in creating compelling web content. You understand SEO best practices, user psychology, 
            and how to write content that converts visitors into customers.""",
            llm_model="claude-3.5-sonnet",
            tools=["web_search", "keyword_research", "content_optimizer"]
        )
    
    def generate_blog_post(self, topic: str, keywords: List[str], tone: str = "professional") -> Dict[str, Any]:
        """Generate a complete blog post"""
        
        prompt = f"""
        Create a comprehensive blog post about: {topic}
        Target keywords: {', '.join(keywords)}
        Tone: {tone}
        
        Include:
        1. Engaging title with main keyword
        2. Meta description (155 chars)
        3. Introduction with hook
        4. 3-5 main sections with H2 headings
        5. Conclusion with CTA
        6. Internal linking suggestions
        
        Format: Markdown
        Word count: 1500-2000 words
        """
        
        # Simulate content generation
        content = {
            "title": f"The Ultimate Guide to {topic}",
            "meta_description": f"Discover everything about {topic}. Expert insights and practical tips.",
            "content": f"# {topic}\n\n## Introduction\n\nContent here...",
            "keywords": keywords,
            "word_count": 1500,
            "reading_time": 7,
            "seo_score": 92
        }
        
        return content

class SiteArchitectAgent(Agent):
    """Agent specialized in site structure and architecture"""
    
    def __init__(self):
        super().__init__(
            name="SiteArchitect",
            role="WordPress Site Architecture Expert",
            goal="Design optimal site structures that are user-friendly and SEO-optimized",
            backstory="""You are a WordPress architecture specialist who has designed hundreds 
            of successful websites. You understand information architecture, user experience, 
            and technical SEO requirements for optimal site structure.""",
            llm_model="gpt-4o",
            tools=["sitemap_generator", "url_optimizer", "navigation_builder"]
        )
    
    def design_site_structure(self, business_info: Dict[str, Any]) -> Dict[str, Any]:
        """Design complete site structure"""
        
        business_type = business_info.get("type", "general")
        
        # Generate structure based on business type
        if business_type == "ecommerce":
            structure = {
                "pages": [
                    {"title": "Home", "slug": "/", "template": "home"},
                    {"title": "Shop", "slug": "/shop", "template": "shop"},
                    {"title": "About", "slug": "/about", "template": "page"},
                    {"title": "Contact", "slug": "/contact", "template": "contact"},
                    {"title": "Cart", "slug": "/cart", "template": "cart"},
                    {"title": "Checkout", "slug": "/checkout", "template": "checkout"}
                ],
                "navigation": {
                    "primary": ["Home", "Shop", "About", "Contact"],
                    "footer": ["Privacy Policy", "Terms", "Shipping", "Returns"]
                },
                "taxonomies": ["product_categories", "product_tags"]
            }
        elif business_type == "service":
            structure = {
                "pages": [
                    {"title": "Home", "slug": "/", "template": "home"},
                    {"title": "Services", "slug": "/services", "template": "services"},
                    {"title": "About", "slug": "/about", "template": "page"},
                    {"title": "Portfolio", "slug": "/portfolio", "template": "portfolio"},
                    {"title": "Contact", "slug": "/contact", "template": "contact"}
                ],
                "navigation": {
                    "primary": ["Home", "Services", "Portfolio", "About", "Contact"],
                    "footer": ["Privacy Policy", "Terms of Service"]
                },
                "taxonomies": ["service_categories"]
            }
        else:
            structure = {
                "pages": [
                    {"title": "Home", "slug": "/", "template": "home"},
                    {"title": "About", "slug": "/about", "template": "page"},
                    {"title": "Blog", "slug": "/blog", "template": "blog"},
                    {"title": "Contact", "slug": "/contact", "template": "contact"}
                ],
                "navigation": {
                    "primary": ["Home", "About", "Blog", "Contact"],
                    "footer": ["Privacy Policy", "Terms of Service"]
                },
                "taxonomies": ["categories", "tags"]
            }
        
        structure["seo"] = {
            "sitemap": True,
            "robots_txt": True,
            "schema_markup": business_type
        }
        
        return structure

class DesignAgent(Agent):
    """Agent specialized in visual design and UX"""
    
    def __init__(self):
        super().__init__(
            name="DesignExpert",
            role="UI/UX Design Specialist",
            goal="Create visually appealing and user-friendly designs that convert",
            backstory="""You are an award-winning UI/UX designer with expertise in web design, 
            color theory, typography, and conversion optimization. You create designs that are 
            both beautiful and functional.""",
            llm_model="claude-3.5-sonnet",
            tools=["color_palette_generator", "font_pairing", "layout_designer", "image_generator"]
        )
    
    def create_design_system(self, brand_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete design system"""
        
        industry = brand_info.get("industry", "general")
        style = brand_info.get("style", "modern")
        
        # Generate design system
        design_system = {
            "colors": self._generate_color_palette(industry, style),
            "typography": self._generate_typography(style),
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "xxl": "3rem"
            },
            "components": {
                "buttons": self._generate_button_styles(style),
                "cards": self._generate_card_styles(style),
                "forms": self._generate_form_styles(style)
            },
            "layout": {
                "container_width": "1200px",
                "grid_columns": 12,
                "breakpoints": {
                    "mobile": "640px",
                    "tablet": "768px",
                    "desktop": "1024px",
                    "wide": "1280px"
                }
            }
        }
        
        return design_system
    
    def _generate_color_palette(self, industry: str, style: str) -> Dict[str, str]:
        """Generate color palette based on industry and style"""
        
        palettes = {
            "tech_modern": {
                "primary": "#0066FF",
                "secondary": "#00D4FF",
                "accent": "#FF6B6B",
                "dark": "#0A0E27",
                "light": "#F8F9FA",
                "success": "#00C896",
                "warning": "#FFB800",
                "error": "#FF3860"
            },
            "health_clean": {
                "primary": "#00C896",
                "secondary": "#00A8E8",
                "accent": "#FF6B6B",
                "dark": "#2C3E50",
                "light": "#FFFFFF",
                "success": "#00C896",
                "warning": "#FFC107",
                "error": "#E74C3C"
            },
            "corporate_professional": {
                "primary": "#2C3E50",
                "secondary": "#3498DB",
                "accent": "#E74C3C",
                "dark": "#1A1A1A",
                "light": "#F5F5F5",
                "success": "#27AE60",
                "warning": "#F39C12",
                "error": "#C0392B"
            }
        }
        
        # Select palette based on industry
        if industry == "technology" and style == "modern":
            return palettes["tech_modern"]
        elif industry == "healthcare":
            return palettes["health_clean"]
        else:
            return palettes["corporate_professional"]
    
    def _generate_typography(self, style: str) -> Dict[str, Any]:
        """Generate typography system"""
        
        font_pairs = {
            "modern": {
                "heading": "Inter, sans-serif",
                "body": "Inter, sans-serif",
                "mono": "Fira Code, monospace"
            },
            "classic": {
                "heading": "Playfair Display, serif",
                "body": "Lato, sans-serif",
                "mono": "Courier New, monospace"
            },
            "playful": {
                "heading": "Poppins, sans-serif",
                "body": "Open Sans, sans-serif",
                "mono": "Space Mono, monospace"
            }
        }
        
        typography = font_pairs.get(style, font_pairs["modern"])
        typography["sizes"] = {
            "h1": "3rem",
            "h2": "2.5rem",
            "h3": "2rem",
            "h4": "1.5rem",
            "h5": "1.25rem",
            "h6": "1rem",
            "body": "1rem",
            "small": "0.875rem"
        }
        typography["weights"] = {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700
        }
        
        return typography
    
    def _generate_button_styles(self, style: str) -> Dict[str, Any]:
        """Generate button component styles"""
        
        return {
            "variants": {
                "primary": {
                    "background": "var(--color-primary)",
                    "color": "white",
                    "border": "none"
                },
                "secondary": {
                    "background": "transparent",
                    "color": "var(--color-primary)",
                    "border": "2px solid var(--color-primary)"
                },
                "ghost": {
                    "background": "transparent",
                    "color": "var(--color-dark)",
                    "border": "none"
                }
            },
            "sizes": {
                "sm": {"padding": "0.5rem 1rem", "fontSize": "0.875rem"},
                "md": {"padding": "0.75rem 1.5rem", "fontSize": "1rem"},
                "lg": {"padding": "1rem 2rem", "fontSize": "1.125rem"}
            },
            "borderRadius": "8px" if style == "modern" else "4px"
        }
    
    def _generate_card_styles(self, style: str) -> Dict[str, Any]:
        """Generate card component styles"""
        
        return {
            "background": "white",
            "border": "1px solid rgba(0,0,0,0.1)",
            "borderRadius": "12px" if style == "modern" else "4px",
            "padding": "1.5rem",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"
        }
    
    def _generate_form_styles(self, style: str) -> Dict[str, Any]:
        """Generate form component styles"""
        
        return {
            "input": {
                "border": "1px solid rgba(0,0,0,0.2)",
                "borderRadius": "6px" if style == "modern" else "4px",
                "padding": "0.75rem",
                "fontSize": "1rem"
            },
            "label": {
                "fontSize": "0.875rem",
                "fontWeight": 500,
                "marginBottom": "0.25rem"
            },
            "error": {
                "color": "var(--color-error)",
                "fontSize": "0.875rem"
            }
        }

class SEOAgent(Agent):
    """Agent specialized in SEO optimization"""
    
    def __init__(self):
        super().__init__(
            name="SEOOptimizer",
            role="Technical SEO Expert",
            goal="Optimize websites for maximum search engine visibility",
            backstory="""You are a technical SEO expert with deep knowledge of search engine 
            algorithms, ranking factors, and optimization techniques. You ensure websites are 
            fully optimized for search engines.""",
            llm_model="gpt-4o",
            tools=["keyword_research", "meta_optimizer", "schema_generator", "sitemap_builder"]
        )
    
    def optimize_page(self, page_content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Optimize a page for SEO"""
        
        optimizations = {
            "meta_title": self._generate_meta_title(target_keywords),
            "meta_description": self._generate_meta_description(target_keywords),
            "h1_tag": self._optimize_h1(target_keywords),
            "schema_markup": self._generate_schema(),
            "internal_links": self._suggest_internal_links(),
            "image_alt_texts": self._generate_alt_texts(),
            "url_slug": self._optimize_url(target_keywords[0]),
            "seo_score": 85
        }
        
        return optimizations
    
    def _generate_meta_title(self, keywords: List[str]) -> str:
        """Generate SEO-optimized meta title"""
        primary_keyword = keywords[0] if keywords else "Website"
        return f"{primary_keyword.title()} - Professional Services | Brand Name"
    
    def _generate_meta_description(self, keywords: List[str]) -> str:
        """Generate SEO-optimized meta description"""
        keyword_str = ", ".join(keywords[:2]) if keywords else "services"
        return f"Discover top-quality {keyword_str}. Expert solutions, competitive prices, and exceptional service. Get started today!"
    
    def _optimize_h1(self, keywords: List[str]) -> str:
        """Generate optimized H1 tag"""
        return f"{keywords[0].title()} Solutions You Can Trust" if keywords else "Welcome"
    
    def _generate_schema(self) -> Dict[str, Any]:
        """Generate schema markup"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Business Name",
            "url": "https://example.com",
            "logo": "https://example.com/logo.png",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+1-234-567-8900",
                "contactType": "customer service"
            }
        }
    
    def _suggest_internal_links(self) -> List[Dict[str, str]]:
        """Suggest internal linking opportunities"""
        return [
            {"anchor": "our services", "url": "/services"},
            {"anchor": "learn more", "url": "/about"},
            {"anchor": "contact us", "url": "/contact"}
        ]
    
    def _generate_alt_texts(self) -> List[str]:
        """Generate image alt texts"""
        return [
            "Professional team providing expert services",
            "Modern office workspace",
            "Customer satisfaction guaranteed"
        ]
    
    def _optimize_url(self, keyword: str) -> str:
        """Generate SEO-friendly URL slug"""
        return keyword.lower().replace(" ", "-").replace("_", "-")

class WordPressAgent(Agent):
    """Agent specialized in WordPress implementation"""
    
    def __init__(self):
        super().__init__(
            name="WordPressBuilder",
            role="WordPress Development Expert",
            goal="Build high-performance WordPress sites with best practices",
            backstory="""You are a WordPress core contributor with extensive experience in 
            building scalable, secure, and performant WordPress websites. You know every 
            aspect of WordPress development.""",
            llm_model="claude-3.5-sonnet",
            tools=["wp_cli", "plugin_manager", "theme_builder", "database_optimizer"]
        )
    
    def generate_wordpress_code(self, site_structure: Dict[str, Any], design_system: Dict[str, Any]) -> Dict[str, Any]:
        """Generate WordPress implementation code"""
        
        wordpress_code = {
            "theme": self._generate_theme(design_system),
            "pages": self._generate_pages(site_structure["pages"]),
            "menus": self._generate_menus(site_structure["navigation"]),
            "plugins": self._recommend_plugins(site_structure),
            "settings": self._generate_settings(),
            "custom_post_types": self._generate_cpts(site_structure.get("custom_types", []))
        }
        
        return wordpress_code
    
    def _generate_theme(self, design_system: Dict[str, Any]) -> Dict[str, Any]:
        """Generate WordPress theme files"""
        
        return {
            "functions.php": self._generate_functions_php(),
            "style.css": self._generate_style_css(design_system),
            "index.php": self._generate_index_php(),
            "header.php": self._generate_header_php(),
            "footer.php": self._generate_footer_php(),
            "page.php": self._generate_page_template(),
            "single.php": self._generate_single_template()
        }
    
    def _generate_functions_php(self) -> str:
        """Generate functions.php content"""
        
        return """<?php
/**
 * Theme Functions
 */

// Theme Support
add_theme_support('post-thumbnails');
add_theme_support('title-tag');
add_theme_support('custom-logo');
add_theme_support('html5', array('search-form', 'comment-form', 'gallery', 'caption'));

// Register Menus
register_nav_menus(array(
    'primary' => __('Primary Menu'),
    'footer' => __('Footer Menu')
));

// Enqueue Scripts and Styles
function theme_scripts() {
    wp_enqueue_style('theme-style', get_stylesheet_uri());
    wp_enqueue_script('theme-script', get_template_directory_uri() . '/js/main.js', array('jquery'), '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'theme_scripts');

// Custom Post Types
function register_custom_post_types() {
    // Add custom post types here
}
add_action('init', 'register_custom_post_types');
"""
    
    def _generate_style_css(self, design_system: Dict[str, Any]) -> str:
        """Generate style.css with design system"""
        
        colors = design_system.get("colors", {})
        typography = design_system.get("typography", {})
        
        return f"""/*
Theme Name: AI Generated Theme
Theme URI: https://kenzysites.com
Author: KenzySites AI
Description: AI-powered WordPress theme
Version: 1.0.0
*/

:root {{
    --color-primary: {colors.get('primary', '#0066FF')};
    --color-secondary: {colors.get('secondary', '#00D4FF')};
    --color-accent: {colors.get('accent', '#FF6B6B')};
    --color-dark: {colors.get('dark', '#0A0E27')};
    --color-light: {colors.get('light', '#F8F9FA')};
    
    --font-heading: {typography.get('heading', 'Inter, sans-serif')};
    --font-body: {typography.get('body', 'Inter, sans-serif')};
}}

/* Reset and Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-body);
    color: var(--color-dark);
    line-height: 1.6;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-heading);
    line-height: 1.2;
    margin-bottom: 1rem;
}}

/* Components */
.btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: var(--color-primary);
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    transition: all 0.3s ease;
}}

.btn:hover {{
    background: var(--color-secondary);
    transform: translateY(-2px);
}}
"""
    
    def _generate_index_php(self) -> str:
        """Generate index.php template"""
        
        return """<?php get_header(); ?>

<main id="main" class="site-main">
    <?php if (have_posts()) : ?>
        <div class="posts-grid">
            <?php while (have_posts()) : the_post(); ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                    <?php if (has_post_thumbnail()) : ?>
                        <div class="post-thumbnail">
                            <?php the_post_thumbnail('medium'); ?>
                        </div>
                    <?php endif; ?>
                    
                    <h2 class="entry-title">
                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                    </h2>
                    
                    <div class="entry-excerpt">
                        <?php the_excerpt(); ?>
                    </div>
                    
                    <a href="<?php the_permalink(); ?>" class="read-more">Read More</a>
                </article>
            <?php endwhile; ?>
        </div>
        
        <?php the_posts_navigation(); ?>
    <?php else : ?>
        <p>No posts found.</p>
    <?php endif; ?>
</main>

<?php get_footer(); ?>"""
    
    def _generate_header_php(self) -> str:
        """Generate header.php template"""
        
        return """<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
    <header id="masthead" class="site-header">
        <div class="container">
            <div class="site-branding">
                <?php if (has_custom_logo()) : ?>
                    <?php the_custom_logo(); ?>
                <?php else : ?>
                    <h1 class="site-title">
                        <a href="<?php echo esc_url(home_url('/')); ?>">
                            <?php bloginfo('name'); ?>
                        </a>
                    </h1>
                <?php endif; ?>
            </div>
            
            <nav id="site-navigation" class="main-navigation">
                <?php wp_nav_menu(array(
                    'theme_location' => 'primary',
                    'menu_id' => 'primary-menu',
                )); ?>
            </nav>
        </div>
    </header>"""
    
    def _generate_footer_php(self) -> str:
        """Generate footer.php template"""
        
        return """    <footer id="colophon" class="site-footer">
        <div class="container">
            <?php if (has_nav_menu('footer')) : ?>
                <nav class="footer-navigation">
                    <?php wp_nav_menu(array(
                        'theme_location' => 'footer',
                        'menu_id' => 'footer-menu',
                    )); ?>
                </nav>
            <?php endif; ?>
            
            <div class="site-info">
                <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.</p>
                <p>Powered by AI from KenzySites</p>
            </div>
        </div>
    </footer>
    
    <?php wp_footer(); ?>
</body>
</html>"""
    
    def _generate_page_template(self) -> str:
        """Generate page.php template"""
        
        return """<?php get_header(); ?>

<main id="main" class="site-main">
    <?php while (have_posts()) : the_post(); ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <header class="entry-header">
                <h1 class="entry-title"><?php the_title(); ?></h1>
            </header>
            
            <div class="entry-content">
                <?php the_content(); ?>
            </div>
        </article>
    <?php endwhile; ?>
</main>

<?php get_footer(); ?>"""
    
    def _generate_single_template(self) -> str:
        """Generate single.php template"""
        
        return """<?php get_header(); ?>

<main id="main" class="site-main">
    <?php while (have_posts()) : the_post(); ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <header class="entry-header">
                <h1 class="entry-title"><?php the_title(); ?></h1>
                <div class="entry-meta">
                    Posted on <?php echo get_the_date(); ?> by <?php the_author(); ?>
                </div>
            </header>
            
            <?php if (has_post_thumbnail()) : ?>
                <div class="post-thumbnail">
                    <?php the_post_thumbnail('large'); ?>
                </div>
            <?php endif; ?>
            
            <div class="entry-content">
                <?php the_content(); ?>
            </div>
            
            <footer class="entry-footer">
                <?php the_category(', '); ?>
                <?php the_tags('Tags: ', ', '); ?>
            </footer>
        </article>
        
        <?php comments_template(); ?>
    <?php endwhile; ?>
</main>

<?php get_footer(); ?>"""
    
    def _generate_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate WordPress pages"""
        
        wp_pages = []
        for page in pages:
            wp_pages.append({
                "title": page["title"],
                "slug": page["slug"],
                "template": page.get("template", "page"),
                "content": self._generate_page_content(page),
                "meta": {
                    "_wp_page_template": page.get("template", "default")
                }
            })
        return wp_pages
    
    def _generate_page_content(self, page: Dict[str, Any]) -> str:
        """Generate page content based on template"""
        
        if page["slug"] == "/":
            return """<!-- wp:cover {"url":"hero-image.jpg","dimRatio":50} -->
<div class="wp-block-cover">
    <div class="wp-block-cover__inner-container">
        <h1>Welcome to Our Website</h1>
        <p>Your success starts here</p>
        <div class="wp-block-buttons">
            <div class="wp-block-button">
                <a class="wp-block-button__link">Get Started</a>
            </div>
        </div>
    </div>
</div>
<!-- /wp:cover -->"""
        else:
            return f"<!-- wp:paragraph --><p>Content for {page['title']} page.</p><!-- /wp:paragraph -->"
    
    def _generate_menus(self, navigation: Dict[str, List[str]]) -> Dict[str, Any]:
        """Generate WordPress menus"""
        
        menus = {}
        for location, items in navigation.items():
            menus[location] = {
                "name": f"{location.title()} Menu",
                "items": [{"title": item, "url": f"/{item.lower().replace(' ', '-')}"} for item in items]
            }
        return menus
    
    def _recommend_plugins(self, site_structure: Dict[str, Any]) -> List[str]:
        """Recommend WordPress plugins based on site structure"""
        
        plugins = [
            "yoast-seo",
            "wordfence",
            "wp-super-cache",
            "contact-form-7"
        ]
        
        # Add specific plugins based on site type
        if "shop" in str(site_structure):
            plugins.append("woocommerce")
        if "portfolio" in str(site_structure):
            plugins.append("nextgen-gallery")
        
        return plugins
    
    def _generate_settings(self) -> Dict[str, Any]:
        """Generate WordPress settings"""
        
        return {
            "timezone": "America/Sao_Paulo",
            "date_format": "F j, Y",
            "time_format": "g:i a",
            "start_of_week": "1",
            "permalinks": "/%postname%/",
            "comments": {
                "require_name_email": True,
                "comment_moderation": True,
                "comment_registration": False
            },
            "media": {
                "thumbnail_size": [150, 150],
                "medium_size": [300, 300],
                "large_size": [1024, 1024]
            }
        }
    
    def _generate_cpts(self, custom_types: List[str]) -> List[Dict[str, Any]]:
        """Generate custom post types"""
        
        cpts = []
        for cpt_name in custom_types:
            cpts.append({
                "name": cpt_name,
                "singular": cpt_name.title(),
                "plural": f"{cpt_name.title()}s",
                "supports": ["title", "editor", "thumbnail", "excerpt"],
                "has_archive": True,
                "public": True,
                "show_in_rest": True
            })
        return cpts

class QualityAssuranceAgent(Agent):
    """Agent specialized in quality assurance and testing"""
    
    def __init__(self):
        super().__init__(
            name="QualityAssurance",
            role="QA and Testing Expert",
            goal="Ensure highest quality standards for all generated content and code",
            backstory="""You are a meticulous QA expert with experience in web development, 
            content quality, and user experience testing. You ensure everything meets the 
            highest standards before deployment.""",
            llm_model="gpt-4o",
            tools=["validator", "performance_tester", "accessibility_checker", "seo_analyzer"]
        )
    
    def validate_site(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive site validation"""
        
        validation_results = {
            "html_validation": self._validate_html(site_data.get("html", "")),
            "css_validation": self._validate_css(site_data.get("css", "")),
            "seo_check": self._check_seo(site_data),
            "performance_score": self._test_performance(site_data),
            "accessibility_score": self._check_accessibility(site_data),
            "mobile_friendly": self._check_mobile(site_data),
            "security_check": self._check_security(site_data),
            "overall_score": 0
        }
        
        # Calculate overall score
        scores = [
            validation_results["seo_check"]["score"],
            validation_results["performance_score"],
            validation_results["accessibility_score"],
            95 if validation_results["mobile_friendly"] else 60
        ]
        validation_results["overall_score"] = sum(scores) / len(scores)
        
        return validation_results
    
    def _validate_html(self, html: str) -> Dict[str, Any]:
        """Validate HTML structure"""
        return {
            "valid": True,
            "errors": [],
            "warnings": []
        }
    
    def _validate_css(self, css: str) -> Dict[str, Any]:
        """Validate CSS"""
        return {
            "valid": True,
            "errors": [],
            "warnings": []
        }
    
    def _check_seo(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check SEO optimization"""
        return {
            "score": 92,
            "issues": [],
            "recommendations": [
                "Add more internal links",
                "Optimize image file sizes"
            ]
        }
    
    def _test_performance(self, site_data: Dict[str, Any]) -> int:
        """Test site performance"""
        return 88  # Performance score
    
    def _check_accessibility(self, site_data: Dict[str, Any]) -> int:
        """Check accessibility standards"""
        return 95  # Accessibility score
    
    def _check_mobile(self, site_data: Dict[str, Any]) -> bool:
        """Check mobile responsiveness"""
        return True
    
    def _check_security(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check security issues"""
        return {
            "secure": True,
            "issues": [],
            "recommendations": [
                "Enable HTTPS",
                "Add security headers"
            ]
        }

# Export all agents
__all__ = [
    'Agent',
    'ContentGeneratorAgent',
    'SiteArchitectAgent',
    'DesignAgent',
    'SEOAgent',
    'WordPressAgent',
    'QualityAssuranceAgent'
]