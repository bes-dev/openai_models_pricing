# OpenAI Models Pricing

**Comprehensive OpenAI pricing solution with automated data updates and Python library for cost calculation.**

This project provides two integrated components:

1. **Pricing Data Provider** - Automatically scrapes and publishes OpenAI pricing data via JSON API
2. **Python Library** (`openai-pricing`) - Clean API for calculating costs and tracking usage

## 🎯 Features

### Pricing Data Provider
- Daily automatic price updates via GitHub Actions
- JSON API for integration into your projects
- Web interface for browsing prices
- Price history for the last 90 days
- Search and filter models

### Python Library
- Simple and clean API for cost calculation
- Support for all OpenAI model types (GPT, DALL-E, Whisper, Sora)
- Automatic pricing updates with local caching
- Credit-based billing support
- Variance tracking (estimated vs actual costs)
- Mixed usage calculation across multiple models
- Zero dependencies (only Pydantic required)

## Demo

Site available at: **https://bes-dev.github.io/openai-pricing/**

## 📦 Quick Start - Python Library

Install the library:

```bash
pip install openai-pricing
```

Calculate costs:

```python
from openai_pricing import PricingCalculator

calculator = PricingCalculator()

# Calculate cost for GPT-4o
cost = calculator.calculate_token_cost(
    "gpt-4o",
    input_tokens=1000,
    output_tokens=500
)
print(f"Cost: ${cost:.4f}")  # Cost: $0.0125

# Calculate cost for DALL-E-3
cost = calculator.calculate_image_cost(
    "dall-e-3",
    count=5,
    size="1024x1024",
    quality="hd"
)
print(f"Cost: ${cost:.4f}")  # Cost: $0.4000

# Mixed usage (multiple models)
usage = {
    "analyze": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
    "generate": {"model": "dall-e-3", "count": 5, "size": "1024x1024"}
}
total = calculator.calculate_mixed_usage(usage)
print(f"Total: ${total:.4f}")
```

