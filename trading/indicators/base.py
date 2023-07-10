from ..candlechart import CandleChart
from abc import ABC, abstractmethod

class BaseIndicator(CandleChart):
    def __init__(self, candlesticks = None, candlesticks_df = None) -> None:
        super().__init__(candlesticks, candlesticks_df)
        pass

    @abstractmethod
    def run(self):
        pass