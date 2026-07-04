import os
import re
from collections import defaultdict
from datetime import datetime

import pyodbc


MDB_PATH = os.environ.get(
    "MDB_FILE_PATH",
    r"C:\Users\User\Documents\Reporting_app\Reporting App\KISMET SECONDARY 2026  JAN (1).mdb",
)
MDB_PASSWORD = os.environ.get("MDB_PASSWORD", "Sit@dbe")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "MDB_SCHEMA_DOCUMENTATION.md")


def connect_mdb(path: str, password: str) -> pyodbc.Connection:
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        + r"DBQ="
        + path
        + ";"
        + (f"PWD={password};" if password else "")
    )
    return pyodbc.connect(conn_str)


def normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def relation_score(col_name: str, target_table: str, target_pk: str) -> int:
    c = col_name.lower()
    t = target_table.lower()
    pk = target_pk.lower()
    score = 0

    if c == pk:
        score += 6
    if c.endswith("id"):
        score += 2
    if t in c:
        score += 2
    if c == f"{t}id":
        score += 5
    if c == f"{t}_id":
        score += 5
    if c.startswith(t):
        score += 1
    return score


def group_table(table_name: str) -> str:
    n = table_name.lower()
    if any(k in n for k in ["learner", "student", "pupil"]):
        return "Learner Domain"
    if any(k in n for k in ["parent", "guardian", "nextofkin"]):
        return "Parent/Guardian Domain"
    if any(k in n for k in ["educator", "teacher", "staff"]):
        return "Educator/Staff Domain"
    if any(k in n for k in ["subject", "mark", "assessment", "result", "exam", "report", "criterion"]):
        return "Academic & Assessment Domain"
    if any(k in n for k in ["class", "grade", "phase", "stream"]):
        return "Class/Grade Structure Domain"
    if any(k in n for k in ["attendance", "discipline", "absence"]):
        return "Attendance & Discipline Domain"
    if any(k in n for k in ["fee", "finance", "invoice", "payment", "debit", "credit", "billing"]):
        return "Finance Domain"
    if any(k in n for k in ["sms", "message", "communication", "notify", "mail", "whatsapp"]):
        return "Communication Domain"
    if any(k in n for k in ["setup", "config", "setting", "param", "lookup", "code"]):
        return "Configuration/Lookup Domain"
    if any(k in n for k in ["audit", "log", "history", "patch", "sync"]):
        return "System/Audit Domain"
    return "Other/Uncategorized Domain"


