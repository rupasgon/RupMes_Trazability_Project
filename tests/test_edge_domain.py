import asyncio
from datetime import timedelta

from rupmes_edge.domain import LiveStation, StationDefinition, StationState, utc_now
from rupmes_edge.runtime import EdgeRuntime


def station() -> LiveStation:
    return LiveStation(StationDefinition("ST01", "Test station", 20.0, {}))


def test_fault_has_priority_over_running():
    live = station()
    now = utc_now()
    live.apply("Running", True, now)
    live.apply("FaultActive", True, now)

    assert live.state(True, now) == StationState.FAULT


def test_stale_data_is_disconnected():
    live = station()
    now = utc_now()
    live.apply("Running", True, now - timedelta(seconds=6))

    assert live.state(True, now) == StationState.DISCONNECTED


def test_cycle_complete_records_plc_cycle_time_once_per_pulse():
    live = station()
    now = utc_now()
    live.apply("CycleTime", 21.5, now)
    live.apply("CycleComplete", True, now)
    live.apply("CycleComplete", True, now)

    assert live.completed_cycles == 1
    assert live.last_cycle_seconds == 21.5
    assert live.cycles_over_target == 1


def test_snapshot_uses_the_configured_output_station_for_line_parts():
    runtime = EdgeRuntime(
        "Demo line",
        [
            StationDefinition("ST01", "Assembly", 20.0, {}, is_output_station=False),
            StationDefinition("ST02", "Packing", 20.0, {}, is_output_station=True),
        ],
    )
    now = utc_now()
    runtime.set_endpoint_health("default", True)
    asyncio.run(runtime.apply_update("ST01", "PartsCounter", 12, now))
    asyncio.run(runtime.apply_update("ST02", "PartsCounter", 9, now))

    snapshot = runtime.snapshot()

    assert snapshot["line_parts"] == 9
    assert snapshot["line_parts_station"] == "Packing"
