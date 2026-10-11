"""Scrapers for the 2026-10-11 Daily-10 accelerator batch.
Usage: python batch_oct11.py [slug...]

Sources: each accelerator's own public portfolio / cohort pages (or the JSON those
pages themselves load, or the accelerator's own company detail pages), plus the
company's own website for blank descriptions / names. Never Crunchbase / LinkedIn /
PitchBook (LinkedIn URLs are only kept when the accelerator page or the company's
own site links them; LinkedIn itself is never fetched). Tags are keyword-only
(automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
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
SOCIAL = re.compile(r"facebook\.com|twitter\.com|x\.com/|instagram\.com|youtube\.com|linkedin\.com|"
                    r"t\.me/|tiktok\.com|medium\.com/@|wa\.me|github\.com", re.I)


# Accelerator-published sector labels (PT/ES/EN) -> Everywhere tags, used by finish() on top of
# the keyword classifier (labels are the accelerators' own published categories).
batch_oct8.ES_LABELS.update({
    # Cubo Itau segments (PT)
    "financeiro": "FinTech / Insurance", "seguros": "FinTech / Insurance", "saúde": "Health",
    "biotecnologia": "BioTech", "recursos humanos": "Future of Work", "produtividade": "Future of Work",
    "varejo": "Consumer", "direito": "RegTech/Gov/Legal", "governo": "RegTech/Gov/Legal",
    "construção civil": "PropTech", "agricultura e pecuária": "Climate / Sustainability",
    "esg": "Climate / Sustainability", "energia": "Climate / Sustainability", "logística": "Logistics / Supply Chain",
    "marítimo e portuário": "Logistics / Supply Chain", "educação": "Consumer", "cibersegurança": "Cybersecurity",
    "mobilidade urbana": "Transportation / Mobility", "entretenimento": "Gaming / Media / Entertainment",
    "análise de dados": "Data & Analytics", "inteligência artificial": "Data & Analytics",
    # Parallel18 industries
    "fintech & finance": "FinTech / Insurance", "healthtech & biotech": "Health", "agritech & food": "Climate / Sustainability",
    "e-commerce & marketplace": "Consumer", "saas & enterprise software": "Dev Tools / Cloud", "ai & data": "Data & Analytics",
    "cleantech & energy": "Climate / Sustainability", "consumer goods & retail": "CPG", "entertainment & media": "Gaming / Media / Entertainment",
    "fashion & beauty": "Consumer", "fitness & wellness": "Health", "govtech": "RegTech/Gov/Legal", "hr & productivity": "Future of Work",
    "industrial & manufacturing": "Deeptech / Robotics / AR/VR", "legal & compliance": "RegTech/Gov/Legal",
    "logistics & transportation": "Logistics / Supply Chain", "real estate & housing": "PropTech", "blockchain & crypto": "Web3 / Crypto",
    "tourism & hospitality": "Consumer", "sports": "Consumer", "education": "Consumer",
    # Hub71 sectors
    "health and life sciences": "Health", "fintech": "FinTech / Insurance", "proptech": "PropTech",
    "mobility & logistics": "Transportation / Mobility", "energy & sustainability": "Climate / Sustainability",
    "agtech & food": "Climate / Sustainability", "edtech": "Consumer", "cybersecurity": "Cybersecurity",
    # Start-Up Chile categories
    "retail, wholesales and consumer products": "Consumer", "health and biotech": "Health",
    "developer and it tools": "Dev Tools / Cloud", "education and learning": "Consumer",
    # NXTP / Platanus / F6 / CcHUB labels
    "fintech & payments": "FinTech / Insurance", "e-commerce & b2b platforms": "Consumer", "infrastructure & security": "Cybersecurity",
    "plg & dev tools": "Dev Tools / Cloud", "information services": "Data & Analytics", "healthtech": "Health",
    "insurtech": "FinTech / Insurance", "climatech": "Climate / Sustainability", "dev tools": "Dev Tools / Cloud",
    "hr tech": "Future of Work", "regtech": "RegTech/Gov/Legal", "foodtech": "CPG", "data": "Data & Analytics",
    "crypto / blockchain": "Web3 / Crypto", "e-commerce": "Consumer", "logistics": "Logistics / Supply Chain",
    "greentech": "Climate / Sustainability", "transportation & logistics": "Logistics / Supply Chain",
    "media & entertainment": "Gaming / Media / Entertainment", "real estate": "PropTech", "workforce management": "Future of Work",
    "agritech": "Climate / Sustainability", "wellness & lifestyle": "Health", "travel & hospitality": "Consumer",
    "healthcare": "Health", "agriculture": "Climate / Sustainability", "beauty": "CPG", "transportation": "Transportation / Mobility",
})


batch_oct8.ES_LABELS.update({
    "climatetech": "Climate / Sustainability", "data science": "Data & Analytics", "enterprise": "Dev Tools / Cloud",
    "ai/ml": "Data & Analytics", "ai": "Data & Analytics", "artificial intelligence": "Data & Analytics",
    "ai / information services": "Data & Analytics", "indústria": "Deeptech / Robotics / AR/VR",
    "saas": "Dev Tools / Cloud", "vertical saas": "Dev Tools / Cloud", "cloud & saas": "Dev Tools / Cloud",
    "software": "Dev Tools / Cloud", "software development": "Dev Tools / Cloud", "ict": "Dev Tools / Cloud",
    "it": "Dev Tools / Cloud", "cyber security": "Cybersecurity", "advanced manufacturing and robotics": "Deeptech / Robotics / AR/VR",
    "manufacturing": "Deeptech / Robotics / AR/VR", "aviation & space": "Deeptech / Robotics / AR/VR",
    "creators economy": "Gaming / Media / Entertainment", "pet care": "Consumer", "travel & tourism": "Consumer",
    "wholesales and consumer products": "Consumer", "telecomunicação": "Dev Tools / Cloud", "telecommunications": "Dev Tools / Cloud",
    "food tech": "CPG", "fashion": "Consumer", "supply chain & logistics": "Logistics / Supply Chain",
    "power": "Climate / Sustainability", "energy / o&g": "Climate / Sustainability", "governance": "RegTech/Gov/Legal",
    "housing": "PropTech", "food & beverage / agri-business": "CPG", "fintech – proptech": "FinTech / Insurance",
    "saas – ecommerce": "Dev Tools / Cloud", "media monitoring saas": "Data & Analytics",
})

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


def no_batch(out):
    for r in out:
        r["batch_date"], r["batch_date_precision"], r["most_recent_batch"] = "", "", False
    return out


def site_meta(url, timeout=15):
    """(name, description, linkedin) from the company's OWN homepage: og:site_name or
    <title> first segment; meta description; a linkedin.com/company link it publishes."""
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


def domain_label(url):
    h = urlparse(url if url.startswith("http") else "https://" + url).netloc.lower()
    h = re.sub(r"^(www\d?|shop|app|get|use|try)\.", "", h)
    return h.split(".")[0]


def name_from_site(url, meta_name):
    """Prefer the company's own site name when it matches its domain; else the domain label."""
    dl = domain_label(url)
    dln = norm_name(re.sub(r"^(get|use|try|my)", "", dl)) or norm_name(dl)
    if meta_name:
        mn = norm_name(meta_name)
        if mn and (dln[:4] in mn or mn[:4] in norm_name(dl)):
            return meta_name, "company website (site name)"
    return dl.replace("-", " ").title() if not re.search(r"\d", dl) else dl, "website domain"


