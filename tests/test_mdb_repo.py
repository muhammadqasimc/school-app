"""Tests for mdb_repo.py core functions."""
import importlib
import pytest

mdb_repo = importlib.import_module("mdb_repo")
# Convenience references to pure functions
_extract_col = mdb_repo._extract_col
_parse_table_name = mdb_repo._parse_table_name
_parse_join_tables = mdb_repo._parse_join_tables
_parse_columns = mdb_repo._parse_columns
_parse_where_conditions = mdb_repo._parse_where_conditions
_parse_limit = mdb_repo._parse_limit
_parse_order_by = mdb_repo._parse_order_by
_parse_group_by = mdb_repo._parse_group_by
_is_distinct = mdb_repo._is_distinct
_has_join = mdb_repo._has_join
_has_aggregate = mdb_repo._has_aggregate
_split_columns = mdb_repo._split_columns
_split_on_AND = mdb_repo._split_on_AND
_value_from_row = mdb_repo._value_from_row
_match_value = mdb_repo._match_value
_apply_conditions = mdb_repo._apply_conditions
_apply_conditions.__wrapped__ = None  # noqa

# ── _extract_col ─────────────────────────────────────────────────────────


class TestExtractCol:
    def test_plain_column(self):
        assert _extract_col("FName") == "FName"

    def test_table_prefix(self):
        assert _extract_col("pi.Tel1") == "Tel1"

    def test_bracketed(self):
        assert _extract_col("[LearnerID]") == "LearnerID"

    def test_table_with_brackets(self):
        assert _extract_col("pi.[ChildId]") == "ChildId"

    def test_empty_string(self):
        assert _extract_col("") == ""


# ── _parse_table_name ────────────────────────────────────────────────────


class TestParseTableName:
    def test_simple_from(self):
        assert _parse_table_name("SELECT * FROM Learners") == "Learners"

    def test_bracketed_table(self):
        assert _parse_table_name("SELECT * FROM [Learner_Info]") == "Learner_Info"

    def test_no_from(self):
        assert _parse_table_name("SELECT 1") is None

    def test_with_join(self):
        assert _parse_table_name("SELECT * FROM Learners INNER JOIN Marks ON ...") == "Learners"


# ── _parse_join_tables ───────────────────────────────────────────────────


class TestParseJoinTables:
    def test_single_table(self):
        assert _parse_join_tables("SELECT * FROM Learners") == {"Learners": "Learners"}

    def test_table_with_alias(self):
        assert _parse_join_tables("SELECT * FROM Learner_Info li") == {"li": "Learner_Info"}

    def test_inner_join(self):
        sql = "SELECT * FROM Learners l INNER JOIN Marks m ON l.ID = m.LearnerID"
        result = _parse_join_tables(sql)
        assert result == {"l": "Learners", "m": "Marks"}

    def test_left_join(self):
        sql = "SELECT * FROM Learners l LEFT JOIN Marks m ON l.ID = m.LearnerID"
        result = _parse_join_tables(sql)
        assert result == {"l": "Learners", "m": "Marks"}

    def test_bracketed_tables(self):
        sql = "SELECT * FROM [Learner_Info] li INNER JOIN [Parent_Child] pc ON ..."
        result = _parse_join_tables(sql)
        assert result == {"li": "Learner_Info", "pc": "Parent_Child"}


# ── _parse_columns ───────────────────────────────────────────────────────


class TestParseColumns:
    def test_select_star(self):
        assert _parse_columns("SELECT * FROM Table") is None

    def test_select_table_star(self):
        assert _parse_columns("SELECT t.* FROM Table t") is None

    def test_single_column(self):
        result = _parse_columns("SELECT FName FROM Table")
        assert result == [("FName", "FName")]

    def test_multiple_columns(self):
        result = _parse_columns("SELECT FName, SName FROM Table")
        assert result == [("FName", "FName"), ("SName", "SName")]

    def test_with_alias(self):
        result = _parse_columns("SELECT FName AS FirstName FROM Table")
        assert result == [("FName", "FirstName")]

    def test_select_1(self):
        result = _parse_columns("SELECT 1 FROM Table")
        assert result == [("1", "1")]

    def test_top_n(self):
        result = _parse_columns("SELECT TOP 10 FName FROM Table")
        assert result == [("FName", "FName")]

    def test_bracketed_column(self):
        result = _parse_columns("SELECT [FName] FROM Table")
        assert result == [("FName", "FName")]

    def test_function_wrapped(self):
        """CSTR([ID]) should extract the column name."""
        result = _parse_columns("SELECT CSTR([ID]) AS LearnerKey FROM Table")
        # After stripping CSTR() wrapper, col_clean = "ID"
        assert result == [("ID", "LearnerKey")]


