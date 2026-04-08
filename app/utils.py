from __future__ import annotations

import csv
import io
from datetime import datetime
from functools import wraps

from flask import Response, flash, redirect, url_for
from flask_login import current_user
from sqlalchemy import inspect, text

from .models import ComputerRecord


STATUS_BADGE_MAP = {
    ComputerRecord.STATUS_RECEBIDO: "status-recebido",
    ComputerRecord.STATUS_EM_ANALISE: "status-analise",
    ComputerRecord.STATUS_EM_MANUTENCAO: "status-manutencao",
    ComputerRecord.STATUS_AGUARDANDO_PECA: "status-peca",
    ComputerRecord.STATUS_PRONTO: "status-pronto",
    ComputerRecord.STATUS_ENTREGUE: "status-entregue",
}


def seed_admin(app, db, User):
    username = app.config["ADMIN_USERNAME"]
    password = app.config["ADMIN_PASSWORD"]
    full_name = app.config.get("ADMIN_FULL_NAME", "Administrador")
    sync_password = app.config.get("SYNC_ADMIN_PASSWORD_ON_STARTUP", False)

    admin = User.query.filter_by(username=username).first()
    if not admin:
        admin = User(
            username=username,
            full_name=full_name,
            is_admin=True,
            is_active=True,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return

    changed = False
    if not admin.full_name:
        admin.full_name = full_name
        changed = True
    if not admin.is_admin:
        admin.is_admin = True
        changed = True
    if not admin.is_active:
        admin.is_active = True
        changed = True
    if sync_password and password and not admin.check_password(password):
        admin.set_password(password)
        changed = True
    if changed:
        db.session.commit()


def run_startup_migrations(db) -> None:
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    if "users" in table_names:
        columns = {column["name"] for column in inspector.get_columns("users")}
        migrations = []
        if "full_name" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN full_name VARCHAR(150)")
        if "is_active" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
        if "last_login_at" not in columns:
            migrations.append("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP NULL")

        for statement in migrations:
            db.session.execute(text(statement))
        if migrations:
            db.session.commit()


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            flash("Você não tem permissão para acessar essa área.", "danger")
            return redirect(url_for("main.dashboard"))
        return view_func(*args, **kwargs)

    return wrapper


def status_badge_class(status: str) -> str:
    return STATUS_BADGE_MAP.get(status, "status-default")


def generate_reference_code() -> str:
    while True:
        candidate = f"TI-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        exists = ComputerRecord.query.filter_by(reference_code=candidate).first()
        if not exists:
            return candidate


def export_records_csv(records: list[ComputerRecord]) -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Código",
            "Responsável",
            "Setor",
            "Patrimônio",
            "Marca/Modelo",
            "Número de Série",
            "Problema Relatado",
            "Acessórios",
            "Data de Recebimento",
            "Recebido por",
            "Status",
            "Data de Saída",
            "Retirado por",
            "Entregue por",
        ]
    )

    for record in records:
        writer.writerow(
            [
                record.reference_code,
                record.responsible_name,
                record.department,
                record.asset_tag,
                record.brand_model,
                record.serial_number or "",
                record.issue_reported,
                record.accessories or "",
                record.received_date.strftime("%d/%m/%Y"),
                record.received_by,
                record.status,
                record.dispatched_date.strftime("%d/%m/%Y") if record.dispatched_date else "",
                record.withdrawn_by or "",
                record.delivered_by or "",
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=controle_ti_registros.csv"},
    )
