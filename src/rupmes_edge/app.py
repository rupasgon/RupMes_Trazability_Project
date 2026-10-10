from __future__ import annotations

import asyncio
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse

from rupmes_edge.config import EdgeConfig, secret_from_reference
from rupmes_edge.opcua import OpcUaSubscriptionCollector
from rupmes_edge.runtime import EdgeRuntime
from rupmes_edge.store import EdgeStore


def create_app(config: EdgeConfig) -> FastAPI:
    store = EdgeStore(config.storage.database_path)
    stations = config.station_definitions()
    runtime = EdgeRuntime(config.line_name, stations, store)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        collectors, tasks = [], []
        for endpoint in config.endpoints:
            assigned = [station for station in stations if station.endpoint_id == endpoint.endpoint_id]
            collector = OpcUaSubscriptionCollector(endpoint, assigned, runtime.apply_update, lambda connected, error, endpoint_id=endpoint.endpoint_id: runtime.set_endpoint_health(endpoint_id, connected, error), endpoint.subscription_interval_ms)
            collectors.append(collector)
            tasks.append(asyncio.create_task(collector.run()))
        try:
            yield
        finally:
            for collector in collectors:
                collector.stop()
            await asyncio.gather(*tasks, return_exceptions=True)
            store.close()

    app = FastAPI(title="RupMES Edge Dashboard", lifespan=lifespan)
    static_dir = Path(__file__).with_name("static")

    def require_admin(token: str | None) -> None:
        expected = secret_from_reference(config.admin.token_secret_ref)
        if expected and not (token and secrets.compare_digest(token, expected.get_secret_value())):
            raise HTTPException(status_code=401, detail="Invalid edge administrator token")

    @app.get("/edge")
    def dashboard() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/edge/api/snapshot")
    def snapshot() -> dict:
        return runtime.snapshot()

    @app.get("/edge/health")
    def health() -> dict:
        result = runtime.snapshot()["connection"]
        return {"status": "ok" if result["connected"] else "degraded", **result}

    @app.get("/edge/api/admin/config")
    def get_config(x_edge_admin_token: str | None = Header(default=None)) -> dict:
        require_admin(x_edge_admin_token)
        return config.sanitized()

    return app
