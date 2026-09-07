# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Cambridge Innovation Capital portfolio companies from the Start Codon accelerator.
    Returns a list of portfolio company dictionaries.
    """
    portfolio_url = "https://cic.vc/portfolio"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # Fetch the main portfolio page
        response = session.get(portfolio_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all portfolio company grid items in the "Active Portfolio" section
        grid_container = soup.find('div', class_='company-grid')
        if not grid_container:
            return companies
        
        grid_items = grid_container.find_all('div', class_='grid-item')
        
        for item in grid_items:
            try:
                # Extract company name from h4 tag
                company_name_elem = item.find('h4')
                if not company_name_elem:
                    continue
                
                company_name = company_name_elem.get_text(strip=True)
                
                # Skip duplicates and empty names
                if not company_name or company_name in seen_names:
                    continue
                seen_names.add(company_name)
                
                # Extract description from the paragraph following the name
                description = None
                desc_elem = item.find('p', class_='mb-0')
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                
                # Extract company URL from the link with class 'full-banner-arrow-link'
                company_url = None
                link_elem = item.find('a', class_='full-banner-arrow-link')
                if link_elem and link_elem.get('href'):
                    company_url = link_elem.get('href')
                
                # Build company record - only include fields that actually have data
                company_record = {
                    'company_name': company_name,
                    'company_url': company_url,
                    'description': description,
                    'everywhere_tags': [],
                    'source_url': portfolio_url
                }
                
                companies.append(company_record)
                time.sleep(0.3)
                
            except (AttributeError, IndexError, TypeError):
                continue
        
    except requests.RequestException:
        pass
    
    return companies


# --- auto-appended runner (trusted template, not LLM output) -----------------
if __name__ == "__main__":
    import json as _json, os as _os, sys as _sys
    from datetime import datetime as _dt, timezone as _tz
    _records = scrape()
    _now = _dt.now(_tz.utc).replace(microsecond=0).isoformat()
    for _r in _records:
        _r.setdefault("everywhere_tags", [])
        _r.setdefault("scraped_at", _now)
    _out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                         "..", "data", "cambridgeinnovationcapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
