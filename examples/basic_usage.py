"""Basic usage examples for openai-pricing library."""

from openai_pricing import PricingCalculator


def example_token_cost():
    """Example: Calculate token-based cost."""
    print("=" * 60)
    print("EXAMPLE 1: Token-Based Cost")
    print("=" * 60)

    calculator = PricingCalculator()

    # GPT-4o
    cost = calculator.calculate_token_cost(
        "gpt-4o",
        input_tokens=1000,
        output_tokens=500
    )
    print(f"\n📝 GPT-4o (1000 in, 500 out): ${cost:.4f}")

    # GPT-5-nano (cheaper alternative)
    cost = calculator.calculate_token_cost(
        "gpt-5-nano",
        input_tokens=1000,
        output_tokens=500
    )
    print(f"📝 GPT-5-nano (1000 in, 500 out): ${cost:.4f}")

    # With cached tokens
    cost = calculator.calculate_token_cost(
        "gpt-4o",
        input_tokens=500,
        output_tokens=500,
        cached_tokens=500  # 50% cached
    )
    print(f"📝 GPT-4o with 50% cache: ${cost:.4f}")


def example_image_cost():
    """Example: Calculate image generation cost."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Image Generation Cost")
    print("=" * 60)

    calculator = PricingCalculator()

    # DALL-E-3 standard
    cost = calculator.calculate_image_cost(
        "dall-e-3",
        count=5,
        size="1024x1024",
        quality="standard"
    )
    print(f"\n🎨 DALL-E-3 (5 × 1024x1024, standard): ${cost:.4f}")

    # DALL-E-3 HD
    cost = calculator.calculate_image_cost(
        "dall-e-3",
        count=5,
        size="1024x1024",
        quality="hd"
    )
    print(f"🎨 DALL-E-3 (5 × 1024x1024, HD): ${cost:.4f}")

    # DALL-E-2 (cheaper alternative)
    cost = calculator.calculate_image_cost(
        "dall-e-2",
        count=10,
        size="1024x1024",
        quality="standard"
    )
    print(f"🎨 DALL-E-2 (10 × 1024x1024, standard): ${cost:.4f}")


def example_mixed_usage():
    """Example: Calculate cost from mixed usage."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Mixed Usage (Multiple Models)")
    print("=" * 60)

    calculator = PricingCalculator()

    # Simulate multi-stage AI pipeline
    usage = {
        "analysis": {
            "model": "gpt-5-nano",
            "input_tokens": 500,
            "output_tokens": 100
        },
        "generation": {
            "model": "gpt-4o",
            "input_tokens": 2000,
            "output_tokens": 800
        },
        "refinement": {
            "model": "gpt-4o",
            "input_tokens": 3500,
            "output_tokens": 2200
        },
        "image_creation": {
            "model": "dall-e-3",
            "count": 10,
            "size": "1024x1024",
            "quality": "standard"
        }
    }

    total = calculator.calculate_mixed_usage(usage)

    print(f"\n🔄 Total pipeline cost: ${total:.4f}")
    print(f"\nBreakdown:")
    for stage, stage_usage in usage.items():
        print(f"  • {stage}: {stage_usage['model']}")


def example_credit_billing():
    """Example: Credit-based billing."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Credit-Based Billing")
    print("=" * 60)

    calculator = PricingCalculator()

    # Estimate cost for batch operation
    estimate = calculator.estimate_credits(
        items=10,           # 10 items
        overhead=3,         # Fixed overhead (analysis + processing)
        per_item=2,         # 2 credits per item
        currency="credits"
    )

    print(f"\n💳 Estimate for 10 items:")
    print(f"  • Overhead: {estimate.overhead} {estimate.currency}")
    print(f"  • Items: {estimate.items} × {estimate.per_item} = {estimate.items * estimate.per_item} {estimate.currency}")
    print(f"  • Total: {estimate.total} {estimate.currency}")

    # Different quality mode
    hq_estimate = calculator.estimate_credits(
        items=10,
        overhead=3,
        per_item=3,  # Premium mode costs more per item
        currency="credits"
    )

    print(f"\n💎 Premium mode for 10 items:")
    print(f"  • Total: {hq_estimate.total} {hq_estimate.currency}")
    print(f"  • Difference: +{hq_estimate.total - estimate.total} {estimate.currency}")


def example_variance_tracking():
    """Example: Track variance between estimated and actual."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Variance Tracking")
    print("=" * 60)

    calculator = PricingCalculator()

    # Simulate estimated cost
    estimated_usd = 1.50

    # Simulate actual usage
    actual_usage = {
        "stage1": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
        "stage2": {"model": "dall-e-3", "count": 8, "size": "1024x1024", "quality": "standard"}
    }

    actual = calculator.calculate_actual_cost(
        estimated=estimated_usd,
        usage=actual_usage
    )

    print(f"\n📊 Cost Analysis:")
    print(f"  • Estimated: ${actual.estimated:.4f}")
    print(f"  • Actual: ${actual.actual:.4f}")
    print(f"  • Variance: {actual.variance_percent:+.1f}%")
    print(f"  • Savings: ${actual.savings:.4f}")
    print(f"  • Over budget: {actual.is_over_budget}")

    if actual.is_over_budget:
        print(f"\n⚠️  Cost exceeded estimate!")
    else:
        print(f"\n✅ Within budget (margin: {abs(actual.variance_percent):.1f}%)")


def example_model_info():
    """Example: Get model pricing information."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Model Pricing Information")
    print("=" * 60)

    calculator = PricingCalculator()

    # Get pricing for specific model
    pricing = calculator.get_model_pricing("gpt-4o")

    if pricing:
        print(f"\n📋 Pricing for {pricing.model}:")
        print(f"  • Type: {pricing.pricing_type}")
        print(f"  • Input: ${pricing.input_price}/1M tokens")
        print(f"  • Output: ${pricing.output_price}/1M tokens")
        if pricing.cached_input_price:
            print(f"  • Cached: ${pricing.cached_input_price}/1M tokens")
        print(f"  • Source: {pricing.source}")

    # List all available models
    models = calculator.get_available_models()
    print(f"\n📦 Total available models: {len(models)}")
    print(f"Examples: {', '.join(models[:5])}...")


def main():
    """Run all examples."""
    example_token_cost()
    example_image_cost()
    example_mixed_usage()
    example_credit_billing()
    example_variance_tracking()
    example_model_info()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
