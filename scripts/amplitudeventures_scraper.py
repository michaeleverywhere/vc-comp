#!/usr/bin/env python3
"""Amplitude Ventures portfolio scraper -> amplitudeventures_companies.json
Source: https://amplitudevc.com/en/portfolio — portfolio page via chrome-dom; company name + website where published."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://amplitudevc.com/en/portfolio"
PRIMARY = "Amplitude Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(dom(url, 15000, min_len=3000), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []

    s = soup_of(SOURCE_URL)
    host = 'amplitude'
    seen = set()
    for img in s.find_all("img", alt=True):
        nm = clean(re.sub(r"(?i)[\s_-]*(logo|logotype|icon)(\.\w+)?\s*$", "", img.get("alt") or ""))
        if nm and ":" in nm:
            nm = nm.split(":", 1)[0].strip()
        nm = re.sub(r"(?i)\s+logo.*$", "", nm or "").strip()
        if not nm or len(nm) > 40 or len(nm.split()) > 5:
            continue
        if re.search(r"(?i)^(logo|home|menu|banner|image|photo|icon|opens in|type a description|customise|customize|avlogo)", nm):
            continue
        if host and host.lower()[:5] in nm.lower().replace(" ", ""):
            continue
        if re.search(r"(?i)ventures|capital|partners", nm) and len(nm.split()) <= 3:
            continue
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = img.find_parent("a", href=True)
        u = None
        if a and (a.get("href") or "").startswith("http"):
            href = a["href"]
            d = re.sub(r"^www\.", "", re.sub(r"^https?://", "", href).split("/")[0].lower())
            if host not in d and not is_social(href):
                u = href.split("?")[0]
        out.append(rec(nm, None, u, PRIMARY, SOURCE_URL, scraped_at))
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]

    finish(out, "amplitudeventures", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
