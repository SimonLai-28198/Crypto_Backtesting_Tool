import os
import streamlit.components.v1 as components

def render_plot(bt_instance, filename='plot.html'):
    """
    解決 Backtesting.py 圖表無法直接在 Streamlit 顯示的問題。
    原理：生成 HTML 檔案 -> 讀取字串 -> 用 Streamlit Component 渲染
    """
    # 1. 產生 HTML 檔案 (open_browser=False 是關鍵)
    bt_instance.plot(filename=filename, open_browser=False)
    
    # 2. 讀取 HTML 內容
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # 3. 渲染 (height 設為 800 以確保圖表完整顯示)
        components.html(html_content, height=800, scrolling=True)
        
    except Exception as e:
        return f"Error render plot: {e}"
    finally:
        # 4. 清理暫存檔 (保持環境整潔)
        if os.path.exists(filename):
            os.remove(filename)