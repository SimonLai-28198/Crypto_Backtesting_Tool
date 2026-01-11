"""
UI Components Module
側邊欄 UI 元件 - 負責渲染所有側邊欄控制項
"""
import streamlit as st
import pandas as pd
from strategies import SmaCross, RsiOscillator, SmaCrossATR


# 策略映射表
STRATEGY_MAP = {
    "SMA Cross (趨勢)": SmaCross,
    "RSI Mean Reversion (震盪)": RsiOscillator,
    "SMA Cross + ATR 停損 (進階)": SmaCrossATR
}


def render_data_settings():
    """
    渲染數據來源設定區
    Returns: (symbol, timeframe, start_date)
    """
    st.sidebar.subheader("1. 數據來源 (Binance)")
    symbol = st.sidebar.selectbox("交易對", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "DOGE/USDT"])
    timeframe = st.sidebar.selectbox("K線週期", ["15m", "30m", "1h", "4h", "1d"])
    start_date = st.sidebar.date_input("開始日期", pd.to_datetime("2024-01-01"))
    return symbol, timeframe, start_date


def render_strategy_selector():
    """
    渲染策略選擇區
    Returns: (strategy_name, strategy_class)
    """
    st.sidebar.subheader("2. 策略選擇")
    selected_strategy_name = st.sidebar.radio("選擇策略", list(STRATEGY_MAP.keys()))
    strategy_class = STRATEGY_MAP[selected_strategy_name]
    return selected_strategy_name, strategy_class


