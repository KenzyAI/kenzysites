"""
Template-related models for WordPress AI SaaS
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ACFFieldType(str, Enum):
    """ACF Field Types"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    URL = "url"
    PASSWORD = "password"
    IMAGE = "image"
    GALLERY = "gallery"
    FILE = "file"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    BUTTON_GROUP = "button_group"
    TRUE_FALSE = "true_false"
    LINK = "link"
    POST_OBJECT = "post_object"
    PAGE_LINK = "page_link"
    RELATIONSHIP = "relationship"
    TAXONOMY = "taxonomy"
    USER = "user"
    GOOGLE_MAP = "google_map"
    DATE_PICKER = "date_picker"
    DATE_TIME_PICKER = "date_time_picker"
    TIME_PICKER = "time_picker"
    COLOR_PICKER = "color_picker"
    MESSAGE = "message"
    ACCORDION = "accordion"
    TAB = "tab"
    GROUP = "group"
    REPEATER = "repeater"
    FLEXIBLE_CONTENT = "flexible_content"
    CLONE = "clone"

class ACFField(BaseModel):
    """ACF Field Model"""
    key: str
    label: str
    name: str
    type: ACFFieldType
    instructions: Optional[str] = ""
    required: bool = False
    conditional_logic: Optional[Dict] = None
    wrapper: Optional[Dict] = None
    default_value: Optional[Union[str, int, bool, List, Dict]] = None
    placeholder: Optional[str] = ""
    prepend: Optional[str] = ""
    append: Optional[str] = ""
    formatting: Optional[str] = "none"
    maxlength: Optional[int] = None
    choices: Optional[Dict[str, str]] = None
    allow_null: Optional[bool] = False
    multiple: Optional[bool] = False
    ui: Optional[bool] = True
    ajax: Optional[bool] = False
    return_format: Optional[str] = "value"

class ACFFieldGroup(BaseModel):
    """ACF Field Group Model"""
    key: str
    title: str
    fields: List[ACFField]
    location: List[List[Dict]] = []
    menu_order: int = 0
    position: str = "normal"
    style: str = "default"
    label_placement: str = "top"
    instruction_placement: str = "label"
    hide_on_screen: Optional[List[str]] = None
    active: bool = True
    description: Optional[str] = ""

class TemplateCustomizationRequest(BaseModel):
    template_id: str
    business_name: str
    business_description: str
    industry: str
    target_audience: Optional[str] = ""
    services_products: List[str] = []
    unique_selling_points: List[str] = []
    tone_of_voice: str = "professional"
    primary_language: str = "pt_BR"
    color_scheme: Optional[Dict[str, str]] = None
    fonts: Optional[Dict[str, str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class CustomizedTemplate(BaseModel):
    template_id: str
    customization_id: str
    business_name: str
    customized_fields: Dict[str, Any]
    generated_content: Dict[str, Any]
    suggested_images: List[str] = []
    generated_images: List[str] = []
    acf_export_data: Dict[str, Any]
    ai_credits_used: int
    processing_time: float
    created_at: datetime = Field(default_factory=datetime.now)

class TemplateDefinition(BaseModel):
    """Template definition model"""
    id: str
    name: str
    description: str
    category: str
    industry: str
    style: str
    acf_field_groups: List[ACFFieldGroup] = []
    preview_url: Optional[str] = None
    thumbnail: Optional[str] = None
    features: List[str] = []
    is_premium: bool = False
    tags: List[str] = []

class SitePreview(BaseModel):
    """Site preview model"""
    preview_id: str
    customization_id: str
    preview_url: str
    expires_at: datetime
    is_published: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class TemplateLibrary(BaseModel):
    """Template library overview"""
    total_templates: int
    categories: List[str]
    industries: List[str]
    featured_templates: List[str]
    new_templates: List[str]
    popular_templates: List[str]

class TemplateSearchFilter(BaseModel):
    """Search and filter options"""
    category: Optional[str] = None
    industry: Optional[str] = None
    style: Optional[str] = None
    is_premium: Optional[bool] = None
    tags: Optional[List[str]] = None
    search_query: Optional[str] = None

@dataclass
class BrazilianTemplate:
    industry_key: str
    industry_name: str
    description: str
    whatsapp_integration: bool = True
    pix_payment: bool = True
    lgpd_notice: bool = True
    cnpj_field: bool = True
    cpf_field: bool = False
    delivery_areas: bool = False
    specific_features: List[str] = None

    def __post_init__(self):
        if self.specific_features is None:
            self.specific_features = []

BRAZILIAN_INDUSTRIES = {
    "restaurante": BrazilianTemplate(
        industry_key="restaurante",
        industry_name="Restaurante e Alimentação",
        description="Templates para restaurantes, lanchonetes, delivery e food trucks",
        delivery_areas=True,
        specific_features=["cardapio_digital", "pedidos_online", "delivery", "sistema_mesa", "cardapio_qr"]
    ),
    "saude": BrazilianTemplate(
        industry_key="saude",
        industry_name="Saúde e Bem-estar",
        description="Templates para clínicas, consultórios, dentistas e profissionais da saúde",
        cpf_field=True,
        specific_features=["agendamento_online", "prontuario", "telemedicina", "planos_saude", "receituario"]
    ),
    "ecommerce": BrazilianTemplate(
        industry_key="ecommerce",
        industry_name="E-commerce",
        description="Templates para lojas virtuais e vendas online",
        specific_features=["catalogo_produtos", "carrinho_compras", "checkout_pix", "marketplace", "cupons_desconto"]
    ),
    "educacao": BrazilianTemplate(
        industry_key="educacao",
        industry_name="Educação",
        description="Templates para escolas, cursos online e educação",
        cpf_field=True,
        specific_features=["portal_aluno", "cursos_online", "area_professor", "biblioteca", "certificados"]
    ),
    "imobiliaria": BrazilianTemplate(
        industry_key="imobiliaria",
        industry_name="Imobiliária",
        description="Templates para imobiliárias e corretores",
        cpf_field=True,
        specific_features=["busca_imoveis", "calculadora_financiamento", "visita_virtual", "portal_proprietario"]
    ),
    "advocacia": BrazilianTemplate(
        industry_key="advocacia",
        industry_name="Advocacia e Jurídico",
        description="Templates para escritórios de advocacia e advogados",
        cpf_field=True,
        specific_features=["area_cliente", "agendamento_consulta", "contratos", "peticoes", "honorarios"]
    ),
    "consultoria": BrazilianTemplate(
        industry_key="consultoria",
        industry_name="Consultoria",
        description="Templates para consultores e prestadores de serviço",
        specific_features=["portfolio", "depoimentos", "agenda_online", "proposta_comercial", "cases_sucesso"]
    ),
    "fitness": BrazilianTemplate(
        industry_key="fitness",
        industry_name="Academia e Fitness",
        description="Templates para academias, personal trainers e esportes",
        cpf_field=True,
        specific_features=["planos_treino", "agendamento_aula", "avalacao_fisica", "nutricao", "check_in"]
    ),
    "beleza": BrazilianTemplate(
        industry_key="beleza",
        industry_name="Beleza e Estética",
        description="Templates para salões, clínicas de estética e profissionais da beleza",
        cpf_field=True,
        specific_features=["agendamento_servico", "catalogo_servicos", "before_after", "fidelidade", "promocoes"]
    ),
    "automotivo": BrazilianTemplate(
        industry_key="automotivo",
        industry_name="Automotivo",
        description="Templates para oficinas, concessionárias e serviços automotivos",
        specific_features=["catalogo_veiculos", "agendamento_servico", "orcamento_online", "revisao", "pecas"]
    )
}