#!/usr/bin/env python3
"""645 Ventures portfolio scraper -> 645ventures_companies.json
Source: https://www.645ventures.com/portfolio — a Next.js page whose portfolio records
(exported from the firm's Airtable, ids "rec…") are compiled into one of the page's own
JS chunks. The scraper loads the page, walks its <script src> chunks, and decodes every
{"id":"rec…"} record: name, one-liner + company overview, website, investment year
(first invested), stage at entry (funding round), status (Active / Acquired / IPO /
Liquidated / exited position), industry, founders and an exit summary. Stealth records are skipped."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.645ventures.com/portfolio"
PRIMARY = "645 Ventures"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "health tech": ["Health"], "healthtech": ["Health"],
              "cybersecurity": ["Cybersecurity"], "deep tech": ["Deeptech / Robotics / AR/VR"],
              "ai infrastructure": ["Dev Tools / Cloud"], "consumer": ["Consumer"]}
STATUS = {"active": "active", "acquired": "acquired", "ipo": "public", "closed": "closed", "exited": "exited",
          "liquidated": "closed", "645 exited position": "exited", "secondary sale": "exited"}


def records(js):
    js = js.replace("\\'", "'")
    dec, out = json.JSONDecoder(), []
    for m in re.finditer(r'\{"id":"rec[A-Za-z0-9]+"', js):
        try:
            obj, _ = dec.raw_decode(js, m.start())
        except ValueError:
            continue
        if isinstance(obj, dict) and "name" in obj and ("one_liner" in obj or "company_overview" in obj):
            out.append(obj)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    rows = []
    for src in dict.fromkeys(re.findall(r'<script[^>]+src="([^"]+\.js[^"]*)"', html)):
        js = fetch(urljoin(SOURCE_URL, src))
        if '"one_liner"' in js:
            rows += records(js)
    out = []
    for r in rows:
        if r.get("stealth"):
            continue
        name = clean(r.get("name"))
        if not name:
            continue
        w = clean(r.get("website"))
        st = clean(r.get("status"))
        yr = re.match(r"((?:19|20)\d{2})", clean(r.get("investment_date")) or "")
        ind = [clean(x) for x in (r.get("web_industry") or []) if clean(x)]
        out.append(rec(name, clean(r.get("company_overview")) or clean(r.get("one_liner")),
                       w if w and w.startswith("http") and not is_social(w) else None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=ind, sector_map=SECTOR_MAP, tagline=r.get("one_liner"),
                       stage=clean(r.get("stage")), first_invested=int(yr.group(1)) if yr else None,
                       portfolio_status=st, status=STATUS.get((st or "").lower(), (st or "").lower() or None),
                       founders=[clean(f.get("name")) for f in (r.get("founders_data") or []) if clean(f.get("name"))],
                       exit_summary=clean(r.get("exit_summary")),
                       detail_url=f"https://www.645ventures.com/portfolio/{r['slug']}" if r.get("slug") else None))
    finish(out, "645ventures", ("description", "company_url", "stage", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
