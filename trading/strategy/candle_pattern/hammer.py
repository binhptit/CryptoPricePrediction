from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class Hammer(BasePattern):
    def __init__(self, candlesticks: List[CandleStick]):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "hammer"
        self.no_candles = 1

    def run(self):
        """
            Finds the Hammer pattern.

            Return:
                list[int]: index of the candlestick where the Hammer was found
        """
        found_positions = []

        for candlestick in self.candlesticks:
            open = candlestick.open
            close = candlestick.close
            high = candlestick.high
            low = candlestick.low

            if (((high - low) > 3 * (open - close)) and
                ((close - low) / (.001 + high - low) > 0.6) and
                ((open - low) / (.001 + high - low) > 0.6)):
                found_positions.append(self.candlesticks.index(candlestick))

        return found_positions

    def __repr__(self) -> str:
        return "Hammer Pattern"