# ---------------- Start-Up Chile ----------------
SUC_POSTS = [  # Start-Up Chile's own generation announcement posts (startupchile.org/blog)
    ("build-3-new-generation", "Generation 3"), ("ignite-3-new-generation", "Generation 3"),
    ("growth-3-new-generation", "Generation 3"), ("build-4-new-generation", "Generation 4"),
    ("ignite-4-new-generation", "Generation 4"), ("growth-4-new-generation", "Generation 4"),
    ("seleccionados-big-5", "BIG 5"), ("generacion-big-8", "BIG 8"),
    ("big-9-esta-aqui-conoce-a-las-startups", "BIG 9"), ("estas-son-las-startups-seleccionadas-para-big-10", "BIG 10"),
    ("big-11-descubre-a-las-startups-que-marcan-el-futuro", "BIG 11"),
    ("big-12-descubre-las-startups-seleccionadas20094-2", "BIG 12"),
]
PROG_RX = re.compile(r"^(build|ignite|growth|tsf|the s factory|female founder|scale|seed)\b[\w\s]*$", re.I)
NOT_NAME = re.compile(r"startups?\b|conoce|know who|seleccion|selected|generation|generaci|programa|^\d+\.|^hq\b|"
                      r"^(build|ignite|growth)\s*\d*$|faq|postula|apply|^https?://|\?$", re.I)


