"""
Block Patterns Library
Biblioteca de 20+ patterns de blocos Gutenberg/Spectra
Similar ao ZIPWP - Templates pré-construídos para montagem rápida
"""

from typing import Dict, List, Any

class BlockPatternsLibrary:
    """
    Biblioteca de patterns de blocos para geração de sites
    Cada pattern é um template de seção pronto para usar
    """
    
    def __init__(self):
        self.patterns = self._load_all_patterns()
        self.categories = [
            "hero", "about", "services", "features", "testimonials",
            "pricing", "team", "portfolio", "contact", "cta",
            "stats", "gallery", "faq", "blog", "footer"
        ]
    
    def _load_all_patterns(self) -> Dict[str, List[Dict]]:
        """Carrega todos os patterns organizados por categoria"""
        return {
            "hero": self._get_hero_patterns(),
            "about": self._get_about_patterns(),
            "services": self._get_services_patterns(),
            "features": self._get_features_patterns(),
            "testimonials": self._get_testimonials_patterns(),
            "pricing": self._get_pricing_patterns(),
            "team": self._get_team_patterns(),
            "portfolio": self._get_portfolio_patterns(),
            "contact": self._get_contact_patterns(),
            "cta": self._get_cta_patterns(),
            "stats": self._get_stats_patterns(),
            "gallery": self._get_gallery_patterns(),
            "faq": self._get_faq_patterns(),
            "blog": self._get_blog_patterns(),
            "footer": self._get_footer_patterns()
        }
    
    def get_pattern(self, category: str, variant: str = "default") -> str:
        """Retorna um pattern específico"""
        patterns = self.patterns.get(category, [])
        for pattern in patterns:
            if pattern["variant"] == variant:
                return pattern["content"]
        return patterns[0]["content"] if patterns else ""
    
    def get_patterns_for_business(self, business_type: str) -> List[Dict]:
        """Retorna patterns recomendados para tipo de negócio"""
        recommendations = {
            "restaurant": ["hero_image_overlay", "about_split", "menu_showcase", 
                          "testimonials_carousel", "contact_with_map"],
            "professional": ["hero_minimal", "services_grid", "about_corporate",
                            "team_grid", "testimonials_simple", "contact_form"],
            "ecommerce": ["hero_product", "features_icons", "products_grid",
                         "testimonials_cards", "cta_sale"],
            "health": ["hero_medical", "services_medical", "team_doctors",
                      "testimonials_health", "contact_appointment"],
            "education": ["hero_education", "courses_grid", "team_instructors",
                         "testimonials_students", "cta_enrollment"]
        }
        
        pattern_ids = recommendations.get(business_type, recommendations["professional"])
        patterns = []
        
        for pattern_id in pattern_ids:
            category, variant = pattern_id.split("_", 1)
            patterns.append({
                "category": category,
                "variant": variant,
                "content": self.get_pattern(category, variant)
            })
        
        return patterns
    
    def _get_hero_patterns(self) -> List[Dict]:
        """Patterns para seção Hero"""
        return [
            {
                "variant": "minimal",
                "name": "Hero Minimalista",
                "content": """
<!-- wp:uagb/section {"block_id":"hero-minimal","contentWidth":"full_width","minHeight":600,"backgroundType":"color"} -->
<section class="wp-block-uagb-section uagb-section__wrap uagb-hero-minimal">
<div class="uagb-section__overlay"></div>
<div class="uagb-section__inner-wrap">
<!-- wp:uagb/container {"block_id":"hero-container","contentWidth":"content"} -->
<div class="wp-block-uagb-container alignfull">
<!-- wp:uagb/advanced-heading {"block_id":"hero-title","headingTag":"h1","headingAlign":"center","headingColor":"#1e293b","fontSize":48} -->
<h1 class="wp-block-uagb-advanced-heading">{{headline}}</h1>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:paragraph {"align":"center","fontSize":"large"} -->
<p class="has-text-align-center has-large-font-size">{{subtitle}}</p>
<!-- /wp:paragraph -->

<!-- wp:uagb/buttons {"block_id":"hero-buttons","align":"center","gap":20} -->
<div class="wp-block-uagb-buttons uagb-buttons__outer-wrap">
<!-- wp:uagb/buttons-child {"block_id":"hero-btn-primary","buttonType":"primary","size":"large"} -->
<div class="uagb-button__wrapper">
<a class="uagb-button__link" href="#contato">{{cta_primary}}</a>
</div>
<!-- /wp:uagb/buttons-child -->
<!-- wp:uagb/buttons-child {"block_id":"hero-btn-secondary","buttonType":"secondary","size":"large"} -->
<div class="uagb-button__wrapper">
<a class="uagb-button__link" href="#sobre">{{cta_secondary}}</a>
</div>
<!-- /wp:uagb/buttons-child -->
</div>
<!-- /wp:uagb/buttons -->
</div>
<!-- /wp:uagb/container -->
</div>
</section>
<!-- /wp:uagb/section -->"""
            },
            {
                "variant": "image_overlay",
                "name": "Hero com Imagem de Fundo",
                "content": """
<!-- wp:uagb/section {"block_id":"hero-overlay","contentWidth":"full_width","minHeight":700,"backgroundType":"image","backgroundImage":{"url":"{{hero_image}}"},"overlayType":"color","overlayColor":"#000000","overlayOpacity":50} -->
<section class="wp-block-uagb-section uagb-section__wrap uagb-hero-overlay">
<div class="uagb-section__overlay"></div>
<div class="uagb-section__inner-wrap">
<!-- wp:uagb/advanced-heading {"block_id":"hero-title-overlay","headingTag":"h1","headingAlign":"center","headingColor":"#ffffff","fontSize":56} -->
<h1 class="wp-block-uagb-advanced-heading" style="color:#ffffff">{{headline}}</h1>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:paragraph {"align":"center","style":{"color":{"text":"#ffffff"}},"fontSize":"x-large"} -->
<p class="has-text-align-center has-text-color has-x-large-font-size" style="color:#ffffff">{{subtitle}}</p>
<!-- /wp:paragraph -->

<!-- wp:uagb/buttons {"block_id":"hero-cta-overlay","align":"center"} -->
<div class="wp-block-uagb-buttons uagb-buttons__outer-wrap">
<a class="uagb-button__link uagb-button__size-large" href="#contato">{{cta_primary}}</a>
</div>
<!-- /wp:uagb/buttons -->
</div>
</section>
<!-- /wp:uagb/section -->"""
            },
            {
                "variant": "split",
                "name": "Hero Split Screen",
                "content": """
<!-- wp:uagb/section {"block_id":"hero-split","contentWidth":"full_width"} -->
<section class="wp-block-uagb-section uagb-section__wrap">
<div class="uagb-section__inner-wrap">
<!-- wp:columns {"verticalAlignment":"center"} -->
<div class="wp-block-columns are-vertically-aligned-center">
<!-- wp:column {"verticalAlignment":"center"} -->
<div class="wp-block-column is-vertically-aligned-center">
<!-- wp:uagb/advanced-heading {"block_id":"split-heading","headingTag":"h1"} -->
<h1 class="wp-block-uagb-advanced-heading">{{headline}}</h1>
<!-- /wp:uagb/advanced-heading -->
<!-- wp:paragraph {"fontSize":"medium"} -->
<p class="has-medium-font-size">{{description}}</p>
<!-- /wp:paragraph -->
<!-- wp:uagb/buttons {"block_id":"split-buttons"} -->
<div class="wp-block-uagb-buttons">
<a class="uagb-button__link" href="#contato">{{cta_primary}}</a>
</div>
<!-- /wp:uagb/buttons -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:image {"sizeSlug":"large"} -->
<figure class="wp-block-image size-large"><img src="{{hero_image}}" alt="{{business_name}}"/></figure>
<!-- /wp:image -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</div>
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_services_patterns(self) -> List[Dict]:
        """Patterns para seção de Serviços"""
        return [
            {
                "variant": "grid",
                "name": "Grid de Serviços",
                "content": """
<!-- wp:uagb/section {"block_id":"services-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"services-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Nossos Serviços</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/post-grid {"block_id":"services-grid","columns":3,"columnsMobile":1,"columnsTablet":2} -->
<div class="wp-block-uagb-post-grid uagb-post-grid">

<!-- wp:uagb/info-box {"block_id":"service-1","iconView":"framed","icon":"dashboard","headingTag":"h3"} -->
<div class="wp-block-uagb-info-box">
<div class="uagb-ifb-icon-wrap"><span class="uagb-ifb-icon"><i class="fas fa-chart-line"></i></span></div>
<div class="uagb-ifb-content">
<h3 class="uagb-ifb-title">{{service_1_title}}</h3>
<p class="uagb-ifb-desc">{{service_1_description}}</p>
</div>
</div>
<!-- /wp:uagb/info-box -->

<!-- wp:uagb/info-box {"block_id":"service-2","iconView":"framed","icon":"support","headingTag":"h3"} -->
<div class="wp-block-uagb-info-box">
<div class="uagb-ifb-icon-wrap"><span class="uagb-ifb-icon"><i class="fas fa-headset"></i></span></div>
<div class="uagb-ifb-content">
<h3 class="uagb-ifb-title">{{service_2_title}}</h3>
<p class="uagb-ifb-desc">{{service_2_description}}</p>
</div>
</div>
<!-- /wp:uagb/info-box -->

<!-- wp:uagb/info-box {"block_id":"service-3","iconView":"framed","icon":"settings","headingTag":"h3"} -->
<div class="wp-block-uagb-info-box">
<div class="uagb-ifb-icon-wrap"><span class="uagb-ifb-icon"><i class="fas fa-cog"></i></span></div>
<div class="uagb-ifb-content">
<h3 class="uagb-ifb-title">{{service_3_title}}</h3>
<p class="uagb-ifb-desc">{{service_3_description}}</p>
</div>
</div>
<!-- /wp:uagb/info-box -->

</div>
<!-- /wp:uagb/post-grid -->
</section>
<!-- /wp:uagb/section -->"""
            },
            {
                "variant": "cards",
                "name": "Cards de Serviços",
                "content": """
<!-- wp:uagb/section {"block_id":"services-cards"} -->
<section class="wp-block-uagb-section">
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/marketing-button {"block_id":"service-card-1","headingTag":"h3","headingAlign":"center","iconPosition":"above"} -->
<div class="wp-block-uagb-marketing-button">
<h3 class="uagb-marketing-btn__title">{{service_1_title}}</h3>
<p class="uagb-marketing-btn__prefix">{{service_1_description}}</p>
<a class="uagb-marketing-btn__link" href="#service1">Saiba Mais</a>
</div>
<!-- /wp:uagb/marketing-button -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/marketing-button {"block_id":"service-card-2","headingTag":"h3","headingAlign":"center"} -->
<div class="wp-block-uagb-marketing-button">
<h3 class="uagb-marketing-btn__title">{{service_2_title}}</h3>
<p class="uagb-marketing-btn__prefix">{{service_2_description}}</p>
<a class="uagb-marketing-btn__link" href="#service2">Saiba Mais</a>
</div>
<!-- /wp:uagb/marketing-button -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/marketing-button {"block_id":"service-card-3","headingTag":"h3","headingAlign":"center"} -->
<div class="wp-block-uagb-marketing-button">
<h3 class="uagb-marketing-btn__title">{{service_3_title}}</h3>
<p class="uagb-marketing-btn__prefix">{{service_3_description}}</p>
<a class="uagb-marketing-btn__link" href="#service3">Saiba Mais</a>
</div>
<!-- /wp:uagb/marketing-button -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_about_patterns(self) -> List[Dict]:
        """Patterns para seção Sobre"""
        return [
            {
                "variant": "split",
                "name": "Sobre com Imagem Lateral",
                "content": """
<!-- wp:uagb/section {"block_id":"about-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:columns {"verticalAlignment":"center"} -->
<div class="wp-block-columns are-vertically-aligned-center">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:image {"sizeSlug":"large"} -->
<figure class="wp-block-image size-large"><img src="{{about_image}}" alt="Sobre {{business_name}}"/></figure>
<!-- /wp:image -->
</div>
<!-- /wp:column -->
<!-- wp:column {"verticalAlignment":"center"} -->
<div class="wp-block-column is-vertically-aligned-center">
<!-- wp:uagb/advanced-heading {"block_id":"about-heading","headingTag":"h2"} -->
<h2 class="wp-block-uagb-advanced-heading">{{about_title}}</h2>
<!-- /wp:uagb/advanced-heading -->
<!-- wp:paragraph -->
<p>{{about_description}}</p>
<!-- /wp:paragraph -->
<!-- wp:uagb/icon-list {"block_id":"about-list","hideLabel":false} -->
<div class="wp-block-uagb-icon-list">
<ul class="uagb-icon-list__wrapper">
<li class="uagb-icon-list-item"><span class="uagb-icon-list__icon"><i class="fas fa-check"></i></span><span>{{about_point_1}}</span></li>
<li class="uagb-icon-list-item"><span class="uagb-icon-list__icon"><i class="fas fa-check"></i></span><span>{{about_point_2}}</span></li>
<li class="uagb-icon-list-item"><span class="uagb-icon-list__icon"><i class="fas fa-check"></i></span><span>{{about_point_3}}</span></li>
</ul>
</div>
<!-- /wp:uagb/icon-list -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:uagb/section -->"""
            },
            {
                "variant": "centered",
                "name": "Sobre Centralizado",
                "content": """
<!-- wp:uagb/section {"block_id":"about-centered"} -->
<section class="wp-block-uagb-section">
<div class="uagb-section__inner-wrap">
<!-- wp:uagb/advanced-heading {"block_id":"about-title-centered","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">{{about_title}}</h2>
<!-- /wp:uagb/advanced-heading -->
<!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center">{{about_description}}</p>
<!-- /wp:paragraph -->
<!-- wp:uagb/counter {"block_id":"about-stats","columns":3} -->
<div class="wp-block-uagb-counter">
<div class="uagb-counter-item">
<span class="uagb-counter-number">{{stat_1_number}}</span>
<span class="uagb-counter-title">{{stat_1_label}}</span>
</div>
<div class="uagb-counter-item">
<span class="uagb-counter-number">{{stat_2_number}}</span>
<span class="uagb-counter-title">{{stat_2_label}}</span>
</div>
<div class="uagb-counter-item">
<span class="uagb-counter-number">{{stat_3_number}}</span>
<span class="uagb-counter-title">{{stat_3_label}}</span>
</div>
</div>
<!-- /wp:uagb/counter -->
</div>
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_testimonials_patterns(self) -> List[Dict]:
        """Patterns para Testemunhos"""
        return [
            {
                "variant": "carousel",
                "name": "Carrossel de Testemunhos",
                "content": """
<!-- wp:uagb/section {"block_id":"testimonials-section","backgroundType":"color","backgroundColor":"#f8f9fa"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"testimonials-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">O Que Nossos Clientes Dizem</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/testimonial {"block_id":"testimonials","test_item_count":3,"columns":1,"tcolumns":1,"mcolumns":1,"pauseOnHover":true,"infiniteLoop":true,"transitionSpeed":500} -->
<div class="wp-block-uagb-testimonial">
<div class="uagb-testimonial__wrap uagb-slick-carousel">

<div class="uagb-testimonial__item">
<div class="uagb-testimonial__content">
<div class="uagb-tm__text">{{testimonial_1_text}}</div>
<div class="uagb-tm__meta">
<div class="uagb-tm__author">{{testimonial_1_author}}</div>
<div class="uagb-tm__company">{{testimonial_1_company}}</div>
</div>
</div>
</div>

<div class="uagb-testimonial__item">
<div class="uagb-testimonial__content">
<div class="uagb-tm__text">{{testimonial_2_text}}</div>
<div class="uagb-tm__meta">
<div class="uagb-tm__author">{{testimonial_2_author}}</div>
<div class="uagb-tm__company">{{testimonial_2_company}}</div>
</div>
</div>
</div>

<div class="uagb-testimonial__item">
<div class="uagb-testimonial__content">
<div class="uagb-tm__text">{{testimonial_3_text}}</div>
<div class="uagb-tm__meta">
<div class="uagb-tm__author">{{testimonial_3_author}}</div>
<div class="uagb-tm__company">{{testimonial_3_company}}</div>
</div>
</div>
</div>

</div>
</div>
<!-- /wp:uagb/testimonial -->
</section>
<!-- /wp:uagb/section -->"""
            },
            {
                "variant": "grid",
                "name": "Grid de Testemunhos",
                "content": """
<!-- wp:uagb/section {"block_id":"testimonials-grid"} -->
<section class="wp-block-uagb-section">
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/blockquote {"block_id":"quote-1"} -->
<blockquote class="wp-block-uagb-blockquote">
<p>{{testimonial_1_text}}</p>
<cite>{{testimonial_1_author}}</cite>
</blockquote>
<!-- /wp:uagb/blockquote -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/blockquote {"block_id":"quote-2"} -->
<blockquote class="wp-block-uagb-blockquote">
<p>{{testimonial_2_text}}</p>
<cite>{{testimonial_2_author}}</cite>
</blockquote>
<!-- /wp:uagb/blockquote -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/blockquote {"block_id":"quote-3"} -->
<blockquote class="wp-block-uagb-blockquote">
<p>{{testimonial_3_text}}</p>
<cite>{{testimonial_3_author}}</cite>
</blockquote>
<!-- /wp:uagb/blockquote -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_features_patterns(self) -> List[Dict]:
        """Patterns para Features/Características"""
        return [
            {
                "variant": "icons",
                "name": "Features com Ícones",
                "content": """
<!-- wp:uagb/section {"block_id":"features-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"features-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Por Que Nos Escolher</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/icon {"block_id":"feature-icon-1","icon":"shield","iconSize":40,"iconColor":"#3b82f6"} -->
<div class="wp-block-uagb-icon"><i class="fas fa-shield-alt"></i></div>
<!-- /wp:uagb/icon -->
<!-- wp:heading {"level":3,"textAlign":"center"} -->
<h3 class="has-text-align-center">{{feature_1_title}}</h3>
<!-- /wp:heading -->
<!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center">{{feature_1_description}}</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/icon {"block_id":"feature-icon-2","icon":"clock","iconSize":40,"iconColor":"#3b82f6"} -->
<div class="wp-block-uagb-icon"><i class="fas fa-clock"></i></div>
<!-- /wp:uagb/icon -->
<!-- wp:heading {"level":3,"textAlign":"center"} -->
<h3 class="has-text-align-center">{{feature_2_title}}</h3>
<!-- /wp:heading -->
<!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center">{{feature_2_description}}</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/icon {"block_id":"feature-icon-3","icon":"award","iconSize":40,"iconColor":"#3b82f6"} -->
<div class="wp-block-uagb-icon"><i class="fas fa-award"></i></div>
<!-- /wp:uagb/icon -->
<!-- wp:heading {"level":3,"textAlign":"center"} -->
<h3 class="has-text-align-center">{{feature_3_title}}</h3>
<!-- /wp:heading -->
<!-- wp:paragraph {"align":"center"} -->
<p class="has-text-align-center">{{feature_3_description}}</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_pricing_patterns(self) -> List[Dict]:
        """Patterns para Preços"""
        return [
            {
                "variant": "table",
                "name": "Tabela de Preços",
                "content": """
<!-- wp:uagb/section {"block_id":"pricing-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"pricing-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Nossos Planos</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/pricing-table {"block_id":"pricing-table","columns":3} -->
<div class="wp-block-uagb-pricing-table">
<!-- wp:uagb/pricing-table-item {"block_id":"pricing-basic"} -->
<div class="uagb-pricing-table-item">
<div class="uagb-pricing-table__header">
<h3 class="uagb-pricing-table__title">{{plan_1_name}}</h3>
</div>
<div class="uagb-pricing-table__price-wrapper">
<span class="uagb-pricing-table__currency">R$</span>
<span class="uagb-pricing-table__amount">{{plan_1_price}}</span>
<span class="uagb-pricing-table__duration">/mês</span>
</div>
<ul class="uagb-pricing-table__features">
<li>{{plan_1_feature_1}}</li>
<li>{{plan_1_feature_2}}</li>
<li>{{plan_1_feature_3}}</li>
</ul>
<div class="uagb-pricing-table__button-wrap">
<a class="uagb-pricing-table__button" href="#contato">Começar Agora</a>
</div>
</div>
<!-- /wp:uagb/pricing-table-item -->

<!-- wp:uagb/pricing-table-item {"block_id":"pricing-pro","featured":true} -->
<div class="uagb-pricing-table-item uagb-pricing-table-featured">
<div class="uagb-pricing-table__header">
<h3 class="uagb-pricing-table__title">{{plan_2_name}}</h3>
<span class="uagb-pricing-table__ribbon">Mais Popular</span>
</div>
<div class="uagb-pricing-table__price-wrapper">
<span class="uagb-pricing-table__currency">R$</span>
<span class="uagb-pricing-table__amount">{{plan_2_price}}</span>
<span class="uagb-pricing-table__duration">/mês</span>
</div>
<ul class="uagb-pricing-table__features">
<li>{{plan_2_feature_1}}</li>
<li>{{plan_2_feature_2}}</li>
<li>{{plan_2_feature_3}}</li>
</ul>
<div class="uagb-pricing-table__button-wrap">
<a class="uagb-pricing-table__button" href="#contato">Começar Agora</a>
</div>
</div>
<!-- /wp:uagb/pricing-table-item -->

<!-- wp:uagb/pricing-table-item {"block_id":"pricing-enterprise"} -->
<div class="uagb-pricing-table-item">
<div class="uagb-pricing-table__header">
<h3 class="uagb-pricing-table__title">{{plan_3_name}}</h3>
</div>
<div class="uagb-pricing-table__price-wrapper">
<span class="uagb-pricing-table__currency">R$</span>
<span class="uagb-pricing-table__amount">{{plan_3_price}}</span>
<span class="uagb-pricing-table__duration">/mês</span>
</div>
<ul class="uagb-pricing-table__features">
<li>{{plan_3_feature_1}}</li>
<li>{{plan_3_feature_2}}</li>
<li>{{plan_3_feature_3}}</li>
</ul>
<div class="uagb-pricing-table__button-wrap">
<a class="uagb-pricing-table__button" href="#contato">Fale Conosco</a>
</div>
</div>
<!-- /wp:uagb/pricing-table-item -->
</div>
<!-- /wp:uagb/pricing-table -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_contact_patterns(self) -> List[Dict]:
        """Patterns para Contato"""
        return [
            {
                "variant": "form",
                "name": "Formulário de Contato",
                "content": """
<!-- wp:uagb/section {"block_id":"contact-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"contact-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Entre em Contato</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column {"width":"60%"} -->
<div class="wp-block-column" style="flex-basis:60%">
<!-- wp:uagb/forms {"block_id":"contact-form"} -->
<div class="wp-block-uagb-forms">
<form class="uagb-forms-main-form">
<!-- wp:uagb/forms-name {"block_id":"form-name","nameRequired":true,"label":"Nome Completo"} -->
<div class="uagb-forms-name-wrap">
<label>Nome Completo <span class="required">*</span></label>
<input type="text" name="name" required />
</div>
<!-- /wp:uagb/forms-name -->

<!-- wp:uagb/forms-email {"block_id":"form-email","emailRequired":true,"label":"E-mail"} -->
<div class="uagb-forms-email-wrap">
<label>E-mail <span class="required">*</span></label>
<input type="email" name="email" required />
</div>
<!-- /wp:uagb/forms-email -->

<!-- wp:uagb/forms-phone {"block_id":"form-phone","label":"Telefone"} -->
<div class="uagb-forms-phone-wrap">
<label>Telefone</label>
<input type="tel" name="phone" />
</div>
<!-- /wp:uagb/forms-phone -->

<!-- wp:uagb/forms-textarea {"block_id":"form-message","label":"Mensagem","textareaRequired":true} -->
<div class="uagb-forms-textarea-wrap">
<label>Mensagem <span class="required">*</span></label>
<textarea name="message" rows="5" required></textarea>
</div>
<!-- /wp:uagb/forms-textarea -->

<!-- wp:uagb/forms-submit {"block_id":"form-submit","buttonText":"Enviar Mensagem"} -->
<div class="uagb-forms-submit-wrap">
<button type="submit" class="uagb-forms-submit-button">Enviar Mensagem</button>
</div>
<!-- /wp:uagb/forms-submit -->
</form>
</div>
<!-- /wp:uagb/forms -->
</div>
<!-- /wp:column -->

<!-- wp:column {"width":"40%"} -->
<div class="wp-block-column" style="flex-basis:40%">
<!-- wp:uagb/info-box {"block_id":"contact-info"} -->
<div class="wp-block-uagb-info-box">
<h3 class="uagb-ifb-title">Informações de Contato</h3>
<div class="uagb-ifb-desc">
<p><strong>Endereço:</strong><br/>{{address}}</p>
<p><strong>Telefone:</strong><br/>{{phone}}</p>
<p><strong>E-mail:</strong><br/>{{email}}</p>
<p><strong>Horário:</strong><br/>{{business_hours}}</p>
</div>
</div>
<!-- /wp:uagb/info-box -->

<!-- wp:uagb/google-map {"block_id":"contact-map","address":"{{address}}","zoom":15,"height":300} -->
<div class="wp-block-uagb-google-map">
<iframe src="https://maps.google.com/maps?q={{address_encoded}}&z=15&output=embed" width="100%" height="300"></iframe>
</div>
<!-- /wp:uagb/google-map -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</section>
<!-- /wp:uagb/section -->"""
            },
            {
                "variant": "with_map",
                "name": "Contato com Mapa Grande",
                "content": """
<!-- wp:uagb/section {"block_id":"contact-map-section","contentWidth":"full_width"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/google-map {"block_id":"full-map","address":"{{address}}","zoom":15,"height":400} -->
<div class="wp-block-uagb-google-map">
<iframe src="https://maps.google.com/maps?q={{address_encoded}}&z=15&output=embed" width="100%" height="400"></iframe>
</div>
<!-- /wp:uagb/google-map -->

<!-- wp:uagb/container {"block_id":"contact-overlay","contentWidth":"content"} -->
<div class="wp-block-uagb-container">
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/info-box {"block_id":"location-box","icon":"map-marker","headingTag":"h3"} -->
<div class="wp-block-uagb-info-box">
<h3>Localização</h3>
<p>{{address}}</p>
</div>
<!-- /wp:uagb/info-box -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/info-box {"block_id":"phone-box","icon":"phone","headingTag":"h3"} -->
<div class="wp-block-uagb-info-box">
<h3>Telefone</h3>
<p>{{phone}}</p>
</div>
<!-- /wp:uagb/info-box -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:uagb/info-box {"block_id":"hours-box","icon":"clock","headingTag":"h3"} -->
<div class="wp-block-uagb-info-box">
<h3>Horário</h3>
<p>{{business_hours}}</p>
</div>
<!-- /wp:uagb/info-box -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</div>
<!-- /wp:uagb/container -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_cta_patterns(self) -> List[Dict]:
        """Patterns para Call-to-Action"""
        return [
            {
                "variant": "centered",
                "name": "CTA Centralizado",
                "content": """
<!-- wp:uagb/section {"block_id":"cta-section","backgroundType":"gradient","gradientColor1":"#3b82f6","gradientColor2":"#8b5cf6"} -->
<section class="wp-block-uagb-section">
<div class="uagb-section__inner-wrap">
<!-- wp:uagb/advanced-heading {"block_id":"cta-heading","headingTag":"h2","headingAlign":"center","headingColor":"#ffffff"} -->
<h2 class="wp-block-uagb-advanced-heading" style="color:#ffffff">{{cta_headline}}</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:paragraph {"align":"center","style":{"color":{"text":"#ffffff"}}} -->
<p class="has-text-align-center has-text-color" style="color:#ffffff">{{cta_description}}</p>
<!-- /wp:paragraph -->

<!-- wp:uagb/buttons {"block_id":"cta-buttons","align":"center"} -->
<div class="wp-block-uagb-buttons uagb-buttons__outer-wrap">
<a class="uagb-button__link uagb-button__size-large" href="#contato" style="background-color:#ffffff;color:#3b82f6">{{cta_button_text}}</a>
</div>
<!-- /wp:uagb/buttons -->
</div>
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_team_patterns(self) -> List[Dict]:
        """Patterns para Equipe"""
        return [
            {
                "variant": "grid",
                "name": "Grid de Equipe",
                "content": """
<!-- wp:uagb/section {"block_id":"team-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"team-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Nossa Equipe</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/team {"block_id":"team-grid","columns":3} -->
<div class="wp-block-uagb-team">
<!-- wp:uagb/team-member {"block_id":"member-1"} -->
<div class="uagb-team-member">
<figure class="uagb-team__image-wrap">
<img src="{{team_member_1_photo}}" alt="{{team_member_1_name}}" />
</figure>
<h3 class="uagb-team__name">{{team_member_1_name}}</h3>
<div class="uagb-team__designation">{{team_member_1_role}}</div>
<div class="uagb-team__description">{{team_member_1_bio}}</div>
</div>
<!-- /wp:uagb/team-member -->

<!-- wp:uagb/team-member {"block_id":"member-2"} -->
<div class="uagb-team-member">
<figure class="uagb-team__image-wrap">
<img src="{{team_member_2_photo}}" alt="{{team_member_2_name}}" />
</figure>
<h3 class="uagb-team__name">{{team_member_2_name}}</h3>
<div class="uagb-team__designation">{{team_member_2_role}}</div>
<div class="uagb-team__description">{{team_member_2_bio}}</div>
</div>
<!-- /wp:uagb/team-member -->

<!-- wp:uagb/team-member {"block_id":"member-3"} -->
<div class="uagb-team-member">
<figure class="uagb-team__image-wrap">
<img src="{{team_member_3_photo}}" alt="{{team_member_3_name}}" />
</figure>
<h3 class="uagb-team__name">{{team_member_3_name}}</h3>
<div class="uagb-team__designation">{{team_member_3_role}}</div>
<div class="uagb-team__description">{{team_member_3_bio}}</div>
</div>
<!-- /wp:uagb/team-member -->
</div>
<!-- /wp:uagb/team -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_portfolio_patterns(self) -> List[Dict]:
        """Patterns para Portfólio"""
        return [
            {
                "variant": "grid",
                "name": "Grid de Portfólio",
                "content": """
<!-- wp:uagb/section {"block_id":"portfolio-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"portfolio-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Nossos Trabalhos</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/post-masonry {"block_id":"portfolio-masonry","postsToShow":6,"categories":"portfolio","displayPostImage":true,"displayPostExcerpt":false} -->
<div class="wp-block-uagb-post-masonry">
<!-- Portfolio items will be dynamically loaded -->
</div>
<!-- /wp:uagb/post-masonry -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_stats_patterns(self) -> List[Dict]:
        """Patterns para Estatísticas"""
        return [
            {
                "variant": "counters",
                "name": "Contadores Animados",
                "content": """
<!-- wp:uagb/section {"block_id":"stats-section","backgroundType":"color","backgroundColor":"#f8f9fa"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/counter {"block_id":"stats-counters","columns":4} -->
<div class="wp-block-uagb-counter">
<div class="uagb-counter-item">
<span class="uagb-counter-number" data-target="{{stat_1_number}}">{{stat_1_number}}</span>
<span class="uagb-counter-title">{{stat_1_label}}</span>
</div>
<div class="uagb-counter-item">
<span class="uagb-counter-number" data-target="{{stat_2_number}}">{{stat_2_number}}</span>
<span class="uagb-counter-title">{{stat_2_label}}</span>
</div>
<div class="uagb-counter-item">
<span class="uagb-counter-number" data-target="{{stat_3_number}}">{{stat_3_number}}</span>
<span class="uagb-counter-title">{{stat_3_label}}</span>
</div>
<div class="uagb-counter-item">
<span class="uagb-counter-number" data-target="{{stat_4_number}}">{{stat_4_number}}</span>
<span class="uagb-counter-title">{{stat_4_label}}</span>
</div>
</div>
<!-- /wp:uagb/counter -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_gallery_patterns(self) -> List[Dict]:
        """Patterns para Galeria"""
        return [
            {
                "variant": "masonry",
                "name": "Galeria Masonry",
                "content": """
<!-- wp:uagb/section {"block_id":"gallery-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"gallery-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Galeria</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:gallery {"columns":3,"imageCrop":false,"sizeSlug":"large","linkTo":"media"} -->
<figure class="wp-block-gallery has-nested-images columns-3">
<figure class="wp-block-image size-large">
<img src="{{gallery_image_1}}" alt="{{gallery_alt_1}}" />
</figure>
<figure class="wp-block-image size-large">
<img src="{{gallery_image_2}}" alt="{{gallery_alt_2}}" />
</figure>
<figure class="wp-block-image size-large">
<img src="{{gallery_image_3}}" alt="{{gallery_alt_3}}" />
</figure>
<figure class="wp-block-image size-large">
<img src="{{gallery_image_4}}" alt="{{gallery_alt_4}}" />
</figure>
<figure class="wp-block-image size-large">
<img src="{{gallery_image_5}}" alt="{{gallery_alt_5}}" />
</figure>
<figure class="wp-block-image size-large">
<img src="{{gallery_image_6}}" alt="{{gallery_alt_6}}" />
</figure>
</figure>
<!-- /wp:gallery -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_faq_patterns(self) -> List[Dict]:
        """Patterns para FAQ"""
        return [
            {
                "variant": "accordion",
                "name": "FAQ Accordion",
                "content": """
<!-- wp:uagb/section {"block_id":"faq-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"faq-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Perguntas Frequentes</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/faq {"block_id":"faq-accordion","schema":true} -->
<div class="wp-block-uagb-faq">
<!-- wp:uagb/faq-child {"block_id":"faq-1"} -->
<div class="wp-block-uagb-faq-child">
<div class="uagb-faq-question">
<span class="uagb-faq-question-label">{{faq_1_question}}</span>
</div>
<div class="uagb-faq-content">
<p>{{faq_1_answer}}</p>
</div>
</div>
<!-- /wp:uagb/faq-child -->

<!-- wp:uagb/faq-child {"block_id":"faq-2"} -->
<div class="wp-block-uagb-faq-child">
<div class="uagb-faq-question">
<span class="uagb-faq-question-label">{{faq_2_question}}</span>
</div>
<div class="uagb-faq-content">
<p>{{faq_2_answer}}</p>
</div>
</div>
<!-- /wp:uagb/faq-child -->

<!-- wp:uagb/faq-child {"block_id":"faq-3"} -->
<div class="wp-block-uagb-faq-child">
<div class="uagb-faq-question">
<span class="uagb-faq-question-label">{{faq_3_question}}</span>
</div>
<div class="uagb-faq-content">
<p>{{faq_3_answer}}</p>
</div>
</div>
<!-- /wp:uagb/faq-child -->
</div>
<!-- /wp:uagb/faq -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_blog_patterns(self) -> List[Dict]:
        """Patterns para Blog"""
        return [
            {
                "variant": "recent_posts",
                "name": "Posts Recentes",
                "content": """
<!-- wp:uagb/section {"block_id":"blog-section"} -->
<section class="wp-block-uagb-section">
<!-- wp:uagb/advanced-heading {"block_id":"blog-heading","headingTag":"h2","headingAlign":"center"} -->
<h2 class="wp-block-uagb-advanced-heading">Últimas do Blog</h2>
<!-- /wp:uagb/advanced-heading -->

<!-- wp:uagb/post-grid {"block_id":"blog-grid","postsToShow":3,"columns":3,"displayPostImage":true,"displayPostAuthor":false,"displayPostDate":true,"displayPostExcerpt":true,"excerptLength":20} -->
<div class="wp-block-uagb-post-grid">
<!-- Posts will be dynamically loaded -->
</div>
<!-- /wp:uagb/post-grid -->

<!-- wp:uagb/buttons {"block_id":"blog-more","align":"center"} -->
<div class="wp-block-uagb-buttons">
<a class="uagb-button__link" href="/blog">Ver Todos os Posts</a>
</div>
<!-- /wp:uagb/buttons -->
</section>
<!-- /wp:uagb/section -->"""
            }
        ]
    
    def _get_footer_patterns(self) -> List[Dict]:
        """Patterns para Footer/Rodapé"""
        return [
            {
                "variant": "complete",
                "name": "Rodapé Completo",
                "content": """
<!-- wp:uagb/section {"block_id":"footer-section","contentWidth":"full_width","backgroundType":"color","backgroundColor":"#1e293b"} -->
<footer class="wp-block-uagb-section">
<div class="uagb-section__inner-wrap">
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":3,"style":{"color":{"text":"#ffffff"}}} -->
<h3 class="has-text-color" style="color:#ffffff">{{business_name}}</h3>
<!-- /wp:heading -->
<!-- wp:paragraph {"style":{"color":{"text":"#94a3b8"}}} -->
<p class="has-text-color" style="color:#94a3b8">{{footer_about}}</p>
<!-- /wp:paragraph -->
<!-- wp:social-links {"className":"is-style-logos-only"} -->
<ul class="wp-block-social-links is-style-logos-only">
<li class="wp-social-link wp-social-link-facebook"><a href="{{facebook_url}}"><span class="wp-block-social-link-label">Facebook</span></a></li>
<li class="wp-social-link wp-social-link-instagram"><a href="{{instagram_url}}"><span class="wp-block-social-link-label">Instagram</span></a></li>
<li class="wp-social-link wp-social-link-whatsapp"><a href="https://wa.me/{{whatsapp_number}}"><span class="wp-block-social-link-label">WhatsApp</span></a></li>
</ul>
<!-- /wp:social-links -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":4,"style":{"color":{"text":"#ffffff"}}} -->
<h4 class="has-text-color" style="color:#ffffff">Links Rápidos</h4>
<!-- /wp:heading -->
<!-- wp:list {"style":{"color":{"text":"#94a3b8"}}} -->
<ul class="has-text-color" style="color:#94a3b8">
<li><a href="/sobre" style="color:#94a3b8">Sobre Nós</a></li>
<li><a href="/servicos" style="color:#94a3b8">Serviços</a></li>
<li><a href="/portfolio" style="color:#94a3b8">Portfólio</a></li>
<li><a href="/contato" style="color:#94a3b8">Contato</a></li>
</ul>
<!-- /wp:list -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":4,"style":{"color":{"text":"#ffffff"}}} -->
<h4 class="has-text-color" style="color:#ffffff">Contato</h4>
<!-- /wp:heading -->
<!-- wp:paragraph {"style":{"color":{"text":"#94a3b8"}}} -->
<p class="has-text-color" style="color:#94a3b8">
<strong>Endereço:</strong><br/>{{address}}<br/><br/>
<strong>Telefone:</strong><br/>{{phone}}<br/><br/>
<strong>E-mail:</strong><br/>{{email}}
</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:heading {"level":4,"style":{"color":{"text":"#ffffff"}}} -->
<h4 class="has-text-color" style="color:#ffffff">Newsletter</h4>
<!-- /wp:heading -->
<!-- wp:paragraph {"style":{"color":{"text":"#94a3b8"}}} -->
<p class="has-text-color" style="color:#94a3b8">Receba nossas novidades</p>
<!-- /wp:paragraph -->
<!-- wp:uagb/forms {"block_id":"newsletter-form"} -->
<form class="wp-block-uagb-forms">
<input type="email" placeholder="Seu e-mail" required />
<button type="submit">Inscrever</button>
</form>
<!-- /wp:uagb/forms -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->

<!-- wp:separator {"style":{"color":{"background":"#334155"}}} -->
<hr class="wp-block-separator has-text-color has-background" style="background-color:#334155;color:#334155"/>
<!-- /wp:separator -->

<!-- wp:paragraph {"align":"center","style":{"color":{"text":"#94a3b8"}}} -->
<p class="has-text-align-center has-text-color" style="color:#94a3b8">© {{current_year}} {{business_name}}. Todos os direitos reservados. | <a href="/privacidade" style="color:#94a3b8">Política de Privacidade</a> | <a href="/termos" style="color:#94a3b8">Termos de Uso</a></p>
<!-- /wp:paragraph -->
</div>
</footer>
<!-- /wp:uagb/section -->"""
            }
        ]

# Instância global
block_patterns_library = BlockPatternsLibrary()