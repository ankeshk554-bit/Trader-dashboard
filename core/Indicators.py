import numpy as np
import pandas as pd
import streamlit as st


def compute_rsi(series: pd.Series, length: int = 14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def compute_atr(df: pd.DataFrame, length: int = 14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1 / length, adjust=False).mean()

    return atr


def compute_relative_volume(df: pd.DataFrame):
    vol_ma20 = df["Volume"].rolling(20).mean()

    rv = df["Volume"] / vol_ma20.replace(0, np.nan)

    return rv.fillna(0)


def compute_avwap(df: pd.DataFrame):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3.0

    cumulative_pv = (tp * df["Volume"]).cumsum()
    cumulative_vol = df["Volume"].cumsum()

    avwap = cumulative_pv / cumulative_vol.replace(0, np.nan)

    return avwap


def compute_momentum_score(df: pd.DataFrame):
    if len(df) < 120:
        return 0

    close = df["Close"]

    ret_1m = (close.iloc[-1] / close.iloc[-21] - 1) * 100
    ret_3m = (close.iloc[-1] / close.iloc[-63] - 1) * 100
    ret_6m = (close.iloc[-1] / close.iloc[-126] - 1) * 100

    score = (
        ret_1m * 0.4 +
        ret_3m * 0.35 +
        ret_6m * 0.25
    )

    return round(score, 2)


@st.cache_data(show_spinner=False)
def compute_indicators(df: pd.DataFrame):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # EMAs
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # RSI
    df["RSI"] = compute_rsi(df["Close"])

    # ATR
    df["ATR"] = compute_atr(df)

    # Relative Volume
    df["RVOL"] = compute_relative_volume(df)

    # AVWAP
    df["AVWAP"] = compute_avwap(df)

    # Bollinger Bands
    bb_mid = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()

    df["BB_UPPER"] = bb_mid + (2 * bb_std)
    df["BB_LOWER"] = bb_mid - (2 * bb_std)

    # Keltner
    kc_mid = bb_mid
    kc_atr = df["ATR"].rolling(20).mean()

    df["KC_UPPER"] = kc_mid + (1.5 * kc_atr)
    df["KC_LOWER"] = kc_mid - (1.5 * kc_atr)

    # Squeeze
    df["IN_SQUEEZE"] = (
        (df["BB_UPPER"] < df["KC_UPPER"]) &
        (df["BB_LOWER"] > df["KC_LOWER"])
    )

    # Trend score
    trend_score = 0

    if df["Close"].iloc[-1] > df["EMA21"].iloc[-1]:
        trend_score += 1

    if df["Close"].iloc[-1] > df["EMA50"].iloc[-1]:
        trend_score += 1

    if df["Close"].iloc[-1] > df["EMA200"].iloc[-1]:
        trend_score += 1

    df["TREND_SCORE"] = trend_score

    return df
