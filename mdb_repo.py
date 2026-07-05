"""
mdb_repo.py — Drop-in replacement for PostgresRepository + MDBConnection
that reads the MDB file directly using mdbtools (mdb-json CLI).

No PostgreSQL required. All queries run against the in-memory cache of the MDB file.
"""

import json
import logging
import os
import re
import sqlite3
import subprocess
import threading
from collections import OrderedDict, defaultdict
from typing import Any

logger = logging.getLogger(__name__)

# ── SQLite path (from environment or auto-detect) ──────────────────────
_SQLITE_DB = os.environ.get(
    "SCHOOL_DATA_DB",
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "school_data.db"),
)


# ── Global SQLite connection (reused across queries) ───────────────────
_sqlite_conn: sqlite3.Connection | None = None
_sqlite_lock = threading.Lock()


def _get_sqlite_conn() -> sqlite3.Connection | None:
    global _sqlite_conn
    if _sqlite_conn is None:
        with _sqlite_lock:
            if _sqlite_conn is None:
                # Check env at runtime (may have been set by load_dotenv after import)
                sqlite_path = os.environ.get(
                    "SCHOOL_DATA_DB",
                    os.path.join(os.path.abspath(os.path.dirname(__file__)), "school_data.db"),
                )
                if not os.path.isfile(sqlite_path):
                    logger.warning("school_data.db not found at %s", sqlite_path)
                    return None
                try:
                    conn = sqlite3.connect(sqlite_path, check_same_thread=False)
                    conn.row_factory = sqlite3.Row
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA cache_size=-80000")  # ~80 MB cache
                    _sqlite_conn = conn
                    logger.info("SQLite school_data.db connected: %s", sqlite_path)
                except Exception as e:
                    logger.error("Failed to connect to school_data.db: %s", e)
                    return None
    return _sqlite_conn


# ── Access SQL → SQLite translator ─────────────────────────────────────
def _access_to_sqlite(sql: str) -> str:
    """Convert common Access SQL patterns to SQLite-compatible SQL."""
    s = sql

    # IIF(a,b,c) → CASE WHEN a THEN b ELSE c END
    # Handle nested IIF
    def _replace_iif(m):
        cond = m.group(1)
        true_v = m.group(2)
        false_v = m.group(3)
        return f"CASE WHEN {cond} THEN {true_v} ELSE {false_v} END"

    # Simple case (non-nested)
    s = re.sub(r"(?i)IIF\s*\(([^,()]+|[^()]*\([^()]*\))\s*,\s*([^,()]+)\s*,\s*([^)]+)\)", _replace_iif, s)

    # CSTR(x) → CAST(x AS TEXT)
    s = re.sub(r"(?i)CSTR\s*\(([^)]+)\)", r"CAST(\1 AS TEXT)", s)

    # UCASE(x) → UPPER(x)
    s = re.sub(r"(?i)UCASE\s*\(([^)]+)\)", r"UPPER(\1)", s)

    # CLNG(x) → CAST(x AS INTEGER)
    s = re.sub(r"(?i)CLNG\s*\(([^)]+)\)", r"CAST(\1 AS INTEGER)", s)

    # CDBL(x) → CAST(x AS REAL)
    s = re.sub(r"(?i)CDBL\s*\(([^)]+)\)", r"CAST(\1 AS REAL)", s)

    # NZ(x, default) → COALESCE(x, default)
    s = re.sub(r"(?i)NZ\s*\(([^,]+)\s*,\s*([^)]+)\)", r"COALESCE(\1, \2)", s)

    # TOP N → LIMIT N (at end of SELECT, before FROM — need to move it)
    # Access: SELECT TOP 10 col FROM table
    # SQLite: SELECT col FROM table LIMIT 10
    top_m = re.search(r"(?i)\bSELECT\s+TOP\s+(\d+)", s)
    limit_clause = None
    if top_m:
        limit_clause = int(top_m.group(1))
        s = s[:top_m.start()] + "SELECT " + s[top_m.end():]

    # [brackets] → "brackets" (SQLite accepts double-quotes for identifiers)
    s = re.sub(r"\[(\w+)\]", r'"\1"', s)

    # Replace Access string concatenation & with ||
    s = re.sub(r"(?<![<>!])&(?![&<>])", "||", s)

    # Handle InStr(1, string, substring) → INSTR(string, substring) 
    # Access: InStr(1, [Desc], 'EXEMPT') > 0
    # SQLite: INSTR([Desc], 'EXEMPT') > 0
    s = re.sub(r"(?i)InStr\s*\(\s*\d+\s*,\s*([^,]+)\s*,\s*('[^']*')\s*\)", r"INSTR(\1, \2)", s)
    # InStr with 4 args (start, string, substring, compare) → INSTR(string, substring)
    s = re.sub(r"(?i)InStr\s*\(\s*\d+\s*,\s*([^,]+)\s*,\s*('[^']*')\s*,\s*\d+\s*\)", r"INSTR(\1, \2)", s)
    s = re.sub(r"(?i)\bNOW\s*\(\s*\)", "datetime('now')", s)

    # Handle DATE() → date('now')
    s = re.sub(r"(?i)\bDATE\s*\(\s*\)", "date('now')", s)

    if limit_clause is not None:
        s = s.rstrip().rstrip(";")
        s += f" LIMIT {limit_clause}"

    return s


