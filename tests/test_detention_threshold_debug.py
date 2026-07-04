import importlib
from datetime import datetime


def test_detention_threshold_debug_snapshot():
    app_mod = importlib.import_module("app")
    app = app_mod.app

    with app.app_context():
        latest_year_rows = app_mod.mdb_conn.execute_query(
            """
            SELECT TOP 1 CSTR(Datayear) AS Y
            FROM DisciplinaryRecords
            WHERE Datayear IS NOT NULL
            ORDER BY Datayear DESC
            """
        ) or []
        target_year = (
            str(latest_year_rows[0].get("Y")).strip()
            if latest_year_rows and latest_year_rows[0].get("Y")
            else str(datetime.now().year)
        )

        summary_rows = app_mod.mdb_conn.execute_query(
            """
            SELECT
                CSTR(dr.Learnerid) AS LearnerKey,
                SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) AS TotalDemerit,
                SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) AS TotalMerit,
                SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) - SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) AS Balance
            FROM DisciplinaryRecords dr
            WHERE CSTR(dr.Datayear) = ?
            GROUP BY CSTR(dr.Learnerid)
            HAVING SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) - SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) >= 12
            ORDER BY SUM(IIF(dr.Demerit IS NULL, 0, dr.Demerit)) - SUM(IIF(dr.Merit IS NULL, 0, dr.Merit)) DESC
            """,
            (target_year,),
        ) or []

        learner_rows = app_mod.mdb_conn.execute_query(
            """
            SELECT ID, LearnerID, FName, SName, Grade, Gender, Status
            FROM Learner_Info
            """
        ) or []
        lookup = app_mod.build_learner_lookup_by_any_id(learner_rows)

        mapped = 0
        active = 0
        grade_parse_ok = 0
        phase_counts = {"foundation": 0, "primary": 0, "highschool": 0}
        unmapped_examples = []
        raw_grade_examples = []

        for row in summary_rows:
            learner_key = str(row.get("LearnerKey") or "").strip()
            info = lookup.get(learner_key)
            if not info:
                if len(unmapped_examples) < 10:
                    unmapped_examples.append(learner_key)
                continue
            mapped += 1
            status = str(info.get("status") or "").strip().upper()
            if status == "C":
                active += 1
            grade_val = app_mod._parse_grade_int(info.get("grade"))
            if grade_val is not None:
                grade_parse_ok += 1
                if grade_val == 3:
                    phase_counts["foundation"] += 1
                elif 4 <= grade_val <= 7:
                    phase_counts["primary"] += 1
                elif 8 <= grade_val <= 12:
                    phase_counts["highschool"] += 1
            if len(raw_grade_examples) < 12:
                raw_grade_examples.append(str(info.get("grade") or ""))

        fetched_foundation = app_mod._fetch_detention_candidates("foundation", target_year, 12)
        fetched_primary = app_mod._fetch_detention_candidates("primary", target_year, 12)
        fetched_highschool = app_mod._fetch_detention_candidates("highschool", target_year, 12)

        print("\n=== Detention Threshold Debug Snapshot ===")
        print(f"Target year: {target_year}")
        print(f"Learner keys at balance >= 12: {len(summary_rows)}")
        print(f"Mapped to Learner_Info by ID/LearnerID: {mapped}")
        print(f"Mapped + active status (C): {active}")
        print(f"Mapped with parseable grade: {grade_parse_ok}")
        print(f"Phase counts from mapped data: {phase_counts}")
        print(f"Function result foundation: {len(fetched_foundation)}")
        print(f"Function result primary: {len(fetched_primary)}")
        print(f"Function result highschool: {len(fetched_highschool)}")
        print(f"Unmapped key examples: {unmapped_examples}")
        print(f"Raw grade examples: {raw_grade_examples}")

        # Keep test non-blocking; this is diagnostic output to explain filtering.
        assert True
