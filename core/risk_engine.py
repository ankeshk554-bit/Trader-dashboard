def calculate_position_size(
    capital,
    risk_pct,
    entry,
    stoploss,
):

    risk_amount = capital * risk_pct / 100

    sl_distance = abs(entry - stoploss)

    if sl_distance <= 0:
        return 0

    qty = int(risk_amount / sl_distance)

    return max(qty, 0)


def portfolio_heat(open_risks):

    total = sum(open_risks)

    return round(total, 2)
