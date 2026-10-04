#!/usr/bin/env python3
"""RTP Global portfolio scraper -> rtpglobal_companies.json
Source: https://rtp.vc/our-companies/ — WordPress company cards (div.customer).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://rtp.vc/our-companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "rtpglobal_companies.json")
PRIMARY = "RTP Global"

STAGE_RE = re.compile(
    r"(?i)\b(Pre-?Seed|Seed|Series\s+[A-G]|Growth|IPO)\b"
)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for it in soup.select("div.customer"):
        # name from img alt (often "All3 RTP Global" or brand)
        name = None
        for img in it.select("img[alt]"):
            alt = clean(img.get("alt"))
            if not alt:
                continue
            alt = re.sub(r"\s*RTP Global\s*$", "", alt, flags=re.I).strip()
            if alt and len(alt) < 60:
                name = alt
                break
        raw = clean(it.get_text(" ", strip=True)) or ""
        # Parse structured fields from text blob
        desc = None
        # description is usually the leading sentence before "Year of Investment"
        m = re.match(r"^(.*?)\s*Year of Investment\s*", raw)
        if m:
            desc = clean(m.group(1))
        year = None
        m = re.search(r"Year of Investment\s*(\d{4})", raw)
        if m:
            year = m.group(1)
        sector = None
        m = re.search(r"Sector\s*(.+?)(?:\s*Customer\b|\s*Country\b|\s*Stage\b|$)", raw)
        if m:
            sector = clean(m.group(1))
        country = None
        m = re.search(r"Country\s*(.+?)(?:\s*Stage\b|\s*Status\b|$)", raw)
        if m:
            country = clean(m.group(1))
        stage = None
        m = re.search(r"Stage\s*(?:RTP Invested\s*)?(.+?)(?:\s*Status\b|$)", raw)
        if m:
            st = clean(m.group(1))
            mm = STAGE_RE.search(st or "")
            if mm:
                stage = mm.group(1).title().replace("Pre-Seed", "Pre-Seed").replace("Pre Seed", "Pre-Seed")
                stage = re.sub(r"(?i)series\s+([a-g])", lambda x: f"Series {x.group(1).upper()}", stage)
                if stage.lower() == "seed":
                    stage = "Seed"
                elif stage.lower().startswith("pre"):
                    stage = "Pre-Seed"
        status = "active"
        m = re.search(r"Status\s*(.+?)$", raw)
        if m:
            st = m.group(1).lower()
            if "acquir" in st or "exit" in st:
                status = "acquired"

        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["rtp.vc", "linkedin", "twitter", "facebook", "instagram"]):
                continue
            website = clean(href)
            break

        if not name:
            # fallback: use domain from website
            if website:
                host = re.sub(r"^https?://(www\.)?", "", website).split("/")[0]
                name = host.split(".")[0].title()
            else:
                continue
        if name.lower() in seen:
            continue
        seen.add(name.lower())

        # Don't use year as stage; keep as invested_date
        sectors = [s.strip() for s in sector.split(",")] if sector else None
        # Filter sector list noise
        if sectors:
            sectors = [s for s in sectors if s and len(s) < 60][:5] or None

        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": stage,
            "location": country,
            "sectors": sectors,
            "invested_date": year,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  stage: {sum(1 for r in out if r.get('stage'))}/{n}")
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