def _suc_parse(body, gen, prog0, url, date):
    out, cur, prog = [], None, prog0
    for tag, inner in re.findall(r"<(h[1-6]|p|li)\b[^>]*>(.*?)</\1>", body, re.S):
        t = txt(inner)
        if not t:
            continue
        if tag.startswith("h") or (PROG_RX.match(t) and len(t) < 30):
            if PROG_RX.match(t):
                prog = re.sub(r"\s*\d+$", "", t).strip().title()
            continue
        lines = re.split(r"<br\s*/?>", inner)
        m = re.match(r"\s*(?:<span[^>]*>\s*)*<(strong|b|a)\b([^>]*)>(.*?)</\1>(.*)$", lines[0], re.S)
        nm = clean(re.sub(r"^[\s–—\-•]+", "", txt(m.group(3)))) if m else ""
        if m and nm and len(nm) <= 60 and not NOT_NAME.search(nm):
            web = first(r'href="([^"]+)"', m.group(2) + m.group(3))
            cur = rec(nm, "Start-Up Chile", "Start-Up Chile", website=web if web.startswith("http") else "",
                      date=f"Start-Up Chile {gen} {prog}".strip(), source_url=url)
            cur["selection_date"] = date
            out.append(cur)
            rest = [re.sub(r"<[^>]+>", "", m.group(4))] + lines[1:]
        elif cur is not None:
            rest = lines
        else:
            continue
        for ln in rest:
            lt = clean(re.sub(r"^[\s–—\-]+", "", txt(ln)))
            if not lt:
                continue
            hq = re.match(r"^HQ\s*:?\s*(.+)$", lt, re.I)
            if hq:
                cur["location"] = hq.group(1)
                continue
            u = first(r'href="(https?://[^"]+)"', ln)
            if re.fullmatch(r"(https?://)?[\w.\-]+\.[a-z]{2,}(/\S*)?", lt) or (u and len(lt) < 60 and lt.lower().startswith(("http", "www"))):
                if not cur["website"]:
                    cur["website"] = u or ("https://" + lt if not lt.startswith("http") else lt)
                continue
            if len(lt) > 15:
                if not cur["description"] and re.match(r"^(is|are|helps?|supports?|offers?|provides?|allows?|enables?|connects?|"
                                                       r"creates?|develops?|uses?|gets?|personalized|es|son|ayuda|ofrece)\b", lt):
                    lt = f"{cur['name']} {lt}"   # announcement sentences that start right after the bolded name
                cur["description"] = clean((cur["description"] + " " + lt).strip())
    return out


def startupchile():
    out = []
    for slug, gen in SUC_POSTS:
        es = f"https://startupchile.org/blog/{slug}/"
        try:
            h = get(es)
        except Exception:
            continue
        en = first(r'href="(https://startupchile.org/en/blog/[^"]+)"', h)
        url = es
        if en:
            try:
                h, url = get(en), en
            except Exception:
                pass
        date = first(r'article:published_time" content="([\d-]{10})', h)
        dm = re.search(r"(\d\d) · (\d\d) · (20\d\d)", h)
        if dm:
            date = f"{dm.group(3)}-{dm.group(2)}-{dm.group(1)}"
        body = h.split('class="article__body"', 1)[-1].split('class="site__footer"', 1)[0]
        prog0 = ""
        pm = re.match(r"(build|ignite|growth)-\d", slug)
        if pm:
            prog0 = pm.group(1).title()
        out += _suc_parse(body, gen, prog0, url, date)
    # featured portfolio on startupchile.org/portafolio/ (loaded by the page from admin-ajax)
    pj = json.loads(get("https://startupchile.org/cms/wp-admin/admin-ajax.php?action=startups&ppp=500&page=1"))

    def det(p):
        try:
            h = get(p["link"], timeout=40)
        except Exception:
            return p, "", [], ""
        web = first(r'class="hero-tertiary__link[^"]*" href="([^"]+)"', h)
        tags_ = [txt(x) for x in re.findall(r'hero-tertiary__tag[^>]*>(.*?)</div>', h, re.S)]
        fnd = txt(first(r'hero-tertiary__mail">.*?<p[^>]*>(.*?)</p>', h))
        if "@" in fnd:
            fnd = ""
        h1 = txt(first(r'<h1 class="hero-tertiary__title[^"]*"[^>]*>(.*?)</h1>', h))
        if h1:
            p = dict(p, title=h1)
        return p, web, tags_, fnd
    for p, web, tags_, fnd in pmap(det, pj.get("posts", []), 8):
        r = rec(_h.unescape(p["title"]),
                "Start-Up Chile", "Start-Up Chile", description=txt(p.get("paragraph")), website=web,
                verticals="; ".join(t for t in tags_ if t not in ("TSF", "Build", "Ignite", "Growth", "Female Founder", "Q.E.P.D")),
                team=re.sub(r"^Founders?:\s*", "", fnd), date="Start-Up Chile portfolio" + (
                    " " + "/".join(t for t in tags_ if t in ("TSF", "Build", "Ignite", "Growth")) if any(t in ("TSF", "Build", "Ignite", "Growth") for t in tags_) else ""),
                location="", source_url=p["link"])
        out.append(r)
    out = [r for r in out if norm_name(r["name"])]
    out = dedupe(out)
    enrich_from_sites(out)
    gens = {g: i for i, (_, g) in enumerate(SUC_POSTS)}
    for r in out:
        d = r.get("selection_date") or ""
        r["batch_date"] = d if re.fullmatch(r"20\d\d-\d\d-\d\d", d) else ""
        r["batch_date_precision"] = "day (selection announcement)" if r["batch_date"] else ""
        r["most_recent_batch"] = "BIG 12" in r["date"]
    return finish(out)


