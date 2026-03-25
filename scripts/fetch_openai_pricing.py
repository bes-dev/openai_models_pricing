#!/usr/bin/env python3
"""
Fetch OpenAI pricing from official website and save to JSON.
This script parses the OpenAI pricing page and extracts model prices.
"""

import json
import re
import sys
from datetime import datetime, timezone
from typing import Dict, Any


PRICING_URL = "https://platform.openai.com/docs/pricing"
OUTPUT_FILE = "github_pages/pricing.json"
API_FILE = "github_pages/api.json"
HISTORY_FILE = "github_pages/history.json"
SUPPORTED_TIERS = ("standard", "batch", "flex", "priority")
PREFERRED_TIER_ORDER = ("standard", "batch", "flex", "priority")


def fetch_html(url: str) -> str:
    """
    Fetch HTML content using Playwright with proper JavaScript rendering.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

    print(f"Fetching {url} with Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Set extra HTTP headers for proper rendering
        page.set_extra_http_headers({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/112.0.0.0 Safari/537.36"),
            "Accept-Language": "en-US,en;q=0.9"
        })

        # Wait for network to be idle (all resources loaded and JS executed)
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except PlaywrightTimeoutError:
            print(f"Warning: Timeout while loading {url}, continuing with partial content")

        # Wait for content to stabilize and render
        try:
            page.wait_for_function(
                """() => {
                    // Wait for content to stabilize (React/Vue rendering)
                    const bodyText = document.body.innerText.trim();
                    return bodyText.length > 1000; // Ensure substantial content loaded
                }""",
                timeout=30000
            )
        except PlaywrightTimeoutError:
            print("Warning: Content stabilization timeout, continuing anyway")

        # Extra delay for any remaining JS execution
        page.wait_for_timeout(2000)

        html_content = page.content()
        browser.close()

        print(f"Fetched {len(html_content)} characters")
        return html_content


def parse_price(text: str) -> float:
    """Extract price from text like '$2.50', '2.50', etc."""
    if not text:
        return 0.0

    # Remove $ and whitespace
    cleaned = re.sub(r'[\$\s,]', '', text)

    # Try to extract first number
    match = re.search(r'(\d+\.?\d*)', cleaned)
    if match:
        return float(match.group(1))
    return 0.0


def normalize_model_key(model_name: str) -> str:
    """Normalize model name for use as a JSON key."""
    return model_name.lower().replace(' ', '-').replace('·', '-')


def normalize_text(text: str) -> str:
    """Normalize text for heading/tier comparisons."""
    return ' '.join(text.strip().lower().split())


def infer_table_tier(table) -> str:
    """Infer pricing tier from the closest preceding heading-like element."""
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'strong', 'em']

    for element in table.find_all_previous(heading_tags, limit=100):
        text = normalize_text(element.get_text(" ", strip=True))
        if text in SUPPORTED_TIERS:
            return text

    return "standard"


def build_tier_payload(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a tier-specific pricing payload from extracted model data."""
    return {
        key: value for key, value in model_data.items()
        if key not in ['model', 'timestamp', 'default_tier', 'available_tiers', 'tiers']
    }


def sync_default_tier_fields(entry: Dict[str, Any]) -> None:
    """Expose a stable top-level view using the preferred default tier."""
    tier_data = entry.get("tiers", {})
    if not tier_data:
        return

    default_tier = next((tier for tier in PREFERRED_TIER_ORDER if tier in tier_data), None)
    if not default_tier:
        default_tier = next(iter(tier_data))

    entry["default_tier"] = default_tier
    entry["available_tiers"] = [tier for tier in PREFERRED_TIER_ORDER if tier in tier_data]

    for field in ["pricing_type", "category", "input", "output", "cached_input", "price", "image_pricing"]:
        if field in tier_data[default_tier]:
            entry[field] = tier_data[default_tier][field]
        elif field in entry:
            del entry[field]


def upsert_tiered_model(
    pricing: Dict[str, Any],
    model_name: str,
    model_data: Dict[str, Any],
    tier: str,
) -> None:
    """Create or update a model entry with tier-specific pricing."""
    model_key = normalize_model_key(model_name)
    tier_payload = build_tier_payload(model_data)

    if model_key not in pricing:
        pricing[model_key] = {
            "model": model_name,
            "timestamp": model_data["timestamp"],
            "tiers": {},
        }

    entry = pricing[model_key]
    entry["tiers"][tier] = tier_payload

    if len(model_name) > len(entry["model"]):
        entry["model"] = model_name

    sync_default_tier_fields(entry)


