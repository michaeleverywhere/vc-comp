#!/usr/bin/env python3
"""Moonfire Ventures portfolio scraper -> moonfire_companies.json
Source: https://www.moonfire.com/portfolio/ — Next.js (App Router) page. Company
records (slug, one-liner, website, founders, HQ, founded year, Moonfire sector,
backed year, lead partner) are decoded from the page's own server-rendered RSC
payload (self.__next_f); which cards are Moonfire portfolio vs the separate
"Prior Investments" section (partners' pre-Moonfire deals, EXCLUDED) is read from
the rendered page via headless Chrome (_chrome_dom.py)."""
import os, re, sys, json
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.moonfire.com/portfolio/"
PRIMARY = "Moonfire Ventures"
SECTOR_MAP = {"capital & finance": ["FinTech / Insurance"], "health & wellbeing": ["Health"],
              "security, infrastructure & tooling": ["Dev Tools / Cloud"], "work & knowledge": ["Future of Work"],
              "gaming, community & leisure": ["Gaming / Media / Entertainment"]}


def rsc_companies(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
    s = "".join(json.loads('"' + c + '"') for c in chunks)
    dec, out = json.JSONDecoder(), {}
    for m in re.finditer(r'\{"_id"', s):
        try:
            o, _ = dec.raw_decode(s, m.start())
        except ValueError:
            continue
        if isinstance(o, dict) and "foundedAt" in o and o.get("slug"):
            out[o["slug"]] = o
    return out


def portable_text(blocks):
    if not isinstance(blocks, list):
        return None
    return clean(" ".join(ch.get("text", "") for b in blocks if isinstance(b, dict) for ch in b.get("children", []) if isinstance(ch, dict)))


def _n(x):
    return re.sub(r"[^a-z0-9]", "", (x or "").lower())


def company_name(slug, o):
    """The RSC record has no name field (the site shows a logo), so take the name as
    written in the company's own long description ("Artifact is ...") when it matches
    the slug; else the logo/founder-image alt text when it matches; else the slug."""
    desc = portable_text(o.get("description")) or ""
    m = re.match(r"^([A-Z0-9][\w.&'’ -]{0,40}?)(?:,| is | are | helps | builds | provides | offers | was | has |’s |'s | \()", desc)
    cands = [m.group(1).strip()] if m else []
    for k in ("logo", "image"):
        alt = (o.get(k) or {}).get("alt") or ""
        cands.append(re.sub(r"(?i)[\s_-]+(founders?|logo|img|image)([\s_-]+(img|image))?\s*$", "", alt.strip()))
    for c in cands:
        if c and (_n(c) == _n(slug) or _n(c).startswith(_n(slug)) or _n(slug).startswith(_n(c))) and len(_n(c)) >= 2:
            c = clean(c)
            return c.replace("-", " ").title() if c == c.lower() and "-" in c else c
    return slug.replace("-", " ").title()


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = rsc_companies(fetch(SOURCE_URL))
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=200000), "html.parser")
    portfolio, prior, in_prior = [], [], False
    for el in s.find_all(True):
        if el.name in ("h1", "h2", "h3", "h4", "p", "span", "div") and not el.find(True) and \
                (clean(el.get_text(" ", strip=True)) or "").lower() == "prior investments":
            in_prior = True
        if el.name == "a" and "?company=" in (el.get("href") or ""):
            slug = el["href"].split("?company=")[1].split("&")[0]
            (prior if in_prior else portfolio).append(slug)
    out = []
    for slug in dict.fromkeys(portfolio):
        if slug in prior:
            continue
        o = data.get(slug, {})
        name = company_name(slug, o)
        secs = [x.get("name") for x in (o.get("sectors") or []) if isinstance(x, dict) and x.get("name")]
        web = o.get("website")
        lead = [clean(x) for x in (o.get("lead") or []) if clean(x)]
        out.append(rec(name, clean(o.get("shortDesc")) or portable_text(o.get("description")),
                       web if web and not is_social(web) else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=secs, sector_map=SECTOR_MAP, location=clean(o.get("headquarters")),
                       founded_year=o.get("foundedAt") if isinstance(o.get("foundedAt"), int) else None,
                       first_invested=o.get("backedAt") if isinstance(o.get("backedAt"), int) and o.get("backedAt") > 1990 else None,
                       founders=[clean(f) for f in (o.get("founders") or []) if clean(f)],
                       moonfire_lead=lead[0] if lead else None, profile_url=f"https://www.moonfire.com/portfolio/?company={slug}"))
    if len(out) < 50:
        raise SystemExit(f"FATAL: only {len(out)} Moonfire portfolio cards")
    print(f"excluded {len(set(prior))} 'Prior Investments' cards")
    finish(out, "moonfire", ("description", "company_url", "location", "founded_year", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
