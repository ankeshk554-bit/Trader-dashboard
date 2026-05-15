import yfinance as yf
import pandas as pd


def get_market_regime():

    df = yf.download(
        "^NSEI",
        period="1y",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        return "UNKNOWN"

    # Fix multi-index issue
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()

    close = pd.to_numeric(df["Close"], errors="coerce")
    ema50 = close.ewm(span=50).mean()
    ema200 = close.ewm(span=200).mean()

    latest_close = float(close.iloc[-1])
    latest_ema50 = float(ema50.iloc[-1])
    latest_ema200 = float(ema200.iloc[-1])

    if latest_close > latest_ema50 > latest_ema200:
        return "BULL"

    elif latest_close < latest_ema50 < latest_ema200:
        return "BEAR"

    return "SIDEWAYS"
