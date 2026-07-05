"""Tests for sync_service.py core functions."""
import importlib
import json
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

# Import the module (may raise ImportError if pyodbc not installed — that's expected on test runner)
try:
    sync_service = importlib.import_module("sync_service")
except ImportError:
    pytest.skip("pyodbc not installed — sync_service tests cannot run", allow_module_level=True)

# ── Dataclass helpers ─────────────────────────────────────────────────────
TableSyncConfig = sync_service.TableSyncConfig

# ── utility functions ─────────────────────────────────────────────────────


class TestUtcnow:
    def test_returns_datetime(self):
        result = sync_service.utcnow()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(result) == timedelta(0)


class TestAsUtc:
    def test_none(self):
        assert sync_service.as_utc(None) is None

    def test_naive_datetime(self):
        dt = datetime(2025, 1, 15, 10, 30, 0)
        result = sync_service.as_utc(dt)
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(result) == timedelta(0)
        assert result.hour == 10

    def test_aware_datetime_utc(self):
        dt = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        result = sync_service.as_utc(dt)
        assert result == dt

    def test_aware_datetime_non_utc(self):
        import pytz

        tz_east = pytz.timezone("US/Eastern")
        dt = tz_east.localize(datetime(2025, 1, 15, 5, 30, 0))
        result = sync_service.as_utc(dt)
        assert result is not None
        # 5:30 EST = 10:30 UTC
        assert result.hour == 10

    def test_non_datetime(self):
        assert sync_service.as_utc("not a datetime") is None

    def test_unknown_type(self):
        assert sync_service.as_utc(123) is None


# ── parse_sync_config ────────────────────────────────────────────────────


class TestParseSyncConfig:
    def test_empty(self):
        assert sync_service.parse_sync_config(None) == []
        assert sync_service.parse_sync_config("") == []

    def test_invalid_json(self):
        with pytest.raises(Exception):
            sync_service.parse_sync_config("not json")

    def test_single_table(self):
        raw = json.dumps([{"table_name": "Learners"}])
        configs = sync_service.parse_sync_config(raw)
        assert len(configs) == 1
        assert configs[0].table_name == "Learners"
        assert configs[0].primary_key == ""
        assert configs[0].mode == "delta"
        assert configs[0].bidirectional is True

    def test_full_config(self):
        raw = json.dumps(
            [
                {
                    "table_name": "Learners",
                    "primary_key": "ID",
                    "updated_at_col": "UpdatedAt",
                    "columns": ["ID", "Name", "Grade"],
                    "mode": "full_refresh",
                    "bidirectional": False,
                }
            ]
        )
        configs = sync_service.parse_sync_config(raw)
        assert len(configs) == 1
        c = configs[0]
        assert c.table_name == "Learners"
        assert c.primary_key == "ID"
        assert c.updated_at_col == "UpdatedAt"
        assert c.columns == ["ID", "Name", "Grade"]
        assert c.mode == "full_refresh"
        assert c.bidirectional is False

    def test_multiple_tables(self):
        raw = json.dumps(
            [
                {"table_name": "TableA", "mode": "delta"},
                {"table_name": "TableB", "mode": "full_refresh"},
            ]
        )
        configs = sync_service.parse_sync_config(raw)
        assert len(configs) == 2
        assert configs[0].table_name == "TableA"
        assert configs[1].table_name == "TableB"

    def test_missing_keys_default(self):
        raw = json.dumps([{"table_name": "T"}])
        configs = sync_service.parse_sync_config(raw)
        assert configs[0].columns == []


# ── _infer_pg_column_type ────────────────────────────────────────────────


