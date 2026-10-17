#!/usr/bin/env python3
"""Very Serious Ventures portfolio scraper -> veryserious_companies.json
Source: https://www.veryseriousventures.com/ — homepage Investments paragraph: names of the
notable angel investments and the fund's recent investments (acquired flags kept)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.veryseriousventures.com/"
PRIMARY = "Very Serious Ventures"


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
    p = next((x for x in s.find_all("p") if "Investments:" in x.get_text()), None)
    if p is not None:
        links = {clean(a.get_text()).rstrip(","): a.get("href") for a in p.find_all("a") if clean(a.get_text())}
        text = clean(p.get_text(" "))
        text = text.split("Investments:", 1)[1]
        groups = re.split(r"including:|Our recent investments include:", text)
        for gi, chunk in enumerate(groups[1:]):
            chunk = re.split(r"\s(?:and many more|Portfolio|Contact)\b", chunk)[0]
            for raw in re.split(r",", chunk):
                nm = clean(raw.replace("\u200d", ""))
                if not nm or len(nm) > 40:
                    continue
                acq = bool(re.search(r"\(acquired\)", nm, re.I))
                nm = clean(re.sub(r"\(acquired\)", "", nm, flags=re.I).strip(" .,"))
                if not nm:
                    continue
                href = links.get(nm) or links.get(nm + " (acquired)")
                out.append(rec(nm, None, href if href and href.startswith("http") and not href.endswith(".com/#") else href, PRIMARY, SOURCE_URL, scraped_at,
                               investment_type="angel (partners)" if gi == 0 else "fund",
                               status="acquired" if acq else None))
    finish(out, "veryserious", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
