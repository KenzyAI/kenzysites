"""
Instant Site Generation API Router
ZipWP-inspired instant WordPress site generation with AI
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from app.services.agno_manager import AgnoManager
from app.models.ai_models import SiteGenerationRequest, AIResponse
from app.core.config import get_settings
from app.services.acf_integration import acf_service
from app.services.blueprint_manager import blueprint_manager

router = APIRouter(prefix="/instant", tags=["Instant Site Generation"])
logger = logging.getLogger(__name__)

# Global instance
agno_manager = AgnoManager()

@router.on_event("startup")
async def startup_instant_sites():
    """Initialize instant site generation system"""
    try:
        await agno_manager.initialize()
        logger.info("✅ Instant site generation system initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize instant site system: {str(e)}")

@router.post("/generate")
async def generate_instant_site(
    request: SiteGenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "demo_user",  # In production, get from auth
    user_plan: str = "pro"       # In production, get from user data
) -> JSONResponse:
    """
    Generate complete WordPress site instantly (< 60s)
    
    Inspired by ZipWP's rapid site generation approach:
    - Business context analysis
    - Brazilian market features
    - Dynamic content generation
    - Elementor + ACF integration
    - Complete deployment package
    """
    
    try:
        logger.info(f"🚀 Starting instant site generation for: {request.business_name}")
        
        # Validate request
        if not request.business_name or not request.industry:
            raise HTTPException(
                status_code=400,
                detail="Business name and industry are required"
            )
        
        # Generate site instantly
        result = await agno_manager.generate_instant_site(
            request=request,
            user_id=user_id,
            user_plan=user_plan
        )
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.message
            )
        
        # Schedule background tasks
        background_tasks.add_task(
            _post_generation_tasks,
            result.content["generation_id"],
            user_id
        )
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": result.message,
                "generation_time": result.content["generation_time"],
                "generation_id": result.content["generation_id"],
                "preview_url": result.content["success_url"],
                "credits_used": result.credits_used,
                "site_data": {
                    "structure": result.content["site_structure"],
                    "design_system": result.content["design_system"],
                    "brazilian_features": result.content["brazilian_features"],
                    "deployment_instructions": result.content["deployment_instructions"],
                    "validation_score": result.content["validation_results"].get("overall_score", 0)
                },
                "download_links": {
                    "wordpress_package": f"/api/instant/download/{result.content['generation_id']}/wordpress",
                    "elementor_templates": f"/api/instant/download/{result.content['generation_id']}/elementor",
                    "acf_configuration": f"/api/instant/download/{result.content['generation_id']}/acf"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Instant site generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/generate-minimal")
async def generate_minimal_site(
    business_name: str,
    industry: str,
    description: Optional[str] = None,
    user_id: str = "demo_user"
) -> JSONResponse:
    """
    Generate minimal site with just business name and industry
    Ultra-fast generation for quick prototyping
    """
    
    try:
        # Create minimal request
        minimal_request = SiteGenerationRequest(
            business_name=business_name,
            industry=industry,
            business_type="service",
            business_description=description or f"Professional {industry} services",
            services=["Consultation", "Professional Services"],
            target_audience="General customers"
        )
        
        # Generate site with reduced complexity
        result = await agno_manager.generate_instant_site(
            request=minimal_request,
            user_id=user_id,
            user_plan="basic"
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Minimal site generated in {result.content['generation_time']:.1f}s",
                "preview_url": result.content["success_url"],
                "generation_time": result.content["generation_time"],
                "features": [
                    "WordPress site with Astra theme",
                    "Elementor page builder integration",
                    "ACF custom fields configured",
                    "Brazilian market features",
                    "Mobile responsive design",
                    "SEO optimized"
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Minimal site generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{generation_id}")
async def preview_generated_site(generation_id: str):
    """
    Preview the generated site
    Returns HTML preview or redirect to hosted preview
    """
    
    try:
        # In a real implementation, this would:
        # 1. Fetch generation data from database
        # 2. Render preview using stored templates
        # 3. Return HTML or redirect to preview URL
        
        preview_html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Site Preview - {generation_id}</title>
            <style>
                body {{ font-family: Inter, sans-serif; margin: 0; padding: 20px; }}
                .preview-container {{ max-width: 1200px; margin: 0 auto; }}
                .hero {{ background: linear-gradient(135deg, #0066FF, #00D4FF); color: white; padding: 60px 20px; text-align: center; }}
                .content {{ padding: 40px 20px; }}
                .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 40px 0; }}
                .feature {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .footer {{ background: #0A0E27; color: white; padding: 40px 20px; text-align: center; }}
                .btn {{ background: #0066FF; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="preview-container">
                <div class="hero">
                    <h1>🚀 Site Generated Successfully!</h1>
                    <p>Your WordPress site was created in under 60 seconds</p>
                    <button class="btn">Download Site Package</button>
                </div>
                
                <div class="content">
                    <h2>What's Included:</h2>
                    <div class="features">
                        <div class="feature">
                            <h3>📱 Complete WordPress Site</h3>
                            <p>Full WordPress installation with Astra theme and Elementor</p>
                        </div>
                        <div class="feature">
                            <h3>🇧🇷 Brazilian Features</h3>
                            <p>WhatsApp integration, PIX payment, LGPD compliance</p>
                        </div>
                        <div class="feature">
                            <h3>⚡ ACF Fields</h3>
                            <p>Custom fields configured for dynamic content</p>
                        </div>
                        <div class="feature">
                            <h3>🎨 Elementor Templates</h3>
                            <p>Professional page layouts with dynamic content</p>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Generated by KenzySites AI • Generation ID: {generation_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return JSONResponse(
            status_code=200,
            content={"html": preview_html, "generation_id": generation_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Preview not found")

@router.get("/download/{generation_id}/{package_type}")
async def download_site_package(generation_id: str, package_type: str):
    """
    Download specific package components
    
    package_type options:
    - wordpress: Complete WordPress files
    - elementor: Elementor templates and data
    - acf: ACF field configurations
    - complete: Full site package
    """
    
    try:
        if package_type not in ["wordpress", "elementor", "acf", "complete"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid package type"
            )
        
        # In production, this would fetch from storage and return actual files
        download_info = {
            "generation_id": generation_id,
            "package_type": package_type,
            "download_url": f"/downloads/{generation_id}/{package_type}.zip",
            "size": "2.5MB",
            "files_included": _get_package_files(package_type),
            "expires_at": (datetime.now().timestamp() + 3600 * 24)  # 24 hours
        }
        
        return JSONResponse(content=download_info)
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Package not found")

@router.get("/status/{generation_id}")
async def get_generation_status(generation_id: str):
    """
    Get status of site generation
    Useful for long-running generations or background processing
    """
    
    try:
        # Mock status - in production, fetch from database/cache
        status_info = {
            "generation_id": generation_id,
            "status": "completed",
            "progress": 100,
            "current_phase": "deployment_ready",
            "generation_time": 45.2,
            "created_at": datetime.now().isoformat(),
            "phases": [
                {"name": "Analysis & Setup", "completed": True, "duration": 4.1},
                {"name": "Content & Design", "completed": True, "duration": 18.3},
                {"name": "WordPress & Templates", "completed": True, "duration": 15.8},
                {"name": "Assembly & Personalization", "completed": True, "duration": 5.2},
                {"name": "Quality Check", "completed": True, "duration": 1.8}
            ]
        }
        
        return JSONResponse(content=status_info)
        
    except Exception as e:
        raise HTTPException(status_code=404, detail="Generation not found")

@router.post("/personalize/{generation_id}")
async def personalize_generated_site(
    generation_id: str,
    personalization_data: Dict[str, Any]
):
    """
    Apply additional personalization to generated site
    Allows customization after initial generation
    """
    
    try:
        # Use ContentPersonalizationAgent for additional customization
        personalization_agent = agno_manager.specialized_agents.get("content_personalization")
        
        if not personalization_agent:
            raise HTTPException(
                status_code=503,
                detail="Personalization service not available"
            )
        
        # Apply personalization
        result = personalization_agent.personalize_content(
            "[BUSINESS_NAME] offers [SERVICES] with [UNIQUE_VALUE]",
            personalization_data
        )
        
        return JSONResponse(
            content={
                "success": True,
                "generation_id": generation_id,
                "personalization_score": result["personalization_score"],
                "improvements": result["improvements"],
                "updated_content": result["personalized_content"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/brazilian/{industry}")
async def get_brazilian_templates(industry: str):
    """
    Get Brazilian-specific templates for an industry
    """
    
    try:
        from app.models.template_models import BRAZILIAN_INDUSTRIES
        
        if industry not in BRAZILIAN_INDUSTRIES:
            raise HTTPException(
                status_code=404,
                detail=f"No Brazilian template found for industry: {industry}"
            )
        
        template = BRAZILIAN_INDUSTRIES[industry]
        
        return JSONResponse(
            content={
                "industry": industry,
                "template": {
                    "name": template.industry_name,
                    "description": template.description,
                    "features": {
                        "whatsapp_integration": template.whatsapp_integration,
                        "pix_payment": template.pix_payment,
                        "lgpd_compliance": template.lgpd_notice,
                        "cpf_field": template.cpf_field,
                        "cnpj_field": template.cnpj_field,
                        "delivery_areas": template.delivery_areas,
                        "specific_features": template.specific_features
                    }
                },
                "recommended_plugins": _get_industry_plugins(industry),
                "estimated_generation_time": "45-60 seconds"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _post_generation_tasks(generation_id: str, user_id: str):
    """Background tasks after site generation"""
    try:
        logger.info(f"🔄 Running post-generation tasks for {generation_id}")
        
        # Tasks that could run in background:
        # 1. Generate additional content variations
        # 2. Create backup/restore points
        # 3. Send email notification
        # 4. Update user statistics
        # 5. Cache optimization
        
        logger.info(f"✅ Post-generation tasks completed for {generation_id}")
        
    except Exception as e:
        logger.error(f"❌ Post-generation tasks failed: {str(e)}")

def _get_package_files(package_type: str) -> list:
    """Get list of files included in package"""
    
    files_map = {
        "wordpress": [
            "wp-config.php",
            "functions.php", 
            "style.css",
            "header.php",
            "footer.php",
            "index.php"
        ],
        "elementor": [
            "elementor-templates.json",
            "page-layouts.json",
            "widget-configurations.json"
        ],
        "acf": [
            "acf-export.json",
            "field-groups.json",
            "wp-cli-commands.sh"
        ],
        "complete": [
            "wordpress-package.zip",
            "elementor-templates.zip", 
            "acf-configuration.zip",
            "deployment-script.sh",
            "README.md"
        ]
    }
    
    return files_map.get(package_type, [])

def _get_industry_plugins(industry: str) -> list:
    """Get recommended plugins for industry"""
    
    plugin_map = {
        "restaurante": [
            "woocommerce",
            "restaurant-reservations",
            "menu-ordering-reservations",
            "wp-food-manager"
        ],
        "saude": [
            "appointment-booking-calendar",
            "medical-wp",
            "patient-manager",
            "gdpr-compliance"
        ],
        "ecommerce": [
            "woocommerce",
            "yoast-seo",
            "mailchimp-for-wp",
            "jetpack"
        ]
    }
    
    return plugin_map.get(industry, [
        "elementor",
        "advanced-custom-fields-pro", 
        "yoast-seo",
        "wordfence"
    ])

@router.get("/blueprints")
async def list_available_blueprints(
    blueprint_type: Optional[str] = None,
    industry: Optional[str] = None,
    complexity: Optional[str] = None
):
    """
    List available blueprints with optional filters
    """
    
    try:
        from app.services.blueprint_manager import BlueprintType, BlueprintComplexity
        
        # Convert string parameters to enums if provided
        type_filter = None
        if blueprint_type:
            try:
                type_filter = BlueprintType(blueprint_type)
            except ValueError:
                pass
        
        complexity_filter = None
        if complexity:
            try:
                complexity_filter = BlueprintComplexity(complexity)
            except ValueError:
                pass
        
        blueprints = blueprint_manager.list_blueprints(
            blueprint_type=type_filter,
            industry=industry,
            complexity=complexity_filter
        )
        
        blueprint_summaries = []
        for blueprint in blueprints:
            summary = blueprint_manager.get_blueprint_summary(blueprint.id)
            blueprint_summaries.append(summary)
        
        return JSONResponse(
            content={
                "success": True,
                "blueprints": blueprint_summaries,
                "total": len(blueprint_summaries),
                "filters_applied": {
                    "type": blueprint_type,
                    "industry": industry,
                    "complexity": complexity
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blueprints/{blueprint_id}")
async def get_blueprint_details(blueprint_id: str):
    """
    Get detailed information about a specific blueprint
    """
    
    try:
        blueprint = blueprint_manager.get_blueprint(blueprint_id)
        
        if not blueprint:
            raise HTTPException(
                status_code=404,
                detail=f"Blueprint {blueprint_id} not found"
            )
        
        return JSONResponse(
            content={
                "success": True,
                "blueprint": {
                    "id": blueprint.id,
                    "name": blueprint.name,
                    "description": blueprint.description,
                    "type": blueprint.type,
                    "category": blueprint.category,
                    "complexity": blueprint.complexity,
                    "industry": blueprint.industry,
                    "target_audience": blueprint.target_audience,
                    "pages": blueprint.pages,
                    "navigation": blueprint.navigation,
                    "features": blueprint.features,
                    "required_fields": blueprint.required_fields,
                    "optional_fields": blueprint.optional_fields,
                    "wordpress_theme": blueprint.wordpress_theme,
                    "required_plugins": blueprint.required_plugins,
                    "brazilian_features": blueprint.brazilian_features,
                    "estimated_generation_time": blueprint.estimated_generation_time,
                    "credits_cost": blueprint.credits_cost,
                    "rating": blueprint.rating,
                    "usage_count": blueprint.usage_count,
                    "version": blueprint.version
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-from-blueprint/{blueprint_id}")
async def generate_site_from_blueprint(
    blueprint_id: str,
    business_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    user_id: str = "demo_user",
    user_plan: str = "pro"
):
    """
    Generate site using a specific blueprint
    """
    
    try:
        # Get blueprint
        blueprint = blueprint_manager.get_blueprint(blueprint_id)
        if not blueprint:
            raise HTTPException(
                status_code=404,
                detail=f"Blueprint {blueprint_id} not found"
            )
        
        # Validate required fields
        missing_fields = []
        for field in blueprint.required_fields:
            if field not in business_data or not business_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Create site generation request from blueprint and business data
        site_request = SiteGenerationRequest(
            business_name=business_data.get("business_name", ""),
            industry=blueprint.industry,
            business_type=blueprint.type.value,
            business_description=business_data.get("business_description", ""),
            services=business_data.get("services", []),
            target_audience=business_data.get("target_audience", blueprint.target_audience[0])
        )
        
        # Add blueprint-specific data to request
        for field_name, field_value in business_data.items():
            setattr(site_request, field_name, field_value)
        
        # Generate site using the blueprint
        result = await agno_manager.generate_instant_site(
            request=site_request,
            user_id=user_id,
            user_plan=user_plan
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        # Increment blueprint usage
        blueprint_manager.increment_usage(blueprint_id)
        
        # Add blueprint information to result
        result.content["blueprint_used"] = {
            "id": blueprint.id,
            "name": blueprint.name,
            "version": blueprint.version
        }
        
        # Schedule background tasks
        background_tasks.add_task(
            _post_generation_tasks,
            result.content["generation_id"],
            user_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Site generated using blueprint '{blueprint.name}' in {result.content['generation_time']:.1f}s",
                "generation_id": result.content["generation_id"],
                "blueprint_used": result.content["blueprint_used"],
                "preview_url": result.content["success_url"],
                "generation_time": result.content["generation_time"],
                "credits_used": result.credits_used,
                "features_included": blueprint.features
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Blueprint generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend-blueprint")
async def recommend_blueprint(industry: str, business_type: str):
    """
    Get recommended blueprint for industry and business type
    """
    
    try:
        recommended = blueprint_manager.get_recommended_blueprint(industry, business_type)
        
        if not recommended:
            raise HTTPException(
                status_code=404,
                detail=f"No blueprint found for industry '{industry}' and business type '{business_type}'"
            )
        
        summary = blueprint_manager.get_blueprint_summary(recommended.id)
        
        return JSONResponse(
            content={
                "success": True,
                "recommended_blueprint": summary,
                "match_reason": f"Best match for {industry} industry",
                "confidence": 0.95 if industry in ["restaurante", "saude", "ecommerce"] else 0.75
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo")
async def demo_instant_generation():
    """
    Demo endpoint to showcase the instant generation system
    """
    
    try:
        demo_data = {
            "system_overview": {
                "name": "KenzySites Instant Generation System",
                "description": "Sistema de geração instantânea de sites WordPress inspirado no ZipWP",
                "generation_time": "< 60 segundos",
                "supported_industries": ["restaurante", "saude", "ecommerce", "geral"],
                "features": [
                    "Geração instantânea com IA",
                    "Templates específicos para o Brasil",
                    "Integração WhatsApp + PIX",
                    "Compliance LGPD automático",
                    "ACF + Elementor integrados",
                    "WordPress real (sem lock-in)"
                ]
            },
            "specialized_agents": {
                "content_personalization": "Personalização dinâmica de conteúdo",
                "brazilian_market": "Recursos específicos do mercado brasileiro",
                "elementor_integration": "Integração seamless com Elementor",
                "site_architect": "Arquitetura de sites otimizada",
                "design_system": "Sistema de design consistente",
                "seo_optimization": "Otimização SEO automática",
                "wordpress_generation": "Geração de código WordPress",
                "quality_assurance": "Validação e testes automáticos"
            },
            "blueprint_system": {
                "available_blueprints": len(blueprint_manager.blueprints),
                "blueprint_types": ["restaurant", "healthcare", "ecommerce", "business"],
                "complexity_levels": ["simple", "standard", "advanced"],
                "customization_options": "Completa personalização via ACF"
            },
            "brazilian_features": {
                "whatsapp_integration": "Botão flutuante + integração completa",
                "pix_payment": "Pagamento instantâneo configurado",
                "lgpd_compliance": "Compliance automático com LGPD",
                "local_seo": "SEO otimizado para Brasil",
                "delivery_integration": "iFood, Uber Eats, Rappi",
                "marketplace_integration": "Mercado Livre, Magazine Luiza"
            },
            "generation_process": {
                "phase_1": "Análise & Setup (0-5s)",
                "phase_2": "Conteúdo & Design (5-25s)", 
                "phase_3": "WordPress & Templates (25-45s)",
                "phase_4": "Assembly & Personalização (45-55s)",
                "phase_5": "Quality Check & Package (55-60s)"
            },
            "demo_endpoints": {
                "generate_minimal": "/api/instant/generate-minimal",
                "generate_full": "/api/instant/generate",
                "list_blueprints": "/api/instant/blueprints",
                "recommend_blueprint": "/api/instant/recommend-blueprint",
                "preview_site": "/api/instant/preview/{generation_id}"
            },
            "example_usage": {
                "minimal_generation": {
                    "method": "POST",
                    "url": "/api/instant/generate-minimal",
                    "body": {
                        "business_name": "Restaurante do João",
                        "industry": "restaurante",
                        "description": "Comida caseira com delivery"
                    }
                },
                "blueprint_generation": {
                    "method": "POST", 
                    "url": "/api/instant/generate-from-blueprint/restaurant_complete_2025",
                    "body": {
                        "business_name": "Pizzaria Italiana",
                        "phone_number": "(11) 99999-9999",
                        "whatsapp_number": "(11) 99999-9999",
                        "address": "Rua das Pizzas, 123",
                        "opening_hours": "Ter-Dom: 18h às 23h",
                        "specialty": "Pizza italiana artesanal"
                    }
                }
            }
        }
        
        return JSONResponse(content=demo_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))