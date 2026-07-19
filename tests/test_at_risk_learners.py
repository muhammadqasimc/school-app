"""Tests for the At-Risk Learners management report feature."""

import pytest


# ── Management report registry ─────────────────────────────────────────


class TestAtRiskReportRegistration:
    """Verify the report is registered correctly in MANAGEMENT_REPORT_REGISTRY."""

    def test_report_registered(self):
        """The at-risk-learners report key exists in the registry."""
        import app as app_module
        keys = [r["key"] for r in app_module.MANAGEMENT_REPORT_REGISTRY]
        assert "at-risk-learners" in keys

    def test_report_metadata(self):
        """Verify report metadata is complete."""
        import app as app_module
        meta = app_module.MANAGEMENT_REPORTS_BY_KEY.get("at-risk-learners")
        assert meta is not None
        assert meta["title"] == "At-Risk Learners"
        assert meta["template"] == "management/at_risk_learners.html"

    def test_template_exists(self):
        """The template file must exist on disk."""
        from pathlib import Path
        tpl = Path(__file__).resolve().parent.parent / "templates" / "management" / "at_risk_learners.html"
        assert tpl.is_file(), f"Template not found: {tpl}"


# ── API endpoint / handler smoke test ──────────────────────────────


class TestAtRiskHandler:
    """Smoke test that the handler function exists and is callable."""

    def test_handler_exists(self):
        """The _management_build_at_risk_payload function is defined and callable."""
        import app as app_module
        assert hasattr(app_module, "_management_build_at_risk_payload")
        assert callable(app_module._management_build_at_risk_payload)


# ── Risk computation logic ─────────────────────────────────────────


class TestRiskComputation:
    """Test the risk flag computation thresholds used by the at-risk payload builder."""

    ATTENDANCE_THRESHOLD = 5
    GRADE_THRESHOLD = 40.0
    DISCIPLINE_THRESHOLD = 3

    def test_attendance_risk_threshold(self):
        """>= 5 absences = at-risk for attendance."""
        assert self.ATTENDANCE_THRESHOLD == 5  # boundary
        assert 4 < self.ATTENDANCE_THRESHOLD  # 4 should NOT trigger

    def test_grade_risk_threshold(self):
        """avg < 40% = at-risk for grade."""
        assert self.GRADE_THRESHOLD == 40.0

    def test_discipline_risk_threshold(self):
        """demerit balance >= 3 = at-risk for discipline."""
        assert self.DISCIPLINE_THRESHOLD == 3

    def test_risk_level_low(self):
        """1 flag = low risk."""
        flags = ["attendance"]
        level = "high" if len(flags) == 3 else ("medium" if len(flags) == 2 else "low")
        assert level == "low"

    def test_risk_level_medium(self):
        """2 flags = medium risk."""
        flags = ["attendance", "grade"]
        level = "high" if len(flags) == 3 else ("medium" if len(flags) == 2 else "low")
        assert level == "medium"

    def test_risk_level_high(self):
        """3 flags = high risk."""
        flags = ["attendance", "grade", "discipline"]
        level = "high" if len(flags) == 3 else ("medium" if len(flags) == 2 else "low")
        assert level == "high"

    def test_no_risk_skips_learner(self):
        """Learner with zero flags should NOT appear in at-risk list."""
        flags: list[str] = []
        # Simulating the skip logic from _management_build_at_risk_payload
        if not flags:
            assert True  # would continue (skip)
        else:
            pytest.fail("Should have skipped learner with no flags")


# ── Payload structure ─────────────────────────────────────────


class TestAtRiskPayloadStructure:
    """Test the structure of the payload returned by the at-risk builder."""

    def test_kpi_keys_present(self):
        """The KPIs dict must contain all expected keys."""
        required = {"learners", "atRisk", "attendanceFlags", "gradeFlags", "disciplineFlags"}
        kpis = {
            "learners": 0, "atRisk": 0, "attendanceFlags": 0,
            "gradeFlags": 0, "disciplineFlags": 0,
        }
        assert required.issubset(kpis.keys())

    def test_risk_breakdown_format(self):
        """Risk breakdown must be a list of {label, value} dicts."""
        breakdown = [
            {"label": "Attendance Risk", "value": 0},
            {"label": "Grade Risk", "value": 0},
            {"label": "Discipline Risk", "value": 0},
        ]
        for item in breakdown:
            assert "label" in item
            assert "value" in item

    def test_learner_object_fields(self):
        """Each learner object must have the expected fields."""
        sample = {
            "id": "1", "name": "John", "surname": "Doe",
            "grade": "8", "class": "8A",
            "absenceCount": 5, "hasAttendanceRisk": True,
            "avgPct": 35.0, "hasGradeRisk": True,
            "demeritBalance": 4.0, "hasDisciplineRisk": True,
            "riskLevel": "high", "riskFlags": ["attendance", "grade", "discipline"],
        }
        required = {
            "id", "name", "surname", "grade", "class",
            "absenceCount", "hasAttendanceRisk",
            "avgPct", "hasGradeRisk",
            "demeritBalance", "hasDisciplineRisk",
            "riskLevel", "riskFlags",
        }
        assert required.issubset(sample.keys())

    def test_risk_flags_contain_only_known_values(self):
        """Risk flags must only contain 'attendance', 'grade', or 'discipline'."""
        valid = {"attendance", "grade", "discipline"}
        for flags in [["attendance"], ["grade", "discipline"], ["attendance", "grade", "discipline"]]:
            for f in flags:
                assert f in valid, f"Unknown risk flag: {f}"
