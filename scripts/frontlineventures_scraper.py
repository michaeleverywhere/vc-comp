# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import time
import re
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

def scrape() -> List[dict]:
    """
    Scrape Frontline Ventures portfolio companies from https://frontline.vc/companies
    Parses the visible HTML loop items instead of relying solely on JSON-LD.
    Fetches individual company detail pages to extract company URLs and richer data.
    """
    portfolio_url = "https://frontline.vc/companies"
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
    
    # Find all company row containers (e-loop-item elements with company class)
    company_rows = soup.find_all("div", class_=re.compile(r"e-loop-item.*\bcompany\b"))
    
    for row in company_rows:
        try:
            # Extract company name from heading
            name_elem = row.find("h3", class_="elementor-heading-title")
            if not name_elem:
                continue
            
            name_link = name_elem.find("a", href=True)
            if not name_link:
                continue
            
            company_name = name_link.get_text(strip=True)
            profile_url = name_link.get("href", "").strip()
            
            if not company_name or not profile_url or company_name in seen_names:
                continue
            
            seen_names.add(company_name)
            
            # Extract description from the company-desc element
            desc_elem = row.find("div", class_="company-desc")
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract location from location element
            location_elem = row.find("div", class_="location")
            location = None
            if location_elem:
                location_span = location_elem.find("span")
                if location_span:
                    location = location_span.get_text(strip=True)
            
            # Extract fund type from CSS classes
            fund_type = None
            class_list = row.get("class", [])
            for cls in class_list:
                if "fund-frontline-growth" in cls:
                    fund_type = "Frontline Growth"
                    break
                elif "fund-frontline-seed" in cls:
                    fund_type = "Frontline Seed"
                    break
            
            company_dict = {
                "company_name": company_name,
                "company_url": None,
                "description": description,
                "profile_url": profile_url,
                "everywhere_tags": [],
                "source_url": portfolio_url,
            }
            
            # Add location and fund tags
            if location:
                company_dict["everywhere_tags"].append(location)
            if fund_type:
                company_dict["everywhere_tags"].append(fund_type)
            
            # Fetch detail page to get company website URL
            time.sleep(0.3)
            try:
                detail_resp = session.get(profile_url, timeout=20)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                
                # Look for company website URL
                company_url = _extract_company_url(detail_soup, company_name)
                if company_url:
                    company_dict["company_url"] = company_url
                
            except requests.RequestException:
                pass
            
            companies.append(company_dict)
            
        except (AttributeError, TypeError, ValueError):
            continue
    
    return companies


def _extract_company_url(soup: BeautifulSoup, company_name: str) -> str:
    """
    Extract the company's actual website URL from their detail page.
    Looks for external links that are likely the company website.
    """
    # Common patterns for website links on detail pages
    # Look for links in prominent positions or with certain text
    
    # Strategy 1: Find links with text like "Visit Website", "Website", "Company Site"
    website_keywords = ["visit website", "website", "company site", "visit site", "learn more"]
    for keyword in website_keywords:
        link = soup.find("a", href=True, string=re.compile(keyword, re.IGNORECASE))
        if link:
            url = link.get("href", "").strip()
            if _is_valid_company_url(url):
                return url
    
    # Strategy 2: Look for the first prominent external link (not social media, not frontline.vc)
    all_links = soup.find_all("a", href=True)
    
    # Filter to likely company URLs
    for link in all_links:
        url = link.get("href", "").strip()
        if _is_valid_company_url(url):
            # Prefer links early in the page
            return url
    
    return None


def _is_valid_company_url(url: str) -> bool:
    """Check if URL is likely a company website (not social media, internal, etc.)"""
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Must be HTTP(S)
    if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
        return False
    
    # Exclude internal frontline.vc links
    if "frontline.vc" in url_lower:
        return False
    
    # Exclude common social media and non-company-site domains
    excluded_domains = [
        "linkedin.com", "twitter.com", "facebook.com", "instagram.com",
        "youtube.com", "github.com", "crunchbase.com", "angellist.com",
        "medium.com", "substack.com", "mailto:", "tel:"
    ]
    
    for domain in excluded_domains:
        if domain in url_lower:
            return False
    
    # Exclude anchor links and javascript
    if url_lower.startswith("#") or url_lower.startswith("javascript:"):
        return False
    
    return True


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
                         "..", "data", "frontlineventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
