"""Regression tests for tier-aware pricing support."""

import importlib.util
import json
from pathlib import Path

from openai_pricing_api import PricingCalculator
from openai_pricing_api.pricing import PricingProvider


def load_scraper_module():
    """Load the scraper script as a module for direct unit testing."""
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "fetch_openai_pricing.py"
    spec = importlib.util.spec_from_file_location("fetch_openai_pricing", module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_cache(cache_file: Path, models: dict) -> None:
    """Write a valid provider cache file for isolated tests."""
    cache_file.write_text(
        json.dumps(
            {
                "timestamp": "2099-01-01T00:00:00",
                "models": models,
            }
        ),
        encoding="utf-8",
    )


def test_parse_pricing_html_preserves_multiple_tiers_and_defaults_to_standard():
    """Repeated models should keep separate tier prices instead of being overwritten."""
    scraper = load_scraper_module()
    html = """
    <html>
      <body>
        <div>Standard</div>
        <table>
          <thead>
            <tr><th>Model</th><th>Input</th><th>Cached input</th><th>Output</th></tr>
          </thead>
          <tbody>
            <tr><td>gpt-5</td><td>$1.25</td><td>$0.125</td><td>$10.00</td></tr>
            <tr><td>gpt-5-chat-latest</td><td>$1.25</td><td>$0.125</td><td>$10.00</td></tr>
          </tbody>
        </table>
        <div>Priority</div>
        <table>
          <thead>
            <tr><th>Model</th><th>Input</th><th>Cached input</th><th>Output</th></tr>
          </thead>
          <tbody>
            <tr><td>gpt-5</td><td>$2.50</td><td>$0.25</td><td>$20.00</td></tr>
          </tbody>
        </table>
      </body>
    </html>
    """

    pricing = scraper.parse_pricing_html(html)

    assert pricing["gpt-5"]["default_tier"] == "standard"
    assert pricing["gpt-5"]["available_tiers"] == ["standard", "priority"]
    assert pricing["gpt-5"]["input"] == 1.25
    assert pricing["gpt-5"]["output"] == 10.0
    assert pricing["gpt-5"]["tiers"]["standard"]["input"] == 1.25
    assert pricing["gpt-5"]["tiers"]["priority"]["input"] == 2.5
    assert pricing["gpt-5-chat-latest"]["tiers"]["standard"]["output"] == 10.0


def test_pricing_provider_resolves_requested_tier_from_cache(tmp_path):
    """Provider should expose tier-specific views from cached tiered model data."""
    cache_file = tmp_path / "pricing_cache.json"
    write_cache(
        cache_file,
        {
            "gpt-5": {
                "model": "gpt-5",
                "default_tier": "standard",
                "available_tiers": ["standard", "batch"],
                "tiers": {
                    "standard": {
                        "pricing_type": "per_1m_tokens",
                        "category": "language_model",
                        "input": 1.25,
                        "cached_input": 0.125,
                        "output": 10.0,
                    },
                    "batch": {
                        "pricing_type": "per_1m_tokens",
                        "category": "language_model",
                        "input": 0.625,
                        "cached_input": 0.0625,
                        "output": 5.0,
                    },
                },
                "input": 1.25,
                "cached_input": 0.125,
                "output": 10.0,
                "pricing_type": "per_1m_tokens",
                "category": "language_model",
            }
        },
    )

    provider = PricingProvider(cache_file=cache_file)
    default_pricing = provider.get_model_pricing("gpt-5")
    batch_pricing = provider.get_model_pricing("gpt-5", tier="batch")

    assert default_pricing is not None
    assert default_pricing.selected_tier == "standard"
    assert default_pricing.available_tiers == ["standard", "batch"]
    assert default_pricing.input_price == 1.25

    assert batch_pricing is not None
    assert batch_pricing.selected_tier == "batch"
    assert batch_pricing.input_price == 0.625
    assert provider.get_model_pricing("gpt-5", tier="priority") is None


def test_calculator_uses_requested_token_tier(tmp_path):
    """Token cost calculations should respect the selected pricing tier."""
    cache_file = tmp_path / "pricing_cache.json"
    write_cache(
        cache_file,
        {
            "gpt-5": {
                "model": "gpt-5",
                "default_tier": "standard",
                "available_tiers": ["standard", "batch"],
                "tiers": {
                    "standard": {
                        "pricing_type": "per_1m_tokens",
                        "category": "language_model",
                        "input": 1.25,
                        "cached_input": 0.125,
                        "output": 10.0,
                    },
                    "batch": {
                        "pricing_type": "per_1m_tokens",
                        "category": "language_model",
                        "input": 0.625,
                        "cached_input": 0.0625,
                        "output": 5.0,
                    },
                },
                "input": 1.25,
                "cached_input": 0.125,
                "output": 10.0,
                "pricing_type": "per_1m_tokens",
                "category": "language_model",
            }
        },
    )

    calculator = PricingCalculator(cache_file=cache_file)

    standard_cost = calculator.calculate_token_cost("gpt-5", input_tokens=1_000_000, output_tokens=0)
    batch_cost = calculator.calculate_token_cost(
        "gpt-5",
        input_tokens=1_000_000,
        output_tokens=0,
        tier="batch",
    )

    assert standard_cost == 1.25
    assert batch_cost == 0.625


def test_calculator_uses_requested_image_tier(tmp_path):
    """Image generation calculations should resolve prices from the requested tier."""
    cache_file = tmp_path / "pricing_cache.json"
    write_cache(
        cache_file,
        {
            "gpt-image-1": {
                "model": "gpt-image-1",
                "default_tier": "standard",
                "available_tiers": ["standard", "batch"],
                "tiers": {
                    "standard": {
                        "pricing_type": "per_image_resolution",
                        "category": "image_generation_token",
                        "image_pricing": {
                            "standard": {
                                "1024x1024": 0.04,
                            }
                        },
                    },
                    "batch": {
                        "pricing_type": "per_image_resolution",
                        "category": "image_generation_token",
                        "image_pricing": {
                            "standard": {
                                "1024x1024": 0.02,
                            }
                        },
                    },
                },
                "pricing_type": "per_image_resolution",
                "category": "image_generation_token",
                "image_pricing": {
                    "standard": {
                        "1024x1024": 0.04,
                    }
                },
            }
        },
    )

    calculator = PricingCalculator(cache_file=cache_file)

    assert calculator.calculate_image_cost("gpt-image-1", count=2) == 0.08
    assert calculator.calculate_image_cost("gpt-image-1", count=2, tier="batch") == 0.04
