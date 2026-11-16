
import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


# ==========================================
# PROCESS ORDER BATCH - BRANCH COVERAGE
# ==========================================

def test_valid_empty_orders():
    result = process_order_batch([], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_invalid_orders_type():
    with pytest.raises(ValueError):
        process_order_batch("coffee", 0.1)


def test_negative_tax():
    with pytest.raises(ValueError):
        process_order_batch([], -0.1)


def test_zero_tax():
    result = process_order_batch(
        [{"paid": True, "size": "medium"}], 0
    )
    assert result["status"] == "COMPLETED"


def test_unpaid_order():
    result = process_order_batch(
        [{"paid": False, "size": "large"}], 0
    )
    assert result["status"] == "NO_SALE"


@pytest.mark.parametrize("size, expected", [
    ("small", 3.0),
    ("medium", 4.5),
    ("large", 6.0),
    ("unknown", 0.0)
])
def test_size_branches(size, expected):
    result = process_order_batch(
        [{"paid": True, "size": size}], 0
    )
    assert result["total"] == expected


def test_empty_customizations():
    result = process_order_batch(
        [{"paid": True, "size": "medium", "customizations": []}], 0
    )
    assert result["total"] == 4.5


def test_negative_customization_cost():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "syrup", "cost": -1}]
        }], 0
    )
    assert result["total"] == 4.5


def test_positive_customization_cost():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "extra_shot", "cost": 1}]
        }], 0
    )
    assert result["total"] == 5.5


def test_allergen_non_strict():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "allergen_alert"}],
            "strict_allergy": False
        }], 0
    )
    assert result["total"] == 4.5
    assert result["status"] == "COMPLETED"


def test_allergen_strict():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [
                {"type": "allergen_alert"},
                {"type": "extra_shot", "cost": 2}
            ],
            "strict_allergy": True
        }], 0
    )
    assert result["total"] == 0
    assert result["status"] == "NO_SALE"


def test_syrup_at_limit():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "syrup", "cost": 1.5}]
        }], 0
    )
    assert result["total"] == 6.0


def test_syrup_above_limit():
    result = process_order_batch(
        [{
            "paid": True,
            "customizations": [{"type": "syrup", "cost": 2.5}]
        }], 0
    )
    assert result["total"] == 6.0


def test_member_order():
    result = process_order_batch(
        [{"paid": True, "is_member": True}], 0
    )
    assert result["total"] == 4.05


def test_non_member_order():
    result = process_order_batch(
        [{"paid": True, "is_member": False}], 0
    )
    assert result["total"] == 4.5


def test_audit_rejected():
    orders = [
        {"paid": True, "size": "invalid"}
        for _ in range(5)
    ]
    result = process_order_batch(orders, 0)
    assert result["status"] == "AUDIT_REJECTED"


def test_audit_not_rejected():
    orders = [
        {"paid": True, "size": "invalid"}
        for _ in range(4)
    ]
    result = process_order_batch(orders, 0)
    assert result["status"] == "NO_SALE"


def test_completed_status():
    result = process_order_batch(
        [{"paid": True, "size": "large"}], 0.1
    )
    assert result["status"] == "COMPLETED"


# ==========================================
# ESPRESSO MACHINE - BRANCH COVERAGE
# ==========================================

def test_empty_temperature_cycles():
    assert check_espresso_machine([]) == "NO_DATA"


def test_empty_inner_cycle():
    assert check_espresso_machine([[]]) == "OPTIMAL"


def test_normal_temperature():
    assert check_espresso_machine([[90, 92]]) == "OPTIMAL"


def test_single_overheat():
    assert check_espresso_machine([[97]]) == "OPTIMAL"


def test_overheat_followed_by_normal():
    assert check_espresso_machine([[97, 90]]) == "OPTIMAL"


def test_two_consecutive_overheats():
    assert check_espresso_machine([[97, 98]]) == "SHUTDOWN"


def test_overheat_streak_reset():
    assert check_espresso_machine([[97, 90, 97, 98]]) == "SHUTDOWN"


def test_multiple_cycles():
    assert check_espresso_machine([[97], [90, 91]]) == "OPTIMAL"


def test_shutdown_in_later_cycle():
    assert check_espresso_machine([[90], [97, 98]]) == "SHUTDOWN"
