from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class ThreeLineStrikeBullish(BasePattern):
    """
    Class for an ThreeLineStrikeBullish pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the ThreeLineStrikeBullish pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bearish"
        self.pattern_name = "ThreeLineStrikeBullish"
        self.no_candles = 4

    def run(self):
        """
        Runs the ThreeLineStrikeBullish pattern.

        Return:
            list[int]: index of the candlestick where the ThreeLineStrikeBullish pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the ThreeLineStrikeBullish pattern"
        found_positions = []

        candlestick_0 = None
        candlestick_1 = None
        candlestick_2 = None
        candlestick_3 = None

        dp = [0] * len(self.candlesticks)
        for i in range(len(self.candlesticks)):
            if i == 0:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open)
            else:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open) + dp[i - 1]

        for i in range(len(self.candlesticks) - 3):
            candlestick_0 = self.candlesticks[i]
            candlestick_1 = self.candlesticks[i + 1]
            candlestick_2 = self.candlesticks[i + 2]
            candlestick_3 = self.candlesticks[i + 3]

            upper_shadow_0 = candlestick_0.high - max(candlestick_0.open, candlestick_0.close)
            lower_shadow_0 = min(candlestick_0.open, candlestick_0.close) - candlestick_0.low
            body_0 = abs(candlestick_0.close - candlestick_0.open)

            upper_shadow_1 = candlestick_1.high - max(candlestick_1.open, candlestick_1.close)
            lower_shadow_1 = min(candlestick_1.open, candlestick_1.close) - candlestick_1.low
            body_1 = abs(candlestick_1.close - candlestick_1.open)

            upper_shadow_2 = candlestick_2.high - max(candlestick_2.open, candlestick_2.close)
            lower_shadow_2 = min(candlestick_2.open, candlestick_2.close) - candlestick_2.low
            body_2 = abs(candlestick_2.close - candlestick_2.open)

            upper_shadow_3 = candlestick_3.high - max(candlestick_3.open, candlestick_3.close)
            lower_shadow_3 = min(candlestick_3.open, candlestick_3.close) - candlestick_3.low
            body_3 = abs(candlestick_3.close - candlestick_3.open)

            min_idx = i - 22 if i >= 22 else 0
            average_body = (dp[i] - dp[min_idx]) / (i - min_idx + 1)

            # Days 1 to 3 Three white candles, each with a higher close.
            # Last day A black candle that opens higher but closes below the open
            # of the first candle.

            # candlestick_0 must be a bullish candlestick
            if candlestick_0.close < candlestick_0.open:
                continue

            # candlestick_1 must be a bullish candlestick
            if candlestick_1.close < candlestick_1.open:
                continue

            # candlestick_2 must be a bullish candlestick
            if candlestick_2.close < candlestick_2.open:
                continue

            # candlestick_3 must be a bearish candlestick and cover of body of 3 previous candlesticks
            if candlestick_3.close > candlestick_3.open or body_3 < average_body:
                continue

            if not (candlestick_3.open >= candlestick_2.close and\
                candlestick_3.close < candlestick_0.open):
                continue

            found_positions.append(i + 3)

        return found_positions

    def __repr__(self) -> str:
        return "ThreeLineStrikeBullish pattern"

            
            