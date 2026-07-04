#!/usr/bin/env python3
"""
Cross-check LearnerPromotion text codes (e.g. P / NP) against promoted vs failed counts.

Queries `LearnerPromotion` joined to `ReportCycles` when possible; falls back to year-only.

Usage (repo root, POSTGRES_DATABASE_URL in .env):

    python scripts/audit_promotion_codes.py 2026 1
    python scripts/audit_promotion_codes.py 2026 1 --grade 5
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, ".env"))


def _norm(v) -> str:
    return str(v if v is not None else "").strip().upper()


def _cell(row: dict, *keys: str) -> str:
    for k in keys:
        if k in row and row.get(k) is not None and str(row.get(k)).strip() != "":
            return _norm(row.get(k))
        lk = k.lower()
        for rk in row:
            if str(rk).lower() == lk:
                if row.get(rk) is not None and str(row.get(rk)).strip() != "":
                    return _norm(row.get(rk))
    return ""


def classify_promotion_row(row: dict) -> tuple[str, str]:
    """Return (bucket, reason) with bucket in promoted | progressed | failed | unknown.

    Matches EMS exports seen in this project: ``CodeSelected`` / ``CodeAuto`` / ``CodeSched``
    hold ``P``, ``NP``, ``PG``; ``PromotionDecision`` often ``6`` (pass) vs ``14`` (fail).
    Precedence: ``CodeSched == PG`` → progressed; else any ``NP`` → failed; else all ``P`` → promoted;
    else fall back to ``PromotionDecision``.
    """

    sel = _cell(row, "CodeSelected", "codeselected")
    auto = _cell(row, "CodeAuto", "codeauto")
    sched = _cell(row, "CodeSched", "codesched")
    pd_raw = row.get("PromotionDecision")
    if pd_raw is None:
        for rk in row:
            if str(rk).lower() == "promotiondecision":
                pd_raw = row.get(rk)
                break
    pd_s = _norm(pd_raw)

    codes_present = bool(sel or auto or sched or pd_s)

    # Progressed (many exports put PG on CodeSched even when CodeAuto is NP)
    if sched == "PG" or "PROGRESSED" in sched:
        return "progressed", "CodeSched=PG (progressed)"

    # Not progressed
    if sel == "NP" or auto == "NP" or sched == "NP":
        return "failed", "NP on CodeSelected/CodeAuto/CodeSched"

    if pd_s == "14":
        return "failed", "PromotionDecision=14"

    # Promoted / passed on codes (require literal P on at least one field)
    has_p = sel == "P" or auto == "P" or sched == "P"
    has_np = sel == "NP" or auto == "NP" or sched == "NP"
    if has_p and not has_np:
        if sel == "P" and auto == "P" and sched == "P":
            return "promoted", "P on Selected, Auto, Sched"
        return "promoted", "P on one or more code fields (no NP)"

    if pd_s == "6":
        return "promoted", "PromotionDecision=6"

    if not codes_present:
        return "unknown", "all code fields empty"

    return "unknown", f"unmatched: Sel={sel!r} Auto={auto!r} Sched={sched!r} Dec={pd_s!r}"


def fetch_promotion_rows(mdb_conn, year: str, term: str, *, year_only: bool) -> list[dict]:
    sel = (
        "SELECT CSTR(lp.LearnerId) AS LearnerID, CSTR(lp.Grade) AS Grade, "
        "lp.CodeSelected, lp.CodeAuto, lp.CodeSched, lp.PromotionDecision "
        "FROM LearnerPromotion lp"
    )
    if year_only:
        attempts = [
            (sel + " WHERE CSTR(lp.DataYear)=?", (year,)),
            (sel + " WHERE CSTR(lp.Datayear)=?", (year,)),
        ]
    else:
        attempts = [
            (
                sel
                + ", ReportCycles rc WHERE lp.ReportId = rc.CycleId AND CSTR(lp.DataYear)=? AND CSTR(rc.Term)=?",
                (year, term),
            ),
            (
                sel
                + ", ReportCycles rc WHERE lp.ReportId = rc.CycleId AND CSTR(lp.Datayear)=? AND CSTR(rc.Term)=?",
                (year, term),
            ),
            (sel + " WHERE CSTR(lp.DataYear)=?", (year,)),
            (sel + " WHERE CSTR(lp.Datayear)=?", (year,)),
        ]
    for q, params in attempts:
        rows = mdb_conn.execute_query(q, params) or []
        if rows:
            return rows
    return []


def _codes_nonempty_fraction(rows: list[dict]) -> float:
    if not rows:
        return 0.0
    n = 0
    for r in rows:
        if _cell(r, "CodeSelected", "codeselected") or _cell(r, "CodeAuto", "codeauto") or _cell(r, "CodeSched", "codesched"):
            n += 1
        elif _norm(r.get("PromotionDecision")):
            n += 1
    return n / len(rows)


def dedupe_rows(rows: list[dict]) -> list[dict]:
    """Keep first row per (grade, learner) like Result Analysis promotion iterator."""
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for r in rows:
        lid = str(r.get("LearnerID") or "").strip()
        g = str(r.get("Grade") or "").strip()
        if not lid or not g.isdigit():
            continue
        key = (g, lid)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("year")
    parser.add_argument("term")
    parser.add_argument("--grade", help="Only this grade (e.g. 5)")
    parser.add_argument(
        "--year-only",
        action="store_true",
        help="Ignore ReportCycles term filter; use LearnerPromotion rows for the year only (codes often populated here).",
    )
    args = parser.parse_args()
    year, term = args.year.strip(), args.term.strip()

    if not os.environ.get("POSTGRES_DATABASE_URL"):
        print("POSTGRES_DATABASE_URL is not set.", file=sys.stderr)
        return 1

    import app as app_mod

    app = app_mod.app
    with app.app_context():
        rows = fetch_promotion_rows(app_mod.mdb_conn, year, term, year_only=args.year_only)

    rows = dedupe_rows(rows)

    # Term-linked exports sometimes return promotion rows with blank code columns while year-wide rows carry P/NP.
    if not args.year_only and rows and _codes_nonempty_fraction(rows) < 0.05:
        with app.app_context():
            alt = fetch_promotion_rows(app_mod.mdb_conn, year, term, year_only=True)
        alt = dedupe_rows(alt)
        if _codes_nonempty_fraction(alt) > _codes_nonempty_fraction(rows):
            rows = alt
            print("(Note: cycle-linked rows had empty codes; switched to year-wide LearnerPromotion for this audit.)")
            print()
    if args.grade:
        g = str(args.grade).strip()
        rows = [r for r in rows if str(r.get("Grade") or "").strip() == g]

    buckets = Counter()
    reasons = Counter()
    code_combo = Counter()
    raw_cs = Counter()
    raw_ca = Counter()
    raw_sched = Counter()
    raw_pd = Counter()

    for r in rows:
        cs = _cell(r, "CodeSelected", "codeselected")
        ca = _cell(r, "CodeAuto", "codeauto")
        sc = _cell(r, "CodeSched", "codesched")
        pd_raw = r.get("PromotionDecision")
        if pd_raw is None:
            for rk in r:
                if str(rk).lower() == "promotiondecision":
                    pd_raw = r.get(rk)
                    break
        pd = _norm(pd_raw)

        raw_cs[cs or "(empty)"] += 1
        raw_ca[ca or "(empty)"] += 1
        raw_sched[sc or "(empty)"] += 1
        raw_pd[pd or "(empty)"] += 1
        combo = f"Sel={cs or '-'} | Auto={ca or '-'} | Sched={sc or '-'} | Dec={pd or '-'}"
        code_combo[combo] += 1

        b, why = classify_promotion_row(r)
        buckets[b] += 1
        reasons[f"{b}: {why}"] += 1

    promoted_like = buckets["promoted"] + buckets["progressed"]
    failed_like = buckets["failed"]
    unknown_ct = buckets["unknown"]

    print(f"Year={year} Term={term}  rows(after dedupe" + (f", grade={args.grade}" if args.grade else "") + f"): {len(rows)}")
    print()
    print("=== Classification (P / NP style — see classify_promotion_row in script) ===")
    print(f"  promoted (strict): {buckets['promoted']}")
    print(f"  progressed:       {buckets['progressed']}")
    print(f"  promoted+progressed (report ‘passed register’ style): {promoted_like}")
    print(f"  failed (NP etc.):  {failed_like}")
    print(f"  unknown / blank: {unknown_ct}")
    print()
    print("=== Top CodeSelected values ===")
    for k, v in raw_cs.most_common(25):
        print(f"  {k!r}: {v}")
    print()
    print("=== Top CodeAuto values ===")
    for k, v in raw_ca.most_common(25):
        print(f"  {k!r}: {v}")
    print()
    print("=== Top CodeSched values ===")
    for k, v in raw_sched.most_common(25):
        print(f"  {k!r}: {v}")
    print()
    print("=== Top PromotionDecision values ===")
    for k, v in raw_pd.most_common(25):
        print(f"  {k!r}: {v}")
    print()
    print("=== Sample distinct code combinations (up to 40) ===")
    for k, v in code_combo.most_common(40):
        print(f"  [{v:4}] {k}")
    print()
    print("=== Classification reasons (collapsed) ===")
    for k, v in reasons.most_common(50):
        print(f"  [{v:4}] {k}")

    summary = {
        "year": year,
        "term": term,
        "gradeFilter": args.grade,
        "rowCount": len(rows),
        "buckets": dict(buckets),
        "promotedPlusProgressed": promoted_like,
        "failed": failed_like,
        "unknown": unknown_ct,
        "codeSelected": dict(raw_cs),
        "codeAuto": dict(raw_ca),
    }
    print()
    print("=== JSON summary ===")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
