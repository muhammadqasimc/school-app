"""School EMS marks-based promotion rules for Result Analysis (register fallback)."""

import importlib

import pytest


@pytest.fixture
def app_mod():
    return importlib.import_module("app")


def test_foundation_fails_when_home_language_below_50(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    by_cell = {
        ("English Home Language", 2): {"L1": 49.0},
        ("Afrikaans First Additional Language", 2): {"L1": 45.0},
        ("Mathematics", 2): {"L1": 45.0},
        ("Life Skills", 2): {"L1": 45.0},
    }
    assert not fn(by_cell, {}, 2, "L1")


def test_foundation_requires_afrikaans_fal_not_afrikaans_home_language(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    by_cell = {
        ("English Home Language", 3): {"L1": 55.0},
        ("Afrikaans Home Language", 3): {"L1": 55.0},
        ("Mathematics", 3): {"L1": 45.0},
        ("Life Skills", 3): {"L1": 45.0},
    }
    assert not fn(by_cell, {}, 3, "L1")


def test_foundation_fails_when_life_skills_below_40(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    by_cell = {
        ("English Home Language", 3): {"L1": 55.0},
        ("Afrikaans First Additional Language", 3): {"L1": 41.0},
        ("Mathematics", 3): {"L1": 41.0},
        ("Life Skills", 3): {"L1": 35.0},
    }
    assert not fn(by_cell, {}, 3, "L1")


def test_foundation_passes_when_all_phase_subjects_met(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    by_cell = {
        ("English Home Language", 3): {"L1": 55.0},
        ("Afrikaans First Additional Language", 3): {"L1": 41.0},
        ("Mathematics", 3): {"L1": 41.0},
        ("Life Skills", 3): {"L1": 41.0},
    }
    assert fn(by_cell, {}, 3, "L1")


def test_intermediate_requires_nst_social_sciences_life_skills_at_40(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    grade = 5
    base = {
        ("English Home Language", grade): {"L1": 55.0},
        ("Afrikaans First Additional Language", grade): {"L1": 45.0},
        ("Mathematics", grade): {"L1": 45.0},
        ("Natural Sciences and Technology", grade): {"L1": 45.0},
        ("Social Sciences", grade): {"L1": 35.0},
        ("Life Skills", grade): {"L1": 35.0},
    }
    assert not fn(base, {}, grade, "L1")

    ok = dict(base)
    ok[("Social Sciences", grade)] = {"L1": 41.0}
    ok[("Life Skills", grade)] = {"L1": 41.0}
    assert fn(ok, {}, grade, "L1")


def test_senior_requires_each_curriculum_subject_at_40(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    grade = 8
    core = {
        ("English Home Language", grade): {"L1": 55.0},
        ("Afrikaans First Additional Language", grade): {"L1": 45.0},
        ("Mathematics", grade): {"L1": 45.0},
    }
    others_weak = {
        ("Natural Sciences", grade): {"L1": 41.0},
        ("Social Sciences", grade): {"L1": 41.0},
        ("Life Orientation", grade): {"L1": 35.0},
        ("Technology", grade): {"L1": 41.0},
        ("Economic Management Sciences", grade): {"L1": 41.0},
        ("Creative Arts", grade): {"L1": 41.0},
    }
    by_fail = {**core, **others_weak}
    assert not fn(by_fail, {}, grade, "L1")

    others_ok = dict(others_weak)
    others_ok[("Life Orientation", grade)] = {"L1": 41.0}
    assert fn({**core, **others_ok}, {}, grade, "L1")


def test_fet_per_subject_thresholds(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    grade = 11
    by_cell = {
        ("English Home Language", grade): {"L1": 41.0},
        ("Afrikaans First Additional Language", grade): {"L1": 31.0},
        ("Mathematics", grade): {"L1": 31.0},
        ("Life Orientation", grade): {"L1": 31.0},
        ("Physical Sciences", grade): {"L1": 31.0},
        ("Accounting", grade): {"L1": 31.0},
    }
    assert fn(by_cell, {}, grade, "L1")

    bad_hl = dict(by_cell)
    bad_hl[("English Home Language", grade)] = {"L1": 39.0}
    assert not fn(bad_hl, {}, grade, "L1")

    bad_fal = dict(by_cell)
    bad_fal[("Afrikaans First Additional Language", grade)] = {"L1": 29.0}
    assert not fn(bad_fal, {}, grade, "L1")

    bad_elective = dict(by_cell)
    bad_elective[("Accounting", grade)] = {"L1": 29.0}
    assert not fn(bad_elective, {}, grade, "L1")


def test_fet_mathematical_literacy_at_30_passes(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    grade = 12
    by_cell = {
        ("English Home Language", grade): {"L1": 40.0},
        ("Afrikaans First Additional Language", grade): {"L1": 30.0},
        ("Mathematical Literacy", grade): {"L1": 30.0},
        ("Life Orientation", grade): {"L1": 30.0},
        ("Tourism", grade): {"L1": 35.0},
    }
    assert fn(by_cell, {}, grade, "L1")


def test_five_fet_subjects_all_met_passes(app_mod):
    fn = app_mod._management_learner_passes_result_analysis
    grade = 11
    by_cell = {
        ("English Home Language", grade): {"L1": 40.0},
        ("Afrikaans First Additional Language", grade): {"L1": 30.0},
        ("Mathematics", grade): {"L1": 30.0},
        ("Life Orientation", grade): {"L1": 30.0},
        ("History", grade): {"L1": 35.0},
    }
    assert fn(by_cell, {}, grade, "L1")


def test_aggregate_averages_duplicate_rows(monkeypatch, app_mod):
    def fake_fetch(year, term, subject=""):
        return [
            {"Grade": "4", "LearnerID": "L1", "Subject": "Mathematics", "Mark": 50, "TotalMark": 100},
            {"Grade": "4", "LearnerID": "L1", "Subject": "Mathematics", "Mark": 70, "TotalMark": 100},
        ]

    monkeypatch.setattr(app_mod, "_management_fetch_marks_with_grades", fake_fetch)
    cell, gl, _ = app_mod._management_result_analysis_aggregate("2026", "1")
    assert cell[("Mathematics", 4)]["L1"] == pytest.approx(60.0)
    assert gl[4]["L1"] == [pytest.approx(60.0)]


def test_result_analysis_summary_uses_register_p_over_marks_fail(app_mod):
    """P / CodeAuto promotes in summary even when marks-based rule would fail."""
    g = 5
    by_cell = {
        ("English Home Language", g): {"42": 30.0},
        ("Afrikaans First Additional Language", g): {"42": 30.0},
        ("Mathematics", g): {"42": 30.0},
        ("Natural Sciences and Technology", g): {"42": 30.0},
        ("Social Sciences", g): {"42": 30.0},
        ("Life Skills", g): {"42": 30.0},
    }
    promo_row = {
        "LearnerID": "42",
        "Grade": str(g),
        "CodeAuto": "P",
        "CodeSelected": "",
        "CodeSched": "",
        "PromotionDecision": "",
    }
    by_any = app_mod.build_learner_lookup_by_any_id([{"ID": "42", "LearnerID": ""}])
    promo_lookup = app_mod._management_build_promo_fast_lookup([promo_row], by_any)
    promoted, failed, progressed = app_mod._management_register_promotion_summary_for_learners(
        by_cell, promo_lookup, by_any, g, {"42"}
    )
    assert app_mod._management_learner_passes_result_analysis(by_cell, {}, g, "42") is False
    assert promoted == 1 and failed == 0 and progressed == 0


def test_result_analysis_summary_np_counts_failed_even_if_marks_pass(app_mod):
    g = 5
    by_cell = {
        ("English Home Language", g): {"42": 80.0},
        ("Afrikaans First Additional Language", g): {"42": 80.0},
        ("Mathematics", g): {"42": 80.0},
        ("Natural Sciences and Technology", g): {"42": 80.0},
        ("Social Sciences", g): {"42": 80.0},
        ("Life Skills", g): {"42": 80.0},
    }
    promo_row = {
        "LearnerID": "42",
        "Grade": str(g),
        "CodeAuto": "NP",
        "CodeSelected": "",
        "CodeSched": "",
        "PromotionDecision": "",
    }
    by_any = app_mod.build_learner_lookup_by_any_id([{"ID": "42", "LearnerID": ""}])
    promo_lookup = app_mod._management_build_promo_fast_lookup([promo_row], by_any)
    promoted, failed, progressed = app_mod._management_register_promotion_summary_for_learners(
        by_cell, promo_lookup, by_any, g, {"42"}
    )
    assert promoted == 0 and failed == 1 and progressed == 0


def test_result_analysis_summary_pg_counts_progressed(app_mod):
    g = 5
    by_cell = {
        ("English Home Language", g): {"42": 80.0},
        ("Afrikaans First Additional Language", g): {"42": 80.0},
        ("Mathematics", g): {"42": 80.0},
        ("Natural Sciences and Technology", g): {"42": 80.0},
        ("Social Sciences", g): {"42": 80.0},
        ("Life Skills", g): {"42": 80.0},
    }
    promo_row = {
        "LearnerID": "42",
        "Grade": str(g),
        "CodeAuto": "",
        "CodeSelected": "",
        "CodeSched": "PG",
        "PromotionDecision": "",
    }
    by_any = app_mod.build_learner_lookup_by_any_id([{"ID": "42", "LearnerID": ""}])
    promo_lookup = app_mod._management_build_promo_fast_lookup([promo_row], by_any)
    promoted, failed, progressed = app_mod._management_register_promotion_summary_for_learners(
        by_cell, promo_lookup, by_any, g, {"42"}
    )
    assert promoted == 0 and failed == 0 and progressed == 1


def test_aggregate_merges_numeric_id_and_learner_code(monkeypatch, app_mod):
    """ReportMarks sometimes stores the same learner as code vs numeric ID; summary must not double-count."""

    def fake_fetch(year, term, subject=""):
        return [
            {"Grade": "5", "LearnerID": "CODE1", "Subject": "English Home Language", "Mark": 60, "TotalMark": 100},
            {"Grade": "5", "LearnerID": "42", "Subject": "Mathematics", "Mark": 60, "TotalMark": 100},
        ]

    def fake_execute(query, params=()):
        text = " ".join(str(query).split())
        if "SELECT [ID], [LearnerID] FROM Learner_Info WHERE [Status]" in text:
            return [{"ID": "42", "LearnerID": "CODE1"}]
        return []

    monkeypatch.setattr(app_mod, "_management_fetch_marks_with_grades", fake_fetch)
    monkeypatch.setattr(app_mod.mdb_conn, "execute_query", fake_execute)
    cell, _gl, _ = app_mod._management_result_analysis_aggregate("2026", "1")
    assert cell[("English Home Language", 5)] == {"42": 60.0}
    assert cell[("Mathematics", 5)] == {"42": 60.0}


def test_percentage_half_up_rounding(app_mod):
    ru = app_mod._management_round_percentage_half_up
    assert ru(49.4, 0) == 49.0
    assert ru(49.5, 0) == 50.0
    assert ru(49.6, 0) == 50.0
    assert ru(12.345, 2) == 12.35


def test_aggregate_half_up_average(monkeypatch, app_mod):
    """Per-row % rounded to integer; mean 49.5 rounds half-up to 50."""

    def fake_fetch(year, term, subject=""):
        return [
            {"Grade": "5", "LearnerID": "L1", "Subject": "English Home Language", "Mark": 49, "TotalMark": 100},
            {"Grade": "5", "LearnerID": "L1", "Subject": "English Home Language", "Mark": 50, "TotalMark": 100},
        ]

    monkeypatch.setattr(app_mod, "_management_fetch_marks_with_grades", fake_fetch)
    cell, gl, _ = app_mod._management_result_analysis_aggregate("2026", "1")
    assert cell[("English Home Language", 5)]["L1"] == 50.0
    assert gl[5]["L1"] == [pytest.approx(50.0)]