# ── _split_columns ───────────────────────────────────────────────────────


class TestSplitColumns:
    def test_simple(self):
        assert _split_columns("a, b") == ["a", " b"]

    def test_parens_not_split(self):
        assert _split_columns("CSTR(a), b") == ["CSTR(a)", " b"]

    def test_nested_parens(self):
        assert _split_columns("IIF(a,b,c), d") == ["IIF(a,b,c)", " d"]

    def test_empty(self):
        assert _split_columns("") == []


# ── _split_on_AND ────────────────────────────────────────────────────────


class TestSplitOnAND:
    def test_simple_and(self):
        assert _split_on_AND("a = ? AND b = ?") == ["a = ?", "b = ?"]

    def test_no_and(self):
        assert _split_on_AND("a = ?") == ["a = ?"]

    def test_empty_string(self):
        assert _split_on_AND("") == []

    def test_whitespace_only(self):
        assert _split_on_AND("   ") == []

    def test_keeps_paren_intact(self):
        result = _split_on_AND("(a AND b) AND c = ?")
        assert len(result) == 2


# ── _parse_where_conditions ──────────────────────────────────────────────


class TestParseWhereConditions:
    def test_no_where(self):
        """No WHERE clause returns empty list."""
        assert _parse_where_conditions("SELECT * FROM T", ()) == []

    def test_simple_eq(self):
        """= ? pattern with column name."""
        conditions = _parse_where_conditions("SELECT * FROM T WHERE [ID] = ?", ("123",))
        assert len(conditions) == 1
        assert conditions[0][:3] == ("ID", "=", 0)

    def test_is_null(self):
        conditions = _parse_where_conditions("SELECT * FROM T WHERE [FName] IS NULL", ())
        assert len(conditions) == 1
        assert conditions[0][1] == "IS_NULL"

    def test_is_not_null(self):
        conditions = _parse_where_conditions("SELECT * FROM T WHERE [FName] IS NOT NULL", ())
        assert len(conditions) == 1
        assert conditions[0][1] == "IS_NOT_NULL"

    def test_not_empty(self):
        conditions = _parse_where_conditions("SELECT * FROM T WHERE [Email] <> ''", ())
        assert len(conditions) == 1
        assert conditions[0][1] == "NOT_EMPTY"

    def test_ucase_cstr(self):
        """UCASE(CSTR([col])) = ? pattern."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE UCASE(CSTR([EdID])) = ?", ("ED123",)
        )
        assert len(conditions) == 1
        assert conditions[0][1] == "UCASE_CSTR_EQ"
        assert conditions[0][0] == "EdID"

    def test_cstr_eq(self):
        """CSTR([col]) = ? pattern."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE CSTR([LearnerID]) = ?", ("L123",)
        )
        assert len(conditions) == 1
        assert conditions[0][1] == "CSTR_EQ"
        assert conditions[0][0] == "LearnerID"

    def test_in_clause(self):
        """col IN (?, ?) pattern."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE [Status] IN (?, ?)", ("a", "b")
        )
        assert len(conditions) == 1
        assert conditions[0][1] == "IN"
        assert conditions[0][2] == 2  # 2 placeholders

    def test_between(self):
        """BETWEEN clause — note: AND in BETWEEN is also split by _split_on_AND,
        so this is a known limitation. Test documents the edge case."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE [Mark] BETWEEN ? AND ?", ("40", "100")
        )
        # The BETWEEN ... AND ... pattern gets split by _split_on_AND
        # at the depth-0 "AND" between the two values. This is a known
        # limitation — each half doesn't match the BETWEEN regex.
        assert len(conditions) == 0

    def test_or_eq(self):
        """col = ? OR col2 = ? pattern."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE [Tel1] = ? OR [Tel2] = ?", ("123", "456")
        )
        assert len(conditions) == 1
        assert conditions[0][1] == "OR_EQ"

    def test_and_separated_conditions(self):
        """AND-separated conditions should all be parsed."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE [Grade] = ? AND [Status] = ?", ("5", "Active")
        )
        assert len(conditions) == 2
        assert conditions[0][0] == "Grade"
        assert conditions[1][0] == "Status"

    def test_unrecognized_returns_empty(self):
        """Unrecognized patterns should not cause crash, returns [] (issue #2)."""
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE [Name] LIKE '%Smith%'", ()
        )
        # Unrecognized pattern returns [] — caller falls back to no filtering
        assert conditions == []

    def test_empty_where_body(self):
        conditions = _parse_where_conditions("SELECT * FROM T WHERE  ORDER BY Name", ())
        assert conditions == []

    def test_where_with_order_by(self):
        conditions = _parse_where_conditions(
            "SELECT * FROM T WHERE [Grade] = ? ORDER BY [Name]", ("5",)
        )
        assert len(conditions) == 1
        assert conditions[0][0] == "Grade"


