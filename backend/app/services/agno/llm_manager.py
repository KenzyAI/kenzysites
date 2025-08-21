"""
Multi-LLM Manager for Agno Framework
Manages multiple LLM providers with fallback and load balancing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random

# Import LLM providers
from agno.models.anthropic import Claude
from agno.models.openai import OpenAI
from agno.models.google import GoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"

class ModelTier(Enum):
    PRIMARY = 1
    SECONDARY = 2
    TERTIARY = 3

@dataclass
class LLMConfig:
    """Configuration for an LLM provider"""
    provider: LLMProvider
    model_id: str
    tier: ModelTier
    api_key: Optional[str]
    max_tokens: int = 4000
    temperature: float = 0.7
    rate_limit: int = 60  # requests per minute
    cost_per_1k_tokens: float = 0.01
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

class LLMHealthStatus:
    """Track health status of LLM providers"""
    
    def __init__(self):
        self.status: Dict[LLMProvider, Dict[str, Any]] = {}
        self.last_check: Dict[LLMProvider, datetime] = {}
        self.failure_count: Dict[LLMProvider, int] = {}
        self.response_times: Dict[LLMProvider, List[float]] = {}
    
    def update_status(
        self,
        provider: LLMProvider,
        success: bool,
        response_time: float = 0,
        error: Optional[str] = None
    ):
        """Update provider health status"""
        now = datetime.now()
        
        if provider not in self.status:
            self.status[provider] = {
                "healthy": True,
                "last_success": now,
                "last_failure": None,
                "avg_response_time": 0
            }
            self.failure_count[provider] = 0
            self.response_times[provider] = []
        
        if success:
            self.status[provider]["healthy"] = True
            self.status[provider]["last_success"] = now
            self.failure_count[provider] = 0
            
            # Track response times (keep last 100)
            self.response_times[provider].append(response_time)
            if len(self.response_times[provider]) > 100:
                self.response_times[provider].pop(0)
            
            # Calculate average response time
            self.status[provider]["avg_response_time"] = sum(
                self.response_times[provider]
            ) / len(self.response_times[provider])
        else:
            self.failure_count[provider] += 1
            self.status[provider]["last_failure"] = now
            
            # Mark unhealthy after 3 consecutive failures
            if self.failure_count[provider] >= 3:
                self.status[provider]["healthy"] = False
        
        self.last_check[provider] = now
    
    def is_healthy(self, provider: LLMProvider) -> bool:
        """Check if provider is healthy"""
        if provider not in self.status:
            return True  # Assume healthy if not checked yet
        
        # Check if provider has been unhealthy for too long
        if not self.status[provider]["healthy"]:
            last_failure = self.status[provider].get("last_failure")
            if last_failure:
                # Try again after 5 minutes
                if datetime.now() - last_failure > timedelta(minutes=5):
                    self.status[provider]["healthy"] = True
                    self.failure_count[provider] = 0
        
        return self.status[provider]["healthy"]

class MultiLLMManager:
    """Manages multiple LLM providers with intelligent routing"""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, Any] = {}
        self.configs: Dict[LLMProvider, LLMConfig] = {}
        self.health_status = LLMHealthStatus()
        self.request_counts: Dict[LLMProvider, int] = {}
        self.last_reset = datetime.now()
        self.initialized = False
    
    async def initialize(self):
        """Initialize all configured LLM providers"""
        
        # Configure Claude 3.5 Sonnet (Primary - PRD requirement)
        if settings.ANTHROPIC_API_KEY:
            self.configs[LLMProvider.ANTHROPIC] = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model_id="claude-3-5-sonnet-20241022",
                tier=ModelTier.PRIMARY,
                api_key=settings.ANTHROPIC_API_KEY,
                max_tokens=8192,
                temperature=0.7,
                rate_limit=50,
                cost_per_1k_tokens=0.003,
                capabilities=[
                    "long_context",
                    "creative_writing",
                    "code_generation",
                    "reasoning",
                    "multimodal"
                ]
            )
            
            self.providers[LLMProvider.ANTHROPIC] = Claude(
                id=self.configs[LLMProvider.ANTHROPIC].model_id,
                api_key=self.configs[LLMProvider.ANTHROPIC].api_key
            )
            
            logger.info("✅ Claude 3.5 Sonnet (Primary) initialized")
        
        # Configure GPT-4o (Secondary)
        if settings.OPENAI_API_KEY:
            self.configs[LLMProvider.OPENAI] = LLMConfig(
                provider=LLMProvider.OPENAI,
                model_id="gpt-4o-2024-08-06",
                tier=ModelTier.SECONDARY,
                api_key=settings.OPENAI_API_KEY,
                max_tokens=4096,
                temperature=0.7,
                rate_limit=60,
                cost_per_1k_tokens=0.005,
                capabilities=[
                    "function_calling",
                    "code_generation",
                    "reasoning",
                    "multimodal",
                    "json_mode"
                ]
            )
            
            self.providers[LLMProvider.OPENAI] = OpenAI(
                id=self.configs[LLMProvider.OPENAI].model_id,
                api_key=self.configs[LLMProvider.OPENAI].api_key
            )
            
            logger.info("✅ GPT-4o (Secondary) initialized")
        
        # Configure Gemini 2.0 (Tertiary)
        if settings.GOOGLE_AI_API_KEY:
            self.configs[LLMProvider.GOOGLE] = LLMConfig(
                provider=LLMProvider.GOOGLE,
                model_id="gemini-2.0-flash-exp",
                tier=ModelTier.TERTIARY,
                api_key=settings.GOOGLE_AI_API_KEY,
                max_tokens=8192,
                temperature=0.7,
                rate_limit=60,
                cost_per_1k_tokens=0.0005,
                capabilities=[
                    "fast_inference",
                    "code_generation",
                    "multimodal",
                    "long_context"
                ]
            )
            
            self.providers[LLMProvider.GOOGLE] = GoogleGenerativeAI(
                id=self.configs[LLMProvider.GOOGLE].model_id,
                api_key=self.configs[LLMProvider.GOOGLE].api_key
            )
            
            logger.info("✅ Gemini 2.0 Flash (Tertiary) initialized")
        
        if not self.providers:
            raise ValueError("No LLM providers configured. Please set API keys.")
        
        self.initialized = True
        logger.info(f"✅ Multi-LLM Manager initialized with {len(self.providers)} providers")
    
    def get_primary_provider(self) -> Optional[Any]:
        """Get the primary LLM provider"""
        for provider, config in self.configs.items():
            if config.tier == ModelTier.PRIMARY and self.health_status.is_healthy(provider):
                return self.providers.get(provider)
        return None
    
    def get_provider_by_capability(
        self,
        required_capabilities: List[str]
    ) -> Optional[Any]:
        """Get provider that supports specific capabilities"""
        eligible_providers = []
        
        for provider, config in self.configs.items():
            if not self.health_status.is_healthy(provider):
                continue
            
            # Check if provider has all required capabilities
            if all(cap in config.capabilities for cap in required_capabilities):
                eligible_providers.append((provider, config))
        
        if not eligible_providers:
            return None
        
        # Sort by tier (prefer primary)
        eligible_providers.sort(key=lambda x: x[1].tier.value)
        
        return self.providers.get(eligible_providers[0][0])
    
    async def execute_with_fallback(
        self,
        prompt: str,
        preferred_provider: Optional[LLMProvider] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Execute prompt with automatic fallback to other providers"""
        
        # Determine provider order
        if preferred_provider and preferred_provider in self.providers:
            provider_order = [preferred_provider] + [
                p for p in self.providers if p != preferred_provider
            ]
        else:
            # Sort by tier
            provider_order = sorted(
                self.providers.keys(),
                key=lambda p: self.configs[p].tier.value
            )
        
        last_error = None
        
        for provider in provider_order:
            if not self.health_status.is_healthy(provider):
                continue
            
            # Check rate limits
            if not self._check_rate_limit(provider):
                continue
            
            try:
                start_time = datetime.now()
                
                # Execute with provider
                model = self.providers[provider]
                response = await model.agenerate(prompt)
                
                # Calculate response time
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Update health status
                self.health_status.update_status(
                    provider,
                    success=True,
                    response_time=response_time
                )
                
                # Track usage
                self._track_usage(provider)
                
                return {
                    "success": True,
                    "content": response.content,
                    "provider": provider.value,
                    "model": self.configs[provider].model_id,
                    "response_time": response_time,
                    "cost_estimate": self._estimate_cost(provider, len(prompt))
                }
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Provider {provider.value} failed: {last_error}")
                
                # Update health status
                self.health_status.update_status(
                    provider,
                    success=False,
                    error=last_error
                )
                
                continue
        
        # All providers failed
        return {
            "success": False,
            "error": f"All providers failed. Last error: {last_error}",
            "providers_tried": len(provider_order)
        }
    
    def _check_rate_limit(self, provider: LLMProvider) -> bool:
        """Check if provider is within rate limits"""
        now = datetime.now()
        
        # Reset counts every minute
        if now - self.last_reset > timedelta(minutes=1):
            self.request_counts.clear()
            self.last_reset = now
        
        current_count = self.request_counts.get(provider, 0)
        rate_limit = self.configs[provider].rate_limit
        
        return current_count < rate_limit
    
    def _track_usage(self, provider: LLMProvider):
        """Track usage for rate limiting"""
        if provider not in self.request_counts:
            self.request_counts[provider] = 0
        self.request_counts[provider] += 1
    
    def _estimate_cost(self, provider: LLMProvider, token_count: int) -> float:
        """Estimate cost for the request"""
        config = self.configs[provider]
        # Rough estimate: 1 token ≈ 4 characters
        estimated_tokens = token_count / 4
        cost = (estimated_tokens / 1000) * config.cost_per_1k_tokens
        return round(cost, 4)
    
    def get_load_balanced_provider(self) -> Optional[Any]:
        """Get provider using load balancing strategy"""
        healthy_providers = [
            p for p in self.providers
            if self.health_status.is_healthy(p)
        ]
        
        if not healthy_providers:
            return None
        
        # Weighted selection based on:
        # 1. Tier (prefer primary)
        # 2. Current load
        # 3. Average response time
        
        weights = []
        for provider in healthy_providers:
            config = self.configs[provider]
            
            # Base weight by tier (higher for primary)
            weight = 4 - config.tier.value
            
            # Adjust by current load
            current_load = self.request_counts.get(provider, 0)
            rate_limit = config.rate_limit
            load_factor = 1 - (current_load / rate_limit)
            weight *= load_factor
            
            # Adjust by response time (if available)
            status = self.health_status.status.get(provider, {})
            avg_response_time = status.get("avg_response_time", 1)
            if avg_response_time > 0:
                weight *= (1 / avg_response_time)
            
            weights.append(weight)
        
        # Select provider based on weights
        if sum(weights) > 0:
            selected = random.choices(healthy_providers, weights=weights)[0]
            return self.providers[selected]
        
        return self.providers[healthy_providers[0]]
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report of all providers"""
        report = {
            "initialized": self.initialized,
            "total_providers": len(self.providers),
            "healthy_providers": sum(
                1 for p in self.providers
                if self.health_status.is_healthy(p)
            ),
            "providers": {}
        }
        
        for provider in self.providers:
            config = self.configs[provider]
            status = self.health_status.status.get(provider, {})
            
            report["providers"][provider.value] = {
                "model": config.model_id,
                "tier": config.tier.name,
                "healthy": self.health_status.is_healthy(provider),
                "current_load": self.request_counts.get(provider, 0),
                "rate_limit": config.rate_limit,
                "avg_response_time": status.get("avg_response_time", 0),
                "last_success": status.get("last_success"),
                "last_failure": status.get("last_failure"),
                "capabilities": config.capabilities
            }
        
        return report
    
    async def benchmark_providers(self, test_prompt: str) -> Dict[str, Any]:
        """Benchmark all providers with a test prompt"""
        results = {}
        
        for provider in self.providers:
            if not self.health_status.is_healthy(provider):
                results[provider.value] = {"status": "unhealthy"}
                continue
            
            try:
                start_time = datetime.now()
                model = self.providers[provider]
                response = await model.agenerate(test_prompt)
                response_time = (datetime.now() - start_time).total_seconds()
                
                results[provider.value] = {
                    "status": "success",
                    "response_time": response_time,
                    "response_length": len(response.content),
                    "cost_estimate": self._estimate_cost(provider, len(test_prompt))
                }
                
            except Exception as e:
                results[provider.value] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results

# Create global instance
multi_llm_manager = MultiLLMManager()