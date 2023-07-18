from .base import BaseIndicator
import pandas as pd
import numpy as np

class RSI(BaseIndicator):
    def __init__(self, candlesticks=None, candlesticks_df=None) -> None:
        super().__init__(candlesticks, candlesticks_df)
        self.candlesticks_df.index = pd.DatetimeIndex(self.candlesticks_df['Date'])
    
    def run(self, period: int = 14, round_rsi: bool = True):
        delta = self.candlesticks_df["Close"].diff()

        up = delta.copy()
        up[up < 0] = 0
        up = pd.Series.ewm(up, alpha=1/period).mean()

        down = delta.copy()
        down[down > 0] = 0
        down *= -1
        down = pd.Series.ewm(down, alpha=1/period).mean()

        rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))

        return np.round(rsi, 2) if round_rsi else rsi
