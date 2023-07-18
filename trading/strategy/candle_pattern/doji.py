from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class Doji(BasePattern):
    def __init__(self, candlesticks: List[CandleStick]):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "unsure"
        self.pattern_name = "doji"
        self.no_candles = 1
    
    def run(self):
        """
            Finds the doji pattern.

            Return:
                list[int]: index of the candlestick where the doji was found
        """
        found_positions = []

        for candlestick in self.candlesticks:
            open = candlestick.open
            close = candlestick.close
            high = candlestick.high
            low = candlestick.low

            if abs(close - open) / (high - low + 0.0001) < 0.1 and \
               (high - max(close, open)) > (3 * abs(close - open)) and \
               (min(close, open) - low) > (3 * abs(close - open)):
                found_positions.append(self.candlesticks.index(candlestick))

        return found_positions

    def __repr__(self) -> str:
        return "Doji Pattern"