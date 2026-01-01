import streamlit as st
import pandas as pd
from backtesting import Backtest

# 引入我們自定義的模組
from data_loader import fetch_binance_data
from strategies import SmaCross, RsiOscillator
from utils import render_plot

# 頁面設定
st.set_page_config(layout="wide", page_title="Crypto Backtester Pro")

def main():
    st.title("🚀 Python 加密貨幣量化回測系統")

    # --- Sidebar: 設定區 ---
    st.sidebar.header("⚙️ 參數設定")

    # 1. 數據設定
    st.sidebar.subheader("1. 數據來源 (Binance)")
    symbol = st.sidebar.selectbox("交易對", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "DOGE/USDT"])
    timeframe = st.sidebar.selectbox("K線週期", ["15m", "30m", "1h", "4h", "1d"])
    start_date = st.sidebar.date_input("開始日期", pd.to_datetime("2024-01-01"))
    
    # 2. 策略選擇
    st.sidebar.subheader("2. 策略選擇")
    strategy_map = {
        "SMA Cross (趨勢)": SmaCross,
        "RSI Mean Reversion (震盪)": RsiOscillator
    }
    selected_strategy_name = st.sidebar.radio("選擇策略", list(strategy_map.keys()))
    strategy_class = strategy_map[selected_strategy_name]

    # 3. 動態參數調整 (根據選擇的策略顯示不同滑桿)
    st.sidebar.markdown("---")
    st.sidebar.subheader("3. 策略參數優化")
    params = {}
    
    if selected_strategy_name == "SMA Cross (趨勢)":
        params['n1'] = st.sidebar.slider("短均線 (n1)", 5, 50, 10)
        params['n2'] = st.sidebar.slider("長均線 (n2)", 20, 200, 50)
    elif selected_strategy_name == "RSI Mean Reversion (震盪)":
        params['rsi_period'] = st.sidebar.slider("RSI 週期", 5, 30, 14)
        params['upper_bound'] = st.sidebar.slider("超買界線", 50, 95, 70)
        params['lower_bound'] = st.sidebar.slider("超賣界線", 5, 50, 30)

    # 4. 資金與手續費
    st.sidebar.markdown("---")
    cash = st.sidebar.number_input("初始資金 (USDT)", value=10000)
    commission = st.sidebar.number_input("手續費率 (0.001 = 0.1%)", value=0.001, step=0.0001, format="%.4f")

    # --- Main Area: 執行區 ---
    if st.sidebar.button("開始回測", type="primary"):
        
        # A. 獲取數據
        with st.spinner('正在從 Binance 下載數據，請稍候...'):
            df = fetch_binance_data(symbol, timeframe, str(start_date))

        if df.empty:
            st.error("❌ 無法獲取數據，請檢查日期或網絡連接。")
            return

        st.success(f"✅ 成功獲取 {len(df)} 根 K 線")

        # B. 執行回測
        bt = Backtest(df, strategy_class, cash=cash, commission=commission)
        stats = bt.run(**params)

        # C. 顯示指標 (Metrics)
        st.markdown("### 📊 回測績效")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("總報酬率 (Return)", f"{stats['Return [%]']:.2f}%")
        col2.metric("夏普比率 (Sharpe)", f"{stats['Sharpe Ratio']:.2f}")
        col3.metric("最大回撤 (MDD)", f"{stats['Max. Drawdown [%]']:.2f}%")
        col4.metric("勝率 (Win Rate)", f"{stats['Win Rate [%]']:.2f}%")

        # D. 顯示詳細數據
        with st.expander("查看詳細交易數據"):
            st.dataframe(stats._strategy._params) # 顯示參數
            st.write(stats)

        # E. 繪製互動圖表
        st.markdown("### 🕯️ 互動式 K 線圖")
        with st.spinner('正在渲染圖表...'):
            render_plot(bt)

if __name__ == "__main__":
    main()