
import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


# ==========================================
# PROCESS ORDER BATCH - LINE COVERAGE TESTS
# ==========================================

def test_invalid_orders():
    with pytest.raises(ValueError):
        process_order_batch("invalid", 0.1)


def test_negative_tax_rate():
    with pytest.raises(ValueError):
        process_order_batch([], -0.1)


def test_unpaid_order():
    result = process_order_batch(
        [{"paid": False, "size": "medium"}], 0.1
    )
    assert result["status"] == "NO_SALE"


@pytest.mark.parametrize("size, price", [
    ("small", 3.0),
    ("medium", 4.5),
    ("large", 6.0)
])
def test_all_coffee_sizes(size, price):
    result = process_order_batch(
        [{"paid": True, "size": size}], 0
    )
    assert result["total"] == price
    assert result["status"] == "COMPLETED"


def test_invalid_coffee_size():
    result = process_order_batch(
        [{"paid": True, "size": "extra_large"}], 0
    )
    assert result["status"] == "NO_SALE"


def test_default_order_values():
    result = process_order_batch([{"paid": True}], 0)
    assert result["total"] == 4.5


def test_negative_customization_cost():
    result = process_order_batch(
        [{
            "paid": True,
            "size": "medium",
            "customizations": [{"type": "syrup", "cost": -1}]
        }], 0
    )
    assert result["total"] == 4.5


def test_allergen_alert_non_strict():
    result = process_order_batch(
        [{
            "paid": True,
            "size": "medium",
            "strict_allergy": False,
            "customizations": [{"type": "allergen_alert"}]
        }], 0
    )
    assert result["total"] == 4.5


def test_allergen_alert_strict():
    result = process_order_batch(
        [{
            "paid": True,
            "size": "large",
            "strict_allergy": True,
            "customizations": [{"type": "allergen_alert"}]
        }], 0
    )
    assert result["total"] == 0
    assert result["status"] == "NO_SALE"


def test_syrup_cost_below_limit():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "syrup", "cost": 1.0}]
        }], 0
    )
    assert result["total"] == 5.5


def test_syrup_cost_above_limit():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "syrup", "cost": 2.5}]
        }], 0
    )
    assert result["total"] == 6.0


def test_other_customization():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "extra_shot", "cost": 2.0}]
        }], 0
    )
    assert result["total"] == 6.5


def test_member_discount():
    result = process_order_batch(
        [{
            "paid": True,
            "size": "large",
            "is_member": True
        }], 0
    )
    assert result["total"] == 5.4


def test_tax_calculation():
    result = process_order_batch(
        [{"paid": True, "size": "medium"}], 0.1
    )
    assert result["total"] == 4.95


def test_audit_rejected_status():
    orders = [
        {"paid": True, "size": "invalid"}
        for _ in range(5)
    ]
    result = process_order_batch(orders, 0.1)
    assert result["status"] == "AUDIT_REJECTED"


# ==========================================
# ESPRESSO MACHINE - LINE COVERAGE TESTS
# ==========================================

def test_no_temperature_data():
    assert check_espresso_machine([]) == "NO_DATA"


def test_optimal_temperature():
    assert check_espresso_machine([[90, 92, 94]]) == "OPTIMAL"


def test_single_overheating_reading():
    assert check_espresso_machine([[97, 90]]) == "OPTIMAL"


def test_two_consecutive_overheating_readings():
    assert check_espresso_machine([[97, 98]]) == "SHUTDOWN"


def test_overheating_streak_reset():
    assert check_espresso_machine([[97, 90, 97, 98]]) == "SHUTDOWN"


def test_multiple_temperature_cycles():
    assert check_espresso_machine([[97], [90, 91]]) == "OPTIMAL"