For complete library documentation, see [Python Library Usage](#-python-library-usage) section.

## 📁 Project Structure

```
openai-pricing/
├── .github/workflows/
│   ├── update-pricing.yml         # Daily pricing updates
│   ├── publish-pypi.yml           # PyPI publishing (WIP)
│   └── tests.yml                  # Library tests (WIP)
├── github_pages/                   # GitHub Pages site
│   ├── index.html                 # Web interface
│   ├── script.js                  # Frontend JavaScript
│   ├── styles.css                 # Styling
│   ├── api.json                   # Simplified API (generated)
│   ├── pricing.json               # Full data (generated)
│   └── history.json               # Price history (generated)
├── scripts/
│   └── fetch_openai_pricing.py    # Price scraping script
├── src/openai_pricing/             # Python library source
│   ├── __init__.py
│   ├── calculator.py              # Main calculator class
│   ├── pricing.py                 # Pricing data provider
│   └── models.py                  # Pydantic data models
├── examples/
│   ├── basic_usage.py             # Library usage examples
│   └── README.md                  # Examples documentation
├── pyproject.toml                 # Python package configuration
└── requirements.txt               # Scraper dependencies
```

## 🚀 Quick Start

### Option 1: Use Python Library (Recommended)

```bash
pip install openai-pricing
```

See [Python Library Usage](#-python-library-usage) for full documentation.

### Option 2: Fork Repository for Custom Data Provider

### 1. Fork the Repository

Fork this repository to your GitHub account.

### 2. Enable GitHub Pages

**Important:** You must enable GitHub Pages before the workflow can deploy.

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select **GitHub Actions** from the dropdown
5. Click **Save** (if available)

> **Note:** If you don't see the "GitHub Actions" option:
> - Make sure your repository is **public** (or you have GitHub Pro for private repos)
> - The workflow must run at least once to create the deployment
> - You may need to wait a few seconds and refresh the page

### 3. Enable GitHub Actions

1. Go to the **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The workflow will run automatically on push or on schedule (daily at 12:00 UTC)

### 4. Run Workflow Manually

1. Go to **Actions** → **Update OpenAI Pricing**
2. Click **"Run workflow"** dropdown (right side)
3. Select branch (usually `main` or `master`)
4. Click green **"Run workflow"** button
5. Wait for completion (~2-3 minutes)
6. If it fails with "Pages not enabled", go back to step 2 and enable Pages first

### 5. Check the Result

After the workflow completes successfully:
- Open https://bes-dev.github.io/openai-pricing/
- It may take 1-2 minutes for the site to become available
- Check the Actions tab for the deployment URL in the workflow summary

## API Usage

### Simple API (Recommended)

```bash
curl https://bes-dev.github.io/openai-pricing/api.json
```

Response:
```json
{
  "models": {
    "gpt-4o": {
      "model": "gpt-4o",
      "pricing_type": "per_1m_tokens",
      "input": 2.5,
      "output": 10.0,
      "timestamp": "2025-01-27T12:00:00Z"
    }
  },
  "timestamp": "2025-01-27T12:00:00Z",
  "models_count": 20,
  "source": "openai_official_pricing_page"
}
```

### JavaScript Example

```javascript
fetch('https://bes-dev.github.io/openai-pricing/api.json')
  .then(res => res.json())
  .then(data => {
    console.log('Models:', data.models);
    console.log('Last updated:', data.timestamp);
  });
```

### Python Example

```python
import requests

url = 'https://bes-dev.github.io/openai-pricing/api.json'
data = requests.get(url).json()

# Filter by category
for model_name, model_data in data['models'].items():
    if model_data.get('category') == 'image_generation_token':
        print(f"{model_name} ({model_data['category']}):")
        print(f"  Input: ${model_data.get('input', 0)}/1M tokens")
        print(f"  Output: ${model_data.get('output', 0)}/1M tokens")
        print()

# Or show all models with their categories
for model_name, model_data in data['models'].items():
    category = model_data.get('category', 'unknown')
    pricing_type = model_data.get('pricing_type', 'unknown')
    print(f"{model_name}: {category} ({pricing_type})")
```

### Available Endpoints

- `/api.json` - Simplified data (recommended)
- `/pricing.json` - Full data with all details
- `/history.json` - Price change history for the last 90 days

## Local Testing

### Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Run the Script

```bash
python scripts/fetch_openai_pricing.py
```

This will create files in the `github_pages/` directory:
- `pricing.json`
- `api.json`
- `history.json`

### View Results

Open `github_pages/index.html` in your browser.

## Update Schedule

GitHub Actions workflow runs:
- **Daily at 12:00 UTC** (automatically)
- **On push to master/main** (automatically)
- **Manually** via GitHub Actions web interface

## Configuration

### Change Schedule

Edit `.github/workflows/update-pricing.yml`:

```yaml
schedule:
  - cron: '0 12 * * *'  # Daily at 12:00 UTC
```

Examples:
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * *'` - Daily at midnight UTC
- `'0 12 * * 1'` - Every Monday at 12:00 UTC

### Change Pricing URL

Edit `scripts/fetch_openai_pricing.py`:

```python
PRICING_URL = "https://platform.openai.com/docs/pricing"  # API docs (recommended)
# OR
PRICING_URL = "https://openai.com/api/pricing/"  # Marketing page (limited data)
```

**Note:** The API docs URL (`platform.openai.com`) contains more comprehensive pricing data (60+ models) compared to the marketing page.

## Data Structure

### pricing.json

Full model data:

```json
{
  "gpt-4o": {
    "model": "gpt-4o",
    "pricing_type": "per_1m_tokens",
    "category": "language_model",
    "input": 2.5,
    "output": 10.0,
    "timestamp": "2025-01-27T12:00:00Z"
  },
  "gpt-image-1": {
    "model": "gpt-image-1",
    "pricing_type": "per_1m_tokens",
    "category": "image_generation_token",
    "input": 10.0,
    "output": 40.0,
    "timestamp": "2025-01-27T12:00:00Z"
  },
  "dall-e-3": {
    "model": "dall-e-3",
    "pricing_type": "per_image",
    "category": "image_generation",
    "price": 0.04,
    "timestamp": "2025-01-27T12:00:00Z"
  }
}
```

### history.json

Price change history:

```json
[
  {
    "date": "2025-01-27",
    "timestamp": "2025-01-27T12:00:00Z",
    "models": { ... },
    "models_count": 20
  },
  {
    "date": "2025-01-26",
    "timestamp": "2025-01-26T12:00:00Z",
    "models": { ... },
    "models_count": 19
  }
]
```

## Data Fields

Each model in the JSON has the following fields:

- `model` - Model name
- `pricing_type` - How the model is billed (per_1m_tokens, per_image, per_second, etc.)
- `category` - Model category (see below)
- `input` - Input price (for token-based models)
- `output` - Output price (for token-based models)
- `cached_input` - Cached input price (if available)
- `price` - Fixed price (for non-token models)
- `timestamp` - When the data was last updated

### Pricing Types

- `per_1m_tokens` - Price per 1 million tokens (language, image-gen, embeddings)
- `per_image` - Price per image (DALL-E)
- `per_second` - Price per second (Sora video generation)
- `per_minute` - Price per minute (Whisper audio transcription)
- `per_1k_chars` - Price per 1K characters (TTS)

### Categories

- `language_model` - GPT-5, GPT-4, GPT-3.5, davinci, babbage
- `reasoning` - o1-pro, o3-pro, o3-deep-research
- `image_generation_token` - gpt-image-1 (token-based image generation)
- `image_generation` - DALL-E (fixed price per image)
- `video_generation` - Sora models
- `audio_transcription` - Whisper models
- `text_to_speech` - TTS models
- `embeddings` - text-embedding models
- `computer_use` - Computer use models
- `storage` - Storage pricing
- `other` - Other models

---

## 📚 Python Library Usage

The `openai-pricing` Python library provides a clean API for calculating costs across all OpenAI model types.

### Installation

```bash
# From PyPI
pip install openai-pricing

# From source (for development)
git clone https://github.com/bes-dev/openai-pricing.git
cd openai-pricing
pip install -e .
```

### Basic Usage

```python
from openai_pricing import PricingCalculator

calculator = PricingCalculator()
```

### API Reference

#### `calculate_token_cost(model, input_tokens=0, output_tokens=0, cached_tokens=0)`

Calculate cost for token-based models (GPT-4, GPT-3.5, embeddings, etc.).

```python
# GPT-4o
cost = calculator.calculate_token_cost(
    "gpt-4o",
    input_tokens=1000,
    output_tokens=500
)
print(f"${cost:.4f}")  # $0.0125

# With cached tokens
cost = calculator.calculate_token_cost(
    "gpt-4o",
    input_tokens=500,
    output_tokens=500,
    cached_tokens=500  # 90% cheaper
)
```

#### `calculate_image_cost(model, count=1, size="1024x1024", quality="standard")`

Calculate cost for image generation (DALL-E, gpt-image-1).

```python
# DALL-E-3
cost = calculator.calculate_image_cost(
    "dall-e-3",
    count=5,
    size="1024x1024",
    quality="hd"
)
print(f"${cost:.4f}")  # $0.4000

# gpt-image-1
cost = calculator.calculate_image_cost(
    "gpt-image-1",
    count=10,
    size="1024x1024",
    quality="low"
)
```

#### `calculate_video_cost(model, duration_seconds)`

Calculate cost for video generation (Sora).

```python
cost = calculator.calculate_video_cost(
    "sora-2",
    duration_seconds=30
)
```

#### `calculate_mixed_usage(usage)`

Calculate total cost from multiple models and stages.

```python
usage = {
    "analysis": {
        "model": "gpt-4o",
        "input_tokens": 1000,
        "output_tokens": 500
    },
    "generation": {
        "model": "gpt-4o",
        "input_tokens": 2000,
        "output_tokens": 800
    },
    "images": {
        "model": "dall-e-3",
        "count": 5,
        "size": "1024x1024",
        "quality": "standard"
    }
}

total = calculator.calculate_mixed_usage(usage)
print(f"Total: ${total:.4f}")
```

#### `estimate_credits(items, overhead, per_item, currency="credits")`

Estimate cost in credits or custom units.

```python
estimate = calculator.estimate_credits(
    items=10,           # Number of items
    overhead=3,         # Fixed overhead
    per_item=2,         # Cost per item
    currency="credits"
)

print(f"Total: {estimate.total} {estimate.currency}")  # Total: 23 credits
print(f"Breakdown: {estimate.overhead} + ({estimate.items} × {estimate.per_item})")
```

#### `calculate_actual_cost(estimated, usage)`

Calculate actual cost and compare with estimate (variance tracking).

```python
# Charge user 23 credits (estimated)
estimated_usd = 23 * 0.05  # Convert to USD

# After generation, calculate actual cost
actual = calculator.calculate_actual_cost(
    estimated=estimated_usd,
    usage={
        "stage1": {"model": "gpt-4o", "input_tokens": 1000, "output_tokens": 500},
        "stage2": {"model": "dall-e-3", "count": 5}
    }
)

print(f"Estimated: ${actual.estimated:.4f}")
print(f"Actual: ${actual.actual:.4f}")
print(f"Variance: {actual.variance_percent:+.1f}%")
print(f"Is over budget: {actual.is_over_budget}")
print(f"Savings/Loss: ${actual.savings:.4f}")
```

#### `get_model_pricing(model)`

Get pricing information for a specific model.

```python
pricing = calculator.get_model_pricing("gpt-4o")

if pricing:
    print(f"Model: {pricing.model}")
    print(f"Type: {pricing.pricing_type}")
    print(f"Input: ${pricing.input_price}/1M tokens")
    print(f"Output: ${pricing.output_price}/1M tokens")
    if pricing.cached_input_price:
        print(f"Cached: ${pricing.cached_input_price}/1M tokens")
```

#### `get_available_models()`

Get list of all available models.

```python
models = calculator.get_available_models()
print(f"Available models: {len(models)}")
print(models[:5])  # ['gpt-4o', 'gpt-5', 'dall-e-3', ...]
```

#### `refresh_pricing()`

Force refresh pricing data from API.

```python
success = calculator.refresh_pricing()
if success:
    print("Pricing data refreshed successfully")
```

### Configuration

#### Custom API URL

```python
calculator = PricingCalculator(
    api_url="https://your-custom-api.com/pricing.json"
)
```

#### Custom Cache Location

```python
from pathlib import Path

calculator = PricingCalculator(
    cache_file=Path("/custom/path/pricing_cache.json")
)
```

#### Custom Cache Duration

```python
from datetime import timedelta

calculator = PricingCalculator(
    cache_duration=timedelta(hours=24)  # Cache for 24 hours
)
```

### Data Models

#### `CostEstimate`

```python
class CostEstimate:
    items: int              # Number of items
    overhead: float         # Fixed overhead
    per_item: float         # Cost per item
    total: float            # Total cost
    currency: str           # Currency unit
```

#### `ActualCost`

```python
class ActualCost:
    estimated: float        # Estimated cost
    actual: float           # Actual cost
    variance_percent: float # Variance percentage
    is_over_budget: bool    # True if over budget
    savings: float          # Savings (negative if over)
    details: dict           # Detailed breakdown
```

#### `ModelPricing`

```python
class ModelPricing:
    model: str                    # Model identifier
    pricing_type: str             # Type of pricing
    input_price: Optional[float]  # Input price per 1M tokens
    output_price: Optional[float] # Output price per 1M tokens
    cached_input_price: Optional[float]
    image_pricing: Optional[dict] # Image pricing by size/quality
    video_price_per_second: Optional[float]
    source: str                   # Data source
```

### Examples

Complete examples are available in the [`examples/`](examples/) directory:

```bash
python examples/basic_usage.py
```

This will demonstrate:
1. Token-based cost calculation
2. Image generation cost
3. Mixed usage calculation
4. Credit-based billing
5. Variance tracking
6. Model information retrieval

### Error Handling

The library raises `ValueError` for invalid inputs:

```python
try:
    cost = calculator.calculate_token_cost("invalid-model", input_tokens=1000)
except ValueError as e:
    print(f"Error: {e}")  # Error: Model not found: invalid-model
```

### Caching

The library automatically caches pricing data:
- **Location**: `~/.openai_pricing/pricing_cache.json`
- **Duration**: 12 hours (configurable)
- **Fallback**: Uses cached data if API is unavailable
- **Update**: Automatically refreshes expired cache

To force refresh:

```python
calculator.refresh_pricing()
```

### Integration with tiktoken

For accurate token counting:

```python
import tiktoken
from openai_pricing import PricingCalculator

# Count tokens
encoding = tiktoken.encoding_for_model("gpt-4o")
input_tokens = len(encoding.encode("Your input text"))
output_tokens = len(encoding.encode("Model response"))

# Calculate cost
calculator = PricingCalculator()
cost = calculator.calculate_token_cost(
    "gpt-4o",
    input_tokens=input_tokens,
    output_tokens=output_tokens
)
```

---

## How to Calculate Costs (Manual Method)

This section explains how to use the pricing data to calculate the cost of using different OpenAI models.

### Understanding Tokens

**What is a token?** A token is the basic unit of text processing in OpenAI models. It can be a word, subword, punctuation mark, or symbol.

**Rule of thumb:**
- 1 token ≈ 4 characters of English text
- 1,000 tokens ≈ 750 English words
- 100 tokens ≈ 75 words

**Example:** The sentence "Hello, how are you today?" contains approximately 6-7 tokens.

### Cost Calculation Formulas

#### 1. Language Models (per_1m_tokens)

Models: GPT-4, GPT-3.5, o1, embeddings, etc.

**Formula:**
```
Total Cost = (Input Tokens / 1,000,000 × Input Price) + (Output Tokens / 1,000,000 × Output Price)
```

**Example with GPT-4o:**
- Input price: $2.50 / 1M tokens
- Output price: $10.00 / 1M tokens
- Your request: 500 input tokens, 1,500 output tokens

```
Cost = (500 / 1,000,000 × $2.50) + (1,500 / 1,000,000 × $10.00)
     = $0.00125 + $0.015
     = $0.01625 (≈ $0.016)
```

**With cached input:**
```
Total Cost = (Cached Input / 1,000,000 × Cached Price) + (New Input / 1,000,000 × Input Price) + (Output / 1,000,000 × Output Price)
```

#### 2. Image Generation - Token-based (image_generation_token)

Models: gpt-image-1, gpt-image-1-mini

These models have **two pricing components**:

**A) Text tokens (for your prompt):**
```
Text Cost = (Input Tokens / 1,000,000 × Input Price) + (Output Tokens / 1,000,000 × Output Price)
```

**B) Image generation (per image by resolution and quality):**
```
Image Cost = Number of Images × Price per Image (from image_pricing)
```

