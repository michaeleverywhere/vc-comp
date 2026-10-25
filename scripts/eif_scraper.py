#!/usr/bin/env python3
"""Ecosystem Integrity Fund portfolio scraper -> eif_companies.json
Source: https://www.eif.vc/portfolio — The Ecosystem Integrity Fund (EIF, San Francisco), venture firm investing
in early- and growth-stage sustainability, climate and clean-energy companies. Each portfolio logo opens a dialog
with the logo, the company website link, bullet-point description and (for exits) a note such as "Sold to PepsiCo
(PEP) December 2016". Dialogs carry no name field, so the company name is the phrase in the bullets that spells the
website domain, else the leading words of the site-authored logo title when they spell the domain or appear verbatim
in the bullets; other dialogs are skipped."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.eif.vc/portfolio"
PRIMARY = "Ecosystem Integrity Fund"
EXIT = re.compile(r"(?i)^(sold to|acquired by|merged with|management buyout|ipo|went public|public via|listed on)\b")
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

def title_prefixes(t):
    t = unquote(t or "")
    t = re.sub(r"\.(png|jpe?g|svg|webp|gif)$", "", t, flags=re.I)
    t = re.sub(r"(?i)[\s_-]*(logo|horizontal|color|colour|black|white|rgb|final|vector|new)\b.*$", "", t)
    toks = [x for x in re.split(r"[\s_-]+", t) if x]
    return [" ".join(toks[:j]) for j in range(min(len(toks), 5), 0, -1)]


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for row in soup.select("div.et_pb_row"):
        if row.select("div.et_pb_row"):
            continue
        img = row.select_one("img")
        txt = row.select_one("div.et_pb_text_inner")
        if not img or not txt:
            continue
        a = txt.select_one('a[href^="http"]')
        site = a["href"].strip() if a else None
        if site and (is_social(site) or "eif.vc" in site):
            site = None
        lines = [clean(x.get_text(" ")) for x in txt.select("li, p") if clean(x.get_text(" "))]
        lines = [l for l in lines if not re.match(r"^(https?://|www\.)", l)]
        note = next((l for l in lines if EXIT.match(l)), None)
        bullets = [l for l in lines if l != note]
        if not bullets:
            continue
        keys = keys_affix(site) if site else set()
        name = name_from(bullets, keys) if keys else None
        if name and (re.search(r"(?i)\.(com|io|co|ai|net|org|in|no)$", name) or len(norm(name)) < 3):
            name = None
        if not name:
            for ph in title_prefixes(img.get("title") or img.get("src", "").rsplit("/", 1)[-1]):
                if len(norm(ph)) >= 3 and ((keys and norm(ph) in keys) or name_from(bullets, {norm(ph)})):
                    name = ph
                    break
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append(rec(name, " ".join(bullets)[:1500], site, PRIMARY, SOURCE_URL, scraped_at,
                       status="Exited" if note else "Active", exit_note=note))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Ecosystem Integrity Fund companies")
    finish(out, "eif", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
