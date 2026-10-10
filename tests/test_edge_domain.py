from datetime import timedelta

from rupmes_edge.domain import LiveStation, StationDefinition, StationState, utc_now


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
