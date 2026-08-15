# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

def scrape() -> List[dict]:
    """
    Scrapes Blockchain Capital's portfolio from https://blockchain.capital/portfolio
    Returns a list of portfolio company dicts.
    """
    portfolio_url = "https://blockchain.capital/portfolio"
    session = requests.Session()
    companies = []
    seen = set()
    
    try:
        # Fetch the portfolio page
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Look for embedded JSON data in script tags (Webflow often embeds CMS data)
        scripts = soup.find_all("script", type="application/json")
        
        # Also look for portfolio items rendered in the DOM
        portfolio_items = soup.find_all("div", class_="portfolio__coll-list__item")
        
        for item in portfolio_items:
            # Extract the link element
            link_elem = item.find("a", class_="portfolio__link")
            if not link_elem:
                continue
            
            company_url = link_elem.get("href", "").strip()
            
            # Extract company name from div with class t-36
            name_elem = link_elem.find("div", class_="t-36")
            company_name = name_elem.get_text(strip=True) if name_elem else None
            
            if not company_name or company_name in seen:
                continue
            
            seen.add(company_name)
            
            # Extract sector from fs-cmsfilter-field="sector"
            sector_elem = link_elem.find("div", attrs={"fs-cmsfilter-field": "sector"})
            sector = sector_elem.get_text(strip=True) if sector_elem else None
            
            # Extract stage from fs-cmsfilter-field="stage"
            # There may be multiple stage divs; find the one with actual text content
            stage = None
            stage_elems = link_elem.find_all("div", attrs={"fs-cmsfilter-field": "stage"})
            for elem in stage_elems:
                text = elem.get_text(strip=True)
                if text and text not in ("w-dyn-bind-empty", ""):
                    stage = text
                    break
            
            # Build initial company record
            company = {
                "company_name": company_name,
                "company_url": company_url if company_url else None,
                "description": None,
                "founders": [],
                "sectors": [sector] if sector else [],
                "stage": stage,
                "status": None,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            
            # Attempt to fetch detail page for enrichment
            if company_url and company_url.startswith("http"):
                try:
                    time.sleep(0.3)  # Be polite
                    detail_resp = session.get(company_url, timeout=20)
                    detail_resp.raise_for_status()
                    detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                    
                    # Try to extract description from meta tags
                    meta_desc = detail_soup.find("meta", attrs={"name": "description"})
                    if meta_desc:
                        desc_text = meta_desc.get("content", "").strip()
                        if desc_text:
                            company["description"] = desc_text
                    
                    # Try to find founder/team information in page content
                    # Look for common patterns (site-dependent; Webflow sites often use specific structures)
                    # Try finding team section or about section with names
                    team_section = detail_soup.find(string=re.compile(r"founder|team|leadership", re.IGNORECASE))
                    if team_section:
                        parent = team_section.parent
                        # Extract nearby text that might contain founder names
                        # This is best-effort and site-dependent
                        nearby_text = parent.get_text(strip=True) if parent else ""
                        if nearby_text and len(nearby_text) < 500:
                            # Could contain founder info, but we won't extract blindly
                            pass
                    
                except Exception:
                    # If detail fetch fails, continue with what we have
                    pass
            
            companies.append(company)
    
    except Exception:
        # If main page fetch fails, return empty list
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
                         "..", "data", "blockchaincapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
