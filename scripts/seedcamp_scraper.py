# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import re
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

PORTFOLIO_URL = "https://seedcamp.com/our-companies"

def scrape() -> List[Dict]:
    """
    Scrape Seedcamp portfolio companies.
    Returns list of dicts with company information.
    """
    companies = []
    seen = set()
    session = requests.Session()
    
    try:
        # Fetch main portfolio page
        resp = session.get(PORTFOLIO_URL, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract companies from the company__item divs in the filters__body
        filters_body = soup.find("div", class_="filters__body")
        if not filters_body:
            return []
        
        company_items = filters_body.find_all("div", class_="company__item")
        
        for item in company_items:
            try:
                # Get company name
                name_elem = item.find("span", class_="company__item__name")
                if not name_elem:
                    continue
                
                # Extract clean name (remove icon text)
                company_name = name_elem.get_text(strip=True)
                # Remove trailing icon characters
                company_name = re.sub(r'\s*[\u2000-\u2BFF\u00A0]+\s*$', '', company_name).strip()
                
                if not company_name or company_name in seen:
                    continue
                seen.add(company_name)
                
                # Get company URL from the link
                link_elem = item.find("a", class_="company__item__link")
                company_url = None
                if link_elem and link_elem.get("href"):
                    url = link_elem.get("href")
                    # Only use if it's an external URL
                    if url and url.startswith("http"):
                        company_url = url
                
                # Get investment year
                year_elem = item.find("h6", class_="company__item__year")
                investment_year = None
                if year_elem:
                    year_text = year_elem.get_text(strip=True)
                    try:
                        investment_year = int(year_text)
                    except (ValueError, TypeError):
                        pass
                
                # Get description
                desc_elem = item.find("div", class_="company__item__description__content")
                description = None
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                
                # Extract sectors from CSS classes
                sectors = []
                item_classes = item.get("class", [])
                sector_map = {
                    "ai": "AI",
                    "climate": "Climate",
                    "consumer": "Consumer",
                    "crypto": "Crypto",
                    "developer-tools": "Developer Tools",
                    "enterprise": "Enterprise",
                    "fintech": "Fintech",
                    "health-bio": "Health/Bio",
                    "marketplaces": "Marketplaces",
                    "security": "Security"
                }
                for cls in item_classes:
                    if cls in sector_map:
                        sectors.append(sector_map[cls])
                
                # Build company record
                company_record = {
                    "company_name": company_name,
                    "company_url": company_url,
                    "description": description,
                    "sectors": sectors,
                    "investment_year": investment_year,
                    "everywhere_tags": [],
                    "source_url": PORTFOLIO_URL
                }
                
                companies.append(company_record)
                
            except Exception:
                # Skip malformed entries
                continue
        
        # Also scrape the profile tiles at the top (featured companies)
        profile_tiles = soup.find_all("div", class_="tile--company")
        
        for tile in profile_tiles:
            try:
                # Get company name
                name_elem = tile.find("h4", class_="tile__name")
                if not name_elem:
                    continue
                
                company_name = name_elem.get_text(strip=True)
                
                if not company_name or company_name in seen:
                    continue
                seen.add(company_name)
                
                # Get profile URL
                link_elem = tile.find("a", class_="tile__link")
                profile_url = None
                if link_elem and link_elem.get("href"):
                    profile_url = urljoin(PORTFOLIO_URL, link_elem.get("href"))
                
                # Get description from role
                role_elem = tile.find("div", class_="tile__role")
                description = None
                if role_elem:
                    description = role_elem.get_text(strip=True)
                
                # Fetch detail page to get more information
                company_url = None
                founders = []
                
                if profile_url:
                    time.sleep(0.3)
                    try:
                        detail_resp = session.get(profile_url, timeout=20)
                        detail_resp.raise_for_status()
                        detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                        
                        # Look for external link in credits section
                        credits = detail_soup.find("div", class_="credits")
                        if credits:
                            link = credits.find("a", href=True)
                            if link:
                                url = link.get("href")
                                if url and url.startswith("http"):
                                    company_url = url
                        
                        # Look for founders in the credits details
                        credits_header = detail_soup.find("h3", class_="pageheader__details")
                        if credits_header:
                            founder_links = credits_header.find_all("a", href=re.compile(r"/people/"))
                            for flink in founder_links:
                                fname = flink.get_text(strip=True)
                                if fname and fname not in founders:
                                    founders.append(fname)
                        
                    except Exception:
                        pass
                
                # Build company record
                company_record = {
                    "company_name": company_name,
                    "company_url": company_url,
                    "description": description,
                    "profile_url": profile_url,
                    "founders": founders,
                    "everywhere_tags": [],
                    "source_url": PORTFOLIO_URL
                }
                
                companies.append(company_record)
                
            except Exception:
                continue
        
    except Exception:
        return []
    
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
                         "..", "data", "seedcamp_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
