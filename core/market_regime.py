from core.utils import load_data
from core.indicators import compute_indicators


def get_market_regime():

    df = load_data("^NSEI", interval="1d", period="2y")

    if df.empty:
        return "UNKNOWN"

    df = compute_indicators(df)

    close = float(df["Close"].iloc[-1])

    ema21 = float(df["EMA21"].iloc[-1])
    ema50 = float(df["EMA50"].iloc[-1])
    ema200 = float(df["EMA200"].iloc[-1])

    rsi = float(df["RSI"].iloc[-1])

    if (
        close > ema21 and
        close > ema50 and
        close > ema200 and
        rsi > 60
    ):
        return "BULL_EXPANSION"

    if (
        close > ema200 and
        rsi > 50
    ):
        return "BULLISH"

    if (
        close < ema200 and
        rsi < 40
    ):
        return "BEARISH"

    return "RANGEBOUND"
