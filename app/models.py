from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class ComputerRecord(db.Model):
    __tablename__ = "computer_records"

    STATUS_RECEBIDO = "Recebido"
    STATUS_EM_ANALISE = "Em análise"
    STATUS_EM_MANUTENCAO = "Em manutenção"
    STATUS_AGUARDANDO_PECA = "Aguardando peça"
    STATUS_PRONTO = "Pronto para devolução"
    STATUS_ENTREGUE = "Entregue"

    STATUS_CHOICES = [
        STATUS_RECEBIDO,
        STATUS_EM_ANALISE,
        STATUS_EM_MANUTENCAO,
        STATUS_AGUARDANDO_PECA,
        STATUS_PRONTO,
        STATUS_ENTREGUE,
    ]

    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    responsible_name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(150), nullable=False)
    asset_tag = db.Column(db.String(80), nullable=False, index=True)
    brand_model = db.Column(db.String(150), nullable=False)
    serial_number = db.Column(db.String(120), nullable=True, index=True)
    issue_reported = db.Column(db.Text, nullable=False)
    accessories = db.Column(db.Text, nullable=True)
    received_date = db.Column(db.Date, nullable=False)
    received_by = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(50), nullable=False, default=STATUS_RECEBIDO, index=True)

    dispatched_date = db.Column(db.Date, nullable=True)
    withdrawn_by = db.Column(db.String(150), nullable=True)
    delivered_by = db.Column(db.String(120), nullable=True)
    dispatch_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def can_dispatch(self) -> bool:
        return self.status != self.STATUS_ENTREGUE

    def __repr__(self) -> str:
        return f"<ComputerRecord {self.reference_code}>"
