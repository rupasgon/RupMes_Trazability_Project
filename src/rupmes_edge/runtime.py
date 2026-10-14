from __future__ import annotations

from datetime import datetime
from typing import Any

from rupmes_edge.domain import LiveStation, StationDefinition, utc_now


class EdgeRuntime:
    def __init__(self, line_name: str, stations: list[StationDefinition], store=None):
        self.line_name = line_name
        self.stations = {definition.station_id: LiveStation(definition) for definition in stations}
        self.endpoint_health: dict[str, tuple[bool, str | None]] = {}
        self.store = store
        self._last_states: dict[str, str] = {}

    async def apply_update(self, station_id: str, metric: str, value: Any, observed_at: datetime) -> None:
        station = self.stations[station_id]
        previous_cycles = station.completed_cycles
        station.apply(metric, value, observed_at)
        if self.store and station.completed_cycles > previous_cycles and station.last_cycle_seconds is not None:
            self.store.record_cycle(station_id, station.last_cycle_seconds, observed_at)
        if self.store and metric == "PartsCounter":
            try:
                self.store.record_counter(station_id, float(value), observed_at)
            except (TypeError, ValueError):
                pass

    def set_endpoint_health(self, endpoint_id: str, connected: bool, error: str | None = None) -> None:
        self.endpoint_health[endpoint_id] = (connected, error)
        if self.store:
            self.store.record_connector(endpoint_id, connected, error, utc_now())

    def snapshot(self) -> dict[str, Any]:
        now = utc_now()
        stations = []
        for station in self.stations.values():
            connected = self.endpoint_health.get(station.definition.endpoint_id, (False, None))[0]
            item = station.as_dict(connected, now)
            if self.store and self._last_states.get(station.definition.station_id) != item["state"]:
                self.store.record_state(station.definition.station_id, item["state"], now)
            self._last_states[station.definition.station_id] = item["state"]
            stations.append(item)
        health = {endpoint_id: {"connected": value[0], "error": value[1]} for endpoint_id, value in self.endpoint_health.items()}
        output_counters = [item for item in stations if item["is_output_station"] and item["parts_counter"] is not None]
        bottleneck_candidates = [item for item in stations if item["average_cycle_seconds"] is not None]
        bottleneck = max(
            bottleneck_candidates,
            key=lambda item: item["average_cycle_seconds"] / item["target_cycle_seconds"],
            default=None,
        )
        state_counts = {state: sum(1 for item in stations if item["state"] == state) for state in ("RUNNING", "IDLE", "STOPPED", "FAULT", "MANUAL", "DISCONNECTED", "UNKNOWN")}
        return {
            "line_name": self.line_name,
            "generated_at": now.isoformat(),
            "connection": {"connected": all(value[0] for value in self.endpoint_health.values()) and bool(self.endpoint_health), "endpoints": health},
            "stations": stations,
            "line_parts": output_counters[0]["parts_counter"] if len(output_counters) == 1 else None,
            "line_parts_station": output_counters[0]["name"] if len(output_counters) == 1 else None,
            "total_parts": sum(item["parts_counter"] or 0 for item in stations),
            "active_alarms": sum(1 for item in stations if item["state"] == "FAULT"),
            "state_counts": state_counts,
            "completed_cycles": sum(item["completed_cycles"] for item in stations),
            "cycles_over_target": sum(item["cycles_over_target"] for item in stations),
            "bottleneck": (
                {
                    "id": bottleneck["id"],
                    "name": bottleneck["name"],
                    "average_cycle_seconds": bottleneck["average_cycle_seconds"],
                    "target_cycle_seconds": bottleneck["target_cycle_seconds"],
                }
                if bottleneck
                else None
            ),
        }
