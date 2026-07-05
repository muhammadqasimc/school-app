"""Tests for management_report_handlers.py."""
import importlib
import pytest

mrh = importlib.import_module("management_report_handlers")


# ── _cached_pct ──────────────────────────────────────────────────────────


class TestCachedPct:
    def test_basic_percentage(self):
        """50 out of 100 should give 50.0%."""
        assert mrh._cached_pct(50.0, 100.0) == 50.0

    def test_rounding(self):
        """1 out of 3 should give 33.33 (rounded to 2 decimal places)."""
        assert mrh._cached_pct(1.0, 3.0) == 33.33

    def test_zero_total(self):
        """Division by zero should return 0.0."""
        assert mrh._cached_pct(50.0, 0.0) == 0.0

    def test_negative_total(self):
        """Negative total should return 0.0."""
        assert mrh._cached_pct(50.0, -10.0) == 0.0

    def test_float_mark_int_total(self):
        """Mixed types should work."""
        assert mrh._cached_pct(50.0, 200) == 25.0

    def test_hundred_percent(self):
        assert mrh._cached_pct(100.0, 100.0) == 100.0

    def test_zero_mark(self):
        assert mrh._cached_pct(0.0, 100.0) == 0.0

    def test_lru_caching_same_inputs(self):
        """Same inputs should return same cached result."""
        result1 = mrh._cached_pct(75.0, 100.0)
        result2 = mrh._cached_pct(75.0, 100.0)
        assert result1 == result2 == 75.0

    def test_rounding_edge(self):
        """Test ROUND_HALF_UP behavior: 2.5 rounds to 2.5, not 2.0."""
        # 5 out of 200 = 2.5 — decimal quantize with ROUND_HALF_UP
        result = mrh._cached_pct(5.0, 200.0)
        assert result == 2.5


# ── _apply_pagination ────────────────────────────────────────────────────


