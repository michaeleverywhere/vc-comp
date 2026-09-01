# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import time
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Air Street Capital portfolio companies from https://airstreet.com/portfolio
    Returns a list of dicts with company information extracted from HTML list items.
    """
    portfolio_url = "https://airstreet.com/portfolio"
    session = requests.Session()
    
    companies = []
    seen_urls = set()
    
    try:
        response = session.get(portfolio_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all portfolio sections by looking for container divs with portfolio class
    portfolio_sections = soup.find_all("div", class_="container has-text portfolio")
    
    for section in portfolio_sections:
        # Get the epoch/section header if available
        header = section.find("h1")
        if not header:
            header = section.find("h3")
        
        epoch = header.get_text(strip=True) if header else None
        
        # Find all list items in this section
        ul = section.find("ul")
        if not ul:
            continue
        
        list_items = ul.find_all("li")
        
        for li in list_items:
            link = li.find("a")
            if not link:
                continue
            
            # Extract company URL and name
            company_url = link.get("href", "").strip()
            
            # Skip unannounced companies (###) and empty URLs
            if not company_url or company_url == "###":
                continue
            
            # Get link text which contains company name
            link_text = link.get_text(strip=True)
            
            # Get the full text of the list item for description
            full_text = li.get_text(strip=True)
            
            # Parse company name and acquisition/status info
            company_name = link_text
            status = None
            
            # Check for acquisition or public status in company name
            if "(acq." in company_name.lower():
                status = "acquired"
            elif "nasdaq:" in company_name.lower() or "nyse:" in company_name.lower():
                status = "public"
            
            # Clean company name from status markers
            company_name = re.sub(r'\s*\(acq\..*?\)', '', company_name, flags=re.IGNORECASE)
            company_name = re.sub(r'\s*\(NASDAQ:.*?\)', '', company_name, flags=re.IGNORECASE)
            company_name = re.sub(r'\s*\(NYSE:.*?\)', '', company_name, flags=re.IGNORECASE)
            company_name = company_name.strip()
            
            # Deduplicate by URL
            if company_url in seen_urls:
                continue
            
            seen_urls.add(company_url)
            
            # Extract description from the text after the link
            description = None
            # Get text after the link
            after_link = full_text.replace(link_text, "", 1).strip()
            # Remove leading dot and semicolon, then extract description
            after_link = after_link.lstrip(".;").strip()
            
            # Description is typically before any location markers like (USA), (UK), etc.
            # Split by common patterns
            desc_match = re.match(r'^([^(;]+)', after_link)
            if desc_match:
                description = desc_match.group(1).strip()
                if description:
                    # Clean up trailing punctuation
                    description = description.rstrip(".;,").strip()
            
            # Extract location/tags from parentheses
            tags = []
            if epoch:
                tags.append(epoch)
            
            # Find location tags in parentheses at the end
            location_matches = re.findall(r'\(([A-Z]{2,3}(?:/[A-Z]{2,3})*)\)', after_link)
            for loc in location_matches:
                # Split combined locations like USA/UK
                for single_loc in loc.split('/'):
                    tags.append(single_loc.strip())
            
            company_record = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description if description else None,
                "status": status,
                "everywhere_tags": tags,
                "source_url": portfolio_url,
            }
            
            companies.append(company_record)
    
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
                         "..", "data", "airstreetcapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
