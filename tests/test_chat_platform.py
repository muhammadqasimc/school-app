import importlib
import secrets


def _auth_client(app_mod, user):
    app_mod.app.config["WTF_CSRF_ENABLED"] = False
    client = app_mod.app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)
        sess["_fresh"] = True
    return client


def test_chat_routes_exist():
    app_mod = importlib.import_module("app")
    rules = {r.rule for r in app_mod.app.url_map.iter_rules()}
    assert "/api/chat/threads" in rules
    assert "/api/chat/candidates" in rules
    assert "/api/chat/threads/<int:thread_id>/messages" in rules
    assert "/api/chat/threads/<int:thread_id>/read" in rules
    assert "/api/chat/messages/<int:message_id>/moderate" in rules
    assert "/api/chat/attachments/<int:attachment_id>" in rules
    assert "/parent/messages" in rules
    assert "/management/chat" in rules
    assert "/admin/chat" in rules


def test_chat_models_exist():
    app_mod = importlib.import_module("app")
    assert hasattr(app_mod, "ChatThread")
    assert hasattr(app_mod, "ChatParticipant")
    assert hasattr(app_mod, "ChatMessage")
    assert hasattr(app_mod, "ChatAttachment")
    assert hasattr(app_mod, "ChatMessageReceipt")


def test_chat_thread_lifecycle_smoke():
    app_mod = importlib.import_module("app")
    app = app_mod.app
    with app.app_context():
        app_mod.ensure_sqlite_schema()
        suffix = secrets.token_hex(4)
        u1 = app_mod.User(
            username=f"chat_parent_{suffix}",
            password_hash="x",
            is_parent=True,
            first_login=False,
        )
        u2 = app_mod.User(
            username=f"chat_manager_{suffix}",
            password_hash="x",
            is_manager=True,
            first_login=False,
        )
        app_mod.db.session.add_all([u1, u2])
        app_mod.db.session.commit()
        app_mod.db.session.add(app_mod.UserLearner(user_id=u1.id, learner_id="123"))
        app_mod.db.session.commit()

        client = _auth_client(app_mod, u1)
        fd = {
            "thread_type": "direct",
            "participant_ids": str(u2.id),
            "learner_id": "123",
        }
        resp = client.post("/api/chat/threads", data=fd)
        assert resp.status_code == 200, resp.get_data(as_text=True)
        payload = resp.get_json() or {}
        thread_id = int(payload.get("thread", {}).get("id") or 0)
        assert thread_id > 0

        msg_resp = client.post(
            f"/api/chat/threads/{thread_id}/messages",
            data={"body": "Hello from automated test."},
        )
        assert msg_resp.status_code == 200, msg_resp.get_data(as_text=True)

        list_resp = client.get("/api/chat/threads")
        assert list_resp.status_code == 200
        rows = (list_resp.get_json() or {}).get("threads") or []
        assert any(int(r.get("id") or 0) == thread_id for r in rows)

        # --- Read receipt test ---
        # Create a second message from the manager directly via DB
        msg2 = app_mod.ChatMessage(
            thread_id=thread_id,
            sender_user_id=u2.id,
            body="Response from manager — read receipt test.",
            message_type="text",
        )
        app_mod.db.session.add(msg2)
        app_mod.db.session.commit()

        # Parent reads the thread (marks messages as delivered/read)
        read_resp = client.post(f"/api/chat/threads/{thread_id}/read")
        assert read_resp.status_code == 200, read_resp.get_data(as_text=True)
        read_data = read_resp.get_json() or {}
        assert read_data.get("ok") is True
        assert isinstance(read_data.get("receipts_created"), int)
        assert read_data["receipts_created"] >= 1

        # Verify ChatMessageReceipt records exist
        receipts = app_mod.ChatMessageReceipt.query.filter_by(user_id=u1.id).all()
        assert len(receipts) >= 1
        for r in receipts:
            assert r.delivered_at is not None
            assert r.read_at is not None

        # Verify participant last_read_message_id is set
        part = app_mod.ChatParticipant.query.filter_by(
            thread_id=thread_id, user_id=u1.id,
        ).first()
        assert part is not None
        assert part.last_read_message_id is not None

        # Second read should report 0 new receipts (already read)
        read_resp2 = client.post(f"/api/chat/threads/{thread_id}/read")
        assert read_resp2.status_code == 200
        assert read_resp2.get_json().get("receipts_created") == 0