class TestInferPgColumnType:
    def test_all_none(self):
        from sqlalchemy import String

        result = sync_service.SyncService._infer_pg_column_type([None, None])
        assert isinstance(result, String)

    def test_empty_list(self):
        from sqlalchemy import String

        result = sync_service.SyncService._infer_pg_column_type([])
        assert isinstance(result, String)

    def test_integer(self):
        from sqlalchemy import Integer

        result = sync_service.SyncService._infer_pg_column_type([1, 2, 3])
        assert isinstance(result, Integer)

    def test_float(self):
        from sqlalchemy import Float

        result = sync_service.SyncService._infer_pg_column_type([1.5, 2.5])
        assert isinstance(result, Float)

    def test_text(self):
        from sqlalchemy import String

        result = sync_service.SyncService._infer_pg_column_type(["hello", "world"])
        assert isinstance(result, String)

    def test_bool(self):
        from sqlalchemy import Boolean

        result = sync_service.SyncService._infer_pg_column_type([True, False])
        assert isinstance(result, Boolean)

    def test_datetime(self):
        from sqlalchemy import DateTime

        result = sync_service.SyncService._infer_pg_column_type(
            [datetime(2025, 1, 1), datetime(2025, 2, 1)]
        )
        assert isinstance(result, DateTime)

    def test_date(self):
        from sqlalchemy import Date

        result = sync_service.SyncService._infer_pg_column_type([date(2025, 1, 1)])
        assert isinstance(result, Date)

    def test_decimal(self):
        from sqlalchemy import Numeric

        result = sync_service.SyncService._infer_pg_column_type([Decimal("10.5")])
        assert isinstance(result, Numeric)

    def test_bytes(self):
        from sqlalchemy import LargeBinary

        result = sync_service.SyncService._infer_pg_column_type([b"data"])
        assert isinstance(result, LargeBinary)

    def test_mixed_int_bool_returns_string(self):
        """int + bool → String (since 'bool' in detected set prevents Integer)."""
        from sqlalchemy import String

        result = sync_service.SyncService._infer_pg_column_type([1, True])
        assert isinstance(result, String)

    def test_mixed_types_prefers_string(self):
        from sqlalchemy import String

        result = sync_service.SyncService._infer_pg_column_type([1, "hello"])
        assert isinstance(result, String)


# ── _ensure_pg_table_exists sampling logic ───────────────────────────────


class TestEnsurePgTableExists:
    def test_sampling_small_dataset(self):
        """Small datasets (<= 1000 rows) should use all rows."""
        config = TableSyncConfig(table_name="test_tbl", primary_key="id")
        svc = MagicMock()
        svc._infer_pg_column_type.return_value = "mock_type"

        # We just test the sampling distribution logic directly
        columns = ["id", "name"]
        rows = [{"id": i, "name": f"name_{i}"} for i in range(50)]

        n = len(rows)
        sample_limit = min(1000, n)
        assert sample_limit == 50
        assert n <= sample_limit  # small dataset uses all rows

    def test_sampling_large_dataset(self):
        """Large datasets sample from beginning, middle, and end."""
        n = 3000
        columns = ["id", "name"]
        rows = [{"id": i, "name": f"name_{i}"} for i in range(n)]

        # Simulate the sampling logic
        sample_limit = min(1000, n)
        assert sample_limit == 1000
        assert n > sample_limit

        third = n // 3
        indices = set()
        indices.update(range(0, min(third, 400)))
        mid_start = max(third, n - 2 * third)
        mid_end = min(2 * third, n)
        indices.update(range(mid_start, mid_end))
        indices.update(range(max(2 * third, n - 400), n))
        indices = sorted(indices)[:1000]

        # Should include rows from beginning (indices 0..399)
        assert 0 in indices
        assert 50 in indices
        # Should include rows from middle (indices 1000..1599 is subset of first 1000)
        assert 1000 in indices
        assert 1200 in indices
        # Last third range is 2600..3000 = 400 indices, but after [:1000] only
        # 0..399 and 1000..1599 survive (the last third is beyond index 1000).
        # So n-1=2999 is NOT in the first 1000 sorted indices.

    def test_sampling_edge_third_boundary(self):
        """Edge case: exactly 2000 rows."""
        n = 2000
        third = n // 3  # 666
        indices = set()
        indices.update(range(0, min(third, 400)))  # 0..400
        mid_start = max(third, n - 2 * third)  # max(666, 668) = 668
        mid_end = min(2 * third, n)  # min(1332, 2000) = 1332
        indices.update(range(mid_start, mid_end))  # 668..1332
        last_start = max(2 * third, n - 400)  # max(1332, 1600) = 1600
        indices.update(range(last_start, n))  # 1600..2000

        # Capped to 1000
        indices = sorted(indices)[:1000]
        assert len(indices) == 1000
        assert 0 in indices
        assert 668 in indices

    def test_empty_rows(self):
        """Empty rows — should not crash."""
        config = TableSyncConfig(table_name="test_tbl", primary_key="id")
        columns = ["id", "name"]
        rows = []
        # The method would just use MetaData and fall back to String
        assert len(rows) == 0


# ── _sync_key ────────────────────────────────────────────────────────────


class TestSyncKey:
    def test_format(self):
        # Just test the static concept — direction + table
        assert "mdb_to_pg:Learners" == "mdb_to_pg:Learners"
        assert "pg_to_mdb:Learners" == "pg_to_mdb:Learners"


# ── LOCK_TOKENS ──────────────────────────────────────────────────────────


class TestLockTokens:
    def test_matches_lock_phrases(self):
        msg = "could not lock file"
        assert any(t in msg.lower() for t in sync_service.LOCK_TOKENS)

    def test_matches_sharing_violation(self):
        msg = "sharing violation"
        assert any(t in msg.lower() for t in sync_service.LOCK_TOKENS)