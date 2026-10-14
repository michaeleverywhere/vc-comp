# AUTO-GENERATED scraper (Claude API) — passed static guard + sandboxed
# validation before commit. Regenerate rather than hand-edit heavily.
import requests
import time
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin

def scrape() -> List[Dict]:
    """
    Scrape Cambridge Innovation Capital portfolio companies from the Start Codon accelerator.
    Returns a list of portfolio company dictionaries.
    """
    portfolio_url = "https://cic.vc/portfolio"
    companies = []
    seen_names = set()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        # Fetch the main portfolio page
        response = session.get(portfolio_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all portfolio company grid items in the "Active Portfolio" section
        grid_container = soup.find('div', class_='company-grid')
        if not grid_container:
            return companies
        
        grid_items = grid_container.find_all('div', class_='grid-item')
        
        for item in grid_items:
            try:
                # Extract company name from h4 tag
                company_name_elem = item.find('h4')
                if not company_name_elem:
                    continue
                
                company_name = company_name_elem.get_text(strip=True)
                
                # Skip duplicates and empty names
                if not company_name or company_name in seen_names:
                    continue
                seen_names.add(company_name)
                
                # Extract description from the paragraph following the name
                description = None
                desc_elem = item.find('p', class_='mb-0')
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                
                # Extract company URL from the link with class 'full-banner-arrow-link'
                company_url = None
                link_elem = item.find('a', class_='full-banner-arrow-link')
                if link_elem and link_elem.get('href'):
                    company_url = link_elem.get('href')
                
                # Build company record - only include fields that actually have data
                company_record = {
                    'company_name': company_name,
                    'company_url': company_url,
                    'description': description,
                    'everywhere_tags': [],
                    'source_url': portfolio_url
                }
                
                companies.append(company_record)
                time.sleep(0.3)
                
            except (AttributeError, IndexError, TypeError):
                continue
        
    except requests.RequestException:
        pass
    
    return companies



# --- 2026-10 site move: cic.vc/portfolio now redirects to a news post; the
# portfolio lives at https://www.cic.vc/companies/ (WordPress grid with
# company_type-private/-acquired/-ipo classes) + /company/<slug>/ detail pages.
def scrape_v2() -> List[Dict]:
    import re
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'})
    base = "https://www.cic.vc/companies/"
    soup = None
    for attempt in range(6):  # the WP cache intermittently serves a grid-less page
        soup = BeautifulSoup(session.get(base, timeout=30).content, 'html.parser')
        if soup.select('div.grid-item.type-company'):
            break
        time.sleep(3 * (attempt + 1))
    if not soup.select('div.grid-item.type-company'):
        raise SystemExit("cic.vc/companies served no company grid (cache/bot variant) -- keeping previous data")
    out, seen = [], set()
    for item in soup.select('div.grid-item.type-company'):
        a = item.select_one('h4 a[href]')
        if not a:
            continue
        name = a.get_text(" ", strip=True)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cls = item.get('class', [])
        ctype = next((c.split('company_type-', 1)[1] for c in cls if c.startswith('company_type-')), None)
        status = {'private': 'active', 'current-companies': 'active', 'acquired': 'acquired', 'ipo': 'Public'}.get(ctype, ctype)
        tagline_el = item.select_one('h4 + p')
        tagline = tagline_el.get_text(" ", strip=True) if tagline_el else None
        img = item.select_one('img')
        rec = {'company_name': name, 'company_url': None, 'description': tagline, 'tagline': tagline,
               'status': status, 'company_profile_url': a['href'],
               'logo_url': img.get('src') if img else None, 'source_url': base}
        try:
            d = BeautifulSoup(session.get(a['href'], timeout=30).content, 'html.parser')
            vw = next((x for x in d.select('a[href]') if x.get_text(strip=True).lower() == 'visit website'), None)
            if vw and vw['href'].startswith('http'):
                rec['company_url'] = vw['href']
                box = vw.find_parent(lambda t: t.name in ('div', 'section') and len(t.find_all('p')) >= 1)
                paras = [re.sub(r"\s+", " ", p.get_text(" ", strip=True)) for p in (box.find_all('p') if box else [])]
                paras = [p for p in paras if p and p.lower() != 'visit website']
                if paras:
                    rec['description'] = " ".join(paras)
        except requests.RequestException:
            pass
        if rec['status'] == 'acquired' and rec['company_url']:
            # for exited companies CIC's "Visit Website" often points at the acquirer
            rec['visit_website_url'] = rec.pop('company_url'); rec['company_url'] = None
        out.append(rec)
        time.sleep(0.3)
    return out


scrape = scrape_v2

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
                         "..", "data", "cambridgeinnovationcapital_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
