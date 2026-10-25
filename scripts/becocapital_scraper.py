#!/usr/bin/env python3
"""BECO Capital portfolio scraper -> becocapital_companies.json
Source: https://www.becocapital.com/portfolio/ — BECO Capital (Dubai), Gulf/MENA venture capital firm investing from
inception to growth in technology companies. The portfolio grid is loaded by the page's own public
admin-ajax action "load_filtered_portfolio" (same request the page makes in the browser); each tile has the company
name (image alt) and a profile page with founders, country, founded year, partnered year/stage, status,
co-investors, a description and the company website. The "Exits" filter tab marks exited companies."""
import os, sys, re, time
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.becocapital.com/portfolio/"
AJAX = "https://www.becocapital.com/wp-admin/admin-ajax.php"
PRIMARY = "BECO Capital"
UA = {"User-Agent": "Mozilla/5.0 (compatible; vc-comp research)"}


def grid(first_tier=None):
    data = {"action": "load_filtered_portfolio", "posts_per_page": "-1", "orderby": "name", "order": "asc"}
    if first_tier:
        data["first_tier[]"] = first_tier
    r = requests.post(AJAX, data=data, headers=UA, timeout=40)
    r.raise_for_status()
    s = BeautifulSoup(r.json()["posts"], "html.parser")
    out = []
    for a in s.select("div.single-portfolio-box a[href]"):
        img = a.find("img")
        name = clean(img.get("alt")) if img else None
        if name:
            out.append((name, a["href"].strip()))
    return out


def profile(url):
    try:
        s = BeautifulSoup(fetch(url), "html.parser")
    except BaseException:
        return {}
    m = s.find("main") or s.body
    toks = [clean(t) for t in m.get_text("|", strip=True).split("|") if clean(t)]
    info, paras = {}, []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.endswith(":") and len(t) < 30 and i + 1 < len(toks):
            info[t[:-1].strip().lower()] = toks[i + 1]
            i += 2
            continue
        if len(t) > 60:
            paras.append(t)
        i += 1
    site = None
    for a in m.select('a[href^="http"]'):
        h = a["href"].strip()
        if "becocapital" not in h and not is_social(h):
            site = h
            break
    return {"info": info, "desc": " ".join(paras[:2])[:1500] or None, "site": site}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    tiles = grid()
    exits = {n.lower() for n, _ in grid("exits")}
    out, seen = [], set()
    for name, link in tiles:
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        p = profile(link)
        info = p.get("info", {})
        st = info.get("status")
        status = "Exited" if name.lower() in exits else ("Active" if not st or st.lower().startswith("active") else st)
        out.append(rec(name, p.get("desc"), p.get("site"), PRIMARY, SOURCE_URL, scraped_at,
                       status=status, beco_status=st, founders=info.get("founders") or info.get("founder"), country=info.get("country"),
                       founded=info.get("founded"), beco_partnered=info.get("partnered"),
                       co_investors=info.get("co-investors"), beco_profile_url=link))
        time.sleep(0.3)
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} BECO Capital companies")
    finish(out, "becocapital", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
