#!/usr/bin/env python3
"""LDV Capital portfolio scraper -> ldv_companies.json
Source: https://www.ldv.co/capital — Squarespace text blocks, one per company: name +
website (h2 link), then labelled lines: Overview, Location, Founded, First partnered
("2019, Led Seed round" -> first invested year + funding round + whether LDV led),
Co-investors across financings, and exit lines (Acquired: 2025, <acquirer> / IPO)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.ldv.co/capital"
PRIMARY = "LDV Capital"


def fields(p):
    """{label: text} from a <p> of <strong>Label:</strong> value<br> lines."""
    for br in p.find_all("br"):
        br.replace_with("\n")
    out = {}
    for line in p.get_text("").split("\n"):
        m = re.match(r"\s*([A-Z][A-Za-z \-/&]{2,40}?)\s*:\s*(.*)$", line)
        if m:
            out[m.group(1).strip().lower()] = clean(m.group(2))
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    out = []
    for block in s.select(".sqs-html-content"):
        h = block.find("h2")
        p = h.find_next_sibling("p") if h else None
        if not h or not p or "Overview" not in p.get_text():
            continue
        name = clean(h.get_text(" ", strip=True))
        a = h.find("a", href=True)
        href = a["href"].strip() if a else ""
        f = fields(p)
        fp = f.get("first partnered") or ""
        y = re.search(r"\b((?:19|20)\d{2})\b", fp)
        rnd = re.search(r"(Pre-?Seed|Seed|Series\s+[A-Z]\d?)", fp, re.I)
        acq = f.get("acquired")
        ipo = next((v for k, v in f.items() if "ipo" in k or k in ("public", "spac")), None)
        status = "acquired" if acq else ("public" if ipo else ("closed" if f.get("closed") or f.get("shut down") else "active"))
        ay = re.search(r"\b((?:19|20)\d{2})\b", acq or "")
        acquirer = clean(re.sub(r"^\s*(?:19|20)\d{2}\s*,\s*", "", acq).split(" – ")[0].split(" - ")[0]) if acq else None
        fy = re.search(r"\b((?:19|20)\d{2})\b", f.get("founded") or "")
        co = [clean(x) for x in re.split(r"[;,]\s*", f.get("co-investors across financings") or "") if clean(x)]
        out.append(rec(name, f.get("overview"), href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, location=f.get("location"),
                       founded_year=int(fy.group(1)) if fy else None,
                       first_invested=int(y.group(1)) if y else None,
                       stage=(rnd.group(1).title().replace("Preseed", "Pre-Seed") if rnd else None),
                       ldv_led=bool(re.search(r"\bled\b", fp, re.I)) if fp else None,
                       first_partnered=fp or None, co_investors=co,
                       acquirer=acquirer, exit_year=int(ay.group(1)) if ay else None, exit_note=acq or ipo,
                       status=status))
    finish(out, "ldv", ("description", "company_url", "location", "first_invested", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
