import plotly.graph_objects as go
from core.indicators import detect_vcp

def plot_chart(df, symbol, trades_df=None):
    fig = go.Figure()

    # -------------------------
    # Candlesticks
    # -------------------------
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        name="Price"
    ))

    # -------------------------
    # EMA200
    # -------------------------
    if "EMA200" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA200"],
            mode="lines",
            line=dict(color="orange", width=2),
            name="EMA200"
        ))

    # -------------------------
    # AVWAP
    # -------------------------
    if "AVWAP" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["AVWAP"],
            mode="lines",
            line=dict(color="purple", width=2),
            name="AVWAP"
        ))

    # -------------------------
    # VCP Pivot Marker
    # -------------------------
    vcp = detect_vcp(df)
    if vcp["VCP_Flag"]:
        pivot_idx = df.index[-1]
        pivot_price = vcp["Pivot"]

        marker_color = "green" if vcp["VolumeDryUp"] else "red"
        marker_text = f"VCP Stage {vcp['Stage']} | Vol Dry-Up: {vcp['VolumeDryUp']}"

        fig.add_trace(go.Scatter(
            x=[pivot_idx],
            y=[pivot_price],
            mode="markers+text",
            marker=dict(symbol="diamond", size=14, color=marker_color),
            text=[marker_text],
            textposition="top center",
            name="VCP Pivot"
        ))

    # -------------------------
    # Backtest Trade Markers
    # -------------------------
    if trades_df is not None and not trades_df.empty:
        # Entry markers
        fig.add_trace(go.Scatter(
            x=trades_df["EntryDate"],
            y=trades_df["EntryPrice"],
            mode="markers+text",
            marker=dict(symbol="triangle-up", size=12, color="lime"),
            text=["Entry"] * len(trades_df),
            textposition="bottom center",
            name="Entries"
        ))

        # Exit markers
        fig.add_trace(go.Scatter(
            x=trades_df["ExitDate"],
            y=trades_df["ExitPrice"],
            mode="markers+text",
            marker=dict(symbol="triangle-down", size=12, color="red"),
            text=trades_df["Result"],
            textposition="top center",
            name="Exits"
        ))

    # -------------------------
    # Layout
    # -------------------------
    fig.update_layout(
        title=f"{symbol} Chart with VCP + Trades",
        height=700,
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price"),
        showlegend=True
    )

    return fig
