import streamlit as st
import pandas as pd
import numpy as np
from backtesting import Backtest

# 引入我們自定義的模組
from data_loader import fetch_binance_data
from strategies import SmaCross, RsiOscillator, SmaCrossATR
from utils import render_plot

# 頁面設定
st.set_page_config(layout="wide", page_title="Crypto Backtester Pro")

def main():
    st.title("🚀 Python 加密貨幣量化回測系統")
    
    # 初始化 session_state 來保存回測結果
    if 'backtest_results' not in st.session_state:
        st.session_state.backtest_results = None
    if 'optimization_results' not in st.session_state:
        st.session_state.optimization_results = None

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
        "RSI Mean Reversion (震盪)": RsiOscillator,
        "SMA Cross + ATR 停損 (進階)": SmaCrossATR
    }
    selected_strategy_name = st.sidebar.radio("選擇策略", list(strategy_map.keys()))
    strategy_class = strategy_map[selected_strategy_name]

    # 3. 回測模式選擇 [新增]
    st.sidebar.markdown("---")
    st.sidebar.subheader("3. 回測模式")
    backtest_mode = st.sidebar.radio("選擇模式", ["單次回測", "自動優化"], horizontal=True)

    # 4. 動態參數調整 (根據選擇的策略和模式顯示不同控制項)
    st.sidebar.markdown("---")
    
    params = {}
    optimize_params = {}
    
    if backtest_mode == "單次回測":
        st.sidebar.subheader("4. 策略參數")
        if selected_strategy_name == "SMA Cross (趨勢)":
            params['n1'] = st.sidebar.slider("短均線 (n1)", 5, 50, 10)
            params['n2'] = st.sidebar.slider("長均線 (n2)", 20, 200, 50)
        elif selected_strategy_name == "RSI Mean Reversion (震盪)":
            params['rsi_period'] = st.sidebar.slider("RSI 週期", 5, 30, 14)
            params['upper_bound'] = st.sidebar.slider("超買界線", 50, 95, 70)
            params['lower_bound'] = st.sidebar.slider("超賣界線", 5, 50, 30)
        elif selected_strategy_name == "SMA Cross + ATR 停損 (進階)":
            st.sidebar.markdown("**均線參數**")
            params['n1'] = st.sidebar.slider("短均線 (n1)", 5, 50, 10)
            params['n2'] = st.sidebar.slider("長均線 (n2)", 20, 200, 50)
            st.sidebar.markdown("**ATR 停損參數**")
            params['atr_period'] = st.sidebar.slider("ATR 週期", 5, 30, 14)
            params['sl_multiplier'] = st.sidebar.slider("停損倍數 (ATR ×)", 0.5, 5.0, 2.0, step=0.5)
            params['tp_multiplier'] = st.sidebar.slider("停利倍數 (ATR ×)", 0.5, 10.0, 3.0, step=0.5)
    else:
        # 自動優化模式 - 顯示參數範圍設定
        st.sidebar.subheader("4. 參數優化範圍")
        
        if selected_strategy_name == "SMA Cross (趨勢)":
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
            
        elif selected_strategy_name == "RSI Mean Reversion (震盪)":
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
            
        elif selected_strategy_name == "SMA Cross + ATR 停損 (進階)":
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

    # 資金與手續費
    st.sidebar.markdown("---")
    cash = st.sidebar.number_input("初始資金 (USDT)", value=100000, min_value=10000)
    commission = st.sidebar.number_input("手續費率 (0.001 = 0.1%)", value=0.001, step=0.0001, format="%.4f")

    # --- Main Area: 執行區 ---
    
    if backtest_mode == "單次回測":
        # ========== 單次回測模式 ==========
        if st.sidebar.button("開始回測", type="primary"):
            with st.spinner('正在從 Binance 下載數據，請稍候...'):
                df = fetch_binance_data(symbol, timeframe, str(start_date))

            if df.empty:
                st.error("❌ 無法獲取數據，請檢查日期或網絡連接。")
                st.session_state.backtest_results = None
            else:
                bt = Backtest(df, strategy_class, cash=cash, commission=commission, finalize_trades=True)
                stats = bt.run(**params)
                
                st.session_state.backtest_results = {
                    'df': df,
                    'bt': bt,
                    'stats': stats,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'start_date': start_date
                }
                st.session_state.optimization_results = None  # 清除優化結果
        
        # 顯示單次回測結果
        if st.session_state.backtest_results is not None:
            results = st.session_state.backtest_results
            df = results['df']
            bt = results['bt']
            stats = results['stats']
            symbol_saved = results['symbol']
            timeframe_saved = results['timeframe']
            start_date_saved = results['start_date']
            
            st.success(f"✅ 成功獲取 {len(df)} 根 K 線")

            st.markdown("### 📊 回測績效")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("總報酬率 (Return)", f"{stats['Return [%]']:.2f}%")
            col2.metric("夏普比率 (Sharpe)", f"{stats['Sharpe Ratio']:.2f}")
            col3.metric("最大回撤 (MDD)", f"{stats['Max. Drawdown [%]']:.2f}%")
            col4.metric("勝率 (Win Rate)", f"{stats['Win Rate [%]']:.2f}%")

            with st.expander("查看詳細交易數據"):
                st.subheader("策略參數")
                st.dataframe(stats._strategy._params)
                
                st.subheader("📋 交易明細列表")
                if len(stats._trades) > 0:
                    trades_df = stats._trades
                    st.dataframe(
                        trades_df,
                        width='stretch',
                        column_config={
                            "EntryTime": st.column_config.DatetimeColumn("進場時間", format="YYYY-MM-DD HH:mm"),
                            "ExitTime": st.column_config.DatetimeColumn("出場時間", format="YYYY-MM-DD HH:mm"),
                            "ReturnPct": st.column_config.NumberColumn("報酬率 (%)", format="%.2f%%"),
                            "PnL": st.column_config.NumberColumn("損益", format="$%.2f"),
                        }
                    )
                    
                    trades_csv = trades_df.to_csv()
                    st.download_button(
                        label="📥 下載交易明細 (CSV)",
                        data=trades_csv,
                        file_name=f"trades_{symbol_saved.replace('/', '_')}_{timeframe_saved}.csv",
                        mime="text/csv",
                        key="download_trades"
                    )
                else:
                    st.warning("無交易記錄")
                
                st.subheader("完整統計數據")
                stats_dict = {}
                for key, value in stats.items():
                    if isinstance(value, pd.Timedelta):
                        stats_dict[key] = str(value)
                    else:
                        stats_dict[key] = value
                st.json(stats_dict)

            st.markdown("### 🕯️ 互動式 K 線圖")
            with st.spinner('正在渲染圖表...'):
                render_plot(bt)

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
            
            csv = df.to_csv()
            st.download_button(
                label="📥 下載 K 線數據 (CSV)",
                data=csv,
                file_name=f"{symbol_saved.replace('/', '_')}_{timeframe_saved}_{start_date_saved}.csv",
                mime="text/csv",
                key="download_kline"
            )
    
    else:
        # ========== 自動優化模式 ==========
        if st.sidebar.button("🚀 開始自動優化", type="primary"):
            with st.spinner('正在從 Binance 下載數據，請稍候...'):
                df = fetch_binance_data(symbol, timeframe, str(start_date))

            if df.empty:
                st.error("❌ 無法獲取數據，請檢查日期或網絡連接。")
                st.session_state.optimization_results = None
            else:
                bt = Backtest(df, strategy_class, cash=cash, commission=commission, finalize_trades=True)
                
                # 執行優化
                with st.spinner(f'🔄 正在優化 {total_combinations} 種參數組合，請耐心等候...'):
                    try:
                        # 嘗試返回熱力圖（只有2個參數時有效）
                        stats, heatmap = bt.optimize(
                            **optimize_params,
                            maximize=maximize,
                            return_heatmap=True
                        )
                        has_heatmap = True
                    except Exception:
                        # 多於2個參數時不返回熱力圖
                        stats = bt.optimize(
                            **optimize_params,
                            maximize=maximize
                        )
                        heatmap = None
                        has_heatmap = False
                
                # 獲取所有優化結果（使用 return_stats=True 重新運行以獲取排行榜）
                # 由於 optimize 只返回最佳結果，我們手動遍歷獲取 top 結果
                all_results = []
                param_keys = list(optimize_params.keys())
                
                # 生成所有參數組合
                from itertools import product
                param_values = [list(optimize_params[k]) for k in param_keys]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, combo in enumerate(product(*param_values)):
                    param_dict = dict(zip(param_keys, combo))
                    try:
                        result = bt.run(**param_dict)
                        all_results.append({
                            **param_dict,
                            'Return [%]': result['Return [%]'],
                            'Sharpe Ratio': result['Sharpe Ratio'],
                            'Max. Drawdown [%]': result['Max. Drawdown [%]'],
                            'Win Rate [%]': result['Win Rate [%]'],
                            '# Trades': result['# Trades']
                        })
                    except Exception:
                        pass
                    
                    # 更新進度條
                    progress = (i + 1) / total_combinations
                    progress_bar.progress(progress)
                    status_text.text(f"已完成 {i + 1}/{total_combinations} 組合")
                
                progress_bar.empty()
                status_text.empty()
                
                # 轉換為 DataFrame 並排序
                results_df = pd.DataFrame(all_results)
                results_df = results_df.sort_values(by=maximize, ascending=False).reset_index(drop=True)
                
                st.session_state.optimization_results = {
                    'df': df,
                    'bt': bt,
                    'best_stats': stats,
                    'results_df': results_df,
                    'heatmap': heatmap if has_heatmap else None,
                    'param_keys': param_keys,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'maximize': maximize
                }
                st.session_state.backtest_results = None  # 清除單次結果
        
        # 顯示優化結果
        if st.session_state.optimization_results is not None:
            opt_results = st.session_state.optimization_results
            results_df = opt_results['results_df']
            best_stats = opt_results['best_stats']
            param_keys = opt_results['param_keys']
            heatmap = opt_results['heatmap']
            
            st.success(f"✅ 優化完成！共測試 {len(results_df)} 種參數組合")
            
            # 最佳參數
            st.markdown("### 🏆 最佳參數組合")
            best_row = results_df.iloc[0]
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("**最佳參數：**")
                for key in param_keys:
                    st.write(f"- **{key}**: {best_row[key]}")
            
            with col2:
                metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                metrics_col1.metric("總報酬率", f"{best_row['Return [%]']:.2f}%")
                metrics_col2.metric("夏普比率", f"{best_row['Sharpe Ratio']:.2f}")
                metrics_col3.metric("最大回撤", f"{best_row['Max. Drawdown [%]']:.2f}%")
                metrics_col4.metric("勝率", f"{best_row['Win Rate [%]']:.2f}%")
            
            # 參數優化排行榜
            st.markdown("### 📊 參數優化排行榜 (Top 20)")
            display_df = results_df.head(20).copy()
            display_df.index = range(1, len(display_df) + 1)
            display_df.index.name = "排名"
            
            st.dataframe(
                display_df,
                column_config={
                    "Return [%]": st.column_config.NumberColumn("報酬率 (%)", format="%.2f%%"),
                    "Sharpe Ratio": st.column_config.NumberColumn("夏普比率", format="%.2f"),
                    "Max. Drawdown [%]": st.column_config.NumberColumn("最大回撤 (%)", format="%.2f%%"),
                    "Win Rate [%]": st.column_config.NumberColumn("勝率 (%)", format="%.2f%%"),
                    "# Trades": st.column_config.NumberColumn("交易次數", format="%d"),
                },
                width='stretch'
            )
            
            # 下載完整結果
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                label="📥 下載完整優化結果 (CSV)",
                data=csv_data,
                file_name=f"optimization_{opt_results['symbol'].replace('/', '_')}_{opt_results['timeframe']}.csv",
                mime="text/csv",
                key="download_optimization"
            )
            
            # 熱力圖 (僅限2參數)
            if heatmap is not None and len(param_keys) == 2:
                st.markdown("### 🔥 參數熱力圖")
                st.write(f"顯示 **{param_keys[0]}** vs **{param_keys[1]}** 對 **{opt_results['maximize']}** 的影響")
                
                # 使用 Streamlit 內建的熱力圖功能
                import plotly.express as px
                
                # 重塑數據為熱力圖格式
                pivot_df = results_df.pivot_table(
                    index=param_keys[0],
                    columns=param_keys[1],
                    values=opt_results['maximize']
                )
                
                fig = px.imshow(
                    pivot_df,
                    labels=dict(x=param_keys[1], y=param_keys[0], color=opt_results['maximize']),
                    aspect="auto",
                    color_continuous_scale="RdYlGn"
                )
                fig.update_layout(
                    title=f"{param_keys[0]} vs {param_keys[1]} 優化熱力圖",
                    xaxis_title=param_keys[1],
                    yaxis_title=param_keys[0]
                )
                st.plotly_chart(fig, width='stretch')

if __name__ == "__main__":
    main()
