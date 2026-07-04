import os
import re
import json
import pyodbc


SEARCH_TERMS = [
    "nisa",
    "nisaa",
    "nisaa",
    "neesa",
    "neesah",
    "nissa",
    "nisah",
    "0727376225",
    "727376225",
    "27727376225",
    "+27727376225",
]


def normalize_text(v) -> str:
    if v is None:
        return ""
    try:
        s = str(v)
    except Exception:
        return ""
    return s.strip()


def main() -> int:
    base = r"c:\Users\User\Documents\Reporting_app"
    os.chdir(base)
    mdb_path = os.path.abspath(os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb"))
    password = os.environ.get("MDB_PASSWORD", "Sit@dbe")
    conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + mdb_path + ";"
    if password:
        conn_str += "PWD=" + password + ";"

    con = pyodbc.connect(conn_str)
    cur = con.cursor()

    tables = [t.table_name for t in cur.tables(tableType="TABLE")]
    results = []
    summary = {"tables": len(tables), "rows_scanned": 0, "matches": 0}

    for table in tables:
        try:
            q = f"SELECT * FROM [{table}]"
            cur2 = con.cursor()
            cur2.execute(q)
            cols = [d[0] for d in cur2.description] if cur2.description else []
        except Exception:
            continue

        while True:
            try:
                batch = cur2.fetchmany(500)
            except Exception:
                break
            if not batch:
                break
            for row in batch:
                summary["rows_scanned"] += 1
                row_dict = {}
                row_hit = False
                for i, col in enumerate(cols):
                    v = normalize_text(row[i] if i < len(row) else None)
                    row_dict[col] = v
                    lv = v.lower()
                    if any(term in lv for term in SEARCH_TERMS):
                        row_hit = True
                if row_hit:
                    summary["matches"] += 1
                    # Keep only non-empty fields for readability
                    compact = {k: v for k, v in row_dict.items() if str(v).strip()}
                    results.append({"table": table, "row": compact})

    out = {
        "mdb_path": mdb_path,
        "search_terms": SEARCH_TERMS,
        "summary": summary,
        "results": results[:2000],  # safety cap
        "truncated": len(results) > 2000,
        "total_results_before_cap": len(results),
    }
    out_path = os.path.join(base, "scripts", "deep_scan_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("SCAN_COMPLETE")
    print("MDB:", mdb_path)
    print("TABLES:", summary["tables"])
    print("ROWS_SCANNED:", summary["rows_scanned"])
    print("MATCH_ROWS:", summary["matches"])
    print("RESULT_FILE:", out_path)
    if results:
        for r in results[:20]:
            print("HIT_TABLE:", r["table"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
