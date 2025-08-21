"""
ACF (Advanced Custom Fields) Integration Service
"""

import json
import uuid
from typing import Dict, Any, List, Optional
import logging

from app.models.template_models import (
    ACFField, ACFFieldGroup, ACFFieldType, BrazilianTemplate, BRAZILIAN_INDUSTRIES
)

logger = logging.getLogger(__name__)

class ACFService:
    """Service for ACF integration"""
    
    def __init__(self):
        self.field_templates = self._initialize_field_templates()
    
    def _initialize_field_templates(self) -> Dict[str, List[Dict]]:
        """Initialize common field templates for different industries"""
        return {
            "basic_business": [
                {
                    "key": "field_business_info",
                    "label": "Informações do Negócio",
                    "name": "business_info",
                    "type": "group",
                    "sub_fields": [
                        {
                            "key": "field_business_name",
                            "label": "Nome da Empresa",
                            "name": "business_name",
                            "type": "text",
                            "required": True,
                            "placeholder": "{{business_name}}"
                        },
                        {
                            "key": "field_business_description",
                            "label": "Descrição do Negócio",
                            "name": "business_description",
                            "type": "textarea",
                            "placeholder": "{{business_description}}"
                        },
                        {
                            "key": "field_business_phone",
                            "label": "Telefone",
                            "name": "business_phone",
                            "type": "text",
                            "placeholder": "(11) 99999-9999"
                        },
                        {
                            "key": "field_business_email",
                            "label": "Email",
                            "name": "business_email",
                            "type": "email",
                            "placeholder": "contato@empresa.com"
                        },
                        {
                            "key": "field_business_address",
                            "label": "Endereço",
                            "name": "business_address",
                            "type": "textarea",
                            "placeholder": "Rua, número, bairro, cidade - CEP"
                        }
                    ]
                }
            ],
            "contact_section": [
                {
                    "key": "field_contact_info",
                    "label": "Informações de Contato",
                    "name": "contact_info",
                    "type": "group",
                    "sub_fields": [
                        {
                            "key": "field_whatsapp",
                            "label": "WhatsApp",
                            "name": "whatsapp_number",
                            "type": "text",
                            "placeholder": "5511999999999",
                            "instructions": "Número com código do país (55) + DDD + número"
                        },
                        {
                            "key": "field_social_media",
                            "label": "Redes Sociais",
                            "name": "social_media",
                            "type": "repeater",
                            "sub_fields": [
                                {
                                    "key": "field_social_platform",
                                    "label": "Plataforma",
                                    "name": "platform",
                                    "type": "select",
                                    "choices": {
                                        "facebook": "Facebook",
                                        "instagram": "Instagram",
                                        "linkedin": "LinkedIn",
                                        "twitter": "Twitter",
                                        "youtube": "YouTube"
                                    }
                                },
                                {
                                    "key": "field_social_url",
                                    "label": "URL",
                                    "name": "url",
                                    "type": "url"
                                }
                            ]
                        }
                    ]
                }
            ],
            "services_section": [
                {
                    "key": "field_services",
                    "label": "Serviços",
                    "name": "services",
                    "type": "repeater",
                    "sub_fields": [
                        {
                            "key": "field_service_name",
                            "label": "Nome do Serviço",
                            "name": "service_name",
                            "type": "text",
                            "required": True
                        },
                        {
                            "key": "field_service_description",
                            "label": "Descrição",
                            "name": "service_description",
                            "type": "textarea"
                        },
                        {
                            "key": "field_service_price",
                            "label": "Preço",
                            "name": "service_price",
                            "type": "text",
                            "placeholder": "R$ 0,00"
                        },
                        {
                            "key": "field_service_image",
                            "label": "Imagem",
                            "name": "service_image",
                            "type": "image",
                            "return_format": "url"
                        }
                    ]
                }
            ]
        }
    
    def create_template_fields_for_industry(self, industry: str, business_type: str = "service") -> List[ACFFieldGroup]:
        """Create ACF fields for industry template"""
        try:
            field_groups = []
            
            # Always add basic business info
            basic_fields = self._create_basic_business_fields()
            field_groups.append(basic_fields)
            
            # Add contact section
            contact_fields = self._create_contact_fields()
            field_groups.append(contact_fields)
            
            # Add services section
            services_fields = self._create_services_fields()
            field_groups.append(services_fields)
            
            # Add industry-specific fields
            industry_fields = self._create_industry_specific_fields(industry, business_type)
            if industry_fields:
                field_groups.extend(industry_fields)
            
            # Add Brazilian-specific fields if applicable
            if industry.lower() in BRAZILIAN_INDUSTRIES:
                brazilian_fields = self._create_brazilian_fields(industry)
                if brazilian_fields:
                    field_groups.append(brazilian_fields)
            
            logger.info(f"Created {len(field_groups)} field groups for industry: {industry}")
            return field_groups
            
        except Exception as e:
            logger.error(f"Error creating fields for industry {industry}: {str(e)}")
            return []
    
    def _create_basic_business_fields(self) -> ACFFieldGroup:
        """Create basic business information fields"""
        fields = [
            ACFField(
                key="field_business_name",
                label="Nome da Empresa",
                name="business_name",
                type=ACFFieldType.TEXT,
                required=True,
                placeholder="{{business_name}}",
                instructions="Nome principal da empresa ou negócio"
            ),
            ACFField(
                key="field_business_description",
                label="Descrição do Negócio",
                name="business_description",
                type=ACFFieldType.TEXTAREA,
                placeholder="{{business_description}}",
                instructions="Breve descrição sobre o que a empresa faz"
            ),
            ACFField(
                key="field_business_slogan",
                label="Slogan/Tagline",
                name="business_slogan",
                type=ACFFieldType.TEXT,
                placeholder="Sua frase marcante aqui",
                instructions="Frase que representa sua marca"
            ),
            ACFField(
                key="field_business_logo",
                label="Logo da Empresa",
                name="business_logo",
                type=ACFFieldType.IMAGE,
                return_format="url",
                instructions="Upload do logo da empresa"
            )
        ]
        
        return ACFFieldGroup(
            key="group_business_basic",
            title="Informações Básicas da Empresa",
            fields=fields,
            location=[[{"param": "page_template", "operator": "==", "value": "default"}]]
        )
    
    def _create_contact_fields(self) -> ACFFieldGroup:
        """Create contact information fields"""
        fields = [
            ACFField(
                key="field_contact_phone",
                label="Telefone Principal",
                name="contact_phone",
                type=ACFFieldType.TEXT,
                placeholder="(11) 99999-9999",
                instructions="Telefone principal para contato"
            ),
            ACFField(
                key="field_contact_email",
                label="Email Principal",
                name="contact_email",
                type=ACFFieldType.EMAIL,
                placeholder="contato@empresa.com",
                instructions="Email principal para contato"
            ),
            ACFField(
                key="field_contact_address",
                label="Endereço Completo",
                name="contact_address",
                type=ACFFieldType.TEXTAREA,
                placeholder="Rua, número, bairro, cidade - CEP",
                instructions="Endereço completo da empresa"
            ),
            ACFField(
                key="field_contact_whatsapp",
                label="WhatsApp",
                name="contact_whatsapp",
                type=ACFFieldType.TEXT,
                placeholder="5511999999999",
                instructions="Número com código do país (55) + DDD + número"
            ),
            ACFField(
                key="field_contact_hours",
                label="Horário de Funcionamento",
                name="contact_hours",
                type=ACFFieldType.TEXTAREA,
                placeholder="Segunda a Sexta: 08:00 às 18:00",
                instructions="Horários de atendimento"
            )
        ]
        
        return ACFFieldGroup(
            key="group_contact_info",
            title="Informações de Contato",
            fields=fields,
            location=[[{"param": "page_template", "operator": "==", "value": "default"}]]
        )
    
    def _create_services_fields(self) -> ACFFieldGroup:
        """Create services/products fields"""
        fields = [
            ACFField(
                key="field_services_intro",
                label="Introdução dos Serviços",
                name="services_intro",
                type=ACFFieldType.TEXTAREA,
                placeholder="Conheça nossos principais serviços...",
                instructions="Texto introdutório da seção de serviços"
            ),
            ACFField(
                key="field_services_list",
                label="Lista de Serviços",
                name="services_list",
                type=ACFFieldType.REPEATER,
                instructions="Adicione os serviços oferecidos"
            )
        ]
        
        return ACFFieldGroup(
            key="group_services",
            title="Serviços e Produtos",
            fields=fields,
            location=[[{"param": "page_template", "operator": "==", "value": "default"}]]
        )
    
    def _create_industry_specific_fields(self, industry: str, business_type: str) -> List[ACFFieldGroup]:
        """Create industry-specific ACF fields"""
        industry_lower = industry.lower()
        field_groups = []
        
        if industry_lower in ["restaurante", "alimentacao"]:
            field_groups.append(self._create_restaurant_fields())
        elif industry_lower in ["saude", "clinica", "medico"]:
            field_groups.append(self._create_healthcare_fields())
        elif industry_lower in ["ecommerce", "loja"]:
            field_groups.append(self._create_ecommerce_fields())
        elif industry_lower in ["educacao", "escola"]:
            field_groups.append(self._create_education_fields())
        elif industry_lower in ["advocacia", "juridico"]:
            field_groups.append(self._create_legal_fields())
        
        return field_groups
    
    def _create_restaurant_fields(self) -> ACFFieldGroup:
        """Create restaurant-specific fields"""
        fields = [
            ACFField(
                key="field_restaurant_cuisine",
                label="Tipo de Culinária",
                name="restaurant_cuisine",
                type=ACFFieldType.SELECT,
                choices={
                    "brasileira": "Brasileira",
                    "italiana": "Italiana",
                    "japonesa": "Japonesa",
                    "chinesa": "Chinesa",
                    "mexicana": "Mexicana",
                    "fastfood": "Fast Food",
                    "vegetariana": "Vegetariana",
                    "vegana": "Vegana"
                }
            ),
            ACFField(
                key="field_restaurant_delivery",
                label="Aceita Delivery",
                name="restaurant_delivery",
                type=ACFFieldType.TRUE_FALSE,
                default_value=True
            ),
            ACFField(
                key="field_restaurant_reservation",
                label="Aceita Reservas",
                name="restaurant_reservation",
                type=ACFFieldType.TRUE_FALSE,
                default_value=True
            ),
            ACFField(
                key="field_restaurant_menu_url",
                label="Link do Cardápio",
                name="restaurant_menu_url",
                type=ACFFieldType.URL,
                placeholder="https://cardapio.com"
            )
        ]
        
        return ACFFieldGroup(
            key="group_restaurant_specific",
            title="Informações do Restaurante",
            fields=fields
        )
    
    def _create_healthcare_fields(self) -> ACFFieldGroup:
        """Create healthcare-specific fields"""
        fields = [
            ACFField(
                key="field_healthcare_specialty",
                label="Especialidade",
                name="healthcare_specialty",
                type=ACFFieldType.TEXT,
                placeholder="Clínica Geral, Odontologia, etc."
            ),
            ACFField(
                key="field_healthcare_crm",
                label="CRM/Registro Profissional",
                name="healthcare_crm",
                type=ACFFieldType.TEXT,
                placeholder="CRM 12345/SP"
            ),
            ACFField(
                key="field_healthcare_insurance",
                label="Planos de Saúde Aceitos",
                name="healthcare_insurance",
                type=ACFFieldType.TEXTAREA,
                placeholder="SulAmérica, Bradesco, Unimed..."
            ),
            ACFField(
                key="field_healthcare_booking",
                label="Link de Agendamento",
                name="healthcare_booking",
                type=ACFFieldType.URL,
                placeholder="https://agendamento.com"
            )
        ]
        
        return ACFFieldGroup(
            key="group_healthcare_specific",
            title="Informações da Clínica/Consultório",
            fields=fields
        )
    
    def _create_ecommerce_fields(self) -> ACFFieldGroup:
        """Create e-commerce specific fields"""
        fields = [
            ACFField(
                key="field_ecommerce_category",
                label="Categoria Principal",
                name="ecommerce_category",
                type=ACFFieldType.TEXT,
                placeholder="Moda, Eletrônicos, Casa..."
            ),
            ACFField(
                key="field_ecommerce_payment",
                label="Formas de Pagamento",
                name="ecommerce_payment",
                type=ACFFieldType.CHECKBOX,
                choices={
                    "cartao": "Cartão de Crédito/Débito",
                    "pix": "PIX",
                    "boleto": "Boleto",
                    "transferencia": "Transferência"
                }
            ),
            ACFField(
                key="field_ecommerce_shipping",
                label="Informações de Entrega",
                name="ecommerce_shipping",
                type=ACFFieldType.TEXTAREA,
                placeholder="Entregamos em todo Brasil via Correios..."
            ),
            ACFField(
                key="field_ecommerce_store_url",
                label="Link da Loja",
                name="ecommerce_store_url",
                type=ACFFieldType.URL,
                placeholder="https://loja.com"
            )
        ]
        
        return ACFFieldGroup(
            key="group_ecommerce_specific",
            title="Informações da Loja Virtual",
            fields=fields
        )
    
    def _create_education_fields(self) -> ACFFieldGroup:
        """Create education-specific fields"""
        fields = [
            ACFField(
                key="field_education_type",
                label="Tipo de Ensino",
                name="education_type",
                type=ACFFieldType.SELECT,
                choices={
                    "infantil": "Educação Infantil",
                    "fundamental": "Ensino Fundamental",
                    "medio": "Ensino Médio",
                    "tecnico": "Técnico",
                    "superior": "Superior",
                    "curso_livre": "Curso Livre",
                    "online": "Ensino Online"
                }
            ),
            ACFField(
                key="field_education_courses",
                label="Cursos Oferecidos",
                name="education_courses",
                type=ACFFieldType.TEXTAREA,
                placeholder="Liste os principais cursos..."
            ),
            ACFField(
                key="field_education_duration",
                label="Duração dos Cursos",
                name="education_duration",
                type=ACFFieldType.TEXT,
                placeholder="2 anos, 6 meses, etc."
            ),
            ACFField(
                key="field_education_enrollment",
                label="Link de Inscrição",
                name="education_enrollment",
                type=ACFFieldType.URL,
                placeholder="https://inscricoes.escola.com"
            )
        ]
        
        return ACFFieldGroup(
            key="group_education_specific",
            title="Informações Educacionais",
            fields=fields
        )
    
    def _create_legal_fields(self) -> ACFFieldGroup:
        """Create legal services specific fields"""
        fields = [
            ACFField(
                key="field_legal_areas",
                label="Áreas de Atuação",
                name="legal_areas",
                type=ACFFieldType.CHECKBOX,
                choices={
                    "civil": "Direito Civil",
                    "criminal": "Direito Criminal",
                    "trabalhista": "Direito Trabalhista",
                    "empresarial": "Direito Empresarial",
                    "tributario": "Direito Tributário",
                    "familia": "Direito de Família",
                    "imobiliario": "Direito Imobiliário"
                }
            ),
            ACFField(
                key="field_legal_oab",
                label="Número da OAB",
                name="legal_oab",
                type=ACFFieldType.TEXT,
                placeholder="OAB/SP 123456"
            ),
            ACFField(
                key="field_legal_consultation",
                label="Consulta Gratuita",
                name="legal_consultation",
                type=ACFFieldType.TRUE_FALSE,
                default_value=True
            ),
            ACFField(
                key="field_legal_booking",
                label="Link de Agendamento",
                name="legal_booking",
                type=ACFFieldType.URL,
                placeholder="https://agendamento.escritorio.com"
            )
        ]
        
        return ACFFieldGroup(
            key="group_legal_specific",
            title="Informações do Escritório",
            fields=fields
        )
    
    def _create_brazilian_fields(self, industry: str) -> Optional[ACFFieldGroup]:
        """Create Brazilian-specific fields"""
        brazilian_template = BRAZILIAN_INDUSTRIES.get(industry.lower())
        if not brazilian_template:
            return None
        
        fields = []
        
        # CNPJ field
        if brazilian_template.cnpj_field:
            fields.append(ACFField(
                key="field_cnpj",
                label="CNPJ",
                name="cnpj",
                type=ACFFieldType.TEXT,
                placeholder="00.000.000/0000-00",
                instructions="CNPJ da empresa"
            ))
        
        # CPF field (for individual professionals)
        if brazilian_template.cpf_field:
            fields.append(ACFField(
                key="field_cpf",
                label="CPF",
                name="cpf",
                type=ACFFieldType.TEXT,
                placeholder="000.000.000-00",
                instructions="CPF do profissional"
            ))
        
        # PIX payment info
        if brazilian_template.pix_payment:
            fields.append(ACFField(
                key="field_pix_key",
                label="Chave PIX",
                name="pix_key",
                type=ACFFieldType.TEXT,
                placeholder="email@exemplo.com ou telefone",
                instructions="Chave PIX para recebimentos"
            ))
        
        # LGPD notice
        if brazilian_template.lgpd_notice:
            fields.append(ACFField(
                key="field_lgpd_text",
                label="Texto LGPD",
                name="lgpd_text",
                type=ACFFieldType.TEXTAREA,
                default_value="Este site utiliza cookies para melhorar sua experiência. Ao continuar navegando, você concorda com nossa Política de Privacidade.",
                instructions="Texto de aviso LGPD"
            ))
        
        # Delivery areas (for restaurants)
        if brazilian_template.delivery_areas:
            fields.append(ACFField(
                key="field_delivery_areas",
                label="Áreas de Entrega",
                name="delivery_areas",
                type=ACFFieldType.TEXTAREA,
                placeholder="Centro, Zona Sul, Zona Norte...",
                instructions="Regiões atendidas para delivery"
            ))
        
        if not fields:
            return None
        
        return ACFFieldGroup(
            key="group_brazilian_specific",
            title="Informações Brasil",
            fields=fields
        )
    
    def personalize_fields_with_ai(self, field_group: ACFFieldGroup, business_data: Dict[str, Any]) -> None:
        """Personalize fields with AI-generated content"""
        try:
            for field in field_group.fields:
                if field.default_value and isinstance(field.default_value, str):
                    # Replace placeholders with actual business data
                    personalized_value = field.default_value
                    for key, value in business_data.items():
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in personalized_value:
                            personalized_value = personalized_value.replace(placeholder, str(value))
                    field.default_value = personalized_value
                
                # Update placeholders as well
                if field.placeholder and isinstance(field.placeholder, str):
                    personalized_placeholder = field.placeholder
                    for key, value in business_data.items():
                        placeholder = f"{{{{{key}}}}}"
                        if placeholder in personalized_placeholder:
                            personalized_placeholder = personalized_placeholder.replace(placeholder, str(value))
                    field.placeholder = personalized_placeholder
            
            logger.info(f"Personalized field group: {field_group.title}")
            
        except Exception as e:
            logger.error(f"Error personalizing field group {field_group.title}: {str(e)}")
    
    def generate_acf_export(self, field_groups: List[ACFFieldGroup]) -> Dict[str, Any]:
        """Generate ACF export data compatible with WordPress"""
        try:
            export_data = []
            
            for group in field_groups:
                # Convert field group to ACF export format
                group_data = {
                    "key": group.key,
                    "title": group.title,
                    "fields": [],
                    "location": group.location,
                    "menu_order": group.menu_order,
                    "position": group.position,
                    "style": group.style,
                    "label_placement": group.label_placement,
                    "instruction_placement": group.instruction_placement,
                    "hide_on_screen": group.hide_on_screen or [],
                    "active": group.active,
                    "description": group.description
                }
                
                # Convert fields
                for field in group.fields:
                    field_data = {
                        "key": field.key,
                        "label": field.label,
                        "name": field.name,
                        "type": field.type.value,
                        "instructions": field.instructions,
                        "required": 1 if field.required else 0,
                        "conditional_logic": field.conditional_logic or 0,
                        "wrapper": field.wrapper or {
                            "width": "",
                            "class": "",
                            "id": ""
                        },
                        "default_value": field.default_value or "",
                        "placeholder": field.placeholder,
                        "prepend": field.prepend,
                        "append": field.append,
                        "formatting": field.formatting,
                        "maxlength": field.maxlength or "",
                    }
                    
                    # Add type-specific properties
                    if field.type in [ACFFieldType.SELECT, ACFFieldType.CHECKBOX, ACFFieldType.RADIO]:
                        field_data["choices"] = field.choices or {}
                        field_data["allow_null"] = 1 if field.allow_null else 0
                        field_data["multiple"] = 1 if field.multiple else 0
                        field_data["ui"] = 1 if field.ui else 0
                        field_data["ajax"] = 1 if field.ajax else 0
                        field_data["return_format"] = field.return_format
                    
                    group_data["fields"].append(field_data)
                
                export_data.append(group_data)
            
            # Final export structure
            final_export = {
                "version": 2,
                "export_date": "2025-01-20 12:00:00",
                "field_groups": export_data
            }
            
            logger.info(f"Generated ACF export with {len(export_data)} field groups")
            return final_export
            
        except Exception as e:
            logger.error(f"Error generating ACF export: {str(e)}")
            return {}
    
    def get_template_recommendations(self, industry: str) -> Dict[str, Any]:
        """Get template recommendations for industry"""
        recommendations = {
            "theme": "Astra",
            "plugins": ["advanced-custom-fields-pro", "elementor"],
            "colors": {"primary": "#0066FF", "secondary": "#00D4FF"},
            "fonts": {"heading": "Inter", "body": "Inter"}
        }
        
        # Industry-specific recommendations
        industry_lower = industry.lower()
        
        if industry_lower in ["restaurante", "alimentacao"]:
            recommendations.update({
                "plugins": recommendations["plugins"] + ["restaurant-menu", "wp-reservation"],
                "colors": {"primary": "#FF6B35", "secondary": "#F7931E"},
                "fonts": {"heading": "Playfair Display", "body": "Source Sans Pro"}
            })
        elif industry_lower in ["saude", "clinica"]:
            recommendations.update({
                "plugins": recommendations["plugins"] + ["bookly", "appointment-booking"],
                "colors": {"primary": "#2E8B57", "secondary": "#98FB98"},
                "fonts": {"heading": "Lato", "body": "Open Sans"}
            })
        elif industry_lower in ["advocacia", "juridico"]:
            recommendations.update({
                "colors": {"primary": "#1C3A5C", "secondary": "#B8860B"},
                "fonts": {"heading": "Merriweather", "body": "Source Sans Pro"}
            })
        
        return recommendations
    
    def generate_wp_cli_commands(self, field_groups: List[ACFFieldGroup]) -> List[str]:
        """Generate WP-CLI commands to import ACF fields"""
        commands = []
        
        try:
            # Create export file content
            export_data = self.generate_acf_export(field_groups)
            export_json = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            # Commands to import ACF
            commands = [
                # Create temporary file with ACF export
                f"cat > /tmp/acf-export.json << 'EOF'\n{export_json}\nEOF",
                
                # Import ACF fields
                "wp acf import /tmp/acf-export.json",
                
                # Clean up
                "rm /tmp/acf-export.json"
            ]
            
            logger.info(f"Generated {len(commands)} WP-CLI commands for ACF import")
            
        except Exception as e:
            logger.error(f"Error generating WP-CLI commands: {str(e)}")
        
        return commands

acf_service = ACFService()