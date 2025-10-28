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

## Notes

- Data is scraped from the official OpenAI pricing page
- Always verify current prices on [openai.com/api/pricing](https://openai.com/api/pricing/)
- Script uses Playwright for dynamic content loading
- GitHub Actions is free for public repositories

## License

Apache License 2.0 - see [LICENSE](LICENSE)
