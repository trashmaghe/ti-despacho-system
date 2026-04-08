from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .extensions import db
from .models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Usuário ou senha inválidos.", "danger")
            return render_template("auth/login.html")

        if not user.is_active:
            flash("Este usuário está desativado. Procure um administrador.", "danger")
            return render_template("auth/login.html")

        user.last_login_at = datetime.utcnow()
        db.session.commit()
        login_user(user)
        flash("Login realizado com sucesso.", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