def test_chat_auto_mark_receipts_on_get_messages():
    """Auto-marking: GET /api/chat/threads/<id>/messages creates receipts."""
    app_mod = importlib.import_module("app")
    app = app_mod.app
    with app.app_context():
        app_mod.ensure_sqlite_schema()
        suffix = secrets.token_hex(4)
        parent = app_mod.User(
            username=f"am_parent_{suffix}", password_hash="x",
            is_parent=True, first_login=False,
        )
        teacher = app_mod.User(
            username=f"am_teacher_{suffix}", password_hash="x",
            is_teacher=True, first_login=False,
        )
        app_mod.db.session.add_all([parent, teacher])
        app_mod.db.session.commit()
        app_mod.db.session.add(app_mod.UserLearner(user_id=parent.id, learner_id="A1"))
        app_mod.db.session.commit()

        p = _auth_client(app_mod, parent)

        # Create thread
        r = p.post("/api/chat/threads", data={
            "thread_type": "direct", "participant_ids": str(teacher.id), "learner_id": "A1",
        })
        thread_id = (r.get_json() or {}).get("thread", {}).get("id")
        assert thread_id

        # Parent sends first message
        r = p.post(f"/api/chat/threads/{thread_id}/messages", data={"body": "Hello"})
        assert r.status_code == 200

        # Teacher message created directly in DB (unread by parent)
        msg2 = app_mod.ChatMessage(
            thread_id=thread_id, sender_user_id=teacher.id,
            body="Teacher reply", message_type="text",
        )
        app_mod.db.session.add(msg2)
        app_mod.db.session.commit()

        # Before fetching, no receipts exist for parent → teacher msg
        pre = app_mod.ChatMessageReceipt.query.filter_by(
            message_id=msg2.id, user_id=parent.id,
        ).first()
        assert pre is None, "Receipt should not exist before GET"

        # Parent fetches messages → auto-mark triggers
        r = p.get(f"/api/chat/threads/{thread_id}/messages")
        assert r.status_code == 200
        rows = (r.get_json() or {}).get("rows", [])

        # The teacher message should have deliveredAt + readAt
        teacher_msg = next((m for m in rows if m["senderUserId"] == teacher.id), None)
        assert teacher_msg is not None, "Teacher msg missing from response"
        assert teacher_msg.get("deliveredAt") is not None, f"deliveredAt missing: {teacher_msg}"
        assert teacher_msg.get("readAt") is not None, f"readAt missing: {teacher_msg}"

        # Receipt record now exists in DB
        receipt = app_mod.ChatMessageReceipt.query.filter_by(
            message_id=msg2.id, user_id=parent.id,
        ).first()
        assert receipt is not None, "Receipt should exist after GET"
        assert receipt.delivered_at is not None
        assert receipt.read_at is not None

        # Parent's own message should NOT have a receipt
        own_receipt = app_mod.ChatMessageReceipt.query.filter_by(
            user_id=parent.id,
        ).all()
        # Only receipt should be for teacher's message
        assert len(own_receipt) == 1, f"Expected 1 receipt (teacher msg), got {len(own_receipt)}"


def test_chat_auto_mark_sender_not_marked():
    """Auto-marking does NOT create receipts for the user's own messages."""
    app_mod = importlib.import_module("app")
    app = app_mod.app
    with app.app_context():
        app_mod.ensure_sqlite_schema()
        suffix = secrets.token_hex(4)
        u1 = app_mod.User(
            username=f"as_parent_{suffix}", password_hash="x",
            is_parent=True, first_login=False,
        )
        u2 = app_mod.User(
            username=f"as_teacher_{suffix}", password_hash="x",
            is_teacher=True, first_login=False,
        )
        app_mod.db.session.add_all([u1, u2])
        app_mod.db.session.commit()
        app_mod.db.session.add(app_mod.UserLearner(user_id=u1.id, learner_id="A2"))
        app_mod.db.session.commit()

        c = _auth_client(app_mod, u1)

        r = c.post("/api/chat/threads", data={
            "thread_type": "direct", "participant_ids": str(u2.id), "learner_id": "A2",
        })
        thread_id = (r.get_json() or {}).get("thread", {}).get("id")
        assert thread_id

        # u1 sends message (own message)
        r = c.post(f"/api/chat/threads/{thread_id}/messages", data={"body": "My own message"})
        assert r.status_code == 200

        # Fetch messages — should NOT create receipt for own message
        r = c.get(f"/api/chat/threads/{thread_id}/messages")
        assert r.status_code == 200

        my_msg = app_mod.ChatMessage.query.filter_by(
            thread_id=thread_id, sender_user_id=u1.id,
        ).first()
        assert my_msg is not None

        receipt = app_mod.ChatMessageReceipt.query.filter_by(
            message_id=my_msg.id, user_id=u1.id,
        ).first()
        assert receipt is None, "Should NOT create receipt for own message"
