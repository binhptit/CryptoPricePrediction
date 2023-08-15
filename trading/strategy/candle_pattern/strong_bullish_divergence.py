from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick
from .divergence_base_pattern import RsiDivergence

class StrongBullishDivergence(RsiDivergence):
    """
        Find the strong bullish divergence pattern.
        Lower lows in price action and higher lows in the RSI.
    """
    def __init__(self, candlesticks: List[CandleStick], divergence_type="ll"):
        super().__init__(candlesticks, divergence_type)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "strong_bullish_divergence"
        self.no_candles = 1
    
    def run(self):
        """
            Finds the Strong bullish divergence pattern.

            Return:
                list[int]: index of the candlestick where the Strong bullish divergence was found
        """
        found_positions = self.run_divergence_detect()
        found_positions = [x[1] for x in found_positions]
        return found_positions

    def __repr__(self) -> str:
        return "Strong bullish divergence pattern"