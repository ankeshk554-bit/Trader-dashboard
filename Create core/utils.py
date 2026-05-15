import time
import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_data(
    ticker: str,
    interval: str = "1d",
    period: str = "3y",
):
    for _ in range(3):
        try:
            df = yf.download(
                ticker,
                interval=interval,
                period=period,
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if df is not None and not df.empty:
                df.dropna(inplace=True)

                if "Volume" not in df.columns:
                    df["Volume"] = 0

                return df

        except Exception:
            time.sleep(1)

    return pd.DataFrame()


def pct_change(a, b):
    if b == 0:
        return 0
    return ((a - b) / b) * 100


def safe_round(v, d=2):
    try:
        return round(float(v), d)
    except Exception:
        return None
