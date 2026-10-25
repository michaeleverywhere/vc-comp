#!/usr/bin/env python3
"""Armilar Venture Partners portfolio scraper -> armilar_companies.json
Source: https://armilar.com/portfolio — Armilar Venture Partners, Lisbon-based venture capital firm backing
Portuguese-founded technology companies (OutSystems, Feedzai, Sword Health...). The Webflow portfolio grid lists
every company (an "Active" tab marks current holdings); each /companies/<slug> page gives the tagline, website,
description and the Armilar partner following it. The site shows logos rather than name text, so the company name is
taken as the phrase in the site's own tagline/description that spells the company's website domain (companies
without such a phrase fall back to the site-authored logo file name when it matches the page slug, else are skipped)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean
from _d50_common import rec, finish

SOURCE_URL = "https://armilar.com/portfolio"
PRIMARY = "Armilar Venture Partners"
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
    active = set()
    for pane in soup.select("div.w-tab-pane"):
        hrefs = [urljoin(SOURCE_URL, a["href"]) for a in pane.select('a[href^="/companies/"]')]
        if pane.get("data-w-tab") == "Tab 2":
            active.update(hrefs)
    links = list(dict.fromkeys(urljoin(SOURCE_URL, a["href"]) for a in soup.select('a[href^="/companies/"]')))
    pages = fetch_many(links, workers=4)
    out, seen = [], set()
    for href in links:
        html = pages.get(href)
        if not html:
            continue
        s = BeautifulSoup(html, "html.parser")
        box = s.select_one("div.div-block-6")
        if not box:
            continue
        slug = href.rstrip("/").rsplit("/", 1)[-1]
        tag = box.select_one("div.text-block-11")
        tagline = clean(tag.get_text(" ")) if tag else None
        w = box.select_one("a.link-block-4[href]")
        site = w["href"].strip() if w and w["href"].strip().startswith("http") else None
        rt = box.select_one("div.w-richtext")
        desc = None
        if rt:
            ps = [clean(p.get_text(" ")) for p in rt.find_all("p")]
            ps = [p for p in ps if p and p not in ("\u200d",) and not re.match(r"(?i)view open roles", p)]
            desc = clean(" ".join(ps)) if ps else None
        name = name_from([tagline, desc], site, slug) or logo_name(box.select_one("img.logo-private"), slug)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        partners = [clean(x.get_text(" ")) for x in box.select("div.managers")]
        out.append(rec(name, desc or tagline, site, PRIMARY, SOURCE_URL, scraped_at,
                       tagline=tagline, status="Active" if href in active else None,
                       armilar_partners=partners or None, profile_url=href))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Armilar companies")
    finish(out, "armilar", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