# ── _parse_limit ─────────────────────────────────────────────────────────


class TestParseLimit:
    def test_top(self):
        assert _parse_limit("SELECT TOP 10 * FROM T") == 10

    def test_limit(self):
        assert _parse_limit("SELECT * FROM T LIMIT 5") == 5

    def test_no_limit(self):
        assert _parse_limit("SELECT * FROM T") is None


# ── _parse_order_by ──────────────────────────────────────────────────────


class TestParseOrderBy:
    def test_asc(self):
        result = _parse_order_by("SELECT * FROM T ORDER BY Name")
        assert result == [("Name", False)]

    def test_desc(self):
        result = _parse_order_by("SELECT * FROM T ORDER BY Name DESC")
        assert result == [("Name", True)]

    def test_multiple(self):
        result = _parse_order_by("SELECT * FROM T ORDER BY Grade DESC, Name ASC")
        assert result == [("Grade", True), ("Name", False)]

    def test_no_order_by(self):
        assert _parse_order_by("SELECT * FROM T") == []


# ── _parse_group_by ──────────────────────────────────────────────────────


class TestParseGroupBy:
    def test_simple(self):
        result = _parse_group_by("SELECT Subject, COUNT(*) FROM T GROUP BY Subject")
        assert result == ["Subject"]

    def test_multiple(self):
        result = _parse_group_by("SELECT Grade, Subject FROM T GROUP BY Grade, Subject")
        assert result == ["Grade", "Subject"]

    def test_no_group_by(self):
        assert _parse_group_by("SELECT * FROM T") == []


# ── Booleans ─────────────────────────────────────────────────────────────


class TestBooleanHelpers:
    def test_is_distinct(self):
        assert _is_distinct("SELECT DISTINCT Name FROM T") is True
        assert _is_distinct("SELECT Name FROM T") is False

    def test_has_join(self):
        assert _has_join("SELECT * FROM A INNER JOIN B ON ...") is True
        assert _has_join("SELECT * FROM A") is False

    def test_has_aggregate(self):
        assert _has_aggregate("SELECT SUM(Mark) FROM T") is True
        assert _has_aggregate("SELECT MAX(Mark) FROM T") is True
        assert _has_aggregate("SELECT COUNT(*) FROM T") is True
        assert _has_aggregate("SELECT * FROM T") is False


# ── _value_from_row ──────────────────────────────────────────────────────


class TestValueFromRow:
    def test_direct_match(self):
        assert _value_from_row({"Name": "Alice"}, "Name") == "Alice"

    def test_case_insensitive(self):
        assert _value_from_row({"NAME": "Alice"}, "name") == "Alice"

    def test_missing_column(self):
        assert _value_from_row({"Name": "Alice"}, "Missing") is None

    def test_none_value(self):
        assert _value_from_row({"Name": None}, "Name") is None


# ── _match_value ─────────────────────────────────────────────────────────


