# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from typing import Any
from urllib.parse import urljoin

def scrape() -> list[dict]:
    """
    Scrape Episode 1 Ventures portfolio companies from https://episode1.com/portfolio
    Returns a list of dicts with company information.
    """
    portfolio_url = "https://episode1.com/portfolio"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    
    try:
        response = session.get(portfolio_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all portfolio items in the accordion list
    portfolio_items = soup.find_all('div', {'role': 'listitem', 'class': 'portfolio-item'})
    
    for item in portfolio_items:
        try:
            # Extract company name from text-bold div
            name_elem = item.find('div', {'class': 'text-bold'})
            if not name_elem:
                continue
            
            company_name = name_elem.get_text(strip=True)
            
            # Deduplicate
            if company_name in seen_names:
                continue
            seen_names.add(company_name)
            
            # Extract sectors from sector-holder divs
            sectors = []
            sector_holder = item.find('div', {'class': 'sector-holder'})
            if sector_holder:
                sector_divs = sector_holder.find_all('div', {'fs-cmsfilter-field': 'sector'})
                for sector_div in sector_divs:
                    sector_text = sector_div.get_text(strip=True)
                    if sector_text:
                        sectors.append(sector_text)
            
            # Extract stage from _4-grid first column
            stage = None
            stage_grid = item.find('div', {'class': '_4-grid'})
            if stage_grid:
                stage_divs = stage_grid.find_all('div', {'class': 'w-layout-vflex'})
                if stage_divs:
                    stage_text_elem = stage_divs[0].find('div', {'class': 'text-medium'})
                    if stage_text_elem:
                        stage = stage_text_elem.get_text(strip=True)
            
            # Extract status from tag div
            status = None
            status_tag = item.find('div', {'class': 'tag'})
            if status_tag:
                status = status_tag.get_text(strip=True)
            
            # Extract description from accordion content paragraph
            description = None
            accordion_content = item.find('div', {'class': 'accordion-content'})
            if accordion_content:
                desc_p = accordion_content.find('p')
                if desc_p:
                    description = desc_p.get_text(strip=True)
            
            # Extract company URL from link in accordion content
            company_url = None
            if accordion_content:
                url_link = accordion_content.find('a', {'target': '_blank'})
                if url_link and url_link.get('href') and url_link.get('href') != '#':
                    company_url = url_link.get('href')
            
            # Try to fetch detail page for additional info (profile_url)
            profile_url = None
            detail_link = item.find('a', {'class': 'hidden'})
            if detail_link and detail_link.get('href'):
                profile_url = urljoin(portfolio_url, detail_link.get('href'))
            
            company_dict = {
                'company_name': company_name,
                'company_url': company_url,
                'description': description,
                'founders': [],
                'sectors': sectors,
                'stage': stage,
                'status': status,
                'profile_url': profile_url,
                'everywhere_tags': [],
                'source_url': portfolio_url
            }
            
            companies.append(company_dict)
            time.sleep(0.3)
            
        except Exception:
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
                         "..", "data", "episode1ventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
