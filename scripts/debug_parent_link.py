import os
import re
import sys

import pyodbc


def normalize_sa(phone: str) -> str:
    s = str(phone or "").strip()
    s = re.sub(r"[\s\-()]+", "", s)
    if s.startswith("00"):
        s = "+" + s[2:]
    if s.startswith("+"):
        return "+" + re.sub(r"\D", "", s[1:])
    digits = re.sub(r"\D", "", s)
    if digits.startswith("0") and len(digits) == 10:
        return "+27" + digits[1:]
    if digits.startswith("27") and len(digits) == 11:
        return "+" + digits
    return digits


def variants(raw: str) -> list[str]:
    n = normalize_sa(raw)
    d = re.sub(r"\D", "", n)
    out = []
    for v in [raw, n, d]:
        v = str(v).strip()
        if v and v not in out:
            out.append(v)
    if d.startswith("0") and len(d) == 10:
        out += ["+27" + d[1:], "27" + d[1:]]
    if d.startswith("27") and len(d) == 11:
        out += ["+" + d, "0" + d[2:]]
    # unique preserve order
    uniq = []
    for x in out:
        if x not in uniq:
            uniq.append(x)
    return uniq


def mask_phone(v: object) -> str:
    s = str(v).strip()
    d = re.sub(r"\D", "", s)
    return ("*" * (len(d) - 4) + d[-4:]) if len(d) > 4 else ("*" * max(0, len(d) - 1) + d[-1:])


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py scripts\\debug_parent_link.py <phone>")
        return 2

    raw_phone = sys.argv[1]

    mdb_path = os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb")
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    abs_path = os.path.abspath(mdb_path)

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + abs_path + ";"
    )
    if password:
        conn_str += r"PWD=" + password + ";"

    conn = pyodbc.connect(conn_str)
    cur = conn.cursor()

    phone_cols = ["Tel1", "Tel2", "Tel3", "SpouseCell"]
    vlist = variants(raw_phone)

    # Find matching parent rows
    parents = []
    for v in vlist:
        for col in phone_cols:
            try:
                sql = f"SELECT TOP 5 ParentID, [{col}] FROM Parent_Info WHERE [{col}] = ?"
                rows = cur.execute(sql, (v,)).fetchall()
                for parent_id, stored in rows:
                    parents.append((parent_id, col, stored))
            except Exception:
                pass
        if parents:
            break

    if not parents:
        print("No Parent_Info match found for provided phone.")
        conn.close()
        return 1

    # Show parent match (masked)
    pid = parents[0][0]
    print(f"Matched ParentID: {pid} via {parents[0][1]} = {mask_phone(parents[0][2])}")

    # Pull children links
    links = cur.execute(
        "SELECT TOP 50 ParentId, ChildId, Learnerid, Relation FROM Parent_Child WHERE ParentId = ?",
        (pid,),
    ).fetchall()

    print(f"Parent_Child links: {len(links)}")
    for parent_id, child_id, learnerid, relation in links[:10]:
        print(f"- ChildId={child_id} Learnerid={learnerid} Relation={relation}")

    # Check how these map to Learner_Info
    def learner_info_by_id(val):
        try:
            row = cur.execute(
                "SELECT TOP 1 ID, LearnerID, AccessionNo, FName, SName, Grade FROM Learner_Info WHERE ID = ?",
                (int(val),),
            ).fetchone()
            return row
        except Exception:
            return None

    def learner_info_by_learnerid(val):
        row = cur.execute(
            "SELECT TOP 1 ID, LearnerID, AccessionNo, FName, SName, Grade FROM Learner_Info WHERE LearnerID = ? OR AccessionNo = ?",
            (str(val), str(val)),
        ).fetchone()
        return row

    for _, child_id, learnerid, _ in links[:10]:
        for label, key in [("ChildId", child_id), ("Learnerid", learnerid)]:
            if key is None:
                continue
            row = learner_info_by_id(key)
            mode = "ID"
            if not row:
                row = learner_info_by_learnerid(key)
                mode = "LearnerID/AccessionNo" if row else "NONE"
            print(f"  {label}={key} -> {mode} -> {'FOUND' if row else 'NOT FOUND'}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

