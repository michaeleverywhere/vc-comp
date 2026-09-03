# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Iris Capital portfolio companies from their website.
    Returns a list of dicts with company information.
    """
    session = requests.Session()
    companies = []
    seen_names = set()
    
    portfolio_url = "https://iriscapital.com/portfolio"
    
    try:
        # Fetch the main portfolio page
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Find all portfolio company items in the dynamic list
        portfolio_items = soup.find_all("div", {"role": "listitem", "class": "portfolio-logo_item"})
        
        for item in portfolio_items:
            try:
                # Extract company name from the img alt attribute
                logo_img = item.find("img", {"class": "portfolio-logo_image"})
                if not logo_img:
                    continue
                
                company_name = logo_img.get("alt", "").strip()
                if not company_name or company_name in seen_names:
                    continue
                
                seen_names.add(company_name)
                
                # Extract description from modal text
                description = None
                modal_text_div = item.find("div", {"class": "text-size-medium text-style-3lines"})
                if modal_text_div:
                    description = modal_text_div.get_text(strip=True)
                
                # Extract company website URL
                website_url = None
                website_button = item.find("a", {"class": "button-border"})
                if website_button:
                    href = website_button.get("href", "").strip()
                    if href and not href.startswith("#"):
                        website_url = href
                
                # Extract metadata from hidden divs using fs-cmsfilter-field attributes
                status = None
                activity = None
                location = None
                category = None
                
                hidden_div = item.find("div", {"class": "portfolio_logo-hidden"})
                if hidden_div:
                    status_div = hidden_div.find("div", {"fs-cmsfilter-field": "status"})
                    if status_div:
                        status = status_div.get_text(strip=True)
                    
                    activity_div = hidden_div.find("div", {"fs-cmsfilter-field": "activity"})
                    if activity_div:
                        activity = activity_div.get_text(strip=True)
                    
                    location_div = hidden_div.find("div", {"fs-cmsfilter-field": "location"})
                    if location_div:
                        location = location_div.get_text(strip=True)
                
                # Extract category from collection list
                category_list = item.find("div", {"class": "collection-list_hide"})
                if category_list:
                    category_div = category_list.find("div", {"fs-cmsfilter-field": "category"})
                    if category_div:
                        category = category_div.get_text(strip=True)
                
                # Extract website domain as profile_url reference if available
                profile_url = None
                domain_text_div = item.find("div", {"class": "heading-style-h6 text-style-allcaps"})
                if domain_text_div:
                    domain_text = domain_text_div.get_text(strip=True)
                    if domain_text:
                        profile_url = f"https://{domain_text}" if not domain_text.startswith("http") else domain_text
                
                # Build company dict
                company = {
                    "company_name": company_name,
                    "company_url": website_url,
                    "description": description,
                    "founders": [],
                    "sectors": [category] if category else [],
                    "stage": activity,
                    "status": status,
                    "profile_url": profile_url,
                    "everywhere_tags": [],
                    "source_url": portfolio_url
                }
                
                companies.append(company)
                time.sleep(0.3)  # Rate limiting between extractions
            
            except Exception:
                # Skip any individual item that fails to parse
                continue
        
        # For companies with rich modal information, fetch additional details from modals
        # The modal content is embedded in the HTML with company details
        modal_companies = _extract_modal_companies(soup, portfolio_url)
        
        # Merge modal details with existing companies by name
        modal_by_name = {m["company_name"]: m for m in modal_companies}
        for company in companies:
            if company["company_name"] in modal_by_name:
                modal_data = modal_by_name[company["company_name"]]
                # Enrich with modal data
                if modal_data.get("description") and not company["description"]:
                    company["description"] = modal_data["description"]
                if modal_data.get("founders"):
                    company["founders"] = modal_data["founders"]
        
    except requests.RequestException:
        pass
    
    return companies


def _extract_modal_companies(soup: BeautifulSoup, portfolio_url: str) -> List[Dict]:
    """
    Extract company details from embedded modal data in the page.
    Modals contain detailed descriptions and founder information.
    """
    modal_companies = []
    
    # Find all modal wrappers (entrepreneurs_modal*-wrapper)
    modal_wrappers = soup.find_all("div", {"class": re.compile(r"entrepreneurs_modal\d+-wrapper")})
    
    for modal in modal_wrappers:
        try:
            # Extract company name from the right side text
            company_name = None
            
            # Look for founder names and company reference
            modal_right = modal.find("div", {"class": "entrepreneurs_modal-grid-right"})
            if not modal_right:
                continue
            
            # Extract from bold text that contains company/founder info
            name_spans = modal_right.find_all(["span", "strong"])
            for span in name_spans:
                text = span.get_text(strip=True)
                if text and len(text) > 0:
                    company_name = text
                    break
            
            # Extract description
            description = None
            desc_div = modal.find("div", {"class": "text-size-medium"})
            if desc_div:
                # Get all text but exclude founder names
                full_text = desc_div.get_text(strip=True)
                if full_text:
                    description = full_text[:500]  # Limit description length
            
            # Extract founders - look for names in structured text
            founders = []
            text_content = modal.get_text(strip=True)
            
            # Look for patterns like "Name" followed by "Co-founder" or "Founder"
            founder_match = re.findall(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+(?:Co-)?[Ff]ounder', text_content)
            if founder_match:
                founders = list(set(founder_match))[:3]  # Max 3 founders, deduplicated
            
            # If we found a company with details, add to modal companies
            if company_name:
                modal_companies.append({
                    "company_name": company_name,
                    "description": description,
                    "founders": founders,
                    "source_url": portfolio_url
                })
        
        except Exception:
            continue
    
    return modal_companies


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
                         "..", "data", "iriscapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