def parse_image_resolution_table(table, headers: list, pricing: Dict[str, Any], tier: str) -> None:
    """Parse image resolution pricing tables (e.g., 1024x1024, quality-based)."""
    print(f"    Parsing image resolution table for {tier} tier...")

    # Extract resolution headers (e.g., "1024 x 1024", "1024 x 1536")
    resolution_indices = {}
    for idx, header in enumerate(headers):
        if 'x' in header and any(char.isdigit() for char in header):
            # Normalize resolution format: "1024 x 1024" -> "1024x1024"
            resolution = re.sub(r'\s*x\s*', 'x', header)
            resolution_indices[idx] = resolution

    print(f"    Resolution columns: {resolution_indices}")

    # Get quality column index (if exists)
    quality_idx = None
    for idx, header in enumerate(headers):
        if 'quality' in header:
            quality_idx = idx
            break

    rows = table.find_all('tr')[1:]  # Skip header

    current_model = None
    for row_idx, row in enumerate(rows, 1):
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue

        # First cell might be model name or quality
        first_cell = cells[0].get_text(strip=True)

        # Check if this is a quality label
        if first_cell.lower() in ['low', 'medium', 'high', 'standard', 'hd']:
            quality = first_cell.lower()
        # Check if this is a model name
        elif len(first_cell) > 3 and any(c.isalpha() for c in first_cell):
            # Skip header-like names
            if first_cell.lower() in ['model', 'quality']:
                continue
            # Valid model name
            current_model = first_cell
            print(f"    Row {row_idx}: Model = {current_model}")
            quality = 'standard'  # default quality for new model
        else:
            quality = 'standard'  # default

        # Try to find quality in dedicated column if exists
        if quality_idx and quality_idx < len(cells):
            quality_text = cells[quality_idx].get_text(strip=True).lower()
            # Only use if it's a valid quality label
            if quality_text in ['low', 'medium', 'high', 'standard', 'hd']:
                quality = quality_text

        # Skip if no model identified
        if not current_model:
            continue

        # Extract prices for each resolution
        resolution_prices = {}
        for idx, resolution in resolution_indices.items():
            if idx < len(cells):
                price = parse_price(cells[idx].get_text(strip=True))
                if price > 0:
                    resolution_prices[resolution] = price

        if not resolution_prices:
            continue

        model_key = normalize_model_key(current_model)

        if model_key not in pricing:
            pricing[model_key] = {
                "model": current_model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tiers": {},
            }

        entry = pricing[model_key]
        tier_entry = entry["tiers"].setdefault(
            tier,
            {
                "pricing_type": "per_image_resolution",
                "category": "image_generation_token",
                "image_pricing": {},
            },
        )
        tier_entry["image_pricing"][quality] = resolution_prices

        if len(current_model) > len(entry["model"]):
            entry["model"] = current_model

        sync_default_tier_fields(entry)

        print(f"      {quality}: {resolution_prices}")


