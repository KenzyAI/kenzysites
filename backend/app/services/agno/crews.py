"""
Agno Framework Crews Configuration
Defines agent crews and their coordination patterns
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class CrewRole(Enum):
    LEADER = "leader"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"

class CrewStatus(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class CrewMember:
    """Individual crew member definition"""
    agent_type: str
    role: CrewRole
    responsibilities: List[str]
    can_delegate: bool = False
    can_review: bool = False
    priority: int = 1

@dataclass
class CrewConfiguration:
    """Complete crew configuration"""
    name: str
    description: str
    members: List[CrewMember]
    coordination_pattern: str
    max_parallel_tasks: int = 3
    timeout_minutes: int = 30
    retry_on_failure: bool = True

# Specialized Crews for Different Workflows

WORDPRESS_SITE_CREW = CrewConfiguration(
    name="WordPress Site Generation Crew",
    description="Full team for creating complete WordPress sites",
    members=[
        CrewMember(
            agent_type="SiteArchitectAgent",
            role=CrewRole.LEADER,
            responsibilities=[
                "Define site structure",
                "Plan information architecture",
                "Coordinate design decisions"
            ],
            can_delegate=True,
            can_review=True,
            priority=1
        ),
        CrewMember(
            agent_type="DesignAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Create design system",
                "Design UI components",
                "Define visual hierarchy"
            ],
            priority=2
        ),
        CrewMember(
            agent_type="ContentGeneratorAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Generate page content",
                "Create marketing copy",
                "Write documentation"
            ],
            priority=3
        ),
        CrewMember(
            agent_type="WordPressAgent",
            role=CrewRole.EXECUTOR,
            responsibilities=[
                "Generate theme code",
                "Create plugins",
                "Setup WordPress configuration"
            ],
            priority=2
        ),
        CrewMember(
            agent_type="SEOAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Optimize for search engines",
                "Generate meta tags",
                "Create schema markup"
            ],
            priority=3
        ),
        CrewMember(
            agent_type="QualityAssuranceAgent",
            role=CrewRole.REVIEWER,
            responsibilities=[
                "Validate implementation",
                "Test functionality",
                "Ensure quality standards"
            ],
            can_review=True,
            priority=4
        )
    ],
    coordination_pattern="hierarchical",
    max_parallel_tasks=4,
    timeout_minutes=45
)

LANDING_PAGE_CREW = CrewConfiguration(
    name="Landing Page Creation Crew",
    description="Focused team for high-converting landing pages",
    members=[
        CrewMember(
            agent_type="DesignAgent",
            role=CrewRole.LEADER,
            responsibilities=[
                "Design landing page layout",
                "Create visual elements",
                "Define conversion flow"
            ],
            can_delegate=True,
            can_review=True,
            priority=1
        ),
        CrewMember(
            agent_type="ContentGeneratorAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Write compelling copy",
                "Create headlines and CTAs",
                "Generate social proof content"
            ],
            priority=2
        ),
        CrewMember(
            agent_type="SEOAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Optimize for keywords",
                "Setup tracking",
                "Configure analytics"
            ],
            priority=3
        ),
        CrewMember(
            agent_type="QualityAssuranceAgent",
            role=CrewRole.REVIEWER,
            responsibilities=[
                "Test conversions",
                "Validate copy",
                "Check responsiveness"
            ],
            can_review=True,
            priority=4
        )
    ],
    coordination_pattern="collaborative",
    max_parallel_tasks=3,
    timeout_minutes=20
)

CONTENT_AUTOMATION_CREW = CrewConfiguration(
    name="Content Automation Crew",
    description="Automated content generation and optimization",
    members=[
        CrewMember(
            agent_type="ContentGeneratorAgent",
            role=CrewRole.LEADER,
            responsibilities=[
                "Generate blog posts",
                "Create content series",
                "Manage content calendar"
            ],
            can_delegate=True,
            priority=1
        ),
        CrewMember(
            agent_type="SEOAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Keyword optimization",
                "Meta tag generation",
                "Internal linking"
            ],
            priority=2
        ),
        CrewMember(
            agent_type="QualityAssuranceAgent",
            role=CrewRole.REVIEWER,
            responsibilities=[
                "Fact checking",
                "Grammar validation",
                "Tone consistency"
            ],
            can_review=True,
            priority=3
        )
    ],
    coordination_pattern="pipeline",
    max_parallel_tasks=2,
    timeout_minutes=15
)

SITE_CLONING_CREW = CrewConfiguration(
    name="Site Cloning and Enhancement Crew",
    description="Clone and improve existing websites",
    members=[
        CrewMember(
            agent_type="SiteArchitectAgent",
            role=CrewRole.COORDINATOR,
            responsibilities=[
                "Analyze source site",
                "Plan improvements",
                "Map content migration"
            ],
            can_delegate=True,
            priority=1
        ),
        CrewMember(
            agent_type="DesignAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Enhance design",
                "Modernize UI",
                "Improve UX"
            ],
            priority=2
        ),
        CrewMember(
            agent_type="WordPressAgent",
            role=CrewRole.EXECUTOR,
            responsibilities=[
                "Recreate in WordPress",
                "Setup functionality",
                "Configure plugins"
            ],
            priority=2
        ),
        CrewMember(
            agent_type="SEOAgent",
            role=CrewRole.SPECIALIST,
            responsibilities=[
                "Improve SEO",
                "Fix technical issues",
                "Enhance performance"
            ],
            priority=3
        ),
        CrewMember(
            agent_type="QualityAssuranceAgent",
            role=CrewRole.REVIEWER,
            responsibilities=[
                "Compare with original",
                "Validate improvements",
                "Test all features"
            ],
            can_review=True,
            priority=4
        )
    ],
    coordination_pattern="phased",
    max_parallel_tasks=3,
    timeout_minutes=60
)

# Coordination Patterns
class CoordinationPattern:
    """Defines how crew members work together"""
    
    PATTERNS = {
        "hierarchical": {
            "description": "Leader delegates tasks to specialists",
            "communication": "top-down",
            "decision_making": "centralized",
            "best_for": ["complex_projects", "large_teams"]
        },
        "collaborative": {
            "description": "All members work together equally",
            "communication": "peer-to-peer",
            "decision_making": "consensus",
            "best_for": ["creative_tasks", "small_teams"]
        },
        "pipeline": {
            "description": "Sequential task execution",
            "communication": "handoff",
            "decision_making": "stage-based",
            "best_for": ["content_generation", "processing_workflows"]
        },
        "phased": {
            "description": "Work in distinct phases",
            "communication": "phase-gates",
            "decision_making": "milestone-based",
            "best_for": ["migrations", "transformations"]
        },
        "swarm": {
            "description": "Dynamic task assignment",
            "communication": "broadcast",
            "decision_making": "emergent",
            "best_for": ["exploratory_tasks", "optimization"]
        }
    }

class CrewManager:
    """Manages crew coordination and execution"""
    
    def __init__(self):
        self.crews = {
            "wordpress_site": WORDPRESS_SITE_CREW,
            "landing_page": LANDING_PAGE_CREW,
            "content_automation": CONTENT_AUTOMATION_CREW,
            "site_cloning": SITE_CLONING_CREW
        }
        self.active_crews: Dict[str, Dict[str, Any]] = {}
    
    def get_crew(self, crew_type: str) -> Optional[CrewConfiguration]:
        """Get crew configuration by type"""
        return self.crews.get(crew_type)
    
    def assemble_crew(self, crew_type: str, mission_id: str) -> Dict[str, Any]:
        """Assemble a crew for a specific mission"""
        crew_config = self.get_crew(crew_type)
        if not crew_config:
            raise ValueError(f"Unknown crew type: {crew_type}")
        
        crew_instance = {
            "mission_id": mission_id,
            "crew_type": crew_type,
            "config": crew_config,
            "status": CrewStatus.IDLE,
            "members_status": {
                member.agent_type: "ready"
                for member in crew_config.members
            },
            "started_at": None,
            "completed_at": None,
            "results": {},
            "errors": []
        }
        
        self.active_crews[mission_id] = crew_instance
        return crew_instance
    
    def start_mission(self, mission_id: str) -> bool:
        """Start crew mission execution"""
        if mission_id not in self.active_crews:
            return False
        
        crew = self.active_crews[mission_id]
        crew["status"] = CrewStatus.PLANNING
        crew["started_at"] = datetime.now()
        
        return True
    
    def update_member_status(
        self,
        mission_id: str,
        agent_type: str,
        status: str
    ) -> bool:
        """Update individual crew member status"""
        if mission_id not in self.active_crews:
            return False
        
        crew = self.active_crews[mission_id]
        if agent_type in crew["members_status"]:
            crew["members_status"][agent_type] = status
            return True
        
        return False
    
    def complete_mission(
        self,
        mission_id: str,
        results: Dict[str, Any]
    ) -> bool:
        """Mark mission as completed"""
        if mission_id not in self.active_crews:
            return False
        
        crew = self.active_crews[mission_id]
        crew["status"] = CrewStatus.COMPLETED
        crew["completed_at"] = datetime.now()
        crew["results"] = results
        
        return True
    
    def get_mission_status(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get current mission status"""
        return self.active_crews.get(mission_id)
    
    def get_coordination_pattern(
        self,
        pattern_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get coordination pattern details"""
        return CoordinationPattern.PATTERNS.get(pattern_name)
    
    def optimize_crew_composition(
        self,
        crew_type: str,
        constraints: Dict[str, Any]
    ) -> CrewConfiguration:
        """Optimize crew based on constraints"""
        base_crew = self.get_crew(crew_type)
        if not base_crew:
            raise ValueError(f"Unknown crew type: {crew_type}")
        
        # Apply constraints (budget, time, resources)
        optimized = CrewConfiguration(
            name=base_crew.name,
            description=base_crew.description,
            members=base_crew.members,
            coordination_pattern=base_crew.coordination_pattern,
            max_parallel_tasks=base_crew.max_parallel_tasks,
            timeout_minutes=base_crew.timeout_minutes,
            retry_on_failure=base_crew.retry_on_failure
        )
        
        # Adjust based on constraints
        if "max_time" in constraints:
            optimized.timeout_minutes = min(
                optimized.timeout_minutes,
                constraints["max_time"]
            )
        
        if "max_parallel" in constraints:
            optimized.max_parallel_tasks = min(
                optimized.max_parallel_tasks,
                constraints["max_parallel"]
            )
        
        if "priority_agents" in constraints:
            # Filter to only priority agents
            priority_types = constraints["priority_agents"]
            optimized.members = [
                m for m in optimized.members
                if m.agent_type in priority_types
            ]
        
        return optimized
    
    def calculate_crew_cost(
        self,
        crew_type: str,
        estimated_tasks: int
    ) -> Dict[str, Any]:
        """Calculate estimated cost for crew mission"""
        crew = self.get_crew(crew_type)
        if not crew:
            return {"error": "Unknown crew type"}
        
        # Base cost per agent type (in AI credits)
        agent_costs = {
            "ContentGeneratorAgent": 20,
            "SiteArchitectAgent": 30,
            "DesignAgent": 25,
            "SEOAgent": 15,
            "WordPressAgent": 35,
            "QualityAssuranceAgent": 10
        }
        
        total_cost = 0
        agent_breakdown = {}
        
        for member in crew.members:
            agent_cost = agent_costs.get(member.agent_type, 10)
            member_cost = agent_cost * estimated_tasks
            total_cost += member_cost
            agent_breakdown[member.agent_type] = member_cost
        
        return {
            "total_cost": total_cost,
            "agent_breakdown": agent_breakdown,
            "crew_type": crew_type,
            "estimated_tasks": estimated_tasks
        }

# Export crew manager instance
crew_manager = CrewManager()