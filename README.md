# OpenAI Models Pricing

Automatically updated website with current OpenAI model prices. Data is scraped daily from the official OpenAI website and published on GitHub Pages.

## Features

- Daily automatic price updates via GitHub Actions
- JSON API for integration into your projects
- Web interface for browsing prices
- Price history for the last 90 days
- Search and filter models

## Demo

Site available at: **https://bes-dev.github.io/openai_models_pricing/**

## Project Structure

```
openai_models_pricing/
├── .github/
│   └── workflows/
│       └── update-pricing.yml    # GitHub Actions workflow
├── github_pages/                  # GitHub Pages site
│   ├── index.html                # Main page
│   ├── script.js                 # JavaScript for data display
│   ├── styles.css                # Styles
│   ├── api.json                  # Simplified API (generated)
│   ├── pricing.json              # Full data (generated)
│   └── history.json              # Price history (generated)
├── scripts/
│   └── fetch_openai_pricing.py   # Price scraping script
└── requirements.txt               # Python dependencies
```

## Quick Start

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
- Open https://bes-dev.github.io/openai_models_pricing/
- It may take 1-2 minutes for the site to become available
- Check the Actions tab for the deployment URL in the workflow summary

## API Usage

### Simple API (Recommended)

```bash
curl https://bes-dev.github.io/openai_models_pricing/api.json
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
fetch('https://bes-dev.github.io/openai_models_pricing/api.json')
  .then(res => res.json())
  .then(data => {
    console.log('Models:', data.models);
    console.log('Last updated:', data.timestamp);
  });
```

### Python Example

```python
import requests

url = 'https://bes-dev.github.io/openai_models_pricing/api.json'
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

## How to Calculate Costs

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

For automated cost calculation, see the example script: [`examples/cost_calculator.py`](examples/cost_calculator.py)

This Python script provides a `OpenAICostCalculator` class that:
- Loads pricing data from the API automatically
- Calculates costs for different model types
- Provides helper methods for all pricing models
- Includes working examples

Run it:
```bash
python examples/cost_calculator.py
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
