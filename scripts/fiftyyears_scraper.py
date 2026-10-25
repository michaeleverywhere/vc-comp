#!/usr/bin/env python3
"""Fifty Years portfolio scraper -> fiftyyears_companies.json
Source: https://www.fiftyyears.com/companies — Fifty Years (San Francisco), seed fund backing founders who use
science and engineering (synthetic biology, climate, health, AI) to solve big problems. The Squarespace page embeds the
portfolio as a user-items list (JSON in data-current-context): each item has a one-line description (prefixed
"ACQUIRED /" for exits), a logo image and a button linking to the company website. Item titles are template
placeholders, so the company name is taken from the site-authored logo file name, kept only when it spells the
company's website domain; items that don't match (and stealth placeholders) are skipped."""
import os, sys, re, json
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.fiftyyears.com/companies"
PRIMARY = "Fifty Years"
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


def keys_full(url):
    k = name_keys(url)
    host = urlparse(url).netloc.lower().split(":")[0]
    host = re.sub(r"^(www\d?|app|en|get|try|go)\.", "", host)
    k.add(norm(host))
    return k


def file_name(filename, keys):
    f = unquote(filename or "")
    f = re.sub(r"\.(png|jpe?g|svg|webp|avif|gif)$", "", f, flags=re.I)
    toks = [t for t in re.split(r"[\s_+]+", f.replace("-", " ")) if t]
    for j in range(min(len(toks), 5), 0, -1):
        ph = " ".join(toks[:j])
        if norm(ph) in keys:
            return ph
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for ul in soup.select("ul[data-current-context]"):
        for it in json.loads(ul["data-current-context"]).get("userItems", []):
            site = ((it.get("button") or {}).get("buttonLink") or "").strip()
            if not site.startswith("http") or is_social(site) or "fiftyyears" in site:
                continue
            keys = keys_full(site)
            img = it.get("image") or {}
            name = file_name(img.get("filename"), keys) or file_name((img.get("assetUrl") or "").rsplit("/", 1)[-1], keys)
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            desc = clean(BeautifulSoup(it.get("description") or "", "html.parser").get_text(" ")) or None
            status = "Active"
            if desc and re.match(r"(?i)^acquired\s*/", desc):
                status = "Exited"
                desc = clean(re.sub(r"(?i)^acquired\s*/\s*", "", desc)) or None
            out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, status=status))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Fifty Years companies")
    finish(out, "fiftyyears", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
