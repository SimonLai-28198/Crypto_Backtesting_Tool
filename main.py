"""
Crypto Backtester Pro - Main Application
加密貨幣量化回測系統主程式

重構後的精簡版本，僅負責：
- 頁面設定
- Session state 初始化
- 調用各模組函數
- 流程控制
"""
import streamlit as st

# 引入自定義模組
from data_loader import fetch_binance_data
from ui_components import (
    render_data_settings,
    render_strategy_selector,
    render_backtest_mode,
    render_single_params,
    render_optimize_params,
    render_capital_settings
)
from backtest_runner import run_single_backtest, run_optimization
from display import (
    display_backtest_metrics,
    display_trade_details,
    display_chart,
    display_data_info,
    display_optimization_results
)

# 頁面設定
st.set_page_config(layout="wide", page_title="Crypto Backtester Pro")


def init_session_state():
    """初始化 session_state"""
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None


def main():
    st.title("🚀 Python 加密貨幣量化回測系統")
    init_session_state()

    # === Sidebar: 設定區 ===
    st.sidebar.header("⚙️ 參數設定")
    
    # 1. 數據設定
    symbol, timeframe, start_date = render_data_settings()
    
    # 2. 策略選擇
    strategy_name, strategy_class = render_strategy_selector()
    
    # 3. 回測模式
    backtest_mode = render_backtest_mode()
    
    # 4. 參數設定 (根據模式)
    st.sidebar.markdown("---")
    if backtest_mode == "單次回測":
        params = render_single_params(strategy_name)
        optimize_params = None
        total_combinations = 0
        maximize = None
    else:
        params = None
        optimize_params, total_combinations, maximize = render_optimize_params(strategy_name)
    
    # 5. 資金設定
    cash, commission = render_capital_settings()

    # === Main Area: 執行區 ===
    
    if backtest_mode == "單次回測":
        # ---------- 單次回測模式 ----------
        if st.sidebar.button("開始回測", type="primary"):
            with st.spinner('正在從 Binance 下載數據，請稍候...'):
                df = fetch_binance_data(symbol, timeframe, str(start_date))

            if df.empty:
                st.error("❌ 無法獲取數據，請檢查日期或網絡連接。")
                st.session_state.backtest_results = None
            else:
                result = run_single_backtest(df, strategy_class, params, cash, commission)
                st.session_state.backtest_results = {
                    'df': df,
                    **result,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'start_date': start_date
                }
                st.session_state.optimization_results = None
        
        # 顯示結果
        if st.session_state.backtest_results is not None:
            r = st.session_state.backtest_results
            st.success(f"✅ 成功獲取 {len(r['df'])} 根 K 線")
            display_backtest_metrics(r['stats'])
            display_trade_details(r['stats'], r['symbol'], r['timeframe'])
            display_chart(r['bt'])
            display_data_info(r['df'], r['stats'], r['symbol'], r['timeframe'], r['start_date'])
    
    else:
        # ---------- 自動優化模式 ----------
        if st.sidebar.button("🚀 開始自動優化", type="primary"):
            with st.spinner('正在從 Binance 下載數據，請稍候...'):
                df = fetch_binance_data(symbol, timeframe, str(start_date))

            if df.empty:
                st.error("❌ 無法獲取數據，請檢查日期或網絡連接。")
                st.session_state.optimization_results = None
            else:
                opt_result = run_optimization(
                    df, strategy_class, optimize_params, 
                    cash, commission, maximize, total_combinations
                )
                st.session_state.optimization_results = {
                    'df': df,
                    **opt_result,
                    'symbol': symbol,
                    'timeframe': timeframe
                }
                st.session_state.backtest_results = None
        
        # 顯示結果
        if st.session_state.optimization_results is not None:
            r = st.session_state.optimization_results
            display_optimization_results(r, r['symbol'], r['timeframe'])


if __name__ == "__main__":
    main()
