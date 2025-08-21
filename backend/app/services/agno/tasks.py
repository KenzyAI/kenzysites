"""
Agno Framework Tasks Definition
Defines specific tasks that agents can perform
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgnoTask:
    """Base task definition for Agno Framework"""
    name: str
    description: str
    agent_type: str
    priority: TaskPriority
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    output_format: str = "structured"
    max_retries: int = 3
    timeout_seconds: int = 300
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

# Content Generation Tasks
CONTENT_TASKS = {
    "generate_blog_post": AgnoTask(
        name="generate_blog_post",
        description="Generate SEO-optimized blog post with metadata",
        agent_type="ContentGeneratorAgent",
        priority=TaskPriority.MEDIUM,
        parameters={
            "min_words": 800,
            "max_words": 2000,
            "include_meta": True,
            "include_schema": True,
            "optimize_keywords": True
        }
    ),
    
    "generate_landing_page_copy": AgnoTask(
        name="generate_landing_page_copy",
        description="Create compelling landing page copy with CTAs",
        agent_type="ContentGeneratorAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "sections": ["hero", "features", "benefits", "testimonials", "cta"],
            "tone": "professional",
            "include_headlines": True,
            "include_ctas": True
        }
    ),
    
    "generate_product_description": AgnoTask(
        name="generate_product_description",
        description="Create detailed product descriptions for e-commerce",
        agent_type="ContentGeneratorAgent",
        priority=TaskPriority.MEDIUM,
        parameters={
            "format": "structured",
            "include_features": True,
            "include_benefits": True,
            "include_specs": True
        }
    )
}

# Site Architecture Tasks
ARCHITECTURE_TASKS = {
    "design_site_structure": AgnoTask(
        name="design_site_structure",
        description="Create complete site architecture with navigation",
        agent_type="SiteArchitectAgent",
        priority=TaskPriority.CRITICAL,
        parameters={
            "max_depth": 3,
            "include_sitemap": True,
            "include_navigation": True,
            "responsive_design": True
        }
    ),
    
    "generate_page_hierarchy": AgnoTask(
        name="generate_page_hierarchy",
        description="Define page relationships and information architecture",
        agent_type="SiteArchitectAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "include_breadcrumbs": True,
            "include_internal_links": True,
            "seo_friendly_urls": True
        }
    ),
    
    "plan_content_sections": AgnoTask(
        name="plan_content_sections",
        description="Plan content sections for each page type",
        agent_type="SiteArchitectAgent",
        priority=TaskPriority.MEDIUM,
        parameters={
            "section_types": ["header", "hero", "content", "sidebar", "footer"],
            "reusable_components": True
        }
    )
}

# Design Tasks
DESIGN_TASKS = {
    "create_design_system": AgnoTask(
        name="create_design_system",
        description="Generate complete design system with tokens",
        agent_type="DesignAgent",
        priority=TaskPriority.CRITICAL,
        parameters={
            "include_colors": True,
            "include_typography": True,
            "include_spacing": True,
            "include_components": True,
            "dark_mode": True
        }
    ),
    
    "generate_ui_components": AgnoTask(
        name="generate_ui_components",
        description="Create reusable UI component specifications",
        agent_type="DesignAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "component_types": ["buttons", "forms", "cards", "modals", "navigation"],
            "include_variations": True,
            "include_states": True
        }
    ),
    
    "create_page_layouts": AgnoTask(
        name="create_page_layouts",
        description="Design responsive page layouts",
        agent_type="DesignAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "breakpoints": ["mobile", "tablet", "desktop", "wide"],
            "grid_system": True,
            "flexible_sections": True
        }
    )
}

# SEO Tasks
SEO_TASKS = {
    "optimize_page_seo": AgnoTask(
        name="optimize_page_seo",
        description="Comprehensive SEO optimization for pages",
        agent_type="SEOAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "optimize_meta": True,
            "optimize_headers": True,
            "optimize_images": True,
            "generate_schema": True,
            "internal_linking": True
        }
    ),
    
    "generate_seo_content": AgnoTask(
        name="generate_seo_content",
        description="Create SEO-focused content recommendations",
        agent_type="SEOAgent",
        priority=TaskPriority.MEDIUM,
        parameters={
            "keyword_research": True,
            "competitor_analysis": True,
            "content_gaps": True
        }
    ),
    
    "technical_seo_audit": AgnoTask(
        name="technical_seo_audit",
        description="Perform technical SEO analysis and fixes",
        agent_type="SEOAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "check_performance": True,
            "check_accessibility": True,
            "check_crawlability": True,
            "generate_sitemap": True,
            "generate_robots": True
        }
    )
}

# WordPress Tasks
WORDPRESS_TASKS = {
    "generate_wordpress_theme": AgnoTask(
        name="generate_wordpress_theme",
        description="Create complete WordPress theme with templates",
        agent_type="WordPressAgent",
        priority=TaskPriority.CRITICAL,
        parameters={
            "theme_type": "custom",
            "include_customizer": True,
            "include_widgets": True,
            "include_menus": True,
            "block_editor_support": True
        }
    ),
    
    "create_custom_blocks": AgnoTask(
        name="create_custom_blocks",
        description="Generate Gutenberg blocks for WordPress",
        agent_type="WordPressAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "block_types": ["content", "layout", "media", "interactive"],
            "include_variations": True,
            "include_patterns": True
        }
    ),
    
    "generate_plugins": AgnoTask(
        name="generate_plugins",
        description="Create WordPress plugins for functionality",
        agent_type="WordPressAgent",
        priority=TaskPriority.MEDIUM,
        parameters={
            "plugin_types": ["functionality", "integration", "optimization"],
            "admin_interface": True,
            "settings_page": True
        }
    ),
    
    "setup_wordpress_api": AgnoTask(
        name="setup_wordpress_api",
        description="Configure WordPress REST API endpoints",
        agent_type="WordPressAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "custom_endpoints": True,
            "authentication": True,
            "cors_config": True
        }
    )
}

# Quality Assurance Tasks
QA_TASKS = {
    "validate_content": AgnoTask(
        name="validate_content",
        description="Validate content quality and accuracy",
        agent_type="QualityAssuranceAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "check_grammar": True,
            "check_facts": True,
            "check_consistency": True,
            "check_tone": True
        }
    ),
    
    "test_functionality": AgnoTask(
        name="test_functionality",
        description="Test site functionality and interactions",
        agent_type="QualityAssuranceAgent",
        priority=TaskPriority.CRITICAL,
        parameters={
            "test_forms": True,
            "test_navigation": True,
            "test_responsive": True,
            "test_performance": True
        }
    ),
    
    "accessibility_audit": AgnoTask(
        name="accessibility_audit",
        description="Ensure WCAG compliance and accessibility",
        agent_type="QualityAssuranceAgent",
        priority=TaskPriority.HIGH,
        parameters={
            "wcag_level": "AA",
            "test_screen_readers": True,
            "test_keyboard_nav": True,
            "test_color_contrast": True
        }
    )
}

# Workflow Definitions
class WorkflowType(Enum):
    WORDPRESS_SITE = "wordpress_site"
    LANDING_PAGE = "landing_page"
    BLOG_POST = "blog_post"
    SITE_CLONE = "site_clone"
    CONTENT_AUTOMATION = "content_automation"

WORKFLOWS = {
    WorkflowType.WORDPRESS_SITE: {
        "name": "Complete WordPress Site Generation",
        "description": "End-to-end WordPress site creation workflow",
        "tasks": [
            "design_site_structure",
            "create_design_system",
            "generate_wordpress_theme",
            "create_custom_blocks",
            "generate_plugins",
            "setup_wordpress_api",
            "optimize_page_seo",
            "test_functionality",
            "accessibility_audit"
        ],
        "parallel_groups": [
            ["design_site_structure", "create_design_system"],
            ["generate_wordpress_theme", "create_custom_blocks", "generate_plugins"],
            ["optimize_page_seo", "test_functionality", "accessibility_audit"]
        ]
    },
    
    WorkflowType.LANDING_PAGE: {
        "name": "Landing Page Creation",
        "description": "High-converting landing page generation",
        "tasks": [
            "generate_landing_page_copy",
            "create_page_layouts",
            "generate_ui_components",
            "optimize_page_seo",
            "validate_content",
            "test_functionality"
        ],
        "parallel_groups": [
            ["generate_landing_page_copy", "create_page_layouts"],
            ["optimize_page_seo", "validate_content"]
        ]
    },
    
    WorkflowType.BLOG_POST: {
        "name": "Blog Post Generation",
        "description": "SEO-optimized blog post creation",
        "tasks": [
            "generate_blog_post",
            "optimize_page_seo",
            "validate_content"
        ],
        "parallel_groups": []
    },
    
    WorkflowType.SITE_CLONE: {
        "name": "Site Cloning and Enhancement",
        "description": "Clone and improve existing site",
        "tasks": [
            "design_site_structure",
            "create_design_system",
            "generate_wordpress_theme",
            "optimize_page_seo",
            "technical_seo_audit",
            "test_functionality"
        ],
        "parallel_groups": [
            ["design_site_structure", "create_design_system"],
            ["optimize_page_seo", "technical_seo_audit"]
        ]
    },
    
    WorkflowType.CONTENT_AUTOMATION: {
        "name": "Automated Content Pipeline",
        "description": "Automated content generation and publishing",
        "tasks": [
            "generate_blog_post",
            "generate_seo_content",
            "optimize_page_seo",
            "validate_content"
        ],
        "parallel_groups": [
            ["generate_blog_post", "generate_seo_content"]
        ]
    }
}

class TaskOrchestrator:
    """Orchestrates task execution within workflows"""
    
    def __init__(self):
        self.all_tasks = {
            **CONTENT_TASKS,
            **ARCHITECTURE_TASKS,
            **DESIGN_TASKS,
            **SEO_TASKS,
            **WORDPRESS_TASKS,
            **QA_TASKS
        }
    
    def get_task(self, task_name: str) -> Optional[AgnoTask]:
        """Get task definition by name"""
        return self.all_tasks.get(task_name)
    
    def get_workflow(self, workflow_type: WorkflowType) -> Dict[str, Any]:
        """Get workflow definition by type"""
        return WORKFLOWS.get(workflow_type)
    
    def get_tasks_for_workflow(self, workflow_type: WorkflowType) -> List[AgnoTask]:
        """Get all tasks for a specific workflow"""
        workflow = self.get_workflow(workflow_type)
        if not workflow:
            return []
        
        tasks = []
        for task_name in workflow["tasks"]:
            task = self.get_task(task_name)
            if task:
                tasks.append(task)
        
        return tasks
    
    def get_parallel_groups(self, workflow_type: WorkflowType) -> List[List[str]]:
        """Get parallel execution groups for workflow"""
        workflow = self.get_workflow(workflow_type)
        if not workflow:
            return []
        
        return workflow.get("parallel_groups", [])
    
    def validate_workflow(self, workflow_type: WorkflowType) -> bool:
        """Validate that all tasks in workflow exist"""
        workflow = self.get_workflow(workflow_type)
        if not workflow:
            return False
        
        for task_name in workflow["tasks"]:
            if task_name not in self.all_tasks:
                return False
        
        return True

# Export task orchestrator instance
task_orchestrator = TaskOrchestrator()