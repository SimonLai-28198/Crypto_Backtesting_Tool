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
    cash = st.sidebar.number_input("初始資金 (USDT)", value=100000, min_value=10000)
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
        # finalize_trades=True: 回測結束時自動平倉所有未平倉交易，將其計入統計
        bt = Backtest(df, strategy_class, cash=cash, commission=commission, finalize_trades=True)
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
            # 顯示策略參數
            st.subheader("策略參數")
            st.dataframe(stats._strategy._params)
            
            # 顯示交易明細
            st.subheader("📋 交易明細列表")
            if len(stats._trades) > 0:
                trades_df = stats._trades
                st.dataframe(
                    trades_df,
                    width='stretch',  # 使用新的 width 參數替代 use_container_width
                    column_config={
                        "EntryTime": st.column_config.DatetimeColumn("進場時間", format="YYYY-MM-DD HH:mm"),
                        "ExitTime": st.column_config.DatetimeColumn("出場時間", format="YYYY-MM-DD HH:mm"),
                        "ReturnPct": st.column_config.NumberColumn("報酬率 (%)", format="%.2f%%"),
                        "PnL": st.column_config.NumberColumn("損益", format="$%.2f"),
                    }
                )
                
                # 提供交易明細 CSV 下載
                trades_csv = trades_df.to_csv()
                st.download_button(
                    label="📥 下載交易明細 (CSV)",
                    data=trades_csv,
                    file_name=f"trades_{symbol.replace('/', '_')}_{timeframe}.csv",
                    mime="text/csv",
                )
            else:
                st.warning("無交易記錄")
            
            # 顯示完整統計數據
            st.subheader("完整統計數據")
            # 轉換 stats 為字典，避免 Timedelta 序列化問題
            stats_dict = {}
            for key, value in stats.items():
                if isinstance(value, pd.Timedelta):
                    stats_dict[key] = str(value)
                else:
                    stats_dict[key] = value
            st.json(stats_dict)

        # E. 繪製互動圖表
        st.markdown("### 🕯️ 互動式 K 線圖")
        with st.spinner('正在渲染圖表...'):
            render_plot(bt)

        # 在 main.py 的回測後加入
        st.markdown("### 📋 數據詳情")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **K 線總數**: {len(df)} 根  
            **第一根 K 棒時間**: {df.index[0]}  
            **最後一根 K 棒時間**: {df.index[-1]}  
            """)
        
        with col2:
            st.info(f"""
            **第一根 K 棒收盤價**: ${df['Close'].iloc[0]:.2f}  
            **最後一根 K 棒收盤價**: ${df['Close'].iloc[-1]:.2f}  
            **總交易次數**: {len(stats._trades)} 筆
            """)
        
        # 提供 CSV 下載功能
        csv = df.to_csv()
        st.download_button(
            label="📥 下載 K 線數據 (CSV)",
            data=csv,
            file_name=f"{symbol.replace('/', '_')}_{timeframe}_{start_date}.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()