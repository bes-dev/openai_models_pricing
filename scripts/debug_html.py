#!/usr/bin/env python3
"""Debug script to save HTML and analyze structure."""

from playwright.sync_api import sync_playwright

url = "https://openai.com/api/pricing/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    })
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)
    
    html = page.content()
    browser.close()
    
    # Save to file
    with open('github_pages/debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Saved {len(html)} chars to github_pages/debug.html")
    
    # Search for GPT models in HTML
    if 'gpt-4' in html.lower():
        print("Found 'gpt-4' in HTML")
    else:
        print("'gpt-4' NOT found in HTML")
