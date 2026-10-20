#!/usr/bin/env python3
"""Rhombuz VC portfolio scraper -> rhombuzvc_companies.json
Source: https://rhombuz.vc/portfolio — the portfolio page's own company records (shipped in the
site's React bundle; the same records the cards and their pop-ups render): company name, Rhombuz's
one-line description, Rhombuz category code, sector, HQ city, year, status (active / exited) plus
the card badges (Soonicorn / Exited) and the company website."""
import os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://rhombuz.vc/portfolio"
ORIGIN = "https://rhombuz.vc"
PRIMARY = "Rhombuz VC"
STR = r'"((?:[^"\\]|\\.)*)"'


def _arrays(t):
    for m in re.finditer(r'=\[\{name:"', t):
        i, d, j, instr, esc = m.start() + 1, 0, m.start() + 1, False, False
        while j < len(t):
            ch = t[j]
            if instr:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    instr = False
            elif ch == '"':
                instr = True
            elif ch in "[{":
                d += 1
            elif ch in "]}":
                d -= 1
                if d == 0:
                    break
            j += 1
        yield t[i:j + 1]


def _objects(a):
    out, d, start, instr, esc = [], 0, None, False, False
    for j, ch in enumerate(a):
        if instr:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                instr = False
        elif ch == '"':
            instr = True
        elif ch == "{":
            d += 1
            if d == 1:
                start = j
        elif ch == "}":
            d -= 1
            if d == 0 and start is not None:
                out.append(a[start:j + 1])
    return out


def _unesc(s):
    return s.encode().decode("unicode_escape").encode("latin-1", "ignore").decode("utf-8", "ignore") if "\\" in s else s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    home = fetch(SOURCE_URL)
    js = re.search(r'src="(/assets/index-[^"]+\.js)"', home)
    if not js:
        raise SystemExit("FATAL: Rhombuz bundle not found")
    t = fetch(ORIGIN + js.group(1))
    out = []
    for a in _arrays(t):
        if "hq:" not in a:
            continue
        for o in _objects(a):
            f = {k: _unesc(v) for k, v in re.findall(r'(\w+):' + STR, o)}
            badges = re.search(r'badgeStatuses:\[(.*?)\]', o)
            badges = re.findall(STR, badges.group(1)) if badges else []
            name = clean(f.get("name"))
            if not name:
                continue
            url = f.get("url")
            if url and is_social(url):
                url = None
            out.append(rec(name, f.get("oneLiner"), url, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=[f["sector"]] if f.get("sector") else None, location=f.get("hq"),
                           year=f.get("year"), rhombuz_category=f.get("category"),
                           status=(f.get("status") or "").lower() or None, badges=badges))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Rhombuz companies")
    finish(out, "rhombuzvc", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
