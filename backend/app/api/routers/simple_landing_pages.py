"""
Simple Landing Pages API - Sistema direto para personalizar templates Elementor
Focado em casos de uso imediatos para clientes locais
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging
import json
import uuid
from datetime import datetime
import re

logger = logging.getLogger(__name__)
router = APIRouter()

# =============== MODELS ===============

class BusinessInfo(BaseModel):
    """Informações básicas do negócio para personalização"""
    name: str = Field(..., description="Nome do negócio")
    phone: str = Field(..., description="Telefone com WhatsApp")
    email: Optional[str] = Field(None, description="Email de contato")
    address: Optional[str] = Field(None, description="Endereço completo")
    services: str = Field(..., description="Principais serviços/produtos")
    description: Optional[str] = Field(None, description="Descrição do negócio")
    primary_color: Optional[str] = Field("#007BFF", description="Cor primária do site")
    secondary_color: Optional[str] = Field("#6C757D", description="Cor secundária")

class ElementorTemplate(BaseModel):
    """Template Elementor para personalização"""
    name: str = Field(..., description="Nome do template")
    category: str = Field(..., description="Categoria (restaurant, services, etc)")
    elementor_json: Dict[str, Any] = Field(..., description="JSON exportado do Elementor")
    placeholders: List[str] = Field(default=[], description="Lista de placeholders encontrados")
    preview_image: Optional[str] = Field(None, description="URL da imagem de preview")
    description: Optional[str] = Field(None, description="Descrição do template")

class LandingPageGeneration(BaseModel):
    """Request para gerar landing page"""
    template_id: str = Field(..., description="ID do template a ser usado")
    business_info: BusinessInfo = Field(..., description="Informações do negócio")
    ai_enhancement: bool = Field(True, description="Usar IA para melhorar conteúdo")
    language: str = Field("pt-BR", description="Idioma do conteúdo")

class WordPressDeployment(BaseModel):
    """Deploy no WordPress"""
    landing_page_id: str = Field(..., description="ID da landing page gerada")
    wp_url: str = Field(..., description="URL do WordPress")
    wp_username: str = Field(..., description="Username WordPress")
    wp_password: str = Field(..., description="Senha ou Application Password")
    page_title: str = Field(..., description="Título da página")
    page_slug: Optional[str] = Field(None, description="Slug da página (opcional)")

# =============== STORAGE ===============
# Em produção, usar banco de dados
templates_storage = {}
landing_pages_storage = {}

# =============== UTILS ===============

def extract_placeholders(elementor_json: Dict[str, Any]) -> List[str]:
    """Extrai placeholders do JSON do Elementor"""
    placeholders = set()
    json_str = json.dumps(elementor_json)
    
    # Busca padrões como {{BUSINESS_NAME}}, {{PHONE}}, etc.
    matches = re.findall(r'\{\{([A-Z_]+)\}\}', json_str)
    placeholders.update(matches)
    
    return sorted(list(placeholders))

def get_agno_manager(request: Request):
    """Dependency to get Agno manager from request state"""
    return getattr(request.app.state, 'agno_manager', None)

def replace_placeholders(content: str, business_info: BusinessInfo) -> str:
    """Substitui placeholders pelo conteúdo do negócio"""
    replacements = {
        'BUSINESS_NAME': business_info.name,
        'PHONE': business_info.phone,
        'EMAIL': business_info.email or '',
        'ADDRESS': business_info.address or '',
        'SERVICES': business_info.services,
        'DESCRIPTION': business_info.description or f'Somos especialistas em {business_info.services}',
        'PRIMARY_COLOR': business_info.primary_color,
        'SECONDARY_COLOR': business_info.secondary_color,
        # Campos gerados automaticamente
        'WHATSAPP_LINK': f"https://wa.me/{business_info.phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')}",
        'CURRENT_YEAR': str(datetime.now().year),
    }
    
    result = content
    for placeholder, value in replacements.items():
        result = result.replace(f'{{{{{placeholder}}}}}', str(value))
    
    return result

# =============== ENDPOINTS ===============

@router.post("/templates/register")
async def register_template(template: ElementorTemplate):
    """
    Registra um novo template Elementor
    
    Você exporta o template do Elementor como JSON e envia aqui.
    O sistema identifica automaticamente os placeholders.
    """
    try:
        template_id = str(uuid.uuid4())
        
        # Extrai placeholders automaticamente
        placeholders = extract_placeholders(template.elementor_json)
        
        # Salva template
        template_data = {
            "id": template_id,
            "name": template.name,
            "category": template.category,
            "elementor_json": template.elementor_json,
            "placeholders": placeholders,
            "preview_image": template.preview_image,
            "description": template.description,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        templates_storage[template_id] = template_data
        
        logger.info(f"✅ Template registrado: {template.name} ({template_id})")
        
        return {
            "success": True,
            "template_id": template_id,
            "placeholders_found": placeholders,
            "message": f"Template '{template.name}' registrado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao registrar template: {str(e)}")

@router.get("/templates")
async def list_templates(category: Optional[str] = None):
    """Lista todos os templates disponíveis"""
    
    templates = list(templates_storage.values())
    
    if category:
        templates = [t for t in templates if t["category"] == category]
    
    return {
        "success": True,
        "total": len(templates),
        "templates": [{
            "id": t["id"],
            "name": t["name"],
            "category": t["category"],
            "placeholders": t["placeholders"],
            "preview_image": t.get("preview_image"),
            "description": t.get("description"),
            "created_at": t["created_at"]
        } for t in templates]
    }

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Obtém um template específico"""
    
    if template_id not in templates_storage:
        raise HTTPException(status_code=404, detail="Template não encontrado")
    
    return {
        "success": True,
        "template": templates_storage[template_id]
    }

