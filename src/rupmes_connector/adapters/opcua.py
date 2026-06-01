from __future__ import annotations

from typing import Any

from rupmes_connector.adapters.base import BaseSourceAdapter
from rupmes_connector.checkpoint import Checkpoint
from rupmes_connector.config import SourceConfig


class OpcUaSourceAdapter(BaseSourceAdapter):
    def __init__(self, config: SourceConfig):
        self.config = config
        try:
            from asyncua import Client
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("asyncua is required for opcua source support") from exc
        self._client_cls = Client

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict[str, Any]]:
        import asyncio

        async def _read_once():
            async with self._client_cls(url=self.config.endpoint_url) as client:
                row: dict[str, Any] = {}
                for field_name, node_id in self.config.node_map.items():
                    node = client.get_node(node_id)
                    row[field_name] = await node.read_value()
                if self.config.trigger_node:
                    trigger_node = client.get_node(self.config.trigger_node)
                    trigger_value = await trigger_node.read_value()
                    if self.config.trigger_value is not None and trigger_value != self.config.trigger_value:
                        return []
                return [row]

        return asyncio.run(_read_once())