def _try_sqlite_query(sql: str, params: tuple) -> list[dict] | None:
    """Try to run the query on SQLite. Returns None if SQLite is unavailable."""
    conn = _get_sqlite_conn()
    if conn is None:
        return None
    try:
        sql_sqlite = _access_to_sqlite(sql)
        cursor = conn.execute(sql_sqlite, params)
        rows = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return rows
    except Exception as e:
        logger.debug("SQLite query failed for [%s..%s]: %s", sql[:60], sql[-30:], e)
        return None

# ── Path helpers ──────────────────────────────────────────────────────────

_MDBTOOLS_BIN = os.path.expanduser("~/.local/bin")
_SUBPROC_ENV = os.environ.copy()


def _mdb_export_json(mdb_path: str, table_name: str) -> list[dict]:
    """Export a full MDB table as a list of dicts using mdb-json."""
    exe = os.path.join(_MDBTOOLS_BIN, "mdb-json")
    if not os.path.isfile(exe):
        exe = "mdb-json"
    try:
        proc = subprocess.run(
            [exe, mdb_path, table_name],
            capture_output=True,
            text=True,
            timeout=60,
            env=_SUBPROC_ENV,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "mdb-json tool not found. Install mdbtools"
        )
    if proc.returncode != 0:
        err = proc.stderr.strip()
        if err:
            raise RuntimeError(f"mdb-json error for {table_name}: {err}")
        return []
    lines = [l for l in proc.stdout.splitlines() if l.strip()]
    rows: list[dict] = []
    for line in lines:
        try:
            row = json.loads(line)
            rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows


# ── Helper: extract column name from table.col or [table].[col] ──────────

def _extract_col(expr: str) -> str:
    """Strip table prefix, brackets, and function wrappers from a column expression."""
    col = expr.strip()
    # Remove table. prefix
    col = re.sub(r"^[A-Za-z_][A-Za-z0-9_]*\.", "", col)
    # Remove brackets
    col = col.strip("[]")
    return col


# ── SQL Parser & Evaluator ────────────────────────────────────────────────

def _parse_table_name(sql: str) -> str | None:
    """Extract the primary table name."""
    m = re.search(r"(?is)\bFROM\s+\[?([A-Za-z_][A-Za-z0-9_]*)\]?", sql)
    return m.group(1) if m else None


def _parse_join_tables(sql: str) -> dict[str, str]:
    """Extract table names and aliases: {alias: real_name}."""
    tables: dict[str, str] = {}
    m = re.search(r"(?is)\bFROM\s+\[?([A-Za-z_][A-Za-z0-9_]*)\]?(?:\s+([A-Za-z_][A-Za-z0-9_]*))?", sql)
    if m:
        table = m.group(1)
        alias = m.group(2) or table
        tables[alias] = table
    for m in re.finditer(
        r"(?is)(?:INNER|LEFT|RIGHT|OUTER)?\s*JOIN\s+\[?([A-Za-z_][A-Za-z0-9_]*)\]?(?:\s+([A-Za-z_][A-Za-z0-9_]*))?", sql
    ):
        table = m.group(1)
        alias = m.group(2) or table
        tables[alias] = table
    return tables


