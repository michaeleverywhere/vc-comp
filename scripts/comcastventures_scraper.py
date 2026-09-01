# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urljoin

def scrape() -> list[dict]:
    """
    Scrape Comcast Ventures portfolio companies from their portfolio page.
    Returns a list of dicts with company data.
    """
    portfolio_url = "https://comcastventures.com/portfolio"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extract portfolio items from the grid
    portfolio_grid = soup.find('div', class_='grid')
    if not portfolio_grid:
        return []
    
    portfolio_items = portfolio_grid.find_all('div', class_='portfolio-item')
    
    for item in portfolio_items:
        try:
            # Get the link element
            link_elem = item.find('a')
            if not link_elem:
                continue
            
            company_url = link_elem.get('href', '').strip()
            if not company_url:
                continue
            
            # Get logo image for additional metadata
            logo_elem = item.find('img')
            logo_url = None
            if logo_elem:
                logo_url = logo_elem.get('src', '').strip()
            
            # Extract title
            title_elem = item.find('h5')
            if not title_elem:
                continue
            
            title_text = title_elem.get_text(strip=True)
            if not title_text:
                continue
            
            # Parse the title to extract company name and status info
            company_name = title_text
            status = None
            exit_info = None
            
            # Check for acquisition
            acq_match = re.search(r'\(Acquired:\s*(.+?)\s+(\d{4})\)', title_text)
            if acq_match:
                company_name = title_text[:acq_match.start()].strip()
                status = "exited"
                exit_info = f"Acquired by {acq_match.group(1)} in {acq_match.group(2)}"
            else:
                # Check for IPO or listing
                listing_match = re.search(r'\(([A-Z]+):\s*(\d{4})\)', title_text)
                if listing_match:
                    company_name = title_text[:listing_match.start()].strip()
                    status = "exited"
                    exit_info = f"IPO on {listing_match.group(1)} in {listing_match.group(2)}"
            
            # Deduplicate
            if company_name in seen_names:
                continue
            seen_names.add(company_name)
            
            # Extract categories/sectors from CSS classes
            sectors = []
            class_str = item.get('class', '')
            if isinstance(class_str, list):
                classes = class_str
            else:
                classes = str(class_str).split() if class_str else []
            
            category_map = {
                'climate-tech': 'Climate Tech',
                'consumer': 'Consumer',
                'data': 'Data & AI',
                'enabling-technologies': 'Enabling Technologies',
                'future-of-work': 'Future of Work',
                'digital-health': 'Health Tech',
                'real': 'Prop Tech',
                'the-home-proptech': 'Prop Tech',
                'sports': 'Sports Tech',
                'enterprise': 'Enterprise'
            }
            
            for cls in classes:
                if cls in category_map:
                    sector = category_map[cls]
                    if sector not in sectors:
                        sectors.append(sector)
            
            # Determine status if not already set
            if status is None:
                if 'active_alt' in classes:
                    status = "active"
                elif 'exits' in classes:
                    status = "exited"
            
            # Build description from available information
            description = None
            if exit_info:
                description = exit_info
            elif sectors:
                # Create a basic description from sectors
                description = f"{company_name} is in the {', '.join(sectors)} sector"
            
            company_record = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description,
                "sectors": sectors,
                "status": status,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            
            companies.append(company_record)
            time.sleep(0.3)
        
        except Exception:
            continue
    
    # Try to fetch portfolio highlights for richer descriptions
    try:
        portfolio_slider = soup.find('div', class_='portfolio-slider')
        if portfolio_slider:
            slider_items = portfolio_slider.find_all('div', class_='card-slider-item')
            
            for slider_item in slider_items:
                try:
                    # Get company name from logo alt or title
                    logo = slider_item.find('img', class_='bg-img')
                    card_logo = slider_item.find('div', class_='card-logo')
                    
                    # Get description from h2
                    desc_elem = slider_item.find('h2')
                    if not desc_elem:
                        continue
                    
                    description_text = desc_elem.get_text(strip=True)
                    
                    # Extract company name from description (usually starts with "CompanyName:")
                    name_match = re.match(r'^([^:]+):\s*(.+)$', description_text)
                    if name_match:
                        highlight_name = name_match.group(1).strip()
                        highlight_desc = name_match.group(2).strip()
                        
                        # Try to match this to an existing company
                        for company in companies:
                            if company['company_name'].lower() == highlight_name.lower():
                                company['description'] = highlight_desc
                                break
                except Exception:
                    continue
    except Exception:
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
                         "..", "data", "comcastventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
