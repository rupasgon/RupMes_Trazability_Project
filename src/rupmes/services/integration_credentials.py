"""Encryption helpers for credentials configured through the ERP server screen."""

import json

from cryptography.fernet import Fernet, InvalidToken

from rupmes.core.config import get_integration_secrets_key


def _fernet() -> Fernet:
    key = get_integration_secrets_key()
    if not key:
        raise ValueError("INTEGRATION_SECRETS_KEY is not configured")
    try:
        return Fernet(key.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise ValueError("INTEGRATION_SECRETS_KEY is invalid") from exc


def encrypt_oauth_credentials(client_id: str, client_secret: str) -> str:
    payload = json.dumps({"client_id": client_id, "client_secret": client_secret}).encode("utf-8")
    return _fernet().encrypt(payload).decode("utf-8")


def decrypt_oauth_credentials(value: str | None) -> tuple[str, str]:
    if not value:
        raise ValueError("OAuth credentials are not configured")
    try:
        payload = json.loads(_fernet().decrypt(value.encode("utf-8")).decode("utf-8"))
        return payload["client_id"], payload["client_secret"]
    except (InvalidToken, UnicodeDecodeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("Stored OAuth credentials cannot be read") from exc
