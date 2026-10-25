from datetime import date


def bond_price(face, coupon_rate, ytm, years, freq=2):
    n = int(round(years * freq))
    c = face * coupon_rate / freq
    y = ytm / freq
    pv_coupons = sum(c / (1 + y) ** t for t in range(1, n + 1))
    pv_face = face / (1 + y) ** n
    return pv_coupons + pv_face


def find_ytm(price, face, coupon_rate, years, freq=2, tol=1e-8, max_iter=200):
    low, high = 0.0, 1.0
    for _ in range(max_iter):
        mid = (low + high) / 2
        p = bond_price(face, coupon_rate, mid, years, freq)
        if abs(p - price) < tol:
            return mid
        if p > price:
            low = mid
        else:
            high = mid
    return mid


def durations(face, coupon_rate, ytm, years, freq=2):
    n = int(round(years * freq))
    c = face * coupon_rate / freq
    y = ytm / freq
    weighted_sum = 0
    price = 0
    for t in range(1, n + 1):
        cash_flow = c
        if t == n:
            cash_flow = c + face
        pv = cash_flow / (1 + y) ** t
        price = price + pv
        weighted_sum = weighted_sum + t * pv
    macaulay = weighted_sum / price / freq
    modified = macaulay / (1 + y)
    return macaulay, modified


def convexity(face, coupon_rate, ytm, years, freq=2):
    n = int(round(years * freq))
    c = face * coupon_rate / freq
    y = ytm / freq
    total = 0
    price = 0
    for t in range(1, n + 1):
        cash_flow = c
        if t == n:
            cash_flow = c + face
        pv = cash_flow / (1 + y) ** t
        price = price + pv
        total = total + t * (t + 1) * pv
    return total / price / (1 + y) ** 2 / freq ** 2


def sensitivity2(face, coupon_rate, ytm, years, shock_bps, freq=2):
    base = bond_price(face, coupon_rate, ytm, years, freq)
    mac, mod = durations(face, coupon_rate, ytm, years, freq)
    conv = convexity(face, coupon_rate, ytm, years, freq)
    dy = shock_bps / 10000
    est_dur = base * (1 - mod * dy)
    est_conv = base * (1 - mod * dy + 0.5 * conv * dy ** 2)
    actual = bond_price(face, coupon_rate, ytm + dy, years, freq)
    return est_dur, est_conv, actual


def days_360(d1, d2):
    return 360 * (d2.year - d1.year) + 30 * (d2.month - d1.month) + (min(d2.day, 30) - min(d1.day, 30))


def check_inputs(face, coupon_rate, ytm, n_remaining, freq):
    if face <= 0:
        raise ValueError("face must be positive")
    if coupon_rate < 0:
        raise ValueError("coupon_rate cannot be negative")
    if ytm < 0:
        raise ValueError("ytm cannot be negative")
    if n_remaining < 1:
        raise ValueError("n_remaining must be at least 1")
    if freq not in (1, 2, 4, 12):
        raise ValueError("freq must be 1, 2, 4 or 12")


def accrued_interest(face, coupon_rate, last_coupon, settlement, freq=2):
    if settlement < last_coupon:
        raise ValueError("settlement cannot be before the last coupon date")
    period_days = 360 / freq
    days = days_360(last_coupon, settlement)
    return face * coupon_rate / freq * days / period_days


def clean_dirty(face, coupon_rate, ytm, n_remaining, last_coupon, settlement, freq=2):
    check_inputs(face, coupon_rate, ytm, n_remaining, freq)
    period_days = 360 / freq
    days = days_360(last_coupon, settlement)
    if days > period_days:
        raise ValueError("settlement is more than one coupon period after last_coupon")
    w = 1 - days / period_days
    c = face * coupon_rate / freq
    y = ytm / freq
    dirty = 0
    for k in range(n_remaining):
        cash_flow = c
        if k == n_remaining - 1:
            cash_flow = c + face
        dirty = dirty + cash_flow / (1 + y) ** (k + w)
    accrued = accrued_interest(face, coupon_rate, last_coupon, settlement, freq)
    return dirty - accrued, dirty, accrued