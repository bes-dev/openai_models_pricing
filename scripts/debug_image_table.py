#!/usr/bin/env python3
"""Debug script to analyze image pricing table structure."""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = 'https://platform.openai.com/docs/pricing'

print("Fetching page...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(3000)
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')

print(f"\nFound {len(tables)} tables\n")

# Find image resolution table
for i, table in enumerate(tables):
    headers = []
    header_row = table.find('thead')
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    else:
        first_row = table.find('tr')
        if first_row:
            headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]

    # Look for image resolution table
    if any('1024' in str(h) and 'x' in str(h) for h in headers):
        print(f"=== TABLE {i+1}: Image Resolution Pricing ===")
        print(f"Headers: {headers}\n")

        rows = table.find_all('tr')
        print(f"Total rows: {len(rows)}\n")

        for j, row in enumerate(rows[:20], 0):  # Show first 20 rows
            cells = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
            print(f"Row {j:2d}: {cells}")

        print("\n" + "="*80 + "\n")
        break
