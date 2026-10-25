#!/usr/bin/env python3
"""Oregon Venture Fund portfolio scraper -> oregonventurefund_companies.json
Source: https://www.oregonventurefund.com/companies — Oregon Venture Fund (Portland), member-driven venture fund
investing in early-stage and growth companies across the Pacific Northwest. The Squarespace "Active Portfolio
Companies" / "Exited Companies" grids show one logo per company linking to the company website (exits link to an
acquisition article). The site names each logo file "<Company> <investment year(s)> [SOLD]", so the company name is the
part of that site-authored file name before the year/"logo"/"SOLD" markers; it is kept when it spells the website domain
or the file follows that <name> <year> convention. Exits ("SOLD") are marked Exited and their article links are not
stored as company websites."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.oregonventurefund.com/companies"
PRIMARY = "Oregon Venture Fund"
NEWS = re.compile(r"oregonlive|bizjournals|prnewswire|geekwire|oregonbusiness|newsroom|/news|press|acqui|ochin\.org|cisco\.com|cvent\.com|sprinklr|constantcontact")
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

def parse_file(src):
    f = unquote((src or "").rsplit("/", 1)[-1]).replace("+", " ")
    f = re.sub(r"(_[0-9a-f]{20,})?(_\dx)?\.(png|jpe?g|svg|webp|gif)$", "", f, flags=re.I)
    f = re.sub(r"^OVF\s+", "", f)
    sold = bool(re.search(r"\bSOLD\b", f))
    years = re.findall(r"\b(?:19|20)\d\d\b", f)
    m = re.split(r"(?i)\s*(?:\b(?:19|20)\d\d\b|\blogo\b|\bSOLD\b|\bhorizontal\b|\bscreenshot\b|\bv\d\b|\s-\s|\d{1,2}\.\d{4}).*$", f, maxsplit=1)
    name = clean(m[0].strip(" ,-_")) if m else None
    return name, years, sold


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select('a[href^="http"]'):
        href = a["href"].strip()
        img = a.find("img")
        if not img or is_social(href) or "oregonventurefund" in href or "squarespace" in href:
            continue
        name, years, sold = parse_file(img.get("data-src") or img.get("src"))
        if not name or len(name) < 2:
            continue
        news = bool(NEWS.search(href))
        site = None if news else href
        keys = keys_affix(site) if site else set()
        lab = norm(re.sub(r"^www\d?\.", "", urlparse(href).netloc.lower()).split(".")[0])
        words = name.split()
        for j in range(len(words) - 1, 0, -1):
            if site and norm(" ".join(words[:j])) in keys:
                name = " ".join(words[:j])
                break
        n = norm(name)
        spelled = bool(site) and (n in keys or (len(n) >= 4 and (lab.startswith(n) or lab.endswith(n))))
        if not (spelled or (years and len(n) >= 3)):
            continue
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at,
                       status="Exited" if sold else "Active",
                       ovf_years=", ".join(years) or None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Oregon Venture Fund companies")
    finish(out, "oregonventurefund", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