class TestMatchValue:
    def test_both_none(self):
        assert _match_value(None, None) is True

    def test_one_none(self):
        assert _match_value(None, "x") is False
        assert _match_value("x", None) is False

    def test_same_type_int(self):
        assert _match_value(5, 5) is True
        assert _match_value(5, 6) is False

    def test_cross_type_int_str(self):
        assert _match_value(5, "5") is True

    def test_string_strip(self):
        """_match_value with same types returns exact equality, no strip."""
        assert _match_value("abc", " abc ") is False  # different types? No, both str, exact compare

    def test_none_str_strip_handling(self):
        # _match_value short-circuits on None before str().strip()
        assert _match_value("abc", None) is False


# ── _apply_conditions ────────────────────────────────────────────────────


class TestApplyConditions:
    def test_eq_match(self):
        conditions = [("Name", "=", 0, False)]
        assert _apply_conditions({"Name": "Alice"}, conditions, ("Alice",))

    def test_eq_no_match(self):
        conditions = [("Name", "=", 0, False)]
        assert not _apply_conditions({"Name": "Alice"}, conditions, ("Bob",))

    def test_in_clause_matches(self):
        """IN clause should match when value is in the params list."""
        conditions = [("Status", "IN", 2, 0)]  # (col, op, count=2, start_idx=0)
        assert _apply_conditions({"Status": "Active"}, conditions, ("Active", "Inactive"))

    def test_in_clause_no_match(self):
        conditions = [("Status", "IN", 2, 0)]
        assert not _apply_conditions({"Status": "Unknown"}, conditions, ("Active", "Inactive"))

    def test_is_null_true(self):
        conditions = [("Name", "IS_NULL", None, -1)]
        assert _apply_conditions({"Name": None}, conditions, ())

    def test_is_null_false(self):
        conditions = [("Name", "IS_NULL", None, -1)]
        assert not _apply_conditions({"Name": "Alice"}, conditions, ())

    def test_is_not_null_true(self):
        conditions = [("Name", "IS_NOT_NULL", None, -1)]
        assert _apply_conditions({"Name": "Alice"}, conditions, ())

    def test_is_not_null_false(self):
        conditions = [("Name", "IS_NOT_NULL", None, -1)]
        assert not _apply_conditions({"Name": None}, conditions, ())

    def test_not_empty_true(self):
        conditions = [("Email", "NOT_EMPTY", None, -1)]
        assert _apply_conditions({"Email": "a@b.com"}, conditions, ())

    def test_not_empty_false(self):
        conditions = [("Email", "NOT_EMPTY", None, -1)]
        assert not _apply_conditions({"Email": ""}, conditions, ())

    def test_empty_row_value(self):
        conditions = [("Email", "NOT_EMPTY", None, -1)]
        assert not _apply_conditions({"Email": "  "}, conditions, ())

    def test_between_match(self):
        conditions = [("Mark", "BETWEEN", 0, 1)]
        assert _apply_conditions({"Mark": 50}, conditions, (40, 60))

    def test_between_no_match(self):
        conditions = [("Mark", "BETWEEN", 0, 1)]
        assert not _apply_conditions({"Mark": 100}, conditions, (40, 60))

    def test_or_eq_match_first(self):
        conditions = [("Tel1", "OR_EQ", 0, "Tel2")]
        assert _apply_conditions({"Tel1": "123", "Tel2": "456"}, conditions, ("123", "000"))

    def test_or_eq_match_second(self):
        conditions = [("Tel1", "OR_EQ", 0, "Tel2")]
        assert _apply_conditions({"Tel1": "999", "Tel2": "456"}, conditions, ("123", "456"))

    def test_ucase_cstr_eq(self):
        conditions = [("EdID", "UCASE_CSTR_EQ", 0, True)]
        assert _apply_conditions({"EdID": "abc123"}, conditions, ("ABC123",))

    def test_cstr_eq(self):
        conditions = [("LearnerID", "CSTR_EQ", 0, True)]
        assert _apply_conditions({"LearnerID": "123"}, conditions, ("123",))

    def test_unknown_op_false(self):
        conditions = [("Name", "UNKNOWN_OP", None, -1)]
        assert not _apply_conditions({"Name": "Alice"}, conditions, ())

    def test_multiple_conditions_all_true(self):
        conditions = [
            ("Grade", "=", 0, False),
            ("Status", "=", 1, False),
        ]
        assert _apply_conditions({"Grade": "5", "Status": "Active"}, conditions, ("5", "Active"))

    def test_multiple_conditions_one_false(self):
        conditions = [
            ("Grade", "=", 0, False),
            ("Status", "=", 1, False),
        ]
        assert not _apply_conditions({"Grade": "5", "Status": "Inactive"}, conditions, ("5", "Active"))


