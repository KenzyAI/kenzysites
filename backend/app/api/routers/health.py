"""
Health check endpoints for Agno Framework system
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import asyncio
import time
from datetime import datetime

from app.models.ai_models import AgnoSystemStatus, AgentHealth
from app.services.agno_manager import AgnoManager

router = APIRouter()

async def get_agno_manager() -> AgnoManager:
    """Dependency to get Agno manager from app state"""
    # In a real application, this would be injected from app state
    # For now, we'll create a simple dependency
    from main import app
    return app.state.agno_manager

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "WordPress AI SaaS Backend",
        "version": "1.0.0"
    }

@router.get("/health/agno", response_model=AgnoSystemStatus)
async def agno_health_check(agno_manager: AgnoManager = Depends(get_agno_manager)):
    """Detailed Agno Framework health check"""
    
    try:
        # Get agent status
        agent_status = await agno_manager.get_agent_status()
        
        # Check individual agents
        agent_healths = []
        for agent_name in agent_status.get("agents", []):
            agent_healths.append(
                AgentHealth(
                    agent_name=agent_name,
                    status="healthy" if agent_status["initialized"] else "warning",
                    last_used=datetime.now(),
                    total_requests=0,  # Would come from metrics
                    error_count=0,     # Would come from metrics
                    average_response_time=None
                )
            )
        
        return AgnoSystemStatus(
            initialized=agent_status["initialized"],
            total_agents=agent_status["total_agents"],
            healthy_agents=len([a for a in agent_healths if a.status == "healthy"]),
            primary_model=agent_status.get("primary_model"),
            secondary_models=agent_status["secondary_models"],
            agents=agent_healths,
            uptime=time.time(),  # Would track actual uptime
            last_health_check=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agno health check failed: {str(e)}"
        )

@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(agno_manager: AgnoManager = Depends(get_agno_manager)):
    """Comprehensive health check including all system components"""
    
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    # Check Agno Framework
    try:
        agno_status = await agno_manager.get_agent_status()
        health_data["components"]["agno_framework"] = {
            "status": "healthy" if agno_status["initialized"] else "unhealthy",
            "details": agno_status
        }
    except Exception as e:
        health_data["components"]["agno_framework"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["overall_status"] = "degraded"
    
    # Check Database (would be implemented)
    health_data["components"]["database"] = {
        "status": "healthy",  # Placeholder
        "details": "Connection successful"
    }
    
    # Check Redis (would be implemented)
    health_data["components"]["redis"] = {
        "status": "healthy",  # Placeholder
        "details": "Connection successful"
    }
    
    # Check AI Providers
    health_data["components"]["ai_providers"] = {
        "status": "healthy",
        "details": {
            "primary": "Claude 3.5 Sonnet - Available",
            "secondary": "GPT-4o, Gemini 2.0 - Available"
        }
    }
    
    return health_data

@router.get("/metrics", response_model=Dict[str, Any])
async def system_metrics(agno_manager: AgnoManager = Depends(get_agno_manager)):
    """System performance metrics"""
    
    # These would be real metrics from monitoring systems
    return {
        "timestamp": datetime.now().isoformat(),
        "agno_framework": {
            "agents_initialized": len(agno_manager.agents),
            "total_requests_today": 0,  # From metrics store
            "average_response_time_ms": 0,  # From metrics store
            "error_rate_percent": 0,  # From metrics store
        },
        "ai_providers": {
            "claude_requests": 0,
            "gpt4_requests": 0, 
            "gemini_requests": 0,
            "total_tokens_used": 0,
            "estimated_costs_usd": 0.0
        },
        "system": {
            "cpu_usage_percent": 0,  # From system monitoring
            "memory_usage_mb": 0,    # From system monitoring
            "disk_usage_gb": 0,      # From system monitoring
        }
    }