"""
Admin portal routes (communication, detention, user management, etc.).
Registered from app.py after the Flask app is created.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import threading
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename


def root():
    import sys

    main = sys.modules.get("__main__")
    if getattr(main, "User", None) is not None and getattr(main, "db", None) is not None:
        return main
    import app as app_module

    return app_module


def _detention_pdf_esc(text: str) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


_DETENTION_PHASE_GRADES: dict[str, tuple[int, ...]] = {
    "foundation": (3,),
    "primary": (4, 5, 6, 7),
    "highschool": (8, 9, 10, 11, 12),
}

_HHMM_TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def _validate_detention_hhmm(value: str) -> str | None:
    """Return normalized HH:MM or None if invalid."""
    s = str(value or "").strip()
    if not s:
        return None
    m = _HHMM_TIME_RE.match(s)
    if not m:
        return None
    return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"


def _parse_detention_grades_filter(phase: str, raw) -> list[int]:
    """Grades within the phase band; empty list means no grade filter (all in phase)."""
    phase_key = str(phase or "").strip().lower()
    allowed = set(_DETENTION_PHASE_GRADES.get(phase_key, ()))
    if not allowed:
        return []
    nums: list[int] = []
    if raw is None:
        return []
    items: list = list(raw) if isinstance(raw, (list, tuple)) else [raw]
    for item in items:
        for part in str(item).split(","):
            part = part.strip()
            if not part:
                continue
            try:
                n = int(part)
            except ValueError:
                continue
            if n in allowed and n not in nums:
                nums.append(n)
    return sorted(nums)


def _detention_grades_from_request_args(phase: str) -> list[int]:
    parts: list[str] = []
    for g in request.args.getlist("grades"):
        parts.append(str(g))
    if not parts:
        single = str(request.args.get("grades", "") or "").strip()
        if single:
            parts = [single]
    return _parse_detention_grades_filter(phase, parts)


def _load_detention_schedule_times(
    mdb_conn,
    phase: str = "",
    start_override: str | None = None,
    end_override: str | None = None,
) -> tuple[str, str]:
    start_norm = _validate_detention_hhmm(start_override) if start_override else None
    end_norm = _validate_detention_hhmm(end_override) if end_override else None
    if start_norm and end_norm:
        return start_norm, end_norm
    # Foundation Phase uses a dedicated time slot
    if str(phase or "").strip().lower() == "foundation":
        return "13:20", "14:20"
    env_s = (os.environ.get("DETENTION_START_TIME") or "").strip()
    env_e = (os.environ.get("DETENTION_END_TIME") or "").strip()
    if env_s and env_e:
        return env_s, env_e
    try:
        rows = mdb_conn.execute_query(
            "SELECT TOP 1 StartTime, EndTime FROM DetentionNotificationSettings ORDER BY Id",
            (),
        ) or []
        if rows:
            st = str(rows[0].get("StartTime") or "").strip()
            et = str(rows[0].get("EndTime") or "").strip()
            if st and et:
                return st, et
    except Exception:
        pass
    return "13:50", "14:50"


def _fmt_incident_date(val) -> str:
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        try:
            return val.strftime("%Y-%m-%d")
        except Exception:
            pass
    s = str(val).strip()
    if " " in s:
        s = s.split()[0]
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return s[:24]


def _incident_sort_ts(val) -> float:
    s = _fmt_incident_date(val)
    if not s or len(s) < 10:
        return 0.0
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").timestamp()
    except ValueError:
        return 0.0


def _num_cell(v) -> str:
    if v is None or v == "":
        return "0"
    try:
        n = float(v)
        if abs(n - round(n)) < 1e-9:
            return str(int(round(n)))
        return f"{n:.1f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return str(v)[:12]


def _row_points_balance(dem, mer) -> int:
    try:
        d = float(dem or 0)
    except (TypeError, ValueError):
        d = 0.0
    try:
        m = float(mer or 0)
    except (TypeError, ValueError):
        m = 0.0
    return int(round(d - m))


def _detention_pdf_points_float(v) -> int:
    """Parse a Demerit/Merit value from a DB row as an integer."""
    try:
        return int(round(float(v or 0)))
    except (TypeError, ValueError):
        return 0


def _norm_learner_id_key(val: object) -> str:
    """Normalize DB/driver learner id strings (e.g. '42.0' -> '42')."""
    s = str(val or "").strip()
    if s.endswith(".0") and s[:-2].isdigit():
        return s[:-2]
    return s


def _fetch_disciplinary_rows_for_notice(
    mdb_conn,
    learner_keys: list[str],
    year: str,
) -> dict[str, list[dict]]:
    """Return {Learner_Info.ID: [rows from DisciplinaryRecords]} for the data year.

    Always resolves `DisciplinaryRecords.Learnerid` through `Learner_Info` so rows
    attach to the same internal learner ids used by detention generation. Uses
    `DisciplinaryRecords.[Date]` as the incident time (aliased as `IncidentDate` for
    the PDF) because PostgreSQL mirrors often have no `IncidentDate` column—referencing
    it inside `COALESCE` would invalidate the entire query.
    """
    out: dict[str, list[dict]] = {}
    ids = [_norm_learner_id_key(x) for x in (learner_keys or []) if str(x).strip()]
    if not ids:
        return out
    y = str(year or "").strip()
    chunk = 80
    for i in range(0, len(ids), chunk):
        part = ids[i : i + chunk]
        ph = "(" + ",".join(["?"] * len(part)) + ")"
        # INNER JOIN: every returned row has a resolved Learner_Info.ID (LearnerKey).
        q = f"""
            SELECT CSTR(li.[ID]) AS LearnerKey,
                   dr.[Date] AS IncidentDate,
                   dr.LevelMisconduct,
                   dr.MisconductDescription,
                   dr.Demerit,
                   dr.Merit,
                   dr.AuthorisedBy
            FROM DisciplinaryRecords dr
            INNER JOIN Learner_Info li ON (
                 CSTR(li.[ID]) = CSTR(dr.Learnerid)
              OR CSTR(li.[LearnerID]) = CSTR(dr.Learnerid)
              OR CSTR(li.[AccessionNo]) = CSTR(dr.Learnerid)
            )
            WHERE TRIM(CSTR(dr.[Datayear])) = TRIM(?)
              AND CSTR(li.[ID]) IN {ph}
            ORDER BY dr.[Date] DESC NULLS LAST
        """
        params = tuple([y] + part)
        rows = mdb_conn.execute_query(q, params) or []
        if not rows and y.isdigit():
            q2 = f"""
                SELECT CSTR(li.[ID]) AS LearnerKey,
                       dr.[Date] AS IncidentDate,
                       dr.LevelMisconduct,
                       dr.MisconductDescription,
                       dr.Demerit,
                       dr.Merit,
                       dr.AuthorisedBy
                FROM DisciplinaryRecords dr
                INNER JOIN Learner_Info li ON (
                     CSTR(li.[ID]) = CSTR(dr.Learnerid)
                  OR CSTR(li.[LearnerID]) = CSTR(dr.Learnerid)
                  OR CSTR(li.[AccessionNo]) = CSTR(dr.Learnerid)
                )
                WHERE CAST(CSTR(dr.[Datayear]) AS INTEGER) = ?
                  AND CSTR(li.[ID]) IN {ph}
                ORDER BY dr.[Date] DESC NULLS LAST
            """
            rows = mdb_conn.execute_query(q2, tuple([int(y)] + part)) or []
        want = set(part)
        for r in rows:
            key = _norm_learner_id_key(r.get("LearnerKey"))
            if not key or key not in want:
                continue
            shaped = {
                "IncidentDate": r.get("IncidentDate") or r.get("Date"),
                "LevelMisconduct": r.get("LevelMisconduct"),
                "MisconductDescription": r.get("MisconductDescription"),
                "Demerit": r.get("Demerit"),
                "Merit": r.get("Merit"),
                "AuthorisedBy": r.get("AuthorisedBy"),
            }
            out.setdefault(key, []).append(shaped)
    return out


def _resolve_letterhead_path(app_root_path: str | None, phase: str) -> Path | None:
    phase_key = (phase or "").strip().lower()
    phase_aliases = {
        "foundation": ["foundation"],
        "primary": ["primary"],
        "highschool": ["highschool", "high_school", "high-school"],
    }.get(phase_key, [phase_key]) if phase_key else []
    env_lh = (os.environ.get("SCHOOL_LETTERHEAD_PATH") or "").strip()
    candidates: list[Path] = []
    if env_lh:
        candidates.append(Path(env_lh))
    roots: list[Path] = []
    if app_root_path:
        roots.append(Path(app_root_path))
    roots.append(Path.cwd())
    seen: set[Path] = set()
    for rt in roots:
        if rt in seen:
            continue
        seen.add(rt)
        disc_dir = rt / "static" / "uploads" / "disciplinary" / "images"
        if disc_dir.is_dir():
            files = list(disc_dir.glob("*letterhead*.png")) + list(disc_dir.glob("*letterhead*.jpg"))
            if phase_aliases:
                for alias in phase_aliases:
                    matched = [f for f in files if alias in f.name.lower()]
                    matched.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    candidates.extend(matched)
            files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            candidates.extend(files)
        candidates.append(rt / "static" / "images" / "school-logo.png")
    for c in candidates:
        try:
            if c and c.is_file():
                return c
        except OSError:
            continue
    return None


def _letterhead_flowable(letterhead_path: Path | None, frame_width: float):
    if letterhead_path is None:
        return None
    try:
        from reportlab.lib.utils import ImageReader
        from reportlab.platypus import Image
    except ImportError:
        return None
    try:
        ir = ImageReader(str(letterhead_path))
        iw, ih = ir.getSize()
    except Exception:
        return None
    if iw <= 0 or ih <= 0:
        return None
    scaled_h = frame_width * (ih / iw)
    max_h = 1.0 * 72  # 1.0 inch cap so the letterhead leaves room for content
    if scaled_h > max_h:
        scaled_h = max_h
    scaled_w = scaled_h * (iw / ih)
    if scaled_w > frame_width:
        scaled_w = frame_width
        scaled_h = scaled_w * (ih / iw)
    img = Image(str(letterhead_path), width=scaled_w, height=scaled_h)
    img.hAlign = "CENTER"
    return img


def _draw_copy_watermark(canvas, doc) -> None:
    from reportlab.lib import colors

    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 110)
    try:
        canvas.setFillColor(colors.Color(0.5, 0.5, 0.5, alpha=0.55))
    except TypeError:
        canvas.setFillColor(colors.Color(0.5, 0.5, 0.5))
    page_w, page_h = canvas._pagesize
    canvas.translate(page_w / 2.0, page_h / 2.0)
    canvas.rotate(45)
    canvas.drawCentredString(0, -20, "COPY")
    canvas.restoreState()


def _build_learner_notice_flowables(
    *,
    styles,
    doc_width: float,
    letterhead_path: Path | None,
    school_title: str,
    detention_dt: datetime,
    start_time: str,
    end_time: str,
    learner_id: str,
    info: dict,
    demerit_rows: list[dict],
) -> list:
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    fname = str(info.get("fname") or "").strip()
    sname = str(info.get("sname") or "").strip()
    grade = str(info.get("grade") or "").strip()
    hdr_date = detention_dt.strftime("%Y-%m-%d")
    out: list = []
    lh_img = _letterhead_flowable(letterhead_path, doc_width)
    if lh_img is not None:
        out.append(lh_img)
        out.append(Spacer(1, 0.08 * inch))
    else:
        out.append(Paragraph(_detention_pdf_esc(school_title), styles["Title"]))
        out.append(Spacer(1, 0.06 * inch))
    out.append(Paragraph("Dear Parent,", styles["DetNoticeBody"]))
    out.append(
        Paragraph(
            "<b>NOTIFICATION THAT YOUR CHILD IS REQUIRED TO ATTEND DETENTION.</b> Your child is required to attend "
            "detention as they have contravened the school's Code of Conduct. Details of offences are listed in the "
            "demerit account below. To cancel accumulated demerit points, your child must attend detention. Normal "
            "school rules apply during detention and school uniform is required.",
            styles["DetNoticeBody"],
        )
    )
    out.append(Spacer(1, 0.04 * inch))
    out.append(Paragraph("<b>Detention Notification</b>", styles["DetNoticeCenterHeading"]))
    out.append(
        Paragraph(
            f"<b>Date of Detention:</b> {_detention_pdf_esc(hdr_date)}<br/>"
            f"<b>Start Time:</b> {_detention_pdf_esc(start_time)} &nbsp; "
            f"<b>End Time:</b> {_detention_pdf_esc(end_time)}",
            styles["DetNoticeCenterBody"],
        )
    )
    out.append(
        Paragraph(
            "Please arrange for transport. The school will not be held responsible for learners who fail to attend "
            "or leave the premises unsupervised.",
            styles["DetNoticeSmall"],
        )
    )
    out.append(Spacer(1, 0.06 * inch))
    tw = doc_width
    # Wider "Surname" label column than "Name"/"Grade" so the label does not crowd the value.
    lbl_name = 0.54 * inch
    lbl_surname = 0.78 * inch
    lbl_grade = 0.52 * inch
    grade_val_w = 0.52 * inch
    remaining = tw - lbl_name - lbl_surname - lbl_grade - grade_val_w
    name_val_w = remaining * 0.34
    sname_val_w = remaining - name_val_w
    info_tbl = Table(
        [
            [
                "Name",
                _detention_pdf_esc(fname or "—"),
                "Surname",
                _detention_pdf_esc(sname or "—"),
                "Grade",
                _detention_pdf_esc(grade or "—"),
            ],
        ],
        colWidths=[lbl_name, name_val_w, lbl_surname, sname_val_w, lbl_grade, grade_val_w],
    )
    info_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
                ("FONTNAME", (4, 0), (4, 0), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, 0), "Helvetica"),
                ("FONTNAME", (3, 0), (3, 0), "Helvetica"),
                ("FONTNAME", (5, 0), (5, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # Extra horizontal padding so label/value pairs (esp. Surname) read as separate cells.
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    out.append(info_tbl)
    out.append(Spacer(1, 0.04 * inch))
    # Balance summary block
    tot_demerit = sum(
        _detention_pdf_points_float(r.get("Demerit")) for r in (demerit_rows or [])
    )
    tot_merit = sum(
        _detention_pdf_points_float(r.get("Merit")) for r in (demerit_rows or [])
    )
    total_bal = tot_demerit - tot_merit
    bal_tbl = Table(
        [
            ["Total Demerits", str(tot_demerit), "Total Merits", str(tot_merit), "Balance", str(total_bal)],
        ],
        colWidths=[tw * 0.20, tw * 0.13, tw * 0.20, tw * 0.13, tw * 0.17, tw * 0.17],
    )
    bal_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
                ("FONTNAME", (4, 0), (4, 0), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (3, 0), "Helvetica"),
                ("FONTNAME", (5, 0), (5, 0), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    out.append(bal_tbl)
    out.append(Spacer(1, 0.08 * inch))
    acc_title = f"Demerit Account for {_detention_pdf_esc((fname + ' ' + sname).strip() or learner_id)}"
    out.append(Paragraph(f"<b>{acc_title}</b>", styles["Heading2"]))
    dem_rows = sorted(
        list(demerit_rows or []),
        key=lambda r: _incident_sort_ts(r.get("IncidentDate")),
        reverse=True,
    )
    tbl_header = ["Date", "Level", "Description", "Demerit", "Merit", "Balance", "Authorised By"]
    data: list[list] = [tbl_header]
    for dr in dem_rows:
        desc = str(dr.get("MisconductDescription") or "").strip()
        if len(desc) > 220:
            desc = desc[:217] + "..."
        bal = _row_points_balance(dr.get("Demerit"), dr.get("Merit"))
        data.append(
            [
                _detention_pdf_esc(_fmt_incident_date(dr.get("IncidentDate"))),
                _detention_pdf_esc(str(dr.get("LevelMisconduct") or "").strip()),
                Paragraph(_detention_pdf_esc(desc), styles["DetNoticeSmall"]),
                _num_cell(dr.get("Demerit")),
                _num_cell(dr.get("Merit")),
                str(bal),
                _detention_pdf_esc(str(dr.get("AuthorisedBy") or "").strip()[:60]),
            ]
        )
    if len(data) == 1:
        data.append([
            "—",
            "—",
            Paragraph("<i>No disciplinary rows for this data year.</i>", styles["DetNoticeSmall"]),
            "",
            "",
            "",
            "",
        ])
    fixed_w = 0.72 * inch + 0.5 * inch + 0.52 * inch + 0.48 * inch + 0.48 * inch + 1.35 * inch
    desc_w = max(doc_width - fixed_w, 1.2 * inch)
    tbl = Table(
        data,
        colWidths=[0.72 * inch, 0.5 * inch, desc_w, 0.52 * inch, 0.48 * inch, 0.48 * inch, 1.35 * inch],
        repeatRows=1,
    )
    tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("ALIGN", (3, 0), (5, -1), "CENTER"),
            ]
        )
    )
    out.append(tbl)
    out.append(Spacer(1, 0.08 * inch))
    out.append(Paragraph("<b>FOR COMPLETION BY PARENT</b>", styles["Heading3"]))
    out.append(
        Paragraph(
            "Tick your option: I have noted the contents of the Detention Notification and:",
            styles["DetNoticeBody"],
        )
    )
    tick_rows = [
        ["", Paragraph("Will ensure that my child attends as required.", styles["DetNoticeBody"])],
        [
            "",
            Paragraph(
                "Regret that my child cannot attend for the reason listed below.",
                styles["DetNoticeBody"],
            ),
        ],
        [
            Paragraph("<b>Reason</b>", styles["DetNoticeSmall"]),
            Paragraph("&nbsp;", styles["DetNoticeBody"]),
        ],
    ]
    # Left column must fit "Reason" on one line (0.45in caused "Reas" / "on" wrap).
    tick_left_w = max(1.05 * inch, doc_width * 0.14)
    tick_tbl = Table(
        tick_rows,
        colWidths=[tick_left_w, doc_width - tick_left_w],
        rowHeights=[0.28 * inch, 0.28 * inch, 0.6 * inch],
    )
    tick_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("BACKGROUND", (0, 0), (0, 1), colors.HexColor("#f5f7fb")),
                ("ALIGN", (0, 0), (0, 1), "CENTER"),
            ]
        )
    )
    out.append(tick_tbl)
    out.append(Spacer(1, 0.08 * inch))
    sig_tbl = Table(
        [
            [
                Paragraph("<b>Parent / Guardian Signature</b>", styles["DetNoticeSmall"]),
                Paragraph("<b>Date</b>", styles["DetNoticeSmall"]),
            ],
            [
                Paragraph("&nbsp;", styles["DetNoticeBody"]),
                Paragraph("&nbsp;", styles["DetNoticeBody"]),
            ],
        ],
        colWidths=[doc_width * 0.65, doc_width * 0.35],
        rowHeights=[0.2 * inch, 0.4 * inch],
    )
    sig_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5f7fb")),
            ]
        )
    )
    out.append(sig_tbl)
    return out


def _write_detention_notifications_pdf(
    path: Path,
    *,
    school_title: str,
    detention_dt: datetime,
    start_time: str,
    end_time: str,
    learner_order: list[str],
    learner_rows: list[dict],
    demerits_by_learner: dict[str, list[dict]],
    letterhead_path: Path | None = None,
) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import BaseDocTemplate, Frame, NextPageTemplate, PageBreak, PageTemplate

    path.parent.mkdir(parents=True, exist_ok=True)
    lookup = {str(x.get("id") or ""): x for x in learner_rows or []}
    notice_order = sorted(learner_order, key=lambda lid: _learner_grade_sort_key(lid, lookup))
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=40,
        title="Detention notifications",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="content",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="normal", frames=[frame]),
            PageTemplate(id="copy", frames=[frame], onPageEnd=_draw_copy_watermark),
        ]
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="DetNoticeBody",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DetNoticeSmall",
            parent=styles["Normal"],
            fontSize=7,
            leading=9,
        )
    )
    from reportlab.lib.enums import TA_CENTER

    styles.add(
        ParagraphStyle(
            name="DetNoticeCenterHeading",
            parent=styles["Heading2"],
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DetNoticeCenterBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=4,
        )
    )
    story: list = []
    for li, lid in enumerate(notice_order):
        info = lookup.get(str(lid)) or {}
        dem_rows = list(demerits_by_learner.get(str(lid)) or demerits_by_learner.get(lid) or [])
        flowables = _build_learner_notice_flowables(
            styles=styles,
            doc_width=doc.width,
            letterhead_path=letterhead_path,
            school_title=school_title,
            detention_dt=detention_dt,
            start_time=start_time,
            end_time=end_time,
            learner_id=str(lid),
            info=info,
            demerit_rows=dem_rows,
        )
        if li == 0:
            story.append(NextPageTemplate("normal"))
        story.extend(flowables)
        story.append(NextPageTemplate("copy"))
        story.append(PageBreak())
        story.extend(
            _build_learner_notice_flowables(
                styles=styles,
                doc_width=doc.width,
                letterhead_path=letterhead_path,
                school_title=school_title,
                detention_dt=detention_dt,
                start_time=start_time,
                end_time=end_time,
                learner_id=str(lid),
                info=info,
                demerit_rows=dem_rows,
            )
        )
        if li < len(notice_order) - 1:
            story.append(NextPageTemplate("normal"))
            story.append(PageBreak())
    doc.build(story)


def _learner_grade_sort_key(learner_id: str, lookup: dict) -> tuple:
    """Sort key: grade ascending, then surname, first name, id (attendance + notice PDFs)."""
    info = lookup.get(str(learner_id)) or {}
    g_raw = str(info.get("grade") or "").strip()
    m = re.search(r"(\d+)", g_raw)
    grade_num = int(m.group(1)) if m else 10**6
    sname = str(info.get("sname") or "").strip().lower()
    fname = str(info.get("fname") or "").strip().lower()
    return (grade_num, sname, fname, str(learner_id))


def _write_detention_attendance_pdf(
    path: Path,
    *,
    school_title: str,
    phase_register_label: str,
    nice_date: str,
    educator: str,
    start_time: str,
    learner_order: list[str],
    learner_rows: list[dict],
    letterhead_path: Path | None = None,
) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    path.parent.mkdir(parents=True, exist_ok=True)
    lookup = {str(x.get("id") or ""): x for x in learner_rows or []}
    register_order = sorted(learner_order, key=lambda lid: _learner_grade_sort_key(lid, lookup))
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=40,
        title="Detention attendance register",
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="RegTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RegMeta",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RegNote",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#444444"),
        )
    )
    story: list = []
    lh_img = _letterhead_flowable(letterhead_path, doc.width)
    if lh_img is not None:
        story.append(lh_img)
        story.append(Spacer(1, 0.1 * inch))
    else:
        story.append(Paragraph(_detention_pdf_esc(school_title), styles["Title"]))
        story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("DETENTION ATTENDANCE REGISTER", styles["RegTitle"]))
    story.append(Spacer(1, 0.04 * inch))
    educator_display = _detention_pdf_esc(educator) if educator else "..."
    story.append(
        Paragraph(
            f"<b>Date:</b> {_detention_pdf_esc(nice_date)} &nbsp;&nbsp; <b>Educator:</b> {educator_display}",
            styles["RegMeta"],
        )
    )
    story.append(
        Paragraph(
            f"<b>Phase:</b> {_detention_pdf_esc(phase_register_label)} &nbsp;&nbsp; <b>Time:</b> {_detention_pdf_esc(start_time)}",
            styles["RegMeta"],
        )
    )
    story.append(Spacer(1, 0.14 * inch))
    hdr = ["Name", "Grade", "Time", "Signature", "Remarks"]
    data: list[list] = [hdr]
    for lid in register_order:
        info = lookup.get(str(lid)) or {}
        fname = str(info.get("fname") or "").strip()
        sname = str(info.get("sname") or "").strip()
        full = f"{fname} {sname}".strip() or str(lid)
        data.append([_detention_pdf_esc(full), str(info.get("grade") or "").strip(), start_time, "", ""])
    tw = doc.width
    tbl = Table(
        data,
        colWidths=[tw * 0.36, tw * 0.1, tw * 0.12, tw * 0.22, tw * 0.2],
        repeatRows=1,
    )
    tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9.5),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("ALIGN", (1, 1), (2, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 0.14 * inch))
    story.append(
        Paragraph(
            "<i>Note: Please ensure all learners sign the register upon arrival.</i>",
            styles["RegNote"],
        )
    )
    doc.build(story)


def register_admin_routes(flask_app: Flask) -> None:
    r = root()

    def require_admin():
        if not current_user.is_authenticated or not r.is_admin_user(current_user):
            abort(403)

    def _comm_batch_id() -> str:
        return uuid.uuid4().hex

    def _log_delivery(
        *,
        batch_id: str,
        category: str,
        channel: str,
        phone: str,
        message: str,
        status: str,
        recipient_name: str | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
        err: str | None = None,
    ):
        row = r.CommunicationDeliveryLog(
            category=category,
            reference_type=reference_type,
            reference_id=reference_id,
            recipient_name=recipient_name,
            recipient_phone=phone,
            channel=channel,
            message_snapshot=message[:8000],
            sent_by_user_id=getattr(current_user, "id", None),
            sent_by_username=getattr(current_user, "username", None),
            status=status,
            error_message=(err or None),
            batch_id=batch_id,
        )
        r.db.session.add(row)
        r.db.session.commit()

    # --- Communication page & APIs -------------------------------------------------

    @flask_app.route("/admin/communication")
    @login_required
    def admin_communication():
        require_admin()
        grades: list[str] = []
        try:
            rows = r.mdb_conn.execute_query(
                "SELECT DISTINCT CSTR(Grade) AS G FROM Learner_Info WHERE Grade IS NOT NULL ORDER BY G ASC", ()
            ) or []
            for x in rows:
                v = str(x.get("G") or x.get("g") or "").strip()
                if v:
                    grades.append(v)
        except Exception:
            pass
        return render_template(
            "admin/communication.html",
            initial_grades=grades,
            current_year=datetime.utcnow().year,
            sms_max_chars=int(os.environ.get("ADMIN_SMS_MAX_CHARS", "640")),
        )

    @flask_app.route("/admin/communication/grades")
    @login_required
    def admin_communication_grades():
        require_admin()
        grades: list[str] = []
        try:
            rows = r.mdb_conn.execute_query(
                "SELECT DISTINCT CSTR(Grade) AS G FROM Learner_Info WHERE Grade IS NOT NULL ORDER BY G ASC", ()
            ) or []
            for x in rows:
                v = str(x.get("G") or x.get("g") or "").strip()
                if v:
                    grades.append(v)
        except Exception:
            pass
        return jsonify({"grades": grades})

    @flask_app.route("/admin/communication/learners")
    @login_required
    def admin_communication_learners():
        require_admin()
        grade = str(request.args.get("grade", "")).strip()
        surname = str(request.args.get("surname", "")).strip()
        learner_id = str(request.args.get("learner_id", "")).strip()
        clauses, params = ["Status = 'C'"], []
        if learner_id:
            clauses.append("(CSTR(ID) = ? OR CSTR(LearnerID) = ? OR CSTR(AccessionNo) = ?)")
            params.extend([learner_id, learner_id, learner_id])
        elif grade:
            clauses.append("CSTR(Grade) = ?")
            params.append(grade)
        elif surname:
            clauses.append("SName LIKE ?")
            params.append(f"%{surname}%")
        else:
            return jsonify({"learners": []})
        sql = f"SELECT ID, FName, SName, Grade, LearnerID FROM Learner_Info WHERE {' AND '.join(clauses)} ORDER BY SName, FName"
        try:
            rows = r.mdb_conn.execute_query(sql, tuple(params)) or []
        except Exception:
            rows = []
        out = []
        for row in rows:
            lid = str(row.get("ID") or "").strip()
            if not lid:
                continue
            out.append(
                {
                    "id": lid,
                    "name": str(row.get("FName") or ""),
                    "surname": str(row.get("SName") or ""),
                    "grade": str(row.get("Grade") or ""),
                }
            )
        return jsonify({"learners": out})

    @flask_app.route("/admin/communication/parents")
    @login_required
    def admin_communication_parents():
        require_admin()
        raw = str(request.args.get("learner_ids", "")).strip()
        ids = [x.strip() for x in raw.split(",") if x.strip()]
        parents = []
        seen_ph = set()
        for lid in ids:
            for phone, pname in r._get_parent_phones_from_mdb([lid]):
                if phone in seen_ph:
                    continue
                seen_ph.add(phone)
                parents.append({"phone": phone, "name": pname, "learner_id": lid})
        return jsonify({"parents": parents})

    @flask_app.route("/admin/communication/send", methods=["POST"])
    @login_required
    def admin_communication_send():
        require_admin()
        body = request.get_json(force=True, silent=True) or {}
        channels = [str(c).lower() for c in (body.get("channels") or [])]
        message = str(body.get("message") or "").strip()
        phones = [str(p).strip() for p in (body.get("phone_numbers") or []) if str(p).strip()]
        if not phones or not message:
            return jsonify({"ok": False, "error": "Missing phones or message."}), 400
        batch_id = _comm_batch_id()
        sent = 0
        failed = []
        for ph in phones:
            norm = r.normalize_phone(ph)
            if not r.is_valid_phone(norm):
                failed.append({"phone": ph, "error": "invalid"})
                continue
            for ch in channels:
                try:
                    if ch == "sms":
                        r.send_sms_message(norm, message)
                        _log_delivery(
                            batch_id=batch_id,
                            category="custom",
                            channel="sms",
                            phone=norm,
                            message=message,
                            status="sent",
                        )
                        sent += 1
                    elif ch == "whatsapp":
                        ok = r.send_whatsapp_message(norm, message)
                        if ok:
                            _log_delivery(
                                batch_id=batch_id,
                                category="custom",
                                channel="whatsapp",
                                phone=norm,
                                message=message,
                                status="sent",
                            )
                            sent += 1
                        else:
                            failed.append({"phone": norm, "channel": "whatsapp"})
                            _log_delivery(
                                batch_id=batch_id,
                                category="custom",
                                channel="whatsapp",
                                phone=norm,
                                message=message,
                                status="failed",
                                err="whatsapp_failed",
                            )
                except Exception as exc:
                    failed.append({"phone": norm, "channel": ch, "error": str(exc)})
                    _log_delivery(
                        batch_id=batch_id,
                        category="custom",
                        channel=ch,
                        phone=norm,
                        message=message,
                        status="failed",
                        err=str(exc),
                    )
        return jsonify({"ok": True, "sent": sent, "failed": failed, "batch_id": batch_id})

    @flask_app.route("/admin/communication/discipline/incidents")
    @login_required
    def admin_communication_discipline_incidents():
        require_admin()
        year = str(request.args.get("year", "")).strip()
        start_date = str(request.args.get("start_date", "")).strip()
        end_date = str(request.args.get("end_date", "")).strip()
        learner_id = str(request.args.get("learner_id", "")).strip()
        grade = str(request.args.get("grade", "")).strip()
        surname = str(request.args.get("surname", "")).strip()
        misconduct = str(request.args.get("misconduct", "")).strip()
        if not start_date and not end_date:
            return jsonify({"incidents": [], "error": "Select dates."})
        params: list = []
        wh: list[str] = []
        if year:
            wh.append("CSTR(dr.Datayear) = ?")
            params.append(year)
        if learner_id:
            wh.append("CSTR(dr.Learnerid) = ?")
            params.append(learner_id)
        if misconduct:
            wh.append("dr.MisconductDescription LIKE ?")
            params.append(f"%{misconduct}%")
        if start_date:
            wh.append("dr.Date >= ?")
            params.append(start_date)
        if end_date:
            wh.append("dr.Date <= ?")
            params.append(end_date + " 23:59:59")
        where_sql = " AND ".join(wh) if wh else "1=1"
        sql = f"SELECT dr.* FROM DisciplinaryRecords dr WHERE {where_sql} ORDER BY dr.Date DESC"
        try:
            rows = r.mdb_conn.execute_query(sql, tuple(params)) or []
        except Exception:
            rows = []
        learner_rows = r.mdb_conn.execute_query(
            "SELECT ID, LearnerID, FName, SName, Grade FROM Learner_Info", ()
        ) or []
        norm = []
        for row in learner_rows:
            d = dict(row)
            if d.get("IDText") and not d.get("ID"):
                d["ID"] = d.get("IDText")
            if d.get("LearnerIDText") and not d.get("LearnerID"):
                d["LearnerID"] = d.get("LearnerIDText")
            norm.append(d)
        lu = r.build_learner_lookup_by_any_id(norm)
        incidents = []
        for row in rows:
            lk = str(
                row.get("Learnerid") or row.get("LearnerId") or row.get("LearnerID") or row.get("learnerid") or ""
            ).strip()
            info = lu.get(lk) or {}
            fn = str(info.get("name") or "")
            sn = str(info.get("surname") or "")
            if grade and str(info.get("grade") or "").strip() != grade:
                continue
            if surname and surname.lower() not in str(info.get("surname") or "").lower():
                continue
            md = ""
            for k in row:
                if str(k).lower() == "misconductdescription":
                    md = str(row.get(k) or "")
                    break
            dt = row.get("Date") or row.get("date")
            ds = ""
            try:
                if dt:
                    ds = str(dt)[:10]
            except Exception:
                ds = str(dt or "")[:10]
            learner_name = (fn + " " + sn).strip() or lk
            incidents.append(
                {
                    "incident_id": str(row.get("ID") or row.get("id") or ""),
                    "learner_id": lk,
                    "learner_name": learner_name,
                    "incident_date": ds,
                    "misconduct": md,
                    "preview_message": f"{learner_name}: {md}".strip(),
                    "raw": row,
                }
            )
        return jsonify({"incidents": incidents})

    @flask_app.route("/admin/communication/discipline/send", methods=["POST"])
    @login_required
    def admin_communication_discipline_send():
        require_admin()
        body = request.get_json(force=True, silent=True) or {}
        channels = [str(c).lower() for c in (body.get("channels") or [])]
        incidents = body.get("incidents") or []
        if not incidents:
            return jsonify({"ok": False, "error": "No incidents."}), 400
        batch_id = _comm_batch_id()
        sent = 0
        failed: list[dict] = []
        for inc in incidents:
            lid = str(inc.get("learner_id") or "").strip()
            preview = str(inc.get("preview_message") or "").strip() or str(inc.get("misconduct") or "")
            ds = str(inc.get("incident_date") or "").strip()
            md = str(inc.get("misconduct") or "").strip()
            ln = str(inc.get("learner_name") or "").strip()
            if ds and md and ln:
                message = f"{ln} ({ds}): {md}"
            else:
                message = preview
            ref = str(inc.get("incident_id") or "")
            for ph, pname in r._get_parent_phones_from_mdb([lid]):
                for ch in channels:
                    try:
                        if ch == "sms":
                            r.send_sms_message(ph, message)
                            _log_delivery(
                                batch_id=batch_id,
                                category="discipline",
                                channel="sms",
                                phone=ph,
                                message=message,
                                status="sent",
                                recipient_name=pname,
                                reference_type="incident",
                                reference_id=ref,
                            )
                            sent += 1
                        elif ch == "whatsapp":
                            if r.send_whatsapp_message(ph, message):
                                _log_delivery(
                                    batch_id=batch_id,
                                    category="discipline",
                                    channel="whatsapp",
                                    phone=ph,
                                    message=message,
                                    status="sent",
                                    recipient_name=pname,
                                    reference_type="incident",
                                    reference_id=ref,
                                )
                                sent += 1
                            else:
                                failed.append({"phone": ph})
                    except Exception as exc:
                        failed.append({"phone": ph, "error": str(exc)})
        return jsonify({"ok": True, "sent": sent, "failed": failed, "batch_id": batch_id})

    @flask_app.route("/admin/communication/finance/outstanding")
    @login_required
    def admin_communication_finance_outstanding():
        require_admin()
        year_s = str(request.args.get("year", "") or datetime.utcnow().year).strip()
        grade = str(request.args.get("grade", "")).strip()
        surname = str(request.args.get("surname", "")).strip()
        limit = min(int(request.args.get("limit", "500")), 2000)
        try:
            y_int = int(year_s)
        except ValueError:
            y_int = datetime.utcnow().year
        q = ["Status = 'C'"]
        params: list = []
        if grade:
            q.append("CSTR(Grade) = ?")
            params.append(grade)
        if surname:
            q.append("SName LIKE ?")
            params.append(f"%{surname}%")
        sql = f"SELECT TOP {limit} ID, FName, SName, Grade, LearnerID FROM Learner_Info WHERE {' AND '.join(q)} ORDER BY SName"
        try:
            rows = r.mdb_conn.execute_query(sql, tuple(params)) or []
        except Exception:
            rows = r.mdb_conn.execute_query(
                "SELECT ID, FName, SName, Grade, LearnerID FROM Learner_Info WHERE " + " AND ".join(q) + " ORDER BY SName",
                tuple(params),
            ) or []
            rows = rows[:limit]
        out = []
        for row in rows:
            lid = str(row.get("ID") or "").strip()
            fin = r._finance_payload_for_learner(learner_id=lid, target_year=y_int)
            if not fin or float(fin.get("outstanding") or 0) <= 0:
                continue
            nm = (str(row.get("SName") or "").strip() + ", " + str(row.get("FName") or "").strip()).strip(", ")
            out.append(
                {
                    "id": lid,
                    "learner_name": nm,
                    "learner_id": lid,
                    "grade": str(row.get("Grade") or ""),
                    "year": y_int,
                    "outstanding": float(fin.get("outstanding") or 0),
                    "preview_message": f"{nm} (Gr {row.get('Grade')}) balance {fin.get('outstanding')}",
                }
            )
        return jsonify({"learners": out})

    @flask_app.route("/admin/communication/finance/send", methods=["POST"])
    @login_required
    def admin_communication_finance_send():
        require_admin()
        body = request.get_json(force=True, silent=True) or {}
        channels = [str(c).lower() for c in (body.get("channels") or [])]
        learners = body.get("learners") or []
        tpl = str(body.get("finance_template") or "").strip()
        school = (os.environ.get("SCHOOL_DISPLAY_NAME") or "School").strip()
        batch_id = _comm_batch_id()
        sent = 0
        failed: list[dict] = []
        for L in learners:
            lid = str(L.get("learner_id") or L.get("id") or "").strip()
            yr = int(L.get("year") or datetime.utcnow().year)
            claimed = L.get("outstanding")
            fin = r._finance_payload_for_learner(learner_id=lid, target_year=yr)
            if not fin:
                failed.append({"learner_id": lid, "error": "no_finance"})
                continue
            actual = float(fin.get("outstanding") or 0)
            try:
                cl = float(claimed)
            except (TypeError, ValueError):
                cl = -1
            if actual <= 0:
                failed.append({"learner_id": lid, "error": "not_outstanding"})
                continue
            if cl >= 0 and abs(actual - cl) > 0.05:
                failed.append({"learner_id": lid, "error": "amount_mismatch"})
                continue
            nm = str(L.get("learner_name") or "")
            msg = (
                tpl.replace("{parent_name}", "Parent/Guardian")
                .replace("{learner_name}", nm)
                .replace("{grade}", str(L.get("grade") or fin.get("grade") or ""))
                .replace("{year}", str(yr))
                .replace("{outstanding_amount}", str(actual))
                .replace("{school_name}", school)
            )
            seen_phones: set[str] = set()
            for ph, pname in r._get_parent_phones_from_mdb([lid]):
                ph_key = str(ph or "").strip()
                if not ph_key or ph_key in seen_phones:
                    continue
                seen_phones.add(ph_key)
                msg_f = msg.replace("{parent_name}", pname or "Parent/Guardian")
                for ch in channels:
                    try:
                        if ch == "sms":
                            r.send_sms_message(ph, msg_f)
                            _log_delivery(
                                batch_id=batch_id,
                                category="finance",
                                channel="sms",
                                phone=ph,
                                message=msg_f,
                                status="sent",
                                recipient_name=pname,
                                reference_type="learner",
                                reference_id=lid,
                            )
                            sent += 1
                        elif ch == "whatsapp":
                            if r.send_whatsapp_message(ph, msg_f):
                                _log_delivery(
                                    batch_id=batch_id,
                                    category="finance",
                                    channel="whatsapp",
                                    phone=ph,
                                    message=msg_f,
                                    status="sent",
                                    recipient_name=pname,
                                    reference_type="learner",
                                    reference_id=lid,
                                )
                                sent += 1
                    except Exception as exc:
                        failed.append({"learner_id": lid, "error": str(exc)})
        return jsonify({"ok": True, "sent": sent, "failed": failed, "batch_id": batch_id})

    @flask_app.route("/admin/communication/delivery-report/<batch_id>")
    @login_required
    def admin_communication_delivery_report(batch_id: str):
        require_admin()
        q = r.CommunicationDeliveryLog.query.filter_by(batch_id=str(batch_id))
        total = q.count()
        ok = q.filter_by(status="sent").count()
        bad = total - ok
        return jsonify({"report": {"total": total, "sent": ok, "failed": bad}})

    # --- Detention notices ---------------------------------------------------------

    def _detention_meta(batch) -> dict:
        try:
            d = json.loads(batch.learner_ids_json or "{}")
        except Exception:
            d = {}
        if not isinstance(d, dict):
            d = {}
        ids = d.get("learner_ids") or []
        merit = d.get("merit_applied") or []
        if isinstance(ids, str):
            ids = [ids]
        if not ids and batch.learner_ids_json:
            try:
                ids = json.loads(batch.learner_ids_json)
            except Exception:
                ids = []
        if not isinstance(ids, list):
            ids = []
        if not isinstance(merit, list):
            merit = []
        return {"learner_ids": [str(x) for x in ids], "merit_applied": [str(x) for x in merit]}

    @flask_app.route("/admin/detention-notices")
    @login_required
    def admin_detention_notices():
        require_admin()
        schedule_defaults = {
            p: {
                "start": _load_detention_schedule_times(r.mdb_conn, p)[0],
                "end": _load_detention_schedule_times(r.mdb_conn, p)[1],
            }
            for p in ("foundation", "primary", "highschool")
        }
        return render_template(
            "admin/detention_notices.html",
            current_year=datetime.utcnow().year,
            schedule_defaults=schedule_defaults,
        )

    @flask_app.route("/admin/detention-notices/history")
    @login_required
    def admin_detention_notice_history():
        require_admin()
        rows = (
            r.DetentionNoticeBatch.query.order_by(r.DetentionNoticeBatch.created_at.desc()).limit(80).all()
        )
        hist = []
        for b in rows:
            meta = _detention_meta(b)
            ids = meta["learner_ids"]
            applied = meta["merit_applied"]
            hist.append(
                {
                    "id": b.id,
                    "phaseName": b.phase_name,
                    "year": b.data_year,
                    "learnerCount": b.learner_count,
                    "detentionDate": b.detention_date.isoformat() if b.detention_date else "",
                    "educatorName": b.educator_name,
                    "createdBy": b.created_by_name or "",
                    "createdAt": b.created_at.isoformat() if b.created_at else "",
                    "meritAppliedCount": len(applied),
                    "meritTotalCount": len(ids),
                    "notificationsUrl": url_for("admin_detention_download", batch_id=b.id, kind="notifications"),
                    "attendanceUrl": url_for("admin_detention_download", batch_id=b.id, kind="attendance"),
                }
            )
        return jsonify({"history": hist})

    @flask_app.route("/admin/detention-notices/learners")
    @login_required
    def admin_detention_learners():
        require_admin()
        phase = str(request.args.get("phase", "")).strip()
        year = str(request.args.get("year", "")).strip()
        if not year:
            year = str(datetime.utcnow().year)
        grade_filter = _detention_grades_from_request_args(phase)
        learners = r._fetch_detention_candidates(
            phase, year, 12, grades=grade_filter or None
        )
        return jsonify({"learners": learners})

    @flask_app.route("/admin/detention-notices/generate", methods=["POST"])
    @login_required
    def admin_detention_generate():
        require_admin()
        body = request.get_json(force=True, silent=True) or {}
        phase = str(body.get("phase", "")).strip()
        year = str(body.get("year", "")).strip()
        if not year:
            year = str(datetime.utcnow().year)
        educator = str(body.get("educator_name", "")).strip()
        gen_all = bool(body.get("generate_all"))
        ids_req = [str(x).strip() for x in (body.get("learner_ids") or []) if str(x).strip()]
        ddate = str(body.get("detention_date", "")).strip()
        if not ddate or not educator:
            return jsonify({"ok": False, "error": "Missing date or educator."})
        try:
            det_dt = datetime.fromisoformat(ddate[:10])
        except ValueError:
            return jsonify({"ok": False, "error": "Invalid date."})
        grade_filter = _parse_detention_grades_filter(phase, body.get("grades"))
        start_raw = str(body.get("start_time", "") or "").strip()
        end_raw = str(body.get("end_time", "") or "").strip()
        start_ov: str | None = None
        end_ov: str | None = None
        if start_raw or end_raw:
            if not start_raw or not end_raw:
                return jsonify(
                    {"ok": False, "error": "Provide both start_time and end_time, or neither."}
                ), 400
            start_ov = _validate_detention_hhmm(start_raw)
            end_ov = _validate_detention_hhmm(end_raw)
            if not start_ov or not end_ov:
                return jsonify({"ok": False, "error": "Invalid time format (use HH:MM)."}), 400
        all_learners = r._fetch_detention_candidates(
            phase, year, 12, grades=grade_filter or None
        )
        id_set = {x["id"] for x in all_learners}
        if gen_all:
            sel = [x["id"] for x in all_learners]
        else:
            sel = [x for x in ids_req if x in id_set]
        if not sel:
            return jsonify({"ok": False, "error": "No learners selected."})
        phase_names = {
            "foundation": "Foundation (Grade 3)",
            "primary": "Primary (Grades 4-7)",
            "highschool": "High School (Grades 8-12)",
        }
        phase_register_label = {
            "foundation": "Foundation Phase",
            "primary": "Primary Phase",
            "highschool": "High School Phase",
        }.get(phase, phase_names.get(phase, phase))
        phase_file_prefix = {
            "foundation": "Foundation",
            "primary": "Primary",
            "highschool": "High_School",
        }.get(phase, "Detention")
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        date_slug = det_dt.strftime("%Y-%m-%d")
        base = Path(r.app.config["DETENTION_PDF_UPLOAD_FOLDER"])
        not_name = f"{phase_file_prefix}_Detention_Notifications_{date_slug}_{stamp}.pdf"
        att_name = f"{phase_file_prefix}_Attendance_Register_{date_slug}_{stamp}.pdf"
        not_path = base / not_name
        att_path = base / att_name
        school_title = (os.environ.get("SCHOOL_DISPLAY_NAME") or "").strip() or "School"
        start_t, end_t = _load_detention_schedule_times(
            r.mdb_conn, phase, start_override=start_ov, end_override=end_ov
        )
        letterhead_path = _resolve_letterhead_path(getattr(r.app, "root_path", None), phase)
        by_id = {str(x["id"]): x for x in all_learners}
        learner_rows_full: list[dict] = []
        for lid in sel:
            row = by_id.get(str(lid))
            if row:
                learner_rows_full.append(row)
            else:
                learner_rows_full.append({"id": str(lid), "fname": "", "sname": "", "grade": "", "balance": 0})
        dem_map = _fetch_disciplinary_rows_for_notice(r.mdb_conn, sel, year)
        try:
            _write_detention_notifications_pdf(
                not_path,
                school_title=school_title,
                detention_dt=det_dt,
                start_time=start_t,
                end_time=end_t,
                learner_order=[str(x) for x in sel],
                learner_rows=learner_rows_full,
                demerits_by_learner=dem_map,
                letterhead_path=letterhead_path,
            )
            _write_detention_attendance_pdf(
                att_path,
                school_title=school_title,
                phase_register_label=phase_register_label,
                nice_date=det_dt.strftime("%d %B %Y"),
                educator=educator,
                start_time=start_t,
                learner_order=[str(x) for x in sel],
                learner_rows=learner_rows_full,
                letterhead_path=letterhead_path,
            )
        except ImportError:
            base.mkdir(parents=True, exist_ok=True)
            lines = [
                f"Phase: {phase_names.get(phase, phase)}",
                f"Year: {year}",
                f"Educator: {educator}",
                f"Date: {ddate}",
                "Learners:",
            ] + [f" - {lid}" for lid in sel]
            fallback = "Detention notifications\n\n" + "\n".join(lines)
            not_path.write_text(fallback, encoding="utf-8")
            att_path.write_text("Detention attendance register\n\n" + "\n".join(lines), encoding="utf-8")
        except Exception as exc:
            flask_app.logger.exception("detention pdf generation failed")
            return jsonify({"ok": False, "error": "Could not build detention PDFs. Ensure reportlab is installed."}), 500
        rel_n = os.path.relpath(str(not_path), start=os.path.dirname(r.app.instance_path) if r.app.instance_path else ".")
        rel_a = os.path.relpath(str(att_path), start=os.path.dirname(r.app.instance_path) if r.app.instance_path else ".")
        meta = json.dumps({"learner_ids": sel, "merit_applied": []})
        batch = r.DetentionNoticeBatch(
            phase=phase,
            phase_name=phase_names.get(phase, phase),
            data_year=year,
            detention_date=det_dt,
            educator_name=educator,
            learner_count=len(sel),
            learner_ids_json=meta,
            notifications_filename=not_name,
            notifications_relpath=str(not_path),
            attendance_filename=att_name,
            attendance_relpath=str(att_path),
            created_by_user_id=getattr(current_user, "id", None),
            created_by_name=getattr(current_user, "username", None),
        )
        r.db.session.add(batch)
        r.db.session.commit()
        return jsonify(
            {
                "ok": True,
                "selectedCount": len(sel),
                "notificationsUrl": url_for("admin_detention_download", batch_id=batch.id, kind="notifications"),
                "attendanceUrl": url_for("admin_detention_download", batch_id=batch.id, kind="attendance"),
            }
        )

    @flask_app.route("/admin/detention-notices/<int:batch_id>/file/<kind>")
    @login_required
    def admin_detention_download(batch_id: int, kind: str):
        require_admin()
        b = r.DetentionNoticeBatch.query.get_or_404(batch_id)
        if kind == "notifications":
            path = Path(b.notifications_relpath)
        elif kind == "attendance":
            path = Path(b.attendance_relpath)
        else:
            abort(404)
        if not path.is_file():
            flash("File missing on server.", "error")
            return redirect(url_for("admin_detention_notices"))
        return send_file(path, as_attachment=True, download_name=path.name)

    @flask_app.route("/admin/detention-notices/<int:batch_id>/learners", methods=["GET"])
    @login_required
    def admin_detention_batch_learners(batch_id: int):
        require_admin()
        b = r.DetentionNoticeBatch.query.get_or_404(batch_id)
        meta = _detention_meta(b)
        applied = set(meta.get("merit_applied") or [])
        learners = []
        for lid in meta.get("learner_ids") or []:
            info = r.fetch_learner_info_by_id(str(lid)) or {}
            learners.append(
                {
                    "id": str(lid),
                    "name": str(info.get("name") or ""),
                    "surname": str(info.get("surname") or ""),
                    "grade": str(info.get("grade") or ""),
                    "learnerId": str(info.get("learner_id") or ""),
                    "applied": str(lid) in applied,
                }
            )
        return jsonify(
            {
                "learners": learners,
                "phaseName": b.phase_name,
                "detentionDate": b.detention_date.isoformat() if b.detention_date else "",
            }
        )

    @flask_app.route("/admin/detention-notices/<int:batch_id>/apply-sit-detention-merit", methods=["POST"])
    @login_required
    def admin_detention_apply_merit(batch_id: int):
        require_admin()
        b = r.DetentionNoticeBatch.query.get_or_404(batch_id)
        body = request.get_json(force=True, silent=True) or {}
        chosen = [str(x).strip() for x in (body.get("learner_ids") or []) if str(x).strip()]
        meta = _detention_meta(b)
        ids = set(meta.get("learner_ids") or [])
        applied = list(meta.get("merit_applied") or [])
        y = str(b.data_year)
        for lid in chosen:
            if lid not in ids:
                continue
            if lid in applied:
                continue
            try:
                r.mdb_conn.execute_non_query(
                    """
                    INSERT INTO DisciplinaryRecords (Learnerid, Datayear, Merit, Demerit, MisconductDescription, IncidentDate)
                    VALUES (?, ?, 12, 0, ?, ?)
                    """,
                    (lid, y, "SIT DETENTION (merit)", b.detention_date),
                )
            except Exception:
                try:
                    r.mdb_conn.execute_non_query(
                        """
                        INSERT INTO DisciplinaryRecords (LearnerId, DataYear, Merit, Demerit, MisconductDescription, IncidentDate)
                        VALUES (?, ?, 12, 0, ?, ?)
                        """,
                        (lid, y, "SIT DETENTION (merit)", b.detention_date),
                    )
                except Exception as exc:
                    return jsonify({"ok": False, "error": str(exc)})
            applied.append(lid)
        meta["merit_applied"] = applied
        b.learner_ids_json = json.dumps(meta)
        r.db.session.commit()
        return jsonify({"ok": True, "message": f"Applied merit for {len(chosen)} learner(s)."})

    # --- Sync accounts -------------------------------------------------------------

    @flask_app.route("/admin/sync-accounts", methods=["GET", "POST"], endpoint="sync_accounts")
    @login_required
    def sync_accounts():
        require_admin()
        if request.method == "GET":
            return render_template("admin/sync_accounts.html", results=None)
        results = {"total_students": 0, "created": 0, "existing": 0, "errors": 0, "created_accounts": [], "existing_accounts": []}
        try:
            rows = r.mdb_conn.execute_query(
                "SELECT ID, LearnerID, FName, SName, Grade, AccessionNo, Status FROM Learner_Info WHERE Status = 'C'", ()
            ) or []
        except Exception as exc:
            return render_template("admin/sync_accounts.html", results={"error": str(exc)})
        results["total_students"] = len(rows)
        for row in rows:
            lid = str(row.get("ID") or "").strip()
            acc = str(row.get("AccessionNo") or row.get("LearnerID") or lid).strip()
            if not acc:
                results["errors"] += 1
                continue
            existing = r.User.query.filter_by(username=acc).first()
            if existing:
                results["existing"] += 1
                results["existing_accounts"].append(
                    {
                        "accession_no": acc,
                        "name": str(row.get("FName") or ""),
                        "surname": str(row.get("SName") or ""),
                        "grade": str(row.get("Grade") or ""),
                        "learner_id": lid,
                    }
                )
                continue
            pw = secrets.token_urlsafe(12)
            u = r.User(
                username=acc,
                password_hash=generate_password_hash(pw),
                first_login=True,
                is_parent=True,
                learner_id=lid,
            )
            r.db.session.add(u)
            r.db.session.flush()
            r.db.session.add(r.UserLearner(user_id=u.id, learner_id=lid))
            r.db.session.commit()
            results["created"] += 1
            results["created_accounts"].append(
                {
                    "accession_no": acc,
                    "name": str(row.get("FName") or ""),
                    "surname": str(row.get("SName") or ""),
                    "grade": str(row.get("Grade") or ""),
                    "learner_id": lid,
                    "password": pw,
                    "status": "created",
                }
            )
        return render_template("admin/sync_accounts.html", results=results)

    # --- Slideshow -----------------------------------------------------------------

    @flask_app.route("/admin/slideshow")
    @login_required
    def admin_slideshow():
        require_admin()
        images = r.SlideshowImage.query.order_by(r.SlideshowImage.display_order, r.SlideshowImage.id).all()
        return render_template("admin/slideshow.html", images=images)

    @flask_app.route("/admin/slideshow/upload", methods=["POST"], endpoint="upload_slideshow_image")
    @login_required
    def upload_slideshow_image():
        require_admin()
        f = request.files.get("image")
        if not f or not f.filename:
            flash("No file.", "error")
            return redirect(url_for("admin_slideshow"))
        fn = secure_filename(f.filename)
        folder = r.app.config["UPLOAD_FOLDER"]
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, fn)
        f.save(dest)
        img = r.SlideshowImage(filename=fn, display_order=0, is_active=True)
        r.db.session.add(img)
        r.db.session.commit()
        flash("Uploaded.", "success")
        return redirect(url_for("admin_slideshow"))

    @flask_app.route("/admin/slideshow/<int:image_id>/toggle", methods=["POST"], endpoint="toggle_slideshow_image")
    @login_required
    def toggle_slideshow_image(image_id: int):
        require_admin()
        img = r.SlideshowImage.query.get_or_404(image_id)
        img.is_active = not bool(img.is_active)
        r.db.session.commit()
        return redirect(url_for("admin_slideshow"))

    @flask_app.route("/admin/slideshow/<int:image_id>/delete", methods=["POST"], endpoint="delete_slideshow_image")
    @login_required
    def delete_slideshow_image(image_id: int):
        require_admin()
        img = r.SlideshowImage.query.get_or_404(image_id)
        try:
            path = os.path.join(r.app.config["UPLOAD_FOLDER"], img.filename)
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass
        r.db.session.delete(img)
        r.db.session.commit()
        return redirect(url_for("admin_slideshow"))

    # --- WhatsApp admin page -------------------------------------------------------

    @flask_app.route("/admin/whatsapp")
    @login_required
    def admin_whatsapp():
        require_admin()
        return render_template("admin/whatsapp.html")

    @flask_app.route("/admin/whatsapp/status")
    @login_required
    def admin_whatsapp_status():
        require_admin()
        base = str(r.app.config.get("WHATSAPP_SERVICE_URL") or "").strip()
        if not base:
            return jsonify({"ok": False, "ready": False, "error": "Service URL not configured"})
        try:
            import requests

            resp = requests.get(f"{base.rstrip('/')}/status", timeout=5)
            return jsonify(resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text})
        except Exception as exc:
            return jsonify({"ok": False, "ready": False, "error": str(exc)})

    # --- Sick notes ----------------------------------------------------------------

    @flask_app.route("/admin/sick-notes")
    @login_required
    def admin_sick_notes():
        require_admin()
        rows = r.SickNoteSubmission.query.order_by(r.SickNoteSubmission.submitted_at.desc()).limit(500).all()
        uids = {x.submitted_by_user_id for x in rows}
        users_map = {u.id: u for u in r.User.query.filter(r.User.id.in_(uids)).all()} if uids else {}
        return render_template("admin/sick_notes.html", rows=rows, users_map=users_map)

    @flask_app.route("/admin/sick-notes/<int:submission_id>/file")
    @login_required
    def admin_sick_note_file(submission_id: int):
        require_admin()
        sub = r.SickNoteSubmission.query.get_or_404(submission_id)
        base = Path(r.app.root_path)
        path = base / sub.storage_relpath
        if not path.is_file():
            abort(404)
        return send_file(path, as_attachment=False, download_name=sub.original_filename)

    # --- User management -----------------------------------------------------------

    @flask_app.route("/admin/users")
    @login_required
    def admin_users():
        require_admin()
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 30)), 5), 100)
        q = str(request.args.get("q", "")).strip()
        query = r.User.query
        if q:
            like = f"%{q}%"
            query = query.filter((r.User.username.ilike(like)) | (r.User.phone.ilike(like)))
        total = query.count()
        users_rows = query.order_by(r.User.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        view_users = []
        for u in users_rows:
            display = u.username or u.phone or f"#{u.id}"
            if u.is_parent:
                learner_ids = r.get_linked_learner_ids_for_user(u)
                for lid in learner_ids:
                    parent_row = r._mdb_get_parent_profile_row(lid)
                    if parent_row:
                        fname = str(parent_row.get("FName") or "").strip()
                        sname = str(parent_row.get("SName") or "").strip()
                        if fname or sname:
                            display = f"{fname} {sname}".strip()
                            break
            elif u.educator_id:
                edid = str(u.educator_id).strip()
                if edid.startswith("S-"):
                    identity = r.get_staff_identity_by_staffid(edid[2:])
                else:
                    identity = r.get_educator_identity_by_edid(edid)
                if identity and identity.get("display_name"):
                    display = identity["display_name"]
            view_users.append(
                type(
                    "VU",
                    (),
                    {
                        "id": u.id,
                        "display_name": display,
                        "phone": u.phone,
                        "is_parent": u.is_parent,
                        "is_manager": u.is_manager,
                        "is_teacher": u.is_teacher,
                        "is_admin": u.username == r.ADMIN_USERNAME,
                        "last_accessed": None,
                        "mgmt_can_view_academics": u.mgmt_can_view_academics,
                        "mgmt_can_view_disciplinary": u.mgmt_can_view_disciplinary,
                        "mgmt_can_view_attendance": u.mgmt_can_view_attendance,
                        "mgmt_can_view_finance": u.mgmt_can_view_finance,
                        "teacher_role": u.teacher_role,
                        "can_teacher_attendance": u.can_teacher_attendance,
                        "can_teacher_discipline": u.can_teacher_discipline,
                        "can_teacher_assessments": u.can_teacher_assessments,
                        "can_teacher_reports": u.can_teacher_reports,
                        "can_teacher_message_parents": u.can_teacher_message_parents,
                        "can_teacher_announcements": u.can_teacher_announcements,
                    },
                )()
            )
        total_pages = (total + per_page - 1) // per_page if total else 1
        return render_template(
            "admin/users.html",
            users=view_users,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            q=q,
        )

    @flask_app.route("/admin/users/set-manager", methods=["POST"])
    @login_required
    def admin_users_set_manager():
        require_admin()
        is_mgr = str(request.form.get("is_manager", "1")) == "1"
        uid = request.form.get("user_id")
        phone = str(request.form.get("phone", "")).strip()
        if uid:
            u = r.User.query.get(int(uid))
        elif phone:
            p = r.normalize_phone(phone)
            u = r.User.query.filter_by(phone=p).first()
        else:
            flash("Missing user.", "error")
            return redirect(url_for("admin_users"))
        if not u:
            flash("User not found.", "error")
            return redirect(url_for("admin_users"))
        if u.username == r.ADMIN_USERNAME:
            flash("Cannot change admin user.", "error")
            return redirect(url_for("admin_users"))
        u.is_manager = is_mgr
        r.db.session.commit()
        flash("Updated manager flag.", "success")
        return redirect(url_for("admin_users"))

    @flask_app.route("/admin/users/set-mgmt-permissions", methods=["POST"])
    @login_required
    def admin_users_set_mgmt_permissions():
        require_admin()
        u = r.User.query.get_or_404(int(request.form.get("user_id", 0)))
        u.mgmt_can_view_academics = bool(request.form.get("can_academics"))
        u.mgmt_can_view_disciplinary = bool(request.form.get("can_disciplinary"))
        u.mgmt_can_view_attendance = bool(request.form.get("can_attendance"))
        u.mgmt_can_view_finance = bool(request.form.get("can_finance"))
        r.db.session.commit()
        flash("Management permissions saved.", "success")
        return redirect(url_for("admin_users"))

    @flask_app.route("/admin/users/set-teacher", methods=["POST"])
    @login_required
    def admin_users_set_teacher():
        require_admin()
        u = r.User.query.get_or_404(int(request.form.get("user_id", 0)))
        if u.username == r.ADMIN_USERNAME:
            flash("Cannot change admin.", "error")
            return redirect(url_for("admin_users"))
        grant = str(request.form.get("is_teacher", "1")) == "1"
        u.is_teacher = grant
        u.teacher_role = str(request.form.get("teacher_role") or "Teacher")
        r.db.session.commit()
        flash("Teacher role updated.", "success")
        return redirect(url_for("admin_users"))

    @flask_app.route("/admin/users/set-teacher-permissions", methods=["POST"])
    @login_required
    def admin_users_set_teacher_permissions():
        require_admin()
        u = r.User.query.get_or_404(int(request.form.get("user_id", 0)))
        u.can_teacher_attendance = bool(request.form.get("can_teacher_attendance"))
        u.can_teacher_discipline = bool(request.form.get("can_teacher_discipline"))
        u.can_teacher_assessments = bool(request.form.get("can_teacher_assessments"))
        u.can_teacher_reports = bool(request.form.get("can_teacher_reports"))
        u.can_teacher_message_parents = bool(request.form.get("can_teacher_message_parents"))
        u.can_teacher_announcements = bool(request.form.get("can_teacher_announcements"))
        r.db.session.commit()
        flash("Teacher permissions saved.", "success")
        return redirect(url_for("admin_users"))

    @flask_app.route("/admin/users/teacher-assignment", methods=["POST"])
    @login_required
    def admin_teacher_assignment_add():
        require_admin()
        u = r.User.query.get_or_404(int(request.form.get("user_id", 0)))
        a = r.UserTeacherAssignment(
            user_id=u.id,
            class_id=str(request.form.get("class_id", "")).strip(),
            grade=str(request.form.get("grade", "")).strip() or None,
            subject=str(request.form.get("subject", "")).strip() or None,
            academic_year=str(request.form.get("academic_year", "")).strip() or None,
        )
        r.db.session.add(a)
        r.db.session.commit()
        flash("Assignment added.", "success")
        return redirect(url_for("admin_users"))

    # --- Profile change requests ---------------------------------------------------

    @flask_app.route("/admin/profile-change-requests")
    @login_required
    def admin_profile_change_requests():
        require_admin()
        status_filter = str(request.args.get("status", "pending")).strip().lower()
        req_id = request.args.get("request_id")
        q = r.ProfileChangeRequest.query
        if status_filter != "all":
            q = q.filter_by(status=status_filter)
        requests_rows = q.order_by(r.ProfileChangeRequest.submitted_at.desc()).limit(200).all()
        selected = None
        items = []
        if req_id:
            selected = r.ProfileChangeRequest.query.get(int(req_id))
            if selected:
                items = r._profile_change_items_for_request(selected.id)
        uids = {x.submitted_by_user_id for x in requests_rows}
        if selected:
            if selected.reviewed_by_user_id:
                uids.add(selected.reviewed_by_user_id)
            uids.add(selected.submitted_by_user_id)
        id_list = [x for x in uids if x]
        users_map = {u.id: u for u in r.User.query.filter(r.User.id.in_(id_list)).all()} if id_list else {}
        return render_template(
            "admin/profile_change_requests.html",
            requests_rows=requests_rows,
            status_filter=status_filter,
            selected_request=selected,
            selected_items=items,
            users_map=users_map,
        )

    @flask_app.route("/admin/profile-change-requests/<int:request_id>/approve", methods=["POST"])
    @login_required
    def admin_profile_change_request_approve(request_id: int):
        require_admin()
        req = r.ProfileChangeRequest.query.get_or_404(request_id)
        if req.status != "pending":
            flash("Already processed.", "error")
            return redirect(url_for("admin_profile_change_requests", status="all", request_id=request_id))
        items = r._profile_change_items_for_request(req.id)
        for item in items:
            if not r._safe_mdb_field_name(item.field_name):
                continue
            fld = item.field_name
            val = item.new_value or ""
            if item.entity == "learner_info":
                r.mdb_conn.execute_non_query(
                    f"UPDATE Learner_Info SET [{fld}] = ? WHERE CSTR(ID) = ?", (val, str(item.record_key))
                )
            elif item.entity == "parent_info":
                r.mdb_conn.execute_non_query(
                    f"UPDATE Parent_Info SET [{fld}] = ? WHERE CSTR(ParentID) = ?", (val, str(item.record_key))
                )
        req.status = "approved"
        req.reviewed_at = datetime.utcnow()
        req.reviewed_by_user_id = getattr(current_user, "id", None)
        req.admin_comment = str(request.form.get("admin_comment", "") or "").strip() or req.admin_comment
        r.db.session.commit()
        flash("Request approved and applied.", "success")
        return redirect(url_for("admin_profile_change_requests", status="pending"))

    @flask_app.route("/admin/profile-change-requests/<int:request_id>/reject", methods=["POST"])
    @login_required
    def admin_profile_change_request_reject(request_id: int):
        require_admin()
        req = r.ProfileChangeRequest.query.get_or_404(request_id)
        reason = str(request.form.get("admin_comment", "")).strip()
        if not reason:
            flash("Rejection reason required.", "error")
            return redirect(url_for("admin_profile_change_requests", request_id=request_id))
        req.status = "rejected"
        req.reviewed_at = datetime.utcnow()
        req.reviewed_by_user_id = getattr(current_user, "id", None)
        req.admin_comment = reason
        r.db.session.commit()
        flash("Request rejected.", "success")
        return redirect(url_for("admin_profile_change_requests", status="pending"))

    # --- Password reset ------------------------------------------------------------

    @flask_app.route("/admin/users/reset-password", methods=["POST"])
    @login_required
    def admin_reset_user_password():
        require_admin()
        username = str(request.form.get("username", "")).strip()
        pw1 = str(request.form.get("new_password", "")).strip()
        pw2 = str(request.form.get("confirm_password", "")).strip()
        if not username or not pw1 or pw1 != pw2:
            flash("Invalid input.", "error")
            return redirect(url_for("admin_dashboard"))
        ok, errs = r.validate_password_strength(pw1)
        if not ok:
            flash("; ".join(errs), "error")
            return redirect(url_for("admin_dashboard"))
        u = r.User.query.filter_by(username=username).first()
        if not u:
            flash("User not found.", "error")
            return redirect(url_for("admin_dashboard"))
        u.password_hash = generate_password_hash(pw1)
        u.first_login = True
        r.db.session.commit()
        flash("Password reset.", "success")
        return redirect(url_for("admin_dashboard"))

    # --- Sync control UI -----------------------------------------------------------

    def _sync_state_response():
        with r._admin_sync_ui_lock:
            st = dict(r._admin_sync_ui_state)
        try:
            cfg = r.get_sync_service()
            tot = len(cfg.table_configs) if cfg else 0
        except Exception:
            tot = 0
        st.setdefault("total_tables", tot)
        return jsonify(st)

    @flask_app.route("/admin/sync-control")
    @login_required
    def admin_sync_control():
        require_admin()
        return render_template("admin/sync_control.html")

    @flask_app.route("/admin/sync-control/status")
    @r.limiter.exempt
    @login_required
    def admin_sync_control_status():
        require_admin()
        return _sync_state_response()

    @flask_app.route("/admin/sync-control/start", methods=["POST"])
    @login_required
    def admin_sync_control_start():
        require_admin()

        def job():
            with r._admin_sync_ui_lock:
                if r._admin_sync_ui_state.get("running"):
                    return
                r._admin_sync_ui_state["running"] = True
                r._admin_sync_ui_state["last_error"] = ""
                svc = r.get_sync_service()
                tot = len(svc.table_configs) if svc else 0
                r._admin_sync_ui_state["total_tables"] = tot
                r._admin_sync_ui_state["completed_tables"] = 0
            try:
                r._admin_sync_ui_log("Sync thread starting")
                svc = r.get_sync_service()
                if not svc:
                    r._admin_sync_ui_log("Sync service not configured (PostgreSQL + SYNC_TABLE_CONFIG required)", "warning")
                else:
                    svc.sync_once()
            except Exception as exc:
                r._admin_sync_ui_log(str(exc), "error")
                with r._admin_sync_ui_lock:
                    r._admin_sync_ui_state["last_error"] = str(exc)
            finally:
                with r._admin_sync_ui_lock:
                    r._admin_sync_ui_state["running"] = False
                    r._admin_sync_ui_state["completed_tables"] = r._admin_sync_ui_state.get("total_tables", 0)

        threading.Thread(target=job, daemon=True).start()
        return jsonify({"ok": True})
