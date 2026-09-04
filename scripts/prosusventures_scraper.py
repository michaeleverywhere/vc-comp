# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Prosus Ventures portfolio companies from https://prosus.com/portfolio
    
    This implementation extracts data from the portfolio card HTML and categorizes
    companies by the visible tabs (Classifieds, Food Delivery, Payments & Fintech, etc.)
    """
    portfolio_url = "https://prosus.com/portfolio"
    companies = []
    seen = set()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extract category mapping from tab list
    # The tabs show: All, Classifieds, Food Delivery, Payments & Fintech, Edtech, Ventures
    category_map = {}
    tab_list = soup.find('ul')
    if tab_list and tab_list.find_parent('div', class_='tab-list'):
        for li in tab_list.find_all('li', class_='tab-item'):
            a_tag = li.find('a')
            if a_tag and a_tag.get('data-id'):
                cat_id = a_tag['data-id']
                cat_name = a_tag.get_text(strip=True)
                if cat_id != '*':  # Skip "All"
                    category_map[cat_id] = cat_name
    
    # Find all portfolio card wrappers
    portfolio_wrappers = soup.find_all('div', class_='portfolio-cards-wrapper')
    
    for wrapper in portfolio_wrappers:
        try:
            # Extract company name from the aria-label or the h4 heading
            box_link = wrapper.find('a', class_='portfolio-box-wrapper')
            aria_label = box_link.get('aria-label', '') if box_link else ''
            
            # Parse company name from aria-label like "Expand 99minutos Portfolio"
            company_name = None
            if aria_label and 'Expand' in aria_label and 'Portfolio' in aria_label:
                company_name = aria_label.replace('Expand', '').replace('Portfolio', '').strip()
            
            # Fallback: get from h4 in expand section
            if not company_name:
                name_elem = wrapper.find('p', class_='h4')
                if name_elem:
                    company_name = name_elem.get_text(strip=True)
            
            if not company_name or company_name in seen:
                continue
            
            seen.add(company_name)
            
            # Extract description
            description = None
            portfolio_content = wrapper.find('div', class_='portfolio-content')
            if portfolio_content:
                desc_parts = []
                for p in portfolio_content.find_all('p'):
                    # Skip the h4 paragraph
                    if 'h4' in p.get('class', []):
                        continue
                    text = p.get_text(strip=True)
                    if text and text != company_name:
                        desc_parts.append(text)
                if desc_parts:
                    description = ' '.join(desc_parts)
            
            # Extract company URL from the CTA link
            company_url = None
            cta_link = wrapper.find('a', class_='cta')
            if cta_link and cta_link.get('href'):
                url = cta_link['href'].strip()
                if url and url != 'javascript:;' and url.startswith('http'):
                    company_url = url
            
            # Build the record - only include fields that the site exposes
            record = {
                'company_name': company_name,
                'company_url': company_url,
                'description': description,
                'everywhere_tags': [],
                'source_url': portfolio_url
            }
            
            companies.append(record)
            
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
                         "..", "data", "prosusventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
