# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin

PORTFOLIO_URL = "https://fika.vc/portfolio"


def scrape() -> List[Dict]:
    """
    Scrape Fika Ventures portfolio companies from their website.
    Returns a list of dicts with company information.
    
    This implementation focuses on extracting data from the HTML structure
    without attempting to populate fields that aren't actually present on the site
    (founders, stage, status are not available on this portfolio page).
    """
    session = requests.Session()
    companies = []
    seen_names = set()
    
    try:
        # Fetch the portfolio page
        response = session.get(PORTFOLIO_URL, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all portfolio items
        portfolio_items = soup.find_all('div', class_='portfolio_item')
        
        for item in portfolio_items:
            try:
                # Extract company name
                name_elem = item.find('h2', class_='portfolio_item_name')
                if not name_elem:
                    continue
                
                company_name = name_elem.get_text(strip=True)
                
                # Skip duplicates
                if company_name in seen_names:
                    continue
                seen_names.add(company_name)
                
                # Extract company URL from logo link
                company_url = None
                link_elem = item.find('a', class_='portfolio_item_logo-link')
                if link_elem and link_elem.get('href'):
                    url = link_elem['href'].strip()
                    if url and url != '#':
                        company_url = url
                
                # Extract description
                description = None
                desc_elem = item.find('div', class_='text-size-regular')
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                
                # Extract sectors/categories from filter slugs
                sectors = []
                filter_container = item.find('div', class_='item-filters')
                if filter_container:
                    filter_slugs = filter_container.find_all('div', class_='item-filter-slug')
                    for slug_elem in filter_slugs:
                        slug_text = slug_elem.get_text(strip=True)
                        if slug_text:
                            # Convert slug to readable format
                            readable = slug_text.replace('-', ' ').title()
                            sectors.append(readable)
                
                # Extract careers/work link if available
                careers_url = None
                green_button = item.find('a', class_='green_button')
                if green_button and not green_button.has_attr('w-condition-invisible'):
                    href = green_button.get('href', '').strip()
                    if href and href != '#':
                        careers_url = href
                
                # Build company record
                # Note: founders, stage, and status are NOT available on this portfolio page
                # These fields are omitted rather than set to None/[] since the site doesn't expose them
                company_record = {
                    "company_name": company_name,
                    "company_url": company_url,
                    "description": description,
                    "sectors": sectors,
                    "careers_url": careers_url,
                    "everywhere_tags": [],
                    "source_url": PORTFOLIO_URL
                }
                
                companies.append(company_record)
                
            except Exception:
                # Skip individual items that fail to parse
                continue
            
            # Be polite between processing items
            time.sleep(0.1)
        
        return companies
    
    except Exception:
        # Return empty list on error
        return []


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
                         "..", "data", "fikaventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