**Example with gpt-image-1:**
- Input: $10.00 / 1M tokens
- Output: $40.00 / 1M tokens
- Image (low quality, 1024x1024): $0.011 / image

Generate 1 image with prompt "A beautiful sunset over mountains" (≈10 tokens input, ≈50 tokens output):

```
Text Cost = (10 / 1,000,000 × $10.00) + (50 / 1,000,000 × $40.00)
          = $0.0001 + $0.002 = $0.0021

Image Cost = 1 × $0.011 = $0.011

Total Cost = $0.0021 + $0.011 = $0.0131 (≈ $0.013)
```

**Quality comparison** (1 image, 1024x1024):
- Low quality: $0.011 per image
- Medium quality: $0.063 per image (5.7× more expensive)
- High quality: $0.25 per image (23× more expensive)

**Resolution comparison** (low quality):
- 1024x1024: $0.011
- 1024x1536: $0.016 (45% more expensive)
- 1536x1024: $0.016 (45% more expensive)

#### 3. Image Generation - Fixed Price (image_generation)

Models: DALL-E 3, DALL-E 2

**Formula:**
```
Total Cost = Number of Images × Price per Resolution
```

**Example with DALL-E 3:**
- 1024x1024: $0.12 per image
- 1024x1536: $0.12 per image

