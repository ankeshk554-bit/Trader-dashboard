import numpy as np
import pandas as pd
from core.indicators import detect_vcp

def run_backtest(df, risk_per_trade=1000):
    trades = []
    position = None

    for i in range(1, len(df)):
        candle = df.iloc[i]

        # Example entry: bullish divergence + VCP
        if candle.get('Signal') == "Bullish":
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

        # Exit logic
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

# -------------------------
# 🚀 Performance Metrics
# -------------------------
def performance_metrics(trades_df):
    if trades_df.empty:
        return {"WinRate": 0, "Expectancy": 0, "AvgR": 0, "TotalPnL": 0}

    wins = trades_df[trades_df['Result'] == "Win"]
    losses = trades_df[trades_df['Result'] == "Loss"]

    win_rate = len(wins) / len(trades_df) * 100
    total_pnl = trades_df['PnL'].sum()

    # R multiples (PnL / risk per trade)
    trades_df['R'] = trades_df['PnL'] / 1000
    avg_r = trades_df['R'].mean()

    # Expectancy = (Win% * AvgWin) - (Loss% * AvgLoss)
    avg_win = wins['PnL'].mean() if not wins.empty else 0
    avg_loss = abs(losses['PnL'].mean()) if not losses.empty else 0
    expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)

    return {
        "WinRate": round(win_rate, 2),
        "Expectancy": round(expectancy, 2),
        "AvgR": round(avg_r, 2),
        "TotalPnL": round(total_pnl, 2)
    }
