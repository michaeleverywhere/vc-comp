#!/usr/bin/env python3
"""theseedfund portfolio scraper.

Source: https://theseedfund.vc/portfolio/ — India-focused seed fund portfolio (The Seed Fund).
"""
from __future__ import annotations
import json
from pathlib import Path
from _d50_common import rec, finish

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "theseedfund_companies.json"


def main() -> None:
    raw = json.loads(SRC.read_text())
    out = []
    for r in raw:
        name = (r.get("company_name") or "").strip()
        if not name:
            continue
        out.append(
            rec(
                name,
                None,
                r.get("company_url"),
                "The Seed Fund",
                "https://theseedfund.vc/portfolio/",
                "2026-10-26",
            )
        )
    finish(out, "theseedfund", ["company_name"])


if __name__ == "__main__":
    main()
