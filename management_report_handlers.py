"""
Management portal JSON builders (PostgreSQL / EMS). Imported by app.py — keep free of app circular imports.
"""
from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable

_PASS_DEFAULT = 40.0


def _normalize_subject_label(raw: str) -> str:
    """Strip EMS suffixes such as '(Gr 5)'."""
    return re.sub(r"\s*\(Gr\s+\d+\)\s*$", "", str(raw or "").strip(), flags=re.IGNORECASE)


def mr_row_pct(row: dict) -> float | None:
    try:
        m = float(row.get("Mark") or 0)
        t = float(row.get("TotalMark") or 0)
        if t <= 0:
            return None
        return float(Decimal(str(100.0 * m / t)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except (TypeError, ValueError):
        return None


def mr_level_band(pct: float) -> int:
    """Map percentage to display levels L1–L7 (higher = better)."""
    if pct >= 80:
        return 7
    if pct >= 70:
        return 6
    if pct >= 60:
        return 5
    if pct >= 50:
        return 4
    if pct >= 40:
        return 3
    if pct >= 30:
        return 2
    return 1


def mr_subject_aggregates(marks_rows: list[dict], pass_threshold: float = _PASS_DEFAULT) -> list[dict]:
    """Per subject: label, value (avg %), passRate (% learners >= threshold)."""
    by_sub: dict[str, list[float]] = defaultdict(list)
    for r in marks_rows or []:
        p = mr_row_pct(r)
        if p is None:
            continue
        sub = str(r.get("Subject") or "").strip()
        if not sub:
            continue
        by_sub[sub].append(p)
    out: list[dict] = []
    for sub, pcts in sorted(by_sub.items(), key=lambda x: x[0].lower()):
        n = len(pcts)
        avg = round(sum(pcts) / n, 2) if n else 0.0
        passed = sum(1 for x in pcts if x >= pass_threshold)
        pr = round(100.0 * passed / n, 2) if n else 0.0
        out.append({"label": sub, "value": avg, "passRate": pr})
    return out


def mr_chart_rows_from_subject_stats(stats: list[dict]) -> list[dict]:
    return [{"label": s["label"], "value": s["value"]} for s in stats]


def mr_kpi_core(marks_rows: list[dict], pass_threshold: float = _PASS_DEFAULT) -> dict[str, Any]:
    learners: set[str] = set()
    pcts: list[float] = []
    for r in marks_rows or []:
        lid = str(r.get("LearnerID") or "").strip()
        p = mr_row_pct(r)
        if p is None:
            continue
        if lid:
            learners.add(lid)
        pcts.append(p)
    n_pct = len(pcts)
    avg = round(sum(pcts) / n_pct, 2) if n_pct else None
    passed = sum(1 for x in pcts if x >= pass_threshold)
    pr = round(100.0 * passed / n_pct, 2) if n_pct else None
    return {
        "learners": len(learners) if learners else (1 if n_pct else 0),
        "records": n_pct,
        "avgPercent": avg,
        "passRate": pr,
    }


def mr_grade_distribution_from_promotion(grade_map: dict[str, str]) -> list[dict]:
    """grade_map: learner_id -> grade string."""
    counts: dict[str, int] = defaultdict(int)
    for g in grade_map.values():
        gs = str(g or "").strip()
        if gs:
            counts[gs] += 1
    return [{"label": f"Grade {k}", "value": v} for k, v in sorted(counts.items(), key=lambda x: (int(re.search(r"(\d+)", x[0]).group(1)) if re.search(r"(\d+)", x[0]) else 999, x[0]))]


def mr_distribution_groups_by_grade(
    marks_rows: list[dict],
    *,
    grade_key_fn: Callable[[dict], str | None],
    title_for_grade: Callable[[str], str] | None = None,
) -> list[dict]:
    by_g: dict[str, list[dict]] = defaultdict(list)
    for r in marks_rows or []:
        gk = grade_key_fn(r)
        if not gk:
            continue
        by_g[str(gk)].append(r)
    groups: list[dict] = []
    for g_label in sorted(by_g.keys(), key=lambda x: (int(re.search(r"(\d+)", x).group(1)) if re.search(r"(\d+)", str(x)) else 999, x)):
        rows_g = by_g[g_label]
        pcts = [p for r in rows_g for p in [mr_row_pct(r)] if p is not None]
        levels = [0] * 7
        for p in pcts:
            b = mr_level_band(p)
            if 1 <= b <= 7:
                levels[b - 1] += 1
        total = sum(levels)
        avg = round(sum(pcts) / len(pcts), 2) if pcts else 0.0
        totals = {
            "level1": levels[0],
            "level2": levels[1],
            "level3": levels[2],
            "level4": levels[3],
            "level5": levels[4],
            "level6": levels[5],
            "level7": levels[6],
            "absent": 0,
            "total": total,
        }
        title = title_for_grade(g_label) if title_for_grade else f"Grade {g_label}"
        groups.append(
            {
                "title": title,
                "rows": [
                    {
                        "gradeLabel": g_label,
                        "averagePct": avg,
                        "level1": levels[0],
                        "level2": levels[1],
                        "level3": levels[2],
                        "level4": levels[3],
                        "level5": levels[4],
                        "level6": levels[5],
                        "level7": levels[6],
                        "absent": 0,
                        "total": total,
                    }
                ],
                "totals": totals,
            }
        )
    return groups


def mr_results_rows_for_grade(marks_rows: list[dict]) -> list[dict]:
    by_sub: dict[str, list[float]] = defaultdict(list)
    for r in marks_rows or []:
        p = mr_row_pct(r)
        if p is None:
            continue
        by_sub[str(r.get("Subject") or "").strip()].append(p)
    rows: list[dict] = []
    for sub, pcts in sorted(by_sub.items(), key=lambda x: x[0].lower()):
        if not sub:
            continue
        levels = [0] * 7
        for p in pcts:
            b = mr_level_band(p)
            if 1 <= b <= 7:
                levels[b - 1] += 1
        total = sum(levels)
        rows.append(
            {
                "subject": sub,
                "averagePct": round(sum(pcts) / len(pcts), 2) if pcts else 0.0,
                "level1": levels[0],
                "level2": levels[1],
                "level3": levels[2],
                "level4": levels[3],
                "level5": levels[4],
                "level6": levels[5],
                "level7": levels[6],
                "absent": 0,
                "total": total,
            }
        )
    return rows


def mr_averages_grid_by_phase(marks_rows: list[dict], grade_from_row: Callable[[dict], str | None]) -> list[dict]:
    """Build groups with groupName = phase, subjects with g1..g12 avg columns."""
    phase_bucket = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # phase -> subject -> grade -> pcts
    phase_labels = {
        "Foundation": {1, 2, 3},
        "Intermediate": {4, 5, 6},
        "Senior": {7, 8, 9},
        "FET": {10, 11, 12},
    }

    def _gnum(s: str) -> int | None:
        m = re.search(r"(\d+)", str(s or ""))
        return int(m.group(1)) if m else None

    for r in marks_rows or []:
        gstr = grade_from_row(r)
        gn = _gnum(gstr)
        if gn is None:
            continue
        phase = "Other"
        for pname, grades in phase_labels.items():
            if gn in grades:
                phase = pname
                break
        p = mr_row_pct(r)
        if p is None:
            continue
        sub = str(r.get("Subject") or "").strip()
        if not sub:
            continue
        phase_bucket[phase][sub][str(gn)].append(p)

    groups: list[dict] = []
    order = ["Foundation", "Intermediate", "Senior", "FET", "Other"]
    for pname in order:
        if pname not in phase_bucket:
            continue
        subjects_out: list[dict] = []
        for sub in sorted(phase_bucket[pname].keys(), key=lambda x: x.lower()):
            row: dict[str, Any] = {"subject": sub}
            for gn in range(1, 13):
                pcts = phase_bucket[pname][sub].get(str(gn), [])
                row[f"g{gn}"] = round(sum(pcts) / len(pcts), 2) if pcts else None
            subjects_out.append(row)
        groups.append({"groupName": pname, "subjects": subjects_out})
    return groups


def mr_analysis_blocks(marks_rows: list[dict], grade_from_row: Callable[[dict], str | None]) -> list[dict]:
    """One block per (subject, grade) with term rows — single term in filter yields one row per block."""
    key_map: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in marks_rows or []:
        sub = str(r.get("Subject") or "").strip()
        g = grade_from_row(r) or ""
        if not sub or not g:
            continue
        p = mr_row_pct(r)
        if p is None:
            continue
        key_map[(sub, str(g))].append(p)

    blocks: list[dict] = []
    for (sub, g_label), pcts in sorted(key_map.items(), key=lambda x: (x[0][0].lower(), x[0][1])):
        levels = [0] * 7
        for p in pcts:
            b = mr_level_band(p)
            if 1 <= b <= 7:
                levels[b - 1] += 1
        total_l = sum(levels)
        avg = round(sum(pcts) / len(pcts), 2) if pcts else 0.0
        meet = sum(1 for x in pcts if x >= _PASS_DEFAULT)
        blocks.append(
            {
                "subject": _normalize_subject_label(sub),
                "gradeLabel": f"Grade {g_label}",
                "rows": [
                    {
                        "termLabel": "All",
                        "level1": levels[0],
                        "level2": levels[1],
                        "level3": levels[2],
                        "level4": levels[3],
                        "level5": levels[4],
                        "level6": levels[5],
                        "level7": levels[6],
                        "totalLearners": len(set()),  # placeholder
                        "averagePct": avg,
                        "absentCount": 0,
                        "meetingRequirements": meet,
                        "notMeetingRequirements": len(pcts) - meet,
                        "meetingRequirementsPct": round(100.0 * meet / len(pcts), 2) if pcts else 0.0,
                    }
                ],
            }
        )
        # fix totalLearners
        blocks[-1]["rows"][0]["totalLearners"] = len(pcts)
    return blocks


def mr_year_over_year_grade_averages(
    marks_by_year_grade: dict[tuple[str, str], list[float]],
    *,
    current_year: str,
    grade_label: str,
    term_label: str,
) -> dict[str, Any]:
    """For one grade: term1 = current year avg, py = previous years."""
    try:
        y_cur = int(float(str(current_year).strip()))
    except ValueError:
        y_cur = 0
    cur_key = (str(current_year).strip(), str(grade_label).strip())
    pcts_cur = marks_by_year_grade.get(cur_key, [])
    t1 = round(sum(pcts_cur) / len(pcts_cur), 2) if pcts_cur else None

    def _avg_for(yd: int):
        key = (str(yd), str(grade_label).strip())
        pp = marks_by_year_grade.get(key, [])
        return round(sum(pp) / len(pp), 2) if pp else None

    py = _avg_for(y_cur - 1)
    py2 = _avg_for(y_cur - 2)
    py3 = _avg_for(y_cur - 3)

    def _diff(a, b):
        if a is None or b is None:
            return None
        return round(float(a) - float(b), 2)

    return {
        "grade": grade_label,
        "term1": t1,
        "py": py,
        "diffPy": _diff(t1, py) if t1 is not None else None,
        "py2": py2,
        "diffPy2": _diff(t1, py2) if t1 is not None else None,
        "py3": py3,
        "diffPy3": _diff(t1, py3) if t1 is not None else None,
    }


def mr_schoolwide_year_averages(
    marks_by_year: dict[str, list[float]],
    *,
    current_year: str,
    term_label: str,
) -> dict[str, Any]:
    try:
        y_cur = int(float(str(current_year).strip()))
    except ValueError:
        y_cur = 0

    def _avg(ys: str):
        pp = marks_by_year.get(str(ys).strip(), [])
        return round(sum(pp) / len(pp), 2) if pp else None

    t1 = _avg(str(current_year).strip())
    py = _avg(str(y_cur - 1)) if y_cur else None
    py2 = _avg(str(y_cur - 2)) if y_cur else None
    py3 = _avg(str(y_cur - 3)) if y_cur else None

    def _diff(a, b):
        if a is None or b is None:
            return None
        return round(float(a) - float(b), 2)

    return {
        "grade": "All",
        "term1": t1,
        "py": py,
        "diffPy": _diff(t1, py) if t1 is not None else None,
        "py2": py2,
        "diffPy2": _diff(t1, py2) if t1 is not None else None,
        "py3": py3,
        "diffPy3": _diff(t1, py3) if t1 is not None else None,
    }
