import pandas as pd
import numpy as np

from core.utils import load_data
from core.indicators import compute_indicators
from core.relative_strength import get_relative_strength
from core.market_regime import get_market_regime
from core.risk_engine import calculate_position_size


# =========================================================
# QUALITY ENGINE
# =========================================================

def institutional_score(df):

    score = 0

    close = float(df["Close"].iloc[-1])

    ema21 = float(df["EMA21"].iloc[-1])
    ema50 = float(df["EMA50"].iloc[-1])
    ema200 = float(df["EMA200"].iloc[-1])

    rsi = float(df["RSI"].iloc[-1])

    rvol = float(df["RVOL"].iloc[-1])

    if close > ema21:
        score += 10

    if close > ema50:
        score += 15

    if close > ema200:
        score += 20

    if ema21 > ema50 > ema200:
        score += 20

    if 55 <= rsi <= 75:
        score += 15

    if rvol > 1.5:
        score += 20

    return score


# =========================================================
# BREAKOUT ENGINE
# =========================================================

def detect_breakout(df):

    if len(df) < 80:
        return False, None

    recent_high = df["High"].iloc[-40:-5].max()

    close = float(df["Close"].iloc[-1])

    rvol = float(df["RVOL"].iloc[-1])

    if (
        close > recent_high and
        rvol > 1.5
    ):
        return True, recent_high

    return False, None


# =========================================================
# VCP ENGINE
# =========================================================

def detect_vcp(df):

    if len(df) < 100:
        return False

    ranges = []

    for period in [30, 20, 10]:
        sub = df.iloc[-period:]

        high = sub["High"].max()
        low = sub["Low"].min()

        contraction = ((high - low) / low) * 100

        ranges.append(contraction)

    if (
        ranges[2] < ranges[1] <
        ranges[0]
    ):
        return True

    return False


# =========================================================
# LIQUIDITY SWEEP
# =========================================================

def detect_liquidity_sweep(df):

    if len(df) < 30:
        return False

    latest = df.iloc[-1]

    prev_low = df["Low"].iloc[-10:-1].min()

    candle_range = latest["High"] - latest["Low"]

    body = abs(latest["Close"] - latest["Open"])

    lower_wick = min(
        latest["Open"],
        latest["Close"]
    ) - latest["Low"]

    if candle_range <= 0:
        return False

    if (
        latest["Low"] < prev_low and
        lower_wick > body * 1.5 and
        latest["Close"] > prev_low
    ):
        return True

    return False


# =========================================================
# PULLBACK ENGINE
# =========================================================

def detect_pullback(df):

    if len(df) < 50:
        return False

    close = float(df["Close"].iloc[-1])

    ema21 = float(df["EMA21"].iloc[-1])

    ema50 = float(df["EMA50"].iloc[-1])

    rsi = float(df["RSI"].iloc[-1])

    near_ema = (
        abs(close - ema21) / ema21 < 0.02
        or
        abs(close - ema50) / ema50 < 0.02
    )

    if (
        near_ema and
        rsi > 50
    ):
        return True

    return False


# =========================================================
# ENTRY ENGINE
# =========================================================

def generate_trade_levels(df):

    close = float(df["Close"].iloc[-1])

    atr = float(df["ATR"].iloc[-1])

    entry = round(close, 2)

    stoploss = round(close - (1.2 * atr), 2)

    target1 = round(close + (2 * atr), 2)

    target2 = round(close + (4 * atr), 2)

    rr = round(
        (target1 - entry) /
        max(entry - stoploss, 0.01),
        2
    )

    return {
        "ENTRY": entry,
        "SL": stoploss,
        "TARGET1": target1,
        "TARGET2": target2,
        "RR": rr,
    }


# =========================================================
# MASTER SCAN
# =========================================================

def scan_stock(
    ticker,
    capital=200000,
    risk_pct=1,
):

    df = load_data(
        ticker,
        interval="1d",
        period="2y",
    )

    if df.empty:
        return None

    df = compute_indicators(df)

    regime = get_market_regime()

    rs_score = get_relative_strength(ticker)

    institutional = institutional_score(df)

    breakout, breakout_level = detect_breakout(df)

    vcp = detect_vcp(df)

    sweep = detect_liquidity_sweep(df)

    pullback = detect_pullback(df)

    setup = None

    if breakout:
        setup = "BREAKOUT"

    elif vcp:
        setup = "VCP"

    elif sweep:
        setup = "LIQUIDITY_SWEEP"

    elif pullback:
        setup = "PULLBACK"

    if setup is None:
        return None

    levels = generate_trade_levels(df)

    qty = calculate_position_size(
        capital,
        risk_pct,
        levels["ENTRY"],
        levels["SL"],
    )

    confidence = (
        institutional * 0.5 +
        max(rs_score, 0) * 0.5
    )

    return {
        "SYMBOL": ticker.replace(".NS", ""),
        "SETUP": setup,
        "REGIME": regime,
        "RS_SCORE": round(rs_score, 2),
        "INST_SCORE": round(institutional, 2),
        "CONFIDENCE": round(confidence, 2),
        "ENTRY": levels["ENTRY"],
        "SL": levels["SL"],
        "TARGET1": levels["TARGET1"],
        "TARGET2": levels["TARGET2"],
        "RR": levels["RR"],
        "QTY": qty,
        "RVOL": round(float(df["RVOL"].iloc[-1]), 2),
        "RSI": round(float(df["RSI"].iloc[-1]), 2),
    }


# =========================================================
# UNIVERSE SCANNER
# =========================================================

def run_universe_scan(
    universe,
    capital=200000,
    risk_pct=1,
):

    rows = []

    for ticker in universe:

        try:

            row = scan_stock(
                ticker,
                capital,
                risk_pct,
            )

            if row:
                rows.append(row)

        except Exception:
            continue

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    df.sort_values(
        by=[
            "CONFIDENCE",
            "RS_SCORE",
            "RR",
        ],
        ascending=False,
        inplace=True,
    )

    df.reset_index(
        drop=True,
        inplace=True,
    )

    return df
