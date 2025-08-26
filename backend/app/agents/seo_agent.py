"""
SEO Agent
Responsible for search engine optimization
"""

import logging
from typing import Dict, Any, List, Optional
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

class SEOAgent:
    """
    AI Agent specialized in SEO optimization
    """
    
    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider
        self.name = "SEOAgent"
        self.capabilities = [
            "generate_meta_tags",
            "optimize_headlines",
            "create_schema_markup",
            "generate_keywords",
            "optimize_urls",
            "create_sitemap",
            "analyze_content_seo",
            "generate_alt_text"
        ]
    
    async def optimize_for_seo(
        self,
        business_data: Dict[str, Any],
        content_data: Dict[str, Any],
        target_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize content for SEO
        
        Args:
            business_data: Business information
            content_data: Content to optimize
            target_keywords: Target keywords for optimization
            
        Returns:
            SEO optimized data
        """
        
        logger.info(f"Optimizing SEO for {business_data.get('business_name')}")
        
        # Generate keywords if not provided
        if not target_keywords:
            target_keywords = await self.generate_keywords(business_data)
        
        seo_data = {
            "meta_tags": await self.generate_meta_tags(business_data, content_data),
            "schema_markup": self.generate_schema_markup(business_data),
            "optimized_content": await self.optimize_content_for_keywords(content_data, target_keywords),
            "url_structure": self.optimize_url_structure(business_data),
            "internal_links": self.generate_internal_links(content_data),
            "image_optimization": await self.optimize_images(content_data),
            "local_seo": self.optimize_for_local_seo(business_data),
            "technical_seo": self.generate_technical_seo(business_data)
        }
        
        return seo_data
    
    async def generate_meta_tags(
        self,
        business_data: Dict[str, Any],
        content_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, str]]:
        """Generate meta tags for all pages"""
        
        business_name = business_data.get("business_name", "")
        description = business_data.get("description", "")
        city = business_data.get("city", "São Paulo")
        industry = business_data.get("industry", "")
        
        meta_tags = {}
        
        # Home page meta tags
        meta_tags["home"] = {
            "title": f"{business_name} | {self._get_industry_descriptor(industry)} em {city}",
            "description": self._truncate_description(
                description or f"{business_name} - Líder em {self._get_industry_descriptor(industry)} em {city}. "
                f"Qualidade, confiança e excelência em nossos serviços. Entre em contato hoje mesmo!"
            ),
            "keywords": self._generate_page_keywords(business_data, "home"),
            "og:title": f"{business_name} - {self._get_industry_descriptor(industry)}",
            "og:description": self._truncate_description(description, 200),
            "og:type": "website",
            "og:locale": "pt_BR",
            "twitter:card": "summary_large_image",
            "robots": "index, follow",
            "canonical": f"https://{self._generate_domain(business_name)}.com.br/"
        }
        
        # About page meta tags
        meta_tags["about"] = {
            "title": f"Sobre Nós | {business_name}",
            "description": f"Conheça a história do {business_name}. "
                          f"Nossa missão, valores e compromisso com a excelência em {self._get_industry_descriptor(industry)}.",
            "keywords": f"sobre {business_name}, história, missão, valores, {industry}",
            "robots": "index, follow"
        }
        
        # Services page meta tags
        meta_tags["services"] = {
            "title": f"Nossos Serviços | {business_name}",
            "description": f"Descubra todos os serviços oferecidos pelo {business_name}. "
                          f"Soluções completas em {self._get_industry_descriptor(industry)} para sua necessidade.",
            "keywords": f"serviços {business_name}, {industry}, soluções, atendimento",
            "robots": "index, follow"
        }
        
        # Contact page meta tags
        meta_tags["contact"] = {
            "title": f"Contato | {business_name}",
            "description": f"Entre em contato com o {business_name}. "
                          f"Telefone, WhatsApp, endereço e formulário de contato. Atendemos em {city} e região.",
            "keywords": f"contato {business_name}, telefone, whatsapp, endereço, {city}",
            "robots": "index, follow"
        }
        
        return meta_tags
    
    def generate_schema_markup(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schema.org structured data"""
        
        business_name = business_data.get("business_name", "")
        industry = business_data.get("industry", "")
        phone = business_data.get("phone", "")
        email = business_data.get("email", "")
        address = business_data.get("address", "")
        city = business_data.get("city", "São Paulo")
        
        # Determine business type for schema
        schema_type_map = {
            "restaurant": "Restaurant",
            "healthcare": "MedicalBusiness",
            "ecommerce": "Store",
            "services": "ProfessionalService",
            "education": "EducationalOrganization"
        }
        
        schema_type = schema_type_map.get(industry, "LocalBusiness")
        
        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": business_name,
            "description": business_data.get("description", ""),
            "url": f"https://{self._generate_domain(business_name)}.com.br",
            "telephone": phone,
            "email": email,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": address,
                "addressLocality": city,
                "addressRegion": business_data.get("state", "SP"),
                "addressCountry": "BR",
                "postalCode": business_data.get("zip_code", "")
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": self._get_city_coordinates(city)["lat"],
                "longitude": self._get_city_coordinates(city)["lng"]
            },
            "openingHoursSpecification": self._generate_opening_hours(industry),
            "priceRange": "$$",
            "image": f"https://{self._generate_domain(business_name)}.com.br/logo.png"
        }
        
        # Add industry-specific properties
        if industry == "restaurant":
            schema.update({
                "servesCuisine": "Brazilian",
                "acceptsReservations": "true",
                "menu": f"https://{self._generate_domain(business_name)}.com.br/cardapio"
            })
        elif industry == "healthcare":
            schema.update({
                "medicalSpecialty": "General Practice",
                "availableService": business_data.get("services", [])
            })
        elif industry == "ecommerce":
            schema.update({
                "paymentAccepted": ["Cash", "Credit Card", "PIX"],
                "currenciesAccepted": "BRL"
            })
        
        # Add Brazilian specific properties
        if business_data.get("cnpj"):
            schema["taxID"] = business_data["cnpj"]
        
        if business_data.get("accept_pix"):
            if "paymentAccepted" in schema:
                if "PIX" not in schema["paymentAccepted"]:
                    schema["paymentAccepted"].append("PIX")
            else:
                schema["paymentAccepted"] = ["PIX"]
        
        return schema
    
    async def generate_keywords(self, business_data: Dict[str, Any]) -> List[str]:
        """Generate relevant keywords"""
        
        business_name = business_data.get("business_name", "")
        industry = business_data.get("industry", "")
        city = business_data.get("city", "São Paulo")
        services = business_data.get("services", [])
        
        # Base keywords
        keywords = [
            business_name.lower(),
            industry,
            f"{industry} {city}",
            f"{business_name} {city}"
        ]
        
        # Industry-specific keywords
        industry_keywords = {
            "restaurant": [
                "restaurante", "comida", "almoço", "jantar", "delivery",
                "cardápio", "pratos", "gastronomia", "culinária", "chef"
            ],
            "healthcare": [
                "clínica", "médico", "saúde", "consulta", "exame",
                "tratamento", "especialista", "atendimento", "hospital", "doutor"
            ],
            "ecommerce": [
                "loja online", "comprar", "produtos", "ecommerce", "venda",
                "frete grátis", "promoção", "desconto", "entrega", "pagamento"
            ],
            "services": [
                "serviços", "atendimento", "soluções", "consultoria", "suporte",
                "profissional", "qualidade", "empresa", "negócio", "parceria"
            ],
            "education": [
                "escola", "curso", "educação", "ensino", "formação",
                "aula", "professor", "aprendizado", "certificado", "diploma"
            ]
        }
        
        keywords.extend(industry_keywords.get(industry, industry_keywords["services"]))
        
        # Add service-specific keywords
        for service in services:
            if isinstance(service, str):
                keywords.append(service.lower())
                keywords.append(f"{service.lower()} {city}")
        
        # Add location-based keywords
        keywords.extend([
            f"melhor {industry} {city}",
            f"{industry} perto de mim",
            f"{industry} {city} centro",
            f"{industry} zona sul {city}" if city == "São Paulo" else f"{industry} centro {city}"
        ])
        
        # Add Brazilian specific keywords
        if business_data.get("whatsapp"):
            keywords.extend(["whatsapp", "atendimento whatsapp"])
        
        if business_data.get("accept_pix"):
            keywords.extend(["pagamento pix", "aceita pix"])
        
        # Remove duplicates and return
        return list(set(keywords))
    
    async def optimize_content_for_keywords(
        self,
        content_data: Dict[str, Any],
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Optimize content for target keywords"""
        
        optimized = content_data.copy()
        
        # Calculate keyword density targets
        primary_keyword = keywords[0] if keywords else ""
        secondary_keywords = keywords[1:5] if len(keywords) > 1 else []
        
        # Optimization rules
        optimization_rules = {
            "keyword_density": 0.015,  # 1.5% for primary keyword
            "secondary_density": 0.005,  # 0.5% for secondary keywords
            "min_content_length": 300,
            "max_title_length": 60,
            "max_description_length": 160
        }
        
        # Apply optimizations
        for key, value in optimized.items():
            if isinstance(value, str) and len(value) > 50:
                # Ensure primary keyword appears
                if primary_keyword and primary_keyword not in value.lower():
                    value = self._insert_keyword(value, primary_keyword)
                
                # Add secondary keywords naturally
                for keyword in secondary_keywords:
                    if keyword not in value.lower():
                        value = self._insert_keyword(value, keyword, frequency=0.3)
                
                optimized[key] = value
        
        return optimized
    
    def optimize_url_structure(self, business_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate SEO-friendly URL structure"""
        
        business_name = business_data.get("business_name", "site")
        
        # Generate clean domain
        domain = self._generate_domain(business_name)
        
        url_structure = {
            "home": f"https://{domain}.com.br/",
            "about": f"https://{domain}.com.br/sobre",
            "services": f"https://{domain}.com.br/servicos",
            "contact": f"https://{domain}.com.br/contato",
            "blog": f"https://{domain}.com.br/blog",
            "products": f"https://{domain}.com.br/produtos",
            "testimonials": f"https://{domain}.com.br/depoimentos",
            "faq": f"https://{domain}.com.br/perguntas-frequentes",
            "privacy": f"https://{domain}.com.br/politica-privacidade",
            "terms": f"https://{domain}.com.br/termos-uso"
        }
        
        return url_structure
    
    def generate_internal_links(self, content_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate internal linking structure"""
        
        internal_links = [
            {"from": "home", "to": "about", "anchor": "Conheça nossa história"},
            {"from": "home", "to": "services", "anchor": "Nossos serviços"},
            {"from": "about", "to": "services", "anchor": "Veja o que oferecemos"},
            {"from": "services", "to": "contact", "anchor": "Solicite um orçamento"},
            {"from": "blog", "to": "services", "anchor": "Conheça nossos serviços"},
            {"from": "any", "to": "contact", "anchor": "Entre em contato"}
        ]
        
        return internal_links
    
    async def optimize_images(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize images for SEO"""
        
        image_optimizations = {}
        
        # Standard image optimization rules
        standard_images = {
            "hero": {
                "alt": "Banner principal - {business_name}",
                "title": "{business_name} - {industry}",
                "filename": "hero-banner-{business_name}.jpg",
                "max_size_kb": 200
            },
            "about": {
                "alt": "Sobre {business_name}",
                "title": "Conheça o {business_name}",
                "filename": "sobre-{business_name}.jpg",
                "max_size_kb": 150
            },
            "services": {
                "alt": "Serviços {business_name}",
                "title": "Nossos serviços",
                "filename": "servicos-{business_name}.jpg",
                "max_size_kb": 100
            },
            "team": {
                "alt": "Equipe {business_name}",
                "title": "Nossa equipe",
                "filename": "equipe-{business_name}.jpg",
                "max_size_kb": 150
            }
        }
        
        for image_type, optimization in standard_images.items():
            image_optimizations[image_type] = optimization
        
        return image_optimizations
    
    def optimize_for_local_seo(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize for local SEO"""
        
        city = business_data.get("city", "São Paulo")
        state = business_data.get("state", "SP")
        business_name = business_data.get("business_name", "")
        industry = business_data.get("industry", "")
        
        local_seo = {
            "google_my_business": {
                "name": business_name,
                "category": self._get_gmb_category(industry),
                "description": business_data.get("description", ""),
                "service_area": [city, f"{city} e região"],
                "attributes": self._get_gmb_attributes(business_data)
            },
            "local_citations": [
                "Google Meu Negócio",
                "Bing Places",
                "Apple Maps",
                "Facebook Business",
                "Instagram Business",
                "Reclame Aqui",
                "TripAdvisor" if industry == "restaurant" else None,
                "Doctoralia" if industry == "healthcare" else None
            ],
            "local_keywords": [
                f"{industry} em {city}",
                f"{industry} {city} {state}",
                f"melhor {industry} {city}",
                f"{industry} perto de mim",
                f"{industry} {city} centro",
                f"{business_name} {city}"
            ],
            "local_content": {
                "city_pages": [city] + self._get_nearby_cities(city),
                "neighborhood_pages": self._get_neighborhoods(city),
                "local_guides": [
                    f"Guia completo de {industry} em {city}",
                    f"Como escolher o melhor {industry} em {city}",
                    f"Top 10 {industry} em {city}"
                ]
            }
        }
        
        return local_seo
    
    def generate_technical_seo(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical SEO configurations"""
        
        domain = self._generate_domain(business_data.get("business_name", "site"))
        
        technical_seo = {
            "robots_txt": self._generate_robots_txt(domain),
            "sitemap_xml": self._generate_sitemap_structure(),
            "htaccess": self._generate_htaccess(),
            "page_speed": {
                "enable_compression": True,
                "enable_browser_caching": True,
                "minify_css": True,
                "minify_js": True,
                "optimize_images": True,
                "lazy_load_images": True,
                "use_cdn": True
            },
            "mobile_optimization": {
                "responsive_design": True,
                "viewport_meta": "width=device-width, initial-scale=1.0",
                "touch_friendly": True,
                "font_size_readable": True
            },
            "security": {
                "https_enabled": True,
                "ssl_certificate": True,
                "hsts_header": True,
                "secure_headers": True
            },
            "crawlability": {
                "xml_sitemap": True,
                "clean_urls": True,
                "breadcrumbs": True,
                "pagination_tags": True,
                "canonical_urls": True
            }
        }
        
        return technical_seo
    
    def _get_industry_descriptor(self, industry: str) -> str:
        """Get industry descriptor in Portuguese"""
        
        descriptors = {
            "restaurant": "Restaurante e Gastronomia",
            "healthcare": "Saúde e Bem-estar",
            "ecommerce": "Loja Online",
            "services": "Serviços Profissionais",
            "education": "Educação e Ensino"
        }
        
        return descriptors.get(industry, "Serviços")
    
    def _truncate_description(self, description: str, max_length: int = 160) -> str:
        """Truncate description to max length"""
        
        if len(description) <= max_length:
            return description
        
        return description[:max_length - 3] + "..."
    
    def _generate_domain(self, business_name: str) -> str:
        """Generate clean domain from business name"""
        
        # Remove special characters and spaces
        domain = re.sub(r'[^a-zA-Z0-9]', '', business_name.lower())
        
        # Limit length
        if len(domain) > 20:
            domain = domain[:20]
        
        return domain or "site"
    
    def _generate_page_keywords(self, business_data: Dict[str, Any], page: str) -> str:
        """Generate keywords for specific page"""
        
        business_name = business_data.get("business_name", "")
        industry = business_data.get("industry", "")
        city = business_data.get("city", "")
        
        base_keywords = [business_name, industry, city]
        
        page_specific = {
            "home": base_keywords + ["principal", "início"],
            "about": base_keywords + ["sobre", "história", "missão"],
            "services": base_keywords + ["serviços", "soluções", "atendimento"],
            "contact": base_keywords + ["contato", "telefone", "endereço"]
        }
        
        keywords = page_specific.get(page, base_keywords)
        return ", ".join(keywords)
    
    def _get_city_coordinates(self, city: str) -> Dict[str, float]:
        """Get coordinates for Brazilian cities"""
        
        coordinates = {
            "São Paulo": {"lat": -23.5505, "lng": -46.6333},
            "Rio de Janeiro": {"lat": -22.9068, "lng": -43.1729},
            "Belo Horizonte": {"lat": -19.9167, "lng": -43.9345},
            "Brasília": {"lat": -15.7975, "lng": -47.8919},
            "Salvador": {"lat": -12.9714, "lng": -38.5014},
            "Fortaleza": {"lat": -3.7172, "lng": -38.5434},
            "Curitiba": {"lat": -25.4284, "lng": -49.2733},
            "Recife": {"lat": -8.0476, "lng": -34.8770},
            "Porto Alegre": {"lat": -30.0346, "lng": -51.2177}
        }
        
        return coordinates.get(city, coordinates["São Paulo"])
    
    def _generate_opening_hours(self, industry: str) -> List[Dict[str, Any]]:
        """Generate opening hours specification"""
        
        default_hours = {
            "restaurant": {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                "opens": "11:00",
                "closes": "23:00"
            },
            "healthcare": {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "08:00",
                "closes": "18:00"
            },
            "ecommerce": {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "opens": "00:00",
                "closes": "23:59"
            },
            "services": {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00",
                "closes": "18:00"
            },
            "education": {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "07:00",
                "closes": "22:00"
            }
        }
        
        hours = default_hours.get(industry, default_hours["services"])
        
        return [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": hours["days"],
            "opens": hours["opens"],
            "closes": hours["closes"]
        }]
    
    def _get_gmb_category(self, industry: str) -> str:
        """Get Google My Business category"""
        
        categories = {
            "restaurant": "Restaurante",
            "healthcare": "Clínica médica",
            "ecommerce": "Loja",
            "services": "Empresa",
            "education": "Escola"
        }
        
        return categories.get(industry, "Empresa")
    
    def _get_gmb_attributes(self, business_data: Dict[str, Any]) -> List[str]:
        """Get Google My Business attributes"""
        
        attributes = []
        
        if business_data.get("whatsapp"):
            attributes.append("Atendimento por WhatsApp")
        
        if business_data.get("accept_pix"):
            attributes.append("Aceita PIX")
        
        if business_data.get("delivery"):
            attributes.append("Entrega disponível")
        
        return attributes
    
    def _get_nearby_cities(self, city: str) -> List[str]:
        """Get nearby cities for local SEO"""
        
        nearby = {
            "São Paulo": ["Guarulhos", "São Bernardo do Campo", "Santo André", "Osasco"],
            "Rio de Janeiro": ["Niterói", "São Gonçalo", "Duque de Caxias", "Nova Iguaçu"],
            "Belo Horizonte": ["Contagem", "Betim", "Nova Lima", "Ribeirão das Neves"]
        }
        
        return nearby.get(city, [])
    
    def _get_neighborhoods(self, city: str) -> List[str]:
        """Get neighborhoods for local pages"""
        
        neighborhoods = {
            "São Paulo": ["Centro", "Jardins", "Vila Mariana", "Pinheiros", "Moema"],
            "Rio de Janeiro": ["Copacabana", "Ipanema", "Leblon", "Botafogo", "Centro"],
            "Belo Horizonte": ["Savassi", "Funcionários", "Lourdes", "Centro", "Pampulha"]
        }
        
        return neighborhoods.get(city, ["Centro"])
    
    def _insert_keyword(self, text: str, keyword: str, frequency: float = 1.0) -> str:
        """Insert keyword naturally into text"""
        
        # Simple implementation - in production use NLP
        if frequency > 0.5 and keyword not in text.lower():
            # Add keyword to beginning or end
            if len(text) > 100:
                text = f"{text} Nosso foco em {keyword} garante excelência."
        
        return text
    
    def _generate_robots_txt(self, domain: str) -> str:
        """Generate robots.txt content"""
        
        return f"""# Robots.txt for {domain}
User-agent: *
Allow: /
Disallow: /wp-admin/
Disallow: /wp-includes/
Disallow: /?s=
Disallow: /search/
Sitemap: https://{domain}.com.br/sitemap.xml
"""
    
    def _generate_sitemap_structure(self) -> List[str]:
        """Generate sitemap structure"""
        
        return [
            "/",
            "/sobre",
            "/servicos",
            "/contato",
            "/blog",
            "/depoimentos",
            "/perguntas-frequentes",
            "/politica-privacidade",
            "/termos-uso"
        ]
    
    def _generate_htaccess(self) -> str:
        """Generate .htaccess configuration"""
        
        return """# KenzySites .htaccess
RewriteEngine On

# Force HTTPS
RewriteCond %{HTTPS} !=on
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

# Remove www
RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]
RewriteRule ^(.*)$ https://%1/$1 [R=301,L]

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>

# Browser caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
"""