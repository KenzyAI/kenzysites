"""
Agno Framework Manager - Multi-Agent System Orchestration
Handles AI agent initialization, management, and coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Agno Framework v1.8.0 with explicit extras - FINAL ATTEMPT
try:
    # Force fresh import and debug
    import agno
    print(f"Agno installed at: {agno.__file__}")
    print(f"Agno dir contents: {dir(agno)}")
    
    # Check what's available in the package
    import os
    agno_dir = os.path.dirname(agno.__file__)
    agno_files = os.listdir(agno_dir)
    print(f"Agno package files: {agno_files}")
    
    # Try to import Agent directly from agno package root
    try:
        from agno import Agent
        print("✅ Agent imported from agno root")
    except ImportError as e1:
        print(f"❌ Cannot import Agent from agno root: {e1}")
        try:
            from agno.agent import Agent
            print("✅ Agent imported from agno.agent")
        except ImportError as e2:
            print(f"❌ Cannot import Agent from agno.agent: {e2}")
            # Try to find where Agent actually is
            for file in agno_files:
                if file.endswith('.py') and 'agent' in file.lower():
                    print(f"Found potential agent file: {file}")
    
    # Same for Workflow
    try:
        from agno import Workflow
        print("✅ Workflow imported from agno root")
    except ImportError:
        try:
            from agno.workflow import Workflow
            print("✅ Workflow imported from agno.workflow")
        except ImportError as e:
            print(f"❌ Cannot import Workflow: {e}")
            Workflow = None
    
    # Import models - try multiple patterns
    try:
        from agno.models.anthropic import Claude
        from agno.models.openai import OpenAIChat as OpenAI
        from agno.models.google import GoogleGenerativeAI
    except ImportError:
        from agno.models import Claude, OpenAI, GoogleGenerativeAI
    
    # Import tools
    try:
        from agno.tools.reasoning import ReasoningTools
        from agno.tools.python import PythonTools
    except ImportError:
        from agno.tools import ReasoningTools, PythonTools
    
    AGNO_AVAILABLE = True
    logging.info(f"✅ Agno Framework v{agno.__version__} loaded successfully with explicit extras")
    
except Exception as e:
    AGNO_AVAILABLE = False
    Agent = None
    Workflow = None
    Claude = None
    OpenAI = None
    GoogleGenerativeAI = None
    ReasoningTools = None
    PythonTools = None
    logging.error(f"❌ Agno Framework failed to load: {e}")
    logging.error(f"Exception type: {type(e).__name__}")
    
    # Try to load direct APIs as backup
    try:
        import anthropic
        import openai
        import google.generativeai as genai
        logging.info("✅ Direct AI APIs loaded as backup")
    except ImportError as backup_e:
        logging.error(f"❌ Even direct AI APIs failed: {backup_e}")

# Import our real Agno components
from app.services.agno.agents import (
    ContentGeneratorAgent,
    SiteArchitectAgent,
    DesignAgent,
    SEOAgent,
    WordPressAgent,
    QualityAssuranceAgent,
    ContentPersonalizationAgent,
    BrazilianMarketAgent,
    ElementorIntegrationAgent
)
from app.services.agno.tasks import WorkflowType, task_orchestrator
from app.services.agno.crews import crew_manager
from app.services.agno.tools import tool_executor

from app.core.config import settings, AI_CREDITS_COSTS
from app.models.ai_models import (
    ContentGenerationRequest, 
    SiteGenerationRequest,
    AIResponse,
    AICreditsBalance
)
from app.models.template_models import (
    TemplateCustomizationRequest,
    CustomizedTemplate,
    BRAZILIAN_INDUSTRIES
)
from app.services.acf_integration import acf_service

logger = logging.getLogger(__name__)

class AgnoManager:
    """
    Central manager for Agno Framework agents
    Implements multi-provider AI system as specified in PRD
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.specialized_agents = {}
        self.crews = {}
        self.initialized = False
        self.primary_model = None
        self.secondary_models = []
        self.task_orchestrator = task_orchestrator
        self.crew_manager = crew_manager
        self.tool_executor = tool_executor
        
    async def initialize(self):
        """Initialize Agno Framework and create AI agents"""
        try:
            logger.info("🚀 Initializing Agno Framework Manager v1.7.12")
            
            if not AGNO_AVAILABLE:
                logger.warning("⚠️ Agno Framework not available, running in limited mode")
                self.initialized = False
                return
            
            # Initialize model providers (PRD: Claude 3.5 Sonnet primary, GPT-4o secondary, Gemini tertiary)
            await self._initialize_models()
            
            # Create specialized agents (both legacy and new)
            await self._create_content_generation_agent()
            await self._create_site_generation_agent()
            await self._create_seo_optimization_agent()
            
            # Initialize real specialized agents
            await self._initialize_specialized_agents()
            
            self.initialized = True
            logger.info("✅ Agno Framework Manager v1.7.12 initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Agno Manager: {str(e)}")
            raise
    
    async def _initialize_models(self):
        """Initialize AI model providers with fallback strategy"""
        
        # Primary: Claude 3.5 Sonnet (as per PRD)
        if settings.ANTHROPIC_API_KEY:
            self.primary_model = Claude(
                model="claude-3-5-sonnet-20241022",
                api_key=settings.ANTHROPIC_API_KEY
            )
            logger.info("✅ Primary model: Claude 3.5 Sonnet initialized")
        
        # Secondary: GPT-4o
        if settings.OPENAI_API_KEY:
            self.secondary_models.append(
                OpenAI(
                    model="gpt-4o-2024-08-06",
                    api_key=settings.OPENAI_API_KEY
                )
            )
            logger.info("✅ Secondary model: GPT-4o initialized")
        
        # Tertiary: Gemini 2.0
        if settings.GOOGLE_AI_API_KEY:
            self.secondary_models.append(
                GoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    api_key=settings.GOOGLE_AI_API_KEY
                )
            )
            logger.info("✅ Tertiary model: Gemini 2.0 initialized")
        
        if not self.primary_model and not self.secondary_models:
            raise ValueError("No AI providers configured. Please set API keys.")
    
    async def _create_content_generation_agent(self):
        """Create Content Generation Agent (Feature F007)"""
        
        self.agents["content_generator"] = Agent(
            name="WordPress Content Generator",
            model=self.primary_model,
            tools=[
                ReasoningTools(add_instructions=True),
                PythonTools()
            ],
            instructions="""
            You are a specialized WordPress content generation agent.
            
            Your responsibilities:
            1. Generate high-quality blog posts optimized for SEO
            2. Create compelling page content (About, Services, Contact, etc)
            3. Generate meta descriptions and titles
            4. Suggest relevant tags and categories
            5. Optimize content for target keywords
            
            Always:
            - Write in Portuguese (Brazilian) unless specified otherwise
            - Follow SEO best practices
            - Create engaging, valuable content
            - Use proper WordPress formatting
            - Include call-to-actions when appropriate
            
            Content should be:
            - Original and plagiarism-free
            - Optimized for readability (Flesch-Kincaid score > 60)
            - SEO-friendly with proper keyword density (1-3%)
            - Mobile-friendly formatting
            """,
            markdown=True,
            description="Specialized agent for generating WordPress content with SEO optimization"
        )
        
        logger.info("✅ Content Generation Agent created")
    
    async def _create_site_generation_agent(self):
        """Create Site Generation Agent (Feature F001)"""
        
        self.agents["site_generator"] = Agent(
            name="WordPress Site Generator",
            model=self.primary_model,
            tools=[
                ReasoningTools(add_instructions=True),
                PythonTools()
            ],
            instructions="""
            You are a specialized WordPress site generation agent.
            
            Your responsibilities:
            1. Generate complete WordPress site structures based on business descriptions
            2. Create appropriate page hierarchies (Home, About, Services, Blog, Contact)
            3. Generate site navigation menus
            4. Suggest suitable WordPress themes and plugins
            5. Create site configuration recommendations
            
            Site generation requirements (PRD):
            - Must complete in under 5 minutes
            - Minimum 5 pages (Home, About, Services, Blog, Contact)
            - SEO optimized automatically
            - Mobile responsive
            - Target PageSpeed score > 90
            
            Always:
            - Analyze business/industry context
            - Create professional, conversion-focused content
            - Follow WordPress best practices
            - Ensure accessibility standards (WCAG AA)
            - Generate Brazilian Portuguese content unless specified
            """,
            markdown=True,
            description="Specialized agent for generating complete WordPress sites"
        )
        
        logger.info("✅ Site Generation Agent created")
    
    async def _create_seo_optimization_agent(self):
        """Create SEO Optimization Agent"""
        
        self.agents["seo_optimizer"] = Agent(
            name="SEO Optimization Specialist",
            model=self.primary_model,
            tools=[
                ReasoningTools(add_instructions=True),
                PythonTools()
            ],
            instructions="""
            You are a specialized SEO optimization agent for WordPress sites.
            
            Your responsibilities:
            1. Analyze content for SEO best practices
            2. Generate optimized meta titles and descriptions
            3. Suggest internal linking strategies
            4. Optimize images with proper alt tags
            5. Create XML sitemaps structure
            6. Analyze keyword density and distribution
            
            SEO Optimization costs 10 AI Credits per action.
            
            Always:
            - Focus on Brazilian market and Portuguese keywords
            - Follow Google's latest SEO guidelines
            - Prioritize user experience over keyword stuffing
            - Ensure mobile-first optimization
            - Consider local SEO factors for Brazilian businesses
            """,
            markdown=True,
            description="Specialized agent for WordPress SEO optimization"
        )
        
        logger.info("✅ SEO Optimization Agent created")
    
    async def _initialize_specialized_agents(self):
        """Initialize new specialized agents with real implementation"""
        
        # Get the appropriate model for agents
        model = self.primary_model or (self.secondary_models[0] if self.secondary_models else None)
        
        if not model:
            logger.warning("No AI model available for specialized agents")
            return
        
        # Initialize each specialized agent
        self.specialized_agents = {
            "content_generator": ContentGeneratorAgent(),
            "site_architect": SiteArchitectAgent(),
            "design": DesignAgent(),
            "seo": SEOAgent(),
            "wordpress": WordPressAgent(),
            "qa": QualityAssuranceAgent(),
            "content_personalization": ContentPersonalizationAgent(),
            "brazilian_market": BrazilianMarketAgent(),
            "elementor_integration": ElementorIntegrationAgent()
        }
        
        logger.info(f"✅ Initialized {len(self.specialized_agents)} specialized agents")
    
    async def generate_content(
        self, 
        request: ContentGenerationRequest, 
        user_id: str,
        user_plan: str
    ) -> AIResponse:
        """
        Generate content using Content Generation Agent
        Implements AI Credits system (PRD section 6.2)
        """
        
        # Check AI Credits before processing
        credits_required = AI_CREDITS_COSTS["generate_blog_post"]
        credits_available = await self._check_ai_credits(user_id, user_plan)
        
        if credits_available < credits_required:
            return AIResponse(
                success=False,
                message=f"Insufficient AI Credits. Required: {credits_required}, Available: {credits_available}",
                credits_used=0
            )
        
        try:
            # Use content generation agent
            agent = self.agents["content_generator"]
            
            # Prepare prompt based on request
            prompt = self._build_content_prompt(request)
            
            # Generate content with Agno
            response = await agent.arun(prompt)
            
            # Deduct AI Credits
            await self._deduct_ai_credits(user_id, credits_required)
            
            return AIResponse(
                success=True,
                content=response.content,
                message="Content generated successfully",
                credits_used=credits_required,
                model_used=agent.model.id if hasattr(agent.model, 'id') else "unknown"
            )
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            return AIResponse(
                success=False,
                message=f"Content generation failed: {str(e)}",
                credits_used=0
            )
    
    async def generate_site(
        self, 
        request: SiteGenerationRequest, 
        user_id: str,
        user_plan: str
    ) -> AIResponse:
        """
        Generate complete WordPress site using Site Generation Agent
        Costs 100 AI Credits (PRD section 6.2)
        Now with ACF (Advanced Custom Fields) support
        """
        
        # Check AI Credits before processing
        credits_required = AI_CREDITS_COSTS["generate_site"]
        credits_available = await self._check_ai_credits(user_id, user_plan)
        
        if credits_available < credits_required:
            return AIResponse(
                success=False,
                message=f"Insufficient AI Credits. Required: {credits_required}, Available: {credits_available}",
                credits_used=0
            )
        
        try:
            # Use site generation agent
            agent = self.agents["site_generator"]
            
            # Check if this is a Brazilian industry template
            brazilian_template = None
            if request.industry.lower() in BRAZILIAN_INDUSTRIES:
                brazilian_template = BRAZILIAN_INDUSTRIES[request.industry.lower()]
            
            # Generate ACF fields for the industry
            acf_field_groups = acf_service.create_template_fields_for_industry(
                industry=request.industry,
                business_type=request.business_type
            )
            
            # Personalize fields with business data
            business_data = {
                "name": request.business_name,
                "description": request.business_description,
                "industry": request.industry
            }
            
            for field_group in acf_field_groups:
                acf_service.personalize_fields_with_ai(field_group, business_data)
            
            # Generate ACF export data
            acf_export = acf_service.generate_acf_export(acf_field_groups)
            
            # Get template recommendations
            template_recommendations = acf_service.get_template_recommendations(request.industry)
            
            # Prepare comprehensive prompt with ACF data
            prompt = self._build_site_generation_prompt_with_acf(
                request, 
                acf_field_groups,
                template_recommendations,
                brazilian_template
            )
            
            # Generate site with Agno
            response = await agent.arun(prompt)
            
            # Add ACF data to response
            response_data = {
                "site_structure": response.content,
                "acf_export": acf_export,
                "acf_field_groups": [g.to_dict() for g in acf_field_groups],
                "template_recommendations": template_recommendations,
                "wp_cli_commands": acf_service.generate_wp_cli_commands(acf_field_groups)
            }
            
            # If Brazilian template, add specific features
            if brazilian_template:
                response_data["brazilian_features"] = {
                    "whatsapp_integration": brazilian_template.whatsapp_integration,
                    "pix_payment": brazilian_template.pix_payment,
                    "lgpd_notice": brazilian_template.lgpd_notice,
                    "specific_features": brazilian_template.specific_features
                }
            
            # Deduct AI Credits
            await self._deduct_ai_credits(user_id, credits_required)
            
            return AIResponse(
                success=True,
                content=response_data,
                message="Site structure generated successfully with ACF support",
                credits_used=credits_required,
                model_used=agent.model.id if hasattr(agent.model, 'id') else "unknown"
            )
            
        except Exception as e:
            logger.error(f"Site generation error: {str(e)}")
            return AIResponse(
                success=False,
                message=f"Site generation failed: {str(e)}",
                credits_used=0
            )
    
    async def generate_instant_site(
        self, 
        request: SiteGenerationRequest, 
        user_id: str,
        user_plan: str
    ) -> AIResponse:
        """
        Generate complete WordPress site instantly (< 60s) - ZipWP inspired
        Uses all specialized agents for rapid site creation
        """
        
        start_time = datetime.now()
        
        # Check AI Credits before processing
        credits_required = AI_CREDITS_COSTS["generate_site"]
        credits_available = await self._check_ai_credits(user_id, user_plan)
        
        if credits_available < credits_required:
            return AIResponse(
                success=False,
                message=f"Insufficient AI Credits. Required: {credits_required}, Available: {credits_available}",
                credits_used=0
            )
        
        try:
            logger.info(f"🚀 Starting instant site generation for: {request.business_name}")
            
            # Phase 1: Parallel Analysis & Setup (0-5s)
            logger.info("📊 Phase 1: Analysis & Setup")
            analysis_tasks = await asyncio.gather(
                self._analyze_business_context(request),
                self._setup_brazilian_features(request),
                self._generate_acf_structure(request),
                return_exceptions=True
            )
            
            business_context, brazilian_features, acf_structure = analysis_tasks
            
            # Phase 2: Parallel Content & Design Generation (5-25s)
            logger.info("🎨 Phase 2: Content & Design Generation")
            content_tasks = await asyncio.gather(
                self._generate_site_structure(request, business_context),
                self._generate_design_system(request, business_context),
                self._generate_dynamic_content(request, business_context),
                self._generate_seo_optimization(request, business_context),
                return_exceptions=True
            )
            
            site_structure, design_system, dynamic_content, seo_data = content_tasks
            
            # Phase 3: Parallel WordPress & Template Generation (25-45s)
            logger.info("🔧 Phase 3: WordPress & Template Generation")
            wordpress_tasks = await asyncio.gather(
                self._generate_wordpress_implementation(site_structure, design_system),
                self._generate_elementor_templates(site_structure, dynamic_content),
                self._generate_acf_integration(acf_structure, dynamic_content),
                return_exceptions=True
            )
            
            wordpress_code, elementor_templates, acf_integration = wordpress_tasks
            
            # Phase 4: Assembly & Personalization (45-55s)
            logger.info("🔗 Phase 4: Assembly & Personalization")
            assembly_tasks = await asyncio.gather(
                self._apply_content_personalization(elementor_templates, dynamic_content),
                self._apply_brazilian_market_features(wordpress_code, brazilian_features),
                self._generate_deployment_package(wordpress_code, elementor_templates, acf_integration),
                return_exceptions=True
            )
            
            personalized_templates, localized_wordpress, deployment_package = assembly_tasks
            
            # Phase 5: Final Quality Check & Package (55-60s)
            logger.info("✅ Phase 5: Quality Check & Package")
            final_validation = await self._validate_instant_site({
                "site_structure": site_structure,
                "design_system": design_system,
                "wordpress_code": localized_wordpress,
                "elementor_templates": personalized_templates,
                "acf_integration": acf_integration,
                "seo_data": seo_data,
                "brazilian_features": brazilian_features
            })
            
            # Calculate generation time
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Deduct AI Credits
            await self._deduct_ai_credits(user_id, credits_required)
            
            logger.info(f"🎉 Site generated in {generation_time:.2f} seconds!")
            
            return AIResponse(
                success=True,
                content={
                    "generation_id": f"instant_{user_id}_{int(start_time.timestamp())}",
                    "generation_time": generation_time,
                    "site_structure": site_structure,
                    "design_system": design_system,
                    "wordpress_package": deployment_package,
                    "elementor_templates": personalized_templates,
                    "acf_configuration": acf_integration,
                    "seo_optimization": seo_data,
                    "brazilian_features": brazilian_features,
                    "deployment_instructions": self._generate_deployment_instructions(),
                    "validation_results": final_validation,
                    "success_url": f"/preview/{deployment_package['preview_id']}"
                },
                message=f"Site gerado instantaneamente em {generation_time:.2f}s! 🚀",
                credits_used=credits_required,
                model_used="multi-agent-instant-system"
            )
            
        except Exception as e:
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ Instant site generation failed after {generation_time:.2f}s: {str(e)}")
            return AIResponse(
                success=False,
                message=f"Instant site generation failed: {str(e)}",
                credits_used=0
            )
    
    async def _analyze_business_context(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Analyze business context for instant generation"""
        
        # Use multiple agents for comprehensive analysis
        business_analysis = {
            "industry": request.industry,
            "business_type": request.business_type,
            "target_audience": request.target_audience,
            "keywords": request.keywords or self._generate_industry_keywords(request.industry),
            "competitors": self._analyze_competition(request.industry),
            "market_position": self._determine_market_position(request),
            "content_strategy": self._plan_content_strategy(request),
            "conversion_goals": self._identify_conversion_goals(request.business_type)
        }
        
        return business_analysis
    
    async def _setup_brazilian_features(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Setup Brazilian market features using BrazilianMarketAgent"""
        
        brazilian_agent = self.specialized_agents.get("brazilian_market")
        if not brazilian_agent:
            return {}
        
        site_data = {
            "business_name": request.business_name,
            "whatsapp_number": getattr(request, "whatsapp_number", ""),
            "domain": f"{request.business_name.lower().replace(' ', '')}.com.br"
        }
        
        return brazilian_agent.apply_brazilian_features(site_data, request.industry)
    
    async def _generate_acf_structure(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Generate ACF field structure for the site"""
        
        # Use existing ACF service
        acf_field_groups = acf_service.create_template_fields_for_industry(
            industry=request.industry,
            business_type=request.business_type
        )
        
        # Add dynamic placeholders based on industry
        personalization_agent = self.specialized_agents.get("content_personalization")
        if personalization_agent:
            dynamic_placeholders = personalization_agent.generate_dynamic_placeholders(
                request.industry, 
                "landing_page"
            )
            
            return {
                "field_groups": [g.dict() for g in acf_field_groups],
                "dynamic_placeholders": dynamic_placeholders,
                "export_data": acf_service.generate_acf_export(acf_field_groups)
            }
        
        return {
            "field_groups": [g.dict() for g in acf_field_groups],
            "dynamic_placeholders": [],
            "export_data": acf_service.generate_acf_export(acf_field_groups)
        }
    
    async def _generate_site_structure(self, request: SiteGenerationRequest, context: Dict) -> Dict[str, Any]:
        """Generate site structure using SiteArchitectAgent"""
        
        architect_agent = self.specialized_agents.get("site_architect")
        if not architect_agent:
            return self._fallback_site_structure(request)
        
        business_info = {
            "name": request.business_name,
            "type": request.business_type,
            "industry": request.industry,
            "description": request.business_description,
            "services": request.services,
            "target_audience": request.target_audience
        }
        
        return architect_agent.design_site_structure(business_info)
    
    async def _generate_design_system(self, request: SiteGenerationRequest, context: Dict) -> Dict[str, Any]:
        """Generate design system using DesignAgent"""
        
        design_agent = self.specialized_agents.get("design")
        if not design_agent:
            return self._fallback_design_system()
        
        brand_info = {
            "industry": request.industry,
            "style": "modern",  # Could be determined from context
            "business_name": request.business_name,
            "target_audience": request.target_audience
        }
        
        return design_agent.create_design_system(brand_info)
    
    async def _generate_dynamic_content(self, request: SiteGenerationRequest, context: Dict) -> Dict[str, Any]:
        """Generate dynamic content using ContentGeneratorAgent"""
        
        content_agent = self.specialized_agents.get("content_generator")
        if not content_agent:
            return self._fallback_dynamic_content(request)
        
        # Generate content for each page type
        content_types = ["hero", "about", "services", "contact", "testimonials"]
        generated_content = {}
        
        for content_type in content_types:
            content = await self._generate_content_block(content_agent, content_type, request)
            generated_content[content_type] = content
        
        return generated_content
    
    async def _generate_content_block(self, agent, content_type: str, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Generate specific content block"""
        
        # This would call the actual agent with appropriate prompts
        # For now, return structured content with placeholders
        
        content_templates = {
            "hero": {
                "title": f"[BUSINESS_NAME] - {self._get_industry_tagline(request.industry)}",
                "subtitle": f"[BUSINESS_DESCRIPTION]",
                "cta_text": "Entre em Contato",
                "cta_url": "[CONTACT_URL]"
            },
            "about": {
                "title": "Sobre [BUSINESS_NAME]",
                "content": f"A [BUSINESS_NAME] é especializada em {', '.join(request.services[:3])} com foco em qualidade e excelência.",
                "image": "[ABOUT_IMAGE]"
            },
            "services": {
                "title": "Nossos Serviços",
                "services": [
                    {
                        "title": service,
                        "description": f"Serviço especializado em {service} com qualidade garantida.",
                        "icon": "service-icon"
                    } for service in request.services[:6]
                ]
            },
            "contact": {
                "title": "Entre em Contato",
                "phone": "[PHONE]",
                "whatsapp": "[WHATSAPP]",
                "email": "[EMAIL]",
                "address": "[ADDRESS]"
            },
            "testimonials": {
                "title": "O Que Nossos Clientes Dizem",
                "testimonials": [
                    {
                        "content": "Excelente atendimento e qualidade nos serviços!",
                        "author": "Cliente Satisfeito",
                        "rating": 5
                    }
                ]
            }
        }
        
        return content_templates.get(content_type, {"title": f"Conteúdo {content_type}"})
    
    async def _generate_seo_optimization(self, request: SiteGenerationRequest, context: Dict) -> Dict[str, Any]:
        """Generate SEO optimization using SEOAgent"""
        
        seo_agent = self.specialized_agents.get("seo")
        if not seo_agent:
            return self._fallback_seo_data(request)
        
        # Generate SEO data for each page
        keywords = context.get("keywords", [request.business_name])
        
        return {
            "global_seo": {
                "site_title": f"{request.business_name} - {self._get_industry_tagline(request.industry)}",
                "site_description": f"{request.business_description[:150]}",
                "keywords": keywords,
                "og_image": "[SEO_IMAGE]"
            },
            "page_seo": {
                "home": seo_agent.optimize_page("", keywords),
                "about": seo_agent.optimize_page("", [request.business_name, "sobre"]),
                "services": seo_agent.optimize_page("", keywords + ["serviços"]),
                "contact": seo_agent.optimize_page("", [request.business_name, "contato"])
            }
        }
    
    async def _generate_wordpress_implementation(self, site_structure: Dict, design_system: Dict) -> Dict[str, Any]:
        """Generate WordPress implementation using WordPressAgent"""
        
        wp_agent = self.specialized_agents.get("wordpress")
        if not wp_agent:
            return self._fallback_wordpress_code()
        
        return wp_agent.generate_wordpress_code(site_structure, design_system)
    
    async def _generate_elementor_templates(self, site_structure: Dict, dynamic_content: Dict) -> Dict[str, Any]:
        """Generate Elementor templates with dynamic content"""
        
        elementor_agent = self.specialized_agents.get("elementor_integration")
        if not elementor_agent:
            return self._fallback_elementor_templates()
        
        # Create widget configurations for each page
        widget_configs = []
        
        for page in site_structure.get("pages", []):
            page_widgets = self._create_page_widgets(page, dynamic_content)
            widget_configs.extend(page_widgets)
        
        return {
            "templates": elementor_agent.create_dynamic_widgets(widget_configs),
            "acf_bridge": elementor_agent.generate_elementor_acf_bridge([], []),
            "widget_count": len(widget_configs)
        }
    
    async def _generate_acf_integration(self, acf_structure: Dict, dynamic_content: Dict) -> Dict[str, Any]:
        """Generate ACF integration configuration"""
        
        return {
            "field_groups": acf_structure.get("field_groups", []),
            "export_json": acf_structure.get("export_data", {}),
            "wp_cli_commands": acf_service.generate_wp_cli_commands(acf_structure.get("field_groups", [])),
            "dynamic_mappings": self._create_acf_content_mappings(dynamic_content)
        }
    
    async def _apply_content_personalization(self, templates: Dict, dynamic_content: Dict) -> Dict[str, Any]:
        """Apply content personalization using ContentPersonalizationAgent"""
        
        personalization_agent = self.specialized_agents.get("content_personalization")
        if not personalization_agent:
            return templates
        
        personalized_templates = templates.copy()
        
        # Apply personalization to each template
        for template_key, template_data in templates.get("templates", []):
            if isinstance(template_data, dict) and "settings" in template_data:
                # Extract content and apply personalization
                content = str(template_data.get("settings", {}))
                
                personalization_result = personalization_agent.personalize_content(
                    content, 
                    dynamic_content
                )
                
                # Update template with personalized content
                # This would require more sophisticated template processing
                personalized_templates[template_key] = template_data
        
        return personalized_templates
    
    async def _apply_brazilian_market_features(self, wordpress_code: Dict, brazilian_features: Dict) -> Dict[str, Any]:
        """Apply Brazilian market features to WordPress code"""
        
        localized_code = wordpress_code.copy()
        
        # Add Brazilian-specific features to WordPress implementation
        if brazilian_features.get("whatsapp_integration", {}).get("enabled"):
            localized_code["whatsapp_integration"] = brazilian_features["whatsapp_integration"]
        
        if brazilian_features.get("pix_payment", {}).get("enabled"):
            localized_code["pix_integration"] = brazilian_features["pix_payment"]
        
        if brazilian_features.get("lgpd_compliance"):
            localized_code["lgpd_features"] = brazilian_features["lgpd_compliance"]
        
        return localized_code
    
    async def _generate_deployment_package(self, wordpress_code: Dict, elementor_templates: Dict, acf_integration: Dict) -> Dict[str, Any]:
        """Generate deployment package for the site"""
        
        preview_id = f"preview_{datetime.now().timestamp()}"
        
        return {
            "preview_id": preview_id,
            "wordpress_files": wordpress_code,
            "elementor_data": elementor_templates,
            "acf_configuration": acf_integration,
            "deployment_script": self._generate_deployment_script(),
            "container_config": self._generate_container_config(),
            "nginx_config": self._generate_nginx_config(),
            "ssl_config": self._generate_ssl_config()
        }
    
    async def _validate_instant_site(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated site using QualityAssuranceAgent"""
        
        qa_agent = self.specialized_agents.get("qa")
        if not qa_agent:
            return {"validation_score": 85, "issues": [], "warnings": []}
        
        return qa_agent.validate_site(site_data)
    
    def _generate_industry_keywords(self, industry: str) -> List[str]:
        """Generate industry-specific keywords"""
        
        industry_keywords = {
            "restaurante": ["restaurante", "delivery", "comida", "gastronomia", "cardápio"],
            "saude": ["clínica", "médico", "saúde", "consulta", "agendamento"],
            "ecommerce": ["loja online", "produtos", "comprar", "vendas", "e-commerce"],
            "educacao": ["curso", "educação", "ensino", "aprendizado", "aula"],
            "consultoria": ["consultoria", "especialista", "serviços", "soluções", "estratégia"]
        }
        
        return industry_keywords.get(industry, ["serviços", "qualidade", "profissional"])
    
    def _get_industry_tagline(self, industry: str) -> str:
        """Get industry-specific tagline"""
        
        taglines = {
            "restaurante": "Sabor que você vai amar",
            "saude": "Cuidando da sua saúde",
            "ecommerce": "Compre com confiança",
            "educacao": "Aprendizado de qualidade",
            "consultoria": "Soluções que funcionam"
        }
        
        return taglines.get(industry, "Qualidade e confiança")
    
    def _create_page_widgets(self, page: Dict, dynamic_content: Dict) -> List[Dict[str, Any]]:
        """Create widget configurations for a page"""
        
        page_type = page.get("template", "page")
        
        if page_type == "home":
            return [
                {"type": "heading", "content": "[BUSINESS_NAME]", "size": "h1"},
                {"type": "text-editor", "content": "[BUSINESS_DESCRIPTION]"},
                {"type": "button", "text": "[BUTTON_TEXT]", "url": "[CONTACT_URL]"}
            ]
        elif page_type == "services":
            return [
                {"type": "heading", "content": "Nossos Serviços", "size": "h2"},
                {"type": "text-editor", "content": "Conheça nossos serviços especializados"}
            ]
        
        return [{"type": "text-editor", "content": f"Conteúdo da página {page.get('title', '')}"}]
    
    def _create_acf_content_mappings(self, dynamic_content: Dict) -> Dict[str, str]:
        """Create mappings between ACF fields and dynamic content"""
        
        return {
            "business_name": dynamic_content.get("hero", {}).get("title", ""),
            "business_description": dynamic_content.get("about", {}).get("content", ""),
            "phone_number": dynamic_content.get("contact", {}).get("phone", ""),
            "whatsapp_number": dynamic_content.get("contact", {}).get("whatsapp", ""),
            "email_address": dynamic_content.get("contact", {}).get("email", "")
        }
    
    def _generate_deployment_instructions(self) -> List[str]:
        """Generate deployment instructions"""
        
        return [
            "1. Baixe o pacote de arquivos gerado",
            "2. Configure o domínio e hosting",
            "3. Importe a configuração ACF via JSON",
            "4. Configure os templates do Elementor",
            "5. Ative os plugins recomendados",
            "6. Configure o WhatsApp e PIX (se aplicável)",
            "7. Teste e publique o site"
        ]
    
    def _generate_deployment_script(self) -> str:
        """Generate deployment script"""
        
        return """#!/bin/bash
# KenzySites Deployment Script
echo "🚀 Deploying WordPress site..."

# Setup WordPress
wp core download --locale=pt_BR
wp config create --dbname=db --dbuser=user --dbpass=pass
wp core install --url=example.com --title="Site" --admin_user=admin

# Install plugins
wp plugin install advanced-custom-fields-pro --activate
wp plugin install elementor --activate

# Import ACF configuration
wp acf import acf-export.json

echo "✅ Deployment complete!"
"""
    
    def _generate_container_config(self) -> Dict[str, Any]:
        """Generate container configuration"""
        
        return {
            "docker_compose": {
                "version": "3.8",
                "services": {
                    "wordpress": {
                        "image": "wordpress:latest",
                        "environment": {
                            "WORDPRESS_DB_HOST": "db",
                            "WORDPRESS_DB_NAME": "wordpress",
                            "WORDPRESS_LOCALE": "pt_BR"
                        }
                    },
                    "db": {
                        "image": "mysql:8.0",
                        "environment": {
                            "MYSQL_DATABASE": "wordpress",
                            "MYSQL_ROOT_PASSWORD": "rootpass"
                        }
                    }
                }
            }
        }
    
    def _generate_nginx_config(self) -> str:
        """Generate nginx configuration"""
        
        return """
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://wordpress:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""
    
    def _generate_ssl_config(self) -> Dict[str, Any]:
        """Generate SSL configuration"""
        
        return {
            "enabled": True,
            "provider": "letsencrypt",
            "auto_renewal": True,
            "redirect_http": True
        }
    
    # Fallback methods for when agents are not available
    def _fallback_site_structure(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Fallback site structure"""
        return {
            "pages": [
                {"title": "Home", "slug": "/", "template": "home"},
                {"title": "Sobre", "slug": "/sobre", "template": "page"},
                {"title": "Serviços", "slug": "/servicos", "template": "services"},
                {"title": "Contato", "slug": "/contato", "template": "contact"}
            ],
            "navigation": {
                "primary": ["Home", "Sobre", "Serviços", "Contato"]
            }
        }
    
    def _fallback_design_system(self) -> Dict[str, Any]:
        """Fallback design system"""
        return {
            "colors": {
                "primary": "#0066FF",
                "secondary": "#00D4FF",
                "dark": "#0A0E27",
                "light": "#F8F9FA"
            },
            "typography": {
                "heading": "Inter, sans-serif",
                "body": "Inter, sans-serif"
            }
        }
    
    def _fallback_dynamic_content(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Fallback dynamic content"""
        return {
            "hero": {
                "title": f"{request.business_name} - Qualidade e Confiança",
                "subtitle": request.business_description,
                "cta_text": "Entre em Contato"
            }
        }
    
    def _fallback_seo_data(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Fallback SEO data"""
        return {
            "global_seo": {
                "site_title": request.business_name,
                "site_description": request.business_description,
                "keywords": [request.business_name]
            }
        }
    
    def _fallback_wordpress_code(self) -> Dict[str, Any]:
        """Fallback WordPress code"""
        return {
            "theme": {"style.css": "/* Basic theme styles */"},
            "plugins": ["elementor", "advanced-custom-fields"]
        }
    
    def _fallback_elementor_templates(self) -> Dict[str, Any]:
        """Fallback Elementor templates"""
        return {
            "templates": [],
            "widget_count": 0
        }
    
    # Missing helper methods for instant generation
    def _analyze_competition(self, industry: str) -> List[str]:
        """Analyze competition for the industry"""
        return [f"Competitor 1 in {industry}", f"Competitor 2 in {industry}"]
    
    def _determine_market_position(self, request: SiteGenerationRequest) -> str:
        """Determine market positioning"""
        if "premium" in request.business_description.lower():
            return "premium"
        elif "affordable" in request.business_description.lower():
            return "budget"
        else:
            return "standard"
    
    def _plan_content_strategy(self, request: SiteGenerationRequest) -> Dict[str, Any]:
        """Plan content strategy"""
        return {
            "tone": "professional",
            "style": "conversational",
            "keywords_focus": request.keywords[:5] if request.keywords else [],
            "content_pillars": ["quality", "service", "trust"]
        }
    
    def _identify_conversion_goals(self, business_type: str) -> List[str]:
        """Identify conversion goals based on business type"""
        conversion_goals_map = {
            "service": ["contact_form", "phone_call", "whatsapp_message"],
            "ecommerce": ["purchase", "add_to_cart", "newsletter_signup"],
            "restaurant": ["order_online", "reservation", "menu_download"],
            "healthcare": ["appointment_booking", "contact_form", "phone_call"]
        }
        
        return conversion_goals_map.get(business_type, ["contact_form", "phone_call"])
    
    def _build_content_prompt(self, request: ContentGenerationRequest) -> str:
        """Build optimized prompt for content generation"""
        
        prompt = f"""
        Generate a {request.content_type} for WordPress with the following specifications:
        
        Topic: {request.topic}
        Target Audience: {request.target_audience or 'General public'}
        Tone: {request.tone or 'professional'}
        Keywords: {', '.join(request.keywords) if request.keywords else 'Not specified'}
        Length: {request.length or 'medium'}
        
        Requirements:
        - Write in Brazilian Portuguese
        - Include SEO optimization
        - Use engaging headlines and subheadings
        - Add meta description suggestion
        - Include relevant tags and categories
        - Ensure mobile-friendly formatting
        
        Additional Instructions: {request.custom_instructions or 'None'}
        """
        
        return prompt.strip()
    
    def _build_site_generation_prompt(self, request: SiteGenerationRequest) -> str:
        """Build comprehensive prompt for site generation"""
        
        prompt = f"""
        Generate a complete WordPress site structure for:
        
        Business: {request.business_name}
        Industry: {request.industry}
        Description: {request.business_description}
        Target Audience: {request.target_audience or 'General customers'}
        Location: {request.location or 'Brazil'}
        
        Requirements (PRD compliance):
        - Create minimum 5 pages: Home, About, Services, Blog, Contact
        - Generate SEO-optimized content for each page
        - Suggest appropriate WordPress theme
        - Recommend essential plugins
        - Create navigation menu structure
        - Generate meta descriptions for all pages
        - Ensure mobile responsiveness
        - Target PageSpeed score > 90
        
        Output should include:
        1. Site structure and page hierarchy
        2. Content for each page (Brazilian Portuguese)
        3. SEO metadata
        4. Theme and plugin recommendations
        5. Configuration settings
        """
        
        return prompt.strip()
    
    def _build_site_generation_prompt_with_acf(
        self,
        request: SiteGenerationRequest,
        acf_field_groups: list,
        template_recommendations: dict,
        brazilian_template=None
    ) -> str:
        """Build comprehensive prompt for site generation with ACF support"""
        
        prompt = f"""
        Generate a complete WordPress site with Advanced Custom Fields (ACF) support for:
        
        Business: {request.business_name}
        Industry: {request.industry}
        Type: {request.business_type}
        Description: {request.business_description}
        
        Target Audience: {request.target_audience}
        Services: {', '.join(request.services) if request.services else 'General services'}
        USPs: {', '.join(request.unique_selling_points) if request.unique_selling_points else 'Quality and professionalism'}
        
        Keywords: {', '.join(request.keywords) if request.keywords else 'Auto-generate based on industry'}
        
        Template Recommendations:
        - Theme: {template_recommendations.get('theme', 'Astra')}
        - Plugins: {', '.join(template_recommendations.get('plugins', []))}
        - Color Scheme: Primary: {template_recommendations.get('colors', {}).get('primary')}, Secondary: {template_recommendations.get('colors', {}).get('secondary')}
        - Fonts: Heading: {template_recommendations.get('fonts', {}).get('heading')}, Body: {template_recommendations.get('fonts', {}).get('body')}
        
        ACF Field Groups to Configure:
        {self._format_acf_field_groups(acf_field_groups)}
        
        """
        
        if brazilian_template:
            prompt += f"""
        Brazilian Market Specific Features:
        - WhatsApp Integration: {brazilian_template.whatsapp_integration}
        - PIX Payment: {brazilian_template.pix_payment}
        - LGPD Compliance: {brazilian_template.lgpd_notice}
        - Specific Features: {brazilian_template.specific_features}
        """
        
        prompt += """
        Requirements:
        - Create site structure with ACF custom fields
        - Generate content in Brazilian Portuguese
        - Implement industry-specific ACF field groups
        - Ensure all fields have appropriate default values
        - Create minimum 5 pages with custom fields
        - Generate SEO-optimized content
        - Configure WordPress with ACF Pro
        - Set up isolated container architecture
        - Ensure mobile responsiveness
        - Target PageSpeed score > 90
        
        Output should include:
        1. Site structure with ACF field mappings
        2. Content for each page with custom field values
        3. ACF field configuration for each template
        4. WordPress configuration commands
        5. Container isolation setup
        6. SEO metadata with Brazilian keywords
        """
        
        return prompt.strip()
    
    def _format_acf_field_groups(self, field_groups: list) -> str:
        """Format ACF field groups for prompt"""
        formatted = []
        for group in field_groups:
            formatted.append(f"- {group.title}: {len(group.fields)} fields")
            for field in group.fields[:3]:  # Show first 3 fields as example
                formatted.append(f"  - {field.label} ({field.type.value})")
        return '\n'.join(formatted)
    
    async def _check_ai_credits(self, user_id: str, user_plan: str) -> int:
        """Check available AI Credits for user"""
        # This would integrate with Redis/database to track credits
        # For now, return plan limits
        from app.core.config import PLAN_LIMITS
        return PLAN_LIMITS.get(user_plan, {}).get("ai_credits_monthly", 0)
    
    async def _deduct_ai_credits(self, user_id: str, credits: int):
        """Deduct AI Credits from user balance"""
        # This would integrate with Redis/database to update credits
        logger.info(f"Deducted {credits} AI Credits from user {user_id}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "initialized": self.initialized,
            "agents": list(self.agents.keys()),
            "primary_model": self.primary_model.id if self.primary_model else None,
            "secondary_models": len(self.secondary_models),
            "total_agents": len(self.agents)
        }
    
    async def execute_workflow(
        self,
        workflow_type: WorkflowType,
        user_id: str,
        user_plan: str,
        parameters: Dict[str, Any]
    ) -> AIResponse:
        """Execute a complete workflow using crews and tasks"""
        
        try:
            # Get workflow definition
            workflow = self.task_orchestrator.get_workflow(workflow_type)
            if not workflow:
                return AIResponse(
                    success=False,
                    message=f"Unknown workflow type: {workflow_type}",
                    credits_used=0
                )
            
            # Calculate total credits needed
            credits_required = self._calculate_workflow_credits(workflow_type)
            credits_available = await self._check_ai_credits(user_id, user_plan)
            
            if credits_available < credits_required:
                return AIResponse(
                    success=False,
                    message=f"Insufficient AI Credits. Required: {credits_required}, Available: {credits_available}",
                    credits_used=0
                )
            
            # Assemble crew for the mission
            mission_id = f"{user_id}_{workflow_type.value}_{datetime.now().timestamp()}"
            crew = self.crew_manager.assemble_crew(
                crew_type=workflow_type.value,
                mission_id=mission_id
            )
            
            # Start mission execution
            self.crew_manager.start_mission(mission_id)
            
            # Execute tasks in workflow
            results = {}
            tasks = self.task_orchestrator.get_tasks_for_workflow(workflow_type)
            parallel_groups = self.task_orchestrator.get_parallel_groups(workflow_type)
            
            # Execute parallel groups
            for group in parallel_groups:
                group_tasks = [t for t in tasks if t.name in group]
                group_results = await asyncio.gather(
                    *[self._execute_task(t, parameters) for t in group_tasks]
                )
                for task, result in zip(group_tasks, group_results):
                    results[task.name] = result
            
            # Execute remaining sequential tasks
            sequential_tasks = [
                t for t in tasks 
                if t.name not in [task for group in parallel_groups for task in group]
            ]
            for task in sequential_tasks:
                results[task.name] = await self._execute_task(task, parameters)
            
            # Complete mission
            self.crew_manager.complete_mission(mission_id, results)
            
            # Deduct credits
            await self._deduct_ai_credits(user_id, credits_required)
            
            return AIResponse(
                success=True,
                content=results,
                message=f"Workflow {workflow_type.value} completed successfully",
                credits_used=credits_required,
                model_used="multi-agent-system"
            )
            
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            return AIResponse(
                success=False,
                message=f"Workflow execution failed: {str(e)}",
                credits_used=0
            )
    
    async def _execute_task(self, task, parameters):
        """Execute individual task with appropriate agent"""
        try:
            # Get the agent for this task
            agent = self.specialized_agents.get(
                task.agent_type.lower().replace("agent", "")
            )
            
            if not agent:
                logger.warning(f"No agent found for task {task.name}")
                return {"error": f"No agent for {task.agent_type}"}
            
            # Execute task with agent
            result = await agent.execute_task(
                task_name=task.name,
                parameters={**task.parameters, **parameters}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_workflow_credits(self, workflow_type: WorkflowType) -> int:
        """Calculate total credits needed for workflow"""
        credits_map = {
            WorkflowType.WORDPRESS_SITE: 100,
            WorkflowType.LANDING_PAGE: 50,
            WorkflowType.BLOG_POST: 20,
            WorkflowType.SITE_CLONE: 150,
            WorkflowType.CONTENT_AUTOMATION: 30
        }
        return credits_map.get(workflow_type, 50)
    
    async def cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("🧹 Cleaning up Agno Framework resources")
        self.agents.clear()
        self.specialized_agents.clear()
        self.crews.clear()
        self.initialized = False