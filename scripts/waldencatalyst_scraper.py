#!/usr/bin/env python3
"""Walden Catalyst Ventures portfolio scraper -> waldencatalyst_companies.json
Source: https://www.waldencatalyst.com/portfolio — portfolio page; the page's own embedded portfolio data (title, logo description, categories, stage) — current and past investments."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.waldencatalyst.com/portfolio"
PRIMARY = "Walden Catalyst Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    return BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")


def norm(x):
    return re.sub(r"[^a-z0-9]", "", (x or "").lower())


def droot(u):
    d = re.sub(r"^www\.", "", re.sub(r"^https?://", "", u or "").split("/")[0].lower())
    return norm(d.split(".")[0])


def name_in_text(text, url):
    """Company name = the verbatim phrase (1-5 words) of the site's own card text whose
    letters equal the company's own website domain root (so the name is site-authored
    and confirmed by the linked domain; cards where no such phrase exists are skipped)."""
    r = droot(url)
    if len(r) < 3:
        return None
    cands = {r}
    for s in ("inc", "hq", "labs", "tech", "ai", "io", "co", "corp", "app", "get", "try", "the", "use"):
        if r.endswith(s) and len(r) - len(s) >= 3:
            cands.add(r[: -len(s)])
        if r.startswith(s) and len(r) - len(s) >= 3:
            cands.add(r[len(s):])
    tld = (re.sub(r"^https?://", "", url or "").split("/")[0].lower().rsplit(".", 1) + [""])[1]
    w = re.findall(r"[A-Za-z0-9][\w.&'’/\-]*", text or "")
    best = None
    for i in range(len(w)):
        if i and w[i - 1].lower() == "by":  # "Acquired by X" names the acquirer, not the company
            continue
        for n in range(1, 6):
            ph = re.sub(r"['’]s?$", "", " ".join(w[i:i + n])).rstrip(".,")
            if norm(ph) in cands and (best is None or len(norm(ph)) > len(norm(best))):
                best = ph
                nx = re.sub(r"['’]s?$", "", w[i + n]).rstrip(".,") if i + n < len(w) else ""
                if tld and nx.lower() == tld and len(tld) >= 2 and tld not in ("com", "net", "org"):
                    best = ph + " " + nx  # e.g. amber.bio -> "Amber Bio"
    return best


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    h = fetch_response(SOURCE_URL).content.decode("utf-8", "replace")
    d = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S).group(1))
    out = []
    for p in d["props"]["pageProps"]["initialData"]["portfolioItems"]:
        nm = clean(p.get("title"))
        desc = clean((p.get("logo") or {}).get("description"))
        sec = [c.get("title") for c in (p.get("categories") or []) if c.get("title")]
        st = clean(p.get("currentStage"))
        out.append(rec(nm, desc if desc and desc != nm else None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sec, status=st))
    finish(out, "waldencatalyst", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
