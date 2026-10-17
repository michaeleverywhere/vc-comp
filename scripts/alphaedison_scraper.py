#!/usr/bin/env python3
"""Alpha Edison portfolio scraper -> alphaedison_companies.json
Source: https://www.alphaedison.com/portfolio — Squarespace image blocks, one per
company: website (image link), description (image caption) and the logo file name.
Company name = the caption's subject (text before its first verb, e.g. "Alloy is a
fintech company…" -> Alloy), falling back to the logo file name (Blu_Port_<Name>.png).
Sector = which of the firm's category sub-pages (/portfolio-fintech, -deep-tech,
-software-ai, -data-ai, -other) lists the company."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

ORIGIN = "https://www.alphaedison.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Alpha Edison"
CATS = {"/portfolio-fintech": "Fintech", "/portfolio-deep-tech": "Deep Tech", "/portfolio-software-ai": "Software",
        "/portfolio-data-ai": "Data & AI", "/portfolio-other": "Other"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "deep tech": ["Deeptech / Robotics / AR/VR"],
              "data & ai": ["Data & Analytics"]}
VERB = re.compile(r"\s+(?:is|are|was|offers|provides|develops|helps|builds|creates|enables|makes|delivers|uses|"
                  r"specializes|operates|has|empowers|allows|designs|connects|leverages|transforms|aims|"
                  r"focuses|combines|manufactures|produces|sells|serves|partners|brings)\b")


def figures(url):
    try:
        s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    except SystemExit:
        return []
    out = []
    for f in s.select("figure.sqs-block-image-figure"):
        a = f.select_one("a[href]")
        href = (a.get("href") or "").strip() if a else ""
        if not href.startswith("http") or "alphaedison" in href:
            continue
        img = f.select_one("img")
        fn = (img.get("data-src") or img.get("src") or "").split("/")[-1].split("?")[0] if img else ""
        cap = f.select_one("figcaption")
        out.append((href, fn, clean(cap.get_text(" ", strip=True)) if cap else None))
    return out


def key(u):
    return urlparse(u).netloc.lower().removeprefix("www.") + urlparse(u).path.rstrip("/").lower()


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cat_of = {}
    for path, label in CATS.items():
        for href, _, _ in figures(ORIGIN + path):
            cat_of.setdefault(key(href), []).append(label)
    out, seen = [], set()
    for href, fn, cap in figures(SOURCE_URL):
        token = clean(re.sub(r"^(?:Blu[_ ]Port[_ ]|blu[_ ]AE[_ ])|\.(png|jpe?g|webp|svg)$", "", fn, flags=re.I).replace("_", " ").replace("+", " "))
        name = None
        if cap:
            m = VERB.search(cap)
            if m and 0 < len(cap[:m.start()].split()) <= 5:
                name = clean(cap[:m.start()].rstrip(",").strip())
        if not name or (token and token.lower()[:3] not in name.lower()):
            name = token
        elif (len(name.split()) == 2 and len(name.split()[1]) > 3
              and name.split()[0].lower().endswith(name.split()[1].lower())):
            name = name.split()[0]  # caption typo like "AutoIVF utoIVF is …"
        k = key(href)
        if k in seen:
            continue
        seen.add(k)
        if not name:
            continue
        out.append(rec(name, cap, None if is_social(href) else href, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=cat_of.get(key(href), []), sector_map=SECTOR_MAP))
    finish(out, "alphaedison", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
