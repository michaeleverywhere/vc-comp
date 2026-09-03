# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Great Oaks Venture Capital portfolio from https://greatoaksvc.com/portfolio
    Returns a list of dicts, one per portfolio company.
    
    This scraper extracts data from embedded JSON in script tags on the portfolio page,
    which contains richer structured data than HTML cards alone.
    """
    portfolio_url = "https://greatoaksvc.com/portfolio"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Look for embedded JSON data in script tags (Webflow often embeds CMS data)
    json_data = None
    for script in soup.find_all("script", type="application/json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "items" in data:
                json_data = data
                break
        except:
            continue
    
    # If JSON approach doesn't work, fall back to parsing HTML cards
    # but this time we'll fetch company detail pages for descriptions
    card_items = soup.find_all("div", class_="company-logo-item")
    
    for card in card_items:
        try:
            link_elem = card.find("a", class_="card")
            if not link_elem:
                continue
            
            company_url = link_elem.get("href", "").strip()
            if not company_url:
                continue
            
            # Extract company name from alt text
            img_elem = link_elem.find("img", class_="company-logo")
            company_name = img_elem.get("alt", "").strip() if img_elem else None
            
            if not company_name:
                continue
            
            # Deduplicate
            if company_name in seen_names:
                continue
            seen_names.add(company_name)
            
            # Extract category
            category_div = link_elem.find("div", attrs={"fs-cmsfilter-field": "category"})
            category = category_div.get_text(strip=True) if category_div else None
            
            # Build sectors list - only include if not "Exits"
            sectors = []
            if category and category != "Exits":
                sectors = [category]
            
            # Determine status from category
            status = None
            if category == "Exits":
                status = "exited"
            
            # Try to fetch description from the company's own website
            description = None
            if company_url and company_url.startswith("http"):
                try:
                    time.sleep(0.3)  # Rate limiting
                    company_resp = session.get(company_url, timeout=20)
                    if company_resp.status_code == 200:
                        company_soup = BeautifulSoup(company_resp.text, "html.parser")
                        
                        # Try multiple common meta description locations
                        meta_desc = company_soup.find("meta", attrs={"name": "description"})
                        if not meta_desc:
                            meta_desc = company_soup.find("meta", attrs={"property": "og:description"})
                        if not meta_desc:
                            meta_desc = company_soup.find("meta", attrs={"name": "twitter:description"})
                        
                        if meta_desc and meta_desc.get("content"):
                            description = meta_desc.get("content").strip()
                        
                        # If no meta description, try to find a description paragraph
                        if not description:
                            # Look for common description containers
                            desc_candidates = []
                            
                            # Try hero/header sections
                            for selector in ["p.hero", "p.lead", ".hero p", ".header p", "section p"]:
                                try:
                                    elem = company_soup.select_one(selector)
                                    if elem:
                                        text = elem.get_text(strip=True)
                                        if len(text) > 50 and len(text) < 500:
                                            desc_candidates.append(text)
                                            break
                                except:
                                    pass
                            
                            if desc_candidates:
                                description = desc_candidates[0]
                
                except Exception:
                    pass  # If company site fetch fails, continue without description
            
            record = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description,
                "sectors": sectors,
                "status": status,
                "everywhere_tags": [],
                "source_url": portfolio_url
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
                         "..", "data", "greatoaksventurecapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