def parse_pricing_html(html: str) -> Dict[str, Any]:
    """Parse OpenAI pricing HTML and extract model prices."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    pricing = {}

    # Find all tables on the page
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")

    for table_idx, table in enumerate(tables):
        print(f"\nProcessing table {table_idx + 1}...")
        tier = infer_table_tier(table)
        print(f"  Inferred tier: {tier}")

        # Get headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
        else:
            # Try first row as headers
            first_row = table.find('tr')
            if first_row:
                headers = [th.get_text(strip=True).lower() for th in first_row.find_all(['th', 'td'])]

        print(f"  Headers: {headers}")

        # Check if this is an image resolution pricing table
        if any('x' in h and any(char.isdigit() for char in h) for h in headers):
            print(f"  Detected image resolution pricing table")
            parse_image_resolution_table(table, headers, pricing, tier)
            continue

        # Skip if no relevant headers
        if not any(keyword in ' '.join(headers) for keyword in ['model', 'input', 'output', 'price']):
            print(f"  Skipping table (no pricing headers)")
            continue

        # Get all rows
        rows = table.find_all('tr')

        for row_idx, row in enumerate(rows[1:], 1):  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            # First cell is usually model name
            model_name = cells[0].get_text(strip=True)

            # Skip invalid model names
            if not model_name or len(model_name) < 3:
                continue
            if model_name.lower() in ['model', 'tier', '', 'models']:
                continue
            if not any(c.isalnum() for c in model_name):
                continue

            print(f"  Row {row_idx}: {model_name}")

            # Extract prices based on headers
            model_data = {
                "model": model_name,
                "pricing_type": "unknown",
                "category": "unknown",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Try to find input/output prices (for language models)
            for idx, header in enumerate(headers):
                if idx >= len(cells):
                    break

                cell_text = cells[idx].get_text(strip=True)
                price = parse_price(cell_text)

                # Language models (tokens)
                if 'input' in header and 'cached' not in header and price > 0:
                    model_data['input'] = price
                    model_data['pricing_type'] = 'per_1m_tokens'
                elif 'output' in header and price > 0:
                    model_data['output'] = price
                    model_data['pricing_type'] = 'per_1m_tokens'
                elif 'cached input' in header and price > 0:
                    model_data['cached_input'] = price
                # Audio models
                elif 'minute' in header and price > 0:
                    model_data['price'] = price
                    model_data['pricing_type'] = 'per_minute'
                # Video models
                elif 'second' in header and price > 0:
                    model_data['price'] = price
                    model_data['pricing_type'] = 'per_second'
                # Generic price - determine by model name
                elif 'price' in header and price > 0:
                    model_data['price'] = price

            # Determine pricing type and category from model name if not already set
            model_name_lower = model_name.lower()

            # Determine pricing type if still unknown
            if model_data['pricing_type'] == 'unknown' and 'price' in model_data:
                # GPT models (language)
                if any(x in model_name_lower for x in ['gpt', 'o1', 'o3', 'o4']):
                    model_data['pricing_type'] = 'per_1m_tokens'
                # Image generation models
                elif any(x in model_name_lower for x in ['dall-e', 'dall·e']):
                    model_data['pricing_type'] = 'per_image'
                # Video models
                elif 'sora' in model_name_lower:
                    model_data['pricing_type'] = 'per_second'
                # Audio transcription
                elif 'whisper' in model_name_lower:
                    model_data['pricing_type'] = 'per_minute'
                # Text-to-speech
                elif 'tts' in model_name_lower:
                    model_data['pricing_type'] = 'per_1k_chars'
                # Embeddings
                elif 'embedding' in model_name_lower:
                    model_data['pricing_type'] = 'per_1m_tokens'

            # Determine category based on model characteristics
            if 'gpt-image' in model_name_lower:
                model_data['category'] = 'image_generation_token'
            elif any(x in model_name_lower for x in ['dall-e', 'dall·e']):
                model_data['category'] = 'image_generation'
            elif 'sora' in model_name_lower:
                model_data['category'] = 'video_generation'
            elif 'whisper' in model_name_lower:
                model_data['category'] = 'audio_transcription'
            elif 'tts' in model_name_lower:
                model_data['category'] = 'text_to_speech'
            elif 'embedding' in model_name_lower:
                model_data['category'] = 'embeddings'
            elif any(x in model_name_lower for x in ['o1', 'o3', 'o4']) and 'mini' not in model_name_lower:
                model_data['category'] = 'reasoning'
            elif any(x in model_name_lower for x in ['gpt-5', 'gpt-4', 'gpt-3.5', 'davinci', 'babbage']):
                model_data['category'] = 'language_model'
            elif 'computer-use' in model_name_lower:
                model_data['category'] = 'computer_use'
            elif 'storage' in model_name_lower:
                model_data['category'] = 'storage'
            else:
                model_data['category'] = 'other'

            # Only add if has meaningful pricing data
            has_pricing = any(k in model_data for k in ['input', 'output', 'price', 'cached_input'])

            if has_pricing:
                upsert_tiered_model(pricing, model_name, model_data, tier)

                print(f"    Extracted: {model_data}")

    return pricing


def create_api_json(pricing: Dict[str, Any]) -> Dict[str, Any]:
    """Create simplified API JSON."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "models": pricing,
        "timestamp": timestamp,
        "last_updated": timestamp,
        "models_count": len(pricing),
        "source": "openai_official_pricing_page",
    }


def update_history(pricing: Dict[str, Any]) -> None:
    """Update pricing history JSON file."""
    history = []
    
    # Load existing history
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except FileNotFoundError:
        pass
    
    # Create today's entry
    today = datetime.now(timezone.utc).date().isoformat()
    timestamp = datetime.now(timezone.utc).isoformat()
    
    today_entry = {
        "date": today,
        "timestamp": timestamp,
        "models": pricing,
        "models_count": len(pricing),
    }
    
    # Update or append
    updated = False
    for i, entry in enumerate(history):
        if entry.get('date') == today:
            history[i] = today_entry
            updated = True
            break
    
    if not updated:
        history.append(today_entry)
    
    # Keep only last 90 days
    history = sorted(history, key=lambda x: x['date'], reverse=True)[:90]
    
    # Save
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\nHistory updated: {len(history)} days")


def main():
    """Main function."""
    try:
        # Fetch HTML
        html = fetch_html(PRICING_URL)
        
        # Parse pricing
        pricing = parse_pricing_html(html)
        
        if not pricing:
            print("\nWARNING: No pricing data extracted!")
            sys.exit(1)
        
        print(f"\n\nExtracted {len(pricing)} models")
        
        # Save full pricing data
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(pricing, f, indent=2, ensure_ascii=False)
        print(f"Saved to {OUTPUT_FILE}")
        
        # Save API JSON
        api_data = create_api_json(pricing)
        with open(API_FILE, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {API_FILE}")
        
        # Update history
        update_history(pricing)
        
        print("\n✓ Success!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