```
Cost for 5 images (1024x1024) = 5 × $0.12 = $0.60
```

#### 4. Audio Transcription (audio_transcription)

Models: Whisper

**Formula:**
```
Total Cost = Audio Duration (minutes) × Price per Minute
```

**Example:**
- Price: $0.006 / minute
- Audio: 15 minutes

```
Cost = 15 × $0.006 = $0.09
```

#### 5. Text-to-Speech (text_to_speech)

Models: TTS

**Formula:**
```
Total Cost = (Characters / 1,000) × Price per 1K Characters
```

**Example:**
- Price: $0.015 / 1K characters
- Text: 5,000 characters

```
Cost = (5,000 / 1,000) × $0.015 = $0.075
```

#### 6. Video Generation (video_generation)

Models: Sora

**Formula:**
```
Total Cost = Duration (seconds) × Price per Second
```

**Example:**
- Price: $0.05 / second
- Video: 30 seconds

```
Cost = 30 × $0.05 = $1.50
```

### Practical Tips

1. **Use the tiktoken library** to count tokens accurately before making API calls:
   ```python
   import tiktoken

   encoding = tiktoken.encoding_for_model("gpt-4o")
   tokens = encoding.encode("Your text here")
   token_count = len(tokens)
   ```

2. **Monitor your usage** in the OpenAI dashboard to track actual token consumption.

