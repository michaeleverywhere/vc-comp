#!/usr/bin/env python3
"""DASH Ventures portfolio scraper -> dashventures_companies.json
Source: https://www.dashventures.com/ — Webflow portfolio pop-up cards: name,
industries, markets, investment date / stage / status, website and description
(each company appears twice in the markup; deduped)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.dashventures.com/"
PRIMARY = "DASH Ventures"


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
    for it in s.select(".pop-up-card"):
        nm = txt(it.select_one("h2"))
        if not nm:
            continue
        f, cur = {}, None
        for el in it.select(".company-tags_list p, .company-tags_list .tag"):
            if el.name == "p":
                cur = (txt(el) or "").rstrip(":")
                f.setdefault(cur, [])
            elif cur and "alt" not in (el.get("class") or []):
                t = txt(el)
                if t:
                    f[cur].append(t)
        web = next((a for a in it.select("a.tag.alt, .company-tags_list a[href^='http']") if site(a)), None)
        g = lambda k: ", ".join(f.get(k, [])) or None
        st = g("Investment Status") or ""
        out.append(rec(nm, txt(it.select_one(".rt.w-richtext")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=f.get("Industries", []), markets=f.get("Markets", []), investment_date=g("Investment Date"),
                       stage=g("Investment Stage"), portfolio_status=st or None,
                       status="exited" if any(w in st.lower() for w in ("exit", "acquir")) else ("active" if "active" in st.lower() else None)))
    finish(out, "dashventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
