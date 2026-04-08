import os
import warnings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _running_on_railway() -> bool:
    return any(
        os.getenv(key)
        for key in (
            "RAILWAY_PROJECT_ID",
            "RAILWAY_ENVIRONMENT",
            "RAILWAY_SERVICE_ID",
            "RAILWAY_STATIC_URL",
        )
    )


def _default_sqlite_url() -> str:
    if _running_on_railway():
        fallback_dir = Path(os.getenv("SQLITE_STORAGE_DIR", "/tmp/controle-ti"))
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{(fallback_dir / 'app.db').as_posix()}"

    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{(INSTANCE_DIR / 'app.db').as_posix()}"


def _normalize_database_url(url: str | None) -> str:
    if not url or not url.strip():
        if _running_on_railway():
            warnings.warn(
                "DATABASE_URL não foi informada no Railway. O sistema vai iniciar com SQLite temporário em /tmp, sem persistência garantida.",
                RuntimeWarning,
            )
        return _default_sqlite_url()

    normalized = url.strip().strip('"').strip("'")
    normalized = normalized.replace("postgres://", "postgresql://", 1)

    if normalized.startswith("postgresql://") and "sslmode=" not in normalized and _running_on_railway():
        separator = "&" if "?" in normalized else "?"
        normalized = f"{normalized}{separator}sslmode=require"

    return normalized


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_FULL_NAME = os.getenv("ADMIN_FULL_NAME", "Administrador")
    SYNC_ADMIN_PASSWORD_ON_STARTUP = _is_truthy(os.getenv("SYNC_ADMIN_PASSWORD_ON_STARTUP", "false"))

    APP_NAME = os.getenv("APP_NAME", "Controle TI")
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))
    DEFAULT_THEME_ID = os.getenv("DEFAULT_THEME_ID", "railway-night")
