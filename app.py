import streamlit as st
import pandas as pd

from core.utils import load_data
from core.indicators import compute_indicators
from core.market_regime import get_market_regime
from core.scanner import run_universe_scan
from core.charts import institutional_chart
from core.backtest import run_backtest

from data.nifty50 import NIFTY50
from data.nifty200 import NIFTY200
from data.nifty500 import NIFTY500


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Sniper Terminal",
    layout="wide",
)

# =========================================================
# LOAD CSS
# =========================================================

with open("assets/style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True,
    )

# =========================================================
# SESSION STATE
# =========================================================

if "selected_stock" not in st.session_state:
    st.session_state["selected_stock"] = "RELIANCE.NS"

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <h1 style='color:#f5c542;'>
    Sniper Terminal — Institutional Swing Engine
    </h1>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Institutional Relative Strength • Smart Money • "
    "Regime Trading • Swing Execution"
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Terminal")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Scanner",
        "Chart",
        "Backtest",
    ]
)

# =========================================================
# MARKET REGIME
# =========================================================

regime = get_market_regime()

# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":

    st.subheader("Market Regime")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "NIFTY Regime",
            regime,
        )

    with col2:
        st.metric(
            "Trading Bias",
            "LONG ONLY"
            if regime in [
                "BULLISH",
                "BULL_EXPANSION",
            ]
            else "CAUTION",
        )

    with col3:
        st.metric(
            "Institutional State",
            "RISK ON"
            if regime == "BULL_EXPANSION"
            else "NEUTRAL",
        )

    with col4:
        st.metric(
            "Volatility",
            "NORMAL",
        )

    st.markdown("---")

    st.subheader("Institutional Watchlist")

    watchlist = [
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "INFY.NS",
        "HAL.NS",
        "BEL.NS",
    ]

    rows = []

    with st.spinner("Building institutional dashboard..."):

        from core.scanner import scan_stock

        for ticker in watchlist:

            try:

                row = scan_stock(ticker)

                if row:
                    rows.append(row)

            except Exception:
                continue

    if rows:

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
        )

    else:
        st.warning(
            "No institutional setups currently."
        )

# =========================================================
# SCANNER PAGE
# =========================================================

elif page == "Scanner":

    st.subheader("Institutional Scanner")

    col1, col2, col3 = st.columns(3)

    with col1:

        universe_name = st.selectbox(
            "Universe",
            [
                "NIFTY50",
                "NIFTY200",
                "NIFTY500",
            ]
        )

    with col2:

        capital = st.number_input(
            "Capital",
            10000,
            10000000,
            200000,
        )

    with col3:

        risk_pct = st.slider(
            "Risk %",
            0.5,
            5.0,
            1.0,
        )

    if universe_name == "NIFTY50":
        universe = [x + ".NS" for x in NIFTY50]

    elif universe_name == "NIFTY200":
        universe = [x + ".NS" for x in NIFTY200]

    else:
        universe = [x + ".NS" for x in NIFTY500]

    if st.button("Run Institutional Scan"):

        with st.spinner(
            "Scanning institutional flow..."
        ):

            df = run_universe_scan(
                universe,
                capital,
                risk_pct,
            )

        if df.empty:

            st.warning(
                "No setups found."
            )

        else:

            st.success(
                f"{len(df)} institutional setups detected."
            )

            st.dataframe(
                df,
                use_container_width=True,
            )

            selected = st.selectbox(
                "Select Stock",
                df["SYMBOL"].tolist(),
            )

            ticker = selected + ".NS"

            st.session_state["selected_stock"] = ticker

# =========================================================
# CHART PAGE
# =========================================================

elif page == "Chart":

    st.subheader("Institutional Workstation")

    ticker = st.text_input(
        "Ticker",
        st.session_state["selected_stock"],
    )

    interval = st.selectbox(
        "Interval",
        [
            "1d",
            "1h",
            "15m",
        ]
    )

    if st.button("Load Institutional Chart"):

        with st.spinner(
            "Loading institutional chart..."
        ):

            df = load_data(
                ticker,
                interval=interval,
                period="2y",
            )

            if df.empty:

                st.warning(
                    "No data found."
                )

            else:

                df = compute_indicators(df)

                fig = institutional_chart(
                    df,
                    ticker,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.markdown("---")

                latest = df.iloc[-1]

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Close",
                        round(
                            latest["Close"],
                            2,
                        ),
                    )

                with col2:
                    st.metric(
                        "RSI",
                        round(
                            latest["RSI"],
                            2,
                        ),
                    )

                with col3:
                    st.metric(
                        "RVOL",
                        round(
                            latest["RVOL"],
                            2,
                        ),
                    )

                with col4:
                    st.metric(
                        "ATR",
                        round(
                            latest["ATR"],
                            2,
                        ),
                    )

# =========================================================
# BACKTEST PAGE
# =========================================================

elif page == "Backtest":

    st.subheader("Strategy Backtest")

    ticker = st.text_input(
        "Ticker",
        "RELIANCE.NS",
    )

    if st.button("Run Backtest"):

        with st.spinner(
            "Running institutional simulation..."
        ):

            from core.scanner import scan_stock

            rows = []

            for _ in range(30):

                sig = scan_stock(ticker)

                if sig:
                    rows.append(sig)

            if not rows:

                st.warning(
                    "No trades generated."
                )

            else:

                bt = run_backtest(rows)

                st.dataframe(
                    bt,
                    use_container_width=True,
                )

                st.subheader(
                    "Equity Curve"
                )

                st.line_chart(
                    bt["CAPITAL"]
                )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Sniper Terminal • Institutional Swing Trading Engine • India Markets"
)
