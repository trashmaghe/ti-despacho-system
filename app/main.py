from __future__ import annotations

from datetime import datetime

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from .extensions import db
from .models import ComputerRecord
from .utils import export_records_csv, generate_reference_code


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    stats = {
        "total": ComputerRecord.query.count(),
        "em_manutencao": ComputerRecord.query.filter_by(status=ComputerRecord.STATUS_EM_MANUTENCAO).count(),
        "pronto": ComputerRecord.query.filter_by(status=ComputerRecord.STATUS_PRONTO).count(),
        "entregue": ComputerRecord.query.filter_by(status=ComputerRecord.STATUS_ENTREGUE).count(),
    }
    latest_records = ComputerRecord.query.order_by(ComputerRecord.created_at.desc()).limit(5).all()
    return render_template("dashboard.html", stats=stats, latest_records=latest_records)


@main_bp.route("/equipamentos")
@login_required
def records_list():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    query = ComputerRecord.query

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                ComputerRecord.responsible_name.ilike(like_term),
                ComputerRecord.asset_tag.ilike(like_term),
                ComputerRecord.serial_number.ilike(like_term),
                ComputerRecord.department.ilike(like_term),
                ComputerRecord.reference_code.ilike(like_term),
            )
        )

    if status:
        query = query.filter(ComputerRecord.status == status)

    pagination = query.order_by(ComputerRecord.created_at.desc()).paginate(
        page=page,
        per_page=current_app.config.get("ITEMS_PER_PAGE", 10),
        error_out=False,
    )

    return render_template(
        "equipment/list.html",
        pagination=pagination,
        records=pagination.items,
        search=search,
        status=status,
        statuses=ComputerRecord.STATUS_CHOICES,
    )


@main_bp.route("/equipamentos/exportar")
@login_required
def export_records():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = ComputerRecord.query
    if search:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                ComputerRecord.responsible_name.ilike(like_term),
                ComputerRecord.asset_tag.ilike(like_term),
                ComputerRecord.serial_number.ilike(like_term),
                ComputerRecord.department.ilike(like_term),
                ComputerRecord.reference_code.ilike(like_term),
            )
        )
    if status:
        query = query.filter(ComputerRecord.status == status)

    records = query.order_by(ComputerRecord.created_at.desc()).all()
    return export_records_csv(records)


@main_bp.route("/equipamentos/novo", methods=["GET", "POST"])
@login_required
def create_record():
    if request.method == "POST":
        form_data, errors = _validate_receipt_form(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "equipment/form.html",
                record=None,
                statuses=ComputerRecord.STATUS_CHOICES,
                form_data=request.form,
            )

        record = ComputerRecord(
            reference_code=generate_reference_code(),
            responsible_name=form_data["responsible_name"],
            department=form_data["department"],
            asset_tag=form_data["asset_tag"],
            brand_model=form_data["brand_model"],
            serial_number=form_data["serial_number"],
            issue_reported=form_data["issue_reported"],
            accessories=form_data["accessories"],
            received_date=form_data["received_date"],
            received_by=form_data["received_by"],
            notes=form_data["notes"],
            status=form_data["status"],
        )
        db.session.add(record)
        db.session.commit()
        flash("Equipamento recebido e cadastrado com sucesso.", "success")
        return redirect(url_for("main.record_detail", record_id=record.id))

    return render_template(
        "equipment/form.html",
        record=None,
        statuses=ComputerRecord.STATUS_CHOICES,
        form_data=None,
    )


@main_bp.route("/equipamentos/<int:record_id>")
@login_required
def record_detail(record_id: int):
    record = ComputerRecord.query.get_or_404(record_id)
    return render_template("equipment/detail.html", record=record)


@main_bp.route("/equipamentos/<int:record_id>/editar", methods=["GET", "POST"])
@login_required
def edit_record(record_id: int):
    record = ComputerRecord.query.get_or_404(record_id)

    if request.method == "POST":
        form_data, errors = _validate_receipt_form(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "equipment/form.html",
                record=record,
                statuses=ComputerRecord.STATUS_CHOICES,
                form_data=request.form,
            )

        record.responsible_name = form_data["responsible_name"]
        record.department = form_data["department"]
        record.asset_tag = form_data["asset_tag"]
        record.brand_model = form_data["brand_model"]
        record.serial_number = form_data["serial_number"]
        record.issue_reported = form_data["issue_reported"]
        record.accessories = form_data["accessories"]
        record.received_date = form_data["received_date"]
        record.received_by = form_data["received_by"]
        record.notes = form_data["notes"]
        record.status = form_data["status"]

        db.session.commit()
        flash("Registro atualizado com sucesso.", "success")
        return redirect(url_for("main.record_detail", record_id=record.id))

    return render_template(
        "equipment/form.html",
        record=record,
        statuses=ComputerRecord.STATUS_CHOICES,
        form_data=record,
    )


