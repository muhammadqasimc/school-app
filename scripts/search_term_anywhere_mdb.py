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

    print("Search term:", term)
    print("MDB:", mdb_path)
    tables = [t.table_name for t in cur.tables(tableType="TABLE")]

    hits = []
    checked = 0
    for t in tables:
        try:
            cols = []
            for c in cur.columns(table=t):
                type_name = str(getattr(c, "type_name", "") or "").upper()
                if any(x in type_name for x in ("CHAR", "TEXT", "MEMO", "LONGCHAR", "VARCHAR")):
                    cols.append(c.column_name)
        except Exception:
            continue
        for col in cols:
            checked += 1
            try:
                q = f"SELECT TOP 3 * FROM [{t}] WHERE UCASE(Nz([{col}],'')) LIKE UCASE(?)"
                rows = cur.execute(q, (f"%{term}%",)).fetchall()
                if rows:
                    desc = [d[0] for d in cur.description]
                    for r in rows:
                        hits.append((t, col, dict(zip(desc, r))))
            except Exception:
                continue

    print("TEXT_COLUMNS_CHECKED:", checked)
    print("HITS:", len(hits))
    for h in hits[:40]:
        print(h)
    if len(hits) > 40:
        print("...truncated...")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
