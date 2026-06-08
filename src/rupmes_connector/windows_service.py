from __future__ import annotations

import json
import logging
import logging.handlers
import sys
import time
from pathlib import Path

from rupmes_connector.config import load_configs
from rupmes_connector.service import ProductionBridgeService

try:  # pragma: no cover - Windows-only runtime dependency
    import servicemanager
    import win32event
    import win32service
    import win32serviceutil
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("pywin32 is required for Windows service support") from exc


DEFAULT_SERVICE_NAME = "RupMesProductionConnectorService"
DEFAULT_DISPLAY_NAME = "RupMes Production Connector"
DEFAULT_DESCRIPTION = "RupMes production gateway service"


def _project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _settings_path() -> Path:
    if getattr(sys, "frozen", False):
        return _project_root() / "service.settings.json"
    return _project_root() / "production_connector" / "windows" / "service.settings.json"


def _load_settings() -> dict:
    path = _settings_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


SETTINGS = _load_settings()


class RupMesProductionConnectorService(win32serviceutil.ServiceFramework):
    _svc_name_ = SETTINGS.get("service_name", DEFAULT_SERVICE_NAME)
    _svc_display_name_ = SETTINGS.get("display_name", DEFAULT_DISPLAY_NAME)
    _svc_description_ = SETTINGS.get("description", DEFAULT_DESCRIPTION)

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.logger = logging.getLogger("rupmes_connector.windows_service")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.logger.info("Stop signal received")
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg(f"{self._svc_name_} starting")
        try:
            self._run_service()
        except Exception as exc:  # pragma: no cover
            self.logger.exception("Windows service failed: %s", exc)
            servicemanager.LogErrorMsg(f"{self._svc_name_} failed: {exc}")
            raise
        finally:
            servicemanager.LogInfoMsg(f"{self._svc_name_} stopped")

    def _run_service(self) -> None:
        config_path = SETTINGS.get("config_path")
        if not config_path:
            raise RuntimeError("Windows service config_path is not configured")

        log_path = SETTINGS.get("log_path")
        configs = load_configs(config_path)
        _configure_logging(configs[0].runtime.log_level, log_path)

        services = [ProductionBridgeService(config) for config in configs]
        for service in services:
            self.logger.info("Loaded pipeline %s (%s)", service.config.name, service.config.source.type)

        while win32event.WaitForSingleObject(self.stop_event, 0) != win32event.WAIT_OBJECT_0:
            sleep_for = min(service.config.runtime.poll_interval_seconds for service in services)
            for service in services:
                try:
                    processed = service.run_once()
                    self.logger.info("[%s] Cycle completed. Rows transferred: %s", service.config.name, processed)
                except Exception as exc:  # pragma: no cover
                    self.logger.exception("[%s] Bridge cycle failed: %s", service.config.name, exc)
                    if service.config.runtime.stop_on_error:
                        raise
            if win32event.WaitForSingleObject(self.stop_event, int(sleep_for * 1000)) == win32event.WAIT_OBJECT_0:
                break


def _configure_logging(level: str, log_path: str | None) -> None:
    handlers: list[logging.Handler] = []
    if log_path:
        log_file = Path(log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.handlers.RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5, encoding="utf-8"))
    else:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=handlers,
        force=True,
    )


def main() -> None:  # pragma: no cover
    win32serviceutil.HandleCommandLine(RupMesProductionConnectorService)


if __name__ == "__main__":  # pragma: no cover
    main()
