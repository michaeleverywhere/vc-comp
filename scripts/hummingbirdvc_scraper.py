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
    Scrape Hummingbird VC portfolio from https://hummingbird.vc/portfolio
    Returns a list of dicts, one per portfolio company.
    """
    portfolio_url = "https://hummingbird.vc/portfolio"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    })
    
    companies = []
    seen_names = set()
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find all company items - each is a div.image-field.w-dyn-item
    company_items = soup.find_all("div", class_="w-dyn-item", role="listitem")
    
    for item in company_items:
        try:
            # Find the visible link-row (skip w-condition-invisible ones)
            link_rows = item.find_all("div", class_="link-row")
            link_row = None
            for lr in link_rows:
                classes = lr.get("class", [])
                if "w-condition-invisible" not in classes:
                    link_row = lr
                    break
            
            if not link_row:
                continue
            
            grid_item = link_row.find("div", class_="grid-item-row")
            if not grid_item:
                continue
            
            # Extract company name
            title_wrap = grid_item.find("div", class_="title-wrap")
            if not title_wrap:
                continue
            
            companies_name_div = title_wrap.find("div", class_="companies-name")
            if not companies_name_div:
                continue
            
            name_paras = companies_name_div.find_all("p", class_="text-sm")
            company_name = None
            for p in name_paras:
                if "font-bold" in p.get("class", []) and "inline" in p.get("class", []):
                    # Check if it's not the "Exit" label
                    if "italic" not in p.get("class", []):
                        company_name = p.get_text(strip=True)
                        break
            
            if not company_name or company_name in seen_names:
                continue
            
            seen_names.add(company_name)
            
            # Extract sector - single value, not a list in source
            sector_elem = title_wrap.find("p", attrs={"fs-cmsfilter-field": "sector"})
            sector = sector_elem.get_text(strip=True) if sector_elem else None
            sectors = [sector] if sector else []
            
            # Extract region and location
            continent_wrap = grid_item.find("div", class_="continet-wrap")
            region = None
            location = None
            if continent_wrap:
                region_elem = continent_wrap.find("p", attrs={"fs-cmsfilter-field": "region"})
                if region_elem:
                    region = region_elem.get_text(strip=True)
                
                # Second p tag is the country/location
                location_ps = continent_wrap.find_all("p", class_="text-sm")
                if len(location_ps) >= 2:
                    location = location_ps[1].get_text(strip=True)
            
            # Extract year partnered
            year_partnered = None
            numbers_wrap = grid_item.find("div", class_="numbers-wrap")
            if numbers_wrap:
                year_elem = numbers_wrap.find("p", class_="text-sm", recursive=False)
                if year_elem:
                    year_text = year_elem.get_text(strip=True)
                    try:
                        year_partnered = int(year_text)
                    except (ValueError, TypeError):
                        pass
            
            # Extract stage from stage-wrapper
            stage = None
            if numbers_wrap:
                stage_wrapper = numbers_wrap.find("div", class_="stage-wrapper")
                if stage_wrapper:
                    stage_items = stage_wrapper.find_all("p", attrs={"fs-cmsfilter-field": "partnered"})
                    if stage_items:
                        stage = stage_items[0].get_text(strip=True)
            
            # Extract description
            description = None
            rich_txt_wrap = grid_item.find("div", class_="rich-txt-wrap")
            if rich_txt_wrap:
                desc_elem = rich_txt_wrap.find("p", class_="paragraph")
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
            
            # Extract company URL from the link element
            company_url = None
            link_elem = link_row.find("a", class_="company-link")
            if link_elem:
                href = link_elem.get("href")
                if href:
                    company_url = href if href.startswith("http") else urljoin(portfolio_url, href)
            
            # Build company dict - only include fields that exist on the page
            company_dict = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description,
                "sectors": sectors,
                "stage": stage,
                "region": region,
                "location": location,
                "year_partnered": year_partnered,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            
            companies.append(company_dict)
            
            # Polite delay between processing items
            time.sleep(0.1)
            
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
                         "..", "data", "hummingbirdvc_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
