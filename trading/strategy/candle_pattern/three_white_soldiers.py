from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class ThreeWhiteSoldiers(BasePattern):
    """
    Class for an ThreeWhiteSoldiers pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the ThreeWhiteSoldiers pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "ThreeWhiteSoldiers"
        self.no_candles = 3

    def run(self):
        """
        Runs the ThreeWhiteSoldiers pattern.

        Return:
            list[int]: index of the candlestick where the ThreeWhiteSoldiers pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the ThreeWhiteSoldiers pattern"
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

            # Three days Tall white candles with higher closes and price that opens
            # within the previous body. Price should close near the
            # high each day.
            
            # All must be tall then average and have a small upper shadow and a long lower shadow
            if body_0 < average_body or body_1 < average_body or body_2 < average_body:
                continue            

            # candlestick_0 must be a bullish candlestick
            if candlestick_0.close < candlestick_0.open:
                continue

            # candlestick_1 must be a bullish candlestick
            if candlestick_1.close < candlestick_1.open:
                continue

            # candlestick_2 must be a bullish candlestick and upper shadow must be small
            if candlestick_2.close < candlestick_2.open:
                continue

            found_positions.append(i + 2)

        return found_positions

    def __repr__(self) -> str:
        return "ThreeWhiteSoldiers pattern"

            
            