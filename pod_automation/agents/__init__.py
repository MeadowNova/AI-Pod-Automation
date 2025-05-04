"""
Agent components for POD Automation System.
"""

from pod_automation.agents.trend.trend_forecaster import TrendForecaster
from pod_automation.agents.prompt_optimizer import PromptOptimizer
from pod_automation.agents.design.design_generation import DesignGenerationPipeline
from pod_automation.agents.stable_diffusion import create_stable_diffusion_client
from pod_automation.agents.mockup.mockup_generator import MockupGenerator
from pod_automation.agents.publishing.publishing_agent import PublishingAgent
from pod_automation.agents.seo.seo_optimizer import SEOOptimizer

__all__ = [
    'TrendForecaster',
    'PromptOptimizer',
    'DesignGenerationPipeline',
    'create_stable_diffusion_client',
    'MockupGenerator',
    'PublishingAgent',
    'SEOOptimizer'
]