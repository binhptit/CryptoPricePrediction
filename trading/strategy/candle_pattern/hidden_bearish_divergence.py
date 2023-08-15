from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick
from .divergence_base_pattern import RsiDivergence

class HiddenBearishDivergence(RsiDivergence):
    """
        Find the Hidden Bearish divergence pattern.
        Lower lows in price action and higher lows in the RSI.
    """
    def __init__(self, candlesticks: List[CandleStick], divergence_type="lh"):
        super().__init__(candlesticks, divergence_type)
        self.candlesticks = candlesticks
        self.trend = "bearish"
        self.pattern_name = "hidden_bearish_divergence"
        self.no_candles = 1
    
    def run(self):
        """
            Finds the Hidden Bearish divergence pattern.

            Return:
                list[int]: index of the candlestick where the Hidden Bearish divergence was found
        """
        found_positions = self.run_divergence_detect()
        found_positions = [x[1] for x in found_positions]
        return found_positions

    def __repr__(self) -> str:
        return "Hidden Bearish divergence pattern"