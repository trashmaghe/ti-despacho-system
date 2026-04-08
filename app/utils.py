from __future__ import annotations

import csv
import io
from datetime import datetime

from flask import Response

from .models import ComputerRecord


def seed_admin(app, db, User):
    username = app.config["ADMIN_USERNAME"]
    password = app.config["ADMIN_PASSWORD"]

    if not User.query.filter_by(username=username).first():
        admin = User(username=username, is_admin=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()


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
