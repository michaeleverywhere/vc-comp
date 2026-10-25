#!/usr/bin/env python3
"""Sozo Ventures portfolio scraper -> sozo_companies.json
Source: https://www.sozoventures.com/portfolio — Sozo Ventures (Palo Alto / Tokyo), growth-stage venture firm
that helps US technology companies expand into Japan and Asia. The WordPress portfolio grid shows one tile per company:
a logo linking to the company website and a sector heading (public companies show only their ticker). Tiles carry no
name text, so the company name is the site-authored logo file name, kept only when it spells the company's website
domain (or the domain minus a common prefix/suffix such as get-/lets-/-ai); other tiles are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.sozoventures.com/portfolio"
PRIMARY = "Sozo Ventures"
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

def file_label(src):
    f = unquote((src or "").rsplit("/", 1)[-1])
    f = re.sub(r"(-\d+x\d+)?(-scaled)?\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    f = re.sub(r"^[0-9a-f]{20,}[_-]", "", f)
    f = re.sub(r"^\d+px[_-]", "", f)
    f = re.sub(r"(?i)^new[_-]", "", f)
    f = re.sub(r"(?i)[\s_-]*(logo|white|black|color|transparent|scaled)\b.*$", "", f)
    f = re.sub(r"[_-]\d+$", "", f)
    return clean(f.replace("_", " ").replace("-", " "))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select("div.portfolio-item"):
        a = it.select_one("a.o-decor-link[href]")
        img = it.select_one("img")
        if not a or not img:
            continue
        site = a["href"].strip()
        if not site.startswith("http") or is_social(site) or "sozoventures" in site:
            continue
        f = file_label(img.get("data-src") or img.get("src"))
        n = norm(f)
        keys = keys_affix(site)
        lab = norm(re.sub(r"^(www\d?)\.", "", urlparse(site).netloc.lower()).split(".")[0])
        if not n or not (n in keys or (len(n) >= 4 and (lab.startswith(n) or lab.endswith(n)))):
            continue
        name = " ".join(w[:1].upper() + w[1:] for w in f.split()) if f == f.lower() else f
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        h = it.select_one("h6.title")
        sector = clean(h.get_text(" ")) if h else None
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at,
                       sozo_sector=sector if sector and not re.match(r"^[A-Z]+:[A-Z]+$", sector) else None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Sozo Ventures companies")
    finish(out, "sozo", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
