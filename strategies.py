from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

class SmaCross(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：雙均線交叉策略 (Simple Moving Average Crossover)
    ═══════════════════════════════════════════════════════════════
    
    【策略原理】
    利用短期均線和長期均線的交叉來判斷趨勢變化：
    - 短期均線反應快，能及時捕捉價格變化
    - 長期均線反應慢，代表整體趨勢方向
    - 當短期均線穿越長期均線時，代表趨勢可能反轉
    
    【買入訊號】黃金交叉 (Golden Cross)
    - 條件：短期均線由下往上穿越長期均線
    - 意義：短期價格開始強於長期趨勢，可能進入上漲趨勢
    - 動作：全倉買入
    
    【賣出訊號】死亡交叉 (Death Cross)
    - 條件：短期均線由上往下跌破長期均線
    - 意義：短期價格開始弱於長期趨勢，可能進入下跌趨勢
    - 動作：平倉所有持倉
    
    【優點】
    ✓ 邏輯簡單，容易理解
    ✓ 能捕捉中長期趨勢
    ✓ 適合趨勢明顯的市場
    
    【缺點】
    ✗ 在震盪市場容易產生假訊號
    ✗ 訊號有延遲，可能錯過最佳進場點
    ✗ 頻繁交叉會增加交易成本
    ═══════════════════════════════════════════════════════════════
    """
    n1 = 10  # 短期均線週期 (可優化參數)
    n2 = 50  # 長期均線週期 (可優化參數)

    def init(self):
        """
        初始化函數：計算技術指標
        只在回測開始時執行一次
        """
        # 取得收盤價資料序列
        close = pd.Series(self.data.Close)
        
        # 定義短期移動平均線計算函數
        def SMA_Short(series):
            """
            計算短期簡單移動平均線 (SMA)
            - 取最近 n1 根 K 棒的收盤價
            - 計算這些價格的算術平均值
            - 例如：n1=10 時，每次計算最近 10 根 K 棒的平均價格
            """
            return series.rolling(self.n1).mean()
        
        # 定義長期移動平均線計算函數
        def SMA_Long(series):
            """
            計算長期簡單移動平均線 (SMA)
            - 取最近 n2 根 K 棒的收盤價
            - 計算這些價格的算術平均值
            - 例如：n2=50 時，每次計算最近 50 根 K 棒的平均價格
            """
            return series.rolling(self.n2).mean()
        
        # 註冊短期均線指標（會顯示在圖表上）
        self.sma1 = self.I(SMA_Short, close, name=f'SMA{self.n1}')
        # 註冊長期均線指標（會顯示在圖表上）
        self.sma2 = self.I(SMA_Long, close, name=f'SMA{self.n2}')

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據均線交叉情況決定買入或賣出
        """
        # ★ 黃金交叉檢測 ★
        # crossover(A, B) 檢測 A 是否由下往上穿越 B
        # 當短期均線向上穿越長期均線時 → 買入訊號
        if crossover(self.sma1, self.sma2):
            self.buy()  # 執行買入（使用所有可用資金）
        
        # ★ 死亡交叉檢測 ★
        # 當長期均線向上穿越短期均線時（等同於短期均線向下跌破長期均線）→ 賣出訊號
        elif crossover(self.sma2, self.sma1):
            self.position.close()  # 平倉所有持倉

class RsiOscillator(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：RSI 均值回歸策略 (RSI Mean Reversion)
    ═══════════════════════════════════════════════════════════════
    
    【策略原理】
    RSI (Relative Strength Index) 相對強弱指標是一種震盪指標：
    - RSI 值介於 0-100 之間
    - 衡量價格上漲和下跌的相對力量
    - 基於「均值回歸」理論：價格偏離常態後會回歸平均
    
    【指標計算】
    1. 計算每日價格變化 (delta)
    2. 分離上漲日和下跌日的變化
    3. 計算平均漲幅 (gain) 和平均跌幅 (loss)
    4. 相對強度 RS = 平均漲幅 / 平均跌幅
    5. RSI = 100 - (100 / (1 + RS))
    
    【買入訊號】超賣區 (Oversold)
    - 條件：RSI < 30 (下限閾值)
    - 意義：市場過度悲觀，價格被低估
    - 預期：價格可能反彈回升
    - 動作：全倉買入
    
    【賣出訊號】超買區 (Overbought)
    - 條件：RSI > 70 (上限閾值)
    - 意義：市場過度樂觀，價格被高估
    - 預期：價格可能回落
    - 動作：平倉所有持倉
    
    【優點】
    ✓ 能捕捉短期價格反轉機會
    ✓ 在震盪市場表現較好
    ✓ 提供明確的超買超賣訊號
    
    【缺點】
    ✗ 在強勢趨勢中容易過早平倉
    ✗ RSI 可能長時間停留在極端區域
    ✗ 需要搭配其他指標確認訊號
    ═══════════════════════════════════════════════════════════════
    """
    upper_bound = 70   # RSI 超買閾值 (可優化參數)
    lower_bound = 30   # RSI 超賣閾值 (可優化參數)
    rsi_period = 14    # RSI 計算週期 (標準值為 14，可優化參數)

    def init(self):
        """
        初始化函數：計算 RSI 指標
        只在回測開始時執行一次
        """
        # 定義 RSI 計算函數
        def RSI(series, period):
            """
            計算相對強弱指標 (Relative Strength Index)
            
            參數：
            - series: 價格序列（通常是收盤價）
            - period: 計算週期（預設 14）
            
            計算步驟：
            1. delta = 當前價格 - 前一個價格
            2. gain = 上漲的平均值（只保留正數變化）
            3. loss = 下跌的平均值（只保留負數變化的絕對值）
            4. RS = gain / loss（相對強度）
            5. RSI = 100 - (100 / (1 + RS))
            
            RSI 值解讀：
            - RSI > 70: 超買，價格可能過高
            - RSI < 30: 超賣，價格可能過低
            - RSI = 50: 中性，漲跌力量均衡
            """
            # 計算價格變化（當前價格 - 前一個價格）
            delta = series.diff()
            
            # 計算平均漲幅
            # where(delta > 0, 0)：保留上漲（正值），下跌設為 0
            # rolling(period).mean()：計算最近 period 天的平均漲幅
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            
            # 計算平均跌幅
            # where(delta < 0, 0)：保留下跌（負值），上漲設為 0
            # 前面加負號將負值轉為正值（跌幅用正數表示）
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            
            # 計算相對強度 (Relative Strength)
            # RS 越大表示上漲力量越強
            rs = gain / loss
            
            # 計算 RSI 指標值（0-100 之間）
            return 100 - (100 / (1 + rs))
        
        # 註冊 RSI 指標（會顯示在圖表下方的子圖中）
        self.rsi = self.I(RSI, pd.Series(self.data.Close), self.rsi_period, name='RSI')

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據 RSI 超買超賣情況決定買入或賣出
        """
        # ★ 超賣檢測 ★
        # 當 RSI 低於下限閾值（預設 30）時 → 買入訊號
        # 理由：市場過度悲觀，價格可能被低估，預期反彈
        if self.rsi < self.lower_bound:
            self.buy()  # 執行買入（使用所有可用資金）
        
        # ★ 超買檢測 ★
        # 當 RSI 高於上限閾值（預設 70）時 → 賣出訊號
        # 理由：市場過度樂觀，價格可能被高估，預期回落
        elif self.rsi > self.upper_bound:
            self.position.close()  # 平倉所有持倉


class SmaCrossATR(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：ATR 動態停損雙均線策略 (SMA Cross with ATR Stop Loss)
    ═══════════════════════════════════════════════════════════════
    
    【策略原理】
    在傳統雙均線交叉策略的基礎上，加入 ATR (Average True Range) 
    動態停損機制，讓停損點能根據市場波動度自動調整：
    - 波動大時，停損距離較遠，避免被正常波動掃出場
    - 波動小時，停損距離較近，更好地保護利潤
    
    【ATR 指標介紹】
    ATR (Average True Range) 平均真實波動幅度：
    - 衡量市場波動程度的指標
    - True Range = max(High-Low, |High-前Close|, |Low-前Close|)
    - ATR = True Range 的 N 日平均值
    
    【買入訊號】
    - 條件：短期均線向上穿越長期均線（黃金交叉）
    - 動作：買入並設定 ATR 動態停損/停利
    - 停損 = 進場價 - ATR × 停損倍數
    - 停利 = 進場價 + ATR × 停利倍數
    
    【賣出訊號】
    - 條件 1：觸及停損價格（自動執行）
    - 條件 2：觸及停利價格（自動執行）
    - 條件 3：死亡交叉（手動平倉）
    
    【優點】
    ✓ 停損距離會根據市場波動自動調整
    ✓ 在高波動市場不容易被假突破掃出
    ✓ 在低波動市場能更好保護利潤
    ✓ 風險報酬比可預先設定
    
    【缺點】
    ✗ ATR 參數需要根據不同市場調整
    ✗ 極端行情下可能無法完全保護
    ═══════════════════════════════════════════════════════════════
    """
    # 均線參數
    n1 = 10           # 短期均線週期 (可優化參數)
    n2 = 50           # 長期均線週期 (可優化參數)
    
    # ATR 停損參數
    atr_period = 14   # ATR 計算週期 (可優化參數)
    sl_multiplier = 2.0   # 停損 ATR 倍數 (可優化參數)
    tp_multiplier = 3.0   # 停利 ATR 倍數 (可優化參數)

    def init(self):
        """
        初始化函數：計算技術指標
        只在回測開始時執行一次
        """
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # 計算短期均線
        def SMA_Short(series):
            return series.rolling(self.n1).mean()
        
        # 計算長期均線
        def SMA_Long(series):
            return series.rolling(self.n2).mean()
        
        # 計算 ATR (Average True Range)
        def ATR(high, low, close, period):
            """
            計算平均真實波動幅度 (Average True Range)
            
            True Range (TR) 定義為以下三者的最大值：
            1. 當日最高價 - 當日最低價
            2. |當日最高價 - 前一日收盤價|
            3. |當日最低價 - 前一日收盤價|
            
            ATR = TR 的 N 日簡單移動平均
            """
            # 計算三個可能的 True Range 值
            tr1 = high - low  # 當日振幅
            tr2 = abs(high - close.shift(1))  # 高點與前收的距離
            tr3 = abs(low - close.shift(1))   # 低點與前收的距離
            
            # True Range = 三者的最大值
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR = TR 的移動平均
            return tr.rolling(period).mean()
        
        # 註冊指標
        self.sma1 = self.I(SMA_Short, close, name=f'SMA{self.n1}')
        self.sma2 = self.I(SMA_Long, close, name=f'SMA{self.n2}')
        self.atr = self.I(ATR, high, low, close, self.atr_period, name='ATR')

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據均線交叉進場，使用 ATR 設定動態停損停利
        """
        # ★ 黃金交叉檢測 ★
        if crossover(self.sma1, self.sma2):
            # 計算進場價格（使用當前收盤價作為預估）
            entry_price = self.data.Close[-1]
            current_atr = self.atr[-1]
            
            # 計算動態停損價格
            # 停損 = 進場價 - ATR × 停損倍數
            stop_loss = entry_price - current_atr * self.sl_multiplier
            
            # 計算動態停利價格
            # 停利 = 進場價 + ATR × 停利倍數
            take_profit = entry_price + current_atr * self.tp_multiplier
            
            # 執行買入，同時設定停損和停利
            self.buy(sl=stop_loss, tp=take_profit)
        
        # ★ 死亡交叉檢測 ★
        # 如果尚未觸發停損/停利，手動平倉
        elif crossover(self.sma2, self.sma1):
            if self.position:
                self.position.close()