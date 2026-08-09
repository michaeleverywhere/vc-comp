# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import time
from bs4 import BeautifulSoup
from typing import Optional

def scrape() -> list[dict]:
    """
    Scrape Forerunner Ventures portfolio from their investments page.
    Returns a list of dicts, one per portfolio company.
    """
    portfolio_url = "https://forerunnerventures.com/investments"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        response = session.get(portfolio_url, timeout=20)
        response.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Parse the HTML structure directly
    invest_list = soup.find("ol", class_="invest__list")
    if not invest_list:
        return []
    
    rows = invest_list.find_all("li", class_="invest__row")
    
    for row in rows:
        # Extract basic information from the row
        name_elem = row.find("h3", class_="invest__name")
        if not name_elem:
            continue
            
        company_name = name_elem.get_text(strip=True)
        
        # Dedupe by company name
        if company_name in seen_names:
            continue
        seen_names.add(company_name)
        
        # Extract year
        year_elem = row.find("span", class_="invest__year")
        year_str = year_elem.get_text(strip=True) if year_elem else None
        year_int = None
        if year_str:
            try:
                year_int = int(year_str)
            except (ValueError, TypeError):
                pass
        
        # Extract company URL
        visit_link = row.find("a", class_="invest__visit")
        company_url = None
        if visit_link and visit_link.get("href"):
            company_url = visit_link.get("href").strip()
        
        # Extract description
        desc_elem = row.find("p", class_="invest__desc")
        description = desc_elem.get_text(strip=True) if desc_elem else None
        
        # Extract tags (categories and AI lens)
        tags_elem = row.find("p", class_="invest__tags")
        tags_text = tags_elem.get_text(strip=True) if tags_elem else ""
        everywhere_tags = []
        if tags_text:
            # Split by middle dot and clean up
            parts = [tag.strip() for tag in tags_text.split("·") if tag.strip()]
            everywhere_tags = parts
        
        # Build the company record with only fields actually present on the page
        # This site does NOT expose: founders, sectors (they have categories instead),
        # stage, status, or individual profile URLs
        company_record = {
            "company_name": company_name,
            "company_url": company_url,
            "description": description,
            "year": year_int,
            "everywhere_tags": everywhere_tags,
            "source_url": portfolio_url
        }
        
        companies.append(company_record)
        
        # Polite delay between processing companies
        time.sleep(0.1)
    
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
                         "..", "data", "forerunnerventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