def _parse_columns(sql: str) -> list[tuple[str, str]] | None:
    """Extract (col_expr, alias) pairs. Returns None for SELECT * or table.*."""
    m = re.search(r"(?is)\bSELECT\s+(.*?)\bFROM\b", sql)
    if not m:
        return None
    select_part = m.group(1).strip()
    select_part = re.sub(r"(?is)\bTOP\s+\d+\s+", "", select_part).strip()
    select_part = re.sub(r"(?is)\bDISTINCT\s+", "", select_part).strip()
    select_part = select_part.strip().rstrip(";").strip()

    if select_part.strip() in ("*", "1"):
        return None if select_part.strip() == "*" else [("1", "1")]
    if re.match(r"^\w+\.\*\s*$", select_part.strip()):
        return None

    columns: list[tuple[str, str]] = []
    for col in _split_columns(select_part):
        col = col.strip()
        if not col:
            continue
        alias = None
        m_alias = re.search(r"\s+AS\s+(\w+)\s*$", col, re.IGNORECASE)
        if m_alias:
            alias = m_alias.group(1)
            col = col[: m_alias.start()].strip()
        col_clean = _extract_col(col)
        # Strip function wrappers: CSTR(...), UCASE(...), etc.
        while re.match(r"^(CSTR|UCASE|LCASE|IIF|ISNULL|YEAR|MONTH|DAY|NOW|DATE)\s*\(", col_clean, re.IGNORECASE):
            inner = re.search(r"\((.*)\)", col_clean)
            if inner:
                col_clean = _extract_col(inner.group(1))
            else:
                break
        columns.append((col_clean, alias or col_clean))
    return columns or None


def _split_columns(select_part: str) -> list[str]:
    parts = []
    depth = 0
    current = ""
    for ch in select_part:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
            continue
        current += ch
    if current.strip():
        parts.append(current)
    return parts


def _parse_where_conditions(sql: str, params: tuple) -> list[tuple[str, str, Any, int]]:
    """
    Parse WHERE clause. Returns list of (column, operator, data, extra).
    Returns [] on unrecognized patterns (caller falls back to no filtering).
    """
    m = re.search(r"(?is)\bWHERE\s+(.*?)(?:\bORDER\s+BY\b|\bGROUP\s+BY\b|\bHAVING\b|\bLIMIT\b|$)", sql)
    if not m:
        return []
    where_clause = m.group(1).strip()
    if not where_clause:
        return []

    # Split on AND at top level, handling OR by splitting on OR too
    # We'll process AND-separated clauses
    and_parts = _split_on_AND(where_clause)
    conditions: list[tuple[str, str, Any, int]] = []
    param_idx = 0

    for part in and_parts:
        part = part.strip()
        if not part:
            continue

        # Try IS NOT NULL / IS NULL
        m_null = re.match(
            r"(?is)^\[?[A-Za-z_][A-Za-z0-9_]*\.?\[?([A-Za-z_][A-Za-z0-9_]*)\]?\s+IS\s+(NOT\s+)?NULL$", part
        )
        if m_null:
            col = m_null.group(1)
            op = "IS_NOT_NULL" if m_null.group(2) else "IS_NULL"
            conditions.append((col, op, None, -1))
            continue

        # Try = ?
        stripped = re.sub(r"^\[?[A-Za-z_][A-Za-z0-9_]*\]?\.", "", part)  # remove table. prefix
        m_eq = re.match(r"(?is)^\[?(\w+)\]?\s*=\s*\?$", stripped)
        if m_eq:
            conditions.append((m_eq.group(1), "=", param_idx, False))
            param_idx += 1
            continue

        # Try UCASE(CSTR([col])) = ?
        m_ucase = re.match(
            r"(?is)^UCASE\s*\(\s*CSTR\s*\(\s*\[?(\w+)\]?\s*\)\s*\)\s*=\s*\?$", stripped
        )
        if m_ucase:
            conditions.append((m_ucase.group(1), "UCASE_CSTR_EQ", param_idx, True))
            param_idx += 1
            continue

        # Try CSTR([col]) = ?
        m_cstr = re.match(
            r"(?is)^CSTR\s*\(\s*\[?(\w+)\]?\s*\)\s*=\s*\?$", stripped
        )
        if m_cstr:
            conditions.append((m_cstr.group(1), "CSTR_EQ", param_idx, True))
            param_idx += 1
            continue

        # Try col <> ''
        m_ne = re.match(
            r"(?is)^\[?(\w+)\]?\s*<>\s*''$", stripped
        )
        if m_ne:
            conditions.append((m_ne.group(1), "NOT_EMPTY", None, -1))
            continue

        # Try col IN (?, ?)
        m_in = re.match(
            r"(?is)^(?:CSTR\s*\()?\s*\[?(\w+)\]?(?:\s*\))?\s+IN\s+\(([?,?\s]+)\)$", stripped
        )
        if m_in:
            col = m_in.group(1)
            ph_count = m_in.group(2).count("?")
            conditions.append((col, "IN", ph_count, param_idx))
            param_idx += ph_count
            continue

        # Try col BETWEEN ? AND ?
        m_between = re.match(
            r"(?is)^\[?(\w+)\]?\s+BETWEEN\s+\?\s+AND\s+\?$", stripped
        )
        if m_between:
            col = m_between.group(1)
            conditions.append((col, "BETWEEN", param_idx, param_idx + 1))
            param_idx += 2
            continue

        # Try col = ? OR col2 = ? (simple OR of = conditions)
        m_or = re.match(
            r"(?is)^\[?(\w+)\]?\s*=\s*\?\s+OR\s+\[?(\w+)\]?\s*=\s*\?$", stripped
        )
        if m_or:
            col1, col2 = m_or.group(1), m_or.group(2)
            conditions.append((col1, "OR_EQ", param_idx, col2))
            param_idx += 2
            continue

        # Unrecognized -> log warning and skip, don't abort all filtering
        logger.warning(
            "Unrecognized WHERE condition pattern, skipping: %s",
            part[:100],
        )
        continue

    return conditions


def _split_on_AND(clause: str) -> list[str]:
    parts = []
    depth = 0
    current = ""
    i = 0
    while i < len(clause):
        if clause[i] in "(":
            depth += 1
        elif clause[i] in ")":
            depth -= 1
        elif depth == 0 and clause[i : i + 5].upper() == " AND ":
            parts.append(current)
            current = ""
            i += 5
            continue
        current += clause[i]
        i += 1
    if current.strip():
        parts.append(current)
    return parts


def _parse_limit(sql: str) -> int | None:
    m = re.search(r"(?is)\bTOP\s+(\d+)", sql)
    if m:
        return int(m.group(1))
    m = re.search(r"(?is)\bLIMIT\s+(\d+)", sql)
    return int(m.group(1)) if m else None


def _parse_order_by(sql: str) -> list[tuple[str, bool]]:
    m = re.search(r"(?is)\bORDER\s+BY\s+(.*?)(?:\bLIMIT\b|$)", sql)
    if not m:
        return []
    order_clause = m.group(1).strip().rstrip(";").strip()
    orders = []
    for part in order_clause.split(","):
        part = part.strip()
        desc = bool(re.search(r"\bDESC\b", part, re.IGNORECASE))
        col = re.sub(r"\s+(ASC|DESC)\b", "", part, flags=re.IGNORECASE).strip()
        col = _extract_col(col)
        orders.append((col.strip(), desc))
    return orders


def _parse_group_by(sql: str) -> list[str]:
    m = re.search(r"(?is)\bGROUP\s+BY\s+(.*?)(?:\bHAVING\b|\bORDER\s+BY\b|$)", sql)
    if not m:
        return []
    return [_extract_col(c) for c in m.group(1).split(",") if c.strip()]


def _is_distinct(sql: str) -> bool:
    return bool(re.search(r"(?is)\bSELECT\s+DISTINCT\b", sql))


def _has_join(sql: str) -> bool:
    return bool(re.search(r"(?is)\bJOIN\b", sql))


def _has_aggregate(sql: str) -> bool:
    return bool(re.search(r"(?is)\b(SUM|MAX|MIN|COUNT|AVG)\s*\(", sql))


def _value_from_row(row: dict, col: str) -> Any:
    if col in row:
        return row[col]
    col_lower = col.lower()
    for k, v in row.items():
        if k.lower() == col_lower:
            return v
    return None


# ── WHERE condition evaluators ────────────────────────────────────────────

def _match_value(val: Any, param: Any) -> bool:
    if val is None and param is None:
        return True
    if val is None or param is None:
        return False
    if type(val) == type(param):
        return val == param
    try:
        if int(val) == int(param):
            return True
    except (ValueError, TypeError):
        pass
    return str(val).strip() == str(param).strip()


def _apply_conditions(row: dict, conditions: list, params: tuple) -> bool:
    for col, op, data, extra in conditions:
        val = _value_from_row(row, col)

        if op == "=":
            idx = data
            if idx < len(params) and _match_value(val, params[idx]):
                continue
            return False

        elif op == "UCASE_CSTR_EQ":
            idx = data
            if idx < len(params) and str(val or "").upper() == str(params[idx] or "").upper():
                continue
            return False

        elif op == "CSTR_EQ":
            idx = data
            if idx < len(params) and str(val or "") == str(params[idx] or ""):
                continue
            return False

        elif op == "IN":
            count = data
            start_idx = extra  # Use stored param_idx
            val_str = str(val or "")
            for i in range(start_idx, start_idx + count):
                if i < len(params) and str(params[i] or "") == val_str:
                    return True
            return False

        elif op == "IS_NOT_NULL":
            if val is not None:
                continue
            return False

        elif op == "IS_NULL":
            if val is None:
                continue
            return False

        elif op == "NOT_EMPTY":
            if val is not None and str(val).strip():
                continue
            return False

        elif op == "BETWEEN":
            start_idx = data
            end_idx = extra
            if start_idx < len(params) and end_idx < len(params):
                lo = params[start_idx]
                hi = params[end_idx]
                if val is not None and lo is not None and hi is not None:
                    try:
                        if float(lo) <= float(val) <= float(hi):
                            continue
                    except (ValueError, TypeError):
                        if str(lo) <= str(val) <= str(hi):
                            continue
            return False

        elif op == "OR_EQ":
            idx1 = data
            col2 = extra
            val2 = _value_from_row(row, col2)
            if idx1 < len(params) and idx1 + 1 < len(params):
                if _match_value(val, params[idx1]) or _match_value(val2, params[idx1 + 1]):
                    continue
            return False

        else:
            return False

    return True


# ── JOIN execution ────────────────────────────────────────────────────────

def _execute_join_query(mdb_path: str, sql: str, params: tuple, tables_data: dict) -> list[dict]:
    table_aliases = _parse_join_tables(sql)
    for alias, table in table_aliases.items():
        if table not in tables_data:
            tables_data[table] = _mdb_export_json(mdb_path, table)

    if len(table_aliases) <= 1:
        main_table = list(table_aliases.values())[0]
        return tables_data.get(main_table, [])

    on_conditions = []
    for m in re.finditer(
        r"(?is)(?:INNER|LEFT|RIGHT|OUTER)?\s*JOIN\s+\[?[A-Za-z_0-9]+\]?(?:\s+[A-Za-z_][A-Za-z0-9_]*)?\s+ON\s+(.*?)(?:\s+(?:INNER|LEFT|RIGHT|OUTER)?\s*JOIN|\s+WHERE|\s+ORDER\s+BY|\s+GROUP\s+BY|\s+HAVING|$)", sql
    ):
        on_conditions.append(m.group(1).strip())

    aliases_list = list(table_aliases.keys())
    main_alias = aliases_list[0]
    main_table = table_aliases[main_alias]
    result = [dict(r) for r in tables_data.get(main_table, [])]

    join_idx = 1
    while join_idx < len(aliases_list):
        alias = aliases_list[join_idx]
        table = table_aliases[alias]
        join_rows = tables_data.get(table, [])
        on_clause = on_conditions[join_idx - 1] if join_idx - 1 < len(on_conditions) else ""
        is_left = bool(re.search(r"(?is)\bLEFT\s+JOIN\b", sql))

        join_matches = re.findall(
            r"(?is)\[?(\w+)\]?\.\[?(\w+)\]?\s*=\s*\[?(\w+)\]?\.\[?(\w+)\]?", on_clause
        )

        new_result = []
        for mr in result:
            matched = False
            for jr in join_rows:
                for left_tbl, left_col, right_tbl, right_col in join_matches:
                    left_val = _value_from_row(mr, left_col)
                    right_val = _value_from_row(jr, right_col)
                    if str(left_val or "") == str(right_val or ""):
                        merged = dict(mr)
                        for k, v in jr.items():
                            merged[k] = v
                        new_result.append(merged)
                        matched = True
                        break
            if not matched and is_left:
                new_result.append(dict(mr))

        result = new_result
        join_idx += 1

    return result


# ── Aggregate execution ───────────────────────────────────────────────────

def _execute_aggregate_query(rows: list[dict], sql: str, params: tuple) -> list[dict]:
    # MAX without GROUP BY
    m_max = re.search(r"(?is)MAX\s*\(\s*\[?(\w+)\]?\s*\)\s+AS\s+(\w+)", sql)
    if not m_max:
        m_max = re.search(r"(?is)MAX\s*\(\s*\[?\w+\]?\.\[?(\w+)\]?\s*\)\s+AS\s+(\w+)", sql)
    if m_max and "GROUP BY" not in sql.upper():
        col = m_max.group(1)
        alias = m_max.group(2)
        max_val = None
        for row in rows:
            val = _value_from_row(row, col)
            if val is not None and (max_val is None or val > max_val):
                max_val = val
        return [{alias: max_val}]

    if "GROUP BY" not in sql.upper() and "SUM(" not in sql.upper():
        return rows

    group_cols = _parse_group_by(sql)
    limit = _parse_limit(sql)

    # Extract aggregates
    agg_exprs = []
    for m in re.finditer(r"(?is)(SUM|MAX|MIN|COUNT|AVG)\s*\((.*?)\)(?:\s+AS\s+(\w+))?", sql):
        func = m.group(1).upper()
        inner = m.group(2).strip()
        alias = m.group(3) or f"{func.lower()}_{len(agg_exprs)}"
        agg_exprs.append((func, inner, alias))

    iif_in_sum = any(
        func == "SUM" and "IIF" in inner.upper()
        for func, inner, alias in agg_exprs
    )
    if iif_in_sum:
        return _execute_iif_aggregate(rows, sql, group_cols, agg_exprs, limit, params)

    # Simple GROUP BY
    grouped: dict = defaultdict(list)
    for row in rows:
        key = tuple(str(_value_from_row(row, c) or "") for c in group_cols)
        grouped[key].append(row)

    result = []
    m_having = re.search(r"(?is)\bHAVING\s+(.*?)(?:\bORDER\s+BY\b|$)", sql)
    having_expr = m_having.group(1).strip() if m_having else None

    for key, grp_rows in grouped.items():
        out = {}
        for i, c in enumerate(group_cols):
            out[c] = key[i]
        for func, inner, alias in agg_exprs:
            inner_clean = _extract_col(inner)
            vals = [v for r in grp_rows if (v := _value_from_row(r, inner_clean)) is not None]
            if func == "SUM":
                out[alias] = sum(float(v) for v in vals) if vals else 0.0
            elif func == "MAX":
                out[alias] = max(vals) if vals else None
            elif func == "MIN":
                out[alias] = min(vals) if vals else None
            elif func == "COUNT":
                out[alias] = len(vals)
            elif func == "AVG":
                out[alias] = sum(float(v) for v in vals) / len(vals) if vals else 0.0

        # HAVING (simple >= ? pattern)
        if having_expr:
            hm = re.search(r"(?is)(\w+)\s*>=\s*\?", having_expr)
            if hm:
                alias_name = hm.group(1)
                h_val = params[-1] if params else 0
                if not (float(out.get(alias_name, 0) or 0) >= float(h_val or 0)):
                    continue

        result.append(out)

    order_by = _parse_order_by(sql)
    if order_by:
        for od, desc in reversed(order_by):
            result.sort(key=lambda r, c=od: float(r.get(c, 0) or 0), reverse=desc)
    if limit:
        result = result[:limit]

    return result


def _execute_iif_aggregate(rows, sql, group_cols, agg_exprs, limit, params):
    grouped: dict = defaultdict(list)
    for row in rows:
        key = tuple(str(_value_from_row(row, c) or "") for c in group_cols)
        grouped[key].append(row)

    iif_exprs = []
    for func, inner, alias in agg_exprs:
        if func == "SUM":
            for m in re.finditer(r"(?is)IIF\s*\((.*?),(.*?),(.*?)\)", inner):
                iif_exprs.append((alias, m.group(1).strip(), m.group(2).strip(), m.group(3).strip()))

    result = []
    having_expr = None
    m_having = re.search(r"(?is)\bHAVING\s+(.*?)(?:\bORDER\s+BY\b|$)", sql)
    if m_having:
        having_expr = m_having.group(1).strip()

    for key, grp_rows in grouped.items():
        out = {}
        for i, c in enumerate(group_cols):
            out[c] = key[i]
        for alias, cond, true_val, false_val in iif_exprs:
            total = 0.0
            for gr in grp_rows:
                cond_col = _extract_col(cond)
                v = _value_from_row(gr, cond_col)
                is_null_cond = "IS NULL" in cond.upper()
                if is_null_cond:
                    if v is None:
                        total += float(_value_from_row(gr, _extract_col(true_val)) or 0)
                    else:
                        total += float(_value_from_row(gr, _extract_col(false_val)) or 0)
                elif v:
                    total += float(_value_from_row(gr, _extract_col(true_val)) or 0)
                else:
                    total += float(_value_from_row(gr, _extract_col(false_val)) or 0)
            out[alias] = total

        if having_expr:
            hm = re.search(r"(?is)(\w+)\s*>=\s*\?", having_expr)
            if hm:
                alias_name = hm.group(1)
                h_val = params[-1] if params else 0
                if not (float(out.get(alias_name, 0) or 0) >= float(h_val or 0)):
                    continue
        result.append(out)

    order_by = _parse_order_by(sql)
    if order_by:
        for od, desc in reversed(order_by):
            result.sort(key=lambda r, c=od: float(r.get(c, 0) or 0), reverse=desc)
    if limit:
        result = result[:limit]

    return result


# ── MDBRepository ─────────────────────────────────────────────────────────

def expand_legacy_row_key_aliases(row: dict) -> None:
    from postgres_repo import expand_legacy_row_key_aliases as _pg_expand
    _pg_expand(row)


class MDBRepository:
    """Reads MDB file using mdbtools CLI, caches tables in memory."""

    def __init__(self, mdb_path: str):
        self.mdb_path = mdb_path
        self._cache: OrderedDict[str, list[dict]] = OrderedDict()
        self._cache_lock = threading.RLock()
        self._cache_max_size = 20

    def _load_table(self, table_name: str) -> list[dict]:
        with self._cache_lock:
            if table_name not in self._cache:
                self._cache[table_name] = _mdb_export_json(self.mdb_path, table_name)
            else:
                self._cache.move_to_end(table_name)  # LRU: mark as recently used
            self._evict_cache_if_needed()
            return self._cache[table_name]

    def _evict_cache_if_needed(self):
        while len(self._cache) > self._cache_max_size:
            self._cache.popitem(last=False)  # Remove oldest (first) item

    def _rows(self, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        pg_sql = str(sql)
        pg_sql = re.sub(r'"([^"]+)"', r'[\1]', pg_sql)
        pg_sql = re.sub(r"('(?:[^'\\]|\\.)*')|:\w+", lambda m: m.group(1) if m.group(1) else '?', pg_sql)
        param_list = list(params.values()) if params else []
        return self.execute_query(pg_sql, tuple(param_list))

    def execute_query(self, sql: str, params: tuple | None = None) -> list[dict]:
        sql = str(sql or "").strip()
        params = params or ()

        # Try SQLite first (fast path)
        sqlite_rows = _try_sqlite_query(sql, params)
        if sqlite_rows is not None:
            for r in sqlite_rows:
                expand_legacy_row_key_aliases(r)
            return sqlite_rows

        # Fall back to MDB in-memory path
        has_join = _has_join(sql)
        has_agg = _has_aggregate(sql)
        limit = _parse_limit(sql)
        distinct = _is_distinct(sql)
        columns = _parse_columns(sql)
        conditions = _parse_where_conditions(sql, params)
        order_by = _parse_order_by(sql)

        if has_join:
            rows = _execute_join_query(self.mdb_path, sql, params, self._cache)
        else:
            table_name = _parse_table_name(sql)
            if not table_name:
                return []
            rows = self._load_table(table_name)

        # Apply WHERE filter
        if conditions:
            rows = [r for r in rows if _apply_conditions(r, conditions, params)]

        # Handle aggregates
        if has_agg:
            rows = _execute_aggregate_query(rows, sql, params)
            for r in rows:
                expand_legacy_row_key_aliases(r)
            return rows

        # Project columns (do this BEFORE DISTINCT)
        if columns and columns[0][0] != "1":
            projected = []
            for r in rows:
                nr = {}
                for col_clean, col_alias in columns:
                    v = _value_from_row(r, col_clean)
                    nr[col_alias] = v
                projected.append(nr)
            for r in projected:
                expand_legacy_row_key_aliases(r)
            rows = projected
        else:
            for r in rows:
                expand_legacy_row_key_aliases(r)

        # DISTINCT (after projection so only selected columns are compared)
        if distinct:
            seen = set()
            unique = []
            for r in rows:
                key = tuple(str(v) for v in r.values())
                if key not in seen:
                    seen.add(key)
                    unique.append(r)
            rows = unique

        # ORDER BY
        if order_by:
            for col, desc in reversed(order_by):
                rows.sort(key=lambda r, c=col: str(_value_from_row(r, c) or ""), reverse=desc)

        # LIMIT
        if limit:
            rows = rows[:limit]

        return rows

    def execute_non_query(self, sql: str, params: tuple | None = None) -> int:
        logger.warning("Write operations not supported on MDB: %s", sql[:100])
        return 0

    def get_tables(self) -> list[str]:
        exe = os.path.join(_MDBTOOLS_BIN, "mdb-tables")
        if not os.path.isfile(exe):
            exe = "mdb-tables"
        try:
            proc = subprocess.run([exe, self.mdb_path], capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                tables = proc.stdout.strip().split()
                return [t for t in tables if t and not t.startswith("MSys")]
            return []
        except Exception:
            return []

    # ── Named query methods ──

    def learner_by_id_or_code(self, ident: str) -> dict | None:
        if not ident:
            return None
        if str(ident).isdigit():
            rows = self.execute_query(
                "SELECT TOP 1 [ID], [LearnerID], [FName], [SName], [Grade] FROM [Learner_Info] WHERE [ID] = ?",
                (int(ident),),
            )
            if rows:
                return rows[0]
        rows = self.execute_query(
            "SELECT TOP 1 [ID], [LearnerID], [FName], [SName], [Grade] FROM [Learner_Info] WHERE CSTR([LearnerID]) = ? OR CSTR([AccessionNo]) = ?",
            (str(ident), str(ident)),
        )
        return rows[0] if rows else None

    def learner_id_exists(self, learner_id: str) -> bool:
        if not str(learner_id or "").strip():
            return False
        rows = self.execute_query(
            "SELECT TOP 1 [ID] FROM [Learner_Info] WHERE CSTR([ID]) = ?",
            (str(learner_id),),
        )
        return bool(rows)

    def map_parent_phone_to_learner_keys(self, phone_value: str) -> list[str]:
        learner_ids: list[str] = []
        phone = str(phone_value)
        for col in ("Tel1", "Tel2", "Tel3", "SpouseCell"):
            rows = self.execute_query(
                f"SELECT DISTINCT CSTR(pc.[ChildId]) AS LearnerKey FROM [Parent_Info] pi INNER JOIN [Parent_Child] pc ON pc.[ParentId] = pi.[ParentID] WHERE CSTR(pi.[{col}]) = ?",
                (phone,),
            )
            learner_ids.extend(r.get("LearnerKey", "") or "" for r in rows)
            if learner_ids:
                return learner_ids
        for col in ("Tel1", "Tel2", "Tel3", "SpouseCell"):
            rows = self.execute_query(
                f"SELECT DISTINCT CSTR(pc.[Learnerid]) AS LearnerKey FROM [Parent_Info] pi INNER JOIN [Parent_Child] pc ON pc.[ParentId] = pi.[ParentID] WHERE CSTR(pi.[{col}]) = ?",
                (phone,),
            )
            learner_ids.extend(r.get("LearnerKey", "") or "" for r in rows)
            if learner_ids:
                return learner_ids
        return learner_ids

    def generic_phone_lookup(self, table: str, phone_col: str, learner_col: str, phone_value: str) -> list[str]:
        rows = self.execute_query(
            f"SELECT DISTINCT CSTR([{learner_col}]) AS LearnerKey FROM [{table}] WHERE CSTR([{phone_col}]) = ?",
            (str(phone_value),),
        )
        return [str(r.get("LearnerKey") or "").strip() for r in rows if r.get("LearnerKey")]

    def educator_by_edid(self, edid: str) -> dict | None:
        edid_upper = str(edid).upper()
        for col in ("EdID", "Key", "PersalNumber"):
            rows = self.execute_query(
                f"SELECT TOP 1 [EdID], [FName], [SName], [Actual], [Status], [RegisterClass], [Key], [PersalNumber] FROM [Educators] WHERE UCASE(CSTR([{col}])) = ?",
                (edid_upper,),
            )
            if rows:
                return rows[0]
        return None

    def staff_by_staffid(self, staff_id: str) -> dict | None:
        rows = self.execute_query(
            "SELECT TOP 1 [StaffID], [FName], [SName], [PersonnelCategory], [Status] FROM [StaffMembers] WHERE CSTR([StaffID]) = ?",
            (str(staff_id),),
        )
        return rows[0] if rows else None

    def execute_compat_query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        return self._rows(sql, params)

    def execute_compat_non_query(self, sql: str, params: dict[str, Any] | None = None) -> int:
        return self.execute_non_query(str(sql), tuple(params.values()) if params else ())

    def clear_cache(self) -> None:
        with self._cache_lock:
            self._cache.clear()

    def preload_tables(self, table_names: list[str]) -> None:
        for t in table_names:
            self._load_table(t)

    def preload_all(self) -> None:
        for t in self.get_tables():
            try:
                self._load_table(t)
            except Exception:
                logger.warning("Failed to preload table: %s", t)