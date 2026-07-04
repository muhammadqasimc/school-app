"""
Inspect MDB for Communication feature: list tables, check Learner_Info and LearnerPromotion,
run the same queries used by /admin/communication (grades, learners).
Run from repo root: python scripts/inspect_mdb_communication.py
"""
import os
import sys

# Add project root so we can load app config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import pyodbc

def main():
    mdb_path = os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb")
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    abs_path = os.path.abspath(mdb_path)
    print(f"MDB path: {abs_path}")
    print(f"Exists: {os.path.exists(abs_path)}")
    if not os.path.exists(abs_path):
        print("MDB file not found. Set MDB_FILE_PATH or run from project root.")
        return 1

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + abs_path + ";"
    )
    if password:
        conn_str += r"PWD=" + password + ";"

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # List tables
    tables = [row.table_name for row in cursor.tables(tableType="TABLE")]
    print(f"\nTables ({len(tables)}): {sorted(tables)[:30]}{'...' if len(tables) > 30 else ''}")

    # Check Learner_Info
    learner_info_name = None
    for t in tables:
        if t.lower() == "learner_info" or "learner" in t.lower() and "info" in t.lower():
            learner_info_name = t
            break
    if not learner_info_name and "Learner_Info" in tables:
        learner_info_name = "Learner_Info"
    if not learner_info_name:
        learner_info_name = "Learner_Info"  # try anyway

    print(f"\n--- Table: {learner_info_name} ---")
    try:
        cursor.execute(f"SELECT TOP 1 * FROM [{learner_info_name}]")
        cols = [d[0] for d in cursor.description]
        print(f"Columns: {cols}")
        row = cursor.fetchone()
        if row:
            print(f"Sample row: {dict(zip(cols, row))}")
    except Exception as e:
        print(f"Error: {e}")

    # Grades from Learner_Info (Grade is numeric - no comparison to '')
    print("\n--- Grades from Learner_Info (fixed: no Grade <> '') ---")
    try:
        cursor.execute(f"SELECT DISTINCT Grade FROM [{learner_info_name}] WHERE Grade IS NOT NULL ORDER BY Grade")
        grades_li = [str(r[0]) for r in cursor.fetchall()]
        print(f"Count: {len(grades_li)}, Values: {grades_li[:20]}")
    except Exception as e:
        print(f"Error: {e}")

    # LearnerPromotion
    lp_name = None
    for t in tables:
        if "LearnerPromotion" in t or "learner_promotion" in t.lower():
            lp_name = t
            break
    if not lp_name and "LearnerPromotion" in tables:
        lp_name = "LearnerPromotion"
    if not lp_name:
        lp_name = "LearnerPromotion"

    print(f"\n--- Table: {lp_name} ---")
    try:
        cursor.execute(f"SELECT TOP 1 * FROM [{lp_name}]")
        cols = [d[0] for d in cursor.description]
        print(f"Columns: {cols}")
        cursor.execute(f"SELECT DISTINCT Grade FROM [{lp_name}] WHERE Grade IS NOT NULL AND Grade <> '' ORDER BY Grade")
        grades_lp = [str(r[0]) for r in cursor.fetchall()]
        print(f"Distinct grades from LearnerPromotion: {len(grades_lp)}, Values: {grades_lp[:20]}")
    except Exception as e:
        print(f"Error: {e}")

    # Learners by grade: try Learner_Info first, then join with LearnerPromotion
    print("\n--- Learners by grade (Grade=10 from Learner_Info) ---")
    try:
        cursor.execute(f"SELECT ID, LearnerID, FName, SName, Grade FROM [{learner_info_name}] WHERE Grade = ?", ("10",))
        rows = cursor.fetchall()
        print(f"Count: {len(rows)}, Sample: {rows[0] if rows else 'none'}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Learners by grade (Grade=10 from LearnerPromotion join) ---")
    try:
        # LearnerPromotion.LearnerId often matches Learner_Info.ID
        cursor.execute(f"""
            SELECT DISTINCT li.ID, li.LearnerID, li.FName, li.SName, lp.Grade
            FROM [{learner_info_name}] li
            INNER JOIN [{lp_name}] lp ON lp.LearnerId = li.ID
            WHERE lp.Grade = ?
            ORDER BY li.SName, li.FName
        """, ("10",))
        rows = cursor.fetchall()
        print(f"Count: {len(rows)}, Sample: {rows[0] if rows else 'none'}")
    except Exception as e:
        print(f"Error: {e}")

    conn.close()
    print("\nDone.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
