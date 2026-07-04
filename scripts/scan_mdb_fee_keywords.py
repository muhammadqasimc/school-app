"""
Scan an Access MDB for exemption / discount / fee-adjustment related keywords.

Usage (from project root):
  python scripts/scan_mdb_fee_keywords.py
  set MDB_FILE_PATH=path\\to\\file.mdb
  set MDB_PASSWORD=...   (optional; tries empty if omitted)

Writes: scripts/mdb_fee_keyword_scan.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    import pyodbc
except ImportError:
    print("pyodbc required", file=sys.stderr)
    raise SystemExit(1)

# Terms to search in table/column names and in text cell values
NAME_KEYWORDS = [
    "exempt",
    "exemption",
    "bursary",
    "remission",
    "discount",
    "journal",
    "korting",
    "rebate",
    "subsidy",
    "waiver",
    "concession",
    "remit",
    "fee",
    "debtor",
    "creditor",
    "ledger",
    "gltrans",
]

VALUE_KEYWORDS = [
    "EXEMPT",
    "EXEMPTION",
    "BURSARY",
    "REMISSION",
    "DISCOUNT",
    "JOURNAL",
    "KORTING",
    "REBATE",
    "WRITE OFF",
    "WRITEOFF",
    "CREDIT NOTE",
    "SUBSIDY",
    "WAIVER",
    "CONCESSION",
    "REMIT",
    "ALLOWANCE",
    "ADJUSTMENT",
    "GL ",
    "DEBT RELIEF",
    "FEE REDUCT",
    "PART PAY",
    "SCHOLARSHIP",
    "SPONSOR",
    "VRYSTELLING",
    "AFSLAG",
    "SCHOOL FEES",
    "SCHOOL FEE",
    "PARTIAL EXEMPT",
]


def _is_text_col(type_name: str) -> bool:
    """Treat as searchable text unless clearly numeric/datetime (Access/pyodbc varies)."""
    t = (type_name or "").upper()
    if not t:
        return True
    if "LONGCHAR" in t or "LONGVARCHAR" in t or "MEMO" in t:
        return True
    if any(
        x in t
        for x in (
            "INT",
            "LONG",
            "DOUBLE",
            "SINGLE",
            "REAL",
            "FLOAT",
            "CURRENCY",
            "MONEY",
            "BIT",
            "BOOL",
            "DATE",
            "TIME",
            "GUID",
            "COUNTER",
            "AUTOINCREMENT",
            "AUTO",
        )
    ):
        if "CHAR" in t or "TEXT" in t or "NOTE" in t:
            return True
        return False
    return True


def _connect(mdb_path: str, passwords: list[str | None]):
    mdb_path = os.path.abspath(mdb_path)
    last_err = None
    for pwd in passwords:
        cs = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + mdb_path + ";"
        if pwd:
            cs += "PWD=" + pwd + ";"
        try:
            return pyodbc.connect(cs), pwd
        except Exception as e:
            last_err = e
            continue
    raise last_err


def main() -> int:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(base)
    mdb_path = os.environ.get("MDB_FILE_PATH", "KISMET SECONDARY 2026  JAN (1).mdb")
    if not os.path.isfile(mdb_path):
        mdb_path = os.path.join(base, mdb_path)
    pwd_env = os.environ.get("MDB_PASSWORD")
    passwords_to_try = []
    if pwd_env is not None:
        passwords_to_try.append(pwd_env)
        passwords_to_try.append(pwd_env.strip() or None)
    passwords_to_try.extend([None, "Sit@dbe"])

    try:
        con, used_pwd = _connect(mdb_path, passwords_to_try)
    except Exception as e:
        print("CONNECT_FAILED:", e, file=sys.stderr)
        print("Tried MDB:", os.path.abspath(mdb_path), file=sys.stderr)
        return 1

    cur = con.cursor()
    tables = sorted([t.table_name for t in cur.tables(tableType="TABLE")])

    name_hits: list[dict] = []
    for t in tables:
        tl = t.lower()
        for kw in NAME_KEYWORDS:
            if kw in tl:
                name_hits.append({"table": t, "keyword": kw, "kind": "table_name"})
                break

    table_columns: dict[str, list[tuple[str, str]]] = {}
    for t in tables:
        cols = []
        try:
            for c in cur.columns(table=t):
                try:
                    cols.append((c.column_name, str(getattr(c, "type_name", "") or "")))
                except Exception:
                    continue
                cl = (c.column_name or "").lower()
                for kw in NAME_KEYWORDS:
                    if kw in cl:
                        name_hits.append({"table": t, "column": c.column_name, "keyword": kw, "kind": "column_name"})
        except Exception:
            pass
        table_columns[t] = cols

    # Scan text cells: batched OR LIKE (Access can fail on huge WHERE clauses)
    value_hits: list[dict] = []
    max_tables = int(os.environ.get("SCAN_MDB_MAX_TABLES", "500"))
    max_rows_per_hit = int(os.environ.get("SCAN_MDB_MAX_ROWS_PER_HIT", "5"))
    batch_size = int(os.environ.get("SCAN_KEYWORD_BATCH", "8"))

    def keyword_batches(items: list[str], n: int) -> list[list[str]]:
        return [items[i : i + n] for i in range(0, len(items), n)]

    seen_tc: set[tuple[str, str]] = set()

    for t in tables[:max_tables]:
        cols = table_columns.get(t) or []
        text_cols = [c[0] for c in cols if _is_text_col(c[1])]
        if not text_cols:
            continue

        for col in text_cols:
            if (t, col) in seen_tc:
                continue
            samples: list[dict] = []
            matched_kw: set[str] = set()

            for batch in keyword_batches(VALUE_KEYWORDS, batch_size):
                parts = []
                params = []
                for vk in batch:
                    # Nz() is not available in ODBC Access SQL; IIf works.
                    parts.append(f"IIf([{col}] IS NULL, '', [{col}]) LIKE ?")
                    params.append(f"%{vk}%")
                where_sql = " OR ".join(parts)
                q = f"SELECT TOP {max_rows_per_hit} * FROM [{t}] WHERE {where_sql}"
                try:
                    cur2 = con.cursor()
                    cur2.execute(q, tuple(params))
                    desc = [d[0] for d in cur2.description] if cur2.description else []
                    rows = cur2.fetchall()
                    for row in rows:
                        row_dict = {}
                        for i, name in enumerate(desc):
                            v = row[i] if i < len(row) else None
                            if v is not None and not isinstance(v, (int, float)):
                                s = str(v).strip()
                                if len(s) > 500:
                                    s = s[:500] + "…"
                                row_dict[name] = s
                            else:
                                row_dict[name] = v
                        blob = " ".join(str(x) for x in row_dict.values() if x).upper()
                        for vk in VALUE_KEYWORDS:
                            if vk in blob or vk.replace(" ", "") in blob.replace(" ", ""):
                                matched_kw.add(vk)
                        if len(samples) < max_rows_per_hit:
                            samples.append(row_dict)
                except Exception:
                    continue

            if samples or matched_kw:
                seen_tc.add((t, col))
                value_hits.append(
                    {
                        "table": t,
                        "column": col,
                        "matchedKeywords": sorted(matched_kw),
                        "sampleRows": samples[:max_rows_per_hit],
                    }
                )

    # Always scan known finance narrative columns (ODBC may type memo fields oddly).
    extra_columns = [
        ("DebtorsTrans", "Desc"),
        ("GLTrans", "Description"),
        ("GLTrans", "Narration"),
        ("Journals", "Description"),
        ("Journals", "Narrative"),
        ("FeeExemptions", "Reason"),
        ("FeeExemptions", "ExemptionReason"),
        ("FeeExemptions", "Comments"),
    ]
    known_schema_columns = {
        "DebtorsTrans": ("Desc",),
        "FeeExemptions": ("Reason", "ExemptionReason", "Comments", "LearnerId", "Grade"),
    }
    for t, col in extra_columns:
        if (t, col) in seen_tc:
            continue
        if t not in tables:
            continue
        col_names = {c[0] for c in (table_columns.get(t) or [])}
        if col not in col_names and col not in known_schema_columns.get(t, ()):
            continue
        samples = []
        matched_kw = set()
        for batch in keyword_batches(VALUE_KEYWORDS, batch_size):
            parts = []
            params = []
            for vk in batch:
                parts.append(f"IIf([{col}] IS NULL, '', [{col}]) LIKE ?")
                params.append(f"%{vk}%")
            where_sql = " OR ".join(parts)
            q = f"SELECT TOP {max_rows_per_hit} * FROM [{t}] WHERE {where_sql}"
            try:
                cur2 = con.cursor()
                cur2.execute(q, tuple(params))
                desc = [d[0] for d in cur2.description] if cur2.description else []
                rows = cur2.fetchall()
                for row in rows:
                    row_dict = {}
                    for i, name in enumerate(desc):
                        v = row[i] if i < len(row) else None
                        if v is not None and not isinstance(v, (int, float)):
                            s = str(v).strip()
                            if len(s) > 500:
                                s = s[:500] + "…"
                            row_dict[name] = s
                        else:
                            row_dict[name] = v
                    blob = " ".join(str(x) for x in row_dict.values() if x).upper()
                    for vk in VALUE_KEYWORDS:
                        if vk in blob or vk.replace(" ", "") in blob.replace(" ", ""):
                            matched_kw.add(vk)
                    if len(samples) < max_rows_per_hit:
                        samples.append(row_dict)
            except Exception:
                continue
        if samples or matched_kw:
            seen_tc.add((t, col))
            value_hits.append(
                {
                    "table": t,
                    "column": col,
                    "matchedKeywords": sorted(matched_kw),
                    "sampleRows": samples[:max_rows_per_hit],
                    "priorityColumn": True,
                }
            )

    con.close()

    out = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mdbPath": os.path.abspath(mdb_path),
        "passwordUsed": "set" if used_pwd else "empty",
        "tableCount": len(tables),
        "nameHits": name_hits,
        "valueHits": value_hits,
        "valueKeywordsUsed": VALUE_KEYWORDS,
        "nameKeywordsUsed": NAME_KEYWORDS,
    }
    out_path = os.path.join(base, "scripts", "mdb_fee_keyword_scan.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("SCAN_OK")
    print("MDB:", os.path.abspath(mdb_path))
    print("TABLES:", len(tables))
    print("NAME_HITS:", len(name_hits))
    print("VALUE_HITS:", len(value_hits))
    print("JSON:", out_path)
    if name_hits:
        print("--- sample name hits (first 15) ---")
        for h in name_hits[:15]:
            print(h)
    if value_hits:
        print("--- sample value hits (first 10) ---")
        for h in value_hits[:10]:
            print(h.get("table"), h.get("column"), h.get("matchedKeywords", [])[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
