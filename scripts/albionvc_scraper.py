# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Albion VC portfolio companies from https://albion.vc/companies
    Returns list of dicts with company info.
    """
    portfolio_url = "https://albion.vc/companies"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    companies = []
    seen_names = set()
    
    # Fetch main portfolio page
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except Exception:
        return []
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Strategy: Extract company URLs from the logo ticker section
    # Then fetch each detail page for rich data
    company_links = []
    
    # Find all company links in the logo ticker
    ticker_items = soup.select("div.b-logo-ticker__item a")
    for link in ticker_items:
        href = link.get("href", "")
        if href and "/companies/" in href and not href.endswith("/companies/"):
            full_url = urljoin(portfolio_url, href)
            if full_url not in company_links:
                company_links.append(full_url)
    
    # Also check for any other company links in the page content
    for link in soup.select("a[href*='/companies/']"):
        href = link.get("href", "")
        if href and not href.endswith("/companies/"):
            full_url = urljoin(portfolio_url, href)
            if full_url not in company_links and "/companies/" in full_url:
                company_links.append(full_url)
    
    # Deduplicate by URL
    company_links = list(set(company_links))
    
    # Fetch each company detail page
    for idx, company_url in enumerate(company_links):
        if idx > 0:
            time.sleep(0.3)
        
        try:
            detail_resp = session.get(company_url, timeout=20)
            detail_resp.raise_for_status()
        except Exception:
            continue
        
        company_data = _parse_company_detail(detail_resp.text, company_url, portfolio_url)
        if company_data and company_data.get("company_name"):
            # Dedupe by name
            name_key = company_data["company_name"].lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                companies.append(company_data)
    
    return companies


def _parse_company_detail(html: str, company_url: str, source_url: str) -> Dict:
    """
    Parse a single company detail page to extract:
    - company_name
    - company_url (their website)
    - description
    - founders (if available)
    - sectors (if available)
    - stage (if available)
    - status (if available)
    - profile_url (the Albion VC company page)
    - everywhere_tags (empty list)
    - source_url (portfolio page)
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract company name from page title
    company_name = None
    title_tag = soup.find("title")
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        # Format typically: "Company Name - AlbionVC"
        if " - AlbionVC" in title_text:
            company_name = title_text.split(" - AlbionVC")[0].strip()
        elif " - " in title_text:
            company_name = title_text.split(" - ")[0].strip()
    
    # Fallback: extract from h1 heading
    if not company_name:
        h1 = soup.find("h1")
        if h1:
            company_name = h1.get_text(strip=True)
    
    # Fallback: derive from URL slug
    if not company_name:
        slug = company_url.rstrip("/").split("/")[-1]
        company_name = slug.replace("-", " ").title()
    
    # Extract description from meta description
    description = None
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()
    
    # Fallback: extract from article intro paragraphs
    if not description:
        article = soup.find("article")
        if article:
            # Look for first substantial paragraph
            for p in article.find_all("p", limit=5):
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    description = text
                    break
    
    # Extract company website URL
    # Look in the aside section for external links
    website_url = None
    aside = soup.find("div", class_="b-article-header__aside")
    if aside:
        for link in aside.find_all("a", href=True):
            href = link["href"].strip()
            # Filter out social media and internal links
            if (href.startswith("http") and 
                "albion.vc" not in href.lower() and
                "linkedin.com" not in href.lower() and
                "twitter.com" not in href.lower() and
                "x.com" not in href.lower()):
                website_url = href
                break
    
    # Fallback: scan article content for external links
    if not website_url:
        article = soup.find("article")
        if article:
            for link in article.find_all("a", href=True):
                href = link["href"].strip()
                if (href.startswith("http") and 
                    "albion.vc" not in href.lower() and
                    "linkedin.com" not in href.lower() and
                    "twitter.com" not in href.lower() and
                    "x.com" not in href.lower()):
                    website_url = href
                    break
    
    # Extract founders (if mentioned in aside or content)
    founders = []
    if aside:
        # Look for founder mention patterns
        aside_text = aside.get_text()
        # Common patterns: "Founded by X", "Founder: X", "Co-founder: X"
        founder_match = re.search(r'(?:Founded by|Founder[s]?:|Co-founder[s]?:)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:and|&)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*)', aside_text)
        if founder_match:
            founder_text = founder_match.group(1)
            # Split by "and" or "&"
            founder_names = re.split(r'\s+(?:and|&)\s+', founder_text)
            founders = [name.strip() for name in founder_names if name.strip()]
    
    # Extract sectors/tags
    sectors = []
    # Look for tags in the article header
    tags_container = soup.find("div", class_="b-article-header__tags")
    if tags_container:
        for tag in tags_container.find_all("a"):
            tag_text = tag.get_text(strip=True)
            if tag_text:
                sectors.append(tag_text)
    
    # Alternative: look for category/sector mentions in aside
    if not sectors and aside:
        # Look for common sector indicators
        for block in aside.find_all(["p", "div"]):
            text = block.get_text(strip=True)
            # Common patterns
            if any(keyword in text.lower() for keyword in ["sector:", "category:", "industry:"]):
                sector_match = re.search(r'(?:Sector|Category|Industry):\s*(.+)', text, re.IGNORECASE)
                if sector_match:
                    sectors.append(sector_match.group(1).strip())
    
    # Extract stage (seed, series A, etc.)
    stage = None
    if aside:
        aside_text = aside.get_text()
        stage_match = re.search(r'\b(Seed|Series [A-Z]|Pre-seed|Growth)\b', aside_text, re.IGNORECASE)
        if stage_match:
            stage = stage_match.group(1)
    
    # Extract status (Active, Exited, etc.)
    status = None
    # Look for status indicators
    page_text = soup.get_text()
    if re.search(r'\b(exited|acquired|ipo)\b', page_text, re.IGNORECASE):
        status = "Exited"
    elif re.search(r'\bactive\b', page_text, re.IGNORECASE):
        status = "Active"
    # Default to Active if no clear indicator
    if not status:
        status = "Active"
    
    return {
        "company_name": company_name,
        "company_url": website_url,
        "description": description,
        "founders": founders,
        "sectors": sectors,
        "stage": stage,
        "status": status,
        "profile_url": company_url,
        "everywhere_tags": [],
        "source_url": source_url
    }


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
                         "..", "data", "albionvc_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
