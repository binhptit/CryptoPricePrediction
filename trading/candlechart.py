from .candlestick import CandleStick
import pandas as pd
from abc import ABC, abstractmethod

class CandleChart(ABC):
    def __init__(self, candlesticks = None, candlesticks_df = None):
        self.candlesticks = candlesticks
        self.candlesticks_df = candlesticks_df

        if candlesticks is not None and candlesticks_df is None:
            self.candlesticks_df = self.to_pandas(candlesticks)
        elif candlesticks is None and candlesticks_df is not None:
            self.candlesticks = self.to_candlesticks(candlesticks_df)
    
    def to_pandas(self, candlesticks):
        return pd.DataFrame({
            'Date': [candlestick.date for candlestick in candlesticks],
            'Open': [candlestick.open for candlestick in candlesticks],
            'High': [candlestick.high for candlestick in candlesticks],
            'Low': [candlestick.low for candlestick in candlesticks],
            'Close': [candlestick.close for candlestick in candlesticks],
            'Volume': [candlestick.volume for candlestick in candlesticks],
            'OpenTime': [candlestick.open_time for candlestick in candlesticks],
            'CloseTime': [candlestick.close_time for candlestick in candlesticks],
        })
    
    def to_candlesticks(self, candlesticks_df):
        return [CandleStick(
            open = candlesticks_df['Open'][i],
            high = candlesticks_df['High'][i],
            low = candlesticks_df['Low'][i],
            close = candlesticks_df['Close'][i],
            volume = candlesticks_df['Volume'][i],
            open_time = candlesticks_df['OpenTime'][i],
            close_time = candlesticks_df['CloseTime'][i],
            date=candlesticks_df['Date'][i]
        ) for i in range(len(candlesticks_df))]