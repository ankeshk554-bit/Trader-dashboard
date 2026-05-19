import yfinance as yf
import pandas as pd
import ta


def clean_columns(df):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def run_backtest(symbol):

    try:

        df = yf.download(
            symbol,
            period="5y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df = clean_columns(df)

        df["EMA50"] = ta.trend.ema_indicator(
            df["Close"],
            window=50
        )

        df["EMA200"] = ta.trend.ema_indicator(
            df["Close"],
            window=200
        )

        df["Signal"] = 0

        df.loc[
            df["EMA50"] > df["EMA200"],
            "Signal"
        ] = 1

        df["Returns"] = df["Close"].pct_change()

        df["Strategy"] = (
            df["Signal"].shift(1)
            * df["Returns"]
        )

        total_return = (
            (
                1 + df["Strategy"]
            ).cumprod().iloc[-1] - 1
        ) * 100

        return {
            "Total Return": round(total_return, 2)
        }

    except Exception as e:

        print(f"Backtest Error: {e}")

        return None