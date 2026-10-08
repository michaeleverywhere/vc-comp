"""Scrapers for the 2026-10-08 Daily-10 accelerator batch (catch-up run).
Usage: python batch_oct8.py [slug...]

Sources: each accelerator's own public portfolio page (or the JSON API that page
itself calls) plus the company's own website for blank descriptions. Never
Crunchbase / LinkedIn / PitchBook. Tags are keyword-only (automation/tags.py).
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

from common import UA, clean, dedupe, enrich_from_sites, norm_linkedin, save, tag

S = requests.Session()
S.headers.update(UA)


def get(url, **kw):
    r = S.get(url, timeout=kw.pop("timeout", 60), **kw)
    r.raise_for_status()
    return r.text


def strip(s):
    return clean(_h.unescape(re.sub(r"<[^>]+>", " ", s or "")))


def rec(name, acc, source, **kw):
    r = {"name": clean(_h.unescape(name)), "description": "", "website": "", "team": "",
         "round": "", "amount_raised": "", "date": "", "verticals": "", "investors": acc,
         "source": source, "everywhere_tags": [], "source_url": "", "location": "",
         "linkedin_url": ""}
    for k, v in kw.items():
        r[k] = clean(v) if isinstance(v, str) else v
    if r["website"] and re.search(r"linkedin\.com/company", r["website"], re.I):
        r["linkedin_url"] = r["linkedin_url"] or norm_linkedin(r["website"])
        r["website"] = ""
    return r


def fix_moji(t):
    if t and re.search(r"Ã.|â€", t):
        try:
            return t.encode("latin-1").decode("utf-8")
        except Exception:
            return t
    return t


# Accelerator-published Spanish sector labels (Lanzadera) -> Everywhere tags
ES_LABELS = {"alimentación": "CPG", "blockchain/cripto": "Web3 / Crypto",
             "construcciones e infraestructuras": "PropTech", "deeptech": "Deeptech / Robotics / AR/VR",
             "e-commerce": "Consumer", "educación": "Consumer", "energía": "Climate / Sustainability",
             "finanzas y seguros": "FinTech / Insurance", "gaming/esports": "Gaming / Media / Entertainment",
             "horeca": "Consumer", "moda": "Consumer", "movilidad": "Transportation / Mobility",
             "realidad virtual": "Deeptech / Robotics / AR/VR", "retail": "Consumer",
             "salud y bienestar": "Health", "sostenibilidad": "Climate / Sustainability",
             "turismo y viajes": "Consumer"}


def finish(out, labels_key="verticals"):
    for r in out:
        r["name"] = clean(r["name"].replace("\u200b", ""))
        r["description"] = fix_moji(r.get("description") or "")
        if r.get("team", "").startswith("No Information"):
            r["team"] = ""
        labels = [x.strip() for x in re.split(r";|,", r.get(labels_key) or "") if x.strip()]
        t = tag(r["name"], r["description"], labels)
        for l in labels:
            m = ES_LABELS.get(l.lower())
            if m and m not in t:
                t = [m] + t
        r["everywhere_tags"] = t[:4]
    return out


def year_batch(out, rx=r"\b(20\d\d|19\d\d)\b"):
    """batch_date (YYYY-01-01, precision year) from the published batch label;
    most_recent_batch = company is in the newest label year."""
    ys = []
    for r in out:
        m = re.findall(rx, r.get("date") or "")
        y = max(m) if m else ""
        r["batch_date"] = f"{y}-01-01" if y else ""
        r["batch_date_precision"] = "year" if y else ""
        if y:
            ys.append(y)
    newest = max(ys) if ys else None
    for r in out:
        r["most_recent_batch"] = bool(newest and r["batch_date"].startswith(newest))
    return out


# ---------------- STATION F ----------------
def stationf():
    url = "https://stationf.co/startups"
    s = get(url)
    sec = s.split("Proudly built at STATION F", 1)[1].split("Future 40 is Station F", 1)[0]
    out = []
    for blk in sec.split('data-slot="item" ')[1:]:
        name = strip((re.search(r'data-slot="item-title"[^>]*><span>(.*?)</span>', blk, re.S) or [0, ""])[1])
        if not name:
            continue
        backed = strip((re.search(r'<p class="text-muted-foreground line-clamp-none text-xs">(.*?)</p>', blk, re.S) or [0, ""])[1])
        desc = strip((re.search(r'data-slot="item-description"[^>]*>(.*?)</p>', blk, re.S) or [0, ""])[1])
        tail = strip((re.search(r'</svg>(.*?)</p>', blk, re.S) or [0, ""])[1])
        f40 = "Future 40" in blk
        amt = rnd = ""
        m = re.match(r"Raised ([€$£][\d.,]+[MBK]?)\s*(.*)", tail)
        if m:
            amt = m.group(1)
            rnd = re.sub(r"\s*round$", "", m.group(2)).strip()
        inv = "STATION F"
        if backed.startswith("Backed by "):
            inv += "; " + backed[len("Backed by "):]
        d = desc + (f" ({tail})" if tail and not m else "")
        out.append(rec(name, inv, "STATION F", description=d, amount_raised=amt,
                       round=rnd, date="STATION F Future 40" if f40 else "STATION F",
                       location="Paris, France", source_url=url))
    return finish(out)


# ---------------- Wayra (Telefonica) ----------------
def wayra():
    page = get("https://startups.telefonica.com/")
    # code -> label map comes from the page's own filter <option>s
    labels = {}
    for code, lab in re.findall(r'<option value="([^"]+)" id="[^"]+">([^<]+)', page):
        labels[code] = clean(_h.unescape(lab))
    if not labels:  # options are rendered client-side; fall back to Chrome-rendered copy
        import os
        p = os.environ.get("WAYRA_DOM")
        if p:
            for code, lab in re.findall(r'<option value="([^"]+)" id="[^"]+">([^<]+)', open(p).read()):
                labels[code] = clean(_h.unescape(lab))
    items = {}
    for pg in range(0, 20):
        d = S.get(f"https://startups.telefonica.com/api/v1/projects/public?size=100&page={pg}", timeout=60).json()
        if not d["items"]:
            break
        for it in d["items"]:
            items[it["id"]] = it
    HUB, IND, CAT = "9YeO8XkBQs9g7bjVObWB", "9oeO8XkBQs9g7bjVObWC", "U-eO8XkBgfCEVrv0OTiz"
    out = []
    for it in items.values():
        a = it.get("answers") or {}
        lab = lambda q: [labels.get(c.strip(), "") for c in (a.get(q) or "").split(",") if c.strip()]
        hubs = [x for x in lab(HUB) if x]
        inds = [x for x in lab(IND) if x]
        cats = [x for x in lab(CAT) if x]
        desc = clean(it.get("projectDescription") or "")
        hub_s = "; ".join(hubs)
        out.append(rec(it["project_name"], "Wayra (Telefonica)" + (f" - {hub_s}" if hub_s else ""),
                       "Wayra", description=desc, verticals="; ".join(inds),
                       date=hub_s or "Wayra", status="; ".join(cats),
                       source_url="https://startups.telefonica.com/"))
    return finish(dedupe(out))


# ---------------- Startupbootcamp ----------------
def startupbootcamp():
    url = "https://startupbootcamp.org/startups/portfolio-companies"
    s = get(url)
    cards = re.split(r'class="alumnicard-container w-dyn-item"', s)[1:]
    out = []
    for c in cards:
        href = (re.search(r'href="(/startup/[^"]+)"', c) or [0, ""])[1]
        prog = strip((re.search(r'tag-visible accelerator">(.*?)</h6>', c) or [0, ""])[1])
        name = strip((re.search(r'class="program-name">(.*?)</h5>', c) or [0, ""])[1])
        loc = strip((re.search(r'company-location">(.*?)</h6>', c) or [0, ""])[1])
        desc = strip((re.search(r'class="paragraph-4">(.*?)</p>', c, re.S) or [0, ""])[1])
        if not name:
            continue
        out.append(rec(name, "Startupbootcamp", "Startupbootcamp", description=desc,
                       date=f"Startupbootcamp {prog}".strip(), verticals=prog, location=loc,
                       source_url="https://startupbootcamp.org" + href if href else url))

    def detail(r):
        if "/startup/" not in r["source_url"]:
            return r
        try:
            h = get(r["source_url"], timeout=30)
        except Exception:
            return r
        w = re.search(r'Website</[^>]+>\s*<[^>]*>\s*(?:<[^>]*>\s*)*(https?://[^<\s]+)', h)
        if not w:
            t = strip(h)
            w = re.search(r"Website (https?://\S+)", t)
        if w:
            r["website"] = w.group(1).strip()
        t = strip(h)
        m = re.search(r"Management Team (.*?) (?:LEARN MORE|About )", t)
        if m:
            r["team"] = m.group(1).strip()
        return r

    with ThreadPoolExecutor(12) as ex:
        out = list(ex.map(detail, out))
    for r in out:
        if r["website"] and re.search(r"linkedin\.com/company", r["website"], re.I):
            r["linkedin_url"] = norm_linkedin(r["website"]); r["website"] = ""
    enrich_from_sites(out)
    return finish(dedupe(out))


# ---------------- Lanzadera ----------------
def lanzadera():
    tax = {}
    for t in ("batch", "sectores", "modelos"):
        tax[t] = {x["id"]: _h.unescape(x["name"]) for x in
                  S.get(f"https://lanzadera.es/wp-json/wp/v2/{t}?per_page=100", timeout=60).json()}
    posts = []
    for pg in range(1, 20):
        r = S.get(f"https://lanzadera.es/wp-json/wp/v2/startups?per_page=100&page={pg}", timeout=60)
        if r.status_code != 200 or not r.json():
            break
        posts += r.json()
    out = []
    for p in posts:
        batch = "; ".join(tax["batch"].get(i, "") for i in p.get("batch", []))
        sect = "; ".join(x for x in (tax["sectores"].get(i, "") for i in p.get("sectores", [])) if x != "Por definir")
        mod = "; ".join(tax["modelos"].get(i, "").replace(" (obsoleto)", "") for i in p.get("modelos", []))
        exc = strip(p.get("excerpt", {}).get("rendered", ""))
        body = strip(p.get("content", {}).get("rendered", ""))
        out.append(rec(p["title"]["rendered"], "Lanzadera", "Lanzadera",
                       description=exc or body[:400], verticals="; ".join(x for x in (sect, mod) if x),
                       date=f"Lanzadera {batch}".strip(), source_url=p["link"],
                       location="Valencia, Spain (Lanzadera)"))

    def detail(r):
        try:
            h = get(r["source_url"], timeout=30)
        except Exception:
            return r
        main = h.split("Skip to content", 1)[-1]
        m = re.search(r'<a[^>]+href="(https?://(?!lanzadera\.es|marinadeempresas|[a-z.]*linkedin|[a-z.]*facebook|[a-z.]*instagram|[a-z.]*twitter|[a-z.]*youtube|www\.google|edem)[^"]+)"[^>]*>\s*(?:<[^>]+>\s*)*https?://', main)
        if m:
            r["website"] = m.group(1)
        t = strip(main)
        f = re.search(r"Fundadores (.*?) Nº1", t)
        if f:
            r["team"] = f.group(1).strip()
        return r

    with ThreadPoolExecutor(12) as ex:
        out = list(ex.map(detail, out))
    for r in out:  # batch label like SEPT26 / MAR25 / ENE23
        m = re.search(r"(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEPT|OCT|NOV|DIC)(\d\d)", r["date"])
        if m:
            mo = {"ENE": "01", "MAR": "03", "SEPT": "09"}.get(m.group(1), "01")
            r["batch_date"], r["batch_date_precision"] = f"20{m.group(2)}-{mo}-01", "month"
    newest = max((r.get("batch_date") or "" for r in out), default="")
    for r in out:
        r["most_recent_batch"] = bool(newest and r.get("batch_date") == newest)
    return finish(dedupe(out))


# ---------------- Conception X ----------------
def conceptionx():
    base = "https://www.conceptionx.org/portfolio"
    out, seen_pages = [], 0
    url = base
    for pg in range(1, 30):
        s = get(url)
        items = re.split(r'class="portfolio-collection-item w-dyn-item"', s)[1:]
        for c in items:
            name = strip((re.search(r'class="para-xxl-24">(.*?)</div>', c) or [0, ""])[1])
            founders = strip((re.search(r'Founded By</div><div class="label-s-14">(.*?)</div>', c) or [0, ""])[1])
            cohort = strip((re.search(r'fs-list-field="cohort"[^>]*>(.*?)</div>', c) or [0, ""])[1])
            sectors = [strip(x) for x in re.findall(r'fs-list-field="sector"[^>]*>(.*?)</div>', c)]
            desc = strip((re.search(r'class="para-m-16">(.*?)</div>', c, re.S) or [0, ""])[1])
            links = dict((strip(t), u) for u, t in re.findall(r'<a href="([^"]+)"[^>]*class="portfolio-link">(.*?)</a>', c))
            if not name:
                continue
            out.append(rec(name, "Conception X", "Conception X", description=desc, team=founders,
                           date=f"Conception X {cohort}".strip(), verticals="; ".join(x for x in sectors if x),
                           website=links.get("Website", ""), source_url=base, location="UK"))
        nxt = re.search(r'href="(\?[a-z0-9]+_page=\d+)"[^>]*class="[^"]*w-pagination-next', s) or \
              re.search(r'class="[^"]*w-pagination-next[^"]*"[^>]*href="(\?[a-z0-9]+_page=\d+)"', s)
        if not nxt:
            break
        url = base + _h.unescape(nxt.group(1))
    enrich_from_sites(out)
    for r in out:  # CX18 -> cohort year 2018 ... CX26 -> 2026 (CX = cohort year)
        m = re.search(r"CX(\d\d)", r["date"])
        r["batch_date"] = f"20{m.group(1)}-01-01" if m else ""
        r["batch_date_precision"] = "year" if m else ""
    newest = max((r["batch_date"] for r in out if r["batch_date"]), default="")
    for r in out:
        r["most_recent_batch"] = bool(newest and r["batch_date"] == newest)
    return finish(dedupe(out))


# ---------------- Carbon13 ----------------
C13_CATS = {"built-environment": "Built Environment", "energy": "Energy", "food-systems": "Food Systems",
            "materials-and-chemicals": "Materials and Chemicals", "platforms": "Platforms",
            "transport": "Transport"}


def carbon13():
    out, links = [], []
    for pg in range(1, 10):
        url = "https://carbonthirteen.com/our-portfolio/" + (f"page/{pg}/" if pg > 1 else "")
        r = S.get(url, timeout=60)
        if r.status_code != 200:
            break
        arts = re.findall(r"<article[^>]*>.*?</article>", r.text, re.S)
        if not arts:
            break
        for a in arts:
            cls = re.search(r'class="([^"]+)"', a).group(1)
            if "category-our-portfolio" not in cls:
                continue
            name = strip((re.search(r'class="entry-title">\s*<a[^>]*>(.*?)</a>', a, re.S) or [0, ""])[1])
            href = (re.search(r'class="entry-title">\s*<a href="([^"]+)"', a, re.S) or [0, ""])[1]
            desc = strip((re.search(r'post-content-inner">(.*?)</div>', a, re.S) or [0, ""])[1])
            secs = [v for k, v in C13_CATS.items() if f"category-{k}" in cls]
            if name and href not in links:
                links.append(href)
                out.append(rec(name, "Carbon13", "Carbon13", description=desc, verticals="; ".join(secs),
                               date="Carbon13", source_url=href))
    # featured portfolio pages carry founders / cohort / city / website
    home = get("https://carbonthirteen.com/our-portfolio/")
    feats = sorted(set(re.findall(r'https://carbonthirteen\.com/our-portfolio-featured/[a-z0-9-]+/', home)))
    from common import norm_name
    byname = {norm_name(r["name"]): r for r in out}
    for f in feats:
        t = strip(get(f))
        m = re.search(r"Company Name (.*?) Founded (\d{4})? ?Cohort (.*?) City (.*?) Country (.*?) Founders & Roles (.*?) Web (\S+)", t)
        if not m:
            continue
        nm, fy, coh, city, ctry, fnd, web = m.groups()
        r = byname.get(norm_name(nm))
        if not r:
            r = rec(nm, "Carbon13", "Carbon13", date="Carbon13", source_url=f)
            out.append(r); byname[norm_name(nm)] = r
        r["team"] = fnd.strip(); r["website"] = web.strip(); r["date"] = f"Carbon13 {coh.strip()}"
        r["location"] = ", ".join(x.strip() for x in (city, ctry) if x.strip())
        if fy:
            r["founded"] = fy
    enrich_from_sites(out)
    return finish(dedupe(out))


# ---------------- Zinc ----------------
def zinc():
    out = []
    for pg in range(1, 30):
        url = "https://www.zinc.vc/portfolio-companies/" + (f"page/{pg}/" if pg > 1 else "")
        r = S.get(url, timeout=60)
        if r.status_code != 200:
            break
        items = re.split(r'class="portfolio-list__item cell', r.text)[1:]
        if not items:
            break
        for c in items:
            name = strip((re.search(r'portfolio-list__item-title">(.*?)</h2>', c, re.S) or [0, ""])[1])
            desc = strip((re.search(r'portfolio-list__item-text">(.*?)</div>', c, re.S) or [0, ""])[1])
            href = (re.search(r'<a href="([^"]+)"[^>]*class="dropanchor"', c) or [0, ""])[1]
            if name:
                out.append(rec(name, "Zinc", "Zinc", description=desc, website=href, date="Zinc",
                               source_url=url, location="UK"))
    enrich_from_sites(out)
    return finish(dedupe(out))


# ---------------- Kickstart Innovation ----------------
def kickstartinnovation():
    url = "https://www.kickstart-innovation.com/community-startups-alumni"
    s = get(url)
    pos = [(m.start(), m.group(1)) for m in re.finditer(
        r'wixui-rich-text__text[^>]*>(?:<[^>]+>)*\s*(20[12]\d)\s*<', s)]
    out = []
    for i, (a, y) in enumerate(pos):
        b = pos[i + 1][0] if i + 1 < len(pos) else len(s)
        seg = s[a:b]
        rep = re.findall(r'<div id="(comp-[a-z0-9]+)__[^"]+" role="listitem"', seg)
        if not rep:
            continue
        comp = max(set(rep), key=rep.count)
        for it in re.split(r'<div id="%s__[^"]+" role="listitem"' % comp, seg)[1:]:
            alt = re.search(r'alt="([^"]+)"', it)
            href = re.search(r'data-testid="linkElement" href="(https?://[^"]+)"', it)
            if not alt:
                continue
            w = href.group(1) if href else ""
            if "wixstatic.com" in w:
                w = ""
            out.append(rec(_h.unescape(alt.group(1)), "Kickstart Innovation", "Kickstart Innovation",
                           website=w, date=f"Kickstart {y}", source_url=url, location="Switzerland (Kickstart Zurich)"))
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- Deep Science Ventures ----------------
def deepscienceventures():
    url = "https://www.deepscienceventures.com/our-portfolio"
    s = get(url)
    out = []
    for c in re.split(r'class="content-card w-dyn-item"', s)[1:]:
        sector = strip((re.search(r'fs-cmsfilter-field="Sector" class="text-tag">(.*?)</div>', c) or [0, ""])[1])
        stage = strip((re.search(r'tag_company"><div class="text-tag">(.*?)</div>', c) or [0, ""])[1])
        one = strip((re.search(r'title_our-company-post">(.*?)</div>', c, re.S) or [0, ""])[1])
        a = re.search(r'<a href="([^"]*)" class="featured-link_wrp[^"]*"><div>(.*?)</div>', c, re.S)
        if not a:
            continue
        name, web = strip(a.group(2)), a.group(1)
        sol = strip((re.search(r"<div>SOLUTION</div><p[^>]*>(.*?)</p>", c, re.S) or [0, ""])[1])
        status = "Acquired" if stage == "Acquired" else ""
        out.append(rec(name, "Deep Science Ventures", "Deep Science Ventures",
                       description=(one.rstrip(".") + (". " + sol if sol else "")).strip(), verticals=sector,
                       round=stage if stage in ("Pre-Seed", "Pre-seed", "Seed", "Series A", "Series B") else "",
                       website=web if web.startswith("http") else "", date="Deep Science Ventures",
                       source_url=url, location="UK", status=status))
    for r in out:
        if r["round"] == "Pre-seed":
            r["round"] = "Pre-Seed"
    enrich_from_sites(out)
    return finish(dedupe(out))


# ---------------- VENTURE KICK ----------------
# venturekick.ch sits behind a JS cookie check and an AJAX "load more" list, so the
# two raw inputs are captured with headless Chrome over CDP (site's own loadmore()):
#   venturekick_cdp_list.py  "https://www.venturekick.ch/portfolio?profilesEntry=1" vk_full.html "<loop js>"
#   venturekick_cdp_details.py  -> vk_details.json  (in-page fetch of every profile)
# VK_CACHE points at the directory holding vk_full.html + vk_details.json.
VK_SKIP = re.compile(r"venturekick|venturelab|startupticker|startup\.ch|top100|linkedin|facebook|twitter|x\.com|"
                     r"xing|instagram|youtube|index\.cfm|^#|^mailto", re.I)


def venturekick():
    import os
    d = os.environ.get("VK_CACHE", "/workspace/accel-daily-2026-10-08")
    src = "https://www.venturekick.ch/portfolio?profilesEntry=1"
    full = open(os.path.join(d, "vk_full.html"), errors="ignore").read()
    det = json.load(open(os.path.join(d, "vk_details.json")))
    out = []
    for m in re.finditer(r'<div class="txt-holder">\s*<h2>\s*<span><a href="([^"]+)">(.*?)</a></span>(.*?)</h2>', full, re.S):
        url, name, short = m.group(1), strip(m.group(2)), strip(m.group(3)).rstrip(".").rstrip()
        v = det.get(url) or {}
        lines = [clean(x) for x in (v.get("text") or "").split("\n") if clean(x)]
        tagline, inc, hq, labels = "", "", "", []
        if lines:
            try:
                i = lines.index(name) if name in lines else 0
                tagline = lines[i + 1] if len(lines) > i + 1 and not lines[i + 1].startswith("Incorporated") else ""
            except Exception:
                pass
            for j, x in enumerate(lines):
                if x.startswith("Incorporated:"):
                    inc = x.split(":", 1)[1].strip()
                elif x.startswith("Headquarter:"):
                    hq = x.split(":", 1)[1].strip()
                elif x.startswith("Support:"):
                    labels = [y for y in lines[j + 1:] if not y.startswith(("Incorporated", "Headquarter"))]
        web = ""
        for c in v.get("comments") or []:
            u = re.sub(r"^<!--\s*|\s*-->$", "", c).strip()
            if u and not VK_SKIP.search(u):
                web = u if u.startswith("http") else "https://" + u
                break
        links = [x for x in (v.get("links") or []) if x.startswith("http")]
        if not web:
            web = next((x for x in links if not VK_SKIP.search(x)), "")
        li = next((norm_linkedin(x) for x in links if "linkedin.com/company" in x), "")
        yr = (re.search(r"(\d{4})$", inc) or [0, ""])[1]
        branch = [y.strip() for y in (labels[0].split(",") if labels else []) if y.strip()]
        verts = list(dict.fromkeys(branch + labels[1:]))
        desc = tagline or (short if not short.endswith("...") else "")
        out.append(rec(name, "Venture Kick", "Venture Kick", description=desc, website=web, linkedin_url=li or "",
                       verticals="; ".join(verts), location=(hq + ", Switzerland") if hq else "Switzerland",
                       source_url=url, founded=yr))
    enrich_from_sites([r for r in out if not r["description"]])
    return finish(dedupe(out))


FUNCS = {"stationffoundersprogram": stationf, "wayratelefonica": wayra,
         "startupbootcamp": startupbootcamp, "lanzadera": lanzadera, "conceptionx": conceptionx,
         "carbon13": carbon13, "zinc": zinc, "kickstartinnovation": kickstartinnovation,
         "deepscienceventures": deepscienceventures,
         "venturekick": venturekick}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct8.{FUNCS[slug].__name__}"})
