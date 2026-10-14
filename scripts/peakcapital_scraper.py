#!/usr/bin/env python3
"""Peak Capital (Amsterdam) portfolio scraper -> peakcapital_companies.json
Source: https://peak.capital/founders/ — WordPress REST `founders` post type
(title = company, content: founder names, tagline, description, co-investors,
company link; `businessmodel` taxonomy SaaS / Platform-Marketplace).
"""
import os, re, sys, html
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides, carry_forward_descriptions
from _d20_common import write_out

SOURCE_URL = "https://peak.capital/founders/"
API = "https://peak.capital/wp-json/wp/v2/founders?per_page=100&page={}"
TAX = "https://peak.capital/wp-json/wp/v2/businessmodel?per_page=100"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "peakcapital_companies.json")
PRIMARY = "Peak Capital"
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Gardia": ["Health", "Consumer"], "Juo": ["Consumer"], "revel8": ["Cybersecurity"], "Meet5": ["Consumer"],
    "Vetnio": ["Health"], "Delfio": ["Logistics / Supply Chain"], "Platform Engineering Labs": ["Dev Tools / Cloud"],
    "Healthsage": ["Health", "Dev Tools / Cloud"], "Circula": ["FinTech / Insurance", "Future of Work"],
    "Workwize": ["Future of Work", "Logistics / Supply Chain"], "Sonomo": ["FinTech / Insurance", "Gaming / Media / Entertainment"],
    "Authologic": ["Cybersecurity", "Dev Tools / Cloud"], "Hygraph": ["Dev Tools / Cloud"],
    "Precisely": ["RegTech/Gov/Legal", "Future of Work"], "Urban Sports Club": ["Consumer", "Health"],
    "Catawiki": ["Consumer"], "IENS": ["Consumer"], "OneFit": ["Consumer", "Health"], "United Wardrobe": ["Consumer"],
    "Radionomy": ["Gaming / Media / Entertainment"], "Cheapcargo": ["Logistics / Supply Chain"], "NPEX": ["FinTech / Insurance"],
    "Tradecloud": ["Logistics / Supply Chain"], "Floryn": ["FinTech / Insurance"], "LessonUp": ["Consumer"],
    "StoryChief": ["Gaming / Media / Entertainment"], "Route42": ["Transportation / Mobility"],
    "MoonPay": ["Web3 / Crypto", "FinTech / Insurance"], "Channable": ["Data & Analytics"], "Mibo": ["Consumer"],
    "Stack": ["Dev Tools / Cloud"], "DREM": ["Climate / Sustainability"], "VonWood": ["Logistics / Supply Chain"],
}


JOB_BOARDS = ("recruitee.com", "homerun.co", "greenhouse.io", "notion.site", "lever.co", "workable.com", "personio")


def company_root(h):
    """Peak links often point at a company's jobs page; keep the company's own
    root domain (jobs./careers. subdomains dropped), skip third-party job boards."""
    from urllib.parse import urlparse
    u = clean_url(h)
    if not u:
        return None
    pr = urlparse(u)
    host = pr.netloc.lower()
    if any(b in host for b in JOB_BOARDS):
        return None
    host = re.sub(r"^(jobs|careers|career|vacatures|overons)\.", "www.", host)
    return f"{pr.scheme}://{host}/"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    terms = {t["id"]: html.unescape(t["name"]) for t in fetch(TAX, as_json=True)}
    posts, page = [], 1
    while True:
        batch = fetch(API.format(page), as_json=True)
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    out, seen = [], set()
    for p in posts:
        name = clean(html.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        soup = BeautifulSoup(p["content"]["rendered"], "html.parser")
        h2 = soup.select_one("h2")
        founders_raw = clean(h2.get_text(" ")).rstrip(".") if h2 else None
        founders = [clean(x) for x in re.split(r",| and | & ", founders_raw or "") if clean(x)]
        paras = [clean(x.get_text(" ")) for x in soup.find_all("p", recursive=False) if clean(x.get_text(" "))]
        if not paras:
            blk = soup.select_one(".founder-block") or soup
            paras = [clean(x.get_text(" ")) for x in blk.find_all("p", recursive=False) if clean(x.get_text(" "))]
        tagline = re.sub(r"^[.…\s]*(are |bring you: )?", "", paras[0]).rstrip(" .") if paras else None
        tagline = tagline[:1].upper() + tagline[1:] if tagline else None
        desc = paras[1] if len(paras) > 1 else None
        investors, url = [], None
        for col in soup.select(".card-full-content-links .wp-block-column"):
            h3 = (clean(col.select_one("h3").get_text(" ")) if col.select_one("h3") else None) or ""
            links = [(clean(a.get_text(" ")), a.get("href")) for a in col.select("a[href]")]
            if h3.lower().startswith("investor"):
                investors = [t for t, _ in links if t and t.lower() != "peak"]
            elif h3.lower().startswith("link"):
                for t, h in links:
                    if h and h.startswith("http") and "peak.capital" not in h:
                        url = company_root(h)
                        if url:
                            break
        out.append({
            "company_name": name,
            "tagline": tagline,
            "description": desc or tagline,
            "company_url": url,
            "founders": founders,
            "business_model": [terms.get(t) for t in p.get("businessmodel", []) if terms.get(t)],
            "co_investors": investors,
            "profile_url": p.get("link"),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], " ".join(x for x in (r["tagline"], r["description"]) if x))
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "tagline", "company_url", "founders", "co_investors", "everywhere_tags"))


if __name__ == "__main__":
    main()
