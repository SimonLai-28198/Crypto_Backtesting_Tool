"""
Display Module
結果顯示元件 - 負責渲染回測結果和優化結果
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import render_plot


def display_backtest_metrics(stats):
    """
    顯示回測績效指標
    """
    st.markdown("### 📊 回測績效")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總報酬率 (Return)", f"{stats['Return [%]']:.2f}%")
    col2.metric("夏普比率 (Sharpe)", f"{stats['Sharpe Ratio']:.2f}")
    col3.metric("最大回撤 (MDD)", f"{stats['Max. Drawdown [%]']:.2f}%")
    col4.metric("勝率 (Win Rate)", f"{stats['Win Rate [%]']:.2f}%")


def display_trade_details(stats, symbol: str, timeframe: str):
    """
    顯示詳細交易數據（在 expander 內）
    """
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
                file_name=f"trades_{symbol.replace('/', '_')}_{timeframe}.csv",
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


def display_chart(bt):
    """
    顯示互動式 K 線圖
    """
    st.markdown("### 🕯️ 互動式 K 線圖")
    with st.spinner('正在渲染圖表...'):
        render_plot(bt)


def display_data_info(df, stats, symbol: str, timeframe: str, start_date):
    """
    顯示數據詳情和下載按鈕
    """
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
        file_name=f"{symbol.replace('/', '_')}_{timeframe}_{start_date}.csv",
        mime="text/csv",
        key="download_kline"
    )


def display_optimization_results(opt_results: dict, symbol: str, timeframe: str):
    """
    顯示優化結果
    """
    results_df = opt_results['results_df']
    param_keys = opt_results['param_keys']
    heatmap = opt_results['heatmap']
    maximize = opt_results['maximize']
    
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
        file_name=f"optimization_{symbol.replace('/', '_')}_{timeframe}.csv",
        mime="text/csv",
        key="download_optimization"
    )
    
    # 熱力圖 (僅限2參數)
    if heatmap is not None and len(param_keys) == 2:
        display_heatmap(results_df, param_keys, maximize)


def display_heatmap(results_df, param_keys: list, maximize: str):
    """
    顯示參數熱力圖
    """
    st.markdown("### 🔥 參數熱力圖")
    st.write(f"顯示 **{param_keys[0]}** vs **{param_keys[1]}** 對 **{maximize}** 的影響")
    
    # 重塑數據為熱力圖格式
    pivot_df = results_df.pivot_table(
        index=param_keys[0],
        columns=param_keys[1],
        values=maximize
    )
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x=param_keys[1], y=param_keys[0], color=maximize),
        aspect="auto",
        color_continuous_scale="RdYlGn"
    )
    fig.update_layout(
        title=f"{param_keys[0]} vs {param_keys[1]} 優化熱力圖",
        xaxis_title=param_keys[1],
        yaxis_title=param_keys[0]
    )
    st.plotly_chart(fig, width='stretch')
