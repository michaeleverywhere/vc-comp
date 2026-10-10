"""Scrapers for the 2026-10-10 Daily-10 accelerator batch.
Usage: python batch_oct10.py [slug...]

Sources: each accelerator's own public portfolio page (or the data that page
itself loads / its own company detail pages), plus the company's own website for
blank descriptions. Never Crunchbase / LinkedIn / PitchBook. Tags are keyword-only
(automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

import cdp
from batch_oct8 import finish, rec, strip, year_batch
from common import clean, dedupe, enrich_from_sites, norm_linkedin, save

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                                "(KHTML, like Gecko) Version/17.5 Safari/605.1.15"})
SOCIAL = re.compile(r"facebook\.com|twitter\.com|x\.com/|instagram\.com|youtube\.com|linkedin\.com|"
                    r"naver\.com|t\.me/|tiktok\.com|medium\.com/@|wa\.me", re.I)


def get(url, **kw):
    r = S.get(url, timeout=kw.pop("timeout", 60), **kw)
    r.raise_for_status()
    return r.text


def pmap(fn, xs, n=12):
    with ThreadPoolExecutor(n) as ex:
        return list(ex.map(fn, xs))


def txt(s):
    return strip(s or "")


def first(rx, s, flags=re.S, g=1):
    m = re.search(rx, s, flags)
    return m.group(g) if m else ""


# ---------------- Rockstart ----------------
# rockstart.com serves an automatic browser check (SiteGround) to plain HTTP clients,
# so its own /portfolio/ page is rendered in headless Chrome.
def rockstart():
    url = "https://rockstart.com/portfolio/"
    s = cdp.render(url, "document.querySelectorAll('article.portfolio').length")
    domain = {}
    for d, lab in (("agrifood", "AgriFood"), ("energy", "Energy"), ("emerging-tech", "Emerging Tech")):
        ds = cdp.render(f"https://rockstart.com/portfolio/domain-{d}/", "document.querySelectorAll('article.portfolio').length")
        for pid in re.findall(r'<article id="post-(\d+)"', ds):
            domain.setdefault(pid, []).append(lab)
    out = []
    for pid, body in re.findall(r'<article id="post-(\d+)"(.*?)</article>', s, re.S):
        a = re.search(r'<h5[^>]*>\s*<a href="([^"]*)"[^>]*>(.*?)</a>', body, re.S)
        if not a:
            continue
        web, name = a.group(1), txt(a.group(2))
        heads = [txt(x) for x in re.findall(r'<(?:p|h6) class="elementor-heading-title[^"]*">(.*?)</(?:p|h6)>', body, re.S)]
        desc = heads[0] if heads and heads[0] not in ("Year Added", "Funding Status") else ""
        kv = {heads[i]: heads[i + 1] for i in range(len(heads) - 1) if heads[i] in ("Year Added", "Funding Status")}
        terms = [txt(x) for x in re.findall(r'terms-list-item">(.*?)</span>', body, re.S)]
        dom = domain.get(pid, [])
        fs = kv.get("Funding Status", "")
        r = rec(name, "Rockstart", "Rockstart", description=desc, website=web if web.startswith("http") else "",
                verticals="; ".join(dict.fromkeys(dom + terms)), round=fs if fs != "Acquired" else "",
                status="Acquired" if fs == "Acquired" else "",
                date=f"Rockstart {kv.get('Year Added', '')}".strip(), source_url=url)
        r["rockstart_domain"] = "; ".join(dom)
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- Venture Catalysts ----------------
# venturecatalysts.in/portfolio is a JS app; capture the portfolio rows the page itself loads.
BAD_WEB = re.compile(r"resend\.com/emails|linkedin\.com/feed|google\.com/search|^https?://(www\.)?venturecatalysts", re.I)


def venturecatalysts():
    url = "https://www.venturecatalysts.in/portfolio"
    bodies = cdp.capture(url, r"/rest/v1/Portfolio\?")
    rows = []
    for b in bodies:
        try:
            rows = json.loads(b["body"])
            if rows:
                break
        except Exception:
            pass
    out = []
    for d in rows:
        if d.get("is_hidden"):
            continue
        name = clean(d.get("title") or d.get("alt_text") or "")
        if not name:
            continue
        web = (d.get("website_url") or "").strip()
        if BAD_WEB.search(web):
            web = ""
        li = d.get("linkedin_url") or ""
        founders = ", ".join(clean(f.get("name")) for f in (d.get("founders") or []) if f.get("name"))
        ms = {clean(m.get("description")): clean(m.get("year")) for m in (d.get("milestones") or [])}
        founded = next((y for k, y in ms.items() if "Founded" in k and y), "")
        inv = next((y for k, y in ms.items() if "Investment" in k and y), "")
        tags_ = d.get("tags") or []
        desc = clean(d.get("description") or d.get("journey_description") or "")
        r = rec(name, "Venture Catalysts", "Venture Catalysts", description=desc, website=web,
                linkedin_url=norm_linkedin(li), team=founders,
                verticals="; ".join(dict.fromkeys([x for x in [d.get("category") or ""] + list(tags_) if x])),
                location=d.get("location") or "", founded=founded,
                date=f"Venture Catalysts {inv}".strip(), source_url=url)
        if d.get("valuation"):
            r["valuation_band"] = clean(d["valuation"])
        if d.get("investment_status"):
            r["status"] = clean(d["investment_status"])
        if d.get("stage"):
            r["round"] = clean(d["stage"])
        out.append(r)
    out = dedupe(out)
    for r in out:   # duplicate rows merged by dedupe: keep the dated label
        if ";" in r["date"]:
            labs = [x.strip() for x in r["date"].split(";")]
            r["date"] = max(labs, key=len)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- Iterative ----------------
def iterative():
    url = "https://www.iterative.vc/companies"
    s = get(url)
    parts = re.split(r'<h2 class="light-gray-text">(.*?)</h2>', s)
    out = []
    for i in range(1, len(parts), 2):
        batch = clean(re.sub(r"<br\s*/?>", " ", parts[i]))
        for it in re.findall(r'<div role="listitem" class="company-item w-dyn-item">(.*?)</a></div>', parts[i + 1], re.S):
            web = first(r'href="([^"]+)"', it)
            name = txt(first(r'class="company-name">(.*?)</div>', it))
            desc = txt(first(r'class="company-description">(.*?)</div>', it))
            if not name:
                continue
            b2 = first(r"Part of Iterative's ([SW]\d\d) batch", desc)
            label = batch
            if batch.startswith("Scale"):
                label = batch + (f" (orig. {b2})" if b2 else "")
            out.append(rec(name, "Iterative", "Iterative", description=desc,
                           website=web if web.startswith("http") else "",
                           date=label if label.startswith("Iterative") else f"Iterative {label}",
                           source_url=url, location="Southeast Asia"))
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- AppWorks ----------------
AW_CATS = {"ai": "AI", "web3": "Web3", "sea": "SEA", "web12": "Web1/2"}


def appworks():
    url = "https://appworks.tw/investments/"
    s = get(url)
    out = []
    blocks = re.split(r'<div class="vc_row wpb_row vc_inner vc_row-fluid invest-block', s)[1:]
    for b in blocks:
        cls = b.split('"', 1)[0].split()
        name = txt(first(r"<h3>(.*?)</h3>", b))
        if not name:
            continue
        desc_html = first(r'investment-desc"\s*>\s*<div class="wpb_wrapper">(.*?)</div>', b)
        desc = txt(desc_html)
        founders = [txt(x) for x in re.findall(r'<a href="https?://[^"]*linkedin\.com/in/[^"]*"[^>]*>(.*?)</a>', desc_html, re.S)]
        links = dict((txt(t).lower(), u) for u, t in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', first(r'wpb_raw_html"\s*>\s*<div class="wpb_wrapper">((?:(?!</div>).)*Website(?:(?!</div>).)*)</div>', b)))
        web = links.get("website") or first(r'<h3><a href="([^"]+)"', b)
        li = links.get("linkedin", "")
        m = re.search(r"\(AppWorks first funded .*? in (\d{4})(?:[^)]*?(?:during|leading|in) (?:their |its )?([^).]*?(?:Seed|Series|Round|round|Pre-A|Angel)[^).]*))?\.?\)", desc)
        year = m.group(1) if m else ""
        rnd = clean(m.group(2)) if m and m.group(2) else ""
        cats = [AW_CATS[c] for c in cls if c in AW_CATS]
        r = rec(name, "AppWorks", "AppWorks", description=desc, website=web if web.startswith("http") and "appworks.tw" not in web else "",
                linkedin_url=norm_linkedin(li), team=", ".join(dict.fromkeys(f for f in founders if f)),
                verticals="; ".join(cats), round=rnd, date=f"AppWorks first funded {year}".strip() if year else "AppWorks",
                source_url=url)
        if "exit" in cls or "exited" in cls:
            r["status"] = "Exited"
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- SparkLabs (Korea) ----------------
def sparklabs():
    base = "https://sparklabs.co.kr/en/portfolio"
    urls = []
    for pg in range(1, 60):
        s = get(f"{base}?page={pg}")
        found = [f"{base}/{sl}/" for sl in dict.fromkeys(re.findall(r'href="https://sparklabs\.co\.kr/en/portfolio/([^"/?#]+)/(?:\?page=\d+)?"', s))]
        new = [u for u in found if u not in urls]
        if not new:
            break
        urls += new

    def detail(u):
        try:
            h = get(u, timeout=40)
        except Exception:
            return None
        t = strip(re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S))
        body = t.split("본문", 1)[-1].split("Latest Highlights", 1)[0].split("관련자료", 1)[0]
        name = clean(_h.unescape(first(r"<title>(.*?)\s*(?:&gt;|>)\s*All Portfolio", h)))
        name = name or clean(body.split(" ")[0])
        kv = {}
        for k in ("Category", "Status", "Founded", "Location", "CEO", "Batch"):
            v = first(rf"\b{k} (.*?)(?= (?:Category|Status|Founded|Location|CEO|Batch|Related Video)\b|$)", body)
            kv[k] = clean(v)
        desc = clean(first(r"--> (.*?) --> Category", body)) or clean(first(r"^(.*?) Category ", body))
        hrefs = list(dict.fromkeys(re.findall(r'href="(https?://[^"]+)"', h)))
        main = h.split("view_image.php", 1)[-1].split("관련자료", 1)[0]
        ext = [x for x in dict.fromkeys(re.findall(r'href="(https?://[^"]+)"', main)) if "sparklabs" not in x]
        web = next((x for x in ext if not SOCIAL.search(x) and not re.search(r"news|chosun|msn\.com|mt\.co\.kr|hankyung|mk\.co\.kr|venturesquare|platum|zdnet|etnews|yna\.co\.kr|joins|donga|edaily|sedaily|blog\.|platum|youtu|notion|bloter|thebell|businesspost|newsis|naver", x)), "")
        li = next((norm_linkedin(x) for x in ext if "linkedin.com/company" in x), "")
        return {"u": u, "name": name, "desc": desc, "kv": kv, "web": web, "li": li}

    out = []
    for d in pmap(detail, urls, 8):
        if not d or not d["name"]:
            continue
        kv = d["kv"]
        st = kv.get("Status", "")
        b = kv.get("Batch", "")
        r = rec(d["name"], "SparkLabs", "SparkLabs", description=d["desc"], website=d["web"], linkedin_url=d["li"],
                team=(kv.get("CEO") + " (CEO)") if kv.get("CEO") else "", verticals=kv.get("Category", ""),
                location=kv.get("Location", ""), founded=kv.get("Founded", ""),
                status={"IPO": "IPO", "Exit": "Exited", "M&A": "Acquired"}.get(st, st),
                date=f"SparkLabs Batch {b}".strip() if b else "SparkLabs", source_url=d["u"])
        r["batch_number"] = b
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    nums = [int(r["batch_number"]) for r in out if (r.get("batch_number") or "").isdigit()]
    top = max(nums) if nums else None
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and r.get("batch_number") == str(top))
    return finish(out)


# ---------------- Open Network Lab ----------------
ONLAB_PROGRAMS = [("startups-onlab", "Onlab Seed Accelerator"), ("startups-open-innovation", "Onlab Open Innovation"),
                  ("startups-fukuoka", "Onlab Fukuoka"), ("startups-hokkaido", "Onlab Hokkaido"),
                  ("startups-biohealth", "Onlab BioHealth"), ("startups-resitech", "Onlab Resi-Tech")]


def opennetworklab():
    out = []
    for slug, prog in ONLAB_PROGRAMS:
        url = f"https://onlab.jp/en/{slug}/"
        try:
            s = get(url)
        except Exception:
            continue
        for c in re.findall(r'<div class="card-startups">(.*?)</div></div>', s, re.S):
            web = first(r'<a href="([^"]+)"', c).replace("#new_tab", "")
            alt = clean(_h.unescape(first(r'alt="([^"]*)"', c)))
            ps = re.findall(r'<p class="scrl[^"]*">(.*?)</p>', c, re.S)
            desc = txt(ps[0]) if ps else ""
            legal = first(r"\(([^()]*(?:Inc|K\.K\.|Co\.|Ltd|Corporation|LLC|株式会社|GK|G\.K\.)[^()]*)\)\s*$", desc)
            lab = txt(first(r'<p class="exit">(.*?)</p>', c))
            name = first(r"^[“\"]([^”\"]+)[”\"]", desc) or alt or legal
            if not name:
                continue
            r = rec(name, "Open Network Lab", "Open Network Lab", description=desc,
                    website=web if web.startswith("http") and "onlab.jp" not in web else "",
                    date=f"{prog} {lab}".strip(), location="Japan", source_url=url)
            if alt and alt != name:
                r["alt_name"] = alt
            if legal:
                r["legal_name"] = legal
            if re.search(r"exit|ipo|m&a|acquired", lab, re.I):
                r["status"] = lab
            out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:   # newest = highest Seed Accelerator batch number
        r["batch_number"] = first(r"Onlab Seed Accelerator Batch (\d+)", r["date"])
    nums = [int(r["batch_number"]) for r in out if r["batch_number"]]
    top = str(max(nums)) if nums else None
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and r["batch_number"] == top)
    return finish(out)


# ---------------- Brinc ----------------
def brinc():
    url = "https://brinc.io/our-portfolio"
    s = get(url)
    out = []
    for blk in re.split(r'<div role="listitem" class="[^"]*w-dyn-item">', s)[1:]:
        name = txt(first(r'<h1 class="p-company-name">(.*?)</h1>', blk))
        if not name:
            continue
        meta = [txt(x) for x in re.findall(r'<p class="cp-secotor-category-text">(.*?)</p>', blk, re.S)]
        meta = [m for m in meta if m and m != "|"]
        sector, stage = (meta + ["", ""])[:2]
        desc = txt(first(r'<div class="cp-short-desc w-richtext">(.*?)</div>', blk))
        web = first(r'<a href="([^"]+)" class="cp-link"', blk)
        li = first(r'href="(https?://[^"]*linkedin\.com/company/[^"]*)"', blk)
        out.append(rec(name, "Brinc", "Brinc", description=desc, website=web if web.startswith("http") else "",
                       linkedin_url=norm_linkedin(li), verticals=sector,
                       status={"IPO": "IPO", "Acquired": "Acquired"}.get(stage, ""),
                       round="" if stage in ("IPO", "Acquired") else stage, date="Brinc", source_url=url))
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:
        r["batch_date"], r["batch_date_precision"], r["most_recent_batch"] = "", "", False
    return finish(out)


# ---------------- Startmate ----------------
def startmate():
    base = "https://www.startmate.com/portfolio"
    s = get(base)
    keys = list(dict.fromkeys(re.findall(r'href="\?([a-z0-9]+)_page=\d+"', s)))
    slugs = list(dict.fromkeys(re.findall(r'href="/portfolio-companies/([^"]+)"', s)))
    for k in keys:
        for pg in range(2, 80):
            h = get(f"{base}?{k}_page={pg}")
            new = [x for x in dict.fromkeys(re.findall(r'href="/portfolio-companies/([^"]+)"', h)) if x not in slugs]
            slugs += new
            if not re.search(rf'href="\?{k}_page={pg + 1}"', h):
                break

    def detail(sl):
        u = f"https://www.startmate.com/portfolio-companies/{sl}"
        try:
            h = get(u, timeout=40)
        except Exception:
            return None
        name = clean(_h.unescape(first(r"<title>(.*?) \| Startmate", h)))
        t = strip(re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S))
        body = t.split("Back to portfolio", 1)[-1].split("STAY IN THE LOOP", 1)[0]
        desc = clean(first(r"Overview (.*?) Cohort ", body))
        cohort = clean(first(r"Cohort (.*?) Valuation ", body))
        val = clean(first(r"Valuation (.*?) Sector ", body))
        sector = clean(first(r"Sector (.*?) Explore", body))
        main = h.split("Back to portfolio", 1)[-1].split("STAY IN THE LOOP", 1)[0]
        ext = [x for x in dict.fromkeys(re.findall(r'href="(https?://[^"]+)"', main)) if "startmate" not in x]
        web = next((x for x in ext if not SOCIAL.search(x)), "")
        li = next((norm_linkedin(x) for x in ext if "linkedin.com/company" in x), "")
        return dict(u=u, name=name, desc=desc, cohort=cohort, val=val, sector=sector, web=web, li=li)

    out = []
    for d in pmap(detail, slugs, 10):
        if not d or not d["name"]:
            continue
        val = d["val"]
        status = val if val in ("Active", "Inactive", "Acquired") else ""
        r = rec(d["name"], "Startmate", "Startmate", description=d["desc"], website=d["web"], linkedin_url=d["li"],
                verticals=d["sector"], status=status, date=f"Startmate {d['cohort']}".strip(),
                location="Australia/New Zealand", source_url=d["u"])
        if val and not status:
            r["valuation_band"] = val
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    # cohort labels: W26/S26 style or 2016 / SYD19 / MEL20 / NZ20 -> year
    for r in out:
        c = r["date"].replace("Startmate ", "")
        m = re.search(r"(?:^|[A-Z])(\d\d)$", c)
        y = c if re.fullmatch(r"20\d\d", c) else (f"20{m.group(1)}" if m else "")
        r["batch_date"] = f"{y}-01-01" if y else ""
        r["batch_date_precision"] = "year" if y else ""
    newest = max((r["batch_date"] for r in out if r["batch_date"]), default="")
    order = {"W": 2, "S": 1}   # Startmate Winter cohort (mid-year) follows Summer (start of year)
    newest_labels = [r["date"] for r in out if r["batch_date"] == newest]
    top = max(newest_labels, key=lambda l: order.get(l.replace("Startmate ", "")[:1], 0), default="")
    for r in out:
        r["most_recent_batch"] = bool(top and r["date"] == top)
    return finish(out)


# ---------------- Cicada Innovations ----------------
CIC_FILTER = {"advanced-industry-manufacturing": "Advanced Industry & Manufacturing", "climate-energy": "Climate + Energy",
              "food-agriculture": "Food + Agriculture", "health-life-sciences": "Health + Life Sciences",
              "space-aeronautics": "Space & Aeronautics"}


def cicadainnovations():
    url = "https://www.cicadainnovations.com/incubator/residents"
    s = get(url)
    out = []
    for li in re.findall(r"<li\s+x-show=\"([^\"]*)\"[^>]*>(.*?)</li>", s, re.S):
        xs, body = li
        cats = [CIC_FILTER.get(c, c) for c in re.findall(r"filterResidents === '([^']+)'", xs) if c != "all"]
        a = re.search(r'<h4>\s*(?:<a href="([^"]*)"[^>]*>)?(.*?)(?:</a>)?\s*</h4>', body, re.S)
        if not a:
            continue
        name, web = txt(a.group(2)), a.group(1) or ""
        desc = txt(first(r"<p[^>]*>(.*?)</p>", body))
        out.append(rec(name, "Cicada Innovations", "Cicada Innovations", description=desc,
                       website=web if web.startswith("http") else "", verticals="; ".join(dict.fromkeys(cats)),
                       date="Cicada Innovations current resident", location="Sydney, Australia", source_url=url))
    alum = s.split(">Alumni</h2>", 1)[-1].split("</ul>", 1)[0] if ">Alumni</h2>" in s else ""
    for n in re.findall(r"<li[^>]*>\s*(.*?)\s*</li>", alum, re.S):
        n = txt(n)
        if n:
            out.append(rec(n, "Cicada Innovations", "Cicada Innovations", date="Cicada Innovations alumni",
                           location="Australia", source_url=url))
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = "current resident" in r["date"]
    return finish(out)


# ---------------- Creative HQ (Lightning Lab) ----------------
def creativehqlightninglab():
    url = "https://creativehq.co.nz/build-for-founders/startup-alumni/"
    s = get(url)
    out = []
    for it in re.findall(r'<div class="dw-logo-stack__item">(.*?)</a>\s*</div>', s, re.S):
        href = first(r'href="([^"]*)"', it)
        name = clean(_h.unescape(first(r'aria-label="([^"]*)"', it) or first(r'alt="([^"]*)"', it)))
        if not name:
            continue
        web = href if href.startswith("http") and "creativehq.co.nz" not in href else ""
        r = rec(name, "Creative HQ", "Creative HQ (Lightning Lab)", website=web, date="Creative HQ startup alumni",
                location="New Zealand", source_url=url)
        if web and "linkedin.com/company" in href:
            r["linkedin_url"] = norm_linkedin(href)
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:
        r["batch_date"], r["batch_date_precision"], r["most_recent_batch"] = "", "", False
    return finish(out)


FUNCS = {"rockstart": rockstart, "venturecatalysts": venturecatalysts, "iterative": iterative,
         "appworks": appworks, "sparklabs": sparklabs, "opennetworklab": opennetworklab, "brinc": brinc,
         "startmate": startmate, "cicadainnovations": cicadainnovations,
         "creativehqlightninglab": creativehqlightninglab}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct10.{FUNCS[slug].__name__}"})
