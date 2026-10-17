#!/usr/bin/env python3
"""Pathbreaker Ventures portfolio scraper -> pathbreaker_companies.json
Source: https://www.pathbreakervc.com/companies — Squarespace companies page:
each company block opens with the company name in bold (linked to its website) followed by the
site's one-line description; co-investor lines kept; acquisition banners give exits."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.pathbreakervc.com/companies"
PRIMARY = "Pathbreaker Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for blk in s.select(".sqs-html-content"):
        ps = blk.select("p")
        for i, p in enumerate(ps):
            first = next((c for c in p.children if getattr(c, "name", None) or str(c).strip()), None)
            if getattr(first, "name", None) == "a" and first.find("strong"):
                nm, url = txt(first), site(first)
            elif getattr(first, "name", None) == "strong":
                nm, url = txt(first), None
            else:
                continue
            rest = clean((txt(p) or "")[len(nm or ""):])
            if not nm or not rest or not rest[0].islower() or len(nm) > 60:
                continue
            rest = re.sub(r"\s*More (here|on (team|product))\.?", "", rest).strip()
            co = next((txt(q) for q in ps[i + 1:] if re.match(r"co-?investors?:", txt(q) or "", re.I)), None)
            out.append(rec(nm, f"{nm} {rest}", url, PRIMARY, SOURCE_URL, scraped_at,
                           co_investors=re.sub(r"^co-?investors?:\s*", "", co, flags=re.I) if co else None))
            break
    # acquisition banners: "NAME (AI) - ACQ BY X"
    seen = {r["company_name"].lower() for r in out}
    for a in s.select("a.sqs-block-button-element"):
        t = txt(a) or ""
        m = re.match(r"^(.+?)\s*(\([^)]*\))?\s*-\s*acq(?:uired)? by\s+(.+)$", t, re.I)
        if not m:
            continue
        nm = m.group(1).strip()
        nm = nm.title() if nm.isupper() else nm
        note = "Acquired by " + m.group(3).strip()
        hit = next((r for r in out if r["company_name"].lower() == nm.lower()), None)
        if hit:
            hit["status"], hit["exit_note"] = "exited", note
        elif nm.lower() not in seen:
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, status="exited", exit_note=note))
    finish(out, "pathbreaker", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
