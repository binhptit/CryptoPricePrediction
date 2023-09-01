from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class ThreeOutsideUp(BasePattern):
    """
    Class for an ThreeOutsideUp pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the ThreeOutsideUp pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "ThreeOutsideUp"
        self.no_candles = 3

    def run(self):
        """
        Runs the ThreeOutsideUp pattern.

        Return:
            list[int]: index of the candlestick where the ThreeOutsideUp pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the ThreeOutsideUp pattern"
        found_positions = []

        candlestick_0 = None
        candlestick_1 = None
        candlestick_2 = None

        dp = [0] * len(self.candlesticks)
        for i in range(len(self.candlesticks)):
            if i == 0:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open)
            else:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open) + dp[i - 1]

        for i in range(len(self.candlesticks) - 2):
            candlestick_0 = self.candlesticks[i]
            candlestick_1 = self.candlesticks[i + 1]
            candlestick_2 = self.candlesticks[i + 2]

            upper_shadow_0 = candlestick_0.high - max(candlestick_0.open, candlestick_0.close)
            lower_shadow_0 = min(candlestick_0.open, candlestick_0.close) - candlestick_0.low
            body_0 = abs(candlestick_0.close - candlestick_0.open)

            upper_shadow_1 = candlestick_1.high - max(candlestick_1.open, candlestick_1.close)
            lower_shadow_1 = min(candlestick_1.open, candlestick_1.close) - candlestick_1.low
            body_1 = abs(candlestick_1.close - candlestick_1.open)

            upper_shadow_2 = candlestick_2.high - max(candlestick_2.open, candlestick_2.close)
            lower_shadow_2 = min(candlestick_2.open, candlestick_2.close) - candlestick_2.low
            body_2 = abs(candlestick_2.close - candlestick_2.open)

            min_idx = i - 22 if i >= 22 else 0
            average_body = (dp[i] - dp[min_idx]) / (i - min_idx + 1)

            # Price trend Downward leading to the start of the candle pattern.
            # First day A black candle.
            # Second day A white candle opens below the prior body and closes
            # above the body, too. Price need not engulf the shadows.
            # Last day A white candle in which price closes higher.
            
            # candlestick_0 must be a bearish candlestick
            if candlestick_0.close > candlestick_0.open:
                continue

            # candlestick_1 must be a bullish candlestick and open below candlestick_0's body and close above candlestick_0's body
            if not (candlestick_1.close > candlestick_1.open and candlestick_1.open <= candlestick_0.close and candlestick_1.close > candlestick_0.open):
                continue

            # candlestick_2 must be a bullish candlestick and close above candlestick_1's body
            if not (candlestick_2.close > candlestick_2.open and candlestick_2.close > candlestick_1.close):
                continue
            
            found_positions.append(i + 2)

        return found_positions

    def __repr__(self) -> str:
        return "ThreeOutsideUp pattern"

            
            