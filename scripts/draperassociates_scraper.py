# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional

def scrape() -> list[dict]:
    """
    Scrapes Draper Associates portfolio from https://draper.vc/portfolio.
    
    Strategy:
    1. Parse the HTML table rows for basic company data
    2. Extract rich descriptions and additional fields from individual detail pages
    3. Focus on fields that are actually present on the site
    
    Returns list of dicts with company information.
    """
    portfolio_url = "https://draper.vc/portfolio"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        # Fetch main portfolio page
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Find all portfolio company rows
        rows = soup.select("[data-universe-row]")
        
        if not rows:
            return []
        
        for row in rows:
            try:
                # Extract company name
                name_el = row.select_one("[fs-list-field='company']")
                if not name_el:
                    continue
                
                company_name = name_el.get_text(strip=True)
                
                # Skip if empty or duplicate
                if not company_name or company_name in seen_names:
                    continue
                seen_names.add(company_name)
                
                # Extract logo URL
                logo_el = row.select_one("[universe-table_logo]")
                logo_url = None
                if logo_el and logo_el.get("src"):
                    logo_url = logo_el.get("src")
                
                # Extract location
                location_el = row.select_one("[fs-list-field='location']")
                location = location_el.get_text(strip=True) if location_el else None
                
                # Extract all categories (sectors)
                category_els = row.select("[fs-list-field='category']")
                sectors = []
                for cat_el in category_els:
                    cat_text = cat_el.get_text(strip=True)
                    if cat_text and cat_text not in sectors:
                        sectors.append(cat_text)
                
                # Extract status multiplier (indicates company stage/status)
                status_items = row.select("[status-item]")
                status_value = None
                if status_items:
                    # Get highest status value
                    max_status = 0
                    for item in status_items:
                        val = item.get("status-item")
                        if val:
                            try:
                                num_val = float(val)
                                if num_val > max_status:
                                    max_status = num_val
                            except (ValueError, TypeError):
                                pass
                    if max_status > 0:
                        # Map status multiplier to meaningful labels
                        if max_status >= 3:
                            status_value = "Unicorn"
                        elif max_status >= 2:
                            status_value = "Growth"
                        else:
                            status_value = "Active"
                
                # Find detail page link
                profile_url = None
                link_el = row.select_one("a[href*='/portfolio/']")
                if link_el and link_el.get("href"):
                    profile_url = urljoin(portfolio_url, link_el.get("href"))
                
                # Initialize company record
                record = {
                    "company_name": company_name,
                    "company_url": None,
                    "description": None,
                    "sectors": sectors,
                    "status": status_value,
                    "location": location,
                    "logo_url": logo_url,
                    "profile_url": profile_url,
                    "everywhere_tags": [],
                    "source_url": portfolio_url,
                }
                
                # Fetch detail page to get rich description and company website
                if profile_url:
                    time.sleep(0.3)  # Polite crawling
                    try:
                        detail_resp = session.get(profile_url, timeout=20)
                        detail_resp.raise_for_status()
                        detail_soup = BeautifulSoup(detail_resp.content, "html.parser")
                        
                        # Extract description - try multiple selectors
                        description = None
                        
                        # Try structured description fields
                        desc_candidates = [
                            detail_soup.select_one("meta[name='description']"),
                            detail_soup.select_one("meta[property='og:description']"),
                        ]
                        
                        for meta in desc_candidates:
                            if meta and meta.get("content"):
                                desc_text = meta.get("content").strip()
                                if len(desc_text) > 20:
                                    description = desc_text
                                    break
                        
                        # If no meta description, look for content paragraphs
                        if not description:
                            # Look for main content areas
                            content_areas = detail_soup.select(
                                ".w-richtext p, "
                                "[data-description] p, "
                                ".portfolio-content p, "
                                ".company-description, "
                                "section p"
                            )
                            
                            for p_el in content_areas:
                                text = p_el.get_text(strip=True)
                                # Filter out short or navigation text
                                if len(text) > 50 and not text.startswith("[ "):
                                    description = text
                                    break
                        
                        record["description"] = description
                        
                        # Extract company website from detail page
                        # Look for external links
                        link_candidates = detail_soup.select("a[href]")
                        for link in link_candidates:
                            href = link.get("href", "")
                            # Filter for likely company websites (not draper.vc, social, or mailto)
                            if (href.startswith("http") and 
                                "draper.vc" not in href and
                                "linkedin.com" not in href and
                                "twitter.com" not in href and
                                "facebook.com" not in href and
                                "medium.com" not in href and
                                "mailto:" not in href):
                                # Additional heuristics: look for domain-like patterns
                                if re.search(r"^https?://(?:www\.)?[\w-]+\.[\w]+", href):
                                    record["company_url"] = href
                                    break
                        
                    except Exception as e:
                        # Continue even if detail page fails
                        pass
                
                companies.append(record)
                
            except Exception as e:
                # Skip problematic rows
                continue
        
    except Exception as e:
        # If portfolio page fails, return whatever we have
        pass
    
    # Deduplicate by company name (just in case)
    unique_companies = {}
    for company in companies:
        name = company.get("company_name")
        if name and name not in unique_companies:
            unique_companies[name] = company
    
    return list(unique_companies.values())


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
                         "..", "data", "draperassociates_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
