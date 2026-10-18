#!/usr/bin/env python3
"""Catalyst Investors portfolio scraper -> catalystinvestors_companies.json
Source: https://catalyst.com/portfolios/ — WordPress theme grid loaded through the
site's own admin-ajax "loadmore" action (the same call the page's Current / Exited
buttons make): company name, website (card link), one-line description,
"Invested: YYYY" (first invested) and the exit line ("Acquired by X in YYYY" ->
status acquired + acquirer + exit year). Current vs Exited comes from the category."""
import os, re, sys, json, base64, time
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://catalyst.com/portfolios/"
AJAX = "https://catalyst.com/wp-admin/admin-ajax.php"
PRIMARY = "Catalyst Investors"
H = {"User-Agent": "Mozilla/5.0 (compatible; vc-comp-scraper/1.0)"}
CATS = {6: "Current", 7: "Exited"}


def params(html):
    for b64 in re.findall(r'src="data:text/javascript;base64,([^"]+)"', html):
        js = base64.b64decode(b64).decode("utf-8", "replace")
        m = re.search(r"var ajax_params = (\{.*\});", js, re.S)
        if m:
            return json.loads(m.group(1))
    raise SystemExit("ajax_params not found")


def cards(html, cat, scraped_at):
    out = []
    for a in BeautifulSoup(html, "html.parser").select("a.thumb"):
        name = clean(a.select_one(".ititle").get_text(" ", strip=True)) if a.select_one(".ititle") else None
        if not name:
            continue
        it = a.select_one(".itext")
        lines = [clean(x) for x in (it.get_text("\n", strip=True).split("\n") if it else []) if clean(x)]
        desc, yr, exit_note, acq, exit_year = None, None, None, None, None
        for ln in lines:
            m = re.match(r"Invested:\s*(\d{4})", ln)
            if m:
                yr = int(m.group(1)); continue
            if re.match(r"(Acquired|Merged|IPO|Public|Sold|Exited|Recapitalized)", ln, re.I):
                exit_note = ln
                m2 = re.match(r"Acquired by (.+?)(?: in (\d{4}))?$", ln)
                if m2:
                    acq, exit_year = m2.group(1), int(m2.group(2)) if m2.group(2) else None
                continue
            desc = ln if not desc else desc
        href = (a.get("href") or "").strip()
        status = "active" if cat == 6 else ("acquired" if exit_note and re.match(r"(Acquired|Merged|Sold)", exit_note, re.I) else "exited")
        out.append(rec(name, desc, href if href.startswith("http") and not is_social(href) else None, PRIMARY,
                       SOURCE_URL, scraped_at, first_invested=yr, portfolio_group=CATS[cat], exit_note=exit_note,
                       acquirer=acq, exit_year=exit_year, status=status))
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = requests.Session(); s.headers.update(H)
    p = params(s.get(SOURCE_URL, timeout=30).text)
    out = []
    for cat in CATS:
        for page in range(0, 20):
            r = s.post(AJAX, data={"action": "loadmore", "query": p["posts"], "page": page, "p_type": p["post_type"],
                                   "p_count": p["post_count"], "p_cat": cat}, timeout=30)
            got = cards(r.text, cat, scraped_at) if r.ok and r.text.strip() else []
            new = [x for x in got if x["company_name"].lower() not in {y["company_name"].lower() for y in out}]
            if not new:
                break
            out += new
            time.sleep(0.3)
    finish(out, "catalystinvestors", ("description", "company_url", "first_invested", "exit_note", "everywhere_tags"))


if __name__ == "__main__":
    main()
