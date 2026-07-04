import importlib


def test_fetch_demerit_rows_maps_alias_keys(monkeypatch):
    app_mod = importlib.import_module("app")

    monkeypatch.setattr(
        app_mod,
        "get_learner_match_candidates",
        lambda learner_id: [str(learner_id)],
    )

    sample_rows = [
        {
            "LearnerIDText": "101",
            "date": "2026-04-20 09:00:00",
            "levelmisconduct": "Major",
            "misconductdescription": "Late arrival",
            "demerit": 2,
            "merit": 0,
            "authorisedby": "Teacher A",
        }
    ]

    monkeypatch.setattr(
        app_mod.mdb_conn,
        "execute_query",
        lambda *_args, **_kwargs: sample_rows,
    )

    rows = app_mod._fetch_demerit_rows_for_learners(["101"], year="2026", chunk_size=80)

    assert "101" in rows
    assert len(rows["101"]) == 1
    payload = rows["101"][0]
    assert payload["MisconductDescription"] == "Late arrival"
    assert payload["LevelMisconduct"] == "Major"
    assert payload["AuthorisedBy"] == "Teacher A"