# ---------------- Platanus ----------------
def platanus():
    url = "https://platan.us/portafolio"
    s = get(url)
    tag = first(r"<landing-company-list(.*?)>", s)
    v = _h.unescape(first(r':companies="(.*?)"', tag))
    comps = json.loads(v[v.index("(") + 1:v.rindex(")")])

    def det(c):
        u = "https://platan.us" + c["profile_path"]
        try:
            h = get(u, timeout=40)
        except Exception:
            return c, "", []
        ind = txt(first(r'<h1 class="text-5xl[^"]*">.*?</h1>\s*<h3[^>]*>(.*?)</h3>', h))
        fs = []
        for role, nm in re.findall(r'<p class="bg-gradient[^"]*">\s*(.*?)\s*</p>\s*<h3 class="text-lg[^"]*">\s*(.*?)\s*</h3>', h, re.S):
            fs.append(f"{txt(nm)} ({txt(role)})" if txt(role) else txt(nm))
        return c, ind, fs
    out = []
    for c, ind, fs in pmap(det, comps, 8):
        b = c.get("batch") or {}
        lab = b.get("name") or ("Ventures investment" + (f" {c['opportunity_year']}" if c.get("opportunity_year") else ""))
        desc = clean(c.get("description") or "") or clean(c.get("slogan") or "")
        r = rec(c["name"], "Platanus", "Platanus", description=desc, website=c.get("webpage") or "",
                team=", ".join(fs), verticals=ind, location=c.get("country") or "",
                date=f"Platanus {lab}".replace("Generación", "Generación").strip(),
                source_url="https://platan.us" + c["profile_path"])
        if c.get("slogan"):
            r["tagline"] = clean(c["slogan"])
        r["batch_date"] = (b.get("start_date") or "")[:10]
        r["batch_date_precision"] = "day" if r["batch_date"] else ""
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    top = max((r["batch_date"] for r in out if r["batch_date"]), default="")
    for r in out:
        r["most_recent_batch"] = bool(top and r["batch_date"] == top)
    return finish(out)


