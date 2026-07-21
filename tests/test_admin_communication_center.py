import importlib


def _admin_client(app_mod):
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    with app_mod.app.app_context():
        app_mod.ensure_sqlite_schema()
        user = app_mod.User.query.filter_by(username=app_mod.ADMIN_USERNAME).first()
        if not user:
            user = app_mod.User(
                username=app_mod.ADMIN_USERNAME,
                password_hash="x",
                first_login=False,
            )
            app_mod.db.session.add(user)
            app_mod.db.session.commit()
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True
    return client


def test_admin_communication_new_routes_exist():
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/admin/communication/discipline/incidents" in rules
    assert "/admin/communication/discipline/send" in rules
    assert "/admin/communication/finance/outstanding" in rules
    assert "/admin/communication/finance/send" in rules


def test_admin_communication_discipline_incidents_and_send(monkeypatch):
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    def fake_query(sql, params=None):
        text = str(sql)
        if "FROM DisciplinaryRecords dr" in text:
            return [{
                "id": "901",
                "Learnerid": "1001",
                "Date": "2026-04-22",
                "MisconductDescription": "Late for class",
            }]
        if "FROM Learner_Info" in text:
            return [{
                "ID": "1001",
                "LearnerID": "1001",
                "FName": "Learner",
                "SName": "One",
                "Grade": "10",
            }]
        return []

    sent_sms = []
    sent_wa = []

    monkeypatch.setattr(app_mod.mdb_conn, "execute_query", fake_query)
    monkeypatch.setattr(
        app_mod,
        "_get_parent_phones_from_mdb",
        lambda learner_ids: [("+27821234567", "Parent One")],
    )
    monkeypatch.setattr(app_mod, "send_sms_message", lambda phone, message: sent_sms.append((phone, message)))
    monkeypatch.setattr(app_mod, "send_whatsapp_message", lambda phone, message: sent_wa.append((phone, message)) or True)

    incidents_resp = client.get(
        "/admin/communication/discipline/incidents?year=2026&start_date=2026-04-01&end_date=2026-04-30&misconduct=Late"
    )
    assert incidents_resp.status_code == 200
    incidents_payload = incidents_resp.get_json() or {}
    incidents = incidents_payload.get("incidents") or []
    assert len(incidents) == 1
    assert incidents[0]["preview_message"] == "Learner One: Late for class"

    send_resp = client.post(
        "/admin/communication/discipline/send",
        json={"channels": ["sms", "whatsapp"], "incidents": incidents},
    )
    assert send_resp.status_code == 200
    send_payload = send_resp.get_json() or {}
    assert send_payload.get("ok") is True
    assert send_payload.get("sent") == 2
    assert len(sent_sms) == 1
    assert len(sent_wa) == 1
    assert sent_sms[0][1] == "Learner One (2026-04-22): Late for class"


def test_admin_communication_finance_send_guardrails(monkeypatch):
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    def fake_query(sql, params=None):
        text = str(sql)
        if "FROM Learner_Info" in text:
            return [{
                "IDText": "1001",
                "LearnerIDText": "L1001",
                "FName": "L",
                "SName": "One",
                "Grade": "10",
            }]
        return []

    monkeypatch.setattr(app_mod.mdb_conn, "execute_query", fake_query)
    monkeypatch.setattr(
        app_mod,
        "_get_parent_phones_from_mdb",
        lambda learner_ids: [("+27820000001", "Guardian A"), ("+27820000001", "Guardian A")],
    )
    monkeypatch.setattr(app_mod, "send_sms_message", lambda phone, message: None)
    monkeypatch.setattr(
        app_mod,
        "_finance_payload_for_learner",
        lambda **kwargs: {
            "annualFee": 0,
            "totalOwed": 0,
            "totalPaid": 0,
            "balance": 200.0,
            "outstanding": 200.0,
            "currentYearBalance": 200.0,
            "isPaid": False,
            "status": "Outstanding",
            "transactions": [{"Year": str(kwargs.get("target_year", 2026)), "Debit": 200.0, "Credit": 0.0}],
            "grade": "10",
            "currentYear": kwargs.get("target_year", 2026),
        },
    )

    bad_resp = client.post(
        "/admin/communication/finance/send",
        json={"channels": ["sms"], "learners": [{"learner_id": "1001", "learner_name": "L One", "year": 2026, "outstanding": 0}]},
    )
    assert bad_resp.status_code == 200
    bad_payload = bad_resp.get_json() or {}
    assert bad_payload.get("sent") == 0
    assert len(bad_payload.get("failed") or []) == 1

    ok_resp = client.post(
        "/admin/communication/finance/send",
        json={"channels": ["sms"], "learners": [{"learner_id": "1001", "learner_name": "L One", "year": 2026, "outstanding": 200.0}]},
    )
    assert ok_resp.status_code == 200
    ok_payload = ok_resp.get_json() or {}
    assert ok_payload.get("ok") is True
    assert ok_payload.get("sent") == 1
    assert isinstance(ok_payload.get("batch_id"), str)

    outstanding_resp = client.get("/admin/communication/finance/outstanding?year=2024&grade=10&limit=5")
    assert outstanding_resp.status_code == 200


