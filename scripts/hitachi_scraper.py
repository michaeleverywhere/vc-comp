#!/usr/bin/env python3
"""Hitachi Ventures portfolio scraper -> hitachi_companies.json
Source: https://www.hitachi-ventures.com/portfolio/ — portfolio modals
(`div.portfolio-modal-box`): name (logo alt), tagline, description, website,
CEO, sectors, stage and HQ."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.hitachi-ventures.com/portfolio/"
PRIMARY = "Hitachi Ventures"


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
    import time
    for _ in range(5):
        # the host sometimes serves a short "One moment, please..." reload page; wait and retry
        html = fetch_response(SOURCE_URL).content.decode("utf-8", "replace")
        if "portfolio-modal-box" in html:
            break
        time.sleep(8)
    s = BeautifulSoup(html, "html.parser")
    # the page embeds its portfolio posts as JSON: post_slug -> post_title (+ exited flag)
    titles, exited = {}, {}
    for m in re.finditer(r'"post_slug":"((?:[^"\\]|\\.)*)","post_title":"((?:[^"\\]|\\.)*)"', html):
        slug, title = json.loads('"%s"' % m.group(1)), json.loads('"%s"' % m.group(2))
        titles[slug] = clean(BeautifulSoup(title, "html.parser").get_text())
        nxt = html.find('"post_slug":', m.end())
        tail = html[m.end():nxt if nxt > 0 else m.end() + 20000]
        e = re.search(r'"exited":"([^"]*)"', tail)
        exited[slug] = e.group(1) if e else ""
    for b in s.select("div.portfolio-modal-box"):
        bid = b.get("id") or ""
        img = b.select_one(".top-area img")
        alt = clean(re.sub(r"\s*logo\s*$", "", img.get("alt") or "", flags=re.I)) if img else None
        nm = titles.get(bid) or alt
        if nm and re.search(r"\s*\(exited\)\s*$", nm, flags=re.I):
            nm = clean(re.sub(r"\s*\(exited\)\s*$", "", nm, flags=re.I))
            exited[bid] = exited.get(bid) or "1"
        if not nm:
            continue
        info = {txt(x.find("h3")): txt(x.find("p")) for x in b.select(".info-box") if x.find("h3")}
        web = next((site(a) for a in b.select("a.btn") if txt(a) == "Website"), None)
        tag = txt(b.select_one(".top-area h3"))
        sec = [x.strip() for x in (info.get("Sectors") or "").split(",") if x.strip()]
        out.append(rec(nm, txt(b.select_one(".left-area p")) or tag, web, PRIMARY, SOURCE_URL, scraped_at, sectors=sec,
                       tagline=tag, ceo=info.get("CEO"), stage=info.get("Stage"), headquarters=info.get("HQ"),
                       status="exited" if exited.get(bid) else None))
    finish(out, "hitachi", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
