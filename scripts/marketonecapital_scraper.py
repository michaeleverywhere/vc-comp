#!/usr/bin/env python3
"""Market One Capital portfolio scraper -> marketonecapital_companies.json
Source: https://www.moc.vc/portfolio — portfolio page: company name (site-authored
link
text) and website where linked."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.moc.vc/portfolio"
PRIMARY = "Market One Capital"


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
    for el in s.select("a[href^='http']"):
        nm = clean(re.sub(r"(?i)\s*logo\s*$", "", txt(el) or ""))
        if not nm or len(nm) > 60 or len(nm.split()) > 5 or nm.lower() in seen or re.compile('(?i)^(visit|website|learn more|read more|view|linkedin|twitter|lp login|login|jobs|careers|contact|apply|pitch|privacy|terms)\\b|^$', re.I).search(nm):
            continue
        a = el if el.name == "a" else (el.find_parent("a", href=re.compile(r"^https?://")) or el.find("a", href=re.compile(r"^https?://")))
        u = a["href"] if a is not None and a.get("href", "").startswith("http") and 'moc' not in a["href"] and not re.search(r"linkedin|twitter|x\.com/|crunchbase|facebook|instagram", a["href"]) else None
        st = None
        m = re.compile('(?!x)x', re.I).search(nm)
        if m:
            st = clean(m.group(1)); nm = clean(nm[:m.start()])
            if not nm or nm.lower() in seen:
                continue
        seen.add(nm.lower())
        out.append(rec(nm, None, u, PRIMARY, SOURCE_URL, scraped_at, status=st))
    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    out = [r for r in out if r["company_name"] and not re.search('^(Andreas\\ Naumann|Ville\\ Mikkola|August\\ Joseph|Chase\\ Gummer|Borja\\ Balle|Ignacio\\ Gamoneda\\ Lasa|Daniel\\ Arenas\\ Rivera|Denis\\ Stepanov|Dr\\.\\ Pierric\\ Appert|Nico\\ Haltmayer|Pavel\\ Penchev|Alex\\ Sharkov|Laurynas\\ Jokubaitis|Ignas\\ Survila|Przemyslaw\\ Budkowski|Łukasz\\ Lato|Marcin\\ Urbanczyk|Tomasz\\ Drozdzynski|Leszek\\ Zawadzki|Alina\\ Prelicz|Paweł\\ Tatarczuk|Miguel\\ Rasero|Ricardo\\ Ghekiere|Bartosz\\ Majewski|Agata\\ Krawiec‑Rokita|Mateusz\\ Godala|Kamil\\ Warulik|Aish\\ Agarwal|Peter\\ Wisniewski|Charlotte\\ Dryander|Sebastian\\ Riegelbauer|Hans\\-Juergen\\ Griesbacher|Benjamin\\ Rath|Julien\\ Quintard|Quentin\\ Hocquet|Mindaugas\\ Apanavičius|Kęstutis\\ Ramoškevičius|Sebastian\\ Brenner|Rafael\\ Suchan|Mathias\\ Mouats|Steve\\ Belkaçemi|Rashid\\ Mansoor|Tobin\\ Ireland|More\\ Growth|Jakub\\ Koziej|Justinas\\ Baranovskis|Oleg\\ Lopeta|Adrian\\ Kosowski|Claire\\ Nouet|Zuzanna\\ Stamirowska|Jan\\ Chorowski|Alexander\\ Lempka|Nicolas\\ Carmont|Matt\\ Barrie|Louis\\ Collar\\ \\-\\ Smith|Camiel\\ Kraan|Max\\ Faldin|Ralf\\ Wenzel|Konstantin\\ Sorger|Aspa\\ Lekka|Benjamin\\ Bauer|Sven\\ Grajetzki|Rui\\ Bento|Nuno\\ Rodrigues|Adam\\ Plona|Jakub\\ Zieliński|Małgorzata\\ Ohme|Maarten\\ Elferink|Nadim\\ El\\ Manawy|Alex\\ Lamb|Adam\\ Janczewski|Thom\\ Jenkins|Will\\ Monk|Michael\\ Högemann|Uwe\\ Hoelzer|Luca\\ Ongaro|Oliver\\ Ruschpler|Juan\\ Rubio\\ López|Luis\\ García\\ Díez|Chema\\ Roldán|Daniel\\ Kierdal|Wojciech\\ Ciołko|Łukasz\\ Pawlik|Szymon\\ Pawlik|Daniel\\ Wartołowski|Piotr\\ Smoleń|Mateusz\\ Romanowski|Lawrence\\ Leuschner|Julian\\ Blessin|Mathias\\ Laug|Alexandros\\ Trimis|Savvas\\ Georgiou|Tomasz\\ Kucharski|Paweł\\ Tymczyna|Ross\\ Knap|Sergey\\ Butko|Andrew\\ Tkachiv|Octavi\\ Uya|Roger\\ Llovet\\ Hom|Wojtek\\ Sadowski|Maciej\\ Woźniczko|Konrad\\ Kwiatkowski|Maciej\\ Zając|Arkadiusz\\ Wasilonek|Krzysztof\\ Chudzik|Hanno\\ Lippitsch|Emanuel\\ Steiniger|Stefan\\ Feirer|Philipp\\ Braunsberger|Sebastian\\ Maśka|Paweł\\ Kantyka|Stefan\\ Batory|Konrad\\ Howard|Kirill\\ Bigai|Dmytro\\ Voloshyn|Michał\\ Borkowski|Tomasz\\ Kraus|Łukasz\\ Haluch|Mariusz\\ Gralewski|Jakub\\ Skoczylas|Lucjan\\ Samulowski|Portfolio\\ Jobs|Your\\ pitch|Patryk\\ Kabaj|Brand\\ assets)$', r["company_name"])]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]
    finish(out, "marketonecapital", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
