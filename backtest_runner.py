"""
Backtest Runner Module
回測執行邏輯 - 負責執行單次回測和參數優化
"""
import pandas as pd
import streamlit as st
from itertools import product
from backtesting import Backtest


def run_single_backtest(df, strategy_class, params: dict, cash: int, commission: float) -> dict:
    """
    執行單次回測
    
    Args:
        df: K線數據 DataFrame
        strategy_class: 策略類別
        params: 策略參數
        cash: 初始資金
        commission: 手續費率
    
    Returns:
        dict: 包含 bt 和 stats 的結果字典
    """
    bt = Backtest(df, strategy_class, cash=cash, commission=commission, finalize_trades=True)
    stats = bt.run(**params)
    return {'bt': bt, 'stats': stats}


def run_optimization(df, strategy_class, optimize_params: dict, cash: int, 
                     commission: float, maximize: str, total_combinations: int) -> dict:
    """
    執行參數優化
    
    Args:
        df: K線數據 DataFrame
        strategy_class: 策略類別
        optimize_params: 參數範圍字典
        cash: 初始資金
        commission: 手續費率
        maximize: 優化目標 (e.g., "Return [%]")
        total_combinations: 總組合數
    
    Returns:
        dict: 包含優化結果的字典
    """
    bt = Backtest(df, strategy_class, cash=cash, commission=commission, finalize_trades=True)
    
    # 執行優化
    with st.spinner(f'🔄 正在優化 {total_combinations} 種參數組合，請耐心等候...'):
        try:
            # 嘗試返回熱力圖（只有2個參數時有效）
            best_stats, heatmap = bt.optimize(
                **optimize_params,
                maximize=maximize,
                return_heatmap=True
            )
            has_heatmap = True
        except Exception:
            # 多於2個參數時不返回熱力圖
            best_stats = bt.optimize(
                **optimize_params,
                maximize=maximize
            )
            heatmap = None
            has_heatmap = False
    
    # 遍歷所有參數組合獲取完整結果
    all_results = []
    param_keys = list(optimize_params.keys())
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
    
    return {
        'bt': bt,
        'best_stats': best_stats,
        'results_df': results_df,
        'heatmap': heatmap if has_heatmap else None,
        'param_keys': param_keys,
        'maximize': maximize
    }
