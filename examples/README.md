# OpenAI Pricing - Examples

This directory contains usage examples for the `openai-pricing` Python library.

## 📦 Installation

Before running examples, install the library:

```bash
# From PyPI (after release)
pip install openai-pricing

# From source (for development)
cd ..
pip install -e .
```

## 📖 Available Examples

### `basic_usage.py`

Comprehensive examples demonstrating all library features:

1. **Token-based cost calculation** - Calculate costs for GPT models
2. **Image generation cost** - Calculate costs for DALL-E and image models
3. **Mixed usage** - Calculate costs across multiple models and stages
4. **Credit-based billing** - Estimate costs in custom credit units
5. **Variance tracking** - Compare estimated vs actual costs
6. **Model information** - Get pricing details for specific models

Run with:

```bash
python basic_usage.py
```

## 🚀 Quick Start

### Calculate Token Cost

```python
from openai_pricing import PricingCalculator

calculator = PricingCalculator()

# Calculate cost for GPT-4o
cost = calculator.calculate_token_cost(
    "gpt-4o",
    input_tokens=1000,
    output_tokens=500
)
print(f"Cost: ${cost:.4f}")
```

### Calculate Image Cost

```python
# Calculate cost for DALL-E-3
cost = calculator.calculate_image_cost(
    "dall-e-3",
    count=5,
    size="1024x1024",
    quality="hd"
)
print(f"Cost: ${cost:.4f}")
```

### Mixed Usage (Multiple Models)

```python
# Calculate total cost from multiple stages
usage = {
    "analyze": {
        "model": "gpt-4o",
        "input_tokens": 1000,
        "output_tokens": 500
    },
    "generate": {
        "model": "dall-e-3",
        "count": 5,
        "size": "1024x1024"
    }
}

total_cost = calculator.calculate_mixed_usage(usage)
print(f"Total: ${total_cost:.4f}")
```

### Credit-Based Billing

```python
# Estimate cost in credits
estimate = calculator.estimate_credits(
    items=10,           # Number of items
    overhead=3,         # Fixed overhead
    per_item=2,         # Cost per item
    currency="credits"
)

print(f"Total: {estimate.total} {estimate.currency}")
```

### Variance Tracking

```python
# Compare estimated vs actual cost
actual = calculator.calculate_actual_cost(
    estimated=1.50,
    usage={"stage1": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500}}
)

print(f"Estimated: ${actual.estimated:.4f}")
print(f"Actual: ${actual.actual:.4f}")
print(f"Variance: {actual.variance_percent:+.1f}%")
```

## 💡 Cost Optimization Tips

1. **Use appropriate quality levels**
   - Low quality images are significantly cheaper than high quality
   - Only use HD quality when necessary

2. **Leverage cached input**
   - Cached input tokens are typically 90% cheaper
   - Reuse context across multiple requests

3. **Choose the right model**
   - gpt-image-1-mini is ~50% cheaper than gpt-image-1
   - GPT-5-nano is much cheaper than GPT-4o for simple tasks

4. **Monitor token usage**
   - Test with small samples first
   - Account for system messages and formatting overhead
   - Add 10-20% buffer for production estimates

## 📊 Token Counting

To accurately count tokens before making API calls:

```python
import tiktoken

# For GPT-4o and GPT-4
encoding = tiktoken.encoding_for_model("gpt-4o")

# Count tokens in your text
text = "Your prompt here"
tokens = encoding.encode(text)
token_count = len(tokens)

print(f"Token count: {token_count}")
```

## 🔗 Data Source

The library automatically loads pricing data from:
- **Primary**: https://bes-dev.github.io/openai-pricing/api.json
- **Fallback**: Local cache (~/.openai_pricing/pricing_cache.json)
- **Cache duration**: 12 hours (configurable)

Pricing is updated daily via GitHub Actions and always reflects the latest OpenAI pricing.

## 📚 Documentation

For complete API documentation, see the [main README](../README.md).

## 🔗 Links

- **Pricing API**: https://bes-dev.github.io/openai-pricing/
- **Repository**: https://github.com/bes-dev/openai-pricing
- **Issues**: https://github.com/bes-dev/openai-pricing/issues

## 📄 License

Apache License 2.0 - see [LICENSE](../LICENSE)
