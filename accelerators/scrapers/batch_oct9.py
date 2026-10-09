"""Scrapers for the 2026-10-09 Daily-10 accelerator batch.
Usage: python batch_oct9.py [slug...]

Sources: each accelerator's own public portfolio page (or that page's embedded
data / its own company detail pages), plus the company's own website for blank
descriptions. Never Crunchbase / LinkedIn / PitchBook. Tags are keyword-only
(automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

from batch_oct8 import finish, rec, strip, year_batch
from common import clean, dedupe, enrich_from_sites, norm_linkedin, save

S = requests.Session()
# Safari UA: startupwiseguys.com resets TLS for the Chrome UA used elsewhere
S.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                                "(KHTML, like Gecko) Version/17.5 Safari/605.1.15"})


def get(url, **kw):
    r = S.get(url, timeout=kw.pop("timeout", 60), **kw)
    r.raise_for_status()
    return r.text


def pmap(fn, xs, n=12):
    with ThreadPoolExecutor(n) as ex:
        return list(ex.map(fn, xs))


def newest_flag(out):
    newest = max((r.get("batch_date") or "" for r in out), default="")
    for r in out:
        r["most_recent_batch"] = bool(newest and r.get("batch_date") == newest)
    return out


# ---------------- Startup Wise Guys ----------------
def startupwiseguys():
    url = "https://startupwiseguys.com/portfolio/"
    s = get(url)
    out = []
    for raw in re.findall(r'data-details="([^"]+)"', s):
        d = json.loads(_h.unescape(raw))
        info = {i["slug"]: strip(i.get("value") or "") for i in d.get("info-items") or []}
        links = {l["title"]: (l.get("value") or "").strip() for l in d.get("links") or []}
        verts = [strip(x) for x in re.findall(r"<span[^>]*>(.*?)</span>", (d.get("vertical") or "") + (d.get("subVerticals") or ""))]
        status = info.get("status", "")
        batch = clean(d.get("batch") or info.get("batch") or "")
        out.append(rec(d.get("title") or "", "Startup Wise Guys", "Startup Wise Guys",
                       description=strip(d.get("description")), website=links.get("Website", ""),
                       team=info.get("founders", ""), verticals="; ".join(v for v in verts if v),
                       date=f"Startup Wise Guys {batch}".strip(), location=d.get("countryTitle") or "",
                       status="Exited" if status == "Exit" else status, founded=info.get("founding-date", ""),
                       source_url=url))
    enrich_from_sites(out)
    year_batch(out)
    return finish(dedupe(out))


# ---------------- Antler ----------------
# Antler's own published sector labels -> Everywhere tags (prepended to keyword tags)
ANTLER_LABELS = {"consumertech": "Consumer", "fintech": "FinTech / Insurance", "health and biotech": "Health",
                 "energy and climatetech": "Climate / Sustainability", "real estate and proptech": "PropTech"}


def antler_tags(out):
    for r in out:
        for l in [x.strip().lower() for x in (r.get("verticals") or "").split(";") if x.strip()]:
            m = ANTLER_LABELS.get(l)
            if m and m not in r["everywhere_tags"]:
                r["everywhere_tags"] = ([m] + r["everywhere_tags"])[:4]
    return out


def antler():
    base = "https://www.antler.co/portfolio"
    out, url = [], base
    for pg in range(1, 200):
        s = get(url)
        cards = re.split(r'<div class="portco_card">', s)[1:]
        for c in cards:
            name = strip((re.search(r'fs-cmsfilter-field="name"[^>]*>(.*?)</p>', c, re.S) or [0, ""])[1])
            desc = strip((re.search(r'fs-cmsfilter-field="description"[^>]*>(.*?)</p>', c, re.S) or [0, ""])[1])
            tags = re.findall(r'<div fs-cmsfilter-field="([^"]+)" class="tag_small_wrap"><div[^>]*class="tag_small_text">(.*?)</div>', c)
            loc = next((strip(v) for k, v in tags if k not in ("sector", "year")), "")
            sector = "; ".join(strip(v) for k, v in tags if k == "sector")
            year = next((strip(v) for k, v in tags if k == "year"), "")
            web = (re.search(r'class="clickable_wrap[^"]*"><a target="_blank" href="([^"]*)"', c) or [0, ""])[1]
            if name:
                out.append(rec(name, "Antler", "Antler", description=desc, website=web if web.startswith("http") else "",
                               verticals=sector, location=loc, date=f"Antler {year}".strip(), source_url=base))
        nxt = re.search(r'href="(\?[a-z0-9]+_page=\d+)"[^>]*class="[^"]*w-pagination-next', s) or \
            re.search(r'class="[^"]*w-pagination-next[^"]*"[^>]*href="(\?[a-z0-9]+_page=\d+)"', s)
        if not nxt or not cards:
            break
        url = base + _h.unescape(nxt.group(1))
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return antler_tags(finish(out))


# ---------------- EWOR ----------------
def ewor():
    base = "https://www.ewor.com"
    s = get(base + "/our-startups")
    out = []
    for it in s.split('class="startup-item w-dyn-item"')[1:]:
        m = re.search(r'<a href="(/startups/[^"]+)" class="startups-link.*?<div class="text-size-s text-align-center">(.*?)</div><div class="startup-blurb[^"]*">(.*?)</div>', it, re.S)
        if not m:
            continue
        href, name, blurb = m.groups()
        out.append(rec(strip(name), "EWOR", "EWOR", description=strip(blurb), source_url=base + href, date="EWOR Fellowship"))

    def detail(r):
        try:
            h = get(r["source_url"], timeout=30)
        except Exception:
            return r
        main = h.split("Fellow Login", 1)[-1].split("More from EWOR", 1)[0]
        links = [u for u in re.findall(r'href="(https?://[^"]+)"', main) if "ewor" not in u and "website-files" not in u]
        web = next((u for u in links if "linkedin.com" not in u), "")
        li = next((norm_linkedin(u) for u in links if "linkedin.com/company" in u), "")
        t = strip(re.sub(r"<script.*?</script>|<style.*?</style>", " ", main, flags=re.S))
        fellows = re.findall(r"([A-ZÀ-Ž][\w\-'À-ž]+(?: [A-ZÀ-Ž][\w\-'À-ž.]+){1,3}) Fellow\b", t)
        about = (re.search(r"\bAbout (.*)$", t) or [0, ""])[1]
        if web:
            r["website"] = web
        if li:
            r["linkedin_url"] = li
        if fellows:
            r["team"] = ", ".join(dict.fromkeys(fellows))
        if about and len(about) > len(r["description"]):
            r["description"] = (r["description"].rstrip(".") + ". " + about).strip(". ") if r["description"] else about
        return r

    out = pmap(detail, out)
    enrich_from_sites(out)
    return finish(dedupe(out))


# ---------------- Accelerace ----------------
def accelerace():
    url = "https://accelerace.io/startups/"
    s = get(url)
    out = []
    for c in re.split(r'<div class="col-12 col-md-4 startup-item"', s)[1:]:
        country = (re.search(r'data-country="([^"]*)"', c) or [0, ""])[1]
        href = (re.search(r'href="(https://accelerace\.io/startups/[^"]+)"', c) or [0, ""])[1]
        badges = [strip(b) for b in re.findall(r'<span class="badge[^"]*">(.*?)</span>', c, re.S)]
        name = strip((re.search(r'class="card-title[^"]*">(.*?)</h3>', c, re.S) or [0, ""])[1])
        desc = strip((re.search(r'class="card-text">(.*?)</p>', c, re.S) or [0, ""])[1])
        status = next((b for b in badges if b in ("Active", "Exited", "Closed", "Inactive")), "")
        nxt = next((b[len("Next round "):] for b in badges if b.startswith("Next round ")), "")
        inds = [b for b in badges if b and b != status and not b.startswith("Next round")]
        if name:
            out.append(rec(name, "Accelerace", "Accelerace", description=desc, verticals="; ".join(inds),
                           location=country, status=status, next_round=nxt, date="Accelerace",
                           source_url=href or url))
    return finish(dedupe(out))


# ---------------- Norrsken Evolve (formerly Norrsken Accelerator) ----------------
def norrskenaccelerator():
    url = "https://www.norrskenevolve.vc/portfolio"
    s = get(url)
    out = []
    for c in s.split('role="listitem" class="faq-list w-dyn-item"')[1:]:
        name = strip((re.search(r'fs-list-field="name"[^>]*>(.*?)</div>', c, re.S) or [0, ""])[1])
        labs = [strip(x) for x in re.findall(r'fs-list-field="sector"[^>]*>(.*?)</div>', c, re.S)]
        prob = strip((re.search(r'fs-list-field="problem"[^>]*>(.*?)</p>', c, re.S) or [0, ""])[1])
        sol = strip((re.search(r'fs-list-field="solution"[^>]*>(.*?)</p>', c, re.S) or [0, ""])[1])
        web = (re.search(r'const rawUrl = "([^"]*)"', c) or [0, ""])[1]
        year = strip((re.search(r'fs-list-field="year"[^>]*>(.*?)</div>', c, re.S) or [0, ""])[1])
        sector, country = (labs + ["", ""])[:2]
        if name and not re.fullmatch(r"stealth", name, re.I):   # unnamed stealth entry skipped
            out.append(rec(name, "Norrsken Evolve", "Norrsken Evolve", description=sol or prob, website=web,
                           verticals=sector, location=country, date=f"Norrsken Evolve {year}".strip(),
                           source_url=url))
    out = dedupe(out)
    enrich_from_sites([r for r in out if not r["description"]])
    year_batch(out)
    return finish(out)


# ---------------- 8200 EISP ----------------
def eisp8200():
    url = "https://eisp.8200.org.il/alumni"
    s = get(url)
    names = []
    for n in re.findall(r'<h6 class="font_6 wixui-rich-text__text">(?:<[^>]+>)*([^<]+)(?:</[^>]+>)*</h6>', s):
        n = clean(_h.unescape(n))
        if n and n not in names:
            names.append(n)
    out = []
    for n in names:
        status, note = "", ""
        m = re.search(r"\(\s*(Acquired by [^)]+)\)", n, re.I)
        if m:
            status, note = "Acquired", m.group(1)
            n = clean(n[:m.start()])
        m = re.search(r"\(\s*((?:Formerly|Previous|Yeloha|Desti)[^)]*)\)", n, re.I)
        former = ""
        if m:
            former = m.group(1)
            n = clean(n[:m.start()] + n[m.end():])
        desc = "; ".join(x for x in (note, former) if x)
        out.append(rec(n, "8200 EISP", "8200 EISP", description=desc, status=status, location="Israel",
                       date="8200 EISP alumni", source_url=url))
    return finish(dedupe(out))


# ---------------- UpWest ----------------
def upwest():
    url = "https://upwest.vc/portfolio/"
    s = get(url)
    grid, modal = s.split('<section class="portfolio--modal">', 1)
    cards = {}
    for m in re.finditer(r'<div class="portfolio--grid-card[^"]*"\s+data-modal="(\d+)"\s+data-name="([^"]*)"(.*?)</div>\s*</div>', grid, re.S):
        alt = (re.search(r'alt="([^"]*)"', m.group(3)) or [0, ""])[1]
        cards[m.group(1)] = (m.group(2), clean(re.sub(r"\s*logo$", "", _h.unescape(alt), flags=re.I)), "Exited" in m.group(3))
    out = []
    for m in re.finditer(r'<div class="portfolio--modal-slide" data-modal="(\d+)" data-name="([^"]*)">(.*?)<div class="image">', modal, re.S):
        idx, slug, body = m.groups()
        cslug, alt, exited = cards.get(idx, (slug, "", False))
        ps = [strip(p) for p in re.findall(r"<p>(.*?)</p>", body, re.S)]
        web = (re.search(r'<a href="([^"]+)" target="_blank" class="btn"', body) or [0, ""])[1]
        name = alt or (re.search(r'alt="([^"]*)"', body) or [0, ""])[1].replace(" logo", "").strip()
        if not name:
            name = slug.replace("-", " ").title()
        first = " ".join(p for p in ps if re.search(r"first check|first investor", p, re.I))
        yr = (re.search(r"\b(20\d\d)\b", first) or [0, ""])[1]
        desc = " ".join(p for p in ps if p)
        if re.fullmatch(r"[-\s]*stealth[-\s]*", name, re.I):
            continue   # unnamed stealth company: no identifiable record
        first_tok = (re.match(r"([A-Za-z0-9][\w.\-]*)", desc) or [0, ""])[1].rstrip(".")
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", web.lower())).split("/")[0].split(".")[0]
        ft = first_tok.lower().replace("-", "")
        if first_tok and ((name.lower() == host and ft and name.lower().startswith(ft)
                           and name.lower()[len(ft):] in ("drones", "tech", "labs", "ai", "app", "hq", "io"))
                          or (name.islower() and ft == name.lower())):
            name = first_tok
        out.append(rec(name, "UpWest", "UpWest", description=desc, website=web, status="Exited" if exited else "",
                       first_invested=yr, date=f"UpWest {yr}".strip() if yr else "UpWest", source_url=url))
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- SOSA ----------------
def sosa():
    base = "https://www.sosa.co"
    s = get(base + "/ilpn-dealbook")
    hrefs = list(dict.fromkeys(re.findall(r'href="(/portfolio-companies/[^"]+)"', s)))
    sm = get(base + "/sitemap.xml")
    for u in re.findall(r"<loc>https://(?:www\.)?sosa\.co(/portfolio-companies/[^<]+)</loc>", sm):
        if u not in hrefs:
            hrefs.append(u)
    out = []
    for h in hrefs:
        p = get(base + h)
        name = strip((re.search(r'<h1 class="sign-up-heading">(.*?)</h1>', p, re.S) or [0, ""])[1])
        sector = strip((re.search(r'class="sign-up-subheading">(.*?)</div>', p, re.S) or [0, ""])[1])
        tagline = strip((re.search(r'<div class="div-block-108"><h1 class="text-subtitle">(.*?)</h1>', p, re.S) or [0, ""])[1])
        body = strip((re.search(r'<p class="case-study_date">(.*?)</p>', p, re.S) or [0, ""])[1])
        fields = dict((strip(k).upper(), v) for k, v in re.findall(r'<h1 class="text-subtitle smaller">(.*?)</h1>(.*?)</div>', p, re.S))
        country = strip(re.sub(r"<a .*", "", fields.get("COUNTRY", ""), flags=re.S))
        founded = strip(fields.get("FOUNDED", ""))
        rnd = strip(fields.get("FUNDING ROUND", ""))
        leaders = re.findall(r'<p class="case-study_date smaller _1fg">(.*?)</p><p class="case-study_date smaller _1fg">(.*?)</p>', p, re.S)
        team = ", ".join(f"{strip(a)} ({strip(b)})" if strip(b) else strip(a) for a, b in leaders)
        web = (re.search(r'<a href="([^"]+)" target="_blank" class="div-block-111[^"]*"><h1 class="text-subtitle orange">Website', p) or [0, ""])[1]
        li = (re.search(r'<a href="([^"]+)" target="_blank" class="div-block-111[^"]*"><h1 class="text-subtitle orange">LinkedIn', p) or [0, ""])[1]
        desc = (tagline.rstrip(".") + ". " + body).strip(". ") if tagline else body
        out.append(rec(name, "SOSA", "SOSA", description=desc, website=web, linkedin_url=norm_linkedin(li),
                       verticals=sector, location=country, founded=founded, team=team,
                       round="" if rnd.lower() in ("no backing", "") else rnd,
                       date="SOSA International Landing Pad Network (NYC)", most_recent_batch=True,
                       source_url=base + h))
    return finish(dedupe(out))


# ---------------- Surge (Peak XV) ----------------
def surgepeakxv():
    base = "https://surge.peakxv.com"
    sm = get(base + "/sitemap.xml")
    urls = list(dict.fromkeys(re.findall(r"<loc>(https://surge\.peakxv\.com/companies/[^<]+)</loc>", sm)))
    # category labels from the public /companies listing (All Startups tab, paginated)
    cats = {}
    for pg in range(1, 10):
        try:
            h = get(base + f"/companies?c441173e_page={pg}")
        except Exception:
            break
        found = 0
        for it in h.split('class="com-header_inline-item w-dyn-item"')[1:]:
            href = (re.search(r'href="(/companies/[^"]+)"', it) or [0, ""])[1]
            cs = [strip(x) for x in re.findall(r'fs-list-field="category"[^>]*>(.*?)</div>', it, re.S)]
            if href:
                cats[base + href] = "; ".join(c for c in cs if c)
                found += 1
        if not found or f"c441173e_page={pg + 1}" not in h:
            break

    def detail(u):
        try:
            p = get(u, timeout=30)
        except Exception:
            return None
        if 'rel="canonical"' in p and "surge.peakxv.com/404" in p:
            return None
        t = strip(re.sub(r"<script.*?</script>|<style.*?</style>", " ", p, flags=re.S))
        name = clean(_h.unescape((re.search(r"<title>(.*?)\s*\|\s*Surge", p, re.S) or [0, ""])[1]))
        if not name:
            return None
        m = re.search(r"← Back (Surge \d+)", t)
        cohort = m.group(1) if m else ""
        web = (re.search(r"Website (https?://\S+)", t) or [0, ""])[1]
        meta = {}
        for lab, body in re.findall(r'class="text-style-tagline-surge[^"]*">([^<]+)</div>(.*?)(?=class="text-style-tagline-surge|content-style1_rct|$)', p, re.S):
            meta[clean(lab)] = [strip(x) for x in re.findall(r'text-weight-semibold">(.*?)</div>', body, re.S)]
        founders = ", ".join(meta.get("Founders") or meta.get("Founder") or [])
        coinv = [x for x in (meta.get("Co-Investors") or meta.get("Co-Investor") or []) if x]
        rich = (re.search(r'class="content-style1_rct w-richtext">(.*?)</div>', p, re.S) or [0, ""])[1]
        paras = [strip(x) for x in re.findall(r"<p>(.*?)</p>", rich, re.S)]
        desc = " ".join(x for x in paras if x)[:1500]
        inv = "Surge (Peak XV)" + ("; " + "; ".join(coinv) if coinv else "")
        return rec(name, inv, "Surge (Peak XV)", description=desc, website=web, team=founders,
                   verticals=cats.get(u, ""), date=cohort or "Surge", source_url=u)

    out = [r for r in pmap(detail, urls, 8) if r and not re.fullmatch(r"stealth", r["name"], re.I)]
    # current-cohort cards on the listing page carry founders + sectors
    try:
        h = get(base + "/companies")
        for it in h.split('class="com-header_block_item w-dyn-item"')[1:]:
            href = (re.search(r'href="(/companies/[^"]+)"', it) or [0, ""])[1]
            info = {}
            for lab, body in re.findall(r'data-plural-label="([^"]+)"[^>]*>[^<]*</div>(.*?)(?=data-singular-label|$)', it, re.S):
                info[lab] = [strip(x) for x in re.findall(r"<span>(.*?)</span>", body, re.S)]
            for r in out:
                if r["source_url"] == base + href:
                    if not r["team"] and info.get("Founders"):
                        r["team"] = ", ".join(info["Founders"])
                    if info.get("Sectors"):
                        r["verticals"] = "; ".join(dict.fromkeys([x for x in r["verticals"].split("; ") if x] + info["Sectors"]))
                    r["current_cohort"] = True
    except Exception:
        pass
    for r in out:
        m = re.search(r"Surge (\d+)", r["date"])
        r["cohort_number"] = int(m.group(1)) if m else None
    nums = [r["cohort_number"] for r in out if r["cohort_number"]]
    top = max(nums) if nums else None
    for r in out:
        r["most_recent_batch"] = bool(top and r["cohort_number"] == top)
    out = dedupe(out)
    enrich_from_sites([r for r in out if not r["description"]])
    return finish(out)


# ---------------- Axilor Ventures ----------------
AX_STAGE = {"*": "Series A", "**": "Series B", "***": "Series C"}


def axilorventures():
    url = "https://www.axilor.com/portfolio/"
    s = get(url)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)       # drop commented-out (retired) tiles
    out = []
    # featured slider: name, tagline, sector, impact, year of investment
    for blk in s.split('<article class="portfolio-banner-left-blk">')[1:]:
        name = strip((re.search(r"<h2>(.*?)</h2>", blk, re.S) or [0, ""])[1])
        tag = strip((re.search(r'<p class="banner-txt">(.*?)</p>', blk, re.S) or [0, ""])[1])
        vals = dict((strip(k), strip(v)) for k, v in re.findall(r'<h3 class="h5">(.*?)</h3>\s*<p>(.*?)</p>', blk, re.S))
        yr = vals.get("Year of Investment", "").strip("- ")
        out.append(rec(name.title() if name.isupper() else name, "Axilor Ventures", "Axilor Ventures", description=tag,
                       verticals=vals.get("Sector", ""), first_invested=yr if re.match(r"^\d{4}$", yr) else "",
                       location="India", date="Axilor Ventures", source_url=url))
    secs = ["Commerce/Supply Chain", "Global Enterprise SAAS", "SMB SAAS", "Fintech", "Health Care",
            "Agri / Lifesciences", "Consumer", "Climate"]
    pos = sorted((m.start(), sec) for sec in secs
                 for m in re.finditer(r">\s*" + re.escape(sec) + r"\s*<", s))
    grid_start = s.find("Fast growing portfolio")
    feat = {r["name"].lower(): r for r in out}
    tiles = [(m.start(), m.group(1), m.group(2), m.group(3)) for m in re.finditer(
        r'<a href="([^"]*)"[^>]*class="box-link"(?: data-tooltip="([^"]*)")?[^>]*>(.*?)</a>', s, re.S)]
    tiles += [(m.start(), "", m.group(1), m.group(2)) for m in re.finditer(
        r'<div class="box-link"(?: data-tooltip="([^"]*)")?[^>]*>(.*?)</figcaption>', s, re.S)]
    for start, href, tip0, body in sorted(tiles):
        m = type("M", (), {"start": lambda self, v=start: v, "group": lambda self, i, a=(None, href, tip0, body): a[i]})()
        if m.start() < grid_start:
            continue
        body = m.group(3)
        alt = clean(_h.unescape((re.search(r'alt="([^"]*)"', body) or [0, ""])[1]))
        alt = re.sub(r"\s*logo$", "", alt, flags=re.I)
        h3 = strip((re.search(r"<h3[^>]*>(.*?)</h3>", body, re.S) or [0, ""])[1])
        lab = strip((re.search(r"<h4[^>]*>(.*?)</h4>", body, re.S) or [0, ""])[1])
        stars = (re.search(r"(\*+)$", h3) or [0, ""])[1]
        raw = h3.rstrip("*").strip()
        if raw.upper() == "UNANNOUNCED" or not raw:
            continue
        if raw.upper() == "LOCO" and "locofast" in (m.group(1) or ""):
            continue   # tile labelled LOCO/Apparels links to Locofast (already listed); skip the duplicate
        if raw.upper() == "5CN":
            raw = alt = "5C Network"
        name = alt if alt and alt.lower().replace(" ", "") == raw.lower().replace(" ", "") else (raw.title() if raw.isupper() else raw)
        sec = ""
        for q, nm in pos:
            if q < m.start():
                sec = nm
        before = s[:m.start()]
        exit_ = before.rfind(">Exits<") > max((q for q, _ in pos if q < m.start()), default=-1)
        web = m.group(1) if (m.group(1) or "").startswith("http") and "axilor" not in m.group(1) else ""
        news = ""
        if re.search(r"economictimes|livemint|techcrunch|yourstory|inc42|moneycontrol|/articleshow/|/news/", web):
            news, web = web.rstrip(")"), ""
        rnd = "Micelio (Axilor-Micelio fund)" if stars == "****" else AX_STAGE.get(stars, "")
        r = feat.get(name.lower())
        if r is None:
            r = rec(name, "Axilor Ventures", "Axilor Ventures", location="India", date="Axilor Ventures", source_url=url)
            out.append(r); feat[name.lower()] = r
        tip = clean(_h.unescape(m.group(2) or ""))
        if tip and tip not in r["description"]:
            r["description"] = (r["description"].rstrip(".") + ". " + tip).strip(". ") if r["description"] else tip
        r["website"] = r["website"] or web
        r["verticals"] = "; ".join(dict.fromkeys(x for x in (r["verticals"], sec, lab) if x))
        if rnd and not r.get("round"):
            r["round"] = rnd
        if exit_:
            r["status"] = "Exited"
        if news:
            r["exit_source"] = news
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(out)


if __name__ == "__main__":
    FUNCS = {"startupwiseguys": startupwiseguys, "antler": antler, "ewor": ewor, "accelerace": accelerace,
             "norrskenaccelerator": norrskenaccelerator, "8200eisp": eisp8200, "upwest": upwest,
             "sosa": sosa, "surgepeakxv": surgepeakxv, "axilorventures": axilorventures}
    if sys.argv[1:2] == ["--retag-antler"]:   # re-apply antler_tags to the saved file (no re-scrape)
        import os
        from common import DATA_DIR
        d = json.load(open(os.path.join(DATA_DIR, "antler_companies.json")))
        save("antler", antler_tags(d["companies"]), {"source_fn": d["source_fn"]})
        sys.exit(0)
    for slug in sys.argv[1:] or list(FUNCS):
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct9.{FUNCS[slug].__name__}"})
