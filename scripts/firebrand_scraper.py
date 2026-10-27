#!/usr/bin/env python3
"""Firebrand Ventures portfolio scraper -> firebrand_companies.json
Source: https://www.firebrandvc.com/portfolio — Webflow CMS cards; name from description↔domain or clean logo filename; website from Visit Site."""
import os, re, sys, requests
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://www.firebrandvc.com/portfolio"
PRIMARY = "Firebrand Ventures"
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())

def name_from(texts, url):
    keys = set()
    if url:
        host = urlparse(url).netloc.lower().replace("www.", "")
        host = re.sub(r"^(app|en|get|try|go|www\d?)\.", "", host)
        keys.add(norm(host.split(".")[0]))
    keys = {k for k in keys if len(k) >= 2}
    for t in texts:
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9.&+'’-]*", t or "")
        for i in range(len(toks)):
            for j in range(i + 1, min(i + 5, len(toks)) + 1):
                ph = " ".join(toks[i:j])
                ph = re.sub(r"(['’]s|[.'’-])+$", "", ph)
                if norm(ph) in keys and len(ph) > 1:
                    return ph
    if url:
        return urlparse(url).netloc.lower().replace("www.", "").split(".")[0].capitalize()
    return None

def logo_name(src):
    if not src: return None
    f = unquote(src.rsplit("/", 1)[-1].split("?")[0])
    if re.match(r"^[0-9a-f]{8,}", f) or "mv2" in f.lower(): return None
    f = re.sub(r"^[0-9a-f]{20,}_", "", f)
    f = re.sub(r"\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    f = re.sub(r"\s*\(.*?\)", "", f)
    f = re.sub(r"(?i)[\s_-]*(logo|logotipo|full|dark|white|black|color|colour|horizontal|copy|square|cropped)\b.*$", "", f)
    f = clean(f.replace("_", " ").replace("-", " "))
    if not f or len(f) < 2 or len(f) > 45: return None
    if re.search(r"(?i)mv2|cropped|copy$", f): return None
    return f

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT); r.raise_for_status()
    s = BeautifulSoup(r.text, "html.parser")
    out = []; seen = set()
    for it in s.select(".portfolio-collection-item.w-dyn-item, .w-dyn-item"):
        desc_el = it.select_one("p.collection-text, .collection-text")
        desc = clean(desc_el.get_text(" ")) if desc_el else ""
        a = it.select_one("a.text-link[href], a[href^=\"http\"]")
        url = a["href"].strip() if a and a.get("href", "").startswith("http") and not is_social(a["href"]) else None
        img = it.select_one("img.partner-logo, img")
        name = name_from([desc], url) or logo_name(img.get("src") if img else None)
        if not name or re.search(r"(?i)mv2|unannounced|^logo", name): continue
        if name.lower() in seen: continue
        seen.add(name.lower())
        out.append(rec(name, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "firebrand", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
