#!/usr/bin/env python3
"""Print EMS subject names from ReportMarks with promotion-rule bucket + minimum % per grade.

Uses the same helpers as app.py (_management_normalize_subject_label, inclusion, thresholds).

Usage (repo root, POSTGRES_DATABASE_URL in .env):

    python scripts/export_subject_pass_threshold_map.py 2026 1
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, ".env"))


def _rule_bucket(app_mod, sub_norm: str) -> str:
    if app_mod._management_subject_excluded_from_overall_pass(sub_norm):
        return "excluded (sport/club/etc.)"
    if app_mod._management_is_afrikaans_home_language_subject(sub_norm):
        return "Afrikaans Home Language (blocks promotion — not FAL slot)"
    if app_mod._management_is_home_language_subject(sub_norm):
        return "English Home Language"
    if app_mod._management_is_fal_subject(sub_norm):
        return "Afrikaans First Additional Language"
    if app_mod._management_is_maths_subject(sub_norm):
        return "Mathematics / Numeracy / Mathematical Literacy"
    if app_mod._management_is_natural_sciences_technology_subject(sub_norm):
        return "Natural Sciences / NST"
    if app_mod._management_is_social_sciences_subject(sub_norm):
        return "Social Sciences"
    if app_mod._management_is_technology_subject(sub_norm):
        return "Technology"
    if app_mod._management_is_ems_subject(sub_norm):
        return "EMS"
    if app_mod._management_is_life_orientation_subject(sub_norm):
        return "Life Orientation"
    if app_mod._management_is_life_skills_subject(sub_norm):
        return "Life Skills"
    if app_mod._management_is_creative_arts_subject(sub_norm):
        return "Creative Arts"
    if app_mod._management_is_english_subject(sub_norm):
        return "Other English (not HL slot — check naming)"
    return "Other / elective (uses phase default minimum)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("year")
    parser.add_argument("term")
    parser.add_argument("--csv", metavar="PATH", help="Write CSV to PATH")
    parser.add_argument("--json", metavar="PATH", help="Write JSON to PATH")
    args = parser.parse_args()
    year, term = args.year.strip(), args.term.strip()

    if not os.environ.get("POSTGRES_DATABASE_URL"):
        print("POSTGRES_DATABASE_URL is not set.", file=sys.stderr)
        return 1

    import app as app_mod

    q = """
SELECT DISTINCT CSTR(lp.Grade) AS Grade, s.Name AS Subject
FROM ReportMarks rm, ReportCycles rc, Subjects s, LearnerPromotion lp
WHERE rm.ReportId = rc.CycleId
AND rm.SubjectId = s.Id
AND CSTR(lp.LearnerId) = CSTR(rm.LearnerID)
AND CSTR(lp.Datayear) = CSTR(rm.Datayear)
AND CSTR(rm.Datayear) = ?
AND CSTR(rc.Term) = ?
ORDER BY Grade, Subject
"""

    app = app_mod.app
    with app.app_context():
        rows = app_mod.mdb_conn.execute_query(q, (year, term)) or []

    out_rows: list[dict] = []
    for r in rows:
        g = str(r.get("Grade") or "").strip()
        raw = str(r.get("Subject") or "").strip()
        if not g.isdigit() or not raw:
            continue
        gi = int(g)
        norm = app_mod._management_normalize_subject_label(raw)
        inc = app_mod._management_subject_in_overall_pass_computation(gi, norm)
        thr = app_mod._management_marks_pass_threshold_pct_for_subject(gi, norm)
        out_rows.append(
            {
                "grade": gi,
                "subjectRaw": raw,
                "subjectNormalized": norm,
                "includedInPromotion": inc,
                "minimumPercent": thr,
                "ruleBucket": _rule_bucket(app_mod, norm),
            }
        )

    # stdout: compact tables per grade
    from collections import defaultdict

    by_grade: dict[int, list[dict]] = defaultdict(list)
    for row in out_rows:
        by_grade[row["grade"]].append(row)

    for g in sorted(by_grade.keys()):
        print(f"\n=== Grade {g} ===")
        for row in sorted(by_grade[g], key=lambda x: x["subjectRaw"].lower()):
            inc = "yes" if row["includedInPromotion"] else "no"
            thr = row["minimumPercent"]
            thr_s = "—" if thr is None else f">= {thr:g}%"
            print(f"  {row['subjectRaw']}")
            print(f"    normalized: {row['subjectNormalized']}")
            print(f"    bucket: {row['ruleBucket']}")
            print(f"    included: {inc}  |  promotion minimum: {thr_s}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "grade",
                    "subjectRaw",
                    "subjectNormalized",
                    "includedInPromotion",
                    "minimumPercent",
                    "ruleBucket",
                ],
            )
            w.writeheader()
            for row in sorted(out_rows, key=lambda x: (x["grade"], x["subjectRaw"].lower())):
                w.writerow(row)
        print(f"\nWrote {args.csv}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out_rows, f, indent=2)
        print(f"Wrote {args.json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
