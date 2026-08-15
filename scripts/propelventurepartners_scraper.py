# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import time
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

def scrape() -> List[Dict]:
    """
    Scrape Propel Venture Partners portfolio from their website.
    Returns a list of dicts with company information.
    """
    portfolio_url = "https://propel.vc/portfolio"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    companies = []
    seen_names = set()
    
    try:
        # Fetch the portfolio page
        response = session.get(portfolio_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse JSON-LD for structured data
        json_ld_data = None
        script_tags = soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in script_tags:
            if script.string:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'CollectionPage':
                        json_ld_data = data
                        break
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Build a mapping of company names to URLs and exit info from JSON-LD
        company_info_map = {}
        
        if json_ld_data and 'mainEntity' in json_ld_data:
            for item_list in json_ld_data['mainEntity']:
                if not isinstance(item_list, dict) or item_list.get('@type') != 'ItemList':
                    continue
                
                list_name = item_list.get('name', '')
                elements = item_list.get('itemListElement', [])
                
                for elem in elements:
                    if not isinstance(elem, dict):
                        continue
                    
                    item = elem.get('item', {})
                    if not isinstance(item, dict):
                        continue
                    
                    name = item.get('name', '').strip()
                    if not name:
                        continue
                    
                    url = item.get('url')
                    description = item.get('description')
                    
                    if name not in company_info_map:
                        company_info_map[name] = {
                            'url': url,
                            'description': description,
                            'is_exit': list_name == 'Notable Exits'
                        }
        
        # Now scrape each company with detail page fetching
        for company_name, info in company_info_map.items():
            if company_name in seen_names:
                continue
            
            seen_names.add(company_name)
            
            company_url = info.get('url')
            exit_description = info.get('description')
            is_exit = info.get('is_exit', False)
            
            # Determine status from exit description
            status = None
            if is_exit and exit_description:
                desc_upper = exit_description.upper()
                if 'IPO' in desc_upper:
                    status = 'exited_ipo'
                elif 'ACQUIRED' in desc_upper:
                    status = 'exited_acquisition'
            
            # Try to fetch company website for additional info
            description = None
            
            if company_url:
                try:
                    time.sleep(0.3)  # Polite crawling
                    company_response = session.get(company_url, timeout=20, allow_redirects=True)
                    
                    if company_response.status_code == 200:
                        company_soup = BeautifulSoup(company_response.text, 'html.parser')
                        
                        # Try to extract description from meta tags
                        meta_desc = company_soup.find('meta', attrs={'name': 'description'})
                        if meta_desc and meta_desc.get('content'):
                            description = meta_desc.get('content').strip()
                        
                        # Fallback to og:description
                        if not description:
                            og_desc = company_soup.find('meta', attrs={'property': 'og:description'})
                            if og_desc and og_desc.get('content'):
                                description = og_desc.get('content').strip()
                        
                        # Fallback to first paragraph
                        if not description:
                            first_p = company_soup.find('p')
                            if first_p:
                                text = first_p.get_text(strip=True)
                                if text and len(text) > 20:
                                    description = text[:500]
                
                except (requests.RequestException, Exception):
                    # If we can't fetch the company page, continue with what we have
                    pass
            
            # Use exit description as fallback if no website description found
            if not description and exit_description:
                description = exit_description
            
            company_dict = {
                'company_name': company_name,
                'company_url': company_url if company_url else None,
                'description': description if description else None,
                'status': status,
                'everywhere_tags': [],
                'source_url': portfolio_url
            }
            
            companies.append(company_dict)
    
    except requests.RequestException:
        # If main page fails, return empty list
        pass
    
    # Deduplicate by name (safety check)
    unique_companies = []
    final_seen = set()
    
    for company in companies:
        name = company.get('company_name')
        if name and name not in final_seen:
            final_seen.add(name)
            unique_companies.append(company)
    
    return unique_companies


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
                         "..", "data", "propelventurepartners_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
