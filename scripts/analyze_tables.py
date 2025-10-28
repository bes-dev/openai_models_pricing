from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = 'https://platform.openai.com/docs/pricing'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(3000)
    
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')

print(f"Found {len(tables)} tables\n")

# Find the table with image resolutions
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
    if '1024 x 1024' in str(headers):
        print(f"=== Table {i+1}: Image Resolution Pricing ===")
        print(f"Headers: {headers}\n")
        
        rows = table.find_all('tr')[1:]  # Skip header
        for j, row in enumerate(rows[:10], 1):
            cells = [c.get_text(strip=True) for c in row.find_all(['td', 'th'])]
            print(f"Row {j}: {cells}")
        
        print("\n")
        break
