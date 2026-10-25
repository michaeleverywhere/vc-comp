#!/usr/bin/env python3
"""Kaiser Permanente Ventures portfolio scraper -> kpventures_companies.json
Source: https://www.kpventures.com/portfolio/ — Kaiser Permanente Ventures, the corporate venture arm of Kaiser
Permanente investing in digital health, care delivery and medical technology (Abridge, Big Health...). The WordPress
portfolio page carries, per company, a popup with the site's description and website. Cards show logos rather than
name text, so the company name is the phrase in the site's own description that spells the company's website domain
(else the site-authored logo file name when it spells the domain; otherwise skipped)."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.kpventures.com/portfolio/"
PRIMARY = "Kaiser Permanente Ventures"
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


VERB = (r"is|are|has|have|provides|develops|developed|delivers|enables|partners|combines|converts|manufactures|"
        r"helps|proactively|offers|builds|was|uses|leverages|makes|operates|creates|designs")


def lead_name(desc, src):
    """Every popup opens '<Company> is/has/provides ...'; take that subject when the logo file name corroborates it."""
    m = re.match(r"^([A-Z0-9][^.,;:]{0,50}?)(?:['’]s)?\s+(?:%s)\b" % VERB, desc or "")
    if not m or not src or len(m.group(1).split()) > 5:
        return None
    first = norm(m.group(1).split()[0])
    return m.group(1).strip() if len(first) >= 2 and first in norm(unquote(src.rsplit("/", 1)[-1])) else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for c in soup.select("div.popup-description"):
        d = c.select_one("div.description")
        ps = [clean(p.get_text(" ")) for p in d.find_all("p")] if d else []
        desc = clean(" ".join(p for p in ps if p)) or None
        a = c.select_one("div.site-btn a[href]")
        site = a["href"].strip() if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        img = c.select_one("div.logo img")
        src = (img.get("data-lazy-src") or img.get("src")) if img else None
        keys = name_keys(site)
        name = name_from([desc], keys) or logo_name(src, keys) or lead_name(desc, src)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Kaiser Permanente Ventures companies")
    finish(out, "kpventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
