"""Main calculator for OpenAI model pricing and cost tracking.

Simple and clean API for calculating costs across different model types.
"""

import logging
from typing import Optional, Any
from pathlib import Path
from datetime import timedelta

from .pricing import PricingProvider
from .models import TokenUsage, ImageUsage, CostEstimate, ActualCost, ModelPricing

logger = logging.getLogger(__name__)


class PricingCalculator:
    """Main calculator for model pricing and cost tracking.

    Provides a simple API for:
    - Token-based cost calculation (GPT models)
    - Image generation cost (DALL-E)
    - Credit-based billing
    - Actual vs estimated cost tracking

    Example:
        >>> calculator = PricingCalculator()
        >>> cost = calculator.calculate_token_cost("gpt-4o", input_tokens=1000, output_tokens=500)
        >>> print(f"Cost: ${cost:.4f}")
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        cache_file: Optional[Path] = None,
        cache_duration: Optional[timedelta] = None,
    ):
        """Initialize pricing calculator.

        Args:
            api_url: Optional custom API URL for pricing data
            cache_file: Optional custom cache file location
            cache_duration: Optional cache validity duration
        """
        kwargs = {}
        if api_url:
            kwargs["api_url"] = api_url
        if cache_file:
            kwargs["cache_file"] = cache_file
        if cache_duration:
            kwargs["cache_duration"] = cache_duration

        self.provider = PricingProvider(**kwargs)

    # =========================================================================
    # Core calculation methods
    # =========================================================================

    def calculate_token_cost(
        self,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cached_tokens: int = 0,
    ) -> float:
        """Calculate cost for token-based model usage.

        Args:
            model: Model identifier (e.g., "gpt-4o", "gpt-5-nano")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cached_tokens: Number of cached input tokens (if supported)

        Returns:
            Cost in USD

        Raises:
            ValueError: If token counts are negative or model not found

        Example:
            >>> cost = calculator.calculate_token_cost("gpt-4o", input_tokens=1000, output_tokens=500)
            >>> print(f"${cost:.4f}")
            $0.0125
        """
        # Validate inputs
        if input_tokens < 0 or output_tokens < 0 or cached_tokens < 0:
            raise ValueError("Token counts must be >= 0")

        pricing = self.provider.get_model_pricing(model)
        if not pricing:
            raise ValueError(f"Model not found: {model}")

        if pricing.pricing_type != "per_1m_tokens":
            raise ValueError(f"Model {model} is not token-based (type: {pricing.pricing_type})")

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * (pricing.input_price or 0.0)
        output_cost = (output_tokens / 1_000_000) * (pricing.output_price or 0.0)
        cached_cost = 0.0

        if cached_tokens > 0 and pricing.cached_input_price:
            cached_cost = (cached_tokens / 1_000_000) * pricing.cached_input_price

        return input_cost + output_cost + cached_cost

    def calculate_image_cost(
        self,
        model: str,
        count: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
    ) -> float:
        """Calculate cost for image generation.

        Args:
            model: Model identifier (e.g., "dall-e-3")
            count: Number of images
            size: Image size (e.g., "1024x1024", "1024x1792")
            quality: Image quality ("standard" or "hd")

        Returns:
            Cost in USD

        Raises:
            ValueError: If parameters are invalid or model not found

        Example:
            >>> cost = calculator.calculate_image_cost("dall-e-3", count=5, size="1024x1024", quality="hd")
            >>> print(f"${cost:.4f}")
            $0.4000
        """
        if count < 1:
            raise ValueError("Count must be >= 1")

        pricing = self.provider.get_model_pricing(model)
        if not pricing:
            raise ValueError(f"Model not found: {model}")

        if pricing.pricing_type != "per_image_resolution":
            raise ValueError(f"Model {model} is not image-based (type: {pricing.pricing_type})")

        if not pricing.image_pricing:
            raise ValueError(f"No image pricing data for model: {model}")

        # Get price for quality/size
        quality_pricing = pricing.image_pricing.get(quality, pricing.image_pricing.get("standard", {}))
        price_per_image = quality_pricing.get(size, 0.0)

        if price_per_image == 0.0:
            # Try to get any available price as fallback
            for q_pricing in pricing.image_pricing.values():
                if isinstance(q_pricing, dict) and q_pricing:
                    price_per_image = next(iter(q_pricing.values()), 0.0)
                    logger.warning(f"Using fallback price for {model}: ${price_per_image}")
                    break

        return price_per_image * count

    def calculate_video_cost(
        self,
        model: str,
        duration_seconds: float,
    ) -> float:
        """Calculate cost for video generation.

        Args:
            model: Model identifier (e.g., "sora-2")
            duration_seconds: Video duration in seconds

        Returns:
            Cost in USD

        Raises:
            ValueError: If duration is negative or model not found

        Example:
            >>> cost = calculator.calculate_video_cost("sora-2", duration_seconds=5.0)
            >>> print(f"${cost:.4f}")
        """
        if duration_seconds < 0:
            raise ValueError("Duration must be >= 0")

        pricing = self.provider.get_model_pricing(model)
        if not pricing:
            raise ValueError(f"Model not found: {model}")

        if pricing.pricing_type != "per_second":
            raise ValueError(f"Model {model} is not video-based (type: {pricing.pricing_type})")

        price_per_second = pricing.video_price_per_second or 0.0
        return price_per_second * duration_seconds

    def calculate_mixed_usage(self, usage: dict[str, dict[str, Any]]) -> float:
        """Calculate total cost from mixed usage (tokens + images + video).

        Automatically detects usage type and calculates appropriate cost.

        Args:
            usage: Dictionary mapping stage names to usage dicts
                Example: {
                    "text_generation": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
                    "image_generation": {"model": "dall-e-3", "count": 5, "size": "1024x1024"},
                }

        Returns:
            Total cost in USD

        Example:
            >>> usage = {
            ...     "analyze": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
            ...     "generate": {"model": "gpt-image-1", "count": 10}
            ... }
            >>> total = calculator.calculate_mixed_usage(usage)
            >>> print(f"Total: ${total:.4f}")
        """
        total_cost = 0.0

        for stage_name, stage_usage in usage.items():
            model = stage_usage.get("model")
            if not model:
                logger.warning(f"No model specified for stage: {stage_name}")
                continue

            try:
                # Get pricing to determine type
                pricing = self.provider.get_model_pricing(model)
                if not pricing:
                    logger.warning(f"No pricing found for model: {model}")
                    continue

                # Calculate based on type
                if pricing.pricing_type == "per_1m_tokens":
                    cost = self.calculate_token_cost(
                        model,
                        input_tokens=stage_usage.get("input_tokens", 0),
                        output_tokens=stage_usage.get("output_tokens", 0),
                        cached_tokens=stage_usage.get("cached_tokens", 0),
                    )
                elif pricing.pricing_type == "per_image_resolution":
                    cost = self.calculate_image_cost(
                        model,
                        count=stage_usage.get("count", 1),
                        size=stage_usage.get("size", "1024x1024"),
                        quality=stage_usage.get("quality", "standard"),
                    )
                elif pricing.pricing_type == "per_second":
                    cost = self.calculate_video_cost(
                        model,
                        duration_seconds=stage_usage.get("duration_seconds", 0.0),
                    )
                else:
                    logger.warning(f"Unknown pricing type for {model}: {pricing.pricing_type}")
                    continue

                total_cost += cost

            except Exception as e:
                logger.error(f"Failed to calculate cost for {stage_name} ({model}): {e}")
                continue

        return total_cost

    # =========================================================================
    # Credit-based billing
    # =========================================================================

    def estimate_credits(
        self,
        items: int,
        overhead: float,
        per_item: float,
        currency: str = "credits",
    ) -> CostEstimate:
        """Estimate cost in credits (or other unit).

        Generic method for credit-based billing systems.

        Args:
            items: Number of items to generate
            overhead: Fixed overhead cost
            per_item: Cost per item
            currency: Currency unit name (default: "credits")

        Returns:
            CostEstimate with breakdown

        Example:
            >>> estimate = calculator.estimate_credits(
            ...     items=10,
            ...     overhead=3,
            ...     per_item=2,
            ...     currency="credits"
            ... )
            >>> print(f"Total: {estimate.total} {estimate.currency}")
            Total: 23 credits
        """
        if items < 0:
            raise ValueError("Items must be >= 0")
        if overhead < 0 or per_item < 0:
            raise ValueError("Costs must be >= 0")

        total = overhead + (items * per_item)

        return CostEstimate(
            items=items,
            overhead=overhead,
            per_item=per_item,
            total=total,
            currency=currency,
        )

    def calculate_actual_cost(
        self,
        estimated: float,
        usage: dict[str, dict[str, Any]],
    ) -> ActualCost:
        """Calculate actual cost and compare with estimate.

        Args:
            estimated: Originally estimated cost
            usage: Actual usage dictionary (same format as calculate_mixed_usage)

        Returns:
            ActualCost with variance information

        Example:
            >>> actual = calculator.calculate_actual_cost(
            ...     estimated=1.50,
            ...     usage={"stage1": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500}}
            ... )
            >>> print(f"Variance: {actual.variance_percent:.1f}%")
        """
        if estimated < 0:
            raise ValueError("Estimated cost must be >= 0")

        actual_usd = self.calculate_mixed_usage(usage)

        return ActualCost(
            estimated=estimated,
            actual=actual_usd,
            variance_percent=0.0,  # Will be calculated by model validator
            details=usage,
        )

    # =========================================================================
    # Utility methods
    # =========================================================================

    def get_model_pricing(self, model: str) -> Optional[ModelPricing]:
        """Get pricing information for a model.

        Args:
            model: Model identifier

        Returns:
            ModelPricing object or None if not found
        """
        return self.provider.get_model_pricing(model)

    def get_available_models(self) -> list[str]:
        """Get list of all available models.

        Returns:
            List of model identifiers
        """
        return self.provider.get_all_models()

    def refresh_pricing(self) -> bool:
        """Force refresh pricing data from API.

        Returns:
            True if successful, False otherwise
        """
        return self.provider.refresh()
