from __future__ import annotations

import base64
import json
import ssl
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib import error, parse, request

from rupmes_connector.config import OracleApexConfig


@dataclass(frozen=True)
class ApexDeliveryResult:
    confirmed: bool
    duplicate: bool
    status_code: int | None
    response_body: str


class OracleApexClient:
    """Small standard-library OAuth client matching TcpToApexBridge's contract."""

    def __init__(self, config: OracleApexConfig):
        self.config = config
        self._token: str | None = None
        self._token_expires_at = datetime.min.replace(tzinfo=timezone.utc)
        self._token_lock = threading.Lock()
        self._ssl_context = None if config.verify_tls else ssl._create_unverified_context()

    def send_lot(self, payload: dict[str, str]) -> ApexDeliveryResult:
        token = self._get_token()
        url = f"{self.config.base_url.rstrip('/')}/{self.config.endpoint.lstrip('/')}"
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        req = request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            },
        )
        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds, context=self._ssl_context) as response:
                raw = response.read().decode("utf-8", errors="replace")
                status = response.status
        except error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"APEX HTTP {exc.code}: {raw}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Cannot reach Oracle APEX: {exc.reason}") from exc

        try:
            parsed: dict[str, Any] = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise RuntimeError("APEX returned invalid JSON") from exc

        message = str(parsed.get("message", "")).strip()
        duplicate = status == 200 and message.casefold() == self.config.duplicate_message.casefold()
        result_id = parsed.get("id")
        confirmed = duplicate or (isinstance(result_id, int) and result_id > 0)
        if not confirmed:
            raise RuntimeError(f"APEX did not confirm the lot: {raw}")
        return ApexDeliveryResult(confirmed=True, duplicate=duplicate, status_code=status, response_body=raw)

    def _get_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._token and now < self._token_expires_at - timedelta(seconds=self.config.token_refresh_buffer_seconds):
            return self._token
        with self._token_lock:
            now = datetime.now(timezone.utc)
            if self._token and now < self._token_expires_at - timedelta(seconds=self.config.token_refresh_buffer_seconds):
                return self._token
            credentials = base64.b64encode(
                f"{self.config.client_id}:{self.config.client_secret}".encode("utf-8")
            ).decode("ascii")
            body = parse.urlencode({"grant_type": "client_credentials"}).encode("ascii")
            req = request.Request(
                url=self.config.token_url,
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            try:
                with request.urlopen(req, timeout=self.config.timeout_seconds, context=self._ssl_context) as response:
                    raw = response.read().decode("utf-8", errors="replace")
            except error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"APEX OAuth HTTP {exc.code}: {raw}") from exc
            except error.URLError as exc:
                raise RuntimeError(f"Cannot reach Oracle OAuth endpoint: {exc.reason}") from exc
            try:
                token_response = json.loads(raw)
                token = str(token_response["access_token"])
                expires_in = int(token_response["expires_in"])
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise RuntimeError("Invalid OAuth token response from APEX") from exc
            self._token = token
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            return token
