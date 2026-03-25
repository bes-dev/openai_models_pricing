"""Basic tests for PricingCalculator."""

import json

import pytest

from openai_pricing_api import PricingCalculator


@pytest.fixture
def calculator(tmp_path):
    """Create a calculator backed by local fixture data instead of the network."""
    cache_file = tmp_path / "pricing_cache.json"
    cache_file.write_text(
        json.dumps(
            {
                "timestamp": "2099-01-01T00:00:00",
                "models": {
                    "gpt-4o": {
                        "model": "gpt-4o",
                        "pricing_type": "per_1m_tokens",
                        "category": "language_model",
                        "input": 2.5,
                        "output": 10.0,
                        "cached_input": 1.25,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return PricingCalculator(cache_file=cache_file)


def test_calculator_initialization(calculator):
    """Test that calculator can be initialized."""
    assert calculator is not None


def test_get_available_models(calculator):
    """Test that available models can be retrieved."""
    models = calculator.get_available_models()
    assert len(models) > 0
    assert isinstance(models, list)


def test_calculate_token_cost(calculator):
    """Test basic token cost calculation."""
    cost = calculator.calculate_token_cost("gpt-4o", input_tokens=1000, output_tokens=500)

    assert cost >= 0
    assert isinstance(cost, float)


def test_invalid_model(calculator):
    """Test that invalid model raises ValueError."""
    try:
        calculator.calculate_token_cost(
            "invalid-model-that-does-not-exist", input_tokens=1000, output_tokens=500
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Model not found" in str(e)


def test_estimate_credits(calculator):
    """Test credit estimation."""
    estimate = calculator.estimate_credits(items=10, overhead=3, per_item=2, currency="credits")

    assert estimate.total == 23
    assert estimate.items == 10
    assert estimate.overhead == 3
    assert estimate.per_item == 2
    assert estimate.currency == "credits"
