"""
Landing Page ACF Field Groups - Grupos de campos específicos para landing pages
Convertidos a partir de templates Elementor para máxima flexibilidade
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from .template_models import ACFField, ACFFieldGroup, ACFFieldType


class LandingPageType(str, Enum):
    """Tipos de landing pages por objetivo"""
    LEAD_GENERATION = "lead_generation"
    PRODUCT_LAUNCH = "product_launch"
    EVENT_PROMOTION = "event_promotion"
    SERVICE_SHOWCASE = "service_showcase"
    E_COMMERCE = "e_commerce"
    WEBINAR = "webinar"
    COMING_SOON = "coming_soon"
    THANK_YOU = "thank_you"
    DOWNLOAD = "download"
    NEWSLETTER = "newsletter"


class LandingPageIndustry(str, Enum):
    """Indústrias específicas para landing pages"""
    RESTAURANTE = "restaurante"
    DENTISTA = "dentista"
    ADVOGADO = "advogado"
    CLINICA_ESTETICA = "clinica_estetica"
    ACADEMIA = "academia"
    IMOBILIARIA = "imobiliaria"
    CONSULTORIA = "consultoria"
    SAAS = "saas"
    E_COMMERCE = "e_commerce"
    EDUCACAO = "educacao"


def create_hero_section_fields() -> ACFFieldGroup:
    """Grupo de campos para seção Hero/Banner principal"""
    
    fields = [
        ACFField(
            key="hero_headline",
            name="hero_headline",
            label="Título Principal",
            type=ACFFieldType.TEXT,
            instructions="Título principal que aparece na seção hero",
            required=True,
            placeholder="Ex: Transforme Seu Negócio Com IA",
            character_limit=80
        ),
        ACFField(
            key="hero_subheadline",
            name="hero_subheadline", 
            label="Subtítulo",
            type=ACFFieldType.TEXTAREA,
            instructions="Descrição complementar do título principal",
            required=True,
            placeholder="Ex: Automatize processos e aumente vendas com nossa plataforma",
            rows=3,
            character_limit=200
        ),
        ACFField(
            key="hero_cta_text",
            name="hero_cta_text",
            label="Texto do Botão Principal",
            type=ACFFieldType.TEXT,
            instructions="Texto do call-to-action principal",
            required=True,
            placeholder="Ex: Começar Agora Grátis",
            character_limit=30
        ),
        ACFField(
            key="hero_cta_link",
            name="hero_cta_link",
            label="Link do Botão Principal",
            type=ACFFieldType.URL,
            instructions="URL para onde o botão principal direciona",
            required=True,
            placeholder="https://exemplo.com/cadastro"
        ),
        ACFField(
            key="hero_background_image",
            name="hero_background_image",
            label="Imagem de Fundo",
            type=ACFFieldType.IMAGE,
            instructions="Imagem de fundo da seção hero (1920x1080px recomendado)",
            required=False,
            return_format="url",
            preview_size="medium"
        ),
        ACFField(
            key="hero_video_url",
            name="hero_video_url",
            label="URL do Vídeo",
            type=ACFFieldType.URL,
            instructions="URL do vídeo explicativo (YouTube/Vimeo)",
            required=False,
            placeholder="https://youtube.com/watch?v=..."
        ),
        ACFField(
            key="hero_trust_badges",
            name="hero_trust_badges",
            label="Selos de Confiança",
            type=ACFFieldType.REPEATER,
            instructions="Logos/selos para gerar confiança",
            required=False,
            min=0,
            max=5,
            layout="table",
            sub_fields=[
                ACFField(
                    key="badge_image",
                    name="badge_image",
                    label="Imagem do Selo",
                    type=ACFFieldType.IMAGE,
                    return_format="url"
                ),
                ACFField(
                    key="badge_text", 
                    name="badge_text",
                    label="Texto do Selo",
                    type=ACFFieldType.TEXT,
                    placeholder="Ex: Certificado ISO"
                )
            ]
        )
    ]
    
    return ACFFieldGroup(
        key="group_hero_section",
        title="Seção Hero/Banner",
        fields=fields,
        location=[
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            }
        ],
        menu_order=0,
        position="normal",
        style="default",
        label_placement="top",
        instruction_placement="label"
    )


def create_features_section_fields() -> ACFFieldGroup:
    """Grupo de campos para seção de funcionalidades/benefícios"""
    
    fields = [
        ACFField(
            key="features_title",
            name="features_title",
            label="Título da Seção",
            type=ACFFieldType.TEXT,
            instructions="Título da seção de funcionalidades",
            required=True,
            placeholder="Ex: Por Que Escolher Nossa Solução?",
            character_limit=60
        ),
        ACFField(
            key="features_subtitle",
            name="features_subtitle",
            label="Subtítulo",
            type=ACFFieldType.TEXTAREA,
            instructions="Descrição da seção de funcionalidades",
            required=False,
            rows=2,
            character_limit=150
        ),
        ACFField(
            key="features_list",
            name="features_list",
            label="Lista de Funcionalidades",
            type=ACFFieldType.REPEATER,
            instructions="Adicione as principais funcionalidades/benefícios",
            required=True,
            min=3,
            max=6,
            layout="row",
            sub_fields=[
                ACFField(
                    key="feature_icon",
                    name="feature_icon",
                    label="Ícone",
                    type=ACFFieldType.IMAGE,
                    instructions="Ícone da funcionalidade (64x64px)",
                    return_format="url",
                    preview_size="thumbnail"
                ),
                ACFField(
                    key="feature_title",
                    name="feature_title", 
                    label="Título",
                    type=ACFFieldType.TEXT,
                    instructions="Nome da funcionalidade",
                    required=True,
                    placeholder="Ex: Automação Inteligente",
                    character_limit=40
                ),
                ACFField(
                    key="feature_description",
                    name="feature_description",
                    label="Descrição",
                    type=ACFFieldType.TEXTAREA,
                    instructions="Descrição detalhada da funcionalidade",
                    required=True,
                    rows=3,
                    character_limit=120
                ),
                ACFField(
                    key="feature_link",
                    name="feature_link",
                    label="Link (Opcional)",
                    type=ACFFieldType.URL,
                    instructions="Link para mais detalhes",
                    required=False
                )
            ]
        ),
        ACFField(
            key="features_layout",
            name="features_layout",
            label="Layout",
            type=ACFFieldType.SELECT,
            instructions="Como exibir as funcionalidades",
            choices={
                "grid_3_cols": "Grade 3 Colunas",
                "grid_2_cols": "Grade 2 Colunas", 
                "list_vertical": "Lista Vertical",
                "carousel": "Carrossel"
            },
            default_value="grid_3_cols",
            required=True
        )
    ]
    
    return ACFFieldGroup(
        key="group_features_section",
        title="Seção de Funcionalidades",
        fields=fields,
        location=[
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            }
        ],
        menu_order=1,
        position="normal"
    )


def create_testimonials_section_fields() -> ACFFieldGroup:
    """Grupo de campos para depoimentos"""
    
    fields = [
        ACFField(
            key="testimonials_title",
            name="testimonials_title",
            label="Título da Seção",
            type=ACFFieldType.TEXT,
            instructions="Título da seção de depoimentos",
            required=True,
            placeholder="Ex: O Que Nossos Clientes Dizem",
            character_limit=60
        ),
        ACFField(
            key="testimonials_list",
            name="testimonials_list",
            label="Depoimentos",
            type=ACFFieldType.REPEATER,
            instructions="Adicione depoimentos de clientes",
            required=True,
            min=2,
            max=10,
            layout="row",
            sub_fields=[
                ACFField(
                    key="testimonial_content",
                    name="testimonial_content",
                    label="Depoimento",
                    type=ACFFieldType.TEXTAREA,
                    instructions="Texto do depoimento",
                    required=True,
                    rows=4,
                    character_limit=300
                ),
                ACFField(
                    key="testimonial_author",
                    name="testimonial_author",
                    label="Nome do Cliente",
                    type=ACFFieldType.TEXT,
                    instructions="Nome completo do cliente",
                    required=True,
                    character_limit=50
                ),
                ACFField(
                    key="testimonial_role",
                    name="testimonial_role",
                    label="Cargo/Empresa",
                    type=ACFFieldType.TEXT,
                    instructions="Cargo e empresa do cliente",
                    required=True,
                    placeholder="Ex: CEO, Empresa XYZ",
                    character_limit=80
                ),
                ACFField(
                    key="testimonial_avatar",
                    name="testimonial_avatar",
                    label="Foto do Cliente",
                    type=ACFFieldType.IMAGE,
                    instructions="Foto do cliente (200x200px)",
                    required=False,
                    return_format="url",
                    preview_size="thumbnail"
                ),
                ACFField(
                    key="testimonial_rating",
                    name="testimonial_rating",
                    label="Avaliação",
                    type=ACFFieldType.NUMBER,
                    instructions="Nota de 1 a 5 estrelas",
                    required=True,
                    min=1,
                    max=5,
                    default_value=5
                ),
                ACFField(
                    key="testimonial_company_logo",
                    name="testimonial_company_logo",
                    label="Logo da Empresa",
                    type=ACFFieldType.IMAGE,
                    instructions="Logo da empresa do cliente",
                    required=False,
                    return_format="url"
                )
            ]
        ),
        ACFField(
            key="testimonials_layout",
            name="testimonials_layout",
            label="Layout",
            type=ACFFieldType.SELECT,
            instructions="Como exibir os depoimentos",
            choices={
                "carousel": "Carrossel",
                "grid": "Grade",
                "list": "Lista",
                "featured": "Depoimento em Destaque"
            },
            default_value="carousel",
            required=True
        )
    ]
    
    return ACFFieldGroup(
        key="group_testimonials_section",
        title="Seção de Depoimentos",
        fields=fields,
        location=[
            {
                "param": "post_type", 
                "operator": "==",
                "value": "page"
            }
        ],
        menu_order=2,
        position="normal"
    )


def create_cta_section_fields() -> ACFFieldGroup:
    """Grupo de campos para Call-to-Action final"""
    
    fields = [
        ACFField(
            key="cta_headline",
            name="cta_headline",
            label="Título do CTA",
            type=ACFFieldType.TEXT,
            instructions="Título chamativo para ação",
            required=True,
            placeholder="Ex: Pronto Para Começar?",
            character_limit=50
        ),
        ACFField(
            key="cta_description",
            name="cta_description", 
            label="Descrição",
            type=ACFFieldType.TEXTAREA,
            instructions="Texto complementar do CTA",
            required=True,
            rows=2,
            character_limit=150
        ),
        ACFField(
            key="cta_button_text",
            name="cta_button_text",
            label="Texto do Botão",
            type=ACFFieldType.TEXT,
            instructions="Texto do botão principal",
            required=True,
            placeholder="Ex: Começar Agora",
            character_limit=25
        ),
        ACFField(
            key="cta_button_link",
            name="cta_button_link",
            label="Link do Botão",
            type=ACFFieldType.URL,
            instructions="URL de destino do botão",
            required=True
        ),
        ACFField(
            key="cta_secondary_text",
            name="cta_secondary_text",
            label="Texto Secundário",
            type=ACFFieldType.TEXT,
            instructions="Texto complementar (ex: sem cartão de crédito)",
            required=False,
            placeholder="Ex: Teste grátis por 14 dias",
            character_limit=40
        ),
        ACFField(
            key="cta_urgency_text",
            name="cta_urgency_text",
            label="Texto de Urgência",
            type=ACFFieldType.TEXT,
            instructions="Texto para criar urgência",
            required=False,
            placeholder="Ex: Oferta por tempo limitado!",
            character_limit=50
        ),
        ACFField(
            key="cta_background_color",
            name="cta_background_color",
            label="Cor de Fundo",
            type=ACFFieldType.COLOR_PICKER,
            instructions="Cor de fundo da seção CTA",
            required=False,
            default_value="#007cba"
        ),
        ACFField(
            key="cta_text_color",
            name="cta_text_color",
            label="Cor do Texto",
            type=ACFFieldType.COLOR_PICKER,
            instructions="Cor do texto da seção CTA",
            required=False,
            default_value="#ffffff"
        )
    ]
    
    return ACFFieldGroup(
        key="group_cta_section",
        title="Seção Call-to-Action",
        fields=fields,
        location=[
            {
                "param": "post_type",
                "operator": "==", 
                "value": "page"
            }
        ],
        menu_order=3,
        position="normal"
    )


def create_contact_form_fields() -> ACFFieldGroup:
    """Grupo de campos para formulário de contato"""
    
    fields = [
        ACFField(
            key="form_title",
            name="form_title",
            label="Título do Formulário",
            type=ACFFieldType.TEXT,
            instructions="Título acima do formulário",
            required=True,
            placeholder="Ex: Entre em Contato",
            character_limit=40
        ),
        ACFField(
            key="form_description",
            name="form_description",
            label="Descrição",
            type=ACFFieldType.TEXTAREA,
            instructions="Texto explicativo do formulário",
            required=False,
            rows=2,
            character_limit=100
        ),
        ACFField(
            key="form_fields",
            name="form_fields",
            label="Campos do Formulário",
            type=ACFFieldType.CHECKBOX,
            instructions="Selecione os campos necessários",
            choices={
                "name": "Nome",
                "email": "E-mail",
                "phone": "Telefone",
                "company": "Empresa",
                "message": "Mensagem",
                "budget": "Orçamento",
                "service": "Serviço de Interesse"
            },
            default_value=["name", "email", "message"],
            required=True,
            layout="vertical"
        ),
        ACFField(
            key="form_button_text",
            name="form_button_text",
            label="Texto do Botão",
            type=ACFFieldType.TEXT,
            instructions="Texto do botão de envio",
            required=True,
            placeholder="Ex: Enviar Mensagem",
            character_limit=25,
            default_value="Enviar"
        ),
        ACFField(
            key="form_success_message",
            name="form_success_message",
            label="Mensagem de Sucesso",
            type=ACFFieldType.TEXTAREA,
            instructions="Mensagem exibida após envio",
            required=True,
            rows=2,
            default_value="Obrigado! Entraremos em contato em breve.",
            character_limit=150
        ),
        ACFField(
            key="form_redirect_url",
            name="form_redirect_url",
            label="URL de Redirecionamento",
            type=ACFFieldType.URL,
            instructions="Página para redirecionar após envio (opcional)",
            required=False,
            placeholder="https://exemplo.com/obrigado"
        ),
        ACFField(
            key="form_webhook_url",
            name="form_webhook_url",
            label="Webhook URL",
            type=ACFFieldType.URL,
            instructions="URL para enviar dados do formulário",
            required=False,
            placeholder="https://zapier.com/hooks/..."
        )
    ]
    
    return ACFFieldGroup(
        key="group_contact_form",
        title="Formulário de Contato",
        fields=fields,
        location=[
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            }
        ],
        menu_order=4,
        position="normal"
    )


def create_seo_fields() -> ACFFieldGroup:
    """Grupo de campos para configurações SEO"""
    
    fields = [
        ACFField(
            key="seo_title",
            name="seo_title",
            label="Título SEO",
            type=ACFFieldType.TEXT,
            instructions="Título para mecanismos de busca (50-60 caracteres)",
            required=False,
            character_limit=60,
            placeholder="Ex: Landing Page - Solução Completa Para Seu Negócio"
        ),
        ACFField(
            key="seo_description",
            name="seo_description",
            label="Meta Descrição",
            type=ACFFieldType.TEXTAREA,
            instructions="Descrição para mecanismos de busca (150-160 caracteres)",
            required=False,
            rows=3,
            character_limit=160,
            placeholder="Descrição atrativa para aparecer no Google..."
        ),
        ACFField(
            key="seo_keywords",
            name="seo_keywords",
            label="Palavras-chave",
            type=ACFFieldType.TEXT,
            instructions="Palavras-chave separadas por vírgula",
            required=False,
            placeholder="palavra1, palavra2, palavra3"
        ),
        ACFField(
            key="seo_og_image",
            name="seo_og_image",
            label="Imagem de Compartilhamento",
            type=ACFFieldType.IMAGE,
            instructions="Imagem para redes sociais (1200x630px)",
            required=False,
            return_format="url"
        ),
        ACFField(
            key="seo_canonical_url",
            name="seo_canonical_url",
            label="URL Canônica",
            type=ACFFieldType.URL,
            instructions="URL canônica da página",
            required=False
        )
    ]
    
    return ACFFieldGroup(
        key="group_seo_settings",
        title="Configurações SEO",
        fields=fields,
        location=[
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            }
        ],
        menu_order=5,
        position="side",
        style="seamless"
    )


def create_analytics_fields() -> ACFFieldGroup:
    """Grupo de campos para tracking e analytics"""
    
    fields = [
        ACFField(
            key="google_analytics_id",
            name="google_analytics_id",
            label="Google Analytics ID",
            type=ACFFieldType.TEXT,
            instructions="ID do Google Analytics (ex: GA-XXXXXX-X)",
            required=False,
            placeholder="GA-XXXXXX-X"
        ),
        ACFField(
            key="facebook_pixel_id",
            name="facebook_pixel_id",
            label="Facebook Pixel ID",
            type=ACFFieldType.TEXT,
            instructions="ID do Facebook Pixel",
            required=False,
            placeholder="1234567890123456"
        ),
        ACFField(
            key="google_tag_manager_id",
            name="google_tag_manager_id",
            label="Google Tag Manager ID",
            type=ACFFieldType.TEXT,
            instructions="ID do Google Tag Manager (ex: GTM-XXXXXX)",
            required=False,
            placeholder="GTM-XXXXXX"
        ),
        ACFField(
            key="hotjar_site_id",
            name="hotjar_site_id",
            label="Hotjar Site ID",
            type=ACFFieldType.TEXT,
            instructions="ID do site no Hotjar",
            required=False,
            placeholder="1234567"
        ),
        ACFField(
            key="custom_tracking_code",
            name="custom_tracking_code",
            label="Código de Tracking Personalizado",
            type=ACFFieldType.TEXTAREA,
            instructions="Código HTML/JS personalizado para tracking",
            required=False,
            rows=6
        )
    ]
    
    return ACFFieldGroup(
        key="group_analytics_tracking",
        title="Analytics e Tracking",
        fields=fields,
        location=[
            {
                "param": "post_type",
                "operator": "==",
                "value": "page"
            }
        ],
        menu_order=6,
        position="side",
        style="seamless"
    )


def get_all_landing_page_field_groups() -> List[ACFFieldGroup]:
    """Retorna todos os grupos de campos para landing pages"""
    
    return [
        create_hero_section_fields(),
        create_features_section_fields(),
        create_testimonials_section_fields(),
        create_cta_section_fields(),
        create_contact_form_fields(),
        create_seo_fields(),
        create_analytics_fields()
    ]


def get_field_groups_by_landing_page_type(page_type: LandingPageType) -> List[ACFFieldGroup]:
    """Retorna grupos de campos específicos por tipo de landing page"""
    
    # Grupos básicos sempre incluídos
    base_groups = [
        create_hero_section_fields(),
        create_cta_section_fields(),
        create_seo_fields(),
        create_analytics_fields()
    ]
    
    # Grupos específicos por tipo
    type_specific_groups = {
        LandingPageType.LEAD_GENERATION: [
            create_contact_form_fields(),
            create_testimonials_section_fields()
        ],
        LandingPageType.PRODUCT_LAUNCH: [
            create_features_section_fields(),
            create_testimonials_section_fields()
        ],
        LandingPageType.SERVICE_SHOWCASE: [
            create_features_section_fields(),
            create_testimonials_section_fields(),
            create_contact_form_fields()
        ],
        LandingPageType.EVENT_PROMOTION: [
            create_contact_form_fields()
        ],
        LandingPageType.WEBINAR: [
            create_contact_form_fields(),
            create_testimonials_section_fields()
        ],
        LandingPageType.COMING_SOON: [
            create_contact_form_fields()
        ],
        LandingPageType.THANK_YOU: [],
        LandingPageType.DOWNLOAD: [
            create_contact_form_fields()
        ]
    }
    
    # Combinar grupos base com específicos
    specific_groups = type_specific_groups.get(page_type, [])
    return base_groups + specific_groups


class LandingPageACFModel(BaseModel):
    """Modelo completo para uma landing page com todos os campos ACF"""
    
    # Hero Section
    hero_headline: str = Field(..., max_length=80)
    hero_subheadline: str = Field(..., max_length=200)
    hero_cta_text: str = Field(..., max_length=30)
    hero_cta_link: str
    hero_background_image: Optional[str] = None
    hero_video_url: Optional[str] = None
    hero_trust_badges: List[Dict[str, str]] = Field(default_factory=list)
    
    # Features Section
    features_title: Optional[str] = Field(None, max_length=60)
    features_subtitle: Optional[str] = Field(None, max_length=150)
    features_list: List[Dict[str, Any]] = Field(default_factory=list)
    features_layout: str = "grid_3_cols"
    
    # Testimonials Section
    testimonials_title: Optional[str] = Field(None, max_length=60)
    testimonials_list: List[Dict[str, Any]] = Field(default_factory=list)
    testimonials_layout: str = "carousel"
    
    # CTA Section
    cta_headline: str = Field(..., max_length=50)
    cta_description: str = Field(..., max_length=150)
    cta_button_text: str = Field(..., max_length=25)
    cta_button_link: str
    cta_secondary_text: Optional[str] = Field(None, max_length=40)
    cta_urgency_text: Optional[str] = Field(None, max_length=50)
    cta_background_color: str = "#007cba"
    cta_text_color: str = "#ffffff"
    
    # Contact Form
    form_title: Optional[str] = Field(None, max_length=40)
    form_description: Optional[str] = Field(None, max_length=100)
    form_fields: List[str] = Field(default_factory=lambda: ["name", "email", "message"])
    form_button_text: str = "Enviar"
    form_success_message: str = "Obrigado! Entraremos em contato em breve."
    form_redirect_url: Optional[str] = None
    form_webhook_url: Optional[str] = None
    
    # SEO
    seo_title: Optional[str] = Field(None, max_length=60)
    seo_description: Optional[str] = Field(None, max_length=160)
    seo_keywords: Optional[str] = None
    seo_og_image: Optional[str] = None
    seo_canonical_url: Optional[str] = None
    
    # Analytics
    google_analytics_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None
    google_tag_manager_id: Optional[str] = None
    hotjar_site_id: Optional[str] = None
    custom_tracking_code: Optional[str] = None
    
    # Metadata
    landing_page_type: LandingPageType
    industry: LandingPageIndustry
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }