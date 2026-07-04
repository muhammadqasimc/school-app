import re
from typing import Any

from sqlalchemy import text


_SAFE_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Longest first: split lowercase EMS-style keys (e.g. totalmark -> TotalMark) for PostgreSQL drivers
# that fold quoted column labels to all-lowercase.
_EMS_SPLIT_SUFFIXES = (
    "decision",
    "message",
    "language",
    "average",
    "selected",
    "comment",
    "status",
    "number",
    "schedule",
    "year",
    "date",
    "name",
    "mark",
    "time",
    "type",
    "code",
    "level",
    "term",
    "flag",
    "score",
    "sched",
    "auto",
    "desc",
    "key",
    "no",
    "id",
)

_PREFIX_OVERRIDES = {
    "obe": "OBE",
}


def _cap_prefix(prefix: str) -> str:
    p = str(prefix or "").strip().lower()
    if not p:
        return ""
    if p in _PREFIX_OVERRIDES:
        return _PREFIX_OVERRIDES[p]
    return p[0].upper() + p[1:]


def _ems_split_aliases(lowercase_flat: str) -> set[str]:
    kl = lowercase_flat.lower()
    out: set[str] = set()
    if not kl.isascii() or not kl.isalnum():
        return out
    for suf in _EMS_SPLIT_SUFFIXES:
        if not kl.endswith(suf) or len(kl) <= len(suf):
            continue
        prefix = kl[: len(kl) - len(suf)]
        if not prefix or not prefix.isalpha():
            continue
        pc = _cap_prefix(prefix)
        if suf == "id":
            out.add(pc + "ID")
            out.add(pc + "Id")
        elif suf == "no":
            out.add(pc + "No")
        elif suf == "mark":
            out.add(pc + "Mark")
        elif suf == "year":
            out.add(pc + "Year")
            out.add(pc + "year")
        else:
            tail = suf[0].upper() + suf[1:]
            out.add(pc + tail)
    return out


def legacy_key_variants(key: str) -> list[str]:
    """Aliases for one result column name so Access/EMS PascalCase lookups work on PostgreSQL rows."""
    k = str(key or "")
    out: set[str] = {k, k.upper(), k.lower()}
    kl = k.lower()
    special_aliases = {
        "transid": {"TransID"},
        "debacc": {"DebAcc"},
        "debitamount": {"DebitAmount"},
        "creditamt": {"CreditAmt"},
        "creditamount": {"CreditAmount"},
        "journalnumber": {"JournalNumber"},
        "learnerid": {"LearnerID"},
        "educatorid": {"EducatorID"},
        "parentid": {"ParentID"},
        "childid": {"ChildID"},
        "accessionno": {"AccessionNo"},
        "entrydate": {"EntryDate"},
        "fname": {"FName"},
        "sname": {"SName"},
        "totalmark": {"TotalMark"},
        "id": {"ID"},
    }
    out.update(special_aliases.get(kl, set()))
    if "_" in k:
        parts = [p for p in k.split("_") if p]
        pascal = "".join((part[:1].upper() + part[1:].lower()) if part else "" for part in parts)
    else:
        pascal = k[:1].upper() + k[1:] if k else k
    if pascal:
        out.add(pascal)
        pl = pascal.lower()
        if pl.endswith("id") and len(pascal) >= 2:
            stem = pascal[:-2]
            out.add(stem + "ID")
            out.add(stem + "Id")
        if pl == "fname":
            out.add("FName")
        if pl == "sname":
            out.add("SName")
    if kl.isascii():
        out.update(_ems_split_aliases(kl))
    return [x for x in out if x]


def expand_legacy_row_key_aliases(row: dict) -> None:
    """Add missing EMS-style keys to a result row (mutates dict). Safe for all mdb_conn / pg_repo reads."""
    if not row:
        return
    for k, v in list(row.items()):
        if not isinstance(k, str):
            continue
        for alias in legacy_key_variants(k):
            if alias not in row:
                row[alias] = v


def _safe_ident(name: str) -> str:
    raw = str(name or "").strip()
    if not _SAFE_IDENT_RE.fullmatch(raw):
        raise ValueError(f"Unsafe identifier: {raw!r}")
    return f'"{raw}"'


class PostgresRepository:
    def __init__(self, db):
        self.db = db

    def _rows(self, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        result = self.db.session.execute(text(sql), params or {}).mappings().all()
        out = []
        for r in result:
            row = dict(r)
            expand_legacy_row_key_aliases(row)
            out.append(row)
        return out

    def execute_compat_query(self, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        """Execute translated legacy (Access-style) SELECT statements on PostgreSQL."""
        return self._rows(sql, params)

    def execute_compat_non_query(self, sql: str, params: dict[str, Any] | None = None) -> int:
        """Execute translated legacy INSERT/UPDATE/DELETE statements on PostgreSQL."""
        result = self.db.session.execute(text(sql), params or {})
        self.db.session.commit()
        return int(result.rowcount or 0)

    def learner_by_id_or_code(self, ident: str) -> dict | None:
        if not ident:
            return None
        if str(ident).isdigit():
            rows = self._rows(
                """
                SELECT "ID", "LearnerID", "FName", "SName", "Grade"
                FROM "Learner_Info"
                WHERE "ID" = :id_val
                LIMIT 1
                """,
                {"id_val": int(ident)},
            )
            if rows:
                return rows[0]
        rows = self._rows(
            """
            SELECT "ID", "LearnerID", "FName", "SName", "Grade"
            FROM "Learner_Info"
            WHERE CAST("LearnerID" AS TEXT) = :ident OR CAST("AccessionNo" AS TEXT) = :ident
            LIMIT 1
            """,
            {"ident": str(ident)},
        )
        return rows[0] if rows else None

    def learner_id_exists(self, learner_id: str) -> bool:
        if not str(learner_id or "").strip():
            return False
        rows = self._rows(
            """
            SELECT "ID"
            FROM "Learner_Info"
            WHERE CAST("ID" AS TEXT) = :ident
            LIMIT 1
            """,
            {"ident": str(learner_id)},
        )
        return bool(rows)

    def map_parent_phone_to_learner_keys(self, phone_value: str) -> list[str]:
        learner_ids: list[str] = []
        for col in ("Tel1", "Tel2", "Tel3", "SpouseCell"):
            col_sql = _safe_ident(col)
            rows = self._rows(
                f"""
                SELECT DISTINCT CAST(pc."ChildId" AS TEXT) AS "LearnerKey"
                FROM "Parent_Info" pi
                INNER JOIN "Parent_Child" pc ON pc."ParentId" = pi."ParentID"
                WHERE CAST(pi.{col_sql} AS TEXT) = :phone
                """,
                {"phone": str(phone_value)},
            )
            learner_ids.extend([str(r.get("LearnerKey") or "").strip() for r in rows if str(r.get("LearnerKey") or "").strip()])
            if learner_ids:
                return learner_ids

        for col in ("Tel1", "Tel2", "Tel3", "SpouseCell"):
            col_sql = _safe_ident(col)
            rows = self._rows(
                f"""
                SELECT DISTINCT CAST(pc."Learnerid" AS TEXT) AS "LearnerKey"
                FROM "Parent_Info" pi
                INNER JOIN "Parent_Child" pc ON pc."ParentId" = pi."ParentID"
                WHERE CAST(pi.{col_sql} AS TEXT) = :phone
                """,
                {"phone": str(phone_value)},
            )
            learner_ids.extend([str(r.get("LearnerKey") or "").strip() for r in rows if str(r.get("LearnerKey") or "").strip()])
            if learner_ids:
                return learner_ids
        return learner_ids

    def generic_phone_lookup(self, table: str, phone_col: str, learner_col: str, phone_value: str) -> list[str]:
        table_sql = _safe_ident(table)
        phone_sql = _safe_ident(phone_col)
        learner_sql = _safe_ident(learner_col)
        rows = self._rows(
            f"""
            SELECT DISTINCT CAST({learner_sql} AS TEXT) AS "LearnerKey"
            FROM {table_sql}
            WHERE CAST({phone_sql} AS TEXT) = :phone
            """,
            {"phone": str(phone_value)},
        )
        return [str(r.get("LearnerKey") or "").strip() for r in rows if str(r.get("LearnerKey") or "").strip()]

    def educator_by_edid(self, edid: str) -> dict | None:
        rows = self._rows(
            """
            SELECT "EdID", "FName", "SName", "Actual", "Status", "RegisterClass"
            FROM "Educators"
            WHERE UPPER(CAST("EdID" AS TEXT)) = :edid
            LIMIT 1
            """,
            {"edid": str(edid).upper()},
        )
        return rows[0] if rows else None

    def staff_by_staffid(self, staff_id: str) -> dict | None:
        rows = self._rows(
            """
            SELECT "StaffID", "FName", "SName", "PersonnelCategory", "Status"
            FROM "StaffMembers"
            WHERE CAST("StaffID" AS TEXT) = :sid
            LIMIT 1
            """,
            {"sid": str(staff_id)},
        )
        return rows[0] if rows else None
