# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import json
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape() -> list[dict]:
    """Scrape Point Nine Capital portfolio companies."""
    
    portfolio_url = "https://pointnine.com/companies"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    companies = []
    seen_names = set()
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Try to extract company data from Finsweet/Webflow CMS attributes
    # The page uses fs-list-element and data-wf-bind attributes
    
    # First, look for company containers in the grid
    # Based on the HTML, companies appear to be in .cms_ci elements
    company_containers = soup.find_all("div", class_="cms_ci")
    
    # Filter to only those that look like company items (not filter checkboxes)
    company_items = []
    for container in company_containers:
        # Skip filter items by checking for fs-list-field="investment" or similar
        if container.find("input", {"fs-list-field": True}):
            continue
        # This might be a real company item
        if container.get("role") == "listitem":
            company_items.append(container)
    
    # If the grid approach doesn't work, try looking for company links/cards differently
    if not company_items:
        # Look for any div that might contain company info with links to company pages
        potential_items = soup.find_all("a", href=True)
        for link in potential_items:
            href = link.get("href", "").strip()
            # Company detail pages are often like /companies/company-slug
            if "/companies/" in href and href.count("/") == 2:
                parent = link.find_parent("div", recursive=True)
                if parent and parent not in company_items:
                    company_items.append(parent)
    
    # Extract company data from each container
    for container in company_items:
        try:
            # Get company name from link or text
            link = container.find("a", href=True)
            company_name = None
            company_url = None
            
            if link:
                company_url = link.get("href", "").strip()
                if company_url and not company_url.startswith("http"):
                    company_url = urljoin(portfolio_url, company_url)
                company_name = link.get_text(strip=True)
            
            # Fallback: extract from any heading or text
            if not company_name:
                heading = container.find(["h2", "h3", "h4", "h5"])
                if heading:
                    company_name = heading.get_text(strip=True)
                else:
                    # Get first meaningful text
                    text = container.get_text(strip=True)
                    if text and len(text) > 2:
                        company_name = text.split("\n")[0][:100]
            
            if not company_name:
                continue
            
            # Deduplicate by name
            if company_name in seen_names:
                continue
            seen_names.add(company_name)
            
            # Initialize fields
            description = None
            sectors = []
            stage = None
            founders = []
            status = None
            
            # Try to fetch company detail page for richer data
            if company_url:
                try:
                    time.sleep(0.3)  # Be polite
                    detail_resp = session.get(company_url, timeout=20)
                    detail_resp.raise_for_status()
                    detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                    
                    # Extract description from detail page
                    desc_elem = detail_soup.find(
                        ["div", "p"],
                        class_=lambda x: x and any(
                            kw in (x or "").lower() for kw in ["description", "summary", "about", "intro"]
                        )
                    )
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                    
                    # Look for founder information
                    founder_section = detail_soup.find(
                        ["div", "section"],
                        class_=lambda x: x and "founder" in (x or "").lower()
                    )
                    if founder_section:
                        founder_names = founder_section.find_all(
                            ["span", "p", "div"],
                            class_=lambda x: x and "name" in (x or "").lower()
                        )
                        for fname_elem in founder_names:
                            fname = fname_elem.get_text(strip=True)
                            if fname and fname not in founders:
                                founders.append(fname)
                    
                    # Extract sectors/tags from detail page
                    tag_elements = detail_soup.find_all(
                        ["span", "div", "a"],
                        class_=lambda x: x and any(
                            kw in (x or "").lower() for kw in ["tag", "sector", "category", "industry"]
                        )
                    )
                    for tag_elem in tag_elements:
                        tag_text = tag_elem.get_text(strip=True)
                        if tag_text and 2 < len(tag_text) < 50 and tag_text not in sectors:
                            sectors.append(tag_text)
                    
                    # Look for investment stage
                    stage_match = re.search(
                        r"(Pre-seed|Seed|Series A|Series B|Series C|Series D|Series E|Series F)",
                        detail_soup.get_text(),
                        re.IGNORECASE
                    )
                    if stage_match:
                        stage = stage_match.group(1)
                    
                except Exception:
                    pass  # If detail page fetch fails, continue with what we have
            
            # If no sectors found yet, try to extract from container text
            if not sectors:
                # Look for any span or div with tag-like content
                tag_spans = container.find_all(
                    ["span", "div"],
                    class_=lambda x: x and any(
                        kw in (x or "").lower() for kw in ["tag", "badge", "label", "chip"]
                    )
                )
                for tag_span in tag_spans:
                    tag_text = tag_span.get_text(strip=True)
                    if tag_text and tag_text not in sectors:
                        sectors.append(tag_text)
            
            # Try to find stage from container attributes or text
            if not stage:
                stage_match = re.search(
                    r"(Pre-seed|Seed|Series A|Series B|Series C|Series D|Series E|Series F)",
                    container.get_text(),
                    re.IGNORECASE
                )
                if stage_match:
                    stage = stage_match.group(1)
            
            record = {
                "company_name": company_name,
                "company_url": company_url,
                "description": description,
                "founders": founders,
                "sectors": sectors,
                "stage": stage,
                "status": status,
                "profile_url": company_url,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            
            companies.append(record)
            
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
                         "..", "data", "pointninecapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
