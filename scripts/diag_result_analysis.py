#!/usr/bin/env python3
"""
Print Result Analysis summaries and optional promotion diagnostics from the live DB.

Requires POSTGRES_DATABASE_URL (see project .env). Usage from repo root:

    python scripts/diag_result_analysis.py 2026 1
    python scripts/diag_result_analysis.py 2026 1 --explain 5,6,7

With --explain, prints how grades 5–7 (or any list) chose totals (LearnerPromotion vs marks),
sample promotion codes, and per-learner subject rows used by marks rules (first 30 learners per grade).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, ".env"))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Result Analysis diagnostics")
    parser.add_argument("year", help="Report year, e.g. 2026")
    parser.add_argument("term", help="Term number, e.g. 1")
    parser.add_argument(
        "--explain",
        metavar="GRADES",
        help="Comma-separated grades for promotion diagnostics (e.g. 5,6,7)",
    )
    args = parser.parse_args()
    year, term = args.year.strip(), args.term.strip()

    if not os.environ.get("POSTGRES_DATABASE_URL"):
        print("POSTGRES_DATABASE_URL is not set.", file=sys.stderr)
        return 1

    import app as app_module

    app = app_module.app
    with app.app_context():
        payload = app_module._management_build_result_analysis_payload(year, term)
        explain_grades: list[int] = []
        if args.explain:
            for part in args.explain.split(","):
                p = part.strip()
                if p.isdigit():
                    explain_grades.append(int(p))

        diag = None
        if explain_grades:
            diag = app_module._management_promotion_diagnostics_for_grades(year, term, explain_grades)

        out: dict = {
            "year": year,
            "term": term,
            "phases": [
                {
                    "title": p.get("title"),
                    "grades": p.get("grades"),
                    "summary": p.get("summary"),
                }
                for p in payload.get("phases", [])
            ],
            "metaNote": (payload.get("meta") or {}).get("passThresholdNote"),
        }
        if diag is not None:
            out["promotionDiagnostics"] = diag

    print("=== Result Analysis phase summaries (assessed / promoted / failed / totalPassPct) ===")
    print(json.dumps({"year": year, "term": term, "phases": out["phases"]}, indent=2))

    if diag:
        print()
        print("=== Promotion diagnostics (--explain): how totals were obtained ===")
        for gk, block in (diag.get("grades") or {}).items():
            print()
            print(f"--- Grade {gk} ---")
            print("decisionBranch:", block.get("decisionBranch"))
            print("howTotalsWereChosen:", block.get("howTotalsWereChosen"))
            print("phaseMarksRuleHint:", block.get("phaseMarksRuleHint"))
            reg_meta = {
                k: v
                for k, v in block.items()
                if k.startswith("register") or k == "marksDistinctLearners"
            }
            print("registerMeta:", json.dumps(reg_meta, indent=2))
            summ = block.get("summaryOnReport") or {}
            print("summaryOnReport:", json.dumps(summ, indent=2))
            samp = block.get("registerPromotionSampleRows") or []
            if samp:
                print("sample LearnerPromotion rows (first few in export order):")
                print(json.dumps(samp, indent=2))
            learners = block.get("marksLearnersSampleUpTo30") or []
            print(
                f"marks-based detail (up to {len(learners)} learners): "
                "see JSON key marksLearnersSampleUpTo30 in full dump."
            )
        print()
        print("=== Full diagnostics JSON ===")
        print(json.dumps(diag, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