# ---------------- NXTP Ventures ----------------
def nxtpventures():
    url = "https://www.nxtp.vc/portfolio"
    s = get(url)
    items = re.split(r'<div role="listitem" class="company-wrap w-dyn-item">', s)[1:]
    raw = []
    for it in items:
        web = first(r'<a href="([^"]*)" target="_blank" class="company-logo-link', it)
        li = next((x for x in re.findall(r'href="(https?://[^"]*linkedin\.com/company/[^"]+)"', it) if "nxtp" not in x), "")
        verts = [txt(x) for x in re.findall(r'class="vertical-text">(.*?)</div>', it, re.S)]
        desc = txt(first(r'class="company-rt w-richtext">(.*?)</div>', it))
        geo = [txt(x) for x in re.findall(r'fs-list-field="hq" class="loc">(.*?)</div>', it, re.S)]
        fnd = txt(first(r'FOUNDERS:\s*</div><div>(.*?)</div>', it))
        st = txt(first(r'STATUS:\s*</div><div fs-list-field="status">(.*?)</div>', it))
        raw.append(dict(web=web, li=li, verts=verts, desc=desc, geo=geo, fnd=fnd, st=st))
    metas = pmap(lambda d: site_meta(d["web"]) if d["web"] else ("", "", ""), raw, 12)
    out = []
    for d, (mn, md, mli) in zip(raw, metas):
        if not d["web"] and not d["li"]:
            continue
        if d["web"]:
            name, nsrc = name_from_site(d["web"], mn)
        else:
            name, nsrc = d["li"].rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title(), "accelerator-listed LinkedIn slug"
        r = rec(name, "NXTP Ventures", "NXTP Ventures", description=d["desc"] or md, website=d["web"],
                linkedin_url=norm_linkedin(d["li"]) or mli, team=d["fnd"], verticals="; ".join(d["verts"]),
                location=", ".join(d["geo"]), status={"Exit": "Exited"}.get(d["st"], d["st"]), date="NXTP Ventures portfolio",
                source_url=url)
        r["name_source"] = nsrc
        if not d["desc"] and md:
            r["description_source"] = "company website meta description"
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- Parallel18 ----------------
def parallel18():
    base = "https://parallel18.com/startup-directory/"
    first_page = get(base)
    last = max([int(x) for x in re.findall(r'startup-directory/(\d+)/', first_page)] + [1])
    pages = [first_page] + pmap(lambda n: get(f"{base}{n}/"), range(2, last + 1), 6)
    out = []
    for s in pages:
        for c in re.split(r'<div data-elementor-type="loop-item"', s)[1:]:
            c = c.split('<div data-elementor-type="loop-item"', 1)[0]
            pre, _, post = c.partition("jet-listing-dynamic-terms")
            post = post.split("</a>", 1)[0]
            heads = [txt(x) for x in re.findall(r'<p class="elementor-heading-title[^"]*">(.*?)</p>', pre, re.S)]
            if not heads:
                continue
            name, labs = heads[0], heads[1:]
            progs, i = [], 0
            while i < len(labs):
                if labs[i].upper() == "PORTFOLIO":
                    progs.append("Portfolio (investment)")
                    i += 1
                elif re.match(r"Gen\.?\s*\d+", labs[i]) and i + 1 < len(labs):
                    progs.append(f"{labs[i + 1]} {labs[i]}")
                    i += 2
                else:
                    progs.append(labs[i])
                    i += 1
            web = first(r'<a [^>]*href="(https?://[^"]+)"', pre)
            inds = [txt(x) for x in re.findall(r'dynamic-terms__link">(.*?)</span>', post, re.S)]
            out.append(rec(name, "Parallel18", "Parallel18", website=web if "parallel18.com" not in web else "",
                           verticals="; ".join(inds), date="Parallel18 " + "; ".join(progs) if progs else "Parallel18",
                           source_url=base))
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:
        gens = [int(g) for g in re.findall(r"P18 Gen\.?\s*(\d+)", r["date"])]
        r["p18_generation"] = str(max(gens)) if gens else ""
    top = max((int(r["p18_generation"]) for r in out if r["p18_generation"]), default=None)
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and r["p18_generation"] == str(top))
    return finish(out)


