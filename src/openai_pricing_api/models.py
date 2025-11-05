"""Data models for pricing and cost tracking.

All monetary values are in USD unless otherwise specified.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class TokenUsage(BaseModel):
    """Token usage for a single model call.

    Attributes:
        model: Model identifier (e.g., "gpt-4o", "gpt-image-1")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cached_tokens: Number of cached input tokens (optional)
    """

    model: str = Field(..., min_length=1, description="Model identifier")
    input_tokens: int = Field(0, ge=0, description="Input tokens")
    output_tokens: int = Field(0, ge=0, description="Output tokens")
    cached_tokens: int = Field(0, ge=0, description="Cached input tokens")


class ImageUsage(BaseModel):
    """Image generation usage.

    Attributes:
        model: Model identifier (e.g., "dall-e-3")
        count: Number of images generated
        size: Image size (e.g., "1024x1024")
        quality: Image quality ("standard" or "hd")
    """

    model: str = Field(..., min_length=1, description="Model identifier")
    count: int = Field(1, ge=1, description="Number of images")
    size: str = Field("1024x1024", description="Image size")
    quality: str = Field("standard", description="Image quality")

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: str) -> str:
        """Validate quality is either 'standard' or 'hd'."""
        if v not in ("standard", "hd"):
            raise ValueError(f"quality must be 'standard' or 'hd', got '{v}'")
        return v


class CostEstimate(BaseModel):
    """Cost estimate for an operation.

    Attributes:
        items: Number of items (e.g., images, requests, operations)
        overhead: Fixed overhead cost
        per_item: Cost per item
        total: Total estimated cost
        currency: Currency code (default: "credits")
    """

    items: int = Field(..., ge=0, description="Number of items")
    overhead: float = Field(..., ge=0.0, description="Fixed overhead cost")
    per_item: float = Field(..., ge=0.0, description="Cost per item")
    total: float = Field(..., ge=0.0, description="Total cost")
    currency: str = Field("credits", description="Currency unit")

    @model_validator(mode="after")
    def validate_total(self) -> "CostEstimate":
        """Validate that total matches calculation."""
        expected_total = self.overhead + (self.items * self.per_item)
        if abs(self.total - expected_total) > 0.0001:
            raise ValueError(
                f"total ({self.total}) must equal "
                f"overhead ({self.overhead}) + items ({self.items}) × per_item ({self.per_item})"
            )
        return self


class ActualCost(BaseModel):
    """Actual cost after operation completes.

    Tracks variance between estimated and actual costs.

    Attributes:
        estimated: Originally estimated cost
        actual: Actual cost from usage
        variance_percent: Percentage variance (negative = under budget)
        details: Optional detailed breakdown by component
    """

    estimated: float = Field(..., ge=0.0, description="Estimated cost")
    actual: float = Field(..., ge=0.0, description="Actual cost")
    variance_percent: float = Field(..., description="Variance percentage")
    details: dict[str, Any] = Field(default_factory=dict, description="Detailed breakdown")

    @property
    def is_over_budget(self) -> bool:
        """Check if actual cost exceeded estimate."""
        return self.actual > self.estimated

    @property
    def savings(self) -> float:
        """Calculate savings (negative if over budget)."""
        return self.estimated - self.actual

    @model_validator(mode="after")
    def calculate_variance(self) -> "ActualCost":
        """Calculate variance percentage."""
        if self.estimated > 0:
            self.variance_percent = ((self.actual - self.estimated) / self.estimated) * 100
        else:
            self.variance_percent = 0.0
        return self


class ModelPricing(BaseModel):
    """Pricing information for a model.

    Attributes:
        model: Model identifier
        pricing_type: Type of pricing (per_1m_tokens, per_image_resolution, per_second)
        input_price: Price per 1M input tokens (for token-based models)
        output_price: Price per 1M output tokens (for token-based models)
        cached_input_price: Price per 1M cached input tokens (optional)
        image_pricing: Pricing by size and quality (for image models)
        video_price_per_second: Price per second (for video models)
        source: Data source (api, fallback, registry)
    """

    model: str = Field(..., min_length=1, description="Model identifier")
    pricing_type: str = Field(..., description="Pricing type")

    # Token-based pricing
    input_price: Optional[float] = Field(None, ge=0.0, description="Input price per 1M tokens")
    output_price: Optional[float] = Field(None, ge=0.0, description="Output price per 1M tokens")
    cached_input_price: Optional[float] = Field(
        None, ge=0.0, description="Cached input price per 1M tokens"
    )

    # Image pricing
    image_pricing: Optional[dict[str, dict[str, float]]] = Field(
        None, description="Image pricing by quality/size"
    )

    # Video pricing
    video_price_per_second: Optional[float] = Field(
        None, ge=0.0, description="Video price per second"
    )

    # Metadata
    source: str = Field("api", description="Data source")

    @field_validator("pricing_type")
    @classmethod
    def validate_pricing_type(cls, v: str) -> str:
        """Validate pricing type."""
        valid_types = ("per_1m_tokens", "per_image_resolution", "per_second")
        if v not in valid_types:
            raise ValueError(f"pricing_type must be one of {valid_types}, got '{v}'")
        return v
