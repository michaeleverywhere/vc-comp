# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import time
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape CapitalG portfolio companies.
    Strategy: Parse the embedded JSON from the search component, then fetch
    detail pages for internal companies to extract company_url and richer metadata.
    """
    portfolio_url = "https://capitalg.com/portfolio/"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    companies = []
    seen = set()
    
    # Fetch main portfolio page
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Extract embedded JSON from capitalg-search-results data-items attribute
    search_elem = soup.find("capitalg-search-results", {"category": "companies"})
    if not search_elem:
        return []
    
    data_attr = search_elem.get("data-items", "")
    if not data_attr:
        return []
    
    # Decode HTML entities and parse JSON
    try:
        json_str = data_attr.replace("&quot;", '"').replace("&#039;", "'").replace("&amp;", "&")
        items = json.loads(json_str)
    except Exception:
        return []
    
    if not isinstance(items, list):
        return []
    
    # Process each company from the JSON
    for item in items:
        if not isinstance(item, dict):
            continue
        
        name = item.get("title", "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        
        href = item.get("href", "").strip()
        is_external = item.get("isExternal", False)
        terms = item.get("terms", [])
        
        # Build initial record
        record = {
            "company_name": name,
            "company_url": None,
            "description": None,
            "profile_url": None,
            "founders": [],
            "everywhere_tags": [],
            "source_url": portfolio_url
        }
        
        # For external links, href IS the company_url
        if is_external and href:
            record["company_url"] = href if href.startswith("http") else urljoin(portfolio_url, href)
        else:
            # Internal profile page
            if href:
                record["profile_url"] = urljoin(portfolio_url, href)
        
        # Extract description from terms[1] (typically the bio)
        if isinstance(terms, list) and len(terms) > 1:
            desc = terms[1]
            if isinstance(desc, str) and len(desc) > 30:
                record["description"] = desc
        
        # Extract team members from terms[2:] (assume these are people names)
        if isinstance(terms, list) and len(terms) > 2:
            for t in terms[2:]:
                if isinstance(t, str) and t.strip() and len(t) < 50:
                    # Only add if it looks like a name (short, capitalized)
                    if t[0].isupper():
                        record["founders"].append(t.strip())
        
        companies.append(record)
    
    # Now enrich internal companies by fetching their detail pages
    for company in companies:
        if not company["profile_url"]:
            continue
        
        try:
            time.sleep(0.3)
            detail_resp = session.get(company["profile_url"], timeout=20)
            detail_resp.raise_for_status()
        except Exception:
            continue
        
        detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
        
        # Look for company website link in the detail page
        # Common pattern: look for links in main content area
        main = detail_soup.find("main") or detail_soup.find("div", {"id": "root"})
        if main:
            # Find external links (not capitalg.com)
            for link in main.find_all("a", href=True):
                href_val = link.get("href", "").strip()
                if href_val and href_val.startswith("http") and "capitalg.com" not in href_val:
                    # Check if it looks like a company domain
                    if any(ext in href_val for ext in [".com", ".io", ".ai", ".co", ".org", ".net"]):
                        # Prefer shorter URLs (likely homepage vs specific pages)
                        if not company["company_url"] or len(href_val) < len(company["company_url"]):
                            company["company_url"] = href_val
        
        # Enhance description from meta tags if needed
        if not company["description"]:
            og_desc = detail_soup.find("meta", {"property": "og:description"})
            if og_desc:
                content = og_desc.get("content", "").strip()
                if content and "CapitalG portfolio company" not in content:
                    company["description"] = content
        
        # Try to find description in visible content
        if not company["description"] and main:
            # Look for structured text blocks
            for p in main.find_all("p", limit=5):
                text = p.get_text(strip=True)
                if len(text) > 80:
                    company["description"] = text
                    break
    
    # Deduplicate by name (case-insensitive)
    final = []
    names_lower = set()
    for c in companies:
        name_key = c["company_name"].lower()
        if name_key not in names_lower:
            names_lower.add(name_key)
            final.append(c)
    
    return final


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
                         "..", "data", "capitalg_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