class TestApplyPagination:
    def test_empty_list(self):
        result = mrh._apply_pagination([], page=1, per_page=100)
        assert result["items"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["totalPages"] == 1

    def test_single_page(self):
        items = ["a", "b", "c"]
        result = mrh._apply_pagination(items, page=1, per_page=100)
        assert result["items"] == items
        assert result["total"] == 3
        assert result["perPage"] == 100
        assert result["totalPages"] == 1

    def test_multiple_pages_page_1(self):
        items = list(range(25))
        result = mrh._apply_pagination(items, page=1, per_page=10)
        assert result["items"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert result["page"] == 1
        assert result["totalPages"] == 3

    def test_multiple_pages_page_2(self):
        items = list(range(25))
        result = mrh._apply_pagination(items, page=2, per_page=10)
        assert result["items"] == [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        assert result["page"] == 2

    def test_multiple_pages_last_page(self):
        items = list(range(25))
        result = mrh._apply_pagination(items, page=3, per_page=10)
        assert result["items"] == [20, 21, 22, 23, 24]
        assert result["page"] == 3

    def test_page_overflow_clamped(self):
        """Requesting a page beyond totalPages should clamp to last page."""
        items = list(range(5))
        result = mrh._apply_pagination(items, page=99, per_page=10)
        assert result["items"] == items
        assert result["page"] == 1  # clamped to 1

    def test_page_zero_clamped_to_1(self):
        items = list(range(5))
        result = mrh._apply_pagination(items, page=0, per_page=10)
        assert result["page"] == 1

    def test_negative_page(self):
        items = list(range(5))
        result = mrh._apply_pagination(items, page=-5, per_page=10)
        assert result["page"] == 1

    def test_negative_per_page(self):
        items = list(range(20))
        result = mrh._apply_pagination(items, page=1, per_page=-5)
        assert result["perPage"] == 1  # max(1, ...)

    def test_per_page_over_500_clamped(self):
        items = list(range(600))
        result = mrh._apply_pagination(items, page=1, per_page=1000)
        assert result["perPage"] == 500

    def test_per_page_0_clamped_to_1(self):
        items = list(range(5))
        result = mrh._apply_pagination(items, page=1, per_page=0)
        assert result["perPage"] == 1

    def test_exact_fit(self):
        items = list(range(20))
        result = mrh._apply_pagination(items, page=1, per_page=5)
        assert result["totalPages"] == 4
        assert len(result["items"]) == 5

    def test_correct_metadata(self):
        items = list(range(7))
        result = mrh._apply_pagination(items, page=2, per_page=3)
        assert result["total"] == 7
        assert result["page"] == 2
        assert result["perPage"] == 3
        assert result["totalPages"] == 3
        assert result["items"] == [3, 4, 5]

    def test_non_int_page(self):
        """String page should be coerced to int."""
        items = list(range(10))
        result = mrh._apply_pagination(items, page="2", per_page=5)
        assert result["page"] == 2
        assert result["items"] == [5, 6, 7, 8, 9]

    def test_non_int_per_page(self):
        items = list(range(10))
        result = mrh._apply_pagination(items, page=1, per_page="3")
        assert result["perPage"] == 3


# ── mr_row_pct ───────────────────────────────────────────────────────────


class TestMrRowPct:
    def test_normal_row(self):
        row = {"Mark": 75, "TotalMark": 100}
        assert mrh.mr_row_pct(row) == 75.0

    def test_zero_total(self):
        row = {"Mark": 50, "TotalMark": 0}
        assert mrh.mr_row_pct(row) is None

    def test_missing_mark(self):
        row = {"TotalMark": 100}
        assert mrh.mr_row_pct(row) == 0.0

    def test_none_mark(self):
        row = {"Mark": None, "TotalMark": 100}
        assert mrh.mr_row_pct(row) == 0.0

    def test_type_error(self):
        row = {"Mark": "invalid", "TotalMark": 100}
        assert mrh.mr_row_pct(row) is None


# ── mr_level_band ────────────────────────────────────────────────────────


class TestMrLevelBand:
    def test_l7_80_plus(self):
        assert mrh.mr_level_band(85) == 7
        assert mrh.mr_level_band(100) == 7
        assert mrh.mr_level_band(80) == 7

    def test_l6_70_79(self):
        assert mrh.mr_level_band(70) == 6
        assert mrh.mr_level_band(75) == 6
        assert mrh.mr_level_band(79) == 6

    def test_l5_60_69(self):
        assert mrh.mr_level_band(60) == 5
        assert mrh.mr_level_band(65) == 5

    def test_l4_50_59(self):
        assert mrh.mr_level_band(50) == 4
        assert mrh.mr_level_band(55) == 4

    def test_l3_40_49(self):
        assert mrh.mr_level_band(40) == 3
        assert mrh.mr_level_band(45) == 3

    def test_l2_30_39(self):
        assert mrh.mr_level_band(30) == 2
        assert mrh.mr_level_band(35) == 2

    def test_l1_below_30(self):
        assert mrh.mr_level_band(0) == 1
        assert mrh.mr_level_band(15) == 1
        assert mrh.mr_level_band(29) == 1


# ── mr_subject_aggregates ────────────────────────────────────────────────


class TestMrSubjectAggregates:
    def test_single_subject(self):
        rows = [
            {"Subject": "Math", "Mark": 50, "TotalMark": 100},
            {"Subject": "Math", "Mark": 80, "TotalMark": 100},
        ]
        result = mrh.mr_subject_aggregates(rows)
        assert len(result) == 1
        assert result[0]["label"] == "Math"
        assert result[0]["value"] == 65.0  # (50+80)/2
        assert result[0]["passRate"] == 100.0  # both >= default threshold (40)

    def test_multiple_subjects(self):
        rows = [
            {"Subject": "Math", "Mark": 50, "TotalMark": 100},
            {"Subject": "English", "Mark": 70, "TotalMark": 100},
        ]
        result = mrh.mr_subject_aggregates(rows)
        assert len(result) == 2
        subjects = {r["label"]: r for r in result}
        assert subjects["Math"]["value"] == 50.0
        assert subjects["English"]["value"] == 70.0

    def test_empty_rows(self):
        assert mrh.mr_subject_aggregates([]) == []

    def test_none_rows(self):
        assert mrh.mr_subject_aggregates(None) == []

    def test_missing_subject(self):
        rows = [{"Mark": 50, "TotalMark": 100}]
        assert mrh.mr_subject_aggregates(rows) == []


# ── mr_kpi_core ──────────────────────────────────────────────────────────


class TestMrKpiCore:
    def test_basic(self):
        rows = [
            {"LearnerID": "1", "Subject": "Math", "Mark": 50, "TotalMark": 100},
            {"LearnerID": "1", "Subject": "Eng", "Mark": 70, "TotalMark": 100},
            {"LearnerID": "2", "Subject": "Math", "Mark": 30, "TotalMark": 100},
        ]
        result = mrh.mr_kpi_core(rows)
        assert result["learners"] == 2
        assert result["records"] == 3
        assert result["avgPercent"] is not None
        assert result["passRate"] is not None

    def test_empty(self):
        result = mrh.mr_kpi_core([])
        assert result["learners"] == 0
        assert result["records"] == 0

    def test_none(self):
        result = mrh.mr_kpi_core(None)
        assert result["learners"] == 0
        assert result["records"] == 0


# ── mr_grade_distribution_from_promotion ─────────────────────────────────


class TestMrGradeDistribution:
    def test_basic(self):
        grade_map = {"1": "1", "2": "2", "3": "1"}
        result = mrh.mr_grade_distribution_from_promotion(grade_map)
        assert len(result) == 2
        g1 = [r for r in result if "Grade 1" in r["label"]]
        g2 = [r for r in result if "Grade 2" in r["label"]]
        assert g1[0]["value"] == 2
        assert g2[0]["value"] == 1

    def test_empty(self):
        assert mrh.mr_grade_distribution_from_promotion({}) == []


# ── _normalize_subject_label ─────────────────────────────────────────────


class TestNormalizeSubjectLabel:
    def test_strips_grade_suffix(self):
        assert mrh._normalize_subject_label("Math (Gr 5)") == "Math"

    def test_no_suffix(self):
        assert mrh._normalize_subject_label("English") == "English"

    def test_empty(self):
        assert mrh._normalize_subject_label("") == ""

    def test_case_insensitive(self):
        assert mrh._normalize_subject_label("Science (GR 10)") == "Science"

    def test_whitespace_preserved_otherwise(self):
        result = mrh._normalize_subject_label("  Math  ")
        assert result == "Math"


# ── mr_year_over_year_grade_averages ─────────────────────────────────────


class TestYoYGradeAverages:
    def test_current_year_only(self):
        data = {("2025", "5"): [60.0, 70.0]}
        result = mrh.mr_year_over_year_grade_averages(
            data, current_year="2025", grade_label="5", term_label="Term 1"
        )
        assert result["grade"] == "5"
        assert result["term1"] == 65.0
        assert result["py"] is None  # no previous year data

    def test_with_previous_year(self):
        data = {
            ("2025", "5"): [60.0, 80.0],
            ("2024", "5"): [50.0, 70.0],
        }
        result = mrh.mr_year_over_year_grade_averages(
            data, current_year="2025", grade_label="5", term_label="Term 1"
        )
        assert result["term1"] == 70.0
        assert result["py"] == 60.0
        assert result["diffPy"] == 10.0


# ── mr_schoolwide_year_averages ──────────────────────────────────────────


class TestSchoolwideYearAverages:
    def test_current_year_only(self):
        data = {"2025": [60.0, 70.0]}
        result = mrh.mr_schoolwide_year_averages(data, current_year="2025", term_label="Term 1")
        assert result["grade"] == "All"
        assert result["term1"] == 65.0

    def test_with_previous(self):
        data = {"2025": [80.0], "2024": [70.0]}
        result = mrh.mr_schoolwide_year_averages(data, current_year="2025", term_label="Term 1")
        assert result["term1"] == 80.0
        assert result["py"] == 70.0
        assert result["diffPy"] == 10.0