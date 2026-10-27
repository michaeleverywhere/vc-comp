#!/usr/bin/env python3
"""twentytwoventures portfolio scraper.

Source: https://twentytwo.vc/portfolio — Seed VC portfolio (Twenty Two Ventures).
"""
from __future__ import annotations
import json
from pathlib import Path
from _d50_common import rec, finish

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "twentytwoventures_companies.json"


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
                "Twenty Two Ventures",
                "https://twentytwo.vc/portfolio",
                "2026-10-26",
            )
        )
    finish(out, "twentytwoventures", ["company_name"])


if __name__ == "__main__":
    main()
