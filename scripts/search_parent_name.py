import os
import sys
import pyodbc


def main() -> int:
    term = (sys.argv[1] if len(sys.argv) > 1 else "Nisa").strip()
    mdb_path = os.path.abspath(os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb"))
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + mdb_path + ";"
    if password:
        conn_str += "PWD=" + password + ";"
    con = pyodbc.connect(conn_str)
    cur = con.cursor()

    print("Searching term:", term)
    print("MDB:", mdb_path)

    # Candidate name columns usually found in Parent_Info-like tables
    candidates = [
        ("Parent_Info", "FName"),
        ("Parent_Info", "SName"),
        ("Parent_Info", "Name"),
        ("Parent_Info", "Guardian"),
    ]

    hits = []
    for table, col in candidates:
        try:
            q = f"SELECT TOP 50 ParentID, FName, SName, Tel1, Tel2, Tel3, SpouseCell FROM [{table}] WHERE UCASE(Nz([{col}],'')) LIKE UCASE(?)"
            rows = cur.execute(q, (f"%{term}%",)).fetchall()
            for r in rows:
                hits.append((table, col, tuple(r)))
        except Exception:
            continue

    # Try to find generic tables with likely parent names
    try:
        tables = [t.table_name for t in cur.tables(tableType="TABLE")]
    except Exception:
        tables = []
    for t in tables:
        if "parent" not in t.lower():
            continue
        for col in ["FName", "SName", "Name", "Guardian"]:
            try:
                q = f"SELECT TOP 5 * FROM [{t}] WHERE UCASE(Nz([{col}],'')) LIKE UCASE(?)"
                rows = cur.execute(q, (f"%{term}%",)).fetchall()
                if rows:
                    desc = [d[0] for d in cur.description]
                    for rr in rows:
                        data = dict(zip(desc, rr))
                        hits.append((t, col, data))
            except Exception:
                continue

    print("HITS:", len(hits))
    for h in hits:
        print(h)

    # Also show Aiman linkage context
    try:
        learner = cur.execute(
            "SELECT TOP 1 ID, LearnerID, FName, SName, Grade, Status FROM Learner_Info WHERE UCASE(Trim(FName))='AIMAN' AND UCASE(Trim(SName))='AZIZ'"
        ).fetchone()
    except Exception:
        learner = None
    if learner:
        print("AIMAN:", tuple(learner))
        lid, learnerid = learner[0], str(learner[1]).strip()
        links = []
        for q, p in [
            ("SELECT ParentId, ChildId, Learnerid, Relation FROM Parent_Child WHERE ChildId=?", (lid,)),
            ("SELECT ParentId, ChildId, Learnerid, Relation FROM Parent_Child WHERE Learnerid=?", (learnerid,)),
        ]:
            try:
                links.extend(cur.execute(q, p).fetchall())
            except Exception:
                pass
        print("AIMAN_LINKS:", [tuple(x) for x in links])
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
