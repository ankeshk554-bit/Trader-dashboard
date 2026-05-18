import numpy as np
import pandas as pd
from core.indicators import detect_vcp

def run_backtest(df, risk_per_trade=1000):
    trades = []
    position = None

    for i in range(1, len(df)):
        candle = df.iloc[i]
        prev = df.iloc[i-1]

        # -------------------------
        # Entry Condition
        # -------------------------
        # Example: bullish divergence already detected in df['Signal']
        if candle['Signal'] == "Bullish":
            vcp = detect_vcp(df.iloc[:i])
            if vcp["VCP_Flag"] and vcp["VolumeDryUp"]:
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
                    "Stage": vcp["Stage"]
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
                    "Result": "Loss"
                })
                position = None
            elif candle['High'] >= position['Target']:
                trades.append({
                    **position,
                    "ExitDate": candle.name,
                    "ExitPrice": position['Target'],
                    "Result": "Win"
                })
                position = None

    return pd.DataFrame(trades)
