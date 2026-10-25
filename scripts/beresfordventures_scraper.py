#!/usr/bin/env python3
"""Beresford Ventures portfolio scraper -> beresfordventures_companies.json
Source: https://www.beresfordventures.com/portfolio/ — Beresford Ventures, early-stage venture investor in software,
health and climate technology. The WordPress portfolio grid shows one logo tile per company linking to the company's
website (an "Exited" tab/marker flags exits). Tiles carry no name text, so the company name is the site-authored logo
file name, kept only when it spells the company's website domain (tiles that don't match are skipped)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.beresfordventures.com/portfolio/"
PRIMARY = "Beresford Ventures"
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())


def name_keys(url, slug=None):
    keys = set()
    if url:
        host = urlparse(url if "//" in url else "http://" + url).netloc.lower().split(":")[0]
        host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
        keys.add(norm(host.split(".")[0]))
    if slug:
        keys.add(norm(slug))
    return {k for k in keys if len(k) >= 2}


def name_from(texts, keys):
    """The phrase of the site's own text that spells the company's domain (or page slug)."""
    for t in texts:
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.&+'’-]*", t or "")
        for i in range(len(toks)):
            for j in range(i + 1, min(i + 5, len(toks)) + 1):
                ph = re.sub(r"(['’]s|[.'’-])+$", "", " ".join(toks[i:j]))
                if norm(ph) in keys:
                    return ph
    return None


def logo_name(src, keys):
    """Site-authored logo file name, only when it spells the domain/slug."""
    if not src:
        return None
    f = unquote(src.rsplit("/", 1)[-1])
    f = re.sub(r"^[0-9a-f]{20,}_", "", f)
    f = re.sub(r"(-\d+x\d+|-e\d{9,})?\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    f = re.sub(r"\s*\(.*?\)", "", f)
    f = re.sub(r"(?i)[\s_-]*(logo|logotipo|transparente|full|dark|white|black|color|colour|horizontal|green|fka)\b.*$", "", f)
    f = clean(f.replace("_", " ").replace("-", " "))
    return f if f and norm(f) in keys else None


def keys_full(url):
    k = name_keys(url)
    host = urlparse(url).netloc.lower().split(":")[0]
    host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
    k.add(norm(host))
    return k


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    exited = set()
    for col in soup.select("div.vc_column-inner"):
        a = col.select_one("a.column-link[href]")
        if a and re.search(r"\bExited\b", col.get_text(" ")):
            exited.add(a["href"].strip())
    out, seen = [], set()
    for col in soup.select("div.vc_column-inner"):
        a = col.select_one("a.column-link[href]")
        img = col.select_one("img")
        if not a or not img:
            continue
        site = a["href"].strip()
        if not site.startswith("http") or is_social(site) or "beresfordventures" in site:
            continue
        keys = keys_full(site)
        src = img.get("data-src") or img.get("src")
        name = logo_name(src, keys)
        if not name:
            continue
        name = name.rstrip("_ ").strip()
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at,
                       status="Exited" if site in exited else None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Beresford Ventures companies")
    finish(out, "beresfordventures", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
