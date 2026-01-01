import ccxt
import pandas as pd
import streamlit as st
import time

@st.cache_data(ttl=3600)
def fetch_binance_data(symbol, timeframe, start_date_str):
    """
    從 Binance 獲取歷史 K 線數據，並處理分頁 (Pagination)。
    """
    exchange = ccxt.binance()
    
    # 解析起始時間
    since = exchange.parse8601(f"{start_date_str}T00:00:00Z")
    
    all_ohlcv = []
    limit = 1000  # Binance 單次請求上限
    
    # 建立一個進度顯示區
    status_text = st.empty()
    
    while True:
        try:
            current_date = exchange.iso8601(since).split('T')[0]
            status_text.text(f"📥 正在下載數據... 目前進度: {current_date}")
            
            # 抓取數據
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            
            if not ohlcv:
                break
                
            all_ohlcv.extend(ohlcv)
            
            # 更新下一次抓取的起始時間 (最後一筆時間 + 1ms)
            since = ohlcv[-1][0] + 1
            
            # 如果抓到的數量少於 limit，表示已經抓到最新了
            if len(ohlcv) < limit:
                break
            
            # 避免觸發 Rate Limit (稍微停頓)
            time.sleep(0.1)
                
        except Exception as e:
            st.error(f"數據抓取發生錯誤: {e}")
            break
            
    status_text.empty() # 下載完成後清除文字
    
    if not all_ohlcv:
        return pd.DataFrame()

    # 整理格式
    df = pd.DataFrame(all_ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)
    
    # 確保欄位名稱符合 Backtesting.py 要求 (首字大寫)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    return df