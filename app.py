from ui.layout import screener_tab, backtest_tab, quant_lab_tab
from core.screener import run_universe_scan   # ✅ corrected import

st.set_page_config(page_title="Trader Dashboard", layout="wide")

def main():
    st.title("📈 Trader Dashboard")

    tab1, tab2, tab3 = st.tabs(["Screener", "Backtest", "Quant Lab"])

    with tab1:
        screener_tab()

    with tab2:
        backtest_tab()

    with tab3:
        quant_lab_tab()

if __name__ == "__main__":
    main()
