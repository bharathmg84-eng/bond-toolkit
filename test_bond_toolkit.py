from datetime import date
from bond_toolkit import bond_price, accrued_interest, clean_dirty


def test_price_discount_bond():
    assert abs(bond_price(1000, 0.08, 0.10, 5) - 922.78) < 0.01


def test_price_par_bond():
    assert abs(bond_price(1000, 0.08, 0.08, 5) - 1000) < 1e-6


def test_price_zero_yield():
    assert abs(bond_price(1000, 0.08, 0.0, 5) - 1400) < 1e-6


def test_accrued_matches_hand_calc():
    assert abs(accrued_interest(1000, 0.08, date(2026, 1, 15), date(2026, 4, 15)) - 20) < 1e-9


def test_clean_plus_accrued_equals_dirty():
    clean, dirty, accrued = clean_dirty(1000, 0.08, 0.10, 9, date(2026, 1, 15), date(2026, 4, 15))
    assert abs(clean + accrued - dirty) < 1e-9


def test_on_coupon_date_matches_bond_price():
    clean, dirty, accrued = clean_dirty(1000, 0.08, 0.10, 10, date(2026, 1, 15), date(2026, 1, 15))
    assert accrued == 0
    assert abs(clean - 922.7826507) < 1e-6


def test_zero_coupon_has_no_accrued():
    clean, dirty, accrued = clean_dirty(1000, 0.0, 0.10, 10, date(2026, 1, 15), date(2026, 4, 15))
    assert accrued == 0


def test_negative_yield_raises():
    try:
        clean_dirty(1000, 0.08, -0.01, 10, date(2026, 1, 15), date(2026, 1, 15))
        assert False, "should have raised"
    except ValueError:
        pass