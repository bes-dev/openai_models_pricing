# OpenAI Models Pricing

Automatically updated website with current OpenAI model prices. Data is scraped daily from the official OpenAI website and published on GitHub Pages.

## Features

- Daily automatic price updates via GitHub Actions
- JSON API for integration into your projects
- Web interface for browsing prices
- Price history for the last 90 days
- Search and filter models

## Demo

Site available at: `https://<your-username>.github.io/openai_models_pricing/`

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

1. Go to Settings → Pages
2. Source: select "GitHub Actions"
3. Save settings

### 3. Enable GitHub Actions

1. Go to the Actions tab
2. Click "I understand my workflows, go ahead and enable them"
3. Workflow will run automatically on push or on schedule (daily at 12:00 UTC)

### 4. Run Workflow Manually (Optional)

1. Go to Actions → Update OpenAI Pricing
2. Click "Run workflow" → "Run workflow"
3. Wait for completion (~1-2 minutes)

### 5. Check the Result

Open `https://<your-username>.github.io/openai_models_pricing/`

## API Usage

### Simple API (Recommended)

```bash
curl https://<your-username>.github.io/openai_models_pricing/api.json
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
fetch('https://<your-username>.github.io/openai_models_pricing/api.json')
  .then(res => res.json())
  .then(data => {
    console.log('Models:', data.models);
    console.log('Last updated:', data.timestamp);
  });
```

### Python Example

```python
import requests

url = 'https://<your-username>.github.io/openai_models_pricing/api.json'
data = requests.get(url).json()

for model_name, model_data in data['models'].items():
    print(f"{model_name}:")
    if 'input' in model_data:
        print(f"  Input: ${model_data['input']}/1M tokens")
    if 'output' in model_data:
        print(f"  Output: ${model_data['output']}/1M tokens")
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
PRICING_URL = "https://openai.com/api/pricing/"
```

## Data Structure

### pricing.json

Full model data:

```json
{
  "gpt-4o": {
    "model": "gpt-4o",
    "pricing_type": "per_1m_tokens",
    "input": 2.5,
    "output": 10.0,
    "timestamp": "2025-01-27T12:00:00Z"
  },
  "dall-e-3": {
    "model": "dall-e-3",
    "pricing_type": "per_image",
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

## Pricing Types

- `per_1m_tokens` - Language models (GPT, o1, o3, embeddings) - price per 1M tokens
- `per_image` - Image generation (DALL-E) - price per image
- `per_second` - Video generation (Sora) - price per second
- `per_minute` - Audio transcription (Whisper) - price per minute
- `per_1k_chars` - Text-to-speech (TTS) - price per 1K characters
- `unknown` - Unable to determine pricing type

## Notes

- Data is scraped from the official OpenAI pricing page
- Always verify current prices on [openai.com/api/pricing](https://openai.com/api/pricing/)
- Script uses Playwright for dynamic content loading
- GitHub Actions is free for public repositories

## License

MIT License - see [LICENSE](LICENSE)
