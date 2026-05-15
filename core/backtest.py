import pandas as pd


def run_backtest(signals):

    if len(signals) == 0:
        return pd.DataFrame()

    capital_curve = []

    capital = 100000

    for sig in signals:

        rr = sig["RR"]

        confidence = sig["CONFIDENCE"]

        if confidence >= 70:
            pnl = capital * 0.02 * rr
        else:
            pnl = -capital * 0.01

        capital += pnl

        capital_curve.append(
            {
                "SYMBOL": sig["SYMBOL"],
                "SETUP": sig["SETUP"],
                "CONFIDENCE": confidence,
                "RR": rr,
                "CAPITAL": capital,
            }
        )

    return pd.DataFrame(capital_curve)
