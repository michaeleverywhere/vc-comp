# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape High Alpha portfolio companies from https://highalpha.com/companies
    
    Returns:
        List of dicts with company information including name, description, 
        investment type, status, and detail page data where available.
    """
    portfolio_url = "https://highalpha.com/companies"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Find all company items in the portfolio list
    co_items = soup.find_all("div", class_="co-item", attrs={"role": "listitem"})
    
    for item in co_items:
        try:
            co_trigger = item.find("div", class_="co-trigger")
            if not co_trigger:
                continue
            
            # Extract company name
            h2_elem = co_trigger.find("h2")
            if not h2_elem:
                continue
            
            company_name = h2_elem.get_text(strip=True)
            if not company_name or company_name in seen_names:
                continue
            
            seen_names.add(company_name)
            
            # Extract description
            description = None
            desc_div = co_trigger.find("div", class_="co-trigger-desc")
            if desc_div:
                desc_p = desc_div.find("p")
                if desc_p:
                    description = desc_p.get_text(strip=True)
            
            # Extract tags (investment type and status)
            tags_div = co_trigger.find("div", class_="co-trigger-tags")
            investment_type = None
            status = "Active"  # Default to Active if not marked Acquired
            
            if tags_div:
                tag_divs = tags_div.find_all("div", class_="tag")
                for tag in tag_divs:
                    tag_text = tag.get_text(strip=True)
                    
                    # Investment type
                    if "cc-co-studio" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        investment_type = "Studio"
                    elif "cc-co-coinvest" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        investment_type = "Co-Invest"
                    elif "cc-co-capital" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        investment_type = "Anchor"
                    
                    # Status
                    if "cc-co-acquired" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        status = "Acquired"
            
            # Extract company slug from hidden input
            company_slug = None
            jb_embed = item.find("div", class_="jb-embed")
            if jb_embed:
                hidden_input = jb_embed.find("input", type="hidden")
                if hidden_input:
                    company_slug = hidden_input.get("value", "").strip()
            
            # Build company URL from slug
            company_url = None
            if company_slug:
                # The site structure suggests detail pages exist at /companies/{slug}
                company_url = f"https://highalpha.com/companies/{company_slug}"
            
            # Create record with only fields that are actually present on the site
            record = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description,
                "investment_type": investment_type,
                "status": status,
                "profile_url": company_url,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            
            companies.append(record)
            
        except Exception:
            # Skip problematic entries silently
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
                         "..", "data", "highalpha_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
