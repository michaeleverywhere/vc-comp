#!/usr/bin/env python3
"""Change Ventures portfolio scraper -> changeventures_companies.json
Source: https://changeventures.com/portfolio — Change Ventures, Baltic pre-seed/seed venture fund (Riga/Tallinn/Vilnius)
backing founders from the Baltics (Printify, Aerones...). The Webflow portfolio collection gives, per company, the
stage shown (Pre-seed/Seed/Series A/Growth, with Exited/Closed markers), industry, description and website. Cards
show logos rather than name text, so the company name is the phrase in the site's own description that spells the
company's website domain (else the site-authored logo file name when it spells the domain; otherwise skipped)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://changeventures.com/portfolio"
PRIMARY = "Change Ventures"
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


def visible(el):
    return el is not None and "w-condition-invisible" not in (el.get("class") or [])


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    out, seen = [], set()
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for c in soup.select("div.portfolio-more-container"):
            d = c.select_one("div.portfolio-more-p")
            desc = clean(d.get_text(" ")) if d else None
            site = None
            for a in c.select("div.portfolio-more-links a[href]"):
                h = a["href"].strip()
                if h.startswith("http") and not is_social(h) and not re.search(r"crunchbase|linkedin|pitchbook|changeventures\.com", h):
                    site = h
                    break
            keys = name_keys(site)
            logo = c.select_one("img.portfolio-more-logo")
            name = name_from([desc], keys) or logo_name(logo.get("src") if logo else None, keys)
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            stage = None
            for cls in ("seed", "preseed", "seriesa", "growth"):
                el = c.select_one(f"div.portfolio-stage-text-{cls}")
                if visible(el):
                    stage = clean(el.get_text(" "))
            status = "Active"
            if visible(c.select_one("div.portfolio-stage-text-exited")):
                status = "Exited"
            elif visible(c.select_one("div.portfolio-stage-text-closed")):
                status = "Closed"
            ind = c.select_one("div.portfolio-industry-text")
            out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                           stage=stage, status=status, industry=clean(ind.get_text(" ")) if ind else None))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Change Ventures companies")
    finish(out, "changeventures", ("description", "company_url", "status", "industry", "everywhere_tags"))


if __name__ == "__main__":
    main()
