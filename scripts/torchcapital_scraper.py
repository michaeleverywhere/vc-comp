#!/usr/bin/env python3
"""Torch Capital portfolio scraper -> torchcapital_companies.json
Source: https://www.torchcapital.vc/portfolio — Torch Capital (New York), early-stage venture firm investing in
consumer, fintech, healthcare and AI companies. The Webflow collection shows one card per company: logo, sector,
description, status (Active / Exited) and a link to the company website. Cards carry no name field, so the company name
is the phrase in the description that spells the website domain, else the leading words of the site-authored logo file
name when they spell the domain (or the domain minus a common prefix/suffix); other cards are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.torchcapital.vc/portfolio"
PRIMARY = "Torch Capital"
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

def file_prefix(src, keys):
    f = unquote((src or "").rsplit("/", 1)[-1])
    f = re.sub(r"^[0-9a-f]{20,}_", "", f)
    f = re.sub(r"\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    toks = [t for t in re.split(r"[\s_+-]+", f) if t]
    for j in range(min(len(toks), 5), 0, -1):
        ph = " ".join(toks[:j])
        if norm(ph) in keys:
            return ph
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select("div.collection-item-2"):
        a = it.select_one('a[href^="http"]')
        if not a:
            continue
        site = a["href"].strip()
        if is_social(site) or "torchcapital" in site:
            continue
        keys = keys_affix(site)
        d = it.select_one("div.text-block-4")
        desc = clean(d.get_text(" ")) if d else None
        img = it.select_one("img.image-10")
        name = name_from([desc], keys) or file_prefix(img.get("src") if img else None, keys)
        if not name:
            continue
        if name == name.lower():
            name = " ".join(w[:1].upper() + w[1:] for w in name.split())
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        sec = it.select_one("div.sector")
        st = it.select_one("div.text-block-5")
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       status=clean(st.get_text(" ")) if st else None,
                       torch_sector=clean(sec.get_text(" ")) if sec else None))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Torch Capital companies")
    finish(out, "torchcapital", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
