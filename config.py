import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


def _normalize_database_url(url: str | None) -> str:
    if not url:
        sqlite_path = INSTANCE_DIR / "app.db"
        return f"sqlite:///{sqlite_path}"

    normalized = url.replace("postgres://", "postgresql://", 1)

    if normalized.startswith("postgresql://") and "sslmode=" not in normalized and "railway" in normalized:
        separator = "&" if "?" in normalized else "?"
        normalized = f"{normalized}{separator}sslmode=require"

    return normalized


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    APP_NAME = os.getenv("APP_NAME", "Controle TI")
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", "10"))
