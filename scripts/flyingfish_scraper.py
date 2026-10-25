#!/usr/bin/env python3
"""Flying Fish Partners portfolio scraper -> flyingfish_companies.json
Source: https://www.flyingfish.vc/portfolio — Flying Fish Partners (Seattle), seed-stage venture firm focused on
AI and machine-learning startups. The Webflow portfolio feed shows one card per company linking to its website,
with category, logo, a one-line description and the investment year. Cards carry no name text, so the company name is
the phrase in the description that spells the website domain, else the site-authored logo file name when it spells
the domain (or the domain minus a common prefix/suffix such as get-/-ai); other cards are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.flyingfish.vc/portfolio"
PRIMARY = "Flying Fish Partners"
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



AFFIX_PRE = ("my", "run", "get", "try", "use", "join", "go", "hello", "the", "meet", "with", "hey")
AFFIX_SUF = ("hq", "app", "ai", "labs", "lab", "inc", "co", "io", "bio", "health", "tech", "hub", "official")


def keys_affix(url):
    """Domain label variants: the full host, the label, and the label with one common marketing prefix/suffix
    removed (myaidin -> aidin, runalloy -> alloy)."""
    k = set(name_keys(url))
    if not url:
        return k
    host = urlparse(url if "//" in url else "http://" + url).netloc.lower().split(":")[0]
    host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
    k.add(norm(host))
    lab = norm(host.split(".")[0])
    for p in AFFIX_PRE:
        if lab.startswith(p) and len(lab) - len(p) >= 3:
            k.add(lab[len(p):])
    for s_ in AFFIX_SUF:
        if lab.endswith(s_) and len(lab) - len(s_) >= 3:
            k.add(lab[: -len(s_)])
    return k

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.home_layout-2_card[href]"):
        site = a["href"].strip()
        if not site.startswith("http") or is_social(site) or "flyingfish" in site:
            continue
        keys = keys_affix(site)
        p = a.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        img = a.select_one("img")
        name = name_from([desc], keys) or logo_name(img.get("src") if img else None, keys)
        if not name:
            continue
        if name == name.lower():
            name = " ".join(w[:1].upper() + w[1:] for w in name.split())
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        cat = a.select_one('[fs-cmsfilter-field="categories"]')
        yr = a.select_one("div.text-color-alternate")
        y = clean(yr.get_text(" ")) if yr else None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       flyingfish_category=clean(cat.get_text(" ")) if cat else None,
                       investment_year=y if y and re.fullmatch(r"(19|20)\d\d", y) else None))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Flying Fish Partners companies")
    finish(out, "flyingfish", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
