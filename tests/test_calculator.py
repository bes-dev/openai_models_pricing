"""Basic tests for PricingCalculator."""

from openai_pricing_api import PricingCalculator


def test_calculator_initialization():
    """Test that calculator can be initialized."""
    calculator = PricingCalculator()
    assert calculator is not None


def test_get_available_models():
    """Test that available models can be retrieved."""
    calculator = PricingCalculator()
    models = calculator.get_available_models()
    assert len(models) > 0
    assert isinstance(models, list)


def test_calculate_token_cost():
    """Test basic token cost calculation."""
    calculator = PricingCalculator()

    # Get a model that exists
    models = calculator.get_available_models()
    if not models:
        return  # Skip if no models available

    test_model = models[0]

    # Calculate cost
    cost = calculator.calculate_token_cost(test_model, input_tokens=1000, output_tokens=500)

    assert cost >= 0
    assert isinstance(cost, float)


def test_invalid_model():
    """Test that invalid model raises ValueError."""
    calculator = PricingCalculator()

    try:
        calculator.calculate_token_cost(
            "invalid-model-that-does-not-exist", input_tokens=1000, output_tokens=500
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Model not found" in str(e)


def test_estimate_credits():
    """Test credit estimation."""
    calculator = PricingCalculator()

    estimate = calculator.estimate_credits(items=10, overhead=3, per_item=2, currency="credits")

    assert estimate.total == 23
    assert estimate.items == 10
    assert estimate.overhead == 3
    assert estimate.per_item == 2
    assert estimate.currency == "credits"
