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

    # Fix yfinance multi-index columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()

    # Convert to numeric safely
    close = pd.to_numeric(df["Close"], errors="coerce")

    # Force series
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    ema50 = close.ewm(span=50).mean()
    ema200 = close.ewm(span=200).mean()

    latest_close = close.iloc[-1]
    latest_ema50 = ema50.iloc[-1]
    latest_ema200 = ema200.iloc[-1]

    if latest_close > latest_ema50 > latest_ema200:
        return "BULL"

    elif latest_close < latest_ema50 < latest_ema200:
        return "BEAR"

    return "SIDEWAYS"