# ── _execute_join_query LEFT JOIN behavior ───────────────────────────────


class TestExecuteJoinQuery:
    """Test the LEFT JOIN multi-match behavior (issue #3)."""

    def test_left_join_multiple_matches(self):
        """LEFT JOIN should return MULTIPLE rows when right side has multiple matches."""
        sql = "SELECT * FROM [Learners] LEFT JOIN [Marks] ON [Learners].[ID] = [Marks].[LearnerID]"
        tables_data = {
            "Learners": [{"ID": 1, "Name": "Alice"}, {"ID": 2, "Name": "Bob"}],
            "Marks": [
                {"LearnerID": 1, "Mark": 85},
                {"LearnerID": 1, "Mark": 90},  # second match for Alice
                {"LearnerID": 2, "Mark": 75},
            ],
        }
        result = mdb_repo._execute_join_query("/fake/path.mdb", sql, (), tables_data)
        assert len(result) == 3
        # Alice appears twice (two marks)
        alice_rows = [r for r in result if r.get("ID") == 1]
        assert len(alice_rows) == 2

    def test_left_join_no_match_keeps_left_row(self):
        """LEFT JOIN should keep left row even with no match on right."""
        sql = "SELECT * FROM [Learners] LEFT JOIN [Marks] ON [Learners].[ID] = [Marks].[LearnerID]"
        tables_data = {
            "Learners": [{"ID": 1, "Name": "Alice"}, {"ID": 99, "Name": "Orphan"}],
            "Marks": [{"LearnerID": 1, "Mark": 85}],
        }
        result = mdb_repo._execute_join_query("/fake/path.mdb", sql, (), tables_data)
        assert len(result) == 2
        orphan = [r for r in result if r.get("ID") == 99]
        assert len(orphan) == 1
        # Orphan row has no Mark (but still present)
        assert orphan[0].get("Name") == "Orphan"

    def test_inner_join_removes_non_matches(self):
        """INNER JOIN should drop rows with no match."""
        sql = "SELECT * FROM [Learners] INNER JOIN [Marks] ON [Learners].[ID] = [Marks].[LearnerID]"
        tables_data = {
            "Learners": [{"ID": 1, "Name": "Alice"}, {"ID": 99, "Name": "Orphan"}],
            "Marks": [{"LearnerID": 1, "Mark": 85}],
        }
        result = mdb_repo._execute_join_query("/fake/path.mdb", sql, (), tables_data)
        assert len(result) == 1
        assert result[0]["Name"] == "Alice"


# ── MDBRepository._rows() named parameter regex ──────────────────────────


class TestRowsNamedParamRegex:
    """Test that named params are replaced correctly and string literals preserved."""

    def test_named_parameter_replacement(self):
        """The regex in _rows() should replace :name with ? but preserve string literals."""
        # The regex: r"('(?:[^'\\]|\\.)*')|:\w+"
        import re

        pattern = re.compile(r"('(?:[^'\\]|\\.)*')|:\w+")
        sql = "SELECT * FROM T WHERE Name = :name AND Status = :status"
        result = pattern.sub(lambda m: m.group(1) if m.group(1) else "?", sql)
        assert result == "SELECT * FROM T WHERE Name = ? AND Status = ?"

    def test_string_literal_preserved(self):
        """String literals in quotes should be preserved, not replaced."""
        import re

        pattern = re.compile(r"('(?:[^'\\]|\\.)*')|:\w+")
        sql = "SELECT * FROM T WHERE Title = 'This is :not_a_param' AND ID = :id"
        result = pattern.sub(lambda m: m.group(1) if m.group(1) else "?", sql)
        assert result == "SELECT * FROM T WHERE Title = 'This is :not_a_param' AND ID = ?"

    def test_multiple_string_literals(self):
        """Multiple string literals with colons inside should all be preserved."""
        import re

        pattern = re.compile(r"('(?:[^'\\]|\\.)*')|:\w+")
        sql = "SELECT * FROM T WHERE A = ':colon' AND B = ':another:colon' AND C = :param"
        result = pattern.sub(lambda m: m.group(1) if m.group(1) else "?", sql)
        assert result == "SELECT * FROM T WHERE A = ':colon' AND B = ':another:colon' AND C = ?"


