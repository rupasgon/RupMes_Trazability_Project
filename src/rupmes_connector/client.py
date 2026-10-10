from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request

from rupmes_connector.config import ApiConfig


class ApiClient:
    def __init__(self, config: ApiConfig):
        self.config = config

    def send_report(self, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=f"{self.config.base_url.rstrip('/')}{self.config.endpoint}",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Client-Id": self.config.client_id,
                "X-API-Key": self.config.api_key,
            },
        )

        ssl_context = None
        if not self.config.verify_tls:
            ssl_context = ssl._create_unverified_context()

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds, context=ssl_context) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API error {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Cannot reach API: {exc.reason}") from exc
