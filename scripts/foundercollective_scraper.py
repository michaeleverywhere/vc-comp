#!/usr/bin/env python3
"""Founder Collective portfolio scraper -> foundercollective_companies.json
Source: https://foundercollective.com/portfolio/ — WordPress, one server-rendered
table (no pagination). Each row carries a one-line description, Year Invested,
Founders, Location (region filter label), Categories, a website link and, for
exits, an "acquired: <buyer>" note in the row's data-content search string.
The visible name is a logo image only, so the name is read from data-content
(lower-cased by the site) and its casing recovered from the description text.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://foundercollective.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "foundercollective_companies.json")
PRIMARY = "Founder Collective"
REGION = {"nyc": "New York, NY", "bay-area": "San Francisco Bay Area", "boston-ma": "Boston, MA",
          "la": "Los Angeles, CA", "israel": "Israel"}
SECTOR_TAG_MAP = {
    "healthcare": ["Health"], "finance": ["FinTech / Insurance"], "consumer": ["Consumer"],
    "ecommerce": ["Consumer"], "hardware": ["Deeptech / Robotics / AR/VR"],
}


def _alnum(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def recover_name(lower_name, desc):
    """Site lower-cases names in data-content; recover display casing from the
    description (e.g. 'appyai' -> 'Appy.AI'). Falls back to title case."""
    target = _alnum(lower_name)
    toks = re.findall(r"[\w.&'’\-]+", desc or "")
    for n in (3, 2, 1):
        for i in range(len(toks) - n + 1):
            cand = " ".join(toks[i:i + n]).strip(".,'’")
            if _alnum(cand) == target:
                return cand
    return " ".join(w[:1].upper() + w[1:] for w in lower_name.split())


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".companiestable__item"):
        cls = (it.get("class") or [])[2:]
        toks = (it.get("data-content") or "").split()
        i = 0
        while i < len(toks) and toks[i] in cls:
            i += 1
        rest = toks[i:]
        j = next((k for k, t in enumerate(rest) if re.fullmatch(r"(19|20)\d\d", t)), None)
        if not j:
            continue
        lower_name = " ".join(rest[:j])
        title = it.select_one("h6.title")
        note = title.select_one("span.categories") if title else None
        note = clean(note.get_text(" ")) if note else None
        para = title.select_one("p") if title else None
        desc = clean((para or title).get_text(" ")) if title else None
        name = recover_name(lower_name, desc)
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        fields = {}
        for ci in it.select(".cdata-item"):
            lab = ci.select_one("label")
            if not lab:
                continue
            key = clean(lab.get_text()).rstrip(":").lower()
            if key == "categories":
                fields[key] = [clean(li.get_text()) for li in ci.select("li") if clean(li.get_text())]
            elif key == "links":
                for a in ci.select("a[href]"):
                    if "icon-link" in (a.get("class") or []):
                        fields["website"] = a["href"].strip()
            else:
                v = ci.select_one(".location")
                fields[key] = clean(v.get_text(" ")) if v else None
        year = fields.get("year invested")
        m = re.match(r"(?i)(?:acquired:?|merged with)\s*(.*)", note or "")
        status = "acquired" if m else None
        acquirer = clean(m.group(1)) if m else None
        tick = re.match(r"(NYSE|NASDAQ|Nasdaq|LSE|TSX):\s*([A-Z.]+)$", note or "")
        regions = [REGION[c] for c in cls if c in REGION]
        founders = [clean(f) for f in (fields.get("founders") or "").split(",") if clean(f)]
        sectors = fields.get("categories") or []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": fields.get("website"),
            "status": status,
            "acquirer": acquirer,
            "ticker": f"{tick.group(1).upper()}: {tick.group(2)}" if tick else None,
            "site_note": note,
            "first_invested": int(year) if year and year.isdigit() else None,
            "location": regions[0] if regions else fields.get("location"),
            "region": fields.get("location"),
            "founders": founders,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