@router.post("/landing/generate")
async def generate_landing_page(
    generation: LandingPageGeneration, 
    agno_manager=Depends(get_agno_manager)
):
    """
    Gera landing page personalizada usando IA
    
    1. Pega o template Elementor
    2. Usa IA para melhorar/gerar conteúdo
    3. Substitui placeholders
    4. Retorna JSON pronto para WordPress
    """
    try:
        # Verifica se template existe
        if generation.template_id not in templates_storage:
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        template = templates_storage[generation.template_id]
        landing_page_id = str(uuid.uuid4())
        
        logger.info(f"🤖 Gerando landing page para: {generation.business_info.name}")
        
        # 1. Melhorar conteúdo com IA (se disponível)
        enhanced_business_info = generation.business_info
        if generation.ai_enhancement:
            enhanced_business_info = await enhance_with_ai(generation.business_info, agno_manager)
        
        # 2. Substitui placeholders no JSON do Elementor
        elementor_json_str = json.dumps(template["elementor_json"])
        personalized_json_str = replace_placeholders(elementor_json_str, enhanced_business_info)
        personalized_json = json.loads(personalized_json_str)
        
        # 3. Salva landing page gerada
        landing_page_data = {
            "id": landing_page_id,
            "template_id": generation.template_id,
            "template_name": template["name"],
            "business_info": enhanced_business_info.model_dump(),
            "elementor_json": personalized_json,
            "generated_at": datetime.now().isoformat(),
            "status": "generated"
        }
        
        landing_pages_storage[landing_page_id] = landing_page_data
        
        logger.info(f"✅ Landing page gerada: {landing_page_id}")
        
        return {
            "success": True,
            "landing_page_id": landing_page_id,
            "business_name": enhanced_business_info.name,
            "template_used": template["name"],
            "preview_url": f"/api/v1/simple-landing/preview/{landing_page_id}",
            "elementor_json": personalized_json,
            "ai_enhanced": generation.ai_enhancement,
            "message": "Landing page gerada com sucesso!"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar landing page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar landing page: {str(e)}")

@router.get("/preview/{landing_page_id}")
async def preview_landing_page(landing_page_id: str):
    """Preview da landing page antes de publicar no WordPress"""
    
    if landing_page_id not in landing_pages_storage:
        raise HTTPException(status_code=404, detail="Landing page não encontrada")
    
    landing_page = landing_pages_storage[landing_page_id]
    
    return {
        "success": True,
        "landing_page": {
            "id": landing_page["id"],
            "business_name": landing_page["business_info"]["name"],
            "template_name": landing_page["template_name"],
            "generated_at": landing_page["generated_at"],
            "elementor_json": landing_page["elementor_json"]
        }
    }

@router.post("/wordpress/deploy")
async def deploy_to_wordpress(deployment: WordPressDeployment, background_tasks: BackgroundTasks):
    """
    Faz deploy da landing page no WordPress
    
    Envia o JSON do Elementor personalizado para o WordPress
    """
    try:
        # Verifica se landing page existe
        if deployment.landing_page_id not in landing_pages_storage:
            raise HTTPException(status_code=404, detail="Landing page não encontrada")
        
        landing_page = landing_pages_storage[deployment.landing_page_id]
        
        # Adiciona tarefa em background para deploy
        background_tasks.add_task(
            deploy_to_wp_background,
            landing_page,
            deployment
        )
        
        # Atualiza status
        landing_pages_storage[deployment.landing_page_id]["status"] = "deploying"
        landing_pages_storage[deployment.landing_page_id]["wp_deployment"] = {
            "wp_url": deployment.wp_url,
            "page_title": deployment.page_title,
            "page_slug": deployment.page_slug,
            "started_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "Deploy iniciado em background",
            "landing_page_id": deployment.landing_page_id,
            "estimated_time": "30-60 segundos",
            "status_url": f"/api/v1/simple-landing/status/{deployment.landing_page_id}"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar deploy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar deploy: {str(e)}")

@router.get("/status/{landing_page_id}")
async def get_landing_page_status(landing_page_id: str):
    """Verifica status do deploy"""
    
    if landing_page_id not in landing_pages_storage:
        raise HTTPException(status_code=404, detail="Landing page não encontrada")
    
    landing_page = landing_pages_storage[landing_page_id]
    
    return {
        "success": True,
        "status": landing_page["status"],
        "wp_deployment": landing_page.get("wp_deployment", {}),
        "generated_at": landing_page["generated_at"]
    }

@router.post("/test/complete-flow")
async def test_complete_flow(
    wp_url: str,
    wp_username: str,
    wp_password: str,
    agno_manager=Depends(get_agno_manager)
):
    """
    Teste completo do fluxo:
    1. Registra template de exemplo
    2. Gera landing page
    3. Faz deploy no WordPress
    """
    try:
        logger.info(f"🧪 Iniciando teste completo com WordPress: {wp_url}")
        
        # 1. Registrar template de exemplo
        sample_template = {
            "name": "Restaurante Teste",
            "category": "restaurant",
            "elementor_json": {
                "version": "3.0.0",
                "content": [
                    {
                        "id": "test-section",
                        "elType": "section",
                        "settings": {
                            "background_background": "classic",
                            "background_color": "{{PRIMARY_COLOR}}"
                        },
                        "elements": [
                            {
                                "id": "test-column",
                                "elType": "column",
                                "elements": [
                                    {
                                        "id": "test-heading",
                                        "elType": "widget",
                                        "widgetType": "heading",
                                        "settings": {
                                            "title": "{{BUSINESS_NAME}}",
                                            "size": "xxl"
                                        }
                                    },
                                    {
                                        "id": "test-text",
                                        "elType": "widget", 
                                        "widgetType": "text-editor",
                                        "settings": {
                                            "editor": "<p>{{DESCRIPTION}}</p><p>Telefone: {{PHONE}}</p>"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # Registrar template
        template_id = str(uuid.uuid4())
        placeholders = extract_placeholders(sample_template["elementor_json"])
        
        templates_storage[template_id] = {
            "id": template_id,
            "name": sample_template["name"],
            "category": sample_template["category"],
            "elementor_json": sample_template["elementor_json"],
            "placeholders": placeholders,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        logger.info(f"✅ Template de teste registrado: {template_id}")
        
        # 2. Gerar landing page
        business_info_data = {
            "name": "Restaurante Teste KenzySites",
            "phone": "+55 11 99999-9999",
            "email": "contato@restauranteteste.com",
            "address": "Rua dos Testes, 123 - São Paulo, SP",
            "services": "Comida italiana caseira e delivery",
            "description": "O melhor restaurante italiano da cidade",
            "primary_color": "#8B0000",
            "secondary_color": "#FFD700"
        }
        
        business_info = BusinessInfo(**business_info_data)
        enhanced_business_info = await enhance_with_ai(business_info, agno_manager)
        
        # Gerar landing page
        landing_page_id = str(uuid.uuid4())
        elementor_json_str = json.dumps(sample_template["elementor_json"])
        personalized_json_str = replace_placeholders(elementor_json_str, enhanced_business_info)
        personalized_json = json.loads(personalized_json_str)
        
        landing_page_data = {
            "id": landing_page_id,
            "template_id": template_id,
            "template_name": sample_template["name"],
            "business_info": enhanced_business_info.model_dump(),
            "elementor_json": personalized_json,
            "generated_at": datetime.now().isoformat(),
            "status": "generated"
        }
        
        landing_pages_storage[landing_page_id] = landing_page_data
        
        logger.info(f"✅ Landing page de teste gerada: {landing_page_id}")
        
        # 3. Deploy no WordPress
        deployment = WordPressDeployment(
            landing_page_id=landing_page_id,
            wp_url=wp_url,
            wp_username=wp_username,
            wp_password=wp_password,
            page_title=f"Landing Page Teste - {enhanced_business_info.name}",
            page_slug="teste-kenzysites"
        )
        
        # Executar deploy
        await deploy_to_wp_background(landing_page_data, deployment)
        
        # Verificar resultado
        final_status = landing_pages_storage[landing_page_id]
        
        return {
            "success": True,
            "message": "Teste completo executado!",
            "results": {
                "template_registered": {
                    "template_id": template_id,
                    "placeholders": placeholders
                },
                "landing_page_generated": {
                    "landing_page_id": landing_page_id,
                    "business_name": enhanced_business_info.name,
                    "ai_enhanced": True
                },
                "wordpress_deployment": {
                    "status": final_status["status"],
                    "wp_deployment": final_status.get("wp_deployment", {}),
                    "page_url": final_status.get("wp_deployment", {}).get("page_url"),
                    "edit_url": final_status.get("wp_deployment", {}).get("edit_url")
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Teste completo falhou: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Teste falhou: {str(e)}")

# =============== BACKGROUND TASKS ===============

async def enhance_with_ai(business_info: BusinessInfo, agno_manager=None) -> BusinessInfo:
    """Usa IA para melhorar informações do negócio"""
    try:
        if not agno_manager or not getattr(agno_manager, 'primary_model', None):
            # Fallback: apenas melhora descrição básica
            if not business_info.description:
                business_info.description = f"Somos especialistas em {business_info.services} com atendimento de qualidade e preços competitivos."
            return business_info
        
        # Usa IA para melhorar conteúdo
        prompt = f"""
        Melhore as informações deste negócio para uma landing page profissional:
        
        Nome: {business_info.name}
        Serviços: {business_info.services}
        Descrição atual: {business_info.description or 'Não fornecida'}
        
        Retorne APENAS uma descrição melhorada em até 150 caracteres, focada em conversão e benefícios para o cliente.
        Use tom profissional mas acessível. Foque nos benefícios únicos.
        """
        
        try:
            # Tenta usar o agno_manager para gerar conteúdo
            if hasattr(agno_manager, 'agents') and 'content_generator' in agno_manager.agents:
                result = await agno_manager.agents['content_generator'].generate_response(prompt)
                enhanced_description = str(result)[:150] if len(str(result)) > 150 else str(result)
                business_info.description = enhanced_description
                logger.info(f"✅ AI enhancement successful with Agno")
                return business_info
        except Exception as ai_error:
            logger.warning(f"⚠️ Agno AI enhancement failed: {ai_error}")
        
        # Fallback: descrição melhorada automaticamente
        enhanced_description = f"Especialistas em {business_info.services} com atendimento personalizado e resultados garantidos. Entre em contato e comprove a qualidade!"
        business_info.description = enhanced_description
        return business_info
        
    except Exception as e:
        logger.warning(f"⚠️ IA enhancement failed: {str(e)}, using fallback")
        if not business_info.description:
            business_info.description = f"Somos especialistas em {business_info.services} com atendimento de qualidade."
        return business_info

async def deploy_to_wp_background(landing_page: Dict[str, Any], deployment: WordPressDeployment):
    """Deploy em background para WordPress"""
    import aiohttp
    import base64
    
    try:
        logger.info(f"🚀 Iniciando deploy para WordPress: {deployment.wp_url}")
        
        landing_page_id = landing_page["id"]
        
        # Preparar dados para o WordPress
        wp_data = {
            "template_data": {
                "elementor_json": landing_page["elementor_json"]
            },
            "business_info": landing_page["business_info"],
            "page_title": deployment.page_title,
            "page_slug": deployment.page_slug
        }
        
        # Configurar headers de autenticação
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Se username/password fornecidos, usar Basic Auth
        if deployment.wp_username and deployment.wp_password:
            auth_string = base64.b64encode(
                f"{deployment.wp_username}:{deployment.wp_password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {auth_string}"
        
        # URL do endpoint REST do plugin
        wp_rest_url = f"{deployment.wp_url.rstrip('/')}/wp-json/kenzysites/v1/templates/receive"
        
        # Fazer request para o WordPress
        async with aiohttp.ClientSession() as session:
            async with session.post(
                wp_rest_url, 
                json=wp_data, 
                headers=headers,
                timeout=60
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("success"):
                        # Deploy bem-sucedido
                        if landing_page_id in landing_pages_storage:
                            landing_pages_storage[landing_page_id]["status"] = "deployed"
                            landing_pages_storage[landing_page_id]["wp_deployment"]["completed_at"] = datetime.now().isoformat()
                            landing_pages_storage[landing_page_id]["wp_deployment"]["page_url"] = result.get("page_url")
                            landing_pages_storage[landing_page_id]["wp_deployment"]["edit_url"] = result.get("edit_url")
                            landing_pages_storage[landing_page_id]["wp_deployment"]["wp_page_id"] = result.get("page_id")
                        
                        logger.info(f"✅ Deploy concluído: {landing_page_id} -> {result.get('page_url')}")
                    else:
                        raise Exception(f"WordPress API retornou erro: {result.get('error', 'Erro desconhecido')}")
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
        
    except Exception as e:
        logger.error(f"❌ Deploy falhou: {str(e)}")
        landing_page_id = landing_page["id"]
        if landing_page_id in landing_pages_storage:
            landing_pages_storage[landing_page_id]["status"] = "failed"
            landing_pages_storage[landing_page_id]["wp_deployment"]["error"] = str(e)