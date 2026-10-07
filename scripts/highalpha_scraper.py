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
    Scrape High Alpha portfolio companies from https://highalpha.com/companies
    
    Returns:
        List of dicts with company information including name, description, 
        investment type, status, and detail page data where available.
    """
    portfolio_url = "https://highalpha.com/companies"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        resp = session.get(portfolio_url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return []
    
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Find all company items in the portfolio list
    co_items = soup.find_all("div", class_="co-item", attrs={"role": "listitem"})
    panels = {}
    for _p in soup.find_all("div", class_="co-content-item"):
        if _p.get("index"):
            panels.setdefault(_p["index"].strip(), _p)
    
    for item in co_items:
        try:
            co_trigger = item.find("div", class_="co-trigger")
            if not co_trigger:
                continue
            
            # Extract company name
            h2_elem = co_trigger.find("h2")
            if not h2_elem:
                continue
            
            company_name = h2_elem.get_text(strip=True)
            if not company_name or company_name in seen_names:
                continue
            
            seen_names.add(company_name)
            
            # Extract description
            description = None
            desc_div = co_trigger.find("div", class_="co-trigger-desc")
            if desc_div:
                desc_p = desc_div.find("p")
                if desc_p:
                    description = desc_p.get_text(strip=True)
            
            # Extract tags (investment type and status)
            tags_div = co_trigger.find("div", class_="co-trigger-tags")
            investment_type = None
            status = "Active"  # Default to Active if not marked Acquired
            
            if tags_div:
                tag_divs = tags_div.find_all("div", class_="tag")
                for tag in tag_divs:
                    tag_text = tag.get_text(strip=True)
                    
                    # Investment type
                    if "cc-co-studio" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        investment_type = "Studio"
                    elif "cc-co-coinvest" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        investment_type = "Co-Invest"
                    elif "cc-co-capital" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        investment_type = "Anchor"
                    
                    # Status
                    if "cc-co-acquired" in tag.get("class", []) and "w-condition-invisible" not in tag.get("class", []):
                        status = "Acquired"
            
            # Extract company slug from hidden input
            company_slug = None
            jb_embed = item.find("div", class_="jb-embed")
            if jb_embed:
                hidden_input = jb_embed.find("input", type="hidden")
                if hidden_input:
                    company_slug = hidden_input.get("value", "").strip()
            
            # Build company URL from slug
            # /companies/{slug} pages 404; real detail lives in the on-page
            # co-content-item panel keyed by index=<name> (2026-10-07 fix).
            company_url = None
            record = {
                "company_name": company_name,
                "company_url": company_url,
                "tagline": description,
                "description": description,
                "investment_type": investment_type,
                "status": status,
                "everywhere_tags": [],
                "source_url": portfolio_url
            }
            panel = panels.get(company_name)
            if panel is not None:
                body = panel.find("div", class_="cc-body-content") or panel
                paras = [p.get_text(" ", strip=True) for p in body.find_all("p")]
                paras = [t for t in paras if t and t != "\u200d"]
                long_desc = [t for t in paras if t != description and not re.search(r"\bwas acquired by\b", t)]
                if long_desc:
                    record["description"] = long_desc[0]
                for t in paras:
                    m = re.search(r"was acquired by (.+?)(?: in (\d{4}))?$", t.strip().rstrip(" ."))
                    if m:
                        record["acquirer"] = m.group(1).strip()
                        if m.group(2):
                            record["exit_year"] = m.group(2)
                        record["status"] = "acquired"
                for li in panel.find_all("li", class_="co-info-item"):
                    if "w-condition-invisible" in (li.get("class") or []):
                        continue
                    h = li.find("h4")
                    label = h.get_text(strip=True) if h else ""
                    a = li.find("a", href=True)
                    val_el = li.find(["div", "a"], class_=re.compile("paragraph"))
                    val = val_el.get_text(strip=True) if val_el else ""
                    if label == "Website" and a and a["href"].startswith("http"):
                        record["company_url"] = a["href"].strip()
                    elif label == "Year Founded" and val:
                        record["year_founded"] = val
                    elif label == "Fund" and val:
                        record["fund"] = val
                    elif label.startswith("CEO") and val:
                        record["ceo"] = val
                        if "Founder" in label:
                            record["founders"] = [val]
            
            companies.append(record)
            
        except Exception:
            # Skip problematic entries silently
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
                         "..", "data", "highalpha_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
