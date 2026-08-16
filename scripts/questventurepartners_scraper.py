# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin
import re

def scrape() -> List[Dict]:
    """
    Scrape Quest Venture Partners portfolio companies from their portfolio page.
    Returns a list of dicts, one per portfolio company.
    """
    portfolio_url = "https://questvp.com/portfolio.html"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    companies = []
    seen_names = set()
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Find all portfolio cards
    cards = soup.find_all("div", class_="port-card")
    
    for card in cards:
        # Skip placeholder cards and section dividers
        if card.get("class") and ("placeholder" in card.get("class") or "section-divider" in card.get("class")):
            continue
        
        # Extract basic fields from card structure
        name_elem = card.find("h3", class_="port-name")
        company_name = name_elem.get_text(strip=True) if name_elem else None
        
        if not company_name:
            continue
        
        # Deduplicate by name
        if company_name in seen_names:
            continue
        seen_names.add(company_name)
        
        # Extract sector(s)
        sector_elem = card.find("div", class_="port-sector")
        sector_text = sector_elem.get_text(strip=True) if sector_elem else None
        sectors = []
        if sector_text:
            # Split by "/" for multiple sectors
            sectors = [s.strip() for s in sector_text.split("/")]
        
        # Extract description
        desc_elem = card.find("div", class_="port-desc")
        description = desc_elem.get_text(strip=True) if desc_elem else None
        
        # Extract company website URL
        company_url = None
        website_btn = card.find("a", class_="port-website-btn")
        if website_btn and website_btn.get("href"):
            company_url = website_btn.get("href")
        
        # Extract fund stage from data attribute
        fund_stage = card.get("data-fund")
        stage = None
        if fund_stage:
            if fund_stage == "2":
                stage = "Fund II"
            elif fund_stage == "3":
                stage = "Fund III"
            elif fund_stage == "4":
                stage = "Fund IV"
            elif fund_stage == "exited":
                stage = "Exited"
        
        # Fallback: extract from port-fund-tag span
        if not stage:
            fund_tag = card.find("span", class_="port-fund-tag")
            stage = fund_tag.get_text(strip=True) if fund_tag else None
        
        # Determine status from stage
        status = "Active"
        if stage == "Exited":
            status = "Exited"
        
        company_dict = {
            "company_name": company_name,
            "company_url": company_url,
            "description": description,
            "sectors": sectors,
            "stage": stage,
            "status": status,
            "founders": [],
            "everywhere_tags": [],
            "source_url": portfolio_url,
        }
        
        companies.append(company_dict)
        
        # Polite throttling between potential future enrichment requests
        time.sleep(0.3)
    
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
                         "..", "data", "questventurepartners_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
