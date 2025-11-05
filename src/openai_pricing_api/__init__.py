"""OpenAI Pricing - Simple and clean API for OpenAI model cost calculation.

A standalone library for calculating costs across different OpenAI model types:
- Token-based models (GPT-4o, GPT-5, o-series, etc.)
- Image generation (DALL-E-3, DALL-E-2)
- Video generation (Sora-2)

Features:
- Automatic pricing updates from external API
- Local caching for performance
- Credit-based billing support
- Mixed usage calculation
- Variance tracking

Quick Start:
    >>> from openai_pricing_api import PricingCalculator
    >>> calculator = PricingCalculator()
    >>> cost = calculator.calculate_token_cost("gpt-4o", input_tokens=1000, output_tokens=500)
    >>> print(f"Cost: ${cost:.4f}")
"""

__version__ = "0.1.0"
__author__ = "bes-dev"
__license__ = "Apache-2.0"

# Main API
from .calculator import PricingCalculator
from .pricing import PricingProvider

# Models
from .models import (
    TokenUsage,
    ImageUsage,
    CostEstimate,
    ActualCost,
    ModelPricing,
)

__all__ = [
    # Main classes
    "PricingCalculator",
    "PricingProvider",
    # Models
    "TokenUsage",
    "ImageUsage",
    "CostEstimate",
    "ActualCost",
    "ModelPricing",
]
