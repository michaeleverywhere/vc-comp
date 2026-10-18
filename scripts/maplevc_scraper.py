#!/usr/bin/env python3
"""Maple VC portfolio scraper -> maplevc_companies.json
Source: https://maplevc.com/portfolio — portfolio page: company name (site-authored
logo alt) and website where linked."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://maplevc.com/portfolio"
PRIMARY = "Maple VC"


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
    seen = set()
    for img in s.find_all("img", alt=True):
        nm = clean(re.sub(r"(?i)\s*logo\s*$", "", img.get("alt") or ""))
        if not nm or len(nm.split()) > 5 or nm.lower() in set() or nm.lower() in seen or re.search(r"\.(png|jpe?g|svg|webp)$|_", nm, re.I):
            continue
        a = img.find_parent("a", href=re.compile(r"^https?://"))
        if False and (not a or 'maplevc' in a["href"]):
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, site(a) if a and 'maplevc' not in a["href"] else None, PRIMARY, SOURCE_URL, scraped_at))
    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    out = [r for r in out if r["company_name"] and not re.search('^(Maple|Kareem\\ Amin|Justin\\ Lee|Sam\\ Rosen|Ken\\ Chong|Nick\\ Narodny|David\\ Steckel|Andrew\\ Batey|Kuljeev\\ Singh|Jessica\\ Ko|Andrew\\ Chau|Kevin\\ Kim|Steve\\ Lau|Brennan\\ Spellacy|Zak\\ Lefevre|Kate\\ Hiscox|Thomas\\ Russell|Kathleen\\ Chan|Albert\\ Lai|Saad\\ Rajan|Michael\\ Hershfield|Josh\\ Simair|Gui\\ Laliberté|Jared\\ Nusinoff|Bryan\\ Pellegrino|Robbie\\ Deeks|Charlie\\ Labs|Jimoh\\ Ovbiagele|Ari\\ Ramdial|John\\ Yue|Shan\\ Wu|Mesh\\ Lakhani|Ben\\ Zifkin|Tom\\ Mulvey|Eden\\ Ovadia|Taemin\\ Kim|Lisa\\ Yan|Matt\\ Loszak|Mai\\ Trinh|Maricel\\ Saenz|Matthew\\ Shampine|Sean\\ Green|Peter\\ Joseph\\ Fitzpatrick|Ola\\ K\\.|Alexander\\ Liteplo|Sophia\\ Millar|Jonathan\\ Rosenbluth)$', r["company_name"])]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]
    finish(out, "maplevc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
