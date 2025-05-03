"""
Agent components for POD Automation System.
"""

from pod_automation.agents.trend_forecaster import TrendForecaster
from pod_automation.agents.prompt_optimizer import PromptOptimizer
from pod_automation.agents.design_generation import DesignGenerationPipeline
from pod_automation.agents.stable_diffusion import create_stable_diffusion_client
from pod_automation.agents.mockup_generator import MockupGenerator
from pod_automation.agents.publishing_agent import PublishingAgent
from pod_automation.agents.seo_optimizer import SEOOptimizer

__all__ = [
    'TrendForecaster',
    'PromptOptimizer',
    'DesignGenerationPipeline',
    'create_stable_diffusion_client',
    'MockupGenerator',
    'PublishingAgent',
    'SEOOptimizer'
]