"""Add batch_date (ISO), batch_date_precision (day/season/year), location, most_recent_batch
to every accelerator JSON. Derived only from published batch/cohort labels already in the
record (date / programs / first_session_year) and published locations. No guessing."""
import json, os, re, sys
from collections import defaultdict
from common import DATA_DIR
SEASON = {"W": "01-01", "X": "04-01", "S": "06-01", "F": "09-01",
          "winter": "01-01", "spring": "04-01", "summer": "06-01", "fall": "09-01", "autumn": "09-01",
          "h1": "01-01", "h2": "07-01"}
MANUAL_LOC = {  # (slug, name) -> (location, source)
    ("zfellows", "Mach"): ("Huntington Beach, CA, USA", "https://www.ocbj.com/defense-2/military-co-mach-industries-in-oc/"),
    ("zfellows", "Nucleus"): ("New York, NY, USA", "https://en.wikipedia.org/wiki/Nucleus_Genomics"),
    ("zfellows", "Posh"): ("New York, NY, USA", "https://www.gen-zine.com/posts/avante-price-posh"),
    ("hf0", "Proxy"): ("Lehi, UT, USA", "https://www.boringbusinessnerd.com/post/inside-hf0-with-parker-edwards"),
}
SPC_CITIES = {"San Francisco", "New York", "Bengaluru", "Los Angeles", "Denver", "Miami", "Boston", "Vancouver", "Seattle"}

def label_date(slug, r):
    d = r.get("date") or ""
    if slug in ("ycombinator", "hf0"):
        best = None
        for s, yy in re.findall(r"\b([WSFX])(\d{2})\b", d):
            iso = f"20{yy}-{SEASON[s]}"
            best = best or iso          # first listed label = the company's batch
        return (best, "season", d.split(";")[0].strip()) if best else (None, None, None)
    m = re.search(r"\b(Winter|Spring|Summer|Fall|Autumn)\s+(20\d\d)\b", d, re.I)
    if m:
        return f"{m.group(2)}-{SEASON[m.group(1).lower()]}", "season", d
    m = re.search(r"\b(20\d\d)\s+(H[12])\b", d)
    if m:
        return f"{m.group(1)}-{SEASON[m.group(2).lower()]}", "season", d
    y = r.get("first_session_year")
    if not y:
        m = re.search(r"\b(20\d\d|19\d\d)\b", d) if slug not in ("southparkcommons", "zfellows") else None  # SPC year = founding, not batch
        y = int(m.group(1)) if m else None
    if y:
        return f"{int(y)}-01-01", "year", d
    return None, None, None

def program_key(slug, r):
    d = r.get("date") or ""
    if slug == "techstars":
        return re.sub(r"\s*\b(19|20)\d\d\b.*$", "", d).strip() or (r.get("programs") or [""])[0]
    if slug in ("sosv", "hax", "indiebio"):
        return re.sub(r"\s*\b(20\d\d)\b.*$|\s+\d+$", "", d).strip()
    return "_all"

def run(slug):
    p = os.path.join(DATA_DIR, f"{slug}_companies.json"); D = json.load(open(p)); R = D["companies"]
    newest = defaultdict(str); cnt = defaultdict(int)
    for r in R:
        iso, prec, lab = label_date(slug, r)
        r["batch_date"], r["batch_date_precision"] = iso or "", prec or ""
        if slug == "ycombinator":   # most-recent check uses every label the company carries
            r["_labels"] = [f"20{yy}-{SEASON[s]}" for s, yy in re.findall(r"\b([WSFX])(\d{2})\b", r.get("date") or "")]
            for x in r["_labels"]:
                cnt[x] += 1
        elif slug == "catalystaccelerator":
            r["_labels"] = [f"{y}-{SEASON[m.lower()]}" for m, y in re.findall(r"\b(Winter|Spring|Summer|Fall)\s+(20\d\d)", r.get("date") or "")]
            for x in r["_labels"]:
                newest["_all"] = max(newest["_all"], x)
        elif iso:
            k = program_key(slug, r); newest[k] = max(newest[k], iso)
        # location
        loc = r.get("location") or ""
        if not loc and slug == "southparkcommons":
            t = (r.get("verticals") or "").split("; ")[-1]
            if t in SPC_CITIES:
                loc = t; r["location_source"] = "South Park Commons companies page"
        ml = MANUAL_LOC.get((slug, r["name"]))
        if ml and not loc:
            loc, r["location_source"] = ml
        r["location"] = loc or ""
    if slug == "ycombinator":   # newest label with a real cohort (>=20 companies); ignores stray future labels
        newest["_all"] = max(x for x, c in cnt.items() if c >= 20)
    for r in R:
        if slug in ("ycombinator", "catalystaccelerator"):
            r["most_recent_batch"] = bool(r.get("_labels")) and newest["_all"] in r.pop("_labels")
        else:
            k = program_key(slug, r)
            r["most_recent_batch"] = bool(r["batch_date"]) and r["batch_date"] == newest.get(k)
    json.dump(D, open(p, "w"), indent=1, ensure_ascii=False)
    n = len(R)
    print(f"{slug}: rows {n} batch_date {sum(1 for r in R if r['batch_date'])} location {sum(1 for r in R if r['location'])} "
          f"most_recent {sum(1 for r in R if r['most_recent_batch'])} newest {dict(newest) if len(newest) < 4 else str(len(newest)) + ' programs'}")

for s in sys.argv[1:]:
    run(s)
