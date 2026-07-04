"""
School asset inventory — registered from app.py after models load.
"""

from __future__ import annotations

import csv
import io
import json
import secrets
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required
from sqlalchemy import false as sql_false
from sqlalchemy import func, or_


ITEM_TYPES = ("asset", "accessory", "consumable", "component")
OPS_STATUSES = ("ready", "pending", "repair", "archived")
ARCHIVED_REASONS = ("lost", "stolen", "broken", "other")


def register_inventory(flask_app: Flask) -> None:
    """Attach inventory routes to Flask app."""

    def root():
        """
        When the server is started with ``python app.py``, the application's
        globals live under ``sys.modules['__main__']``. Doing ``import app`` in that
        case loads *a second copy* of app.py so Flask-SQLAlchemy sees the wrong
        ``SQLAlchemy`` instance. Prefer ``__main__`` when it exposes our models.
        """
        import sys

        main = sys.modules.get("__main__")
        if getattr(main, "SchoolAssetItem", None) is not None:
            return main
        import app as app_module

        return app_module

    def activity(item_id, action: str, summary: str, payload=None):
        r = root()
        row = r.SchoolAssetActivity(
            item_id=item_id,
            actor_user_id=r.current_user.id,
            action=str(action)[:48],
            summary=str(summary)[:500],
            payload_json=(json.dumps(payload)[:8000] if payload is not None else None),
        )
        r.db.session.add(row)

    def assignable_staff(r):
        return (
            r.User.query.filter(
                or_(
                    r.User.is_teacher.is_(True),
                    r.User.is_manager.is_(True),
                    r.User.username == r.ADMIN_USERNAME,
                )
            )
            .order_by(r.User.username)
            .limit(800)
            .all()
        )

    def effective_requestable(item, model) -> bool:
        o = getattr(item, "is_requestable_override", None)
        if o is not None:
            return bool(o)
        return bool(getattr(model, "is_requestable", False))

    def effective_status_label(item, open_co):
        if getattr(item, "deleted_at", None):
            return "deleted"
        if item.ops_status == "archived":
            return "archived"
        if open_co:
            return "deployed"
        if item.ops_status == "pending":
            return "pending"
        if item.ops_status == "repair":
            return "out_for_repair"
        return "ready_to_deploy"

    def consumable_bulk(model) -> bool:
        return (model.item_type or "").lower() == "consumable"

    def open_checkout(r, item_id: int):
        return r.SchoolAssetCheckout.query.filter_by(
            item_id=item_id, checkin_at=None
        ).first()

    # ---- Dashboard ------------------------------------------------------------

    @flask_app.route("/inventory")
    @login_required
    def inventory_dashboard():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g

        Ai, Am, Ac, Aact = (
            r.SchoolAssetItem,
            r.SchoolAssetModel,
            r.SchoolAssetCheckout,
            r.SchoolAssetActivity,
        )

        base = Ai.query.filter(Ai.deleted_at.is_(None))
        type_counts = dict.fromkeys(ITEM_TYPES, 0)
        for row in (
            r.db.session.query(Am.item_type, r.db.func.count(Ai.id))
            .join(Ai, Ai.model_id == Am.id)
            .filter(Ai.deleted_at.is_(None))
            .group_by(Am.item_type)
            .all()
        ):
            t = (row[0] or "").lower()
            if t in type_counts:
                type_counts[t] = int(row[1])

        status_totals = defaultdict(int)
        for it in base:
            oc = open_checkout(r, it.id)
            status_totals[effective_status_label(it, oc)] += 1

        deployed_ct = Ac.query.filter(Ac.checkin_at.is_(None)).count()
        act_rows = (
            Aact.query.order_by(Aact.created_at.desc()).limit(40).all()
        )
        enriched = [(a, r.User.query.get(a.actor_user_id)) for a in act_rows]

        return render_template(
            "inventory/dashboard.html",
            type_counts=dict(type_counts),
            status_totals=dict(status_totals),
            deployed_ct=deployed_ct,
            item_total=base.count(),
            recent_activity=enriched,
        )

    @flask_app.route("/inventory/lookup", methods=["POST"])
    @login_required
    def inventory_lookup():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        code = (request.form.get("code") or "").strip()
        if not code:
            flash("Enter a tag or scan value.", "error")
            return redirect(url_for("inventory_dashboard"))

        item = r.SchoolAssetItem.query.filter(
            r.SchoolAssetItem.deleted_at.is_(None),
            or_(
                r.SchoolAssetItem.tag.ilike(code),
                r.SchoolAssetItem.scan_token == code,
                r.SchoolAssetItem.serial_number.ilike(code),
            ),
        ).first()
        if not item:
            flash("No matching inventory item.", "error")
            return redirect(url_for("inventory_items"))
        return redirect(url_for("inventory_item_detail", item_id=item.id))

    @flask_app.route("/inventory/scan/<token>")
    @login_required
    def inventory_scan_token(token):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.filter_by(scan_token=token).first()
        if not item or item.deleted_at:
            abort(404)
        return redirect(url_for("inventory_item_detail", item_id=item.id))

    # ---- Items ----------------------------------------------------------------

    @flask_app.route("/inventory/items")
    @login_required
    def inventory_items():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        Ai, Am = r.SchoolAssetItem, r.SchoolAssetModel
        q = Ai.query.filter(Ai.deleted_at.is_(None))
        itype = (request.args.get("item_type") or "").strip().lower()
        if itype in ITEM_TYPES:
            mids = [m.id for m in Am.query.filter_by(item_type=itype).all()]
            if mids:
                q = q.filter(Ai.model_id.in_(mids))
            else:
                q = q.filter(sql_false())
        st = (request.args.get("status") or "").strip().lower()
        search = (request.args.get("q") or "").strip()
        if search:
            q = q.filter(
                or_(
                    Ai.tag.ilike(f"%{search}%"),
                    Ai.serial_number.ilike(f"%{search}%"),
                    Ai.physical_location.ilike(f"%{search}%"),
                    Ai.notes.ilike(f"%{search}%"),
                )
            )
        rows = q.order_by(Ai.tag).limit(500).all()
        out = []
        for it in rows:
            mo = Am.query.get(it.model_id)
            oc = open_checkout(r, it.id)
            assignee = None
            if oc:
                assignee = r.User.query.get(oc.assignee_user_id)
            lab = effective_status_label(it, oc)
            if st and lab != st:
                continue
            out.append((it, mo, oc, assignee, lab))
        return render_template(
            "inventory/items_list.html",
            rows=out,
            item_types=ITEM_TYPES,
            status_filter=st,
            item_type_filter=itype,
            search=search,
        )

    @flask_app.route("/inventory/items/new", methods=["GET", "POST"])
    @login_required
    def inventory_item_new():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        models = (
            r.SchoolAssetModel.query.order_by(r.SchoolAssetModel.name).limit(500).all()
        )
        def _render_new_form(cfs_e, preset_mod=None, draft=None):
            draft = draft or {}
            return render_template(
                "inventory/item_form.html",
                models=models,
                item=None,
                custom_fields=cfs_e,
                preset_model=preset_mod,
                item_types=ITEM_TYPES,
                ops_statuses=OPS_STATUSES,
                archived_reasons=ARCHIVED_REASONS,
                custom_values={},
                draft_model_name=draft.get("model_name", ""),
                draft_item_type=draft.get("item_type", "asset"),
                draft_manufacturer=draft.get("manufacturer", ""),
            )

        if request.method == "POST":
            mid = int(request.form.get("model_id") or 0)
            tag = (request.form.get("tag") or "").strip()
            loc = (request.form.get("physical_location") or "").strip() or None
            notes = (request.form.get("notes") or "").strip() or None
            qty = int(request.form.get("quantity_on_hand") or 1)
            ops = (request.form.get("ops_status") or "ready").strip()
            if ops not in OPS_STATUSES:
                ops = "ready"

            draft = {
                "model_name": (request.form.get("model_name") or "").strip(),
                "item_type": (request.form.get("item_type") or "asset").strip().lower(),
                "manufacturer": (request.form.get("manufacturer") or "").strip(),
            }
            if draft["item_type"] not in ITEM_TYPES:
                draft["item_type"] = "asset"

            mo = None
            if mid:
                mo = r.SchoolAssetModel.query.get(mid)
                if not mo:
                    flash("That kind no longer exists — pick another or describe a new one.", "error")
                    return _render_new_form([], None, draft)
            else:
                if not draft["model_name"]:
                    flash(
                        'Use "What is this?" to name the kind of asset (you can add several items under the same name).',
                        "error",
                    )
                    return _render_new_form([], None, draft)
                mo = (
                    r.SchoolAssetModel.query.filter(
                        func.lower(r.SchoolAssetModel.name)
                        == draft["model_name"].lower(),
                        r.SchoolAssetModel.item_type == draft["item_type"],
                    ).first()
                )

            if not tag:
                flash("Tag is required — it is the unique ID for this physical item or bin.", "error")
                cfs_e = []
                if mo:
                    cfs_e = (
                        r.SchoolAssetCustomField.query.filter_by(model_id=mo.id)
                        .order_by(r.SchoolAssetCustomField.sort_index)
                        .all()
                    )
                return _render_new_form(
                    cfs_e, mo if mid else None, draft
                )

            if r.SchoolAssetItem.query.filter_by(tag=tag).first():
                flash("That tag is already in use.", "error")
                cfs_e = []
                if mo:
                    cfs_e = (
                        r.SchoolAssetCustomField.query.filter_by(model_id=mo.id)
                        .order_by(r.SchoolAssetCustomField.sort_index)
                        .all()
                    )
                return _render_new_form(cfs_e, mo if mid else None, draft)

            if mo is None:
                mo = r.SchoolAssetModel(
                    item_type=draft["item_type"],
                    name=draft["model_name"][:200],
                    manufacturer=(draft["manufacturer"][:160] if draft["manufacturer"] else None),
                    description=None,
                    low_stock_threshold=None,
                    default_location=None,
                    is_requestable=False,
                )
                r.db.session.add(mo)
                r.db.session.flush()
                activity(
                    None,
                    "model_auto_created",
                    f"Auto-created kind: {mo.name}",
                    {"item_type": mo.item_type},
                )

            if consumable_bulk(mo):
                qty = max(0, qty)
            else:
                qty = 1
            token = secrets.token_urlsafe(24)[:64]
            sn = (request.form.get("serial_number") or "").strip() or None
            if sn:
                sn = sn[:120]
            item = r.SchoolAssetItem(
                model_id=mo.id,
                tag=tag,
                serial_number=sn,
                scan_token=token,
                quantity_on_hand=qty,
                ops_status=ops,
                physical_location=loc or mo.default_location,
                notes=notes,
            )
            cf_rows = r.SchoolAssetCustomField.query.filter_by(
                model_id=mo.id
            ).order_by(r.SchoolAssetCustomField.sort_index)
            cv = {}
            for cf in cf_rows:
                key = cf.field_key
                raw = (request.form.get(f"cf_{key}") or "").strip()
                if cf.field_type == "bool":
                    cv[key] = bool(request.form.get(f"cf_{key}"))
                elif cf.field_type == "number":
                    cv[key] = float(raw) if raw else None
                else:
                    cv[key] = raw or None
            item.custom_values_json = json.dumps(cv)
            r.db.session.add(item)
            r.db.session.flush()
            activity(
                item.id,
                "created",
                f"Created item {item.tag}",
                {"model": mo.name},
            )
            r.db.session.commit()
            flash("Item created.", "success")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        preset_model_obj = None
        cfs = []
        try:
            _mid_pre = int(request.args.get("model_id") or 0)
        except ValueError:
            _mid_pre = 0
        if _mid_pre:
            preset_model_obj = r.SchoolAssetModel.query.get(_mid_pre)
            if preset_model_obj:
                cfs = (
                    r.SchoolAssetCustomField.query.filter_by(model_id=_mid_pre)
                    .order_by(r.SchoolAssetCustomField.sort_index)
                    .all()
                )
        return render_template(
            "inventory/item_form.html",
            models=models,
            item=None,
            custom_fields=cfs,
            preset_model=preset_model_obj,
            item_types=ITEM_TYPES,
            ops_statuses=OPS_STATUSES,
            archived_reasons=ARCHIVED_REASONS,
            custom_values={},
            draft_model_name="",
            draft_item_type="asset",
            draft_manufacturer="",
        )

    @flask_app.route("/inventory/items/<int:item_id>")
    @login_required
    def inventory_item_detail(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        if item.deleted_at:
            flash("This item was deleted.", "error")
            return redirect(url_for("inventory_items"))
        mo = r.SchoolAssetModel.query.get(item.model_id)
        cfs = (
            r.SchoolAssetCustomField.query.filter_by(model_id=item.model_id)
            .order_by(r.SchoolAssetCustomField.sort_index)
            .all()
        )
        try:
            cv = json.loads(item.custom_values_json or "{}")
        except Exception:
            cv = {}
        oc = open_checkout(r, item.id)
        assignee = r.User.query.get(oc.assignee_user_id) if oc else None
        history = (
            r.SchoolAssetActivity.query.filter_by(item_id=item.id)
            .order_by(r.SchoolAssetActivity.created_at.desc())
            .limit(100)
            .all()
        )
        checkouts = (
            r.SchoolAssetCheckout.query.filter_by(item_id=item.id)
            .order_by(r.SchoolAssetCheckout.checked_out_at.desc())
            .limit(50)
            .all()
        )
        uids = {c.assignee_user_id for c in checkouts} | {h.actor_user_id for h in history}
        users_map = {u.id: u for u in r.User.query.filter(r.User.id.in_(uids)).all()} if uids else {}
        maint = (
            r.SchoolAssetMaintenance.query.filter_by(item_id=item.id)
            .order_by(r.SchoolAssetMaintenance.serviced_at.desc())
            .limit(30)
            .all()
        )
        staff = assignable_staff(r)
        ext_url = ""
        try:
            p = urlparse(request.host_url)
            ext_url = f"{p.scheme}://{p.netloc}{url_for('inventory_scan_token', token=item.scan_token)}"
        except Exception:
            pass
        return render_template(
            "inventory/item_detail.html",
            item=item,
            model=mo,
            custom_fields=cfs,
            custom_values=cv,
            open_checkout=oc,
            assignee=assignee,
            status_label=effective_status_label(item, oc),
            history=history,
            checkouts=checkouts,
            maintenance=maint,
            staff_users=staff,
            users_map=users_map,
            requestable=effective_requestable(item, mo),
            item_types=ITEM_TYPES,
            ops_statuses=OPS_STATUSES,
            ext_scan_url=ext_url,
        )

    @flask_app.route("/inventory/items/<int:item_id>/edit", methods=["GET", "POST"])
    @login_required
    def inventory_item_edit(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        if item.deleted_at:
            abort(404)
        models = (
            r.SchoolAssetModel.query.order_by(r.SchoolAssetModel.name).limit(500).all()
        )
        cfs = (
            r.SchoolAssetCustomField.query.filter_by(model_id=item.model_id)
            .order_by(r.SchoolAssetCustomField.sort_index)
            .all()
        )
        try:
            cv = json.loads(item.custom_values_json or "{}")
        except Exception:
            cv = {}
        if request.method == "POST":
            tag = (request.form.get("tag") or "").strip()
            dup = (
                r.SchoolAssetItem.query.filter(
                    r.SchoolAssetItem.tag == tag, r.SchoolAssetItem.id != item.id
                ).first()
            )
            if dup:
                flash("Another item already uses that tag.", "error")
                return redirect(url_for("inventory_item_edit", item_id=item.id))
            item.tag = tag
            sn = (request.form.get("serial_number") or "").strip() or None
            item.serial_number = sn[:120] if sn else None
            item.physical_location = (
                request.form.get("physical_location") or ""
            ).strip() or None
            item.notes = (request.form.get("notes") or "").strip() or None
            item.ops_status = (request.form.get("ops_status") or item.ops_status).strip()
            if item.ops_status not in OPS_STATUSES:
                item.ops_status = "ready"
            mo = r.SchoolAssetModel.query.get(item.model_id)
            if consumable_bulk(mo):
                item.quantity_on_hand = max(
                    0, int(request.form.get("quantity_on_hand") or 0)
                )
            ro = request.form.get("req_override") or ""
            if ro == "":
                item.is_requestable_override = None
            elif ro == "1":
                item.is_requestable_override = True
            else:
                item.is_requestable_override = False
            if item.ops_status != "archived":
                item.archived_reason = None
            else:
                ar = (request.form.get("archived_reason") or "").strip()
                item.archived_reason = ar if ar in ARCHIVED_REASONS else None
            cv_post = {}
            for cf in cfs:
                key = cf.field_key
                raw = (request.form.get(f"cf_{key}") or "").strip()
                if cf.field_type == "bool":
                    cv_post[key] = bool(request.form.get(f"cf_{key}"))
                elif cf.field_type == "number":
                    cv_post[key] = float(raw) if raw else None
                else:
                    cv_post[key] = raw or None
            item.custom_values_json = json.dumps(cv_post)
            item.updated_at = datetime.utcnow()
            activity(
                item.id,
                "updated",
                f"Updated {item.tag}",
                {"ops_status": item.ops_status},
            )
            r.db.session.commit()
            flash("Saved.", "success")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        return render_template(
            "inventory/item_form.html",
            models=models,
            item=item,
            custom_fields=cfs,
            preset_model=None,
            item_types=ITEM_TYPES,
            ops_statuses=OPS_STATUSES,
            archived_reasons=ARCHIVED_REASONS,
            custom_values=cv,
            draft_model_name="",
            draft_item_type="asset",
            draft_manufacturer="",
        )

    @flask_app.route("/inventory/items/<int:item_id>/checkout", methods=["POST"])
    @login_required
    def inventory_checkout(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        if item.deleted_at or item.ops_status == "archived":
            flash("Cannot check out archived or deleted items.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        if open_checkout(r, item.id):
            flash("Item already has an open checkout.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        mo = r.SchoolAssetModel.query.get(item.model_id)
        assignee = int(request.form.get("assignee_user_id") or 0)
        if not r.User.query.get(assignee):
            flash("Select a valid assignee.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        qty = max(1, int(request.form.get("quantity") or 1))
        if consumable_bulk(mo):
            if item.quantity_on_hand < qty:
                flash("Not enough stock on hand.", "error")
                return redirect(url_for("inventory_item_detail", item_id=item.id))
            item.quantity_on_hand -= qty
        else:
            qty = 1
        sig = (request.form.get("acceptance_signature") or "").strip()
        if sig.startswith("data:image"):
            sig = sig.split(",", 1)[-1][:500_000]
        else:
            sig = sig[:500_000] if sig else None
        due_raw = (request.form.get("expected_return_at") or "").strip()
        due = None
        if due_raw:
            try:
                due = datetime.fromisoformat(due_raw)
            except Exception:
                due = None
        co = r.SchoolAssetCheckout(
            item_id=item.id,
            assignee_user_id=assignee,
            checked_out_by_user_id=r.current_user.id,
            quantity=qty,
            expected_return_at=due,
            acceptance_signature_png=sig,
            checkout_notes=(request.form.get("checkout_notes") or "").strip()[:500]
            or None,
        )
        r.db.session.add(co)
        assignee_u = r.User.query.get(assignee)
        activity(
            item.id,
            "checkout",
            f"Checked out to {assignee_u.username}",
            {"qty": qty, "due": due_raw or None},
        )
        r.db.session.commit()
        flash("Checked out.", "success")
        return redirect(url_for("inventory_item_detail", item_id=item.id))

    @flask_app.route("/inventory/items/<int:item_id>/checkin", methods=["POST"])
    @login_required
    def inventory_checkin(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        co = open_checkout(r, item.id)
        if not co:
            flash("No open checkout for this item.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        mo = r.SchoolAssetModel.query.get(item.model_id)
        if consumable_bulk(mo):
            rqty = co.quantity
        else:
            rqty = max(1, int(request.form.get("return_quantity") or co.quantity))
            rqty = min(rqty, co.quantity)
        co.checkin_at = datetime.utcnow()
        if consumable_bulk(mo):
            item.quantity_on_hand += rqty
        assignee_u = r.User.query.get(co.assignee_user_id)
        activity(
            item.id,
            "checkin",
            f"Checked in from {assignee_u.username}",
            {"qty": rqty},
        )
        r.db.session.commit()
        flash("Checked in.", "success")
        return redirect(url_for("inventory_item_detail", item_id=item.id))

    @flask_app.route("/inventory/items/<int:item_id>/delete", methods=["POST"])
    @login_required
    def inventory_item_soft_delete(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        if open_checkout(r, item.id):
            flash("Check the item in before deleting.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        item.deleted_at = datetime.utcnow()
        tid = item.id
        tt = item.tag
        activity(tid, "deleted", f"Soft-deleted item {tt}", {"id": tid})
        r.db.session.commit()
        flash("Item removed from active inventory.", "success")
        return redirect(url_for("inventory_items"))

    @flask_app.route("/inventory/items/<int:item_id>/maintenance", methods=["POST"])
    @login_required
    def inventory_maintenance_add(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        summ = (request.form.get("summary") or "").strip()
        if not summ:
            flash("Summary required.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        cost = request.form.get("cost_cents")
        try:
            cost_i = int(cost) if cost else None
        except Exception:
            cost_i = None
        m = r.SchoolAssetMaintenance(
            item_id=item.id,
            logged_by_user_id=r.current_user.id,
            summary=summ[:200],
            detail=(request.form.get("detail") or "").strip() or None,
            cost_cents=cost_i,
        )
        r.db.session.add(m)
        activity(item.id, "maintenance", summ, {})
        r.db.session.commit()
        flash("Maintenance logged.", "success")
        return redirect(url_for("inventory_item_detail", item_id=item.id))

    @flask_app.route("/inventory/items/<int:item_id>/request", methods=["POST"])
    @login_required
    def inventory_request_item(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        mo = r.SchoolAssetModel.query.get(item.model_id)
        if not effective_requestable(item, mo):
            flash("This item is not marked as requestable.", "error")
            return redirect(url_for("inventory_item_detail", item_id=item.id))
        q = max(1, int(request.form.get("quantity") or 1))
        req = r.SchoolAssetRequest(
            requester_user_id=r.current_user.id,
            item_id=item.id,
            model_id=None,
            quantity=q,
            notes=(request.form.get("notes") or "").strip() or None,
        )
        r.db.session.add(req)
        activity(item.id, "request", f"Requested {q} × {item.tag}", {})
        r.db.session.commit()
        flash("Request submitted.", "success")
        return redirect(url_for("inventory_item_detail", item_id=item.id))

    @flask_app.route("/inventory/requests")
    @login_required
    def inventory_requests_list():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        rows = (
            r.SchoolAssetRequest.query.filter_by(status="pending")
            .order_by(r.SchoolAssetRequest.created_at.desc())
            .limit(200)
            .all()
        )
        enriched = []
        for rq in rows:
            req_u = r.User.query.get(rq.requester_user_id)
            tag = None
            if rq.item_id:
                it = r.SchoolAssetItem.query.get(rq.item_id)
                tag = it.tag if it else None
            enriched.append((rq, req_u, tag))
        return render_template("inventory/requests_list.html", enriched=enriched)

    @flask_app.route("/inventory/requests/<int:rid>/decide", methods=["POST"])
    @login_required
    def inventory_request_decide(rid):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        req = r.SchoolAssetRequest.query.get_or_404(rid)
        if req.status != "pending":
            flash("Already decided.", "error")
            return redirect(url_for("inventory_requests_list"))
        action = (request.form.get("action") or "").strip().lower()
        req.decided_by_user_id = r.current_user.id
        req.decided_at = datetime.utcnow()
        if action == "approve":
            req.status = "approved"
            if req.item_id:
                activity(
                    req.item_id,
                    "request_approved",
                    "Request approved",
                    {"request_id": req.id},
                )
        else:
            req.status = "denied"
            if req.item_id:
                activity(
                    req.item_id,
                    "request_denied",
                    "Request denied",
                    {"request_id": req.id},
                )
        r.db.session.commit()
        flash("Updated request.", "success")
        return redirect(url_for("inventory_requests_list"))

    # ---- Models & custom fields -----------------------------------------------

    @flask_app.route("/inventory/models")
    @login_required
    def inventory_models_list():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        rows = (
            r.SchoolAssetModel.query.order_by(r.SchoolAssetModel.name).limit(500).all()
        )
        cats = r.SchoolAssetCategory.query.order_by(
            r.SchoolAssetCategory.sort_index, r.SchoolAssetCategory.name
        ).all()
        return render_template(
            "inventory/models_list.html", rows=rows, categories=cats, item_types=ITEM_TYPES
        )

    @flask_app.route("/inventory/models/new", methods=["GET", "POST"])
    @login_required
    def inventory_model_new():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        cats = r.SchoolAssetCategory.query.order_by(
            r.SchoolAssetCategory.sort_index, r.SchoolAssetCategory.name
        ).all()
        if request.method == "POST":
            it = (request.form.get("item_type") or "asset").strip().lower()
            if it not in ITEM_TYPES:
                it = "asset"
            _lst_raw = (request.form.get("low_stock_threshold") or "").strip()
            try:
                _thr = int(_lst_raw) if _lst_raw else None
            except ValueError:
                _thr = None
            m = r.SchoolAssetModel(
                category_id=int(request.form.get("category_id") or 0) or None,
                item_type=it,
                name=(request.form.get("name") or "").strip(),
                manufacturer=(request.form.get("manufacturer") or "").strip() or None,
                description=(request.form.get("description") or "").strip() or None,
                low_stock_threshold=_thr,
                default_location=(request.form.get("default_location") or "").strip()
                or None,
                is_requestable=bool(request.form.get("is_requestable")),
            )
            if not m.name:
                flash("Name required.", "error")
                return render_template(
                    "inventory/model_form.html", model=None, categories=cats, item_types=ITEM_TYPES
                )
            r.db.session.add(m)
            activity(None, "model_created", f"Model {m.name}", {})
            r.db.session.commit()
            flash("Model created.", "success")
            return redirect(url_for("inventory_models_list"))
        return render_template(
            "inventory/model_form.html", model=None, categories=cats, item_types=ITEM_TYPES
        )

    @flask_app.route("/inventory/models/<int:mid>/edit", methods=["GET", "POST"])
    @login_required
    def inventory_model_edit(mid):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        m = r.SchoolAssetModel.query.get_or_404(mid)
        cats = r.SchoolAssetCategory.query.order_by(
            r.SchoolAssetCategory.sort_index, r.SchoolAssetCategory.name
        ).all()
        cfs = (
            r.SchoolAssetCustomField.query.filter_by(model_id=m.id)
            .order_by(r.SchoolAssetCustomField.sort_index)
            .all()
        )
        if request.method == "POST":
            it = (request.form.get("item_type") or m.item_type).strip().lower()
            if it not in ITEM_TYPES:
                it = m.item_type
            m.item_type = it
            m.category_id = int(request.form.get("category_id") or 0) or None
            m.name = (request.form.get("name") or "").strip()
            m.manufacturer = (request.form.get("manufacturer") or "").strip() or None
            m.description = (request.form.get("description") or "").strip() or None
            lst = request.form.get("low_stock_threshold")
            try:
                m.low_stock_threshold = int(lst) if lst else None
            except Exception:
                m.low_stock_threshold = None
            m.default_location = (request.form.get("default_location") or "").strip() or None
            m.is_requestable = bool(request.form.get("is_requestable"))
            if not m.name:
                flash("Name required.", "error")
                return redirect(url_for("inventory_model_edit", mid=mid))
            activity(None, "model_updated", f"Model {m.name}", {})
            r.db.session.commit()
            flash("Model saved.", "success")
            return redirect(url_for("inventory_model_edit", mid=mid))
        return render_template(
            "inventory/model_form.html",
            model=m,
            categories=cats,
            custom_fields=cfs,
            item_types=ITEM_TYPES,
        )

    @flask_app.route("/inventory/models/<int:mid>/custom-field", methods=["POST"])
    @login_required
    def inventory_model_custom_field(mid):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        r.SchoolAssetModel.query.get_or_404(mid)
        key = (request.form.get("field_key") or "").strip().lower().replace(" ", "_")
        label = (request.form.get("field_label") or "").strip()
        ftype = (request.form.get("field_type") or "text").strip()
        if ftype not in ("text", "number", "bool", "date"):
            ftype = "text"
        if not key or not label:
            flash("Field key and label required.", "error")
            return redirect(url_for("inventory_model_edit", mid=mid))
        if r.SchoolAssetCustomField.query.filter_by(
            model_id=mid, field_key=key
        ).first():
            flash("That field key already exists.", "error")
            return redirect(url_for("inventory_model_edit", mid=mid))
        cf = r.SchoolAssetCustomField(
            model_id=mid,
            field_key=key[:64],
            field_label=label[:120],
            field_type=ftype,
            is_required=bool(request.form.get("is_required")),
            sort_index=int(request.form.get("sort_index") or 0),
        )
        r.db.session.add(cf)
        r.db.session.commit()
        flash("Custom field added.", "success")
        return redirect(url_for("inventory_model_edit", mid=mid))

    @flask_app.route("/inventory/categories/new", methods=["POST"])
    @login_required
    def inventory_category_new():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Category name required.", "error")
            return redirect(url_for("inventory_models_list"))
        if r.SchoolAssetCategory.query.filter_by(name=name).first():
            flash("Category already exists.", "error")
            return redirect(url_for("inventory_models_list"))
        r.db.session.add(r.SchoolAssetCategory(name=name))
        r.db.session.commit()
        flash("Category added.", "success")
        return redirect(url_for("inventory_models_list"))

    # ---- Reports & QR ---------------------------------------------------------

    @flask_app.route("/inventory/reports/expected-checkin")
    @login_required
    def inventory_report_expected():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        rows = (
            r.SchoolAssetCheckout.query.filter(
                r.SchoolAssetCheckout.checkin_at.is_(None),
                r.SchoolAssetCheckout.expected_return_at.isnot(None),
            )
            .order_by(r.SchoolAssetCheckout.expected_return_at)
            .limit(500)
            .all()
        )
        out = []
        for co in rows:
            it = r.SchoolAssetItem.query.get(co.item_id)
            if not it or it.deleted_at:
                continue
            ou = r.User.query.get(co.assignee_user_id)
            out.append((co, it, ou))
        return render_template(
            "inventory/report_expected.html", rows=out, now=datetime.utcnow()
        )

    @flask_app.route("/inventory/reports/low-stock")
    @login_required
    def inventory_report_low_stock():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        Am, Ai = r.SchoolAssetModel, r.SchoolAssetItem
        low = []
        for m in Am.query.filter(Am.item_type == "consumable").all():
            thr = m.low_stock_threshold
            if thr is None:
                continue
            total = (
                r.db.session.query(r.db.func.coalesce(r.db.func.sum(Ai.quantity_on_hand), 0))
                .filter(Ai.model_id == m.id, Ai.deleted_at.is_(None))
                .scalar()
            )
            if int(total or 0) <= int(thr):
                low.append((m, int(total or 0), int(thr)))
        return render_template("inventory/report_low_stock.html", rows=low)

    @flask_app.route("/inventory/items/<int:item_id>/qr.png")
    @login_required
    def inventory_item_qr_png(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        import qrcode

        p = urlparse(request.host_url)
        url = f"{p.scheme}://{p.netloc}{url_for('inventory_scan_token', token=item.scan_token)}"
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=12,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(buf.getvalue(), mimetype="image/png")

    @flask_app.route("/inventory/items/<int:item_id>/print-label")
    @login_required
    def inventory_item_print_label(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        if item.deleted_at:
            abort(404)
        mo = r.SchoolAssetModel.query.get(item.model_id)
        p = urlparse(request.host_url)
        ext_scan_url = f"{p.scheme}://{p.netloc}{url_for('inventory_scan_token', token=item.scan_token)}"
        return render_template(
            "inventory/print_label.html",
            item=item,
            model=mo,
            ext_scan_url=ext_scan_url,
        )

    @flask_app.route("/inventory/items/<int:item_id>/label.pdf")
    @login_required
    def inventory_item_label_pdf(item_id):
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        item = r.SchoolAssetItem.query.get_or_404(item_id)
        mo = r.SchoolAssetModel.query.get(item.model_id)
        import qrcode
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        p = urlparse(request.host_url)
        url = f"{p.scheme}://{p.netloc}{url_for('inventory_scan_token', token=item.scan_token)}"
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qbuf = io.BytesIO()
        qr_img.save(qbuf, format="PNG")
        qbuf.seek(0)

        label_w, label_h = 4 * inch, 2.75 * inch
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(label_w, label_h))
        margin = 0.22 * inch
        qr_size = 2.05 * inch
        x_qr = label_w - margin - qr_size
        y_qr = margin
        c.drawImage(ImageReader(qbuf), x_qr, y_qr, width=qr_size, height=qr_size)

        left_w = x_qr - margin * 2
        y = label_h - margin - 14
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin, y, (item.tag or "")[:56])
        y -= 18
        c.setFont("Helvetica", 9)
        sn = getattr(item, "serial_number", None)
        if sn:
            c.drawString(margin, y, f"Serial: {str(sn)[:64]}")
            y -= 13
        c.setFont("Helvetica", 8)
        if mo and mo.name:
            name = mo.name
            max_chars = max(28, int(left_w / 4))
            lines = []
            while len(name) > max_chars:
                lines.append(name[:max_chars])
                name = name[max_chars:]
            if name:
                lines.append(name)
            for ln in lines[:3]:
                c.drawString(margin, y, ln)
                y -= 11
            y -= 2
            c.drawString(margin, y, f"Type: {mo.item_type or ''}")
            y -= 11
        c.setFont("Helvetica", 6)
        tiny = url if len(url) < 72 else url[:69] + "…"
        c.drawString(margin, margin + 2, tiny)

        c.showPage()
        c.save()
        buf.seek(0)
        return Response(
            buf.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="label-{item.tag}.pdf"'
            },
        )

    @flask_app.route("/inventory/export.csv")
    @login_required
    def inventory_export_csv():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        Ai, Am = r.SchoolAssetItem, r.SchoolAssetModel
        rows = Ai.query.filter(Ai.deleted_at.is_(None)).order_by(Ai.tag).limit(5000)
        si = io.StringIO()
        w = csv.writer(si)
        w.writerow(
            [
                "tag",
                "serial_number",
                "item_type",
                "model_name",
                "qty_on_hand",
                "ops_status",
                "archived_reason",
                "location",
                "notes",
                "scan_token",
            ]
        )
        for it in rows:
            mo = Am.query.get(it.model_id)
            w.writerow(
                [
                    it.tag,
                    it.serial_number or "",
                    mo.item_type if mo else "",
                    mo.name if mo else "",
                    it.quantity_on_hand,
                    it.ops_status,
                    it.archived_reason or "",
                    it.physical_location or "",
                    (it.notes or "").replace("\n", " "),
                    it.scan_token,
                ]
            )
        return Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=school_assets.csv"},
        )

    @flask_app.route("/inventory/import", methods=["GET", "POST"])
    @login_required
    def inventory_import_csv():
        r = root()
        g = r.require_inventory_staff()
        if g:
            return g
        Am, Ai = r.SchoolAssetModel, r.SchoolAssetItem
        if request.method == "POST":
            raw = request.form.get("csv_data") or ""
            if request.files.get("file"):
                raw = request.files["file"].read().decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(raw))
            n_ok = n_err = 0
            for row in reader:
                tag = (row.get("tag") or "").strip()
                model_name = (row.get("model_name") or "").strip()
                if not tag or not model_name:
                    n_err += 1
                    continue
                mo = Am.query.filter(Am.name == model_name).first()
                if not mo:
                    n_err += 1
                    continue
                if Ai.query.filter_by(tag=tag).first():
                    n_err += 1
                    continue
                try:
                    qty = int(row.get("qty_on_hand") or row.get("quantity_on_hand") or 1)
                except Exception:
                    qty = 1
                ops = (row.get("ops_status") or "ready").strip()
                if ops not in OPS_STATUSES:
                    ops = "ready"
                sn = (row.get("serial_number") or "").strip() or None
                if sn:
                    sn = sn[:120]
                item = Ai(
                    model_id=mo.id,
                    tag=tag,
                    serial_number=sn,
                    scan_token=secrets.token_urlsafe(24)[:64],
                    quantity_on_hand=max(0, qty),
                    ops_status=ops,
                    physical_location=(row.get("location") or "").strip() or mo.default_location,
                    notes=(row.get("notes") or "").strip() or None,
                )
                r.db.session.add(item)
                r.db.session.flush()
                activity(item.id, "imported", f"Imported {tag}", {})
                n_ok += 1
            r.db.session.commit()
            flash(f"Import complete: {n_ok} created, {n_err} skipped.", "success")
            return redirect(url_for("inventory_items"))
        return render_template("inventory/import_form.html")
