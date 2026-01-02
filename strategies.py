from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

class SmaCross(Strategy):
    """
    雙均線交叉策略
    """
    n1 = 10 # 短均線 (可優化)
    n2 = 20 # 長均線 (可優化)

    def init(self):
        close = pd.Series(self.data.Close)
        
        # 定義有名稱的函數，讓圖表顯示更清楚
        def SMA_Short(series):
            return series.rolling(self.n1).mean()
        
        def SMA_Long(series):
            return series.rolling(self.n2).mean()
        
        self.sma1 = self.I(SMA_Short, close, name=f'SMA{self.n1}')
        self.sma2 = self.I(SMA_Long, close, name=f'SMA{self.n2}')

    def next(self):
        # 黃金交叉
        if crossover(self.sma1, self.sma2):
            self.buy()
        # 死亡交叉
        elif crossover(self.sma2, self.sma1):
            self.position.close()

class RsiOscillator(Strategy):
    """
    RSI 均值回歸策略
    """
    upper_bound = 70
    lower_bound = 30
    rsi_period = 14

    def init(self):
        # 簡單計算 RSI
        def RSI(series, period):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        self.rsi = self.I(RSI, pd.Series(self.data.Close), self.rsi_period, name='RSI')

    def next(self):
        # 超賣買入
        if self.rsi < self.lower_bound:
            self.buy()
        # 超買賣出
        elif self.rsi > self.upper_bound:
            self.position.close()