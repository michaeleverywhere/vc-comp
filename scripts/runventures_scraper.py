#!/usr/bin/env python3
"""Run Ventures (formerly Signal Peak Ventures) portfolio scraper -> runventures_companies.json
Source: https://www.signalpeak.com/portfolio — Run Ventures, Salt Lake City venture firm formerly named Signal Peak
Ventures (signalpeak.com now carries the Run Ventures brand). The Webflow portfolio grid links each /portfolio/<slug>
page, which gives the sector tag, founders, description and "Visit Site" website. Cards and pages show logos rather
than name text, so the company name is the phrase in the site's own description that spells the company's website
domain or page slug (else the site-authored logo file name when it matches the slug; otherwise skipped)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.signalpeak.com/portfolio"
PRIMARY = "Run Ventures"
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())


def name_from(texts, url, slug):
    keys = set()
    if url:
        host = urlparse(url if "//" in url else "http://" + url).netloc.lower().split(":")[0]
        host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
        keys.add(norm(host.split(".")[0]))
    keys.add(norm(slug))
    keys = {k for k in keys if len(k) >= 2}
    for t in texts:
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.&+'’-]*", t or "")
        for i in range(len(toks)):
            for j in range(i + 1, min(i + 5, len(toks)) + 1):
                ph = " ".join(toks[i:j])
                ph = re.sub(r"(['’]s|[.'’-])+$", "", ph)
                if norm(ph) in keys:
                    return ph
    return None


def logo_name(img, slug):
    if not img or not img.get("src"):
        return None
    f = unquote(img["src"].rsplit("/", 1)[-1])
    f = re.sub(r"^[0-9a-f]{20,}_", "", f)
    f = re.sub(r"\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    f = re.sub(r"\s*\(.*?\)", "", f)
    f = re.sub(r"(?i)[\s_-]*(logo|logotipo|transparente|full|dark|white|black|color|colour|horizontal)\b.*$", "", f)
    f = clean(f.replace("_", " ").replace("-", " "))
    return f if f and norm(f) == norm(slug) else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    links = list(dict.fromkeys(urljoin(SOURCE_URL, a["href"]) for a in soup.select('a[href^="/portfolio/"]')
                               if a["href"].rstrip("/") != "/portfolio"))
    pages = fetch_many(links, workers=4)
    out, seen = [], set()
    for href in links:
        html = pages.get(href)
        if not html:
            continue
        s = BeautifulSoup(html, "html.parser")
        box = s.select_one("div.content-style")
        if not box:
            continue
        slug = href.rstrip("/").rsplit("/", 1)[-1]
        tag = box.select_one("p.company-tag")
        sector = clean(tag.get_text(" ")) if tag else None
        founders = [clean(p.get_text(" ")) for p in box.select("div.founder_text p")]
        founders = [f for f in founders if f]
        d = box.select_one(":scope > div.w-richtext")
        desc = clean(d.get_text(" ")) if d else None
        w = box.select_one("a.main-button[href]")
        site = w["href"].strip() if w and w["href"].startswith("http") and not is_social(w["href"]) else None
        name = name_from([desc], site, slug) or logo_name(box.select_one("img.company-profile-logo"), slug)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sector=sector, founders=founders or None, profile_url=href))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Run Ventures companies")
    finish(out, "runventures", ("description", "company_url", "sector", "everywhere_tags"))


if __name__ == "__main__":
    main()
