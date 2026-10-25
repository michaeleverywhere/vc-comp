#!/usr/bin/env python3
"""Overton Venture Capital portfolio scraper -> overtonvc_companies.json
Source: https://www.overtonvc.com/portfolio — Overton Venture Capital (Philadelphia), early-stage venture firm
backing consumer, retail-tech and SaaS founders. The Squarespace portfolio page shows one row per company: a logo, a
description and a "Learn more" link to the company website. Rows carry no name field, so the company name is the
phrase in the description that spells the website domain, else the leading words of the site-authored logo file name
when they spell the domain, else the description's opening subject when its first word is part of the domain; other
rows are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.overtonvc.com/portfolio"
PRIMARY = "Overton Venture Capital"
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
VERB = (r"is|are|was|has|have|makes|helps|offers|builds|provides|enables|allows|lets|uses|harnesses|transforms|"
        r"creates|connects|develops|delivers|empowers|combines|brings|turns|gives|supports|partners|powers|designs")

def lead_name(desc, keys):
    m = re.match(r"^([A-Z0-9][^.,;:!?]{0,40}?)(?:['\u2019]s)?\s+(?:%s)\b" % VERB, desc or "")
    if not m:
        return None
    n = m.group(1).strip()
    words = n.split()
    if keys:
        return n if any(norm(words[0]) and norm(words[0]) in k for k in keys) else None
    return n if len(words) <= 4 and all(w[:1].isupper() or w in ("+", "&", "and", "of", "the") or w[:1].isdigit() for w in words) else None


def file_prefix(src, keys):
    f = unquote((src or "").split("?")[0].rsplit("/", 1)[-1]).replace("+", " ")
    f = re.sub(r"\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    toks = [t for t in re.split(r"[\s_-]+", f) if t]
    for j in range(min(len(toks), 5), 0, -1):
        ph = " ".join(toks[:j])
        if norm(ph) in keys:
            return ph
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for row in soup.select("div.row.sqs-row"):
        if row.select("div.row.sqs-row"):
            continue
        a = next((x for x in row.select('a[href^="http"]') if "learn more" in x.get_text(" ").lower()), None)
        img = row.select_one("img")
        if not a or not img:
            continue
        site = a["href"].strip()
        if is_social(site) or "overtonvc" in site:
            continue
        keys = keys_affix(site)
        desc = clean(" ".join(p.get_text(" ") for p in row.select("div.sqs-html-content p"))) or None
        if desc:
            desc = clean(re.sub(r"\s*Learn more\s*$", "", desc)) or None
        sentences = re.split(r"(?<=[.!?])\s+", desc or "")
        name = (name_from([desc], keys) or file_prefix(img.get("data-src") or img.get("src"), keys)
                or next((n for n in (lead_name(s_, keys) for s_ in sentences) if n), None))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 12:
        raise SystemExit(f"FATAL: only {len(out)} Overton Venture Capital companies")
    finish(out, "overtonvc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
