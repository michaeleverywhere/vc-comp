"""Scrapers for the 2026-10-12 Daily accelerator batch (final 8 queued Canada programs).
Usage: python batch_oct12.py [slug...]

Sources: each accelerator's own public portfolio / directory pages (or the JSON/HTML
those pages load), plus company websites for blank descriptions. Never Crunchbase /
LinkedIn / PitchBook. Tags are keyword-only (automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import requests

import batch_oct8
import cdp
from batch_oct8 import finish, rec, strip, year_batch
from common import BANNED, UA, _desc_from_html, clean, dedupe, enrich_from_sites, norm_linkedin, norm_name, save, LI_RE

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
                                "(KHTML, like Gecko) Version/17.5 Safari/605.1.15"})

batch_oct8.ES_LABELS.update({
    "edtech": "Consumer", "sports tech": "Consumer", "sportstech": "Consumer",
    "arts & entertainment": "Gaming / Media / Entertainment", "b2c": "Consumer", "b2b": "Dev Tools / Cloud",
    "saas": "Dev Tools / Cloud", "data & analytics": "Data & Analytics", "ai": "Data & Analytics",
    "ai / ml": "Data & Analytics", "ai/ml": "Data & Analytics", "fintech": "FinTech / Insurance",
    "healthtech": "Health", "health care": "Health", "healthcare": "Health", "biotech": "BioTech",
    "cleantech": "Climate / Sustainability", "climate": "Climate / Sustainability",
    "agritech": "Climate / Sustainability", "agrifood": "Climate / Sustainability",
    "cybersecurity": "Cybersecurity", "proptech": "PropTech", "real estate": "PropTech",
    "logistics": "Logistics / Supply Chain", "supply chain": "Logistics / Supply Chain",
    "robotics": "Deeptech / Robotics / AR/VR", "deeptech": "Deeptech / Robotics / AR/VR",
    "hardware": "Deeptech / Robotics / AR/VR", "space": "Deeptech / Robotics / AR/VR",
    "manufacturing": "Deeptech / Robotics / AR/VR", "industrial": "Deeptech / Robotics / AR/VR",
    "medtech": "Health", "medical devices": "Health", "digital media and ict": "Dev Tools / Cloud",
    "financial services": "FinTech / Insurance", "education": "Consumer", "consumer": "Consumer",
    "social innovation": "RegTech/Gov/Legal", "high tech": "Dev Tools / Cloud",
    "advanced therapies": "BioTech", "artificial intelligence": "Data & Analytics",
    "biomedical engineering": "Health", "blockchain": "Web3 / Crypto", "web3": "Web3 / Crypto",
    "cancer": "Health", "carbon removal": "Climate / Sustainability", "commerce": "Consumer",
    "computational health": "Health", "compute": "Dev Tools / Cloud", "defence": "Deeptech / Robotics / AR/VR",
    "digital society": "RegTech/Gov/Legal", "energy": "Climate / Sustainability",
    "health & wellness": "Health", "healthcare delivery": "Health", "healthcare robotics": "Health",
    "matter": "Deeptech / Robotics / AR/VR", "minerals": "Climate / Sustainability",
    "neuro": "Health", "next gen computing": "Dev Tools / Cloud", "oceans": "Climate / Sustainability",
    "prime": "Dev Tools / Cloud", "quantum": "Deeptech / Robotics / AR/VR",
    "recovery": "Health", "risk": "FinTech / Insurance",
    "agriculture": "Climate / Sustainability", "food and beverage": "CPG",
    "wellness and nutrition": "Health", "life sciences and advanced health": "Health",
    "advanced materials and manufacturing": "Deeptech / Robotics / AR/VR",
    "materials and chemicals": "Deeptech / Robotics / AR/VR",
    "pharmaceuticals and drugs": "BioTech", "tourism and culture": "Consumer",
    "manufactured goods": "CPG", "govtech": "RegTech/Gov/Legal",
    "data analytics": "Data & Analytics", "software": "Dev Tools / Cloud",
})


def get(url, **kw):
    r = S.get(url, timeout=kw.pop("timeout", 60), **kw)
    r.raise_for_status()
    return r.text


def pmap(fn, xs, n=16):
    with ThreadPoolExecutor(n) as ex:
        return list(ex.map(fn, xs))


def txt(s):
    return strip(s or "")


def first(rx, s, flags=re.S, g=1):
    m = re.search(rx, s, flags)
    return m.group(g) if m else ""


def no_batch(out):
    for r in out:
        r["batch_date"], r["batch_date_precision"], r["most_recent_batch"] = "", "", False
    return out


def site_meta(url, timeout=15):
    if not url or BANNED.search(url):
        return "", "", ""
    try:
        r = requests.get(url if url.startswith("http") else "https://" + url, headers=UA, timeout=timeout)
        if r.status_code >= 400 or BANNED.search(r.url):
            return "", "", ""
        s = r.text[:300000]
    except Exception:
        return "", "", ""
    name = clean(_h.unescape(first(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']{2,60})["\']', s, re.I)
                             or first(r'<meta[^>]+content=["\']([^"\']{2,60})["\'][^>]+property=["\']og:site_name', s, re.I)))
    if not name:
        t = clean(_h.unescape(first(r"<title[^>]*>(.*?)</title>", s, re.I | re.S)))
        name = clean(re.split(r"\s+[|\-–—:·•]\s+", t)[0]) if t else ""
    if re.search(r"home|welcome|just a moment|attention required|403|404|not found|coming soon|index of", name, re.I):
        name = ""
    d = _desc_from_html(s, None)
    m = LI_RE.search(s)
    return name[:60], d, norm_linkedin(m.group(0)) if m else ""


# ---------------- Creative Destruction Lab ----------------
def _cdl_detail(item):
    url, name, stream = item["url"], item["name"], item["stream"]
    try:
        s = get(url, timeout=40)
    except Exception:
        return rec(name, "Creative Destruction Lab", "Creative Destruction Lab", verticals=stream,
                   date="Creative Destruction Lab", location="Canada/Global", source_url=url)
    desc = txt(first(r'class="[^"]*company-bio[^"]*"[^>]*>(.*?)</div>', s))
    if desc.lower().startswith(name.lower()):
        desc = desc[len(name):].strip()
    web = first(r'class="btn company-website-link"[^>]+href="(https?://[^"]+)"', s)
    site = clean(first(r"Site:\s*</strong>\s*([^<]+)", s))
    cohort = clean(first(r"Cohort Year:\s*</strong>\s*([^<]+)", s))
    stream2 = clean(first(r"Stream:\s*</strong>\s*([^<]+)", s)) or stream
    date = f"Creative Destruction Lab {cohort}".strip() if cohort else "Creative Destruction Lab"
    loc = site or "Canada/Global"
    r = rec(name, "Creative Destruction Lab", "Creative Destruction Lab", description=desc, website=web,
            verticals=stream2, date=date, location=loc, source_url=url)
    if site:
        r["cdl_site"] = site
    if cohort:
        r["cohort_year"] = cohort
    return r


def creativedestructionlab():
    s = get("https://creativedestructionlab.com/companies/")
    items = []
    for url, body in re.findall(
            r'<a href="(https://creativedestructionlab\.com/companies/[a-z0-9\-]+/)"[^>]*>\s*<figure>.*?</figure>\s*(.*?)</a>',
            s, re.S):
        name = txt(first(r'class="companybio-location">(.*?)</p>', body)) or url.rstrip("/").split("/")[-1].replace("-", " ").title()
        stream = txt(first(r'class="companybio-stream">(.*?)</p>', body))
        if name:
            items.append(dict(url=url, name=name, stream=stream))
    # dedupe by slug
    seen, uniq = set(), []
    for it in items:
        slug = it["url"].rstrip("/").split("/")[-1]
        if slug in seen:
            continue
        seen.add(slug)
        uniq.append(it)
    print(f"[cdl] listing {len(uniq)} companies; fetching details...")
    out = pmap(_cdl_detail, uniq, 20)
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out, rx=r"(20\d\d)/\d\d")  # cohort like 2022/23 -> use 2022
    # Better: extract start year from cohort_year field
    ys = []
    for r in out:
        m = re.search(r"(20\d\d)", r.get("cohort_year") or r.get("date") or "")
        y = m.group(1) if m else ""
        r["batch_date"] = f"{y}-01-01" if y else ""
        r["batch_date_precision"] = "year" if y else ""
        if y:
            ys.append(y)
    newest = max(ys) if ys else None
    for r in out:
        r["most_recent_batch"] = bool(newest and r["batch_date"].startswith(newest))
    return finish(out)


# ---------------- DMZ ----------------
def dmz():
    def parse(html):
        rows = []
        for card in re.split(r'class="startup-card w-dyn-item"', html)[1:]:
            name = txt(first(r'fs-list-field="company"[^>]*>(.*?)</', card))
            if not name:
                continue
            inds = [txt(x) for x in re.findall(r'fs-list-field="industry"[^>]*>(.*?)</', card) if txt(x)]
            models = [txt(x) for x in re.findall(r'fs-list-field="business model"[^>]*>(.*?)</', card) if txt(x)]
            status = txt(first(r'fs-list-field="status"[^>]*>(.*?)</', card))
            m = re.search(r'<div class="row2-grid-link"><p>(.*?)</p>\s*<a[^>]+href="(https?://[^"]+)"[^>]*>Visit Company', card, re.S)
            desc, web = (txt(m.group(1)), m.group(2)) if m else ("", "")
            loc = txt(first(r'class="startup-location[^"]*"[^>]*>.*?<p class="text-size-small">(.*?)</p>', card))
            verts = "; ".join(inds + models)
            date = f"DMZ {status}".strip() if status else "DMZ startup directory"
            r = rec(name, "DMZ", "DMZ", description=desc, website=web, verticals=verts, date=date,
                    location=loc or "Toronto, Canada", source_url="https://dmz.torontomu.ca/startup-directory")
            if status:
                r["status"] = status
            rows.append(r)
        return rows

    out = []
    for pg in range(1, 20):
        url = "https://dmz.torontomu.ca/startup-directory" if pg == 1 else f"https://dmz.torontomu.ca/startup-directory?542e3ac2_page={pg}"
        html = get(url)
        rows = parse(html)
        if not rows:
            break
        if pg > 1 and out and rows[0]["name"] == out[0]["name"]:
            break
        out.extend(rows)
        m = re.search(r"Page (\d+) of (\d+)", html)
        if m and pg >= int(m.group(2)):
            break
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- Velocity ----------------
def _vel_detail(path):
    url = "https://www.velocityincubator.com" + path
    try:
        s = get(url, timeout=40)
    except Exception:
        return None
    name = txt(first(r"<h1[^>]*>(.*?)</h1>", s))
    desc = txt(first(r'class="text_company_description"[^>]*>(.*?)</div>', s))
    web = ""
    for href, lab in re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', s, re.S):
        if re.search(r"visit company", txt(lab), re.I) or "visit company" in (href + lab).lower():
            if "velocity" not in href.lower() and "linkedin" not in href.lower():
                web = href
                break
    if not web:
        webs = [u for u in re.findall(r'href="(https?://[^"]+)"', s)
                if "velocity" not in u.lower() and not re.search(r"webflow|google|facebook|twitter|linkedin|youtube|instagram|cdn\.|fonts\.", u, re.I)]
        web = webs[0] if webs else ""
    founders = [txt(x) for x in re.findall(r'class="[^"]*founder[^"]*"[^>]*>(.*?)</div>', s) if txt(x) and txt(x).lower() != "founders"]
    sector = txt(first(r"Sector:\s*</div>\s*<div[^>]*>(.*?)</div>", s)) or txt(first(r'Sector</div>\s*<div[^>]*>(.*?)</div>', s))
    # parse details block
    details = dict(re.findall(r"(Location|Status|Sector|Year joined):\s*</div>\s*<div[^>]*>(.*?)</div>", s))
    if not details:
        # alternate layout from cleaned text patterns
        t = txt(s)
        sector = sector or first(r"Sector:\s*([^\n]+)", t)
        year = first(r"Year joined:\s*(\d{4})", t)
        status = first(r"Status:\s*(\w+)", t)
        loc = first(r"Location:\s*([^S]+?)(?:Status|$)", t)
    else:
        year = txt(details.get("Year joined", ""))
        status = txt(details.get("Status", ""))
        loc = txt(details.get("Location", ""))
        sector = sector or txt(details.get("Sector", ""))
    tags = [txt(x) for x in re.findall(r'class="[^"]*tag[^"]*"[^>]*>(.*?)</', s) if txt(x)]
    verts = "; ".join([x for x in [sector] + tags if x])
    date = f"Velocity {year}".strip() if year else "Velocity Incubator"
    r = rec(name or path.split("/")[-1].replace("-", " ").title(), "Velocity", "Velocity",
            description=desc, website=web, team=", ".join(founders), verticals=verts, date=date,
            location=loc or "Waterloo, Canada", source_url=url)
    if status:
        r["status"] = status
    if year:
        r["year_joined"] = year
    return r


def velocityuniversityofwaterloo():
    s = get("https://www.velocityincubator.com/companies")
    # listing cards
    cards = []
    for m in re.finditer(
            r'fs-cmsfilter-field="company"[^>]*>(.*?)</div>.*?fs-cmsfilter-field="Status"[^>]*>(.*?)</div>.*?fs-cmsfilter-field="year"[^>]*>(.*?)</div>\s*<a[^>]+href="(/company/[^"]+)"',
            s, re.S):
        cards.append(dict(name=txt(m.group(1)), status=txt(m.group(2)), year=txt(m.group(3)), path=m.group(4)))
    # also grab sector from nearby
    sectors = {}
    for m in re.finditer(r'fs-cmsfilter-field="company"[^>]*>(.*?)</div>.*?fs-cmsfilter-field="Sector"[^>]*>(.*?)</div>', s, re.S):
        sectors[txt(m.group(1))] = txt(m.group(2))
    paths = list(dict.fromkeys(c["path"] for c in cards))
    print(f"[velocity] listing {len(paths)} companies; fetching details...")
    details = [d for d in pmap(_vel_detail, paths, 12) if d]
    by_path = {d["source_url"].split("/company/")[-1].strip("/"): d for d in details}
    out = []
    for c in cards:
        slug = c["path"].strip("/").split("/")[-1]
        r = by_path.get(slug)
        if not r:
            r = rec(c["name"], "Velocity", "Velocity", date=f"Velocity {c['year']}".strip(),
                    location="Waterloo, Canada", source_url="https://www.velocityincubator.com" + c["path"],
                    verticals=sectors.get(c["name"], ""))
            if c["status"]:
                r["status"] = c["status"]
        else:
            if not r.get("verticals") and sectors.get(c["name"]):
                r["verticals"] = sectors[c["name"]]
            if c["status"] and not r.get("status"):
                r["status"] = c["status"]
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- Next Canada ----------------
def nextcanada():
    s = get("https://www.nextcanada.com/directory/ventures/")
    # may redirect to directory.nextcanada.com
    out = []
    for v in re.findall(r'<section class="venture">(.*?)</section>', s, re.S):
        name = txt(first(r'<h1 class="name">(.*?)</h1>', v))
        if not name:
            continue
        desc = txt(first(r'<p class="description">(.*?)</p>', v))
        web = first(r'Website:</h2>.*?<a href="([^"]+)"', v)
        cohort = txt(first(r"Cohort:</h2>(.*?)</div>\s*</div>", v))
        founders = [txt(x) for x in re.findall(r'<a class="name"[^>]*>(.*?)<svg', v)]
        ind_sec = first(r"Industries:</h2>(.*?)</div>\s*</div>", v)
        industries = [txt(x) for x in re.findall(r">([^<]+)</a>", ind_sec)] if ind_sec else []
        tech_sec = first(r"Technologies:</h2>(.*?)</div>\s*</div>", v)
        techs = [txt(x) for x in re.findall(r">([^<]+)</a>", tech_sec)] if tech_sec else []
        verts = "; ".join([x for x in industries + techs if x])
        r = rec(name, "Next Canada", "Next Canada", description=desc, website=web,
                team=", ".join(founders), verticals=verts,
                date=f"Next Canada {cohort}".strip() if cohort else "Next Canada venture directory",
                location="Canada", source_url="https://directory.nextcanada.com/directory/ventures/")
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- Centech ----------------
def centech():
    try:
        s = get("https://centech.co/startups-centech/")
        if "Infirnaa" not in s and s.count("<h2") < 5:
            raise ValueError("browser check / thin")
    except Exception:
        s = cdp.render("https://centech.co/startups-centech/", settle=12, port=9411, prof="/tmp/cdp_centech12")
    out = []
    # Current featured cohort cards: h2 name then about section
    # Split by company headings that precede "À propos"
    blocks = re.split(r'<h2[^>]*>', s)[1:]
    for b in blocks:
        name = txt(first(r"^(.*?)</h2>", b))
        if not name or re.search(r"startups|s.abonner|infolettre|newsletter", name, re.I):
            continue
        season = txt(first(r"(Été|Hiver|Automne|Printemps|Summer|Winter|Fall|Spring)\s*20\d\d", b))
        about = txt(first(r"À propos de l.entreprise\s*(.*?)(?:En savoir|Contact|Été|Hiver|$)", b, re.I))
        if not about:
            about = txt(first(r"About(?: the)?(?: company)?\s*(.*?)(?:Learn more|Contact|$)", b, re.I))
        # website if present
        web = ""
        for href in re.findall(r'href="(https?://[^"]+)"', b[:3000]):
            if "centech" not in href.lower() and not re.search(r"facebook|twitter|linkedin|instagram|youtube|google|cdn\.|wp-", href, re.I):
                web = href
                break
        date = f"Centech {season}".strip() if season else "Centech startups (featured cohort)"
        out.append(rec(name, "Centech", "Centech", description=about, website=web, date=date,
                       location="Montreal, Canada", source_url="https://centech.co/startups-centech/"))
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- Accelerator Centre ----------------
def acceleratorcentre():
    try:
        s = get("https://www.acceleratorcentre.com/our-startups/")
        if s.count('alt="Visit ') < 50:
            raise ValueError("thin")
    except Exception:
        s = cdp.render("https://www.acceleratorcentre.com/our-startups/", settle=14, port=9412, prof="/tmp/cdp_ac12b")
    # alumni / roster: <a href="URL"><img alt="Visit NAME Website"
    pairs = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*<img[^>]+alt="Visit ([^"]+) Website"', s)
    by_name = {}
    for web, name in pairs:
        name, web = clean(name), web.strip()
        if not name or BANNED.search(web or ""):
            continue
        k = norm_name(name)
        if k not in by_name:
            by_name[k] = rec(name, "Accelerator Centre", "Accelerator Centre", website=web,
                             date="Accelerator Centre alumni/roster", location="Waterloo, Canada",
                             source_url="https://www.acceleratorcentre.com/our-startups/")
        else:
            # prefer website whose domain matches the company name
            cur = by_name[k]
            dom = urlparse(web if web.startswith("http") else "https://" + web).netloc.lower()
            if norm_name(name)[:4] in norm_name(dom) and norm_name(name)[:4] not in norm_name(cur.get("website") or ""):
                cur["website"] = web
    # showcase descriptions
    for name, desc, web in re.findall(
            r'<h2[^>]*class="[^"]*pretty[^"]*"[^>]*>(.*?)</h2>\s*<p[^>]*>(.*?)</p>\s*<a[^>]+href="(https?://[^"]+)"',
            s, re.S):
        n, d = txt(name), txt(desc)
        k = norm_name(n)
        if k in by_name:
            if d and not by_name[k].get("description"):
                by_name[k]["description"] = d
            if web and not by_name[k].get("website"):
                by_name[k]["website"] = web
        else:
            by_name[k] = rec(n, "Accelerator Centre", "Accelerator Centre", description=d, website=web,
                             date="Accelerator Centre founders showcase", location="Waterloo, Canada",
                             source_url="https://www.acceleratorcentre.com/our-startups/")
    out = list(by_name.values())
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- District 3 ----------------
def district3():
    def parse(html):
        rows = []
        for part in re.split(r'class="startup_grid-card"', html)[1:]:
            name = txt(first(r'fs-cmsfilter-field="name"[^>]*>(.*?)</div>', part))
            if not name:
                continue
            desc = txt(first(r'fs-cmsfilter-field="description"[^>]*>(.*?)</div>', part))
            stream = txt(first(r'fs-cmsfilter-field="stream"[^>]*>(.*?)</div>', part))
            web = first(r'<a href="(https?://[^"]+)"[^>]*class="button is-link', part)
            if not web:
                for href in re.findall(r'<a href="(https?://[^"]+)"', part):
                    if "district3" not in href.lower():
                        web = href
                        break
            rows.append(rec(name, "District 3", "District 3", description=desc, website=web,
                            verticals=stream, date="District 3 startup directory",
                            location="Montreal, Canada", source_url="https://www.district3.co/startups"))
        return rows

    out = []
    for pg in range(1, 15):
        url = "https://www.district3.co/startups" if pg == 1 else f"https://www.district3.co/startups?37e06a8e_page={pg}"
        html = get(url)
        rows = parse(html)
        if not rows:
            break
        if pg > 1 and out and rows[0]["name"] == out[0]["name"]:
            break
        out.extend(rows)
        m = re.search(r"Page (\d+) of (\d+)", html)
        if m and pg >= int(m.group(2)):
            break
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


FUNCS = {
    "creativedestructionlab": creativedestructionlab,
    "dmz": dmz,
    "velocityuniversityofwaterloo": velocityuniversityofwaterloo,
    "nextcanada": nextcanada,
    "centech": centech,
    "acceleratorcentre": acceleratorcentre,
    "district3": district3,
}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        print(f"=== {slug} ===")
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct12.{FUNCS[slug].__name__}"})
