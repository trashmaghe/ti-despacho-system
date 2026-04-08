from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .extensions import db
from .models import User
from .utils import admin_required


users_bp = Blueprint("users", __name__, url_prefix="/usuarios")


@users_bp.route("/")
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.is_admin.desc(), User.username.asc()).all()
    return render_template("users/list.html", users=users)


@users_bp.route("/novo", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        form_data, errors = _validate_user_form(request.form, creating=True)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("users/form.html", user=None, form_data=request.form)

        user = User(
            username=form_data["username"],
            full_name=form_data["full_name"],
            is_admin=form_data["is_admin"],
            is_active=form_data["is_active"],
        )
        user.set_password(form_data["password"])
        db.session.add(user)
        db.session.commit()
        flash("Usuário criado com sucesso.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", user=None, form_data=None)


@users_bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id: int):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        form_data, errors = _validate_user_form(request.form, creating=False, current_user_id=user.id)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("users/form.html", user=user, form_data=request.form)

        user.username = form_data["username"]
        user.full_name = form_data["full_name"]
        user.is_admin = form_data["is_admin"]
        user.is_active = form_data["is_active"]
        if form_data["password"]:
            user.set_password(form_data["password"])

        if user.id == current_user.id and not user.is_active:
            user.is_active = True
            flash("Seu próprio usuário não pode ser desativado durante a edição.", "warning")

        db.session.commit()
        flash("Usuário atualizado com sucesso.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", user=user, form_data=user)


@users_bp.route("/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id: int):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("Você não pode desativar seu próprio usuário por aqui.", "danger")
        return redirect(url_for("users.list_users"))

    user.is_active = not user.is_active
    db.session.commit()
    flash(
        f"Usuário {'ativado' if user.is_active else 'desativado'} com sucesso.",
        "success",
    )
    return redirect(url_for("users.list_users"))


@users_bp.route("/minha-conta", methods=["GET", "POST"])
@login_required
def my_account():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not full_name:
            errors.append("Informe seu nome completo.")

        if new_password or confirm_password or current_password:
            if not current_user.check_password(current_password):
                errors.append("A senha atual está incorreta.")
            if len(new_password) < 6:
                errors.append("A nova senha deve ter pelo menos 6 caracteres.")
            if new_password != confirm_password:
                errors.append("A confirmação da nova senha não confere.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("users/account.html")

        current_user.full_name = full_name
        if new_password:
            current_user.set_password(new_password)
        db.session.commit()
        flash("Sua conta foi atualizada com sucesso.", "success")
        return redirect(url_for("users.my_account"))

    return render_template("users/account.html")


def _validate_user_form(form, creating: bool, current_user_id: int | None = None) -> tuple[dict, list[str]]:
    errors: list[str] = []

    username = form.get("username", "").strip().lower()
    full_name = form.get("full_name", "").strip()
    password = form.get("password", "")
    confirm_password = form.get("confirm_password", "")
    is_admin = form.get("is_admin") == "on"
    is_active = form.get("is_active") == "on"

    if not username:
        errors.append("Informe o nome de usuário.")
    if not full_name:
        errors.append("Informe o nome completo.")

    existing = User.query.filter(User.username == username)
    if current_user_id:
        existing = existing.filter(User.id != current_user_id)
    if username and existing.first():
        errors.append("Já existe um usuário com esse nome de login.")

    if creating and len(password) < 6:
        errors.append("A senha deve ter pelo menos 6 caracteres.")
    if password and len(password) < 6:
        errors.append("A senha deve ter pelo menos 6 caracteres.")
    if creating and not password:
        errors.append("Informe uma senha inicial para o usuário.")
    if password != confirm_password:
        errors.append("A confirmação de senha não confere.")

    return (
        {
            "username": username,
            "full_name": full_name,
            "password": password,
            "is_admin": is_admin,
            "is_active": is_active,
        },
        errors,
    )
