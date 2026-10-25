#!/usr/bin/env python3
"""HAVAIC portfolio scraper -> havaic_companies.json
Source: https://www.havaic.com/track-record — HAVAÍC (Cape Town), South African early-stage venture capital firm
investing in high-growth African technology businesses. The Wix "Investments" page shows one tile per company: a logo
linking to the company website, the investment date (e.g. "JUL '16") and a sector. Tiles carry no name text, so the
company name is the leading words of the site-authored logo file name (the image alt), kept only when they spell the
company's website domain (or the domain minus a common prefix/suffix); other tiles are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup, NavigableString

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.havaic.com/track-record"
PRIMARY = "HAVAIC"
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

def file_prefix(f, keys, lab=""):
    f = unquote(f or "")
    f = re.sub(r"\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    toks = [t for t in re.split(r"[\s_-]+", f) if t]
    for j in range(min(len(toks), 5), 0, -1):
        ph = " ".join(toks[:j])
        n = norm(ph)
        if n in keys or (len(n) >= 4 and lab.startswith(n)):
            return ph
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for t in soup(["script", "style", "svg"]):
        t.decompose()
    seq = []
    for el in soup.body.descendants:
        if getattr(el, "name", None) == "img":
            seq.append(("IMG", el.get("alt") or ""))
        elif getattr(el, "name", None) == "a" and el.get("href", "").startswith("http"):
            seq.append(("A", el["href"].strip()))
        elif isinstance(el, NavigableString) and el.strip() and el.parent.name != "a":
            seq.append(("T", clean(str(el))))
    cards, cur = [], None
    for kind, v in seq:
        if kind == "A":
            cur = {"site": v, "img": None, "date": None, "sector": None, "_k": None}
            cards.append(cur)
        elif cur is None:
            continue
        elif kind == "IMG" and cur["img"] is None:
            cur["img"] = v
        elif kind == "T":
            if v.upper().startswith("INVESTMENT DATE"):
                cur["_k"] = "date"
            elif v.lower().startswith("sector"):
                cur["_k"] = "sector"
            elif cur["_k"] and v not in ("$", "/$"):
                cur[cur["_k"]] = v.replace("\u2018", "'").replace("\u2019", "'")
                cur["_k"] = None
    out, seen = [], set()
    for c in cards:
        site = c["site"]
        if not c["img"] or not (c["date"] or c["sector"]) or is_social(site) or "havaic" in site or "wix" in site:
            continue
        keys = keys_affix(site)
        lab = norm(re.sub(r"^www\d?\.", "", urlparse(site).netloc.lower()).split(".")[0])
        name = file_prefix(c["img"], keys, lab)
        if not name:
            continue
        if name == name.lower():
            name = " ".join(w[:1].upper() + w[1:] for w in name.split())
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at,
                       investment_date=c["date"], havaic_sector=c["sector"]))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} HAVAIC companies")
    finish(out, "havaic", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
