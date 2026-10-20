#!/usr/bin/env python3
"""The General Partnership (TheGP) portfolio scraper -> thegeneralpartnership_companies.json
Source: https://www.thegp.com/portfolio — every company page TheGP publishes (portfolio pages listed
in its own sitemap) with name, TheGP's one-line description, overview, founders, founded year, the year
TheGP partnered (first invested), acquirer when shown, the TheGP services involved and the company website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.thegp.com/portfolio"
BASE = "https://www.thegp.com"
PRIMARY = "The General Partnership"


def links():
    sm = fetch(BASE + "/sitemap.xml")
    urls = re.findall(r"<loc>\s*(https://www\.thegp\.com/portfolio/[a-z0-9-]+)\s*</loc>", sm)
    lst = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    urls += [BASE + a["href"] for a in lst.select('a[aria-label][href^="/portfolio/"]')]
    return list(dict.fromkeys(urls))


def caption_block(m, label):
    h = m.find(lambda t: t.name == "h2" and t.get_text(strip=True).lower() == label)
    if not h:
        return []
    p = h.find_next("p")
    return [clean(x) for x in p.get_text("\n", strip=True).split("\n") if clean(x)] if p else []


def parse(url, h):
    s = BeautifulSoup(h, "html.parser")
    t = s.title.get_text(strip=True) if s.title else ""
    name = clean(t.split("|")[0]) if "|" in t else None
    m = s.select_one("main")
    if not name or not m:
        return None
    h1 = m.select_one("h1")
    extra = {"profile_url": url}
    for line in caption_block(m, "milestones"):
        if g := re.match(r"Founded(?: in)? (\d{4})", line):
            extra["founded_year"] = int(g.group(1))
        elif g := re.match(r"Partnered (\d{4})", line):
            extra["first_invested"] = g.group(1)
        elif g := re.match(r"Acquired by (.+?)(?: (\d{4}))?$", line):
            extra["acquired_by"] = g.group(1)
            if g.group(2):
                extra["acquired_year"] = int(g.group(2))
    f = caption_block(m, "founders")
    if f:
        extra["founders"] = f
    sv = [clean(x.get_text(strip=True)) for x in m.select("span.relative.z-10")]
    if sv:
        extra["gp_services"] = list(dict.fromkeys(sv))
    desc = None
    for p in m.select("p.type-body-sm"):
        cl = p.get("class", [])
        if "leading-none" in cl or "mt-4" in cl or "mb-4" in cl:
            continue
        desc = clean(p.get_text(" ", strip=True))
        if desc:
            break
    web = None
    for a in m.select("a[href^=http]"):
        if "thegp.com" not in a["href"] and not is_social(a["href"]) and "visit" in a.get_text(" ", strip=True).lower():
            web = a["href"]
            break
    extra["status"] = "acquired" if "acquired_by" in extra else "active"
    extra["tagline"] = clean(h1.get_text(" ", strip=True)) if h1 else None
    return name, (desc or extra["tagline"]), web, extra


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    urls = links()
    pages = fetch_many(urls)
    out = []
    for u in urls:
        if not pages.get(u):
            continue
        r = parse(u, pages[u])
        if r:
            out.append(rec(r[0], r[1], r[2], PRIMARY, SOURCE_URL, scraped_at, **r[3]))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} TheGP companies")
    finish(out, "thegeneralpartnership", ("description", "company_url", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
