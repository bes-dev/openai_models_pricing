"""Pricing data management with API integration and caching.

Fetches model pricing from external API and caches locally.
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from .models import ModelPricing

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_API_URL = "https://bes-dev.github.io/openai-pricing-api/api.json"
DEFAULT_CACHE_DURATION = timedelta(hours=12)


class PricingProvider:
    """Manages pricing data from API with local caching.

    Example:
        >>> provider = PricingProvider()
        >>> pricing = provider.get_model_pricing("gpt-4o")
        >>> print(f"Input: ${pricing.input_price}/1M tokens")
    """

    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        cache_file: Optional[Path] = None,
        cache_duration: timedelta = DEFAULT_CACHE_DURATION,
    ):
        """Initialize pricing provider.

        Args:
            api_url: URL to fetch pricing data from
            cache_file: Path to cache file (auto-generated if None)
            cache_duration: How long to keep cache valid
        """
        self.api_url = api_url
        self.cache_duration = cache_duration

        # Default cache location
        if cache_file is None:
            cache_dir = Path.home() / ".openai_pricing_api"
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / "pricing_cache.json"

        self.cache_file = cache_file

        # In-memory cache
        self._pricing_data: Optional[dict[str, dict]] = None
        self._cache_timestamp: Optional[datetime] = None

    def get_model_pricing(self, model: str) -> Optional[ModelPricing]:
        """Get pricing for a specific model.

        Args:
            model: Model identifier

        Returns:
            ModelPricing object or None if not found
        """
        data = self._load_pricing()
        model_data = data.get(model)

        if not model_data:
            logger.warning(f"No pricing found for model: {model}")
            return None

        try:
            return ModelPricing(
                model=model,
                pricing_type=model_data.get("pricing_type", "per_1m_tokens"),
                input_price=model_data.get("input"),
                output_price=model_data.get("output"),
                cached_input_price=model_data.get("cached_input"),
                image_pricing=model_data.get("image_pricing"),
                video_price_per_second=model_data.get("price"),
                source=model_data.get("source", "api"),
            )
        except Exception as e:
            logger.error(f"Failed to parse pricing for {model}: {e}")
            return None

    def get_all_models(self) -> list[str]:
        """Get list of all available models.

        Returns:
            List of model identifiers
        """
        data = self._load_pricing()
        return list(data.keys())

    def refresh(self) -> bool:
        """Force refresh pricing data from API.

        Returns:
            True if refresh successful, False otherwise
        """
        try:
            data = self._fetch_from_api()
            self._save_to_cache(data)
            self._pricing_data = data
            self._cache_timestamp = datetime.now()
            logger.info(f"Refreshed pricing data: {len(data)} models")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh pricing data: {e}")
            return False

    def _load_pricing(self) -> dict[str, dict]:
        """Load pricing data from cache or API."""
        # Return in-memory cache if valid
        if self._pricing_data and self._is_cache_valid():
            return self._pricing_data

        # Try to load from file cache
        if self.cache_file.exists():
            try:
                cache_data = self._load_from_cache()
                cache_age = datetime.now() - cache_data["timestamp"]

                if cache_age < self.cache_duration:
                    self._pricing_data = cache_data["models"]
                    self._cache_timestamp = cache_data["timestamp"]
                    logger.debug(f"Loaded {len(self._pricing_data)} models from cache")
                    return self._pricing_data
                else:
                    logger.debug(f"Cache expired (age: {cache_age})")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

        # Fetch from API
        try:
            data = self._fetch_from_api()
            self._save_to_cache(data)
            self._pricing_data = data
            self._cache_timestamp = datetime.now()
            logger.info(f"Fetched {len(data)} models from API")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch from API: {e}")

            # Fallback to expired cache if available
            if self.cache_file.exists():
                try:
                    cache_data = self._load_from_cache()
                    logger.warning("Using expired cache as fallback")
                    self._pricing_data = cache_data["models"]
                    return self._pricing_data
                except Exception as e:
                    logger.error(f"Failed to load fallback cache: {e}")

            # Return empty dict as last resort
            logger.error("No pricing data available")
            return {}

    def _fetch_from_api(self) -> dict[str, dict]:
        """Fetch pricing data from API."""
        logger.debug(f"Fetching pricing from {self.api_url}")
        with urllib.request.urlopen(self.api_url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("models", {})

    def _load_from_cache(self) -> dict:
        """Load data from cache file."""
        with open(self.cache_file, "r") as f:
            data = json.load(f)

        # Parse timestamp
        timestamp_str = data.get("timestamp")
        if timestamp_str:
            data["timestamp"] = datetime.fromisoformat(timestamp_str)
        else:
            data["timestamp"] = datetime.now()

        return data

    def _save_to_cache(self, models: dict[str, dict]):
        """Save pricing data to cache file."""
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "source": self.api_url,
            "models": models,
        }

        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Saved {len(models)} models to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def _is_cache_valid(self) -> bool:
        """Check if in-memory cache is still valid."""
        if not self._cache_timestamp:
            return False
        age = datetime.now() - self._cache_timestamp
        return age < self.cache_duration