# ---------------- Cubo Itau ----------------
def cuboitau():
    api = "https://api.site.cubo.itau/startups"
    hdr = {"Origin": "https://cubo.itau", "Referer": "https://cubo.itau/"}
    lst, pg = [], 1
    while pg < 60:
        j = S.get(f"{api}?limit=100&page={pg}", headers=hdr, timeout=60).json()
        lst += j.get("startups") or []
        lst += j.get("upcoming") or []
        if not j.get("hasNext"):
            break
        pg += 1
    seen, uniq = set(), []
    for c in lst:
        if c["slug"] not in seen:
            seen.add(c["slug"])
            uniq.append(c)

    def det(c):
        try:
            return c, S.get(f"{api}/{c['slug']}", headers=hdr, timeout=40).json()
        except Exception:
            return c, {}
    out = []
    for c, d in pmap(det, uniq, 10):
        web = clean(d.get("siteUrl") or "")
        if web and not web.startswith("http"):
            web = "https://" + web.lstrip("/")
        segs = [x.get("name") for x in d.get("segments") or [] if x.get("name") and x.get("name") != "UNKNOWN"] or (
            [c["segment"]] if c.get("segment") and c["segment"] != "UNKNOWN" else [])
        r = rec(c["name"], "Cubo Itau", "Cubo Itaú", description=clean(d.get("description") or c.get("description") or ""),
                website=web, linkedin_url=norm_linkedin(d.get("linkedinUrl") or ""), verticals="; ".join(segs),
                location=", ".join(x.get("name", "") for x in d.get("countries") or []),
                date="Cubo Itaú startup (vitrine)", source_url=f"https://cubo.itau/startups-portfolio/{c['slug']}")
        if c.get("gold_seal"):
            r["cubo_gold_seal"] = True
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- Flat6Labs (portfolio published by F6 Ventures, Flat6Labs' investment arm) ----------------
def flat6labs():
    rest = []
    pg = 1
    while True:
        r = S.get(f"https://f6.vc/wp-json/wp/v2/flat6labs_portfolio?per_page=100&page={pg}", timeout=60)
        if r.status_code != 200 or not r.json():
            break
        rest += r.json()
        pg += 1

    def lab(h, cls):
        return txt(first(r'<div class="' + cls + r'">\s*<p class="label">[^<]*</p>\s*<p[^>]*>(.*?)</p>', h))

    def det(p):
        try:
            h = get(p["link"], timeout=40)
        except Exception:
            return p, {}
        d = {}
        d["name"] = txt(first(r'<h1 class="portfolio-title">(.*?)</h1>', h))
        d["country"] = txt(first(r'</h1>\s*<p>(.*?)</p>', h))
        d["web"] = first(r'<div class="title-text">.*?<a href="(https?://[^"]+)"', h)
        d["year"] = lab(h, "funded")
        d["stage"] = lab(h, "stage")
        d["sector"] = lab(h, "sector")
        logo = first(r'class="funded-by-logo"[^>]*>\s*<img src="[^"]*/([^/"]+)\.\w+"', h)
        fund = re.sub(r"[-_](Dark|Light|White|Black|logo|\d+)$", "", logo or "", flags=re.I)
        fund = re.sub(r"[-_]+", " ", fund).strip().title()
        fund = re.sub(r"\s+Dark$", "", fund).replace("Fac ", "FAC ")
        d["fund"] = "" if re.match(r"(Screenshot|Image|Img|\d)", fund) else fund
        d["region"] = first(r"portfolio_region-([a-z-]+)", h).upper().replace("-", " ")
        d["exited"] = bool(re.search(r"portfolio_stages-exit", h))
        d["desc"] = txt(first(r'<div class="entry-content">(.*?)</div>', h))
        fm = h.split('class="founding-members"', 1)[1] if 'class="founding-members"' in h else ""
        fm = fm.split("</section>", 1)[0].split('<footer', 1)[0]
        fnd = []
        for blk in re.findall(r'<div class="member">(.*?)(?=<div class="member">|$)', fm, re.S):
            ps = [txt(x) for x in re.findall(r"<(?:h\d|p|span|strong)[^>]*>(.*?)</(?:h\d|p|span|strong)>", blk, re.S)]
            ps = [x for x in ps if x and len(x) < 80]
            if ps:
                fnd.append(f"{ps[0]} ({ps[1]})" if len(ps) > 1 else ps[0])
        d["team"] = ", ".join(dict.fromkeys(fnd))
        return p, d
    out = []
    for p, d in pmap(det, rest, 8):
        nm = d.get("name") or txt(p["title"]["rendered"])
        yr = d.get("year", "")
        stage = d.get("stage", "")
        fund = d.get("fund", "")
        loc = ", ".join(x for x in (d.get("country", ""), d.get("region", "")) if x)
        r = rec(nm, "Flat6Labs", "Flat6Labs (F6 Ventures portfolio)",
                description=d.get("desc") or txt(p.get("excerpt", {}).get("rendered")),
                website=d.get("web", ""), team=d.get("team", ""), verticals=d.get("sector", ""),
                round="" if stage.lower() == "exit" else stage, location=loc,
                date=("Flat6Labs / F6 Ventures" + (f" - {fund}" if fund else "") + (f" {yr}" if yr else "")),
                source_url=p["link"])
        if d.get("exited") or stage.lower() == "exit":
            r["status"] = "Exited"
        r["fund"] = fund
        r["first_invested"] = yr
        out.append(r)
    # Flat6Labs' own startup listing (flat6labs.com/CompaniesType/startup/, behind a browser check)
    try:
        h = cdp.render("https://flat6labs.com/CompaniesType/startup/", settle=16, port=9351, prof="/tmp/cdp_f6")
        for art in re.findall(r'<article id="post-\d+" class="[^"]*CompaniesType-startup[^"]*">(.*?)</article>', h, re.S):
            nm = txt(first(r'class="entry-title">(.*?)</h2>', art))
            bt = txt(art)
            if not nm:
                continue
            brief = clean(first(r"Company Brief (.*?) Product ", bt))
            ind = clean(first(r" Industry (.*?) Target Customer", bt))
            out.append(rec(nm, "Flat6Labs", "Flat6Labs", description=brief, verticals=ind,
                           date="Flat6Labs Riyadh Seed Program (flat6labs.com startup listing)", location="Saudi Arabia",
                           source_url=first(r'href="(https://flat6labs\.com/Company/[^"]+)"', art) or "https://flat6labs.com/CompaniesType/startup/"))
    except Exception as e:
        print("flat6labs.com startup listing failed:", e)
    out = dedupe(out)
    enrich_from_sites(out)
    year_batch(out)
    return finish(out)


# ---------------- MEST Africa ----------------
def mestafrica():
    url = "https://meltwater.org/our-entrepreneurs/"
    s = get(url)
    seg = s.split("Startups by our entrepreneurs", 1)[-1].split("EdtechFellowship", 1)[0].split("edtech-fellowship", 1)[0]
    webs = [u for u in dict.fromkeys(re.findall(r'href="(https?://[^"]+)"', seg)) if "meltwater.org" not in u]
    metas = pmap(site_meta, webs, 12)
    out = []
    for w, (mn, md, mli) in zip(webs, metas):
        name, nsrc = name_from_site(w, mn)
        r = rec(name, "MEST Africa", "MEST Africa", description=md, website=w, linkedin_url=mli,
                date="MEST Africa alumni startup", location="Africa", source_url=url)
        r["name_source"] = nsrc
        if md:
            r["description_source"] = "company website meta description"
        if mli:
            r["linkedin_source"] = "company website"
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- CcHUB ----------------
def cchub():
    url = "https://cchub.africa/startups/"
    try:
        s = get(url)
        if s.count('class="venture"') < 5:
            raise ValueError("browser check")
    except Exception:
        s = cdp.render(url, settle=16, port=9352, prof="/tmp/cdp_cchub")
    out = []
    for v in re.split(r'<div class="venture">', s)[1:]:
        a = re.search(r'venture__name">\s*<h3>\s*(?:<a href="([^"]*)"[^>]*>)?(.*?)(?:</a>)?\s*</h3>', v, re.S)
        if not a:
            continue
        name, web = txt(a.group(2)), (a.group(1) or "").strip()
        if web and not web.startswith("http"):
            web = "http://" + web
        bio = txt(first(r'venture__bio">(.*?)</div>', v))
        dom = txt(first(r'venture__meta-domain">(.*?)</span>', v))
        st = txt(first(r'venture__meta-started">(.*?)</span>', v))
        out.append(rec(name, "CcHUB", "CcHUB", description=bio, website=web, verticals=dom,
                       date=f"CcHUB {st}".strip() if st else "CcHUB incubation/acceleration portfolio",
                       location="Africa (Nigeria/Kenya/Rwanda)", source_url=url))
    out = dedupe(out)
    enrich_from_sites(out)
    return finish(no_batch(out))


# ---------------- Founders Factory Africa ----------------
def foundersfactoryafrica():
    base = "https://www.foundersfactory.africa"
    s = get(base + "/portfolio")
    slugs = list(dict.fromkeys(re.findall(r'href="/portfolio/([^"/?#]+)"', s)))
    cards = {}
    for c in re.split(r'role="listitem" class="collection-item-2 w-dyn-item">', s)[1:]:
        sl = first(r'href="/portfolio/([^"]+)"', c)
        cards[sl] = dict(tag=txt(first(r"<h6>(.*?)</h6>", c)), desc=txt(first(r"<p>(.*?)</p>", c)),
                         country=txt(first(r'class="text-block">(.*?)</div>', c)),
                         labels=[txt(x) for x in re.findall(r'class="business-tag[^"]*">(.*?)</p>', c)],
                         name=txt(first(r'class="text-block-12">(.*?)</div>', c)))

    def det(sl):
        u = f"{base}/portfolio/{sl}"
        try:
            h = get(u, timeout=40)
        except Exception:
            return sl, {}
        t = txt(re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S))
        web = ""
        for href, lab in re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', h, re.S):
            if re.search(r"visit .* site", txt(lab), re.I):
                web = href
        name = clean(first(r"^(.*?) is a startup from FFA", txt(first(r"<title>(.*?)</title>", h))))
        fb = h.split("Meet the founding team", 1)[-1].split("Get involved", 1)[0]
        fs = [(txt(a), txt(b)) for a, b in re.findall(r'<h5 class="no-margin">(.*?)</h5>\s*<h6 class="heading-30">(.*?)</h6>', fb, re.S) if txt(a)]
        port = first(r"is a startup from FFA's (\w+) portfolio", t)
        tags_ = [x for x in re.findall(r"\b(HEALTHCARE|FINTECH|AGRITECH|EDTECH|LOGISTICS|INSURTECH|CLIMATE|ECOMMERCE|E-COMMERCE)\b", t.split("ACTIVELY RAISING")[-1][:200] if "ACTIVELY RAISING" in t else t[:600])]
        full = clean(first(r"VISIT .*? SITE ↗ (.*?) Meet the founding team", t))
        return sl, dict(web=web, name=name, team=", ".join(f"{a} ({b})" if b else a for a, b in fs), port=port,
                        tags=list(dict.fromkeys(tags_)), full=full, u=u)
    out = []
    for sl, d in pmap(det, slugs, 8):
        c = cards.get(sl, {})
        name = c.get("name") or d.get("name") or sl.replace("-", " ").title()
        labs = c.get("labels") or []
        desc = c.get("desc") or ""
        r = rec(name, "Founders Factory Africa", "Founders Factory Africa", description=desc, website=d.get("web", ""),
                team=d.get("team", ""), verticals="; ".join([d["port"].title()] if d.get("port") else []),
                location=c.get("country", ""), date="Founders Factory Africa " + ("current program" if "CURRENT PROGRAM" in labs else "portfolio"),
                source_url=d.get("u", f"{base}/portfolio/{sl}"))
        if c.get("tag"):
            r["tagline"] = c["tag"]
        if "ACTIVELY RAISING" in labs:
            r["fundraising_status"] = "Actively raising (per FFA)"
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = "current program" in r["date"]
    return finish(out)


