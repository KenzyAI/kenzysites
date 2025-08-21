"""
Landing Page Service - Serviço de provisionamento de landing pages
usando conversão de templates Elementor para ACF

Este serviço permite monetizar portfólio de 10 anos de landing pages Elementor
convertendo-as para templates ACF personalizáveis
"""

from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime
from pathlib import Path
import json

from ..models.template_models import (
    ACFFieldGroup,
    TemplateModel,
    IndustryTemplate,
    BusinessType
)
from .elementor_to_acf_converter import ElementorToACFConverter
from .acf_integration import ACFIntegrationService
from .shared_hosting_provisioner import SharedHostingProvisioner
from .template_repository import TemplateRepository

logger = logging.getLogger(__name__)


class LandingPageService:
    """Serviço principal para provisionar landing pages a partir de templates Elementor"""
    
    def __init__(self):
        self.elementor_converter = ElementorToACFConverter()
        self.acf_service = ACFIntegrationService()
        self.hosting_provisioner = SharedHostingProvisioner()
        self.template_repository = TemplateRepository()
        
    async def list_available_landing_pages(
        self, 
        industry: Optional[str] = None,
        business_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista landing pages disponíveis do portfólio Elementor"""
        
        try:
            # Buscar templates Elementor convertidos
            converted_templates = await self.template_repository.list_templates(
                template_type="landing_page",
                industry=industry
            )
            
            available_pages = []
            
            for template in converted_templates:
                page_info = {
                    "id": template.get("id"),
                    "name": template.get("name"),
                    "industry": template.get("industry"),
                    "business_type": template.get("business_type", "service"),
                    "preview_url": template.get("preview_url"),
                    "elementor_compatible": template.get("elementor_compatible", True),
                    "acf_fields_count": len(template.get("acf_fields", [])),
                    "conversion_score": template.get("conversion_score", 0.0),
                    "features": template.get("features", []),
                    "recommended_for": template.get("recommended_for", []),
                    "created_at": template.get("created_at"),
                    "updated_at": template.get("updated_at")
                }
                available_pages.append(page_info)
            
            # Ordenar por score de conversão e data
            available_pages.sort(
                key=lambda x: (x["conversion_score"], x["updated_at"]), 
                reverse=True
            )
            
            logger.info(f"Listadas {len(available_pages)} landing pages disponíveis")
            return available_pages
            
        except Exception as e:
            logger.error(f"Erro ao listar landing pages: {str(e)}")
            return []
    
    async def get_landing_page_details(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes completos de uma landing page específica"""
        
        try:
            template_data = await self.template_repository.get_template(template_id)
            
            if not template_data:
                logger.warning(f"Landing page {template_id} não encontrada")
                return None
            
            # Processar dados detalhados
            details = {
                "template_info": {
                    "id": template_data.get("id"),
                    "name": template_data.get("name"),
                    "description": template_data.get("description"),
                    "industry": template_data.get("industry"),
                    "business_type": template_data.get("business_type")
                },
                "elementor_data": {
                    "original_url": template_data.get("original_url"),
                    "elementor_version": template_data.get("elementor_version"),
                    "widgets_used": template_data.get("widgets_used", []),
                    "is_pro_required": template_data.get("is_pro_required", False)
                },
                "acf_configuration": {
                    "field_groups": template_data.get("acf_field_groups", []),
                    "customizable_sections": template_data.get("customizable_sections", []),
                    "dynamic_content_areas": template_data.get("dynamic_content_areas", [])
                },
                "conversion_data": {
                    "conversion_score": template_data.get("conversion_score", 0.0),
                    "cta_positions": template_data.get("cta_positions", []),
                    "form_integrations": template_data.get("form_integrations", [])
                },
                "technical_specs": {
                    "load_time_score": template_data.get("load_time_score", 0),
                    "mobile_responsive": template_data.get("mobile_responsive", True),
                    "seo_optimized": template_data.get("seo_optimized", True),
                    "dependencies": template_data.get("dependencies", [])
                }
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da landing page {template_id}: {str(e)}")
            return None
    
    async def provision_landing_page(
        self,
        template_id: str,
        business_data: Dict[str, Any],
        client_domain: str,
        keep_elementor: bool = True,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Provisiona uma landing page personalizada para cliente"""
        
        try:
            logger.info(f"Iniciando provisionamento de landing page {template_id}")
            
            # 1. Obter template base
            template_data = await self.get_landing_page_details(template_id)
            if not template_data:
                raise ValueError(f"Template {template_id} não encontrado")
            
            # 2. Preparar dados de negócio
            business_context = {
                "business_name": business_data.get("business_name"),
                "industry": business_data.get("industry"),
                "target_audience": business_data.get("target_audience"),
                "value_proposition": business_data.get("value_proposition"),
                "contact_info": business_data.get("contact_info", {}),
                "brand_colors": business_data.get("brand_colors", {}),
                "logo_url": business_data.get("logo_url"),
                "social_media": business_data.get("social_media", {})
            }
            
            # 3. Aplicar customizações ACF
            acf_data = await self._generate_personalized_acf_data(
                template_data["acf_configuration"],
                business_context,
                customizations
            )
            
            # 4. Provisionar site WordPress
            provisioning_result = await self.hosting_provisioner.provision_wordpress_multisite(
                business_name=business_data["business_name"],
                industry=business_data["industry"],
                plan=business_data.get("plan", "landing_page"),
                custom_domain=client_domain,
                template_data={
                    "type": "landing_page",
                    "template_id": template_id,
                    "elementor_mode": keep_elementor,
                    "acf_data": acf_data
                }
            )
            
            # 5. Instalar e configurar template
            installation_result = await self._install_landing_page_template(
                provisioning_result["site_info"],
                template_data,
                acf_data,
                keep_elementor
            )
            
            # 6. Configurar integrações (formulários, analytics, etc)
            integrations_result = await self._setup_landing_page_integrations(
                provisioning_result["site_info"],
                business_data
            )
            
            # 7. Resultado final
            result = {
                "success": True,
                "site_info": provisioning_result["site_info"],
                "template_applied": template_id,
                "acf_fields_configured": len(acf_data.get("fields", [])),
                "elementor_preserved": keep_elementor,
                "integrations": integrations_result,
                "urls": {
                    "live_url": provisioning_result["site_info"]["url"],
                    "admin_url": f"{provisioning_result['site_info']['url']}/wp-admin",
                    "elementor_editor": f"{provisioning_result['site_info']['url']}/wp-admin/post.php?post=1&action=elementor" if keep_elementor else None
                },
                "credentials": provisioning_result["credentials"],
                "setup_completed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Landing page provisionada com sucesso: {result['urls']['live_url']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no provisionamento da landing page: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _generate_personalized_acf_data(
        self,
        acf_config: Dict[str, Any],
        business_context: Dict[str, Any],
        customizations: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gera dados ACF personalizados baseados no contexto do negócio"""
        
        acf_data = {
            "fields": {},
            "field_groups": acf_config.get("field_groups", [])
        }
        
        # Campos básicos de negócio
        basic_fields = {
            "business_name": business_context.get("business_name"),
            "tagline": business_context.get("value_proposition"),
            "phone": business_context.get("contact_info", {}).get("phone"),
            "email": business_context.get("contact_info", {}).get("email"),
            "address": business_context.get("contact_info", {}).get("address"),
            "whatsapp": business_context.get("contact_info", {}).get("whatsapp"),
            "logo_url": business_context.get("logo_url")
        }
        
        # Aplicar customizações
        if customizations:
            for field_name, value in customizations.items():
                basic_fields[field_name] = value
        
        acf_data["fields"] = basic_fields
        
        return acf_data
    
    async def _install_landing_page_template(
        self,
        site_info: Dict[str, Any],
        template_data: Dict[str, Any],
        acf_data: Dict[str, Any],
        keep_elementor: bool
    ) -> Dict[str, Any]:
        """Instala o template da landing page no site WordPress"""
        
        try:
            # Instalar plugins necessários
            plugins_to_install = ["advanced-custom-fields"]
            if keep_elementor:
                plugins_to_install.append("elementor")
                
            # Importar template Elementor (se aplicável)
            if keep_elementor and template_data.get("elementor_data"):
                elementor_import = await self._import_elementor_template(
                    site_info,
                    template_data["elementor_data"]
                )
            
            # Configurar campos ACF
            acf_setup = await self.acf_service.create_field_groups_batch(
                template_data["acf_configuration"]["field_groups"]
            )
            
            # Popular campos com dados do cliente
            field_population = await self._populate_acf_fields(
                site_info,
                acf_data
            )
            
            return {
                "plugins_installed": plugins_to_install,
                "elementor_imported": keep_elementor,
                "acf_configured": len(acf_setup),
                "fields_populated": len(field_population)
            }
            
        except Exception as e:
            logger.error(f"Erro na instalação do template: {str(e)}")
            raise
    
    async def _import_elementor_template(
        self,
        site_info: Dict[str, Any],
        elementor_data: Dict[str, Any]
    ) -> bool:
        """Importa template Elementor para o site"""
        
        try:
            # Implementação simplificada
            # Na prática, usaria WP-CLI para importar o template
            logger.info(f"Importando template Elementor para {site_info['url']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na importação Elementor: {str(e)}")
            return False
    
    async def _populate_acf_fields(
        self,
        site_info: Dict[str, Any],
        acf_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Popula os campos ACF com dados do cliente"""
        
        try:
            populated_fields = {}
            
            for field_name, value in acf_data.get("fields", {}).items():
                if value:
                    populated_fields[field_name] = value
                    
            logger.info(f"Populados {len(populated_fields)} campos ACF")
            return populated_fields
            
        except Exception as e:
            logger.error(f"Erro ao popular campos ACF: {str(e)}")
            return {}
    
    async def _setup_landing_page_integrations(
        self,
        site_info: Dict[str, Any],
        business_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configura integrações da landing page (formulários, analytics, etc)"""
        
        integrations = {
            "contact_forms": False,
            "google_analytics": False,
            "facebook_pixel": False,
            "whatsapp_button": False
        }
        
        try:
            # Configurar formulário de contato
            if business_data.get("contact_info", {}).get("email"):
                integrations["contact_forms"] = True
            
            # Configurar WhatsApp
            if business_data.get("contact_info", {}).get("whatsapp"):
                integrations["whatsapp_button"] = True
            
            # Configurar tracking (se fornecido)
            if business_data.get("google_analytics_id"):
                integrations["google_analytics"] = True
                
            if business_data.get("facebook_pixel_id"):
                integrations["facebook_pixel"] = True
            
            return integrations
            
        except Exception as e:
            logger.error(f"Erro ao configurar integrações: {str(e)}")
            return integrations
    
    async def clone_landing_page(
        self,
        source_template_id: str,
        new_business_data: Dict[str, Any],
        modifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Clona uma landing page existente para novo cliente"""
        
        try:
            # Obter template original
            source_template = await self.get_landing_page_details(source_template_id)
            if not source_template:
                raise ValueError(f"Template fonte {source_template_id} não encontrado")
            
            # Aplicar modificações
            if modifications:
                # Aplicar mudanças no template
                modified_template = await self._apply_template_modifications(
                    source_template,
                    modifications
                )
            else:
                modified_template = source_template
            
            # Provisionar nova landing page
            result = await self.provision_landing_page(
                source_template_id,
                new_business_data,
                new_business_data.get("domain"),
                keep_elementor=True,
                customizations=modifications
            )
            
            result["cloned_from"] = source_template_id
            return result
            
        except Exception as e:
            logger.error(f"Erro ao clonar landing page: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _apply_template_modifications(
        self,
        template_data: Dict[str, Any],
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aplica modificações a um template"""
        
        modified_template = template_data.copy()
        
        # Aplicar modificações nos campos ACF
        if "acf_fields" in modifications:
            modified_template["acf_configuration"]["field_groups"] = modifications["acf_fields"]
        
        # Aplicar modificações de design
        if "design_changes" in modifications:
            # Implementar mudanças de design
            pass
        
        return modified_template
    
    async def get_landing_page_analytics(
        self,
        site_info: Dict[str, Any],
        date_range: Optional[str] = "30d"
    ) -> Dict[str, Any]:
        """Obtém analytics de uma landing page (mock implementation)"""
        
        # Implementação mock - na prática integraria com Google Analytics
        return {
            "pageviews": 1250,
            "unique_visitors": 890,
            "bounce_rate": 0.35,
            "conversion_rate": 0.08,
            "avg_time_on_page": "2:45",
            "top_traffic_sources": [
                {"source": "Google Ads", "percentage": 45},
                {"source": "Facebook", "percentage": 30},
                {"source": "Direct", "percentage": 25}
            ],
            "conversions": {
                "form_submissions": 72,
                "phone_calls": 18,
                "whatsapp_messages": 25
            },
            "date_range": date_range,
            "last_updated": datetime.utcnow().isoformat()
        }