@main_bp.route("/equipamentos/<int:record_id>/despacho", methods=["GET", "POST"])
@login_required
def dispatch_record(record_id: int):
    record = ComputerRecord.query.get_or_404(record_id)

    if request.method == "POST":
        errors = []
        dispatched_date_raw = request.form.get("dispatched_date", "").strip()
        withdrawn_by = request.form.get("withdrawn_by", "").strip()
        delivered_by = request.form.get("delivered_by", "").strip()
        dispatch_notes = request.form.get("dispatch_notes", "").strip()
        final_status = request.form.get("final_status", ComputerRecord.STATUS_ENTREGUE).strip()

        try:
            dispatched_date = datetime.strptime(dispatched_date_raw, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Informe uma data de saída válida.")
            dispatched_date = None

        if not withdrawn_by:
            errors.append("Informe quem retirou o equipamento.")
        if not delivered_by:
            errors.append("Informe o técnico responsável pela entrega.")
        if final_status not in {ComputerRecord.STATUS_PRONTO, ComputerRecord.STATUS_ENTREGUE}:
            errors.append("O status final do despacho deve ser 'Pronto para devolução' ou 'Entregue'.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("equipment/dispatch.html", record=record)

        record.dispatched_date = dispatched_date
        record.withdrawn_by = withdrawn_by
        record.delivered_by = delivered_by
        record.dispatch_notes = dispatch_notes
        record.status = final_status

        db.session.commit()
        flash("Despacho registrado com sucesso.", "success")
        return redirect(url_for("main.record_detail", record_id=record.id))

    return render_template("equipment/dispatch.html", record=record)


@main_bp.route("/equipamentos/<int:record_id>/excluir", methods=["POST"])
@login_required
def delete_record(record_id: int):
    record = ComputerRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash("Registro excluído com sucesso.", "info")
    return redirect(url_for("main.records_list"))


@main_bp.route("/equipamentos/<int:record_id>/comprovante-recebimento")
@login_required
def print_receipt(record_id: int):
    record = ComputerRecord.query.get_or_404(record_id)
    return render_template("equipment/print_receipt.html", record=record)


@main_bp.route("/equipamentos/<int:record_id>/comprovante-entrega")
@login_required
def print_dispatch(record_id: int):
    record = ComputerRecord.query.get_or_404(record_id)
    if not record.dispatched_date:
        abort(404)
    return render_template("equipment/print_dispatch.html", record=record)


@main_bp.app_errorhandler(404)
def not_found(_error):
    return render_template("errors/404.html"), 404


@main_bp.app_errorhandler(500)
def server_error(_error):
    db.session.rollback()
    return render_template("errors/500.html"), 500


def _validate_receipt_form(form) -> tuple[dict, list[str]]:
    errors: list[str] = []

    responsible_name = form.get("responsible_name", "").strip()
    department = form.get("department", "").strip()
    asset_tag = form.get("asset_tag", "").strip()
    brand_model = form.get("brand_model", "").strip()
    serial_number = form.get("serial_number", "").strip()
    issue_reported = form.get("issue_reported", "").strip()
    accessories = form.get("accessories", "").strip()
    received_date_raw = form.get("received_date", "").strip()
    received_by = form.get("received_by", "").strip()
    notes = form.get("notes", "").strip()
    status = form.get("status", ComputerRecord.STATUS_RECEBIDO).strip()

    for label, value in [
        ("Nome do responsável", responsible_name),
        ("Setor", department),
        ("Patrimônio", asset_tag),
        ("Marca / modelo", brand_model),
        ("Problema relatado", issue_reported),
        ("Data de recebimento", received_date_raw),
        ("Técnico responsável pelo recebimento", received_by),
    ]:
        if not value:
            errors.append(f"O campo '{label}' é obrigatório.")

    try:
        received_date = datetime.strptime(received_date_raw, "%Y-%m-%d").date()
    except ValueError:
        received_date = None
        errors.append("Informe uma data de recebimento válida.")

    if status not in ComputerRecord.STATUS_CHOICES:
        errors.append("Selecione um status válido.")

    return (
        {
            "responsible_name": responsible_name,
            "department": department,
            "asset_tag": asset_tag,
            "brand_model": brand_model,
            "serial_number": serial_number,
            "issue_reported": issue_reported,
            "accessories": accessories,
            "received_date": received_date,
            "received_by": received_by,
            "notes": notes,
            "status": status,
        },
        errors,
    )