# ---------------- Hub71 ----------------
HUB71_STAGE = {"Emergent": "Emergent (Hub71 stage)"}


def hub71():
    api = "https://www.hub71.com/all-startups?search=&country=&page={}&perPage=500"
    data, pg = [], 1
    while True:
        j = S.get(api.format(pg), headers={"X-Requested-With": "XMLHttpRequest"}, timeout=60).json()
        data += j.get("data") or []
        if not j.get("next_page_url"):
            break
        pg += 1
    en = lambda x: (x or {}).get("en", "") if isinstance(x, dict) else (x or "")
    out = []
    for d in data:
        name = clean(en(d.get("title")))
        if not name:
            continue
        desc = txt(en(d.get("what_we_do_description"))) or txt(en(d.get("description"))) or txt(en(d.get("who_we_are_description")))
        desc = re.sub(r"\s*Follow us on .*$", "", desc)
        web = clean(d.get("website") or "")
        if web and not web.startswith("http"):
            web = "https://" + web
        coh = clean(d.get("cohort") or "")
        r = rec(name, "Hub71", "Hub71", description=desc, website=web, verticals=clean(d.get("sector") or ""),
                round=clean(en(d.get("stage"))), amount_raised=clean(str(d.get("total_funding") or "")),
                location=clean(d.get("new_country") or en(d.get("country"))),
                date=("Hub71 " + re.sub(r"Cohort(\d+)", r"Cohort \1", coh)) if coh else ("Hub71 " + clean(d.get("program_name") or "startup")).strip(),
                source_url="https://www.hub71.com/startups/" + clean(en(d.get("slug"))))
        r["cohort_number"] = first(r"(\d+)", coh)
        if d.get("total_funding"):
            r["amount_raised_source"] = "Hub71 startup directory (total funding)"
        out.append(r)
    out = dedupe(out)
    enrich_from_sites(out)
    nums = [int(r["cohort_number"]) for r in out if r["cohort_number"]]
    top = str(max(nums)) if nums else None
    for r in out:
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and r["cohort_number"] == top)
    return finish(out)


FUNCS = {"startupchile": startupchile, "platanus": platanus, "nxtpventures": nxtpventures,
         "parallel18": parallel18, "cuboitau": cuboitau, "flat6labs": flat6labs, "mestafrica": mestafrica,
         "cchub": cchub, "foundersfactoryafrica": foundersfactoryafrica, "hub71": hub71}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct11.{FUNCS[slug].__name__}"})
