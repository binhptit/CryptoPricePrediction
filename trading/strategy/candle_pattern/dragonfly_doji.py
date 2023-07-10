from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class DragonFlyDoji(BasePattern):
    def __init__(self, candlesticks: List[CandleStick]):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
    
    def run(self):
        """
            Finds the dragon doji pattern.

            Return:
                list[int]: index of the candlestick where the dragon doji was found
        """
        found_positions = []

        for candlestick in self.candlesticks:
            open = candlestick.open
            close = candlestick.close
            high = candlestick.high
            low = candlestick.low

            if  abs(close - open) / (high - low +  0.0001) < 0.1 and \
               (min(close, open) - low) > (3 * abs(close - open)) and \
               (high - max(close, open)) < abs(close - open):
                found_positions.append(self.candlesticks.index(candlestick))

        return found_positions

    def __repr__(self) -> str:
        return "Dragon Doji Pattern"