def render_backtest_mode():
    """
    渲染回測模式選擇
    Returns: backtest_mode ("單次回測" | "自動優化")
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("3. 回測模式")
    return st.sidebar.radio("選擇模式", ["單次回測", "自動優化"], horizontal=True)


def render_single_params(strategy_name: str) -> dict:
    """
    渲染單次回測的參數滑桿
    Args:
        strategy_name: 策略名稱
    Returns: params dict
    """
    st.sidebar.subheader("4. 策略參數")
    params = {}
    
    if strategy_name == "SMA Cross (趨勢)":
        params['n1'] = st.sidebar.slider("短均線 (n1)", 5, 50, 10)
        params['n2'] = st.sidebar.slider("長均線 (n2)", 20, 200, 50)
        
    elif strategy_name == "RSI Mean Reversion (震盪)":
        params['rsi_period'] = st.sidebar.slider("RSI 週期", 5, 30, 14)
        params['upper_bound'] = st.sidebar.slider("超買界線", 50, 95, 70)
        params['lower_bound'] = st.sidebar.slider("超賣界線", 5, 50, 30)
        
    elif strategy_name == "SMA Cross + ATR 停損 (進階)":
        st.sidebar.markdown("**均線參數**")
        params['n1'] = st.sidebar.slider("短均線 (n1)", 5, 50, 10)
        params['n2'] = st.sidebar.slider("長均線 (n2)", 20, 200, 50)
        st.sidebar.markdown("**ATR 停損參數**")
        params['atr_period'] = st.sidebar.slider("ATR 週期", 5, 30, 14)
        params['sl_multiplier'] = st.sidebar.slider("停損倍數 (ATR ×)", 0.5, 5.0, 2.0, step=0.5)
        params['tp_multiplier'] = st.sidebar.slider("停利倍數 (ATR ×)", 0.5, 10.0, 3.0, step=0.5)
    
    return params


def render_optimize_params(strategy_name: str):
    """
    渲染自動優化的參數範圍設定
    Args:
        strategy_name: 策略名稱
    Returns: (optimize_params, total_combinations, maximize)
    """
    st.sidebar.subheader("4. 參數優化範圍")
    optimize_params = {}
    
    if strategy_name == "SMA Cross (趨勢)":
        st.sidebar.markdown("**短均線 (n1)**")
        n1_min = st.sidebar.number_input("n1 最小值", 5, 50, 5, key="n1_min")
        n1_max = st.sidebar.number_input("n1 最大值", 5, 50, 30, key="n1_max")
        n1_step = st.sidebar.number_input("n1 步進值", 1, 10, 5, key="n1_step")
        
        st.sidebar.markdown("**長均線 (n2)**")
        n2_min = st.sidebar.number_input("n2 最小值", 20, 200, 20, key="n2_min")
        n2_max = st.sidebar.number_input("n2 最大值", 20, 200, 100, key="n2_max")
        n2_step = st.sidebar.number_input("n2 步進值", 5, 20, 10, key="n2_step")
        
        optimize_params['n1'] = range(n1_min, n1_max + 1, n1_step)
        optimize_params['n2'] = range(n2_min, n2_max + 1, n2_step)
        
    elif strategy_name == "RSI Mean Reversion (震盪)":
        st.sidebar.markdown("**RSI 週期**")
        rsi_min = st.sidebar.number_input("RSI 最小值", 5, 30, 7, key="rsi_min")
        rsi_max = st.sidebar.number_input("RSI 最大值", 5, 30, 21, key="rsi_max")
        rsi_step = st.sidebar.number_input("RSI 步進值", 1, 10, 7, key="rsi_step")
        
        st.sidebar.markdown("**超買界線**")
        ub_min = st.sidebar.number_input("超買最小值", 50, 95, 60, key="ub_min")
        ub_max = st.sidebar.number_input("超買最大值", 50, 95, 80, key="ub_max")
        ub_step = st.sidebar.number_input("超買步進值", 5, 20, 10, key="ub_step")
        
        st.sidebar.markdown("**超賣界線**")
        lb_min = st.sidebar.number_input("超賣最小值", 5, 50, 20, key="lb_min")
        lb_max = st.sidebar.number_input("超賣最大值", 5, 50, 40, key="lb_max")
        lb_step = st.sidebar.number_input("超賣步進值", 5, 20, 10, key="lb_step")
        
        optimize_params['rsi_period'] = range(rsi_min, rsi_max + 1, rsi_step)
        optimize_params['upper_bound'] = range(ub_min, ub_max + 1, ub_step)
        optimize_params['lower_bound'] = range(lb_min, lb_max + 1, lb_step)
        
    elif strategy_name == "SMA Cross + ATR 停損 (進階)":
        st.sidebar.markdown("**短均線 (n1)**")
        n1_min = st.sidebar.number_input("n1 最小值", 5, 50, 5, key="n1_min")
        n1_max = st.sidebar.number_input("n1 最大值", 5, 50, 20, key="n1_max")
        n1_step = st.sidebar.number_input("n1 步進值", 1, 10, 5, key="n1_step")
        
        st.sidebar.markdown("**長均線 (n2)**")
        n2_min = st.sidebar.number_input("n2 最小值", 20, 200, 30, key="n2_min")
        n2_max = st.sidebar.number_input("n2 最大值", 20, 200, 80, key="n2_max")
        n2_step = st.sidebar.number_input("n2 步進值", 5, 20, 10, key="n2_step")
        
        st.sidebar.markdown("**停損倍數**")
        sl_min = st.sidebar.number_input("停損最小值", 0.5, 5.0, 1.0, step=0.5, key="sl_min")
        sl_max = st.sidebar.number_input("停損最大值", 0.5, 5.0, 3.0, step=0.5, key="sl_max")
        sl_step = st.sidebar.number_input("停損步進值", 0.5, 2.0, 0.5, step=0.5, key="sl_step")
        
        optimize_params['n1'] = range(n1_min, n1_max + 1, n1_step)
        optimize_params['n2'] = range(n2_min, n2_max + 1, n2_step)
        optimize_params['sl_multiplier'] = [x / 10 for x in range(int(sl_min * 10), int(sl_max * 10) + 1, int(sl_step * 10))]
    
    # 計算總組合數
    total_combinations = 1
    for key, values in optimize_params.items():
        total_combinations *= len(list(values))
    st.sidebar.info(f"📊 總共 **{total_combinations}** 種參數組合")
    
    # 優化目標選擇
    st.sidebar.markdown("---")
    st.sidebar.subheader("5. 優化設定")
    maximize_options = {
        "總報酬率": "Return [%]",
        "夏普比率": "Sharpe Ratio",
        "勝率": "Win Rate [%]"
    }
    maximize_display = st.sidebar.selectbox("優化目標", list(maximize_options.keys()))
    maximize = maximize_options[maximize_display]
    
    return optimize_params, total_combinations, maximize


def render_capital_settings():
    """
    渲染資金與手續費設定
    Returns: (cash, commission)
    """
    st.sidebar.markdown("---")
    cash = st.sidebar.number_input("初始資金 (USDT)", value=100000, min_value=10000)
    commission = st.sidebar.number_input("手續費率 (0.001 = 0.1%)", value=0.001, step=0.0001, format="%.4f")
    return cash, commission
