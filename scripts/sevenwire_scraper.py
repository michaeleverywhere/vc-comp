#!/usr/bin/env python3
"""7wireVentures portfolio scraper -> sevenwire_companies.json
Source: https://www.7wireventures.com/portfolio/ (WPBakery grid: logo alt
name, "- Exited" marker, tagline) plus each /portfolio/<slug>/ page
(overview paragraph, website, FOUNDED, HEADQUARTERS, CEO). 7wire invests in
healthcare, so every company carries the Health tag.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, fetch_many, clean, clean_url, label_after, year_of, tags_for,
                             first_external_link, apply_tag_overrides, carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://www.7wireventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "sevenwire_companies.json")
PRIMARY = "7wireVentures"
LABELS = ("FOUNDED", "HEADQUARTERS", "CEO", "CEOS", "FOUNDERS", "CAREERS")
TAG_OVERRIDES = {
    "GroundGame Health": ["Health"],
    "MedArrive": ["Health"],
    "Medisafe": ["Health"],
    "nocd": ["Health"],
    "Override": ["Health"],
    "Cirrus MD": ["Health"],
    "higi": ["Health"],
    "Summer Health": ["Health"],
    "When": ["Future of Work", "Health"],
    "PayZen": ["Health", "FinTech / Insurance"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items, seen_urls = [], set()
    for a in soup.select("a.vc_single_image-wrapper[href*='/portfolio/']"):
        url = a["href"].replace("://7wireventures.com", "://www.7wireventures.com")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        img = a.find("img")
        alt = clean(img.get("alt")) if img else None
        col = a.find_parent(class_="wpb_wrapper")
        tag = col.select_one(".wpb_text_column p") if col else None
        items.append({"url": url, "alt": alt, "tagline": clean(tag.get_text(" ", strip=True)) if tag else None})
    pages = fetch_many([i["url"] for i in items], workers=3)
    out, seen = [], set()
    for it in items:
        alt = it["alt"] or ""
        exited = bool(re.search(r"(?i)-\s*exited\s*$", alt))
        name = clean(re.sub(r"(?i)\s*-\s*exited\s*$", "", alt))
        d = BeautifulSoup(pages.get(it["url"]) or "", "html.parser")
        for x in d(["script", "style", "svg", "nav", "header", "footer", "noscript"]):
            x.decompose()
        if d.title:
            tname = clean(re.sub(r"\s*-\s*7wire Ventures\s*$", "", d.title.get_text()))
            if tname and not name:
                name = tname
        if not name:
            name = it["url"].rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        strings = [s for s in d.stripped_strings]
        desc = None
        try:
            i = [s.strip().upper() for s in strings].index("PORTFOLIO")
            desc = clean(strings[i + 1]) if i + 1 < len(strings) else None
        except ValueError:
            pass
        if desc and desc.upper() in LABELS:
            desc = None
        site = None
        for a in d.select("a[href^=http]"):
            h = a["href"]
            if "7wireventures" in h.lower() or "talent." in h or "careers" in h.lower() or "jobs" in h.lower():
                continue
            if (a.get_text(strip=True) or "").upper() == "CAREERS":
                continue
            site = clean_url(h)
            if site:
                break
        # one page links a sibling company's domain (WellTheory -> zerigohealth.com); drop such mismatches
        if site and name:
            host = re.sub(r"^https?://(www\.)?", "", site.lower()).split("/")[0]
            toks = [t for t in re.findall(r"[a-z0-9]+", name.lower()) if len(t) >= 3 and t != "health"]
            other = [o["alt"] for o in items if o is not it and o["alt"]]
            if toks and not any(t in host for t in toks) and any(
                    any(t in host for t in re.findall(r"[a-z0-9]+", o.lower()) if len(t) >= 4 and t != "health") for o in other):
                site = None
        ceo = label_after(strings, "CEO", "CEOS", "CO-CEOS")
        out.append({
            "company_name": name,
            "description": desc or it["tagline"],
            "tagline": it["tagline"],
            "company_url": site,
            "year_founded": year_of(label_after(strings, "FOUNDED")),
            "location": label_after(strings, "HEADQUARTERS", "HQ"),
            "ceo": ceo if ceo and ceo.upper() not in LABELS else None,
            "exited": exited,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": it["url"],
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        kw = [t for t in tags_for(r["company_name"], r["description"]) if t not in ("Health", "BioTech")]
        r["everywhere_tags"] = (["Health"] + kw)[:2]
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "year_founded", "everywhere_tags"))


if __name__ == "__main__":
    main()
