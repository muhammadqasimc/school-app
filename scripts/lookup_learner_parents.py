import os
import sqlite3
import sys
import re
import pyodbc


def normalize_sa(phone: str) -> str:
    s = str(phone or "").strip()
    digits = re.sub(r"\D", "", s)
    if not digits:
        return ""
    if digits.startswith("0") and len(digits) == 10:
        return "+27" + digits[1:]
    if digits.startswith("27") and len(digits) == 11:
        return "+" + digits
    if s.startswith("+"):
        return "+" + digits
    return "+" + digits


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/lookup_learner_parents.py <name> <surname>")
        return 2

    name = sys.argv[1].strip()
    surname = sys.argv[2].strip()

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(base)

    # MDB lookup
    mdb_path = os.path.abspath(os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb"))
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + mdb_path + ";"
    if password:
        conn_str += "PWD=" + password + ";"
    mdb = pyodbc.connect(conn_str)
    cur = mdb.cursor()

    learners = cur.execute(
        """
        SELECT ID, LearnerID, FName, SName, Grade, Status
        FROM Learner_Info
        WHERE UCASE(Trim(FName)) = UCASE(?) AND UCASE(Trim(SName)) = UCASE(?)
        """,
        (name, surname),
    ).fetchall()

    print("Learner matches:", len(learners))
    if not learners:
        mdb.close()
        return 0

    learner_ids = []
    learner_acc = []
    for r in learners:
        print("  Learner:", tuple(r))
        if r[0] is not None:
            learner_ids.append(r[0])
        if r[1] is not None and str(r[1]).strip():
            learner_acc.append(str(r[1]).strip())

    parent_ids = set()
    for lid in learner_ids:
        try:
            rows = cur.execute("SELECT DISTINCT ParentId FROM Parent_Child WHERE ChildId = ?", (lid,)).fetchall()
            for x in rows:
                if x[0] is not None:
                    parent_ids.add(x[0])
        except Exception:
            pass
    for acc in learner_acc:
        try:
            rows = cur.execute("SELECT DISTINCT ParentId FROM Parent_Child WHERE Learnerid = ?", (acc,)).fetchall()
            for x in rows:
                if x[0] is not None:
                    parent_ids.add(x[0])
        except Exception:
            pass

    print("Parent IDs from MDB:", sorted(parent_ids))
    mdb_parents = []
    if parent_ids:
        ph = ",".join("?" for _ in parent_ids)
        rows = cur.execute(
            f"SELECT ParentID, FName, SName, Tel1, Tel2, Tel3, SpouseCell FROM Parent_Info WHERE ParentID IN ({ph})",
            tuple(parent_ids),
        ).fetchall()
        for r in rows:
            pid, fn, sn, t1, t2, t3, sc = r
            nm = (" ".join([str(fn).strip() if fn else "", str(sn).strip() if sn else ""])).strip()
            nums = [x for x in [t1, t2, t3, sc] if x is not None and str(x).strip()]
            norm_nums = []
            for n in nums:
                pn = normalize_sa(str(n))
                if pn and pn not in norm_nums:
                    norm_nums.append(pn)
            mdb_parents.append((pid, nm, norm_nums))

    print("MDB parents:")
    for pid, nm, nums in mdb_parents:
        print("  -", pid, "|", nm or "(no name)", "|", ", ".join(nums) if nums else "(no numbers)")

    mdb.close()

    # App DB candidates by learner link
    sqlite_path = os.path.join(base, "dashboard.db")
    if not os.path.exists(sqlite_path):
        return 0
    con = sqlite3.connect(sqlite_path)
    c = con.cursor()
    learner_ids_s = [str(x) for x in learner_ids]
    user_ids = set()
    if learner_ids_s:
        qmarks = ",".join("?" for _ in learner_ids_s)
        try:
            for r in c.execute(f"SELECT DISTINCT user_id FROM user_learner WHERE learner_id IN ({qmarks})", learner_ids_s).fetchall():
                user_ids.add(r[0])
        except Exception:
            pass
        try:
            for r in c.execute(f"SELECT DISTINCT id FROM user WHERE learner_id IN ({qmarks})", learner_ids_s).fetchall():
                user_ids.add(r[0])
        except Exception:
            pass

    if user_ids:
        qmarks = ",".join("?" for _ in user_ids)
        users = c.execute(f"SELECT id, username, phone FROM user WHERE id IN ({qmarks})", tuple(user_ids)).fetchall()
        print("App-linked users:")
        for u in users:
            print("  -", u)
    else:
        print("App-linked users: none found")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
