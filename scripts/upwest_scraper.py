# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Optional
from urllib.parse import urljoin

PORTFOLIO_URL = "https://upwest.vc/portfolio"

def scrape() -> list[dict]:
    """
    Scrapes UpWest VC portfolio companies.
    This scraper parses the modal slide content that appears inline in the HTML
    to extract richer company details including descriptions and URLs.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    companies = []
    seen = set()
    
    try:
        response = session.get(PORTFOLIO_URL, timeout=20)
        response.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all modal slides - these contain the detailed company information
    modal_slides = soup.find_all("div", class_="portfolio--modal-slide")
    
    # If no modal slides found, fall back to grid cards
    if not modal_slides:
        modal_slides = soup.find_all("div", class_=re.compile(r"portfolio.*modal"))
    
    # Still no modals? Try a different approach - look for the grid cards and extract what we can
    if not modal_slides:
        grid_cards = soup.find_all("div", class_="portfolio--grid-card")
        
        for card in grid_cards:
            try:
                # Extract company name from logo alt text
                logo_img = card.find("img")
                if not logo_img:
                    continue
                
                alt_text = logo_img.get("alt", "").strip()
                company_name = re.sub(r'\s+logo$', '', alt_text, flags=re.IGNORECASE).strip()
                
                if not company_name or company_name.lower() in seen:
                    continue
                seen.add(company_name.lower())
                
                # Check for exit status
                exited_badge = card.find("span", class_="exited")
                status = "exited" if exited_badge else None
                
                # Try to extract company URL from logo image src or nearby links
                company_url = None
                logo_src = logo_img.get("src", "")
                
                # Look for company website in the card's modal data
                modal_id = card.get("data-modal")
                
                companies.append({
                    "company_name": company_name,
                    "company_url": company_url,
                    "description": None,
                    "status": status,
                    "profile_url": None,
                    "everywhere_tags": [],
                    "source_url": PORTFOLIO_URL
                })
                
            except Exception:
                continue
    else:
        # Process modal slides which contain richer information
        for slide in modal_slides:
            try:
                # Extract company name from heading or title
                company_name = None
                name_elem = (slide.find("h2") or slide.find("h3") or 
                           slide.find(class_=re.compile(r"company.*name", re.I)) or
                           slide.find(class_=re.compile(r"modal.*title", re.I)))
                
                if name_elem:
                    company_name = name_elem.get_text(strip=True)
                
                # If no name in modal, look for it in associated data attributes
                if not company_name:
                    data_name = slide.get("data-name") or slide.get("data-company")
                    if data_name:
                        company_name = data_name.replace("-", " ").title()
                
                if not company_name:
                    continue
                
                if company_name.lower() in seen:
                    continue
                seen.add(company_name.lower())
                
                # Extract description
                description = None
                desc_elem = (slide.find("p", class_=re.compile(r"description", re.I)) or
                           slide.find("div", class_=re.compile(r"description", re.I)) or
                           slide.find("div", class_=re.compile(r"content", re.I)))
                
                if desc_elem:
                    # Get all paragraph text within
                    paragraphs = desc_elem.find_all("p") if desc_elem.name != "p" else [desc_elem]
                    desc_text = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                    if desc_text and len(desc_text) > 20:
                        description = desc_text
                
                # Extract company URL
                company_url = None
                url_link = (slide.find("a", class_=re.compile(r"website|company-link|external", re.I)) or
                          slide.find("a", href=re.compile(r"^https?://(?!upwest\.vc)")))
                
                if url_link:
                    href = url_link.get("href", "")
                    if href and href.startswith("http") and "upwest.vc" not in href.lower():
                        company_url = href
                
                # Check for exit status
                status = None
                exited_elem = slide.find(class_=re.compile(r"exited|exit", re.I))
                if exited_elem:
                    status = "exited"
                
                # Extract profile URL (if UpWest has dedicated pages)
                profile_url = None
                profile_link = slide.find("a", href=re.compile(r"upwest\.vc/portfolio/[^/]+"))
                if profile_link:
                    profile_url = urljoin(PORTFOLIO_URL, profile_link.get("href"))
                
                companies.append({
                    "company_name": company_name,
                    "company_url": company_url,
                    "description": description,
                    "status": status,
                    "profile_url": profile_url,
                    "everywhere_tags": [],
                    "source_url": PORTFOLIO_URL
                })
                
            except Exception:
                continue
    
    # Final pass: try to enrich missing data by searching the entire page content
    if companies:
        # Build a map of company names to their data for enrichment
        page_text = soup.get_text()
        
        for company in companies:
            # If missing description, try to find it in page text near company name
            if not company.get("description"):
                name_lower = company["company_name"].lower()
                # Look for the company name in paragraphs
                for p in soup.find_all("p"):
                    p_text = p.get_text(strip=True)
                    if name_lower in p_text.lower() and len(p_text) > 30:
                        company["description"] = p_text
                        break
    
    # Remove duplicates by name (case-insensitive)
    unique_companies = []
    seen_final = set()
    for company in companies:
        name_key = company["company_name"].lower()
        if name_key not in seen_final:
            seen_final.add(name_key)
            unique_companies.append(company)
    
    return unique_companies


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
                         "..", "data", "upwest_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
