import os
import re
import sys
import pyodbc


def variants(phone: str) -> list[str]:
    d = re.sub(r"\D", "", phone or "")
    out = [phone.strip()]
    if d:
        out.append(d)
    if d.startswith("27") and len(d) == 11:
        out.append("+" + d)
        out.append("0" + d[2:])
        out.append(d[2:])
    if d.startswith("0") and len(d) == 10:
        out.append("+27" + d[1:])
        out.append("27" + d[1:])
    uniq = []
    for v in out:
        s = str(v).strip()
        if s and s not in uniq:
            uniq.append(s)
    return uniq


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/lookup_parent_by_phone.py <phone>")
        return 2
    phone = sys.argv[1]
    mdb_path = os.path.abspath(os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb"))
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + mdb_path + ";"
    if password:
        conn_str += "PWD=" + password + ";"
    con = pyodbc.connect(conn_str)
    cur = con.cursor()

    vlist = variants(phone)
    print("Variants:", vlist)
    found = []
    for col in ["Tel1", "Tel2", "Tel3", "SpouseCell"]:
        for v in vlist:
            try:
                rows = cur.execute(
                    f"SELECT ParentID, FName, SName, Tel1, Tel2, Tel3, SpouseCell FROM Parent_Info WHERE [{col}] = ?",
                    (v,),
                ).fetchall()
                for r in rows:
                    found.append((col, v, tuple(r)))
            except Exception:
                pass

    if not found:
        print("No parent found for this phone.")
        con.close()
        return 1

    seen = set()
    for col, v, r in found:
        pid = r[0]
        if pid in seen:
            continue
        seen.add(pid)
        print(f"ParentID={pid} matched via {col}={v}")
        print(f"  Name: {r[1]} {r[2]}")
        print(f"  Tel1={r[3]} Tel2={r[4]} Tel3={r[5]} SpouseCell={r[6]}")
        try:
            links = cur.execute(
                "SELECT ParentId, ChildId, Learnerid, Relation FROM Parent_Child WHERE ParentId = ?",
                (pid,),
            ).fetchall()
            print("  Parent_Child links:", [tuple(x) for x in links])
        except Exception as e:
            print("  Parent_Child lookup failed:", e)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