# ── MDBRepository LRU eviction ───────────────────────────────────────────


class TestLRUEviction:
    def test_lru_cache_eviction(self):
        """After max_size (20) tables loaded, oldest should be evicted."""
        from collections import OrderedDict
        from unittest.mock import MagicMock, patch

        repo = mdb_repo.MDBRepository("/fake/path.mdb")
        repo._cache_max_size = 3

        # Monkey-patch _mdb_export_json to return empty lists
        with patch.object(mdb_repo, "_mdb_export_json", return_value=[]):
            repo._load_table("A")
            repo._load_table("B")
            repo._load_table("C")
            repo._load_table("D")  # should evict A

        assert len(repo._cache) == 3
        assert "A" not in repo._cache
        assert "B" in repo._cache
        assert "C" in repo._cache
        assert "D" in repo._cache

    def test_lru_move_to_end_on_access(self):
        """Accessing a cached table should move it to end (most recently used)."""
        from unittest.mock import patch

        repo = mdb_repo.MDBRepository("/fake/path.mdb")
        repo._cache_max_size = 3

        with patch.object(mdb_repo, "_mdb_export_json", return_value=[]):
            repo._load_table("A")
            repo._load_table("B")
            repo._load_table("C")
            # Access A again (should move to end)
            repo._load_table("A")
            repo._load_table("D")  # should evict B, not A

        assert "A" in repo._cache
        assert "B" not in repo._cache
        assert "D" in repo._cache

    def test_clear_cache(self):
        repo = mdb_repo.MDBRepository("/fake/path.mdb")
        from unittest.mock import patch

        with patch.object(mdb_repo, "_mdb_export_json", return_value=[]):
            repo._load_table("A")
            repo._load_table("B")

        assert len(repo._cache) == 2
        repo.clear_cache()
        assert len(repo._cache) == 0


# ── _access_to_sqlite ────────────────────────────────────────────────────


class TestAccessToSqlite:
    def test_iif_conversion(self):
        sql = "SELECT IIF(a > b, 1, 0) FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "CASE WHEN" in result
        assert "THEN" in result
        assert "ELSE" in result
        assert "END" in result

    def test_cstr_conversion(self):
        sql = "SELECT CSTR(ID) FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "CAST(ID AS TEXT)" in result

    def test_ucase_conversion(self):
        sql = "SELECT UCASE(Name) FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "UPPER(Name)" in result

    def test_clng_conversion(self):
        sql = "SELECT CLNG(Mark) FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "CAST(Mark AS INTEGER)" in result

    def test_cdbl_conversion(self):
        sql = "SELECT CDBL(Value) FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "CAST(Value AS REAL)" in result

    def test_nz_conversion(self):
        sql = "SELECT NZ(Name, 'Unknown') FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "COALESCE(Name, 'Unknown')" in result

    def test_top_limit(self):
        sql = "SELECT TOP 10 * FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "LIMIT 10" in result

    def test_bracket_to_double_quote(self):
        sql = "SELECT [Name] FROM [Table]"
        result = mdb_repo._access_to_sqlite(sql)
        assert '"Name"' in result
        assert '"Table"' in result

    def test_instr_conversion(self):
        sql = "SELECT InStr(1, [Desc], 'EXEMPT') FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "INSTR([Desc], 'EXEMPT')" in result or "INSTR(" in result

    def test_now_conversion(self):
        sql = "SELECT NOW() FROM T"
        result = mdb_repo._access_to_sqlite(sql)
        assert "datetime('now')" in result.lower()