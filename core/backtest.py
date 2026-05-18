import numpy as np
import pandas as pd
from core.indicators import detect_vcp
from core.data_loader import fetch_data

def run_backtest(df, symbol, risk_per_trade=1000):
    trades = []
    position = None

    # Precompute weekly data for multi‑timeframe filter
    df_weekly = fetch_data(symbol, interval="1wk", lookback="1y")
    vcp_weekly = detect_vcp(df_weekly)

    for i in range(1, len(df)):
        candle = df.iloc[i]

        # -------------------------
        # Entry Condition
        # -------------------------
        if candle.get('Signal') == "Bullish":
            vcp_daily = detect_vcp(df.iloc[:i])

            # Require BOTH daily + weekly VCP confirmation
            if (vcp_daily["VCP_Flag"] and vcp_daily["VolumeDryUp"] and
                vcp_weekly["VCP_Flag"] and vcp_weekly["VolumeDryUp"]):

                entry_price = candle['Open']
                stop_loss = entry_price - 1.5 * candle['ATR']
                target = entry_price + 2 * candle['ATR']

                risk_per_share = entry_price - stop_loss
                qty = int(risk_per_trade / risk_per_share)

                position = {
                    "EntryDate": candle.name,
                    "EntryPrice": entry_price,
                    "StopLoss": stop_loss,
                    "Target": target,
                    "Qty": qty,
                    "StageDaily": vcp_daily["Stage"],
                    "StageWeekly": vcp_weekly["Stage"]
                }

        # -------------------------
        # Exit Condition
        # -------------------------
        if position:
            if candle['Low'] <= position['StopLoss']:
                trades.append({
                    **position,
                    "ExitDate": candle.name,
                    "ExitPrice": position['StopLoss'],
                    "PnL": (position['StopLoss'] - position['EntryPrice']) * position['Qty'],
                    "Result": "Loss"
                })
                position = None
            elif candle['High'] >= position['Target']:
                trades.append({
                    **position,
                    "ExitDate": candle.name,
                    "ExitPrice": position['Target'],
                    "PnL": (position['Target'] - position['EntryPrice']) * position['Qty'],
                    "Result": "Win"
                })
                position = None

    return pd.DataFrame(trades)
