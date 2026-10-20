#!/usr/bin/env python3
"""Neu Venture Capital portfolio scraper -> neuventurecapital_companies.json
Source: https://neuvc.com/ — the investments file behind Neu's console-style site
(https://neuvc.com/investments.js, what its "companies" / "info" / "exits" commands print): company
name, description, website, each Neu round (series + month/year; earliest = first invested) and exit
events (acquired / merged / IPO, with date)."""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, round_label
from _d50_common import rec, finish

SOURCE_URL = "https://neuvc.com/"
DATA_URL = "https://neuvc.com/investments.js"
PRIMARY = "Neu Venture Capital"
EXIT_RX = re.compile(r"acquired|merged|ipo|went public|sold", re.I)


def _ym(d):
    m = re.match(r"(\d{1,2})/(\d{4})$", (d or "").strip())
    return (int(m.group(2)), int(m.group(1))) if m else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = json.loads(fetch(DATA_URL))["investments"]
    out = []
    for co in data:
        name = clean(co.get("company"))
        if not name:
            continue
        rounds = [{"series": clean(r.get("series")), "date": clean(r.get("date"))} for r in co.get("rounds") or []]
        dated = sorted((_ym(r["date"]), r) for r in rounds if _ym(r["date"]))
        first = dated[0] if dated else None
        events = [{"event": clean(e.get("event")), "date": clean(e.get("date"))} for e in co.get("events") or []]
        exited = any(EXIT_RX.search(e["event"] or "") for e in events)
        url = co.get("url")
        if url and is_social(url):
            url = None
        desc = clean(re.sub(r"\s+", " ", co.get("desc") or "")) or None
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at,
                       neu_rounds=rounds,
                       stage=round_label("Series " + first[1]["series"]) if first and first[1]["series"] else None,
                       first_invested=str(first[0][0]) if first else None,
                       exit_events=events,
                       status="acquired" if exited else ("active" if not events else None),
                       status_label="; ".join(e["event"] for e in events if e["event"]) or None))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Neu companies")
    finish(out, "neuventurecapital", ("description", "company_url", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