def main() -> None:
    if not os.path.exists(MDB_PATH):
        raise FileNotFoundError(f"MDB file not found: {MDB_PATH}")

    con = connect_mdb(MDB_PATH, MDB_PASSWORD)
    cur = con.cursor()

    tables = [
        r.table_name
        for r in cur.tables(tableType="TABLE")
        if r.table_name and not str(r.table_name).startswith("MSys")
    ]
    tables = sorted(set(tables), key=lambda x: x.lower())

    columns_by_table = {}
    table_pk = {}
    table_rows = {}
    column_errors = {}
    type_name = {
        pyodbc.SQL_CHAR: "CHAR",
        pyodbc.SQL_VARCHAR: "VARCHAR",
        pyodbc.SQL_LONGVARCHAR: "LONGVARCHAR",
        pyodbc.SQL_WCHAR: "WCHAR",
        pyodbc.SQL_WVARCHAR: "WVARCHAR",
        pyodbc.SQL_WLONGVARCHAR: "WLONGVARCHAR",
        pyodbc.SQL_DECIMAL: "DECIMAL",
        pyodbc.SQL_NUMERIC: "NUMERIC",
        pyodbc.SQL_SMALLINT: "SMALLINT",
        pyodbc.SQL_INTEGER: "INTEGER",
        pyodbc.SQL_REAL: "REAL",
        pyodbc.SQL_FLOAT: "FLOAT",
        pyodbc.SQL_DOUBLE: "DOUBLE",
        pyodbc.SQL_BIT: "BIT",
        pyodbc.SQL_TINYINT: "TINYINT",
        pyodbc.SQL_BIGINT: "BIGINT",
        pyodbc.SQL_BINARY: "BINARY",
        pyodbc.SQL_VARBINARY: "VARBINARY",
        pyodbc.SQL_LONGVARBINARY: "LONGVARBINARY",
        pyodbc.SQL_TYPE_DATE: "DATE",
        pyodbc.SQL_TYPE_TIME: "TIME",
        pyodbc.SQL_TYPE_TIMESTAMP: "TIMESTAMP",
    }

    for t in tables:
        cols = []
        try:
            for c in cur.columns(table=t):
                cols.append(
                    {
                        "name": c.column_name,
                        "type": type_name.get(c.data_type, str(c.type_name or c.data_type)),
                        "size": c.column_size,
                        "nullable": bool(c.nullable),
                        "ordinal": c.ordinal_position,
                    }
                )
        except UnicodeDecodeError as e:
            # Fallback path: derive columns from SELECT metadata.
            try:
                cur.execute(f"SELECT * FROM [{t}] WHERE 1=0")
                desc = cur.description or []
                for idx, d in enumerate(desc, start=1):
                    cols.append(
                        {
                            "name": d[0],
                            "type": str(d[1]).replace("<class '", "").replace("'>", "") if len(d) > 1 else "UNKNOWN",
                            "size": d[2] if len(d) > 2 else None,
                            "nullable": True,
                            "ordinal": idx,
                        }
                    )
                column_errors[t] = f"used SELECT fallback after metadata decode error: {e}"
            except Exception as e2:
                column_errors[t] = f"metadata decode error: {e} | fallback failed: {e2}"
        except Exception as e:
            try:
                cur.execute(f"SELECT * FROM [{t}] WHERE 1=0")
                desc = cur.description or []
                for idx, d in enumerate(desc, start=1):
                    cols.append(
                        {
                            "name": d[0],
                            "type": str(d[1]).replace("<class '", "").replace("'>", "") if len(d) > 1 else "UNKNOWN",
                            "size": d[2] if len(d) > 2 else None,
                            "nullable": True,
                            "ordinal": idx,
                        }
                    )
                column_errors[t] = f"used SELECT fallback after metadata error: {e}"
            except Exception as e2:
                column_errors[t] = f"metadata error: {e} | fallback failed: {e2}"
        cols = sorted(cols, key=lambda x: x["ordinal"])
        deduped = []
        seen_cols = set()
        for c in cols:
            key = c["name"].lower() if c.get("name") else ""
            if key in seen_cols:
                continue
            seen_cols.add(key)
            deduped.append(c)
        cols = deduped
        columns_by_table[t] = cols

        # Heuristic PK selection.
        candidate = None
        for c in cols:
            if c["name"].lower() == "id":
                candidate = c["name"]
                break
        if not candidate:
            tnorm = normalize(t)
            for c in cols:
                cnorm = normalize(c["name"])
                if cnorm in {tnorm + "id", tnorm + "key", tnorm}:
                    candidate = c["name"]
                    break
        if not candidate:
            for c in cols:
                if c["name"].lower().endswith("id"):
                    candidate = c["name"]
                    break
        table_pk[t] = candidate or (cols[0]["name"] if cols else None)

        try:
            cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            table_rows[t] = int(cur.fetchone()[0])
        except Exception:
            table_rows[t] = -1

    # Build PK index for relationship inference.
    pk_index = defaultdict(list)
    for t, pk in table_pk.items():
        if pk:
            pk_index[pk.lower()].append((t, pk))

    inferred_relationships = []
    seen_rel = set()

    for src_table, cols in columns_by_table.items():
        for col in cols:
            cname = col["name"]
            cl = cname.lower()
            if not cl.endswith("id"):
                continue
            candidates = []

            # Exact PK-name matches first.
            for dst_table, dst_pk in pk_index.get(cl, []):
                if dst_table == src_table:
                    continue
                candidates.append((dst_table, dst_pk, relation_score(cname, dst_table, dst_pk)))

            # Name-based fallback: try TableNameId style links.
            if not candidates:
                for dst_table, dst_pk in table_pk.items():
                    if dst_table == src_table or not dst_pk:
                        continue
                    score = relation_score(cname, dst_table, dst_pk)
                    if score >= 5:
                        candidates.append((dst_table, dst_pk, score))

            if not candidates:
                continue

            candidates = sorted(candidates, key=lambda x: (-x[2], x[0].lower()))
            best = candidates[0]
            rel_key = (src_table, cname, best[0], best[1])
            if rel_key in seen_rel:
                continue
            seen_rel.add(rel_key)
            inferred_relationships.append(
                {
                    "from_table": src_table,
                    "from_column": cname,
                    "to_table": best[0],
                    "to_column": best[1],
                    "confidence": best[2],
                }
            )

    inferred_relationships = sorted(
        inferred_relationships,
        key=lambda x: (-x["confidence"], x["from_table"].lower(), x["from_column"].lower()),
    )

    # Domain grouping summary.
    grouped = defaultdict(list)
    for t in tables:
        grouped[group_table(t)].append(t)
    for g in grouped:
        grouped[g] = sorted(grouped[g], key=lambda x: x.lower())

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("# MDB Schema & Relationship Documentation")
    lines.append("")
    lines.append(f"- Source MDB: `{MDB_PATH}`")
    lines.append(f"- Generated: `{now}`")
    lines.append(f"- Total tables (excluding `MSys*`): `{len(tables)}`")
    lines.append(f"- Inferred relationships: `{len(inferred_relationships)}`")
    lines.append(f"- Tables with metadata read issues: `{len(column_errors)}`")
    lines.append("")
    lines.append("## How to Use This Document")
    lines.append("")
    lines.append("- Use **Table Dictionary** to find fields and datatypes quickly.")
    lines.append("- Use **Inferred Relationships** to choose join keys safely.")
    lines.append("- Use **Domain Groupings** to understand which tables collaborate in each workflow.")
    lines.append("- Relationship confidence is heuristic (Access metadata did not expose FK constraints directly).")
    if column_errors:
        lines.append("- Some legacy tables had unreadable metadata; those are listed in **Metadata Read Issues**.")
    lines.append("")

    if column_errors:
        lines.append("## Metadata Read Issues")
        lines.append("")
        for t in sorted(column_errors.keys(), key=lambda x: x.lower()):
            lines.append(f"- `{t}`: {column_errors[t]}")
        lines.append("")
    lines.append("## Domain Groupings")
    lines.append("")
    for domain in sorted(grouped.keys()):
        lines.append(f"### {domain}")
        lines.append("")
        lines.append(f"- Tables: `{len(grouped[domain])}`")
        lines.append("- " + ", ".join(f"`{t}`" for t in grouped[domain]))
        lines.append("")

    lines.append("## Inferred Relationships")
    lines.append("")
    lines.append("| From Table | From Column | To Table | To Column | Confidence |")
    lines.append("|---|---|---|---|---:|")
    for rel in inferred_relationships:
        lines.append(
            f"| `{rel['from_table']}` | `{rel['from_column']}` | `{rel['to_table']}` | `{rel['to_column']}` | {rel['confidence']} |"
        )
    lines.append("")

    lines.append("## Table Dictionary (All Tables and Columns)")
    lines.append("")
    for t in tables:
        lines.append(f"### `{t}`")
        rc = table_rows.get(t, -1)
        lines.append("")
        lines.append(f"- Estimated rows: `{rc if rc >= 0 else 'unknown'}`")
        lines.append(f"- Heuristic primary key: `{table_pk.get(t) or 'unknown'}`")
        lines.append("")
        lines.append("| Column | Type | Size | Nullable |")
        lines.append("|---|---|---:|---|")
        for c in columns_by_table[t]:
            lines.append(
                f"| `{c['name']}` | `{c['type']}` | {c['size'] if c['size'] is not None else ''} | {'Yes' if c['nullable'] else 'No'} |"
            )
        lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    con.close()
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Tables: {len(tables)} | Inferred relationships: {len(inferred_relationships)}")


if __name__ == "__main__":
    main()