def test_admin_communication_finance_reminders_empty():
    """Test that the reminders endpoint returns empty list when no finance deliveries exist."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)
    # Isolate: clear finance delivery logs from prior tests
    with app_mod.app.app_context():
        app_mod.CommunicationDeliveryLog.query.filter_by(category="finance").delete()
        app_mod.db.session.commit()
    resp = client.get("/admin/communication/finance/reminders")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert data.get("batches") == []
    assert data.get("total_batches") == 0
    assert data.get("page") == 1
    assert isinstance(data.get("total_pages"), int)
    assert isinstance(data.get("total_batches"), int)


def test_admin_communication_finance_reminders_with_data(monkeypatch):
    """Test that the reminders endpoint returns past batches after sending finance messages."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    def fake_query(sql, params=None):
        text = str(sql)
        if "FROM Learner_Info" in text:
            return [{
                "ID": "1001",
                "LearnerID": "L1001",
                "FName": "L",
                "SName": "One",
                "Grade": "10",
            }]
        return []

    monkeypatch.setattr(app_mod.mdb_conn, "execute_query", fake_query)
    monkeypatch.setattr(
        app_mod,
        "_get_parent_phones_from_mdb",
        lambda learner_ids: [("+278****0001", "Guardian A")],
    )
    monkeypatch.setattr(app_mod, "send_sms_message", lambda phone, message: None)
    monkeypatch.setattr(
        app_mod,
        "_finance_payload_for_learner",
        lambda **kwargs: {
            "annualFee": 0,
            "totalOwed": 0,
            "totalPaid": 0,
            "balance": 200.0,
            "outstanding": 200.0,
            "currentYearBalance": 200.0,
            "isPaid": False,
            "status": "Outstanding",
            "transactions": [{"Year": str(kwargs.get("target_year", 2026)), "Debit": 200.0, "Credit": 0.0}],
            "grade": "10",
            "currentYear": kwargs.get("target_year", 2026),
        },
    )

    # Send a finance message to create test data
    send_resp = client.post(
        "/admin/communication/finance/send",
        json={
            "channels": ["sms"],
            "learners": [{"learner_id": "1001", "learner_name": "L One", "year": 2026, "outstanding": 200.0}],
            "finance_template": "Dear {parent_name}, balance: {outstanding_amount}",
        },
    )
    assert send_resp.status_code == 200
    send_data = send_resp.get_json() or {}
    assert send_data.get("ok") is True
    batch_id = send_data.get("batch_id")
    assert isinstance(batch_id, str)

    # Now check the reminders endpoint
    resp = client.get("/admin/communication/finance/reminders")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert data.get("total_batches") >= 1
    batches = data.get("batches") or []
    our_batch = next((b for b in batches if b["batch_id"] == batch_id), None)
    assert our_batch is not None, f"Batch {batch_id} not found in {batches}"
    assert our_batch["total"] >= 1
    assert our_batch["sent"] >= 1
    assert our_batch["failed"] == 0
    assert "sms" in our_batch.get("channels", [])
    assert our_batch.get("last_sent") is not None
    assert data.get("page") == 1
    assert isinstance(data.get("total_pages"), int)


def test_admin_communication_finance_reminder_detail(monkeypatch):
    """Test that the reminder detail endpoint returns delivery details for a specific batch."""
    app_mod = importlib.import_module("app")
    client = _admin_client(app_mod)

    def fake_query(sql, params=None):
        text = str(sql)
        if "FROM Learner_Info" in text:
            return [{
                "ID": "1001",
                "LearnerID": "L1001",
                "FName": "L",
                "SName": "One",
                "Grade": "10",
            }]
        return []

    monkeypatch.setattr(app_mod.mdb_conn, "execute_query", fake_query)
    monkeypatch.setattr(
        app_mod,
        "_get_parent_phones_from_mdb",
        lambda learner_ids: [("+278****0001", "Guardian A")],
    )
    monkeypatch.setattr(app_mod, "send_sms_message", lambda phone, message: None)
    monkeypatch.setattr(app_mod, "send_whatsapp_message", lambda phone, message: True)
    monkeypatch.setattr(
        app_mod,
        "_finance_payload_for_learner",
        lambda **kwargs: {
            "annualFee": 0,
            "totalOwed": 0,
            "totalPaid": 0,
            "balance": 200.0,
            "outstanding": 200.0,
            "currentYearBalance": 200.0,
            "isPaid": False,
            "status": "Outstanding",
            "transactions": [{"Year": str(kwargs.get("target_year", 2026)), "Debit": 200.0, "Credit": 0.0}],
            "grade": "10",
            "currentYear": kwargs.get("target_year", 2026),
        },
    )

    # Send a finance message to create test data
    send_resp = client.post(
        "/admin/communication/finance/send",
        json={
            "channels": ["sms", "whatsapp"],
            "learners": [{"learner_id": "1001", "learner_name": "L One", "year": 2026, "outstanding": 200.0}],
            "finance_template": "Dear {parent_name}, balance: {outstanding_amount}",
        },
    )
    assert send_resp.status_code == 200
    send_data = send_resp.get_json() or {}
    assert send_data.get("ok") is True
    batch_id = send_data.get("batch_id")

    # Get detail for this batch
    resp = client.get(f"/admin/communication/finance/reminder/{batch_id}")
    assert resp.status_code == 200
    data = resp.get_json() or {}
    assert data.get("batch_id") == batch_id
    assert data.get("total") >= 2, f"Expected >=2 deliveries, got {data.get('total')}"
    deliveries = data.get("deliveries") or []
    assert len(deliveries) >= 2
    # Check a delivery record
    delivery = deliveries[0]
    assert "recipient_name" in delivery
    assert "recipient_phone" in delivery
    assert "channel" in delivery
    assert "status" in delivery
    assert "sent_at" in delivery
    assert delivery.get("status") == "sent"

    # Test non-existent batch returns empty
    resp2 = client.get("/admin/communication/finance/reminder/nonexistent-batch-id")
    assert resp2.status_code == 200
    data2 = resp2.get_json() or {}
    assert data2.get("total") == 0
    assert data2.get("deliveries") == []


def test_admin_communication_reminders_route_exists():
    """Test that the new reminder routes exist in the URL map."""
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/admin/communication/finance/reminders" in rules
    assert "/admin/communication/finance/reminder/<batch_id>" in rules
