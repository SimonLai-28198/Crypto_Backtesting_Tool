"""
UI Components Module
側邊欄 UI 元件 - 負責渲染所有側邊欄控制項
"""
import streamlit as st
import pandas as pd
from strategies import SmaCross, RsiOscillator, SmaCrossATR, LuciTechEMA, LuciTechEMAShort, EMABandpassCombo, RSIAdaptiveT3Squeeze


# 策略映射表
STRATEGY_MAP = {
    "SMA Cross (趨勢)": SmaCross,
    "RSI Mean Reversion (震盪)": RsiOscillator,
    "SMA Cross + ATR 停損 (進階)": SmaCrossATR,
    "LuciTech EMA (單向)": LuciTechEMA,
    "LuciTech EMA (雙向)": LuciTechEMAShort,
    "EMA + 帶通濾波器 (組合)": EMABandpassCombo,
    "RSI T3 + 擠壓動量 (進階)": RSIAdaptiveT3Squeeze
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
    
    elif strategy_name == "LuciTech EMA (單向)" or strategy_name == "LuciTech EMA (雙向)":
        st.sidebar.markdown("**EMA 參數**")
        params['ema_period'] = st.sidebar.slider("EMA 週期", 5, 50, 15)
        st.sidebar.markdown("**停損設定**")
        params['atr_period'] = st.sidebar.slider("ATR 週期", 5, 30, 14)
        params['atr_multiplier'] = st.sidebar.slider("ATR 停損倍數", 0.5, 5.0, 1.5, step=0.5)
        st.sidebar.markdown("**風險報酬**")
        params['risk_reward'] = st.sidebar.slider("風險報酬比", 1.0, 5.0, 2.0, step=0.5)
    
    elif strategy_name == "EMA + 帶通濾波器 (組合)":
        st.sidebar.markdown("**EMA 參數**")
        params['ema_fast_len'] = st.sidebar.slider("快速 EMA 週期", 1, 10, 2)
        params['ema_slow_len'] = st.sidebar.slider("慢速 EMA 週期", 10, 50, 20)
        st.sidebar.markdown("**帶通濾波器參數**")
        params['bpf_len'] = st.sidebar.slider("BPF 週期", 5, 50, 20)
        params['bpf_delta'] = st.sidebar.slider("BPF Delta", 0.1, 1.0, 0.5, step=0.1)
        params['bpf_sell_zone'] = st.sidebar.slider("BPF 賣出區", 0.0, 20.0, 5.0, step=0.5)
        params['bpf_buy_zone'] = st.sidebar.slider("BPF 買入區", -20.0, 0.0, -5.0, step=0.5)
        st.sidebar.markdown("**其他設定**")
        params['reverse'] = st.sidebar.checkbox("反向訊號", value=False)
    
    elif strategy_name == "RSI T3 + 擠壓動量 (進階)":
        st.sidebar.markdown("**T3 參數**")
        params['rsi_len'] = st.sidebar.slider("RSI 週期", 5, 30, 14)
        params['t3_min_len'] = st.sidebar.slider("T3 最小週期", 2, 20, 5)
        params['t3_max_len'] = st.sidebar.slider("T3 最大週期", 20, 100, 50)
        params['t3_volume_factor'] = st.sidebar.slider("T3 體積因子", 0.1, 1.5, 0.7, step=0.1)
        st.sidebar.markdown("**Squeeze 參數**")
        params['bb_length'] = st.sidebar.slider("布林帶週期", 10, 50, 27)
        params['bb_mult'] = st.sidebar.slider("布林帶倍數", 1.0, 3.0, 2.0, step=0.5)
        params['kc_length'] = st.sidebar.slider("Keltner 週期", 10, 50, 20)
        params['kc_mult'] = st.sidebar.slider("Keltner 倍數", 1.0, 3.0, 1.5, step=0.5)
    
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
    
    elif strategy_name == "LuciTech EMA (風險管理)":
        st.sidebar.markdown("**EMA 週期**")
        ema_min = st.sidebar.number_input("EMA 最小值", 5, 50, 10, key="ema_min")
        ema_max = st.sidebar.number_input("EMA 最大值", 5, 50, 25, key="ema_max")
        ema_step = st.sidebar.number_input("EMA 步進值", 1, 10, 5, key="ema_step")
        
        st.sidebar.markdown("**ATR 停損倍數**")
        atr_m_min = st.sidebar.number_input("ATR倍數最小值", 0.5, 5.0, 1.0, step=0.5, key="atr_m_min")
        atr_m_max = st.sidebar.number_input("ATR倍數最大值", 0.5, 5.0, 2.5, step=0.5, key="atr_m_max")
        atr_m_step = st.sidebar.number_input("ATR倍數步進值", 0.5, 2.0, 0.5, step=0.5, key="atr_m_step")
        
        st.sidebar.markdown("**風險報酬比**")
        rr_min = st.sidebar.number_input("RR 最小值", 1.0, 5.0, 1.5, step=0.5, key="rr_min")
        rr_max = st.sidebar.number_input("RR 最大值", 1.0, 5.0, 3.0, step=0.5, key="rr_max")
        rr_step = st.sidebar.number_input("RR 步進值", 0.5, 2.0, 0.5, step=0.5, key="rr_step")
        
        optimize_params['ema_period'] = range(ema_min, ema_max + 1, ema_step)
        optimize_params['atr_multiplier'] = [x / 10 for x in range(int(atr_m_min * 10), int(atr_m_max * 10) + 1, int(atr_m_step * 10))]
        optimize_params['risk_reward'] = [x / 10 for x in range(int(rr_min * 10), int(rr_max * 10) + 1, int(rr_step * 10))]
    
    elif strategy_name == "LuciTech EMA (雙向)":
        st.sidebar.markdown("**EMA 週期**")
        ema_min = st.sidebar.number_input("EMA 最小值", 5, 50, 10, key="ema_min")
        ema_max = st.sidebar.number_input("EMA 最大值", 5, 50, 25, key="ema_max")
        ema_step = st.sidebar.number_input("EMA 步進值", 1, 10, 5, key="ema_step")
        
        st.sidebar.markdown("**ATR 停損倍數**")
        atr_m_min = st.sidebar.number_input("ATR倍數最小值", 0.5, 5.0, 1.0, step=0.5, key="atr_m_min")
        atr_m_max = st.sidebar.number_input("ATR倍數最大值", 0.5, 5.0, 2.5, step=0.5, key="atr_m_max")
        atr_m_step = st.sidebar.number_input("ATR倍數步進值", 0.5, 2.0, 0.5, step=0.5, key="atr_m_step")
        
        st.sidebar.markdown("**風險報酬比**")
        rr_min = st.sidebar.number_input("RR 最小值", 1.0, 5.0, 1.5, step=0.5, key="rr_min")
        rr_max = st.sidebar.number_input("RR 最大值", 1.0, 5.0, 3.0, step=0.5, key="rr_max")
        rr_step = st.sidebar.number_input("RR 步進值", 0.5, 2.0, 0.5, step=0.5, key="rr_step")
        
        optimize_params['ema_period'] = range(ema_min, ema_max + 1, ema_step)
        optimize_params['atr_multiplier'] = [x / 10 for x in range(int(atr_m_min * 10), int(atr_m_max * 10) + 1, int(atr_m_step * 10))]
        optimize_params['risk_reward'] = [x / 10 for x in range(int(rr_min * 10), int(rr_max * 10) + 1, int(rr_step * 10))]
    
    elif strategy_name == "EMA + 帶通濾波器 (組合)":
        st.sidebar.markdown("**快速 EMA 週期**")
        ema_fast_min = st.sidebar.number_input("快速EMA 最小值", 1, 10, 1, key="ema_fast_min")
        ema_fast_max = st.sidebar.number_input("快速EMA 最大值", 1, 10, 5, key="ema_fast_max")
        ema_fast_step = st.sidebar.number_input("快速EMA 步進值", 1, 5, 1, key="ema_fast_step")
        
        st.sidebar.markdown("**慢速 EMA 週期**")
        ema_slow_min = st.sidebar.number_input("慢速EMA 最小值", 10, 50, 15, key="ema_slow_min")
        ema_slow_max = st.sidebar.number_input("慢速EMA 最大值", 10, 50, 30, key="ema_slow_max")
        ema_slow_step = st.sidebar.number_input("慢速EMA 步進值", 1, 10, 5, key="ema_slow_step")
        
        st.sidebar.markdown("**帶通濾波器週期**")
        bpf_len_min = st.sidebar.number_input("BPF 週期最小值", 5, 50, 15, key="bpf_len_min")
        bpf_len_max = st.sidebar.number_input("BPF 週期最大值", 5, 50, 30, key="bpf_len_max")
        bpf_len_step = st.sidebar.number_input("BPF 週期步進值", 1, 10, 5, key="bpf_len_step")
        
        optimize_params['ema_fast_len'] = range(ema_fast_min, ema_fast_max + 1, ema_fast_step)
        optimize_params['ema_slow_len'] = range(ema_slow_min, ema_slow_max + 1, ema_slow_step)
        optimize_params['bpf_len'] = range(bpf_len_min, bpf_len_max + 1, bpf_len_step)
    
    elif strategy_name == "RSI T3 + 擠壓動量 (進階)":
        st.sidebar.markdown("**RSI 週期**")
        rsi_min = st.sidebar.number_input("RSI 最小值", 5, 30, 10, key="rsi_min")
        rsi_max = st.sidebar.number_input("RSI 最大值", 5, 30, 21, key="rsi_max")
        rsi_step = st.sidebar.number_input("RSI 步進值", 1, 10, 7, key="rsi_step")
        
        st.sidebar.markdown("**布林帶週期**")
        bb_min = st.sidebar.number_input("BB 週期最小值", 10, 50, 20, key="bb_min")
        bb_max = st.sidebar.number_input("BB 週期最大值", 10, 50, 35, key="bb_max")
        bb_step = st.sidebar.number_input("BB 週期步進值", 1, 10, 5, key="bb_step")
        
        st.sidebar.markdown("**Keltner 週期**")
        kc_min = st.sidebar.number_input("KC 週期最小值", 10, 50, 15, key="kc_min")
        kc_max = st.sidebar.number_input("KC 週期最大值", 10, 50, 30, key="kc_max")
        kc_step = st.sidebar.number_input("KC 週期步進值", 1, 10, 5, key="kc_step")
        
        optimize_params['rsi_len'] = range(rsi_min, rsi_max + 1, rsi_step)
        optimize_params['bb_length'] = range(bb_min, bb_max + 1, bb_step)
        optimize_params['kc_length'] = range(kc_min, kc_max + 1, kc_step)
    
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
