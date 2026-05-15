import plotly.graph_objects as go

from plotly.subplots import make_subplots


def institutional_chart(df, ticker):

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.03,
    )

    # =====================================================
    # CANDLESTICK
    # =====================================================

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    # =====================================================
    # EMAs
    # =====================================================

    for col, color in [
        ("EMA21", "cyan"),
        ("EMA50", "orange"),
        ("EMA200", "yellow"),
        ("AVWAP", "magenta"),
    ]:

        if col in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines",
                    name=col,
                    line=dict(
                        width=1.5,
                        color=color,
                    ),
                ),
                row=1,
                col=1,
            )

    # =====================================================
    # VOLUME
    # =====================================================

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
        ),
        row=2,
        col=1,
    )

    # =====================================================
    # STYLING
    # =====================================================

    fig.update_layout(
        template="plotly_dark",
        title=f"{ticker} — Institutional Dashboard",
        xaxis_rangeslider_visible=False,
        height=850,
        legend=dict(
            orientation="h",
        ),
    )

    return fig
