#!/usr/bin/env python3
"""CDP Venture Capital portfolio scraper -> cdpvc_companies.json
Source: https://www.cdpventurecapital.it/it/portfolio.page — portfolio flip cards
(`div.blocks-portfolio__card`): company name (front), sector and website.
Investee funds (fund-of-funds positions such as 'United Ventures III', 'Sofinnova
Capital XI', 'Programma 103') are skipped."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.cdpventurecapital.it/it/portfolio.page"
PRIMARY = "CDP Venture Capital"


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
    FUNDS = re.compile(r"\s(I|II|III|IV|V|VI|VII|VIII|IX|X|XI)$|Ventur|Growth|Programma|^P103$|^Primo (Climate|Digital)$|^360 Digitaly$|Panak|^Neva First|^Opes Italia|^Sofinnova")
    seen = set()
    for card in s.select("div.blocks-portfolio__card"):
        nm = txt(card.select_one("h4"))
        if not nm or nm.lower() in seen or re.search(r"\b(fund|fondo|fondi|sicaf|sicav|sgr|fof|euveca)\b", nm, re.I) or FUNDS.search(nm):
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in card.stripped_strings if clean(x)]
        sec = ss[1] if len(ss) > 1 and ss[1] != nm else None
        out.append(rec(nm, None, site(card.select_one("a[href^=http]")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec and sec != "Other" else []))
    finish(out, "cdpvc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
