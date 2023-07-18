from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class InvertedHammer(BasePattern):
    def __init__(self, candlesticks: List[CandleStick]):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bearish"
        self.pattern_name = "inverted_hammer"
        self.no_candles = 1
    
    def run(self):
        """
            Finds the InvertedHammer pattern.

            Return:
                list[int]: index of the candlestick where the InvertedHammer was found
        """
        found_positions = []

        for candlestick in self.candlesticks:
            open = candlestick.open
            close = candlestick.close
            high = candlestick.high
            low = candlestick.low

            if  (((high - low) > 3 * (open - close)) and
                ((high - close) / (.001 + high - low) > 0.6)
                and ((high - open) / (.001 + high - low) > 0.6)):
                found_positions.append(self.candlesticks.index(candlestick))

        return found_positions

    def __repr__(self) -> str:
        return "Inverted Hammer Pattern"