from flask import Flask

from config import Config

from .auth import auth_bp
from .extensions import db, login_manager
from .main import main_bp
from .models import ComputerRecord, User
from .users import users_bp
from .utils import run_startup_migrations, seed_admin, status_badge_class


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)

    with app.app_context():
        db.create_all()
        run_startup_migrations(db)
        seed_admin(app, db, User)

    @app.context_processor
    def inject_globals():
        return {
            "app_name": app.config.get("APP_NAME", "Controle TI"),
            "status_choices": ComputerRecord.STATUS_CHOICES,
            "status_badge_class": status_badge_class,
        }

    return app
