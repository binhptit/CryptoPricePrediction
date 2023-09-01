from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class ThreeStarsInTheSouth(BasePattern):
    """
    Class for an ThreeStarsInTheSouth pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the ThreeStarsInTheSouth pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "ThreeStarsInTheSouth"
        self.no_candles = 3

    def run(self):
        """
        Runs the ThreeStarsInTheSouth pattern.

        Return:
            list[int]: index of the candlestick where the ThreeStarsInTheSouth pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the ThreeStarsInTheSouth pattern"
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

            # candlestick_0 must be a bearish candlestick
            if candlestick_0.close > candlestick_0.open:
                continue
            
            # candlestick_0 must be tall then average and have a small upper shadow and a long lower shadow
            if not (
                # body_0 >= average_body and\
                lower_shadow_0 >= body_0 and\
                upper_shadow_0 <= 0.1 * body_0):
                continue

            # candlestick_1 low must be inside candlestick_0
            if not (candlestick_1.low > candlestick_0.low and\
                candlestick_1.low < candlestick_0.high):
                continue

            # candlesstick_2 must be marubozu
            # if not (upper_shadow_2 <= 0.1 * body_2 and\
            #     lower_shadow_2 <= 0.1 * body_2):
            #     continue

            # candlestick_2 must be inside candlestick_1
            if not (candlestick_2.low >= candlestick_1.low and\
                candlestick_2.high <= candlestick_1.high):
                continue
            
            found_positions.append(i + 2)

        return found_positions

    def __repr__(self) -> str:
        return "ThreeStarsInTheSouth pattern"

            
            