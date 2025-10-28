# Cost Calculator Examples

This directory contains example scripts demonstrating how to use the OpenAI pricing data.

## cost_calculator.py

A comprehensive cost calculator for OpenAI API usage.

### Features

- **Automatic pricing updates**: Loads latest pricing from API or local file
- **Multiple model types**: Supports language models, image generation, audio, video, and more
- **Detailed cost breakdown**: Shows separate costs for input, output, cached tokens, and images
- **Real-world examples**: Includes practical usage examples for all model types

### Installation

```bash
# Install required dependencies
pip install requests

# For token counting (optional)
pip install tiktoken
```

### Usage

#### Basic Usage

```bash
python cost_calculator.py
```

This will run all examples and show cost calculations for different models.

#### Using in Your Code

```python
from cost_calculator import OpenAICostCalculator

# Initialize calculator
calculator = OpenAICostCalculator()

# Calculate cost for GPT-4o
result = calculator.calculate_language_model_cost(
    model_name="gpt-4o",
    input_tokens=500,
    output_tokens=1500
)
print(f"Total cost: ${result['total_cost']:.6f}")

# Calculate cost for image generation
result = calculator.calculate_image_generation_cost(
    model_name="gpt-image-1",
    num_images=10,
    resolution="1024x1024",
    quality="low",
    input_tokens=100,
    output_tokens=500
)
print(f"Total cost: ${result['total_cost']:.6f}")
```

### API Reference

#### OpenAICostCalculator

Main class for calculating costs.

**Methods:**

- `get_model_pricing(model_name)` - Get pricing data for a specific model
- `calculate_language_model_cost(model_name, input_tokens, output_tokens, cached_input_tokens=0)` - Calculate cost for language models (GPT-4, GPT-3.5, etc.)
- `calculate_image_generation_cost(model_name, num_images=1, resolution="1024x1024", quality="low", input_tokens=0, output_tokens=0)` - Calculate cost for token-based image generation (gpt-image-1)
- `calculate_dalle_cost(model_name, num_images=1, resolution="1024x1024", quality="standard")` - Calculate cost for DALL-E models
- `calculate_audio_cost(model_name, duration_minutes)` - Calculate cost for audio transcription (Whisper)

### Examples Output

The script demonstrates:

1. **GPT-4o language model** - Basic token-based pricing
2. **GPT-4o with cached input** - Using cache to reduce costs
3. **gpt-image-1** - Token-based image generation with quality levels
4. **DALL-E 3** - Fixed price per image
5. **Whisper** - Audio transcription pricing (if available)
6. **Cost comparison** - Compare 100 images across different models

Example output:
```
OpenAI Cost Calculator
==================================================

Example 1: GPT-4o Language Model
--------------------------------------------------
Model: gpt-4o
Input: 500 tokens → $0.002125
Output: 1500 tokens → $0.025500
Total Cost: $0.027625

...

Comparison: Generate 100 images (1024x1024)
--------------------------------------------------
gpt-image-1          (low     ): $   1.31
gpt-image-1-mini     (low     ): $   0.54
dall-e-3             (standard): $  12.00
dall-e-2             (standard): $   1.60
```

### Token Counting

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

### Cost Optimization Tips

1. **Use appropriate quality levels**
   - Low quality images are ~23× cheaper than standard quality
   - Only use high quality when necessary

2. **Leverage cached input**
   - Cached input tokens are 50% cheaper
   - Reuse context across multiple requests

3. **Choose the right model**
   - gpt-image-1-mini is ~50% cheaper than gpt-image-1
   - GPT-3.5 is much cheaper than GPT-4 for simple tasks

4. **Monitor token usage**
   - Test with small samples first
   - Account for system messages and formatting overhead
   - Add 10-20% buffer for production estimates

### Data Source

The calculator loads pricing data from:
1. Local file `github_pages/api.json` (if available)
2. Remote API: https://bes-dev.github.io/openai_models_pricing/api.json

Pricing is updated daily via GitHub Actions.

### Error Handling

The calculator includes error handling for:
- Model not found
- Invalid quality levels
- Invalid resolutions
- Missing pricing data

Errors are returned as `ValueError` with descriptive messages.

### Contributing

To add support for new model types:

1. Add a new calculation method to `OpenAICostCalculator`
2. Add examples to the `main()` function
3. Update this README

### License

Apache License 2.0 - see parent directory [LICENSE](../LICENSE)
