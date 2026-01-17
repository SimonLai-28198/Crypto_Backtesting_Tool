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


class LuciTechEMA(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：LuciTech EMA 突破策略 (EMA Crossover with Risk Management)
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上 LuciTech 分享的 Pine Script 策略模板轉換
    
    【策略原理】
    結合 EMA 穿越訊號和完整的風險管理系統：
    - 進場：價格穿越 EMA 均線
    - 停損：ATR-based 動態停損或 Candle-based 結構停損
    - 停利：基於風險報酬比 (Risk:Reward Ratio)
    - 倉位：基於風險百分比計算
    
    【買入訊號】
    - 條件：收盤價由下往上穿越 EMA
    - 停損：設定為 Low - ATR × ATR倍數 (ATR模式)
            或前 N 根 K 棒最低點 (Candle模式)
    - 停利：停損距離 × 風險報酬比
    
    【賣出訊號】
    - 條件：收盤價由上往下跌破 EMA
    - 停損：設定為 High + ATR × ATR倍數 (ATR模式)
            或前 N 根 K 棒最高點 (Candle模式)
    - 停利：停損距離 × 風險報酬比
    
    【風險管理特點】
    ✓ ATR 動態停損適應市場波動
    ✓ Candle 結構停損基於關鍵支撐阻力
    ✓ 固定風險報酬比確保正期望值
    ✓ 基於風險百分比的倉位管理
    
    【可優化參數】
    - ema_period: EMA 均線週期
    - atr_period: ATR 計算週期
    - atr_multiplier: ATR 停損倍數
    - risk_reward: 風險報酬比
    - sl_candle_lookback: Candle 停損回看週期
    - use_atr_sl: 使用 ATR 停損 (True) 或 Candle 停損 (False)
    ═══════════════════════════════════════════════════════════════
    """
    # EMA 參數
    ema_period = 15       # EMA 均線週期 (可優化參數)
    
    # ATR 停損參數
    atr_period = 14       # ATR 計算週期 (可優化參數)
    atr_multiplier = 1.5  # ATR 停損倍數 (可優化參數)
    
    # 風險管理參數
    risk_reward = 2.0     # 風險報酬比 (可優化參數)
    
    # Candle 停損參數
    sl_candle_lookback = 1  # Candle 停損回看 K 棒數 (可優化參數)
    
    # 停損類型：True = ATR-based, False = Candle-based
    use_atr_sl = True

    def init(self):
        """
        初始化函數：計算技術指標
        只在回測開始時執行一次
        """
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # 計算 EMA
        def EMA(series, period):
            """計算指數移動平均線 (Exponential Moving Average)"""
            return series.ewm(span=period, adjust=False).mean()
        
        # 計算 ATR (Average True Range)
        def ATR(high, low, close, period):
            """
            計算平均真實波動幅度 (Average True Range)
            TR = max(High-Low, |High-前Close|, |Low-前Close|)
            ATR = TR 的 SMA
            """
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return tr.rolling(period).mean()
        
        # 註冊指標
        self.ema = self.I(EMA, close, self.ema_period, name=f'EMA{self.ema_period}')
        self.atr = self.I(ATR, high, low, close, self.atr_period, name='ATR')
        
        # 記錄 High/Low 用於 Candle-based 停損
        self.high = self.data.High
        self.low = self.data.Low

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據 EMA 穿越進場，使用 ATR 或 Candle 設定停損停利
        """
        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_atr = self.atr[-1]
        current_ema = self.ema[-1]
        prev_close = self.data.Close[-2] if len(self.data.Close) > 1 else current_close
        prev_ema = self.ema[-2] if len(self.ema) > 1 else current_ema
        
        # ★ 買入訊號：收盤價由下往上穿越 EMA ★
        bull_cross = prev_close <= prev_ema and current_close > current_ema
        
        # ★ 賣出訊號：收盤價由上往下跌破 EMA ★
        bear_cross = prev_close >= prev_ema and current_close < current_ema
        
        # 如果沒有持倉，檢查進場訊號
        if not self.position:
            if bull_cross:
                # 計算停損價格
                if self.use_atr_sl:
                    # ATR-based 停損
                    stop_loss = current_low - current_atr * self.atr_multiplier
                else:
                    # Candle-based 停損：使用前 N 根 K 棒的最低點
                    lookback = min(self.sl_candle_lookback + 1, len(self.data.Low))
                    stop_loss = min(self.data.Low[-i] for i in range(1, lookback + 1))
                
                # 計算停損距離
                stop_distance = current_close - stop_loss
                
                if stop_distance > 0:
                    # 計算停利價格：進場價 + 停損距離 × 風險報酬比
                    take_profit = current_close + stop_distance * self.risk_reward
                    
                    # 執行買入
                    self.buy(sl=stop_loss, tp=take_profit)
            
            elif bear_cross:
                # 這是做空訊號，但 backtesting.py 預設只支持做多
                # 如果需要做空，可以使用 self.sell()
                # 這裡我們選擇跳過做空訊號，只做多
                pass
        
        else:
            # 已有持倉，檢查是否需要手動平倉（反向訊號）
            if self.position.is_long and bear_cross:
                # 如果持多倉但出現做空訊號，平倉
                self.position.close()


class LuciTechEMAShort(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：LuciTech EMA 雙向策略 (Long & Short)
    ═══════════════════════════════════════════════════════════════
    
    【策略說明】
    與 LuciTechEMA 相同，但支持雙向交易（做多 + 做空）
    
    【買入訊號】
    - 條件：收盤價由下往上穿越 EMA
    
    【賣空訊號】
    - 條件：收盤價由上往下跌破 EMA
    ═══════════════════════════════════════════════════════════════
    """
    ema_period = 15
    atr_period = 14
    atr_multiplier = 1.5
    risk_reward = 2.0
    sl_candle_lookback = 1
    use_atr_sl = True

    def init(self):
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        def EMA(series, period):
            return series.ewm(span=period, adjust=False).mean()
        
        def ATR(high, low, close, period):
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            return tr.rolling(period).mean()
        
        self.ema = self.I(EMA, close, self.ema_period, name=f'EMA{self.ema_period}')
        self.atr = self.I(ATR, high, low, close, self.atr_period, name='ATR')

    def next(self):
        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_atr = self.atr[-1]
        current_ema = self.ema[-1]
        prev_close = self.data.Close[-2] if len(self.data.Close) > 1 else current_close
        prev_ema = self.ema[-2] if len(self.ema) > 1 else current_ema
        
        bull_cross = prev_close <= prev_ema and current_close > current_ema
        bear_cross = prev_close >= prev_ema and current_close < current_ema
        
        if not self.position:
            if bull_cross:
                if self.use_atr_sl:
                    stop_loss = current_low - current_atr * self.atr_multiplier
                else:
                    lookback = min(self.sl_candle_lookback + 1, len(self.data.Low))
                    stop_loss = min(self.data.Low[-i] for i in range(1, lookback + 1))
                
                stop_distance = current_close - stop_loss
                if stop_distance > 0:
                    take_profit = current_close + stop_distance * self.risk_reward
                    self.buy(sl=stop_loss, tp=take_profit)
            
            elif bear_cross:
                # 做空訊號
                if self.use_atr_sl:
                    stop_loss = current_high + current_atr * self.atr_multiplier
                else:
                    lookback = min(self.sl_candle_lookback + 1, len(self.data.High))
                    stop_loss = max(self.data.High[-i] for i in range(1, lookback + 1))
                
                stop_distance = stop_loss - current_close
                if stop_distance > 0:
                    take_profit = current_close - stop_distance * self.risk_reward
                    # 確保停利價格大於 0（避免負數導致錯誤）
                    if take_profit > 0 and stop_loss > 0:
                        self.sell(sl=stop_loss, tp=take_profit)
        
        else:
            # 反向訊號平倉
            if self.position.is_long and bear_cross:
                self.position.close()
            elif self.position.is_short and bull_cross:
                self.position.close()


class EMABandpassCombo(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：EMA 帶通濾波器組合策略 (Combo 2/20 EMA & Bandpass Filter)
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上分享的 Pine Script v6 策略轉換
    原策略名稱：Combo 2/20 EMA & Bandpass Filter v6
    
    【策略原理】
    結合兩種不同類型的技術指標，形成雙重確認機制：
    1. EMA 趨勢訊號：使用快速 EMA 和慢速 EMA 的相對位置
    2. 帶通濾波器訊號：使用數位濾波器提取特定頻率成分
    
    只有當兩種訊號同方向時才進場，降低假訊號風險。
    
    【EMA 訊號邏輯】
    - 快速 EMA > 慢速 EMA → 做多訊號 (+1)
    - 快速 EMA < 慢速 EMA → 做空訊號 (-1)
    - 相等 → 無訊號 (0)
    
    【帶通濾波器訊號邏輯】
    帶通濾波器 (Bandpass Filter) 是一種數位訊號處理技術：
    - 用於提取價格序列中特定週期的波動成分
    - 過濾掉高頻噪音和低頻趨勢
    - BP 值 > 賣出區 → 做空訊號 (+1)
    - BP 值 < 買入區 → 做多訊號 (-1)
    
    【組合訊號】
    - 當 EMA 訊號 = 帶通濾波器訊號，且不為 0 → 進場
    - 訊號 = 1 → 做多
    - 訊號 = -1 → 做空
    - 訊號 = 0 → 平倉
    
    【優點】
    ✓ 雙重確認降低假訊號
    ✓ 結合趨勢追蹤和震盪指標
    ✓ 可選擇反向訊號（適合不同市場環境）
    
    【缺點】
    ✗ 雙重確認可能錯過部分行情
    ✗ 帶通濾波器參數較難直觀理解
    ✗ 需要足夠的歷史數據來計算濾波器
    ═══════════════════════════════════════════════════════════════
    """
    # EMA 參數
    ema_fast_len = 2      # 快速 EMA 週期 (可優化參數)
    ema_slow_len = 20     # 慢速 EMA 週期 (可優化參數)
    
    # 帶通濾波器參數
    bpf_len = 20          # 帶通濾波器週期 (可優化參數)
    bpf_delta = 0.5       # 帶通濾波器 Delta (可優化參數)
    bpf_sell_zone = 5.0   # 帶通濾波器賣出區 (可優化參數)
    bpf_buy_zone = -5.0   # 帶通濾波器買入區 (可優化參數)
    
    # 其他參數
    reverse = False       # 是否反向訊號 (可優化參數)

    def init(self):
        """
        初始化函數：計算技術指標
        只在回測開始時執行一次
        """
        import numpy as np
        
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # 計算 (High + Low) / 2，用於帶通濾波器
        hl2 = (high + low) / 2
        
        # 計算快速 EMA
        def EMA_Fast(series):
            """計算快速 EMA"""
            return series.ewm(span=self.ema_fast_len, adjust=False).mean()
        
        # 計算慢速 EMA
        def EMA_Slow(series):
            """計算慢速 EMA"""
            return series.ewm(span=self.ema_slow_len, adjust=False).mean()
        
        # 計算帶通濾波器 (Bandpass Filter)
        def BandpassFilter(hl2_series):
            """
            計算帶通濾波器 (Bandpass Filter)
            
            這是 John Ehlers 設計的數位濾波器，用於提取特定週期的成分。
            
            數學公式：
            beta = cos(π * (360/len) / 180)
            gamma = 1 / cos(π * (720 * delta / len) / 180)
            alpha = gamma - sqrt(gamma² - 1)
            BP = 0.5 * (1 - alpha) * (hl2 - hl2[2]) + beta * (1 + alpha) * BP[1] - alpha * BP[2]
            """
            n = len(hl2_series)
            bp = np.zeros(n)
            
            # 計算濾波器係數
            beta = np.cos(np.pi * (360 / self.bpf_len) / 180)
            gamma = 1 / np.cos(np.pi * (720 * self.bpf_delta / self.bpf_len) / 180)
            alpha = gamma - np.sqrt(gamma * gamma - 1)
            
            hl2_arr = hl2_series.values
            
            # 迭代計算帶通濾波器值
            for i in range(2, n):
                bp[i] = (0.5 * (1 - alpha) * (hl2_arr[i] - hl2_arr[i-2]) + 
                         beta * (1 + alpha) * bp[i-1] - 
                         alpha * bp[i-2])
            
            return pd.Series(bp, index=hl2_series.index)
        
        # 註冊 EMA 指標
        self.ema_fast = self.I(EMA_Fast, close, name=f'EMA{self.ema_fast_len}')
        self.ema_slow = self.I(EMA_Slow, close, name=f'EMA{self.ema_slow_len}')
        
        # 註冊帶通濾波器指標
        self.bp = self.I(BandpassFilter, hl2, name='BandpassFilter')
        
        # 記錄前一個帶通濾波器訊號（用於當 BP 在中性區時維持前一訊號）
        self._prev_bp_signal = 0

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據 EMA 和帶通濾波器的組合訊號決定交易方向
        """
        # ====== 計算 EMA 訊號 ======
        current_ema_fast = self.ema_fast[-1]
        current_ema_slow = self.ema_slow[-1]
        
        if current_ema_fast > current_ema_slow:
            sig_ema = 1     # 做多訊號
        elif current_ema_fast < current_ema_slow:
            sig_ema = -1    # 做空訊號
        else:
            sig_ema = 0     # 無訊號
        
        # ====== 計算帶通濾波器訊號 ======
        current_bp = self.bp[-1]
        
        if current_bp > self.bpf_sell_zone:
            sig_bpf = 1     # 做空訊號（BP 在高位）
        elif current_bp < self.bpf_buy_zone:
            sig_bpf = -1    # 做多訊號（BP 在低位）
        else:
            # 中性區：維持前一訊號
            sig_bpf = self._prev_bp_signal
        
        # 更新前一訊號
        self._prev_bp_signal = sig_bpf
        
        # ====== 組合訊號 ======
        # 只有當兩個訊號一致且不為 0 時才進場
        if sig_ema == sig_bpf and sig_ema != 0:
            sig = sig_ema
        else:
            sig = 0
        
        # ====== 反向訊號處理 ======
        if self.reverse:
            if sig == 1:
                sig = -1
            elif sig == -1:
                sig = 1
        
        # ====== 交易執行 ======
        if sig == 1:
            # 做多訊號
            if not self.position.is_long:
                if self.position.is_short:
                    self.position.close()
                self.buy()
        elif sig == -1:
            # 做空訊號
            if not self.position.is_short:
                if self.position.is_long:
                    self.position.close()
                self.sell()
        else:
            # 無訊號：平倉
            if self.position:
                self.position.close()


class RSIAdaptiveT3Squeeze(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：RSI 自適應 T3 + 擠壓動量策略 (RSI-Adaptive T3 + Squeeze Momentum)
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上 PakunFX 分享的 Pine Script v6 策略轉換
    結合 ChartPrime 的 RSI Adaptive T3 和 LazyBear 的 Squeeze Momentum 指標
    
    【策略原理】
    這是一個動態趨勢追蹤策略，結合兩個核心概念：
    
    1. RSI 自適應 T3 均線：
       - T3 是一種改良版的移動平均線，比 EMA 更平滑
       - 透過 RSI 動態調整 T3 週期長度
       - RSI 低時（超賣）→ T3 週期變長，反應更慢
       - RSI 高時（超買）→ T3 週期變短，反應更快
    
    2. 擠壓動量 (Squeeze Momentum)：
       - 當布林帶收縮到 Keltner 通道內部時，稱為「擠壓」
       - 擠壓結束後通常會有大行情爆發
       - 結合線性回歸判斷動量方向
    
    【買入訊號】
    - T3 向上穿越（斜率由負轉正）
    - 動量值 > 0（正動量）
    - 擠壓剛結束（sqzOff = True）
    
    【賣空訊號】
    - T3 向下穿越（斜率由正轉負）
    - 動量值 < 0（負動量）
    - 擠壓剛結束（sqzOff = True）
    
    【出場】
    反向訊號出現時自動反手
    
    【優點】
    ✓ RSI 自適應調整讓指標能適應不同市場狀態
    ✓ 擠壓動量能捕捉盤整後的突破行情
    ✓ 雙重過濾減少假訊號
    
    【缺點】
    ✗ 在震盪市場可能產生連續虧損
    ✗ 計算較複雜，需要較多歷史數據
    ✗ 參數較多，需要針對不同市場調整
    ═══════════════════════════════════════════════════════════════
    """
    # T3 參數
    rsi_len = 14          # RSI 週期 (可優化參數)
    t3_min_len = 5        # T3 最小週期 (可優化參數)
    t3_max_len = 50       # T3 最大週期 (可優化參數)
    t3_volume_factor = 0.7  # T3 體積因子 (可優化參數)
    
    # Squeeze 參數 (Bollinger Bands)
    bb_length = 27        # 布林帶週期 (可優化參數)
    bb_mult = 2.0         # 布林帶倍數 (可優化參數)
    
    # Squeeze 參數 (Keltner Channel)
    kc_length = 20        # Keltner 通道週期 (可優化參數)
    kc_mult = 1.5         # Keltner 通道倍數 (可優化參數)
    use_true_range = True # 使用真實波幅 (可優化參數)

    def init(self):
        """
        初始化函數：計算技術指標
        只在回測開始時執行一次
        """
        import numpy as np
        
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # ====== 計算 RSI ======
        def calc_rsi(series, period):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        # ====== 計算 RSI-Adaptive T3 ======
        def calc_t3(src):
            """
            計算 RSI 自適應 T3 均線
            T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3
            其中 e1-e6 是連續 6 次 EMA 平滑
            """
            n = len(src)
            rsi = calc_rsi(src, self.rsi_len)
            
            # RSI 轉換為 0-1 範圍，用於調整 T3 長度
            rsi_scale = 1 - rsi / 100
            
            # 動態計算 T3 長度
            t3_len = self.t3_min_len + (self.t3_max_len - self.t3_min_len) * rsi_scale
            # 填充 NaN 值後再轉換為整數
            t3_len = t3_len.fillna(self.t3_min_len + (self.t3_max_len - self.t3_min_len) / 2)
            t3_len = t3_len.round().astype(int)
            t3_len = t3_len.clip(self.t3_min_len, self.t3_max_len)
            
            # 計算 T3 係數
            v = self.t3_volume_factor
            c1 = -v * v * v
            c2 = 3 * v * v + 3 * v * v * v
            c3 = -6 * v * v - 3 * v - 3 * v * v * v
            c4 = 1 + 3 * v + v * v * v + 3 * v * v
            
            # 使用平均長度計算 EMA（簡化版，避免每根 K 棒不同長度的複雜性）
            avg_len = int(np.nanmean(t3_len.values)) if len(t3_len) > 0 else 20
            avg_len = max(avg_len, 2)  # 確保最小為 2
            
            # 6 層 EMA 平滑
            e1 = src.ewm(span=avg_len, adjust=False).mean()
            e2 = e1.ewm(span=avg_len, adjust=False).mean()
            e3 = e2.ewm(span=avg_len, adjust=False).mean()
            e4 = e3.ewm(span=avg_len, adjust=False).mean()
            e5 = e4.ewm(span=avg_len, adjust=False).mean()
            e6 = e5.ewm(span=avg_len, adjust=False).mean()
            
            # T3 公式
            t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
            return t3
        
        # ====== 計算 Squeeze Momentum ======
        def calc_squeeze(src, high, low):
            """
            計算擠壓動量指標
            sqzOn: 布林帶在 Keltner 通道內部 (正在擠壓)
            sqzOff: 布林帶在 Keltner 通道外部 (擠壓結束)
            val: 動量值 (線性回歸)
            """
            n = len(src)
            
            # Bollinger Bands
            basis = src.rolling(self.bb_length).mean()
            dev = self.bb_mult * src.rolling(self.bb_length).std()
            upper_bb = basis + dev
            lower_bb = basis - dev
            
            # Keltner Channel
            ma = src.rolling(self.kc_length).mean()
            if self.use_true_range:
                tr1 = high - low
                tr2 = abs(high - src.shift(1))
                tr3 = abs(low - src.shift(1))
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            else:
                tr = high - low
            kc_range = tr.rolling(self.kc_length).mean()
            upper_kc = ma + kc_range * self.kc_mult
            lower_kc = ma - kc_range * self.kc_mult
            
            # Squeeze 狀態
            sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
            sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)
            
            # 動量計算 (使用簡化的線性回歸)
            mid_line = (high.rolling(self.kc_length).max() + low.rolling(self.kc_length).min()) / 2
            val_src = src - (mid_line + src.rolling(self.kc_length).mean()) / 2
            
            # 線性回歸（使用滾動計算）
            def linreg(series, length):
                result = pd.Series(index=series.index, dtype=float)
                for i in range(length, len(series)):
                    y = series.iloc[i-length:i].values
                    x = np.arange(length)
                    if len(y) == length and not np.any(np.isnan(y)):
                        slope, intercept = np.polyfit(x, y, 1)
                        result.iloc[i] = intercept + slope * (length - 1)
                return result
            
            val = linreg(val_src, self.kc_length)
            
            return sqz_on, sqz_off, val
        
        # 計算並註冊指標
        self.t3 = self.I(calc_t3, close, name='T3')
        
        sqz_on, sqz_off, val = calc_squeeze(close, high, low)
        self.sqz_on = self.I(lambda x: x, sqz_on.astype(float), name='SqzOn')
        self.sqz_off = self.I(lambda x: x, sqz_off.astype(float), name='SqzOff')
        self.momentum = self.I(lambda x: x, val, name='Momentum')

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據 T3 交叉和動量方向決定交易
        """
        # 確保有足夠的歷史數據
        if len(self.t3) < 2:
            return
        
        current_t3 = self.t3[-1]
        prev_t3 = self.t3[-2]
        current_momentum = self.momentum[-1]
        current_sqz_off = self.sqz_off[-1] > 0.5  # 轉換回布林值
        
        # ====== T3 交叉檢測 ======
        # T3 向上穿越：當前 T3 > 前一個 T3（斜率為正）
        t3_cross_up = current_t3 > prev_t3 and (len(self.t3) < 3 or self.t3[-2] <= self.t3[-3])
        # T3 向下穿越：當前 T3 < 前一個 T3（斜率為負）
        t3_cross_down = current_t3 < prev_t3 and (len(self.t3) < 3 or self.t3[-2] >= self.t3[-3])
        
        # ====== 做多條件 ======
        long_condition = t3_cross_up and current_momentum > 0 and current_sqz_off
        
        # ====== 做空條件 ======
        short_condition = t3_cross_down and current_momentum < 0 and current_sqz_off
        
        # ====== 交易執行 ======
        if long_condition:
            if self.position.is_short:
                self.position.close()
            if not self.position.is_long:
                self.buy()
        
        elif short_condition:
            if self.position.is_long:
                self.position.close()
            if not self.position.is_short:
                self.sell()


class EhlersCombo(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：Ehlers 綜合策略 (Ehlers Combo Strategy)
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上 simwai 分享的 Pine Script v5 策略轉換
    原策略結合了 John Ehlers 的多個經典指標
    
    【策略原理】
    結合 5 個 Ehlers 指標形成高精度的交易系統：
    1. Signal to Noise Ratio (SNR)：信噪比，過濾雜訊
    2. Elegant Oscillator：優雅震盪指標，捕捉動能
    3. Decycler：解循環濾波器，過濾高頻雜訊
    4. Instantaneous Trendline：瞬時趨勢線，判斷趨勢方向
    5. Spearman Rank：斯皮爾曼等級相關，衡量趨勢強度
    
    【買入訊號】必須同時滿足：
    - Elegant Oscillator 向上穿越 0
    - Decycler 訊號向上穿越 0
    - 價格向上穿越 Decycler
    - 價格高於上升中的瞬時趨勢線
    - Spearman Rank 為正值
    - SNR 高於閾值
    
    【賣空訊號】必須同時滿足：
    - Elegant Oscillator 向下穿越 0
    - Decycler 訊號向下穿越 0
    - 價格向下跌破 Decycler
    - 價格低於下降中的瞬時趨勢線
    - Spearman Rank 為負值
    - SNR 高於閾值
    
    【出場】
    - 多單：價格跌破瞬時趨勢線
    - 空單：價格突破瞬時趨勢線
    
    【優點】
    ✓ 五重過濾，訊號品質高
    ✓ SNR 有效過濾盤整雜訊
    ✓ 結合趨勢、動能、統計相關性
    
    【缺點】
    ✗ 交易次數可能較少
    ✗ 計算複雜，需要較多歷史數據
    ✗ 參數較多，需要根據市場調整
    ═══════════════════════════════════════════════════════════════
    """
    # 基本參數
    length = 20           # 主要週期 (可優化參數)
    rms_length = 50       # RMS 計算週期 (可優化參數)
    snr_threshold = 0.1   # SNR 閾值 (可優化參數)
    exit_length = 10      # 出場訊號回看週期 (可優化參數)

    def init(self):
        """
        初始化函數：計算所有 Ehlers 技術指標
        只在回測開始時執行一次
        """
        import numpy as np
        
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        src = close
        n = len(src)
        
        # ====== 1. Ehlers Signal to Noise Ratio (SNR) ======
        def calc_snr(src, high, low):
            """
            計算 Ehlers 信噪比
            用於過濾雜訊，只在信號清晰時交易
            """
            n = len(src)
            
            # 初始化陣列
            Range = np.zeros(n)
            Smooth = np.zeros(n)
            Detrender = np.zeros(n)
            I1 = np.zeros(n)
            Q1 = np.zeros(n)
            jI = np.zeros(n)
            jQ = np.zeros(n)
            I2 = np.zeros(n)
            Q2 = np.zeros(n)
            Re = np.zeros(n)
            Im = np.zeros(n)
            Period = np.zeros(n)
            SNR = np.zeros(n)
            
            price = src.values
            h = high.values
            l = low.values
            
            for i in range(6, n):
                # 計算噪音（平均真實波幅）
                Range[i] = 0.1 * (h[i] - l[i]) + 0.9 * Range[i-1]
                
                # Hilbert Transform
                Smooth[i] = (4*price[i] + 3*price[i-1] + 2*price[i-2] + price[i-3]) / 10
                Detrender[i] = (0.0962*Smooth[i] + 0.5769*Smooth[i-2] - 0.5769*Smooth[i-4] - 0.0962*Smooth[i-6]) * (0.075*Period[i-1] + 0.54)
                
                # 計算 InPhase 和 Quadrature 分量
                Q1[i] = (0.0962*Detrender[i] + 0.5769*Detrender[i-2] - 0.5769*Detrender[i-4] - 0.0962*Detrender[i-6]) * (0.075*Period[i-1] + 0.54)
                I1[i] = Detrender[i-3]
                
                # 相位推進 90 度
                jI[i] = (0.0962*I1[i] + 0.5769*I1[i-2] - 0.5769*I1[i-4] - 0.0962*I1[i-6]) * (0.075*Period[i-1] + 0.54)
                jQ[i] = (0.0962*Q1[i] + 0.5769*Q1[i-2] - 0.5769*Q1[i-4] - 0.0962*Q1[i-6]) * (0.075*Period[i-1] + 0.54)
                
                # 相量加法
                I2[i] = I1[i] - jQ[i]
                Q2[i] = Q1[i] + jI[i]
                
                # 平滑 I 和 Q 分量
                I2[i] = 0.2*I2[i] + 0.8*I2[i-1]
                Q2[i] = 0.2*Q2[i] + 0.8*Q2[i-1]
                
                # Homodyne Discriminator
                Re[i] = I2[i]*I2[i-1] + Q2[i]*Q2[i-1]
                Im[i] = I2[i]*Q2[i-1] - Q2[i]*I2[i-1]
                Re[i] = 0.2*Re[i] + 0.8*Re[i-1]
                Im[i] = 0.2*Im[i] + 0.8*Im[i-1]
                
                # 計算週期
                if Im[i] != 0 and Re[i] != 0:
                    Period[i] = 2*np.pi / np.arctan(Im[i]/Re[i])
                else:
                    Period[i] = Period[i-1]
                
                # 限制週期變化
                if Period[i] > 1.5*Period[i-1]:
                    Period[i] = 1.5*Period[i-1]
                if Period[i] < 0.67*Period[i-1]:
                    Period[i] = 0.67*Period[i-1]
                Period[i] = max(6, min(100, Period[i]))
                Period[i] = 0.2*Period[i] + 0.8*Period[i-1]
                
                # 計算 SNR (以分貝為單位)
                if Range[i] != 0:
                    signal_power = I1[i]*I1[i] + Q1[i]*Q1[i]
                    noise_power = Range[i]*Range[i]
                    if noise_power > 0:
                        SNR[i] = 0.25*(10*np.log10(signal_power/noise_power + 1e-10) + 6) + 0.75*SNR[i-1]
            
            return pd.Series(SNR, index=src.index), pd.Series(Period, index=src.index)
        
        # ====== 2. Ehlers Elegant Oscillator ======
        def calc_elegant_oscillator(src, length, rms_length):
            """
            計算 Ehlers 優雅震盪指標
            使用 SuperSmoother 濾波器和 Fisher Transform
            """
            n = len(src)
            
            # SuperSmoother 係數
            a1 = np.exp(-1.414 * np.pi / length)
            b1 = 2 * a1 * np.cos(1.414 * np.pi / length)
            c2 = b1
            c3 = -a1 * a1
            c1 = 1 - c2 - c3
            
            # 計算導數
            deriv = src.diff(2)
            
            # 計算 RMS
            rms = deriv.pow(2).rolling(rms_length).mean().pow(0.5)
            rms = rms.replace(0, np.nan)
            
            # 標準化導數
            nDeriv = deriv / rms
            nDeriv = nDeriv.fillna(0)
            
            # Fisher Transform
            nDeriv_clipped = nDeriv.clip(-0.999, 0.999)
            iFish = (np.exp(2 * nDeriv_clipped) - 1) / (np.exp(2 * nDeriv_clipped) + 1)
            
            # SuperSmoother
            ss = np.zeros(n)
            iFish_arr = iFish.values
            for i in range(3, n):
                ss[i] = c1 * ((iFish_arr[i] + iFish_arr[i-1]) / 2) + c2 * ss[i-1] + c3 * ss[i-2]
            
            ss_series = pd.Series(ss, index=src.index)
            
            # 信號線 (WMA)
            weights = np.arange(1, length + 1)
            ssSig = ss_series.rolling(length).apply(lambda x: np.dot(x, weights[-len(x):]) / weights[-len(x):].sum(), raw=True)
            
            # 震盪指標
            slo = ss_series - ssSig
            
            # 產生信號
            sig = pd.Series(0, index=src.index)
            for i in range(1, n):
                if slo.iloc[i] > 0:
                    sig.iloc[i] = 2 if slo.iloc[i] > slo.iloc[i-1] else 1
                elif slo.iloc[i] < 0:
                    sig.iloc[i] = -2 if slo.iloc[i] < slo.iloc[i-1] else -1
            
            return sig
        
        # ====== 3. Ehlers Decycler ======
        def calc_decycler(src, length):
            """
            計算 Ehlers 解循環濾波器
            過濾高頻雜訊，留下趨勢
            """
            twoPiPrd = 2 * np.pi / length
            alpha = (np.cos(twoPiPrd) + np.sin(twoPiPrd) - 1) / np.cos(twoPiPrd)
            
            n = len(src)
            dec = np.zeros(n)
            src_arr = src.values
            
            for i in range(1, n):
                dec[i] = (alpha / 2) * (src_arr[i] + src_arr[i-1]) + (1 - alpha) * dec[i-1]
            
            dec_series = pd.Series(dec, index=src.index)
            
            # 產生信號
            sig = (src > dec_series).astype(int) - (src < dec_series).astype(int)
            
            return dec_series, sig
        
        # ====== 4. Ehlers Instantaneous Trendline ======
        def calc_itrend(src, length):
            """
            計算 Ehlers 瞬時趨勢線
            動態追蹤市場趨勢
            """
            alpha = 2 / (length + 1) / 2
            n = len(src)
            
            ITrend = np.zeros(n)
            Trigger = np.zeros(n)
            src_arr = src.values
            
            for i in range(7, n):
                ITrend[i] = ((alpha - alpha*alpha/4) * src_arr[i] + 
                            0.5 * alpha*alpha * src_arr[i-1] - 
                            (alpha - 0.75*alpha*alpha) * src_arr[i-2] + 
                            2 * (1-alpha) * ITrend[i-1] - 
                            (1-alpha) * (1-alpha) * ITrend[i-2])
            
            # 初始化前 7 根 K 棒
            for i in range(2, min(7, n)):
                ITrend[i] = (src_arr[i] + 2*src_arr[i-1] + src_arr[i-2]) / 4
            
            Trigger = 2 * ITrend - np.roll(ITrend, 2)
            Trigger[:2] = 0
            
            return pd.Series(ITrend, index=src.index), pd.Series(Trigger, index=src.index)
        
        # ====== 5. Ehlers Spearman Rank ======
        def calc_spearman(src, length):
            """
            計算 Ehlers 斯皮爾曼等級相關係數
            衡量價格與時間的相關性（趨勢強度）
            """
            n = len(src)
            signal = np.zeros(n)
            src_arr = src.values
            
            for i in range(length, n):
                # 取得價格視窗
                prices = src_arr[i-length+1:i+1].copy()
                
                # 計算等級（排序後的位置）
                sorted_indices = np.argsort(prices)
                ranks = np.zeros(length)
                for j, idx in enumerate(sorted_indices):
                    ranks[idx] = j + 1
                
                # 計算 Spearman Rank Correlation
                positions = np.arange(1, length + 1)
                sum_d2 = np.sum((positions - ranks) ** 2)
                rho = 1 - (6 * sum_d2) / (length * (length**2 - 1))
                signal[i] = 2 * (0.5 - (1 - rho))
            
            signal_series = pd.Series(signal, index=src.index)
            
            # 產生信號
            slo = signal_series.diff()
            sig = pd.Series(0, index=src.index)
            for i in range(1, n):
                if slo.iloc[i] > 0 or signal_series.iloc[i] > 0:
                    sig.iloc[i] = 2 if i > 1 and slo.iloc[i] > slo.iloc[i-1] else 1
                elif slo.iloc[i] < 0 or signal_series.iloc[i] < 0:
                    sig.iloc[i] = -2 if i > 1 and slo.iloc[i] < slo.iloc[i-1] else -1
            
            return sig
        
        # ====== 正規化函數 ======
        def normalize(series, min_val, max_val):
            """將序列正規化到指定範圍"""
            hist_min = series.expanding().min()
            hist_max = series.expanding().max()
            range_val = (hist_max - hist_min).replace(0, 1)
            return min_val + (max_val - min_val) * (series - hist_min) / range_val
        
        # 計算所有指標
        snr, period = calc_snr(src, high, low)
        nSNR = normalize(snr, 0, 2)
        
        eo_sig = calc_elegant_oscillator(src, self.length, self.rms_length)
        
        dec, dec_sig = calc_decycler(src, self.length)
        
        iT, Tr = calc_itrend(src, self.length)
        
        spearman_sig = calc_spearman(src, self.length)
        
        # 註冊指標
        self.snr = self.I(lambda x: x, nSNR, name='SNR')
        self.eo_sig = self.I(lambda x: x, eo_sig, name='ElegantOsc')
        self.dec = self.I(lambda x: x, dec, name='Decycler')
        self.dec_sig = self.I(lambda x: x, dec_sig, name='DecyclerSig')
        self.itrend = self.I(lambda x: x, iT, name='ITrend')
        self.spearman_sig = self.I(lambda x: x, spearman_sig, name='SpearmanSig')

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據 5 個 Ehlers 指標的組合訊號決定交易
        """
        # 確保有足夠的歷史數據
        if len(self.data.Close) < self.exit_length + 2:
            return
        
        current_close = self.data.Close[-1]
        current_snr = self.snr[-1]
        current_eo_sig = self.eo_sig[-1]
        prev_eo_sig = self.eo_sig[-2] if len(self.eo_sig) > 1 else 0
        current_dec_sig = self.dec_sig[-1]
        prev_dec_sig = self.dec_sig[-2] if len(self.dec_sig) > 1 else 0
        current_dec = self.dec[-1]
        prev_close = self.data.Close[-2]
        prev_dec = self.dec[-2] if len(self.dec) > 1 else current_dec
        current_itrend = self.itrend[-1]
        prev_itrend = self.itrend[-2] if len(self.itrend) > 1 else current_itrend
        current_spearman = self.spearman_sig[-1]
        
        # ====== 進場訊號 ======
        # 做多條件：所有指標同時看多
        eo_cross_up = current_eo_sig > 0 and prev_eo_sig <= 0
        dec_cross_up = current_dec_sig > 0 and prev_dec_sig <= 0
        price_cross_dec_up = current_close > current_dec and prev_close <= prev_dec
        price_above_rising_itrend = current_close > current_itrend and current_itrend > prev_itrend
        spearman_positive = current_spearman > 0
        snr_ok = current_snr > self.snr_threshold
        
        enter_long = (eo_cross_up and dec_cross_up and price_cross_dec_up and 
                     price_above_rising_itrend and spearman_positive and snr_ok)
        
        # 做空條件：所有指標同時看空
        eo_cross_down = current_eo_sig < 0 and prev_eo_sig >= 0
        dec_cross_down = current_dec_sig < 0 and prev_dec_sig >= 0
        price_cross_dec_down = current_close < current_dec and prev_close >= prev_dec
        price_below_falling_itrend = current_close < current_itrend and current_itrend < prev_itrend
        spearman_negative = current_spearman < 0
        
        enter_short = (eo_cross_down and dec_cross_down and price_cross_dec_down and 
                      price_below_falling_itrend and spearman_negative and snr_ok)
        
        # ====== 出場訊號 ======
        # 使用 exit_length 根 K 棒前的價格來判斷
        exit_idx = min(self.exit_length, len(self.data.Close) - 1)
        exit_close = self.data.Close[-exit_idx] if exit_idx > 0 else current_close
        exit_itrend = self.itrend[-exit_idx] if exit_idx > 0 and len(self.itrend) > exit_idx else current_itrend
        prev_exit_close = self.data.Close[-exit_idx-1] if exit_idx > 0 and len(self.data.Close) > exit_idx + 1 else exit_close
        
        exit_long = exit_close < exit_itrend and prev_exit_close >= exit_itrend
        exit_short = exit_close > exit_itrend and prev_exit_close <= exit_itrend
        
        # ====== 交易執行 ======
        if self.position.is_long and exit_long:
            self.position.close()
        elif self.position.is_short and exit_short:
            self.position.close()
        
        if enter_long and not self.position.is_long:
            if self.position.is_short:
                self.position.close()
            self.buy()
        elif enter_short and not self.position.is_short:
            if self.position.is_long:
                self.position.close()
            self.sell()


class CatchingTheBottom(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：抄底策略 (Catching the Bottom)
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上 Coinrule 分享的 Pine Script v5 策略轉換
    專門設計用於在熊市中捕捉反彈機會
    
    【策略原理】
    這是一個逆勢策略，在下跌趨勢中尋找超賣反彈機會：
    - 利用 RSI 捕捉超賣和動能急跌
    - 利用 SMA 交叉確認下跌趨勢
    - 在趨勢轉強時獲利了結
    
    【買入訊號】必須同時滿足：
    - RSI < 40（超賣區）
    - RSI 較前一根 K 棒下跌超過 3 點（動能急跌）
    - SMA50 向下穿越 SMA100（死亡交叉，確認空頭趨勢）
    
    【賣出訊號】必須同時滿足：
    - RSI > 65（反彈到高位）
    - SMA9 向上穿越 SMA50（短期黃金交叉）
    
    【優點】
    ✓ 專門為熊市設計，逆勢抄底
    ✓ RSI 動能急跌過濾假訊號
    ✓ 多重條件減少誤判
    
    【缺點】
    ✗ 在牛市表現可能不佳
    ✗ 逆勢操作風險較高
    ✗ 需要精準把握反彈時機
    ═══════════════════════════════════════════════════════════════
    """
    # RSI 參數
    rsi_length = 14           # RSI 計算週期 (可優化參數)
    rsi_oversold = 40         # RSI 超賣閾值 (可優化參數)
    rsi_overbought = 65       # RSI 超買閾值 (可優化參數)
    rsi_decrease = 3          # RSI 下跌幅度閾值 (可優化參數)
    
    # SMA 參數
    sma_fast = 50             # 快速 SMA 週期 (可優化參數)
    sma_slow = 100            # 慢速 SMA 週期 (可優化參數)
    sma_exit_fast = 9         # 出場快速 SMA 週期 (可優化參數)
    sma_exit_slow = 50        # 出場慢速 SMA 週期 (可優化參數)

    def init(self):
        """
        初始化函數：計算 RSI 和 SMA 技術指標
        只在回測開始時執行一次
        """
        close = pd.Series(self.data.Close)
        
        # ====== 計算 RSI ======
        def calc_rsi(series, period):
            """計算相對強弱指標 (RSI)"""
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        # ====== 計算 SMA ======
        def calc_sma(series, period):
            """計算簡單移動平均線 (SMA)"""
            return series.rolling(period).mean()
        
        # 註冊指標
        self.rsi = self.I(calc_rsi, close, self.rsi_length, name='RSI')
        self.sma_fast_line = self.I(calc_sma, close, self.sma_fast, name=f'SMA{self.sma_fast}')
        self.sma_slow_line = self.I(calc_sma, close, self.sma_slow, name=f'SMA{self.sma_slow}')
        self.sma_exit_fast_line = self.I(calc_sma, close, self.sma_exit_fast, name=f'SMA{self.sma_exit_fast}')
        self.sma_exit_slow_line = self.I(calc_sma, close, self.sma_exit_slow, name=f'SMA{self.sma_exit_slow}')

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據 RSI 和 SMA 交叉決定進出場
        """
        # 確保有足夠的歷史數據
        if len(self.rsi) < 2:
            return
        
        current_rsi = self.rsi[-1]
        prev_rsi = self.rsi[-2]
        
        current_sma_fast = self.sma_fast_line[-1]
        prev_sma_fast = self.sma_fast_line[-2] if len(self.sma_fast_line) > 1 else current_sma_fast
        current_sma_slow = self.sma_slow_line[-1]
        prev_sma_slow = self.sma_slow_line[-2] if len(self.sma_slow_line) > 1 else current_sma_slow
        
        current_sma_exit_fast = self.sma_exit_fast_line[-1]
        prev_sma_exit_fast = self.sma_exit_fast_line[-2] if len(self.sma_exit_fast_line) > 1 else current_sma_exit_fast
        current_sma_exit_slow = self.sma_exit_slow_line[-1]
        prev_sma_exit_slow = self.sma_exit_slow_line[-2] if len(self.sma_exit_slow_line) > 1 else current_sma_exit_slow
        
        # ====== 買入條件 ======
        # 條件 1: RSI < 超賣閾值 (預設 40)
        buy_condition1 = current_rsi < self.rsi_oversold
        
        # 條件 2: RSI 較前一根 K 棒下跌超過指定幅度 (預設 3)
        buy_condition2 = current_rsi < (prev_rsi - self.rsi_decrease)
        
        # 條件 3: SMA 快線向下穿越慢線 (死亡交叉)
        # crossunder: 當前快線 < 慢線 且 前一根快線 >= 慢線
        buy_condition3 = (current_sma_fast < current_sma_slow) and (prev_sma_fast >= prev_sma_slow)
        
        enter_long = buy_condition1 and buy_condition2 and buy_condition3
        
        # ====== 賣出條件 ======
        # 條件 1: RSI > 超買閾值 (預設 65)
        sell_condition1 = current_rsi > self.rsi_overbought
        
        # 條件 2: SMA9 向上穿越 SMA50 (黃金交叉)
        # crossover: 當前快線 > 慢線 且 前一根快線 <= 慢線
        sell_condition2 = (current_sma_exit_fast > current_sma_exit_slow) and (prev_sma_exit_fast <= prev_sma_exit_slow)
        
        exit_long = sell_condition1 and sell_condition2
        
        # ====== 交易執行 ======
        # 只做多，不做空（這是一個抄底策略）
        if not self.position:
            if enter_long:
                self.buy()
        else:
            if exit_long:
                self.position.close()


class LevelBreakout(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：Level Breakout 突破策略 (LBAB)
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上 [-_-] 分享的 Pine Script v5 策略轉換
    原名稱：[-_-] LBAB (Level Breakout, Auto Backtesting)
    
    【策略原理】
    這是一個「做多」的突破策略，尋找一種特定的形態：
    - 當前 K 棒收盤價低於前一根的低點（假跌破/回調）
    - 前一根 K 棒的高點低於 N 根 K 棒前的高點（有壓力位）
    - 設置突破買單，當價格突破觸發 K 棒的高點時進場
    
    【買入訊號】
    1. 當前收盤價 < 前一根低點 (close < low[1])
    2. 前一根高點 < N 根前的高點 (high[1] < high[lookback+1])
    3. 價格突破觸發 K 棒的高點時進場
    
    【出場訊號】
    - 止盈 (TP)：進場價 * (1 + TP%)
    - 止損 (SL)：觸發 K 棒的低點 * (1 - SL%)
    
    【優點】
    ✓ 邏輯簡單清晰
    ✓ 止盈止損在進場時就確定
    ✓ 適合趨勢突破行情
    
    【缺點】
    ✗ 只做多，無法在下跌行情獲利
    ✗ 假突破容易觸發止損
    ✗ 需要根據不同幣種調整參數
    ═══════════════════════════════════════════════════════════════
    """
    # 策略參數
    lookback = 2          # 回看週期 (可優化參數)
    tp_percent = 5.0      # 止盈百分比 (可優化參數)
    sl_percent = 5.0      # 止損百分比 (可優化參數)

    def init(self):
        """
        初始化函數：準備價格數據
        只在回測開始時執行一次
        """
        # 儲存 High 和 Low 以便在 next() 中使用
        self.high = self.data.High
        self.low = self.data.Low
        self.close = self.data.Close
        
        # 追蹤觸發 K 棒的索引
        self.trigger_bar_idx = None
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        根據突破邏輯決定進出場
        """
        # 確保有足夠的歷史數據
        if len(self.data.Close) < self.lookback + 3:
            return
        
        current_close = self.close[-1]
        prev_low = self.low[-2]
        prev_high = self.high[-2]
        lookback_high = self.high[-(self.lookback + 2)]
        current_high = self.high[-1]
        current_low = self.low[-1]
        
        # ====== 如果持有倉位，檢查止盈止損 ======
        if self.position:
            # 檢查止損
            if current_low <= self.stop_loss_price:
                self.position.close()
                self.trigger_bar_idx = None
                return
            
            # 檢查止盈
            if current_high >= self.take_profit_price:
                self.position.close()
                self.trigger_bar_idx = None
                return
        
        # ====== 如果有待觸發的突破信號 ======
        if self.trigger_bar_idx is not None and not self.position:
            # 檢查是否突破觸發 K 棒的高點
            trigger_high = self.entry_price
            
            if current_high >= trigger_high:
                # 計算止盈止損價格
                trigger_low = self.high[-(len(self.data) - self.trigger_bar_idx)]
                # 重新計算止損（基於觸發 K 棒的低點）
                self.stop_loss_price = self.low[-(len(self.data) - self.trigger_bar_idx)] * (1 - self.sl_percent / 100)
                self.take_profit_price = trigger_high * (1 + self.tp_percent / 100)
                
                # 進場
                self.buy()
                return
        
        # ====== 檢查進場條件 ======
        # 條件 1: 當前收盤價 < 前一根低點
        condition1 = current_close < prev_low
        
        # 條件 2: 前一根高點 < N 根前的高點
        condition2 = prev_high < lookback_high
        
        # 如果滿足條件，設置突破信號
        if condition1 and condition2 and not self.position:
            self.trigger_bar_idx = len(self.data) - 1
            self.entry_price = current_high  # 在當前 K 棒的高點設置突破買單
            # 預設止損價格（會在進場時更新）
            self.stop_loss_price = current_low * (1 - self.sl_percent / 100)
            self.take_profit_price = current_high * (1 + self.tp_percent / 100)


class CoralTrendPullback(Strategy):
    """
    ═══════════════════════════════════════════════════════════════
    策略名稱：Coral Trend Pullback 珊瑚趨勢回撤策略
    ═══════════════════════════════════════════════════════════════
    
    【策略來源】
    根據 TradingView 上 kevinmck100 分享的 Pine Script v5 策略轉換
    原始來源：TradeIQ YouTube 影片 "I Finally Found 80% Win Rate Trading Strategy For Crypto"
    
    【策略原理】
    這是一個趨勢回撤策略，等待趨勢確立後的回調，然後在回調結束時進場：
    1. 使用 Coral Trend 指標判斷趨勢方向
    2. 等待價格回調到 Coral Trend 之下/上
    3. 當價格重新突破 Coral Trend 時進場
    
    【做多訊號】必須按順序滿足：
    C1: Coral Trend 是看漲（綠色/上升）
    C2: 自從突破後，至少有 1 根 K 棒完全在 Coral Trend 之上
    C3: 價格回調，收盤跌回 Coral Trend 之下
    C4: 回調期間 Coral Trend 保持看漲
    C5: 價格重新收盤突破 Coral Trend 之上 → 進場
    
    【做空訊號】完全對稱相反
    
    【出場】
    - 止損：最近 N 根 K 棒的最低點（多）或最高點（空）
    - 止盈：根據 R:R 比例計算
    
    【優點】
    ✓ 等待回撤進場，風險較低
    ✓ 固定 R:R 比例，風險可控
    ✓ 雙向交易
    
    【缺點】
    ✗ 可能錯過強勢突破行情
    ✗ 計算較複雜
    ✗ 震盪盤整行情可能頻繁止損
    ═══════════════════════════════════════════════════════════════
    """
    # Coral Trend 參數
    ct_smoothing = 25         # 平滑週期 (可優化參數)
    ct_constant_d = 0.4       # 常數 D (可優化參數)
    
    # 風險管理參數
    risk_reward = 1.5         # 風險報酬比 (可優化參數)
    local_hl_lookback = 5     # 止損回看週期 (可優化參數)

    def init(self):
        """
        初始化函數：計算 Coral Trend 指標
        只在回測開始時執行一次
        """
        import numpy as np
        
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        n = len(close)
        
        # ====== 計算 Coral Trend ======
        def calc_coral_trend(src, sm, cd):
            """
            計算 Coral Trend 指標
            使用多層 EMA 平滑和多項式組合
            """
            n = len(src)
            
            # 計算係數
            di = (sm - 1.0) / 2.0 + 1.0
            c1 = 2 / (di + 1.0)
            c2 = 1 - c1
            c3 = 3.0 * (cd * cd + cd * cd * cd)
            c4 = -3.0 * (2.0 * cd * cd + cd + cd * cd * cd)
            c5 = 3.0 * cd + 1.0 + cd * cd * cd + 3.0 * cd * cd
            
            # 初始化 6 層 EMA
            i1 = np.zeros(n)
            i2 = np.zeros(n)
            i3 = np.zeros(n)
            i4 = np.zeros(n)
            i5 = np.zeros(n)
            i6 = np.zeros(n)
            bfr = np.zeros(n)
            
            src_arr = src.values
            
            for i in range(1, n):
                i1[i] = c1 * src_arr[i] + c2 * i1[i-1]
                i2[i] = c1 * i1[i] + c2 * i2[i-1]
                i3[i] = c1 * i2[i] + c2 * i3[i-1]
                i4[i] = c1 * i3[i] + c2 * i4[i-1]
                i5[i] = c1 * i4[i] + c2 * i5[i-1]
                i6[i] = c1 * i5[i] + c2 * i6[i-1]
                
                # Coral Trend 公式
                bfr[i] = -cd * cd * cd * i6[i] + c3 * i5[i] + c4 * i4[i] + c5 * i3[i]
            
            return pd.Series(bfr, index=src.index)
        
        # 計算 Coral Trend
        coral = calc_coral_trend(close, self.ct_smoothing, self.ct_constant_d)
        
        # 計算趨勢方向 (1=bullish, -1=bearish, 0=neutral)
        coral_direction = pd.Series(0, index=close.index)
        for i in range(1, n):
            if coral.iloc[i] > coral.iloc[i-1]:
                coral_direction.iloc[i] = 1  # Bullish
            elif coral.iloc[i] < coral.iloc[i-1]:
                coral_direction.iloc[i] = -1  # Bearish
            else:
                coral_direction.iloc[i] = coral_direction.iloc[i-1]
        
        # 註冊指標
        self.coral = self.I(lambda x: x, coral, name='CoralTrend')
        self.coral_dir = self.I(lambda x: x, coral_direction, name='CoralDir')
        
        # 狀態追蹤變數
        self.pre_pullback_done = False
        self.in_pullback = False
        self.pullback_valid = False
        self.last_cross_bar = 0
        self.trend_at_pullback_start = 0

    def next(self):
        """
        交易邏輯函數：每根 K 棒都會執行一次
        實現趨勢回撤進場邏輯
        """
        # 確保有足夠的歷史數據
        if len(self.data.Close) < self.local_hl_lookback + 5:
            return
        
        current_close = self.data.Close[-1]
        prev_close = self.data.Close[-2]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_coral = self.coral[-1]
        prev_coral = self.coral[-2] if len(self.coral) > 1 else current_coral
        current_dir = self.coral_dir[-1]
        prev_dir = self.coral_dir[-2] if len(self.coral_dir) > 1 else 0
        
        is_bullish = current_dir > 0
        is_bearish = current_dir < 0
        
        # ====== 如果持有倉位，檢查止盈止損 ======
        if self.position:
            if hasattr(self, 'stop_loss') and hasattr(self, 'take_profit'):
                # 多單止損/止盈
                if self.position.is_long:
                    if current_low <= self.stop_loss:
                        self.position.close()
                        self._reset_state()
                        return
                    if current_high >= self.take_profit:
                        self.position.close()
                        self._reset_state()
                        return
                # 空單止損/止盈
                elif self.position.is_short:
                    if current_high >= self.stop_loss:
                        self.position.close()
                        self._reset_state()
                        return
                    if current_low <= self.take_profit:
                        self.position.close()
                        self._reset_state()
                        return
            return
        
        # ====== 檢測價格與 Coral Trend 的交叉 ======
        # 向上穿越
        cross_above = prev_close <= prev_coral and current_close > current_coral
        # 向下穿越
        cross_below = prev_close >= prev_coral and current_close < current_coral
        
        # ====== 狀態機邏輯 ======
        
        # 檢測 C2: 至少有 1 根 K 棒完全在 Coral Trend 之上/下
        if is_bullish and not self.pre_pullback_done:
            if current_low > current_coral and current_high > current_coral:
                self.pre_pullback_done = True
                self.last_cross_bar = len(self.data)
        elif is_bearish and not self.pre_pullback_done:
            if current_low < current_coral and current_high < current_coral:
                self.pre_pullback_done = True
                self.last_cross_bar = len(self.data)
        
        # 檢測 C3: 回撤開始
        if self.pre_pullback_done and not self.in_pullback:
            if is_bullish and cross_below:
                self.in_pullback = True
                self.trend_at_pullback_start = current_dir
            elif is_bearish and cross_above:
                self.in_pullback = True
                self.trend_at_pullback_start = current_dir
        
        # 檢測 C4: 回撤期間趨勢是否保持
        if self.in_pullback:
            if self.trend_at_pullback_start > 0 and current_dir <= 0:
                # 多頭回撤期間趨勢變空，重置
                self._reset_state()
            elif self.trend_at_pullback_start < 0 and current_dir >= 0:
                # 空頭回撤期間趨勢變多，重置
                self._reset_state()
            else:
                self.pullback_valid = True
        
        # 檢測 C5: 回撤結束，進場訊號
        if self.pullback_valid:
            # 多頭進場
            if is_bullish and cross_above:
                # 計算止損（最近 N 根 K 棒的最低點）
                recent_low = min(self.data.Low[-self.local_hl_lookback:])
                sl_distance = current_close - recent_low
                
                if sl_distance > 0:
                    tp_distance = sl_distance * self.risk_reward
                    
                    self.stop_loss = recent_low
                    self.take_profit = current_close + tp_distance
                    
                    self.buy()
                    self._reset_state()
                    return
            
            # 空頭進場
            elif is_bearish and cross_below:
                # 計算止損（最近 N 根 K 棒的最高點）
                recent_high = max(self.data.High[-self.local_hl_lookback:])
                sl_distance = recent_high - current_close
                
                if sl_distance > 0:
                    tp_distance = sl_distance * self.risk_reward
                    
                    self.stop_loss = recent_high
                    self.take_profit = current_close - tp_distance
                    
                    self.sell()
                    self._reset_state()
                    return
        
        # 如果趨勢反轉，重置狀態
        if (is_bullish and prev_dir < 0) or (is_bearish and prev_dir > 0):
            self._reset_state()
    
    def _reset_state(self):
        """重置狀態機"""
        self.pre_pullback_done = False
        self.in_pullback = False
        self.pullback_valid = False
        self.trend_at_pullback_start = 0



