"""Identity — the single source of truth for "what is this firm / company".

Everything that needs to name, key, or dedup a firm or a company goes through
here, so those rules are defined exactly once (no duplicate slug/key logic
scattered across the pipeline). Self-contained: no imports from elsewhere in the
repo.

Two kinds of identity:
  * firm slug  — matches the repo convention data/<slug>_companies.json.
  * company key — stable per-company id used to diff a firm's list over time and
    to upsert into Airtable without duplicates.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional
from urllib.parse import urlsplit

_SUFFIX = "_companies.json"

# Datasets whose filename predates the <slug>_companies.json convention.
# Lightspeed was built from a sitemap before the rule existed, so its file has no
# slug prefix and slug_from_file() returned None for it — meaning the firm
# produced NO slug, and is_known(), the system's only dedup gate, could not see
# it. Anything proposing "Lightspeed" looked brand new and would have been
# scraped into a second, competing lightspeed_companies.json. Mapped in both
# directions so the file->slug and slug->file rules stay one fact, not two.
_FILE_ALIASES = {"companies.json": "lightspeed"}
_SLUG_ALIASES = {v: k for k, v in _FILE_ALIASES.items()}

# Firms whose dataset slug is a nickname or acronym that CANNOT be derived from
# the firm's full name. Observed live 2026-07-27: the finder proposed "Andreessen
# Horowitz", both gates missed it, and it was queued as a brand-new firm despite
# a16z_companies.json holding 852 of its companies. Two separate failures, one
# cause — the slug is a nickname:
#   * is_known() slugifies the NAME ("andreessenhorowitz") and never reaches "a16z";
#   * the exclude list sent to the model is built from display names, and
#     firm_names.json calls that firm "a16z", so the model was never told.
# Listing the alternative names fixes both: they become slug variants for the
# dedup gate, and candidate_finder adds them to what the model must not propose.
_ALT_NAMES: dict[str, tuple[str, ...]] = {
    "ose":     ('OSE', 'Oxford Sciences Innovation'),
    "evp":     ('EVP',),
    "hofcapital":     ('HOF',),
    "baincapitalls":     ('BCLS',),
    "mventures":     ('Merck Ventures', 'MS Ventures'),
    "portage":     ('Portage Ventures',),
    "augmentum":     ('Augmentum Fintech plc',),
    "racapital":     ('RA Capital',),
    "dcg":     ('DCG',),
    "kfund":     ('Kfund',),
    "f2":     ('F2 Venture Capital',),
    "eightroads":     ('Eight Roads Ventures',),
    "extantia":     ('Extantia',),
    "lafamiglia":     ('La Famiglia VC',),
    "p101":     ('P101 SGR',),
    "hongshan":     ('HSG', 'Sequoia Capital China'),
    "z47":     ('Matrix Partners India',),
    "visionfund":     ('Vision Fund',),
    "hf":     ('H&F', 'Hellman and Friedman'),
    "cdr":     ('CD&R', 'Clayton Dubilier and Rice'),
    "hig":     ('HIG Capital',),
    "leonardgreen":     ('Leonard Green',),
    "eqt":     ('EQT Group', 'EQT Partners'),
    "bdmi":     ('Bertelsmann Digital Media Investments',),
    "stonepeak":     ('Stonepeak Partners',),
    "globis":     ('GLOBIS Capital',),
    "iqt":     ('IQT',),
    "axeleo":     ('AXC', 'Axeleo'),
    "mainsequence":     ('Main Sequence Ventures',),
    "foxmont":     ('Foxmont Capital',),
    "skyvc":     ('JetBlue Technology Ventures', 'JetBlue Ventures'),
    "zvc":     ('ZVC',),
    "kepple":     ('Verod-Kepple Africa Ventures',),
    "snocap":     ('SNOCAP', 'Snocap VC'),
    "rightclick":     ('Sydney Seed Fund',),
    "resilience":     ('Resilience VC',),
    "trustfund":     ('Trust Fund VC',),
    "planeta":     ('Planet A',),
    "dfslab":     ('DFS Labs',),
    "rev1":     ('Rev 1 Ventures',),
    "sidecut":     ('Sidecut VC',),
    "morningside":     ('Morningside Venture',),
    "myriad":     ('Myriad Ventures',),
    "artemis":     ('Artemis Fund',),
    "rhocap":     ('Rho Ventures',),
    "toyotaventures":     ('Toyota AI Ventures',),
    "galaxyventures":     ('Galaxy Digital Ventures',),
    "tmv":     ('Trail Mix Ventures',),
    "typeone":     ('Type 1 Ventures',),
    "zeal":     ('Zeal Capital',),
    "lakehouse":     ('Lakehouse',),
    "humba":     ('Humba',),
    "primetime":     ('Prime Time Partners',),
    "rosecliff":     ('Rosecliff',),
    "m1c":     ('M1C',),
    "manchesterstory":     ('Manchester Story',),
    "motivate":     ('Motivate Venture Capital',),
    "kopa":     ('Kopa VC',),
    "broadlight":     ('BroadLight Capital Management',),
    "boutiquevc":     ('Boutique VC',),
    "runwayvc":     ('Runway VC',),
    "fjor":     ('Fjor',),
    "healthx":     ('HealthX',),
    "cuttinghorse":     ('Cutting Horse VC',),
    "altari":     ('Altari',),
    "newtopia":     ('Newtopia',),
    "dashventures":     ('Dash Fund',),
    "oneflourish":     ('1Flourish Capital', '1Flourish'),
    "sumvc":     ('SUM Ventures',),
    "stagevp":     ('Stage Venture Partners',),
    "upshot":     ('CSC Upshot Ventures', 'CSC Upshot', 'Upshot Ventures'),
    "capital1955":     ('1955 Capital',),
    "emergingventures":     ('Emerging Ventures Fund',),
    "italianfounders":     ('Italian Founders Fund',),
    "bigbrain":     ('Big Brain Holdings',),
    "vergehealthtech":     ('Verge HealthTech Fund',),
    "expansionvc":     ('Expansion', 'Expansion Venture Capital'),
    "reshape":     ('Reshape',),
    "outrun":     ('Outrun VC',),
    "brickmortar":     ('Brick & Mortar VC', 'Brick and Mortar Ventures'),
    "theventurecity":     ('The Venture City',),
    "seedspeed":     ('Seed + Speed', 'seed + speed'),
    "mevp":     ('Middle East Venture Partners',),
    "shorooq":     ('Shorooq Partners',),
    "indico":     ('Indico Capital',),
    "rocketship":     ('Rocketship', 'Rocketship VC'),
    "fuse":     ('FUSE', 'Fuse VC'),
    "kdt":     ('KdT', 'KdT VC'),
    "c4ventures":     ('C4V',),
    "lumolabs":     ('Lumo Labs',),
    "techsquare":     ('Tech Square',),
    "mcj":     ('MCJ',),
    "maya":     ('MAYA CAPITAL', 'Maya Capital'),
    "otb":     ('OTB',),
    "nzvc":     ('NZ VC',),
    "momenta":     ('Momenta',),
    "riverpark":     ('Riverpark Ventures',),
    "v2150":     ('2150 VC',),
    "altair":     ('AltaIR', 'Altair Capital'),
    "profounders":     ('PROfounders', 'Profounders Capital'),
    "altos":     ('Altos',),
    "mantaray":     ('Manta Ray', 'MANTA RAY Ventures'),
    "nextech":     ('Nextech',),
    "shiftinvest":     ('SHIFT', 'Shift Invest'),
    "regenerationvc":     ('Regeneration VC', 'Regeneration'),
    "everywherevc":     ('Everywhere VC', 'Everywhere'),
    "maniv":     ('Maniv',),
    "hcvc":     ('Hardware Club',),
    "singular":     ('Singular VC',),
    "cap42":     ('42Cap', '42 CAP'),
    "pt1":     ('PropTech1 Ventures', 'PT1'),
    "firemark":     ('Firemark Ventures', 'IAG Firemark'),
    "tidal":     ('Tidal VC',),
    "embark":     ('Embark',),
    "pilabs":     ('PiLabs',),
    "sky9":     ('Sky9',),
    "gobi":     ('Gobi',),
    "uphonest":     ('UpHonest',),
    "trive":     ('TRIVE', 'Trive Ventures'),
    "growx":     ('growX', 'GrowX Ventures'),
    "concrete":     ('Concrete VC', 'Concrete Ventures'),
    "svhealth":     ('SV Health',),
    "dotcapital":     ('Dot Capital',),
    "amexventures":     ('American Express Ventures', 'AMEX Ventures'),
    "biogeneration":     ('BioGeneration',),
    "peaks14":     ('14 Peaks', '14Peaks Capital'),
    "qumra":     ('Qumra',),
    "bailador":     ('Bailador',),
    "tenacious":     ('Tenacious',),
    "casdin":     ('Casdin',),
    "hiventures":     ('Hi Ventures', 'ALLVP', 'Hi.vc'),
    "activate":     ('Activate Capital Partners',),
    "acme":     ('ACME Capital',),
    "finch":     ('Finch',),
    "valia":     ('Valia',),
    "sourcecode":     ('Source Code',),
    "alphajwc":     ('Alpha JWC',),
    "phoenixcourt":     ('Phoenix Court', 'LocalGlobe'),
    "porscheventures":     ('Porsche Ventures', 'Porsche Digital'),
    "baincapitalcrypto":     ('Bain Crypto',),
    "defy":     ('Defy', 'Defy.vc'),
    "ironspring":     ('Ironspring',),
    "operatorcollective":     ('OpCo', 'Operator Collective Fund'),
    "scribble":     ('Scribble',),
    "calmstorm":     ('Calm Storm', 'Calm/Storm'),
    "nap":     ('NAP VC', 'Cavalry Ventures'),
    "redstone":     ('Redstone VC',),
    "voima":     ('Voima',),
    "yzr":     ('YZR',),
    "practica":     ('Practica',),
    "ysios":     ('Ysios',),
    "asabys":     ('Asabys',),
    "outliers":     ('Outliers Venture Capital',),
    "orios":     ('Orios',),
    "ideaspring":     ('Ideaspring',),
    "luge":     ('Luge',),
    "arboretum":     ('Arboretum',),
    "seventure":     ('Seventure',),
    "actvc":     ('ACT VC', 'ACT Venture'),
    "bostonseed":     ('Boston Seed',),
    "bonangels":     ('Bon Angels',),
    "mizmaa":     ('MizMaa',),
    "twobear":     ('Two Bear',),
    "vorwerk":     ('Vorwerk',),
    "buildersvc":     ('Builders VC Fund',),
    "jsv":     ('JSV', 'Jackson Square'),
    "shinecapital":     ('Shine VC',),
    "dalus":     ('Dalus',),
    "lightboxvc":     ('Lightbox',),
    "incubatefund":     ('Incubate',),
    "launchcapital":     ('LaunchCapital',),
    "acrew":     ('Acrew',),
    "allianceventure":     ('Alliance VC',),
    "forgevc":     ('Forge Ventures',),
    "bivf":     ('BIVF', 'Boehringer Ingelheim Venture'),
    "imecxpand":     ('imec xpand', 'imecxpand'),
    "keen":     ('KEEN Venture Partners', 'Keen VC'),
    "brightstone":     ('Brightstone',),
    "cultivian":     ('Cultivian Sandbox', 'Cultivian'),
    "ripple":     ('Ripple VC',),
    "vibecapital":     ('Vibe', 'Vibe VC'),
    "linearcapital":     ('Linear Venture',),
    "emerald":     ('Emerald VC', 'Emerald Ventures'),
    "atlantaventures":     ('Atlanta Ventures Fund',),
    "catapult":     ('Catapult VC',),
    "sevenstars":     ('Seven Stars VC',),
    "onevc":     ('One VC',),
    "archetype":     ('Archetype Fund',),
    "collabcurrency":     ('Collab Currency',),
    "eos":     ('Eos VC',),
    "fintlv":     ('FinTLV',),
    "hypersphere":     ('Hypersphere Ventures',),
    "loveventures":     ('Love VC',),
    "twinpath":     ('Twin Path',),
    "altara":     ('Altara',),
    "atinum":     ('Atinum',),
    "bluewire":     ('Blue Wire',),
    "firstcheque":     ('First Cheque VC',),
    "mandiri":     ('Mandiri Capital',),
    "yellowdog":     ('Yellow Dog',),
    "saasholic":     ('SaaSholic VC',),
    "ankur":     ('Ankur',),
    "trustageventures":     ('TruStage Ventures', 'CMFG Ventures'),
    "heartfelt":     ('Heartfelt VC',),
    "bamventures":     ('BAM', 'BAM VC'),
    "greenegg":     ('Green Egg',),
    "shakti":     ('Shakti VC',),
    "unrulycapital":     ('Unruly',),
    "virtuevc":     ('Virtue VC',),
    "propellervc":     ('Propeller Ventures',),
    "reignvc":     ('Reign', 'Reign VC'),
    "brainstormvc":     ('Brainstorm',),
    "waterbridge":     ('WaterBridge',),
    "dundeevc":     ('Dundee VC',),
    "verticalvp":     ('Vertical VP',),
    "marathonvc":     ('Marathon VC',),
    "stridevc":     ('Stride',),
    "adaptvc":     ('Adapt VC',),
    "elysiumvc":     ('Elysium VC',),
    "chamaeleon":     ('Chamaeleon VC',),
    "duroventures":     ('Duro VC',),
    "demea":     ('Demea', 'Demeter Investment Managers'),
    "berthacapital":     ('Bertha',),
    "capital359":     ('359 Capital VC',),
    "iosg":     ('IOSG',),
    "allincapital":     ('All In Capital VC',),
    "trihill":     ('Trihill',),
    "cdpvc":     ('CDP VC',),
    "axonpartners":     ('Axon Partners',),
    "speedupvc":     ('SpeedUp Group', 'SpeedUp VC'),
    "wiharper":     ('WI Harper',),
    "avaana":     ('Avaana',),
    "aglae":     ('Aglae Ventures',),
    "v2045vc":     ('2045 VC',),
    "stoutstreet":     ('Stout Street',),
    "mathvp":     ('MATH VP', 'MATH Venture'),
    "firebolt":     ('Firebolt VC',),
    "teambuilder":     ('Team Builder',),
    "utecvc":     ('UTEC', 'University of Tokyo Edge Capital'),
    "scrumvc":     ('Scrum VC',),
    "g20vc":     ('G20 VC',),
    "bluetreevc":     ('BlueTree VC', 'BlueTree Venture Capital'),
    "missionog":     ('Mission OG',),
    "alpacavc":     ('Alpaca Ventures',),
    "vertexisrael":     ('Vertex Israel',),
    "thinairlabs":     ('Thin Air',),
    "nttdocomov":     ('NTT Docomo Ventures', 'NTT DOCOMO Ventures'),
    "coventures":     ('Co Ventures',),
    "detroitvp":     ('DVP', 'Detroit VP'),
    "artisvc":     ('Artis', 'ARTIS Ventures'),
    "omegafunds":     ('Omega Funds',),
    "pwv":     ('PWV',),
    "augustcap":     ('August Capital',),
    "amoon":     ('aMoon',),
    "madison25":     ('25madison',),
    "taurusvc":     ('Taurus VC',),
    "loftyinc":     ('LoftyInc',),
    "chengwei":     ('Chengwei',),
    "fgvcap":     ('FGV', 'Fiat Ventures'),
    "akkadian":     ('Akkadian',),
    "twinevc":     ('Twine',),
    "betatron":     ('Betatron',),
    "kompasvc":     ('KOMPAS',),
    "switchvc":     ('Switch VC',),
    "supermoon":     ('Supermoon',),
    "cadenzavc":     ('Cadenza',),
    "vocap":     ('Vocap',),
    "alixvc":     ('Alix VC',),
    "capriavc":     ('Capria',),
    "firststarvc":     ('First Star',),
    "ibexinv":     ('Ibex',),
    "sociicap":     ('Socii',),
    "kayyak":     ('Kayyak',),
    "silascap":     ('Silas',),
    "utopianvc":     ('Utopian',),
    "modusvc":     ('Modus',),
    "rarebreedvc":     ('RareBreed',),
    "ankona":     ('Ankona',),
    "expeditionsfund":     ('Expeditions',),
    "cyberagentcap":     ('CyberAgent Capital (CAC)',),
    "naverd2sf":     ('D2SF', 'NAVER D2SF'),
    "mongodbvc":     ('MongoDB Ventures',),
    "electric":     ('Electric Capital Management',),
    "weekend":     ('Weekend.fund',),
    "griffin":     ('Griffin Gaming',),
    "section32":     ('S32',),
    "dragonfly":     ('Dragonfly Capital', 'Dragonfly Capital Partners'),
    "peakxv":     ("Peak XV", "Sequoia India", "Sequoia SEA", "Sequoia Capital India"),
    "a16z":       ("Andreessen Horowitz",),
    "usv":        ("Union Square Ventures",),
    "nea":        ("New Enterprise Associates",),
    "crv":        ("Charles River Ventures",),
    "ivp":        ("Institutional Venture Partners",),
    "tcv":        ("Technology Crossover Ventures",),
    "lightspeed": ("Lightspeed Venture Partners",),
    "svangel":    ("SV Angel",),
    "8vc":        ("Eight VC",),
    "cranevp":    ("Crane Venture Partners", "Crane"),
    "fprimecapital": ("F-Prime",),
    "pillarvc":   ("Pillar",),
    "underscorevc": ("Underscore",),
    "backedvc":   ("Backed",),
    "headline":   ("e.ventures", "Headline Ventures"),
    "collaborativefund": ("Collab Fund",),
    "next47":     ("N47",),
    "4dxventures": ("4DX",),
    "tlcomcapital": ("TLcom",),
    "kaporcapital": ("Kapor",),
    "bcapital":   ("B Capital Group", "B Capital Group Management"),
    "b2venture":  ("btov", "btov Partners", "b2venture.vc"),
    "vertexus":   ("Vertex Ventures", "VVUS"),
    "nordicninja": ("Nordic Ninja", "NordicNinja VC"),
    "lool":       ("lool", "lool vc"),
    "visionaries": ("Visionaries", "Visionaries Club VC"),
    "groundup":   ("GroundUp", "GroundUp VC"),
    "cathay":     ("Cathay Innovation",),
    "maki":       ("Maki.vc", "Maki VC"),
    "nexus":      ("Nexus VP", "Nexus Venture Partners"),
    "threevc":    ("3VC", "Three VC"),
    "samsungnext": ("Samsung NEXT", "Samsung Next Ventures"),
    "chrysalix":  ("Chrysalix VC", "Chrysalix Venture Capital"),
    "stage2": ("Stage 2 Capital", "Stage 2",),
    "fiveam": ("5AM Ventures", "5AM",),
    "nextcoast": ("Next Coast Ventures", "Next Coast",),
    "converge": ("Converge VC", "Converge Venture Partners",),
    "onekx": ("1kx", "1kx Capital", "One KX",),
    "variant": ("Variant Fund",),
    "mantis": ("Mantis VC", "Mantis Venture Capital",),
    "htgf": ("HTGF", "High-Tech Grunderfonds", "High-Tech Gruenderfonds", "High Tech Gründerfonds",),
    "psl": ("PSL", "PSL Ventures", "Pioneer Square Labs",),
    "qiming": ("Qiming Venture Partners", "Qiming VC",),
    "samsara": ("Samsara BioCapital", "Samsara Bio Capital",),
    "foresite": ("Foresite Capital", "Foresite",),
    "revolution": ("Revolution LLC", "Revolution Ventures", "Revolution Growth", "Rise of the Rest",),
    "trinity": ("Trinity Ventures",),
    "endiya": ("Endiya Partners", "Endiya",),
    "agfunder": ("AgFunder Ventures",),
    "intelcapital": ("Intel Capital", "IntelCapital",),
    "threesixtycapital": ("360 Capital", "360 Capital Partners", "Three Sixty Capital",),
    "hackvc": ("Hack VC", "Hack.vc",),
    "equal": ("Equal Ventures",),
    "standup": ("StandUp Ventures", "Stand Up Ventures",),
    "flagship": ("Flagship Pioneering", "Flagship",),
    "liquid2": ("Liquid 2 Ventures", "Liquid2", "Liquid 2",),
    "flourish": ("Flourish Ventures",),
    "ffvc": ("ff Venture Capital", "ffVC", "FFVC",),
    "unitedventures": ("United Ventures",),
    "tlv": ("TLV Partners", "TLV",),
    "quona": ("Quona Capital",),
    "molten": ("Molten Ventures", "Draper Esprit",),
    "bmwiventures": ("BMW i Ventures", "BMW i Ventures GmbH",),
    "framework": ("Framework Ventures", "Framework",),
    "mpmbioimpact": ("MPM BioImpact", "MPM Capital",),
    "idgcapital": ("IDG Capital", "IDG Ventures",),
    "team8": ("Team8", "Team 8",),
    "hvcapital": ("HV Capital", "Holtzbrinck Ventures", "HV",),
    "dcm": ("DCM Ventures", "DCM",),
    "wellington": ("Wellington Management", "Wellington", "Wellington Management Company"),
    "creandum": ("Creandum",),
    "sonyinnovation": ("Sony Innovation Fund", "Sony Ventures",),
    "blume": ("Blume Ventures", "Blume",),
    "shrug": ("Shrug Capital", "Shrug",),
    "joyance": ("Joyance Partners", "Joyance",),
    "commerceventures": ("Commerce Ventures",),
    "hg": ("Hg", "HgCapital", "Hg Capital",),
    "dayone": ("Day One Ventures", "Day One",),
    "higherground": ("Higher Ground Labs", "Higher Ground",),
    "versionone": ("Version One Ventures", "Version One",),
    "compound": ("Compound", "Compound VC",),
    "originventures": ("Origin Ventures",),
    "oneconfirmation": ("1confirmation", "One Confirmation",),
    "valor": ("Valor Equity Partners", "Valor", "Valor EP",),
    "corazon": ("Corazon Capital", "Corazon",),
    "fuelcapital": ("Fuel Capital",),
    "round13": ("Round13 Capital", "Round13", "Round 13",),
    "relayventures": ("Relay Ventures", "Relay",),
    "ludlow": ("Ludlow Ventures", "Ludlow",),
    "ocaventures": ("OCA Ventures", "OCA",),
    "moxxie": ("Moxxie Ventures", "Moxxie",),
    "kibo": ("Kibo Ventures", "Kibo", "Kibo Nzyme",),
    "lifeline": ("Lifeline Ventures", "Lifeline",),
    "peakcapital": ("Peak Capital", "Peak",),
    "jmi": ("JMI Equity", "JMI",),
    "energize": ("Energize Capital", "Energize Ventures", "Energize",),
    "playventures": ("Play Ventures",),
    "point72ventures": ("Point72 Ventures", "Point72", "P72 Ventures",),
    "teneleven": ("Ten Eleven Ventures", "Ten Eleven", "1011 Ventures", "1011vc",),
    "spectrumequity": ("Spectrum Equity", "Spectrum Equity Partners",),
    "fiveelms": ("Five Elms Capital", "Five Elms",),
    "edison": ("Edison Partners", "Edison Ventures",),
    "spacecapital": ("Space Capital",),
    "makersfund": ("Makers Fund",),
    "monkshill": ("Monk's Hill Ventures", "Monks Hill Ventures", "Monk's Hill", "MHV",),
    "jumpcapital": ("Jump Capital", "Jump Cap",),
    "castleisland": ("Castle Island Ventures", "Castle Island",),
    "sevenwire": ("7wireVentures", "7wire Ventures", "7wire",),
    "crosscut": ("Crosscut Ventures", "Crosscut",),
}

# Trailing generic words dropped when matching a firm name to an existing slug
# ('Bain Capital Ventures' -> baincapital). Matching only; never used to name files.
_STRIP_TOKENS = {
    "ventures", "venture", "partners", "partner", "capital",
    "management", "group", "growth", "vc",
}

# --- company field aliases (schemas are site-tailored; check in order) ---
_NAME_KEYS = ("company_name", "name", "companyName", "title")
_URL_KEYS = ("company_url", "url", "website", "homepage", "company_website")
_DESC_KEYS = ("description", "desc", "summary", "tagline")
_STATUS_KEYS = ("status", "is_current_investment", "exit_type", "state")
_EXIT_WORDS = {
    "acquired", "acquisition", "ipo", "public", "exited", "exit",
    "merged", "merger", "spac", "delisted", "shutdown", "closed",
}


# ---------------------------------------------------------------- firm identity
def slugify(firm_name: str) -> str:
    """'Founders Fund' -> 'foundersfund'. Deterministic; lowercase alphanumerics."""
    return re.sub(r"[^a-z0-9]", "", firm_name.lower())


def data_file_for(slug: str) -> str:
    return _SLUG_ALIASES.get(slug) or f"{slug}{_SUFFIX}"


def slug_from_file(filename: str) -> Optional[str]:
    if filename in _FILE_ALIASES:
        return _FILE_ALIASES[filename]
    return filename[: -len(_SUFFIX)] if filename.endswith(_SUFFIX) else None


def known_slugs(filenames: Iterable[str]) -> set[str]:
    return {s for s in (slug_from_file(f) for f in filenames) if s}


# alternative-name slug -> canonical dataset slug, built once from _ALT_NAMES
_ALT_SLUGS = {re.sub(r"[^a-z0-9]", "", n.lower()): canon
              for canon, names in _ALT_NAMES.items() for n in names}


def alt_names_for(slug: str) -> tuple[str, ...]:
    """Other names this firm goes by — for telling the model what not to propose."""
    return _ALT_NAMES.get(slug, ())


def _slug_variants(firm_name: str) -> list[str]:
    """Full slug, versions with trailing generic tokens peeled off (so 'Bain
    Capital Ventures' matches the repo's 'baincapital'), and the canonical slug
    for any name the firm is also known by ('Andreessen Horowitz' -> 'a16z')."""
    tokens = re.sub(r"[^a-z0-9 ]", "", firm_name.lower()).split()
    out: list[str] = []
    while tokens:
        out.append("".join(tokens))
        if tokens[-1] in _STRIP_TOKENS and len(tokens) > 1:
            tokens = tokens[:-1]
        else:
            break
    for v in list(out):                       # nickname lookup, on every variant
        canon = _ALT_SLUGS.get(v)
        if canon and canon not in out:
            out.append(canon)
    return out


def is_known(firm_name_or_slug: str, filenames: Iterable[str]) -> bool:
    """True if the firm (by name or slug, incl. suffix-stripped variants) already
    has a dataset in the repo. This is the ONLY dedup gate in the system."""
    known = known_slugs(filenames)
    return any(v in known for v in _slug_variants(firm_name_or_slug))


# ------------------------------------------------------------- company identity
def _first(record: dict, keys: Iterable[str]) -> Optional[str]:
    for k in keys:
        v = record.get(k)
        if v not in (None, "", []):
            return v if isinstance(v, str) else str(v)
    return None


def company_name(record: dict) -> str:
    return (_first(record, _NAME_KEYS) or "").strip()


def company_url(record: dict) -> Optional[str]:
    return _first(record, _URL_KEYS)


def company_desc(record: dict) -> Optional[str]:
    return _first(record, _DESC_KEYS)


def _domain(url: Optional[str]) -> str:
    if not url:
        return ""
    try:
        host = urlsplit(url if "//" in url else "//" + url).netloc.lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def company_key(record: dict) -> str:
    """Stable identity within one firm's dataset: normalized name + domain.
    Diffs and upserts are always per-firm, so this never collides across firms."""
    name = re.sub(r"[^a-z0-9]", "", company_name(record).lower())
    dom = _domain(company_url(record))
    return f"{name}|{dom}" if dom else name


def row_key(slug: str, record: dict) -> str:
    """Globally-unique Airtable upsert key: <firm slug>|<company key>."""
    return f"{slug}|{company_key(record)}"


def is_exited(record: dict) -> bool:
    """True if any status-ish field reads as an exit (acquired / IPO / …).
    `is_current_investment` is inverted: False means exited."""
    for k in _STATUS_KEYS:
        if k not in record:
            continue
        v = record[k]
        if k == "is_current_investment":
            if v is False:
                return True
            continue
        if isinstance(v, str) and any(w in v.lower() for w in _EXIT_WORDS):
            return True
    return False
