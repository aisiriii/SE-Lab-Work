
"""Manage energy meter readings, tariffs, and electricity bills."""

import json
from datetime import datetime
from pathlib import Path

METERS = {}
RATE_TIER_1 = 3.5
RATE_TIER_2 = 5.0
RATE_TIER_3 = 7.5
SPIKE_LIMIT = 500
DATA_FILE = Path("meters.json")


def record_reading(meter_id, units, history=None):
    """Record a meter reading and update its cumulative units."""
    if not isinstance(units, (int, float)) or isinstance(units, bool):
        raise ValueError("Units must be a number.")
    if units < 0:
        raise ValueError("Units cannot be negative.")

    if history is None:
        history = []

    history.append((meter_id, units, datetime.now().isoformat()))
    METERS[meter_id] = METERS.get(meter_id, 0) + units
    return history


def compute_bill(meter_id, tier_rates):
    """Calculate a bill using three consumption tiers."""
    units = METERS.get(meter_id, 0)

    if units <= 100:
        return units * tier_rates[0]
    if units <= 300:
        return 100 * tier_rates[0] + (units - 100) * tier_rates[1]
    return (
        100 * tier_rates[0]
        + 200 * tier_rates[1]
        + (units - 300) * tier_rates[2]
    )


def raise_rates(percent):
    """Increase all tariff rates by a percentage."""
    global RATE_TIER_1, RATE_TIER_2, RATE_TIER_3

    if percent < 0:
        raise ValueError("Rate increase cannot be negative.")

    multiplier = 1 + percent / 100
    RATE_TIER_1 *= multiplier
    RATE_TIER_2 *= multiplier
    RATE_TIER_3 *= multiplier


def flag_spikes():
    """Return meter IDs whose consumption exceeds the spike limit."""
    return [
        meter_id
        for meter_id, units in METERS.items()
        if units > SPIKE_LIMIT
    ]


def load_meter_data(file=DATA_FILE):
    """Load meter totals from a JSON file."""
    global METERS

    try:
        with Path(file).open("r", encoding="utf-8") as data_file:
            loaded_data = json.load(data_file)
        if not isinstance(loaded_data, dict):
            raise ValueError("Meter data must be a JSON object.")
        METERS = loaded_data
    except FileNotFoundError:
        METERS = {}
    except (json.JSONDecodeError, OSError, ValueError) as error:
        raise ValueError(f"Unable to load meter data: {error}") from error


def save_meter_data(file=DATA_FILE):
    """Save meter totals to a JSON file."""
    with Path(file).open("w", encoding="utf-8") as data_file:
        json.dump(METERS, data_file, indent=2)


def main():
    """Run a demonstration of the energy tariff system."""
    record_reading("M-01", 120)
    record_reading("M-02", 640)

    try:
        record_reading("M-03", -50)
    except ValueError as error:
        print(f"Invalid reading: {error}")

    print("Spikes:", flag_spikes())
    raise_rates(10)
    rates = [RATE_TIER_1, RATE_TIER_2, RATE_TIER_3]
    print(f"Bill M-01: {compute_bill('M-01', rates):.2f}")
    print(f"Bill M-03: {compute_bill('M-03', rates):.2f}")

    adjustment_text = input(
        "Extra units for M-01 (Enter for 0): "
    ).strip() or "0"

    try:
        adjustment = int(adjustment_text)
        record_reading("M-01", adjustment)
    except ValueError as error:
        print(f"Invalid adjustment: {error}")
        return

    save_meter_data()
    load_meter_data()
    print(f"Bill M-01 after reload: {compute_bill('M-01', rates):.2f}")


if __name__ == "__main__":
    main()
