# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Optional

def scrape() -> list[dict]:
    """
    Scrape portfolio companies from TMT Investments.
    Returns a list of dicts with company information.
    """
    portfolio_url = "https://tmtinvestments.com"
    companies = {}
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find all portfolio items - they appear in both Current Portfolio and Hall of Fame sections
    portfolio_items = soup.find_all("div", class_="portfolio-item")
    
    for item in portfolio_items:
        try:
            content_div = item.find("div", class_="portfolio-item-content")
            if not content_div:
                continue
            
            # Get logo for potential company name
            logo_div = content_div.find("div", class_="portfolio-item-logo")
            logo_img = logo_div.find("img") if logo_div else None
            logo_alt = logo_img.get("alt", "").strip() if logo_img else ""
            
            # Get text content
            text_div = content_div.find("div", class_="portfolio-item-text")
            if not text_div:
                continue
            
            # Extract all paragraphs
            paragraphs = text_div.find_all("p", class_="wp-block-paragraph")
            if not paragraphs:
                continue
            
            # First paragraph is always description
            description = paragraphs[0].get_text(strip=True) if paragraphs else None
            
            # Extract company name and URLs from links
            company_name = None
            company_url = None
            profile_url = None
            
            links = text_div.find_all("a")
            for link in links:
                href = link.get("href", "").strip()
                link_text = link.get_text(strip=True)
                
                if not href:
                    continue
                
                # Crunchbase link
                if "crunchbase.com" in href.lower():
                    profile_url = href
                    # Extract company name from bold text before "at Crunchbase"
                    strong = link.find("strong")
                    if strong:
                        name_text = strong.get_text(strip=True)
                        if name_text and "at Crunchbase" not in name_text:
                            company_name = name_text
                # Website link (contains "Web Site:" or "WebSite:" prefix in paragraph)
                elif href.startswith(("http://", "https://")) and not company_url:
                    parent_text = link.parent.get_text(strip=True) if link.parent else ""
                    if "Web Site:" in parent_text or "WebSite:" in parent_text or "website:" in parent_text.lower():
                        company_url = href
            
            # Fallback: try to extract company name from logo alt text or first strong tag
            if not company_name:
                strong_tags = text_div.find_all("strong")
                for strong in strong_tags:
                    text = strong.get_text(strip=True)
                    if text and "at Crunchbase" not in text and len(text) < 50:
                        company_name = text
                        break
            
            # Last resort: use domain name from URL
            if not company_name and company_url:
                domain_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.[a-z]+', company_url)
                if domain_match:
                    company_name = domain_match.group(1).replace("-", " ").title()
            
            # Skip if we don't have minimum required data
            if not company_name or not description:
                continue
            
            # Deduplicate by company name
            if company_name in companies:
                continue
            
            # Determine status based on which section this item is in
            status = None
            parent_tab = item.find_parent("div", class_="tab-pane")
            if parent_tab:
                tab_id = parent_tab.get("id", "")
                if "hall-of-fame" in tab_id:
                    status = "exited"
                elif "current-portfolio" in tab_id:
                    status = "active"
            
            # Extract sector from the tab navigation if possible
            sectors = []
            if parent_tab:
                tab_id = parent_tab.get("id", "")
                # Map tab IDs to sector names
                sector_map = {
                    "big-data-cloud": "Data Platforms",
                    "e-commerce": "Digital commerce",
                    "edtech": "Edtech",
                    "fintech": "Fintech",
                    "healthtech": "Healthtech",
                    "mobility": "Logistics and Mobility",
                    "saas": "Enterprise Software"
                }
                for key, sector in sector_map.items():
                    if key in tab_id:
                        sectors.append(sector)
                        break
            
            # Build company record
            record = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description,
                "status": status,
                "sectors": sectors,
                "profile_url": profile_url,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            
            companies[company_name] = record
            
        except Exception:
            continue
    
    return list(companies.values())


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
                         "..", "data", "tmtinvestments_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
