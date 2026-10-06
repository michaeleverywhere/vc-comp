"""Second pass for blank descriptions: from the company's OWN site only.
Order: meta/og/twitter description (homepage, then /about), then the title tagline,
then the first substantive <p> of the homepage/about page. Same spam + expired-domain
(name-token) guards as common._desc_from_html. Never fetches Crunchbase/LinkedIn/PitchBook."""
import html as _h, json, os, re, sys, warnings
from concurrent.futures import ThreadPoolExecutor
import requests
from common import DATA_DIR, UA, BANNED, clean, norm_name, tag
warnings.filterwarnings("ignore")
BAD = re.compile(r"meta description|lorem ipsum|just another wordpress|coming soon|page not found|"
                 r"domain (is )?for sale|access denied|casino|pokies|slots?\b|betting|jackpot|\bbonus\b|"
                 r"cookies?\b|javascript|enable js|captcha|cloudflare|403|404|under construction|"
                 r"buy this domain|parked|log ?in|sign ?in|all rights reserved|copyright|gambl|\bmenu\b|\b18\+", re.I)
ACC = re.compile(r"seraphim\.vc|ycombinator\.com|techstars\.com|sosv\.com|hax\.co|pear\.vc|catalystaccelerator\.space|"
                 r"betaworks\.com|southparkcommons\.com|zfellows\.com|hf0\.com", re.I)

def get(url):
    for u in ([url] if url.startswith("http") else ["https://" + url, "http://" + url]):
        for verify in (True, False):
            try:
                r = requests.get(u, headers=UA, timeout=15, allow_redirects=True, verify=verify)
                if "charset" not in r.headers.get("content-type", "").lower():
                    r.encoding = r.apparent_encoding
                if r.status_code < 400 and not BANNED.search(r.url) and not ACC.search(r.url):
                    return r.text[:400000]
                return ""
            except requests.exceptions.SSLError:
                continue
            except Exception:
                break
    return ""

def ok(d, page, name):
    if not d or len(d) < 15 or len(d.split()) < 3 or BAD.search(d):
        return False
    toks = [norm_name(t) for t in re.split(r"[\s.\-]+", name) if len(norm_name(t)) >= 3]
    return not toks or any(t in norm_name(page[:200000]) for t in toks)

def meta(s):
    for key in ("name=[\"']description", "property=[\"']og:description", "name=[\"']twitter:description"):
        for q in ('"', "'"):
            for pat in (rf'<meta[^>]+{key}["\'][^>]*content={q}([^{q}]+){q}',
                        rf'<meta[^>]+content={q}([^{q}]+){q}[^>]*{key}'):
                m = re.search(pat, s, re.I)
                if m:
                    return clean(_h.unescape(m.group(1)))
    return ""

def tagline(s, name):
    t = (re.search(r"<title[^>]*>(.*?)</title>", s, re.I | re.S) or [None, ""])[1]
    t = clean(_h.unescape(re.sub(r"<[^>]+>", "", t)))
    parts = [p.strip() for p in re.split(r"\s[|\-–—:·]\s", t) if p.strip()]
    toks = [norm_name(x) for x in re.split(r"[\s.\-]+", name) if len(norm_name(x)) >= 3]
    if toks and not any(k in norm_name(t) for k in toks):
        return ""          # title names a different brand (redirected / re-used domain)
    parts = [p for p in parts if len(p.split()) >= 3 and norm_name(p) not in norm_name(name)
             and norm_name(name) not in norm_name(p)]
    return parts[0] if parts else ""

def first_p(s):
    body = re.sub(r"<(script|style|nav|header|footer|noscript)[^>]*>.*?</\1>", " ", s, flags=re.I | re.S)
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", body, re.I | re.S):
        t = clean(_h.unescape(re.sub(r"<[^>]+>", " ", m.group(1))))
        if 8 <= len(t.split()) <= 80 and not BAD.search(t):
            return t
    return ""

def describe(r):
    name, url = r["name"], r["website"]
    if ACC.search(url):
        return "", ""
    home = get(url)
    if not home:
        return "", ""
    base = re.match(r"(https?://[^/]+)", url if url.startswith("http") else "https://" + url).group(1)
    pages = [("homepage", home)]
    for path in ("/about", "/about-us"):
        a = get(base + path)
        if a:
            pages.append((path, a)); break
    for src, s in pages:
        d = meta(s)
        if ok(d, home + s, name):
            return d, f"company website meta description ({src})"
    d = tagline(home, name)
    if ok(d, home, name):
        return d, "company website title tagline"
    for src, s in pages:
        d = first_p(s)
        if ok(d, home + s, name):
            return d[:300], f"company website text ({src})"
    return "", ""

for slug in sys.argv[1:]:
    p = os.path.join(DATA_DIR, f"{slug}_companies.json")
    d = json.load(open(p)); R = d["companies"]
    todo = [r for r in R if not r.get("description") and r.get("website")]
    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(describe, todo))
    n = 0
    for r, (desc, src) in zip(todo, res):
        if desc:
            r["description"], r["description_source"] = desc, src
            if not r.get("everywhere_tags"):
                r["everywhere_tags"] = tag(r["name"], desc, [x for x in (r.get("verticals") or "").split("; ") if x])
            n += 1
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
    print(slug, "tried", len(todo), "filled", n, "still blank", sum(1 for r in R if not r.get("description")),
          "no website", sum(1 for r in R if not r.get("description") and not r.get("website")), flush=True)