3. **Optimize costs:**
   - Use lower-quality image generation when high quality isn't needed
   - Use smaller models (e.g., GPT-3.5 instead of GPT-4) for simpler tasks
   - Cache frequently used prompts to benefit from cached input pricing
   - Keep prompts concise to reduce input token count

4. **Estimate before production:**
   - Test with small samples to measure actual token usage
   - Account for system messages and API formatting overhead
   - Add 10-20% buffer for unexpected token usage

5. **Image token consumption varies:**
   - Low quality: ~85 tokens per image
   - Medium quality: ~300-400 tokens per image
   - High quality: ~765 tokens per image

### Cost Comparison Example

Generate 100 images with text prompt (1024x1024):

| Model | Quality | Text Cost | Image Cost | Total Cost |
|-------|---------|-----------|------------|------------|
| gpt-image-1-mini | Low | $0.11 | $0.50 | **$0.61** |
| gpt-image-1 | Low | $0.21 | $1.10 | **$1.31** |
| gpt-image-1-mini | Medium | $0.11 | $1.50 | **$1.61** |
| DALL-E 2 | Standard | $0 | $1.60 | **$1.60** |
| gpt-image-1-mini | High | $0.11 | $5.20 | **$5.31** |
| gpt-image-1 | Medium | $0.21 | $6.30 | **$6.51** |
| DALL-E 3 | Standard | $0 | $12.00 | **$12.00** |
| gpt-image-1 | High | $0.21 | $25.00 | **$25.21** |

*Assumes 1,000 input tokens and 5,000 output tokens for text processing.*

### Automated Cost Calculator

For automated cost calculation, use the `openai-pricing` Python library:

```bash
pip install openai-pricing
```

See the [Python Library Usage](#-python-library-usage) section for complete documentation.

Or run the examples:
```bash
python examples/basic_usage.py
```

### Additional Resources

- **Official Pricing Page:** https://openai.com/api/pricing/
- **OpenAI Documentation:** https://platform.openai.com/docs/
- **Tokenizer Tool:** https://platform.openai.com/tokenizer
- **tiktoken Library:** https://github.com/openai/tiktoken

## Notes

- Data is scraped from the official OpenAI pricing page
- Always verify current prices on [openai.com/api/pricing](https://openai.com/api/pricing/)
- Script uses Playwright for dynamic content loading
- GitHub Actions is free for public repositories

## License

Apache License 2.0 - see [LICENSE](LICENSE)
