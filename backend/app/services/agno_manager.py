"""
Agno Framework Manager - Multi-Agent System Orchestration
Handles AI agent initialization, management, and coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Agno Framework imports
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAI
from agno.models.google import GoogleGenerativeAI
from agno.tools.reasoning import ReasoningTools
from agno.tools.python import PythonTools

# Import our real Agno components
from app.services.agno.agents import (
    ContentGeneratorAgent,
    SiteArchitectAgent,
    DesignAgent,
    SEOAgent,
    WordPressAgent,
    QualityAssuranceAgent
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
            logger.info("🚀 Initializing Agno Framework Manager")
            
            # Initialize model providers (PRD: Claude 3.5 Sonnet primary, GPT-4o secondary, Gemini tertiary)
            await self._initialize_models()
            
            # Create specialized agents (both legacy and new)
            await self._create_content_generation_agent()
            await self._create_site_generation_agent()
            await self._create_seo_optimization_agent()
            
            # Initialize real specialized agents
            await self._initialize_specialized_agents()
            
            self.initialized = True
            logger.info("✅ Agno Framework Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Agno Manager: {str(e)}")
            raise
    
    async def _initialize_models(self):
        """Initialize AI model providers with fallback strategy"""
        
        # Primary: Claude 3.5 Sonnet (as per PRD)
        if settings.ANTHROPIC_API_KEY:
            self.primary_model = Claude(
                id="claude-sonnet-4-20250514",
                api_key=settings.ANTHROPIC_API_KEY
            )
            logger.info("✅ Primary model: Claude 3.5 Sonnet initialized")
        
        # Secondary: GPT-4o
        if settings.OPENAI_API_KEY:
            self.secondary_models.append(
                OpenAI(
                    id="gpt-4o-2024-08-06",
                    api_key=settings.OPENAI_API_KEY
                )
            )
            logger.info("✅ Secondary model: GPT-4o initialized")
        
        # Tertiary: Gemini 2.0
        if settings.GOOGLE_AI_API_KEY:
            self.secondary_models.append(
                GoogleGenerativeAI(
                    id="gemini-2.0-flash-exp",
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
            "content_generator": ContentGeneratorAgent(model),
            "site_architect": SiteArchitectAgent(model),
            "design": DesignAgent(model),
            "seo": SEOAgent(model),
            "wordpress": WordPressAgent(model),
            "qa": QualityAssuranceAgent(model)
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