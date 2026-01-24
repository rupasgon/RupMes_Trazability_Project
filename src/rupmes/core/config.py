import os


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return database_url


def _get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def get_frontend_origins() -> list[str]:
    value = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:3000")
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def get_cookie_secure() -> bool:
    return _get_env_bool("COOKIE_SECURE", False)


def get_cookie_samesite() -> str:
    return os.getenv("COOKIE_SAMESITE", "lax")


def get_session_ttl_minutes() -> int:
    value = os.getenv("SESSION_TTL_MINUTES", "480")
    try:
        return int(value)
    except ValueError:
        return 480


def get_session_cookie_name() -> str:
    return os.getenv("SESSION_COOKIE_NAME", "rupmes_session")


def get_csrf_cookie_name() -> str:
    return os.getenv("CSRF_COOKIE_NAME", "rupmes_csrf")


def get_default_tenant_id() -> str:
    return os.getenv("DEFAULT_TENANT_ID", "DEFAULT")


def is_multi_tenant_enabled() -> bool:
    return _get_env_bool("MULTI_TENANT_ENABLED", False)
