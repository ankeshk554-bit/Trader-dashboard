import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

from data.nifty50 import NIFTY50
from data.nifty200 import NIFTY200
from data.nifty500 import NIFTY500

st.set_page_config(
    page_title="Sniper Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# THEME
# =========================================================

st.markdown("""
<style>
.stApp {
    background-color: #050816;
    color: white;
}

h1, h2, h3 {
    color: #f5c542;
}

[data-testid="stSidebar"] {
    background-color: #0c1220;
}

.metric-box {
    padding: 20px;
    border-radius: 12px;
    background: #111827;
    border: 1px solid #1f2937;
}

.buy {
    color: #00ff9f;
    font-weight: bold;
}

.sell {
    color: #ff4d6d;
    font-weight: bold;
}

.neutral {
    color: orange;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================

def clean_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def fetch_data(ticker):
    df = yf.download(
        ticker,
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    df = clean_columns(df)

    if df.empty:
        return None

    return df


def add_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    delta = df["Close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain = pd.Series(gain).rolling(14).mean()
    loss = pd.Series(loss).rolling(14).mean()

    rs = gain / loss

    df["RSI"] = 100 - (100 / (1 + rs))

    df["VOL_MA20"] = df["Volume"].rolling(20).mean()

    df["RVOL"] = df["Volume"] / df["VOL_MA20"]

    return df


def calculate_avwap(df, anchor_idx=0):

    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3

    volume = df["Volume"]

    tpv = (typical_price * volume).iloc[anchor_idx:]

    cumulative_tpv = tpv.cumsum()

    cumulative_volume = volume.iloc[anchor_idx:].cumsum()

    avwap = cumulative_tpv / cumulative_volume

    return avwap


def institutional_score(df):

    latest = df.iloc[-1]

    score = 0

    if latest["Close"] > latest["EMA50"]:
        score += 25

    if latest["EMA50"] > latest["EMA200"]:
        score += 25

    if latest["RVOL"] > 1.5:
        score += 25

    if latest["RSI"] > 55:
        score += 25

    return score


def generate_signal(df):

    latest = df.iloc[-1]

    if (
        latest["Close"] > latest["EMA50"]
        and latest["EMA50"] > latest["EMA200"]
        and latest["RSI"] > 55
        and latest["RVOL"] > 1.5
    ):
        return "BUY"

    elif latest["Close"] < latest["EMA50"]:
        return "SELL"

    return "NEUTRAL"


def market_regime():

    nifty = fetch_data("^NSEI")

    nifty = add_indicators(nifty)

    latest = nifty.iloc[-1]

    if latest["Close"] > latest["EMA200"]:
        return "BULLISH"

    return "BEARISH"


def run_backtest(df):

    capital = 100000

    position = 0

    trades = []

    for i in range(200, len(df)):

        row = df.iloc[i]

        if (
            row["Close"] > row["EMA50"]
            and row["EMA50"] > row["EMA200"]
            and row["RSI"] > 55
            and row["RVOL"] > 1.5
            and position == 0
        ):

            buy_price = row["Close"]

            position = capital / buy_price

            trades.append(("BUY", row.name, buy_price))

        elif (
            row["Close"] < row["EMA50"]
            and position > 0
        ):

            sell_price = row["Close"]

            capital = position * sell_price

            position = 0

            trades.append(("SELL", row.name, sell_price))

    total_return = ((capital - 100000) / 100000) * 100

    return round(total_return, 2), trades


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Terminal")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Screener",
        "Chart",
        "Backtest"
    ]
)

# =========================================================
# HEADER
# =========================================================

st.title("Sniper Terminal — Institutional Swing Engine")

st.caption(
    "Institutional Relative Strength • Smart Money • Regime Trading • Swing Execution"
)

regime = market_regime()

if regime == "BULLISH":
    st.success(f"Market Regime: {regime}")
else:
    st.error(f"Market Regime: {regime}")

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.subheader("Market Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Market Regime", regime)
    col2.metric("Universe", "NIFTY 500")
    col3.metric("Strategy", "Institutional Swing")

# =========================================================
# SCREENER
# =========================================================

elif page == "Screener":

    st.subheader("Institutional Scanner")

    universe = st.selectbox(
        "Select Universe",
        ["NIFTY50", "NIFTY200", "NIFTY500"]
    )

    if universe == "NIFTY50":
        stocks = NIFTY50

    elif universe == "NIFTY200":
        stocks = NIFTY200

    else:
        stocks = NIFTY500

    results = []

    progress = st.progress(0)

    total = len(stocks)

    for idx, stock in enumerate(stocks):

        try:

            df = fetch_data(stock)

            if df is None or len(df) < 220:
                continue

            df = add_indicators(df)

            signal = generate_signal(df)

            score = institutional_score(df)

            latest = df.iloc[-1]

            results.append({
                "Stock": stock,
                "Close": round(float(latest["Close"]), 2),
                "RSI": round(float(latest["RSI"]), 2),
                "RVOL": round(float(latest["RVOL"]), 2),
                "Score": score,
                "Signal": signal
            })

        except:
            pass

        progress.progress((idx + 1) / total)

    if len(results) > 0:

        screen_df = pd.DataFrame(results)

        screen_df = screen_df.sort_values(
            by="Score",
            ascending=False
        )

        st.dataframe(
            screen_df,
            use_container_width=True
        )

    else:
        st.warning("No stocks found")

# =========================================================
# CHART
# =========================================================

elif page == "Chart":

    ticker = st.text_input(
        "Enter Stock",
        value="RELIANCE.NS"
    )

    df = fetch_data(ticker)

    if df is not None:

        df = add_indicators(df)

        latest = df.iloc[-1]

        swing_low_idx = df["Low"].idxmin()
        swing_high_idx = df["High"].idxmax()

        low_anchor = df.index.get_loc(swing_low_idx)
        high_anchor = df.index.get_loc(swing_high_idx)

        avwap_low = calculate_avwap(df, low_anchor)
        avwap_high = calculate_avwap(df, high_anchor)

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.8, 0.2]
        )

        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA50"],
                name="EMA50"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["EMA200"],
                name="EMA200"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=avwap_low.index,
                y=avwap_low,
                name="AVWAP Low"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Scatter(
                x=avwap_high.index,
                y=avwap_high,
                name="AVWAP High"
            ),
            row=1,
            col=1
        )

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume"
            ),
            row=2,
            col=1
        )

        fig.update_layout(
            template="plotly_dark",
            height=800,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Close",
            round(float(latest["Close"]), 2)
        )

        col2.metric(
            "RSI",
            round(float(latest["RSI"]), 2)
        )

        col3.metric(
            "RVOL",
            round(float(latest["RVOL"]), 2)
        )

# =========================================================
# BACKTEST
# =========================================================

elif page == "Backtest":

    st.subheader("Strategy Backtest")

    ticker = st.text_input(
        "Ticker",
        value="RELIANCE.NS"
    )

    if st.button("Run Backtest"):

        df = fetch_data(ticker)

        if df is not None:

            df = add_indicators(df)

            returns, trades = run_backtest(df)

            st.metric(
                "Strategy Return %",
                returns
            )

            if len(trades) > 0:

                trades_df = pd.DataFrame(
                    trades,
                    columns=["Action", "Date", "Price"]
                )

                st.dataframe(
                    trades_df,
                    use_container_width=True
                )

            else:
                st.warning("No trades generated")