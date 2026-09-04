# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import bs4
import json
import re
import time
from typing import List, Dict, Optional

def scrape() -> List[Dict]:
    """
    Scrapes Mubadala Capital portfolio companies.
    Extracts data from portfolio page HTML structure.
    Returns a list of dicts with company information.
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    portfolio_url = "https://mubadalacapital.com/portfolio"
    companies = []
    seen = set()
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = bs4.BeautifulSoup(resp.content, 'html.parser')
    
    # Find all portfolio item links
    items = soup.find_all('a', class_='collection_list_item')
    
    for item in items:
        try:
            # Extract company name
            name_elem = item.find('div', attrs={'fs-list-field': 'name'})
            if not name_elem:
                continue
            
            company_name = name_elem.get_text(strip=True)
            if not company_name or company_name in seen:
                continue
            seen.add(company_name)
            
            # Extract company URL from href
            company_url = item.get('href')
            if company_url and not company_url.startswith('http'):
                company_url = None
            
            # Extract description from direction field (seems to contain sector description)
            desc_elem = item.find('div', attrs={'fs-list-field': 'direction'})
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract all sectors
            sector_tags = item.find_all('div', attrs={'fs-list-field': 'sector'})
            sectors = []
            for tag in sector_tags:
                sector_text = tag.get_text(strip=True)
                if sector_text and sector_text not in sectors:
                    sectors.append(sector_text)
            
            # Extract strategy (stage)
            strategy_elem = item.find('div', attrs={'fs-list-field': 'strategy'})
            stage = strategy_elem.get_text(strip=True) if strategy_elem else None
            
            # Extract all geographies
            geo_tags = item.find_all('div', attrs={'fs-list-field': 'geography'})
            geographies = []
            for tag in geo_tags:
                geo_text = tag.get_text(strip=True)
                if geo_text and geo_text not in geographies:
                    geographies.append(geo_text)
            
            # Build company record
            company = {
                'company_name': company_name,
                'company_url': company_url,
                'description': description,
                'sectors': sectors,
                'stage': stage,
                'geographies': geographies,
                'everywhere_tags': [],
                'source_url': portfolio_url
            }
            
            companies.append(company)
            
        except Exception:
            # Skip problematic entries
            continue
    
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
                         "..", "data", "mubadalacapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
