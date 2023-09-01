from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class BreakawayBearish(BasePattern):
    """
    Class for an BreakawayBearish pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the BreakawayBearish pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bearish"
        self.pattern_name = "BreakawayBearish"
        self.no_candles = 5

    def run(self):
        """
        Runs the BreakawayBearish pattern.

        Return:
            list[int]: index of the candlestick where the BreakawayBearish pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the BreakawayBearish pattern"
        found_positions = []

        candlestick_0 = None
        candlestick_1 = None
        candlestick_2 = None
        candlestick_3 = None
        candlestick_4 = None

        dp = [0] * len(self.candlesticks)
        for i in range(len(self.candlesticks)):
            if i == 0:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open)
            else:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open) + dp[i - 1]

        for i in range(len(self.candlesticks) - 4):
            candlestick_0 = self.candlesticks[i]
            candlestick_1 = self.candlesticks[i + 1]
            candlestick_2 = self.candlesticks[i + 2]
            candlestick_3 = self.candlesticks[i + 3]
            candlestick_4 = self.candlesticks[i + 4]

            upper_shadow_0 = candlestick_0.high - max(candlestick_0.open, candlestick_0.close)
            lower_shadow_0 = min(candlestick_0.open, candlestick_0.close) - candlestick_0.low
            body_0 = abs(candlestick_0.close - candlestick_0.open)

            upper_shadow_1 = candlestick_1.high - max(candlestick_1.open, candlestick_1.close)
            lower_shadow_1 = min(candlestick_1.open, candlestick_1.close) - candlestick_1.low
            body_1 = abs(candlestick_1.close - candlestick_1.open)

            upper_shadow_2 = candlestick_2.high - max(candlestick_2.open, candlestick_2.close)
            lower_shadow_2 = min(candlestick_2.open, candlestick_2.close) - candlestick_2.low
            body_2 = abs(candlestick_2.close - candlestick_2.open)

            body_4 = abs(candlestick_4.close - candlestick_4.open)

            min_idx = i - 22 if i >= 22 else 0
            average_body = (dp[i] - dp[min_idx]) / (i - min_idx + 1)
            # First day A tall white candle.
            # Second day A white candle that has a gap between the two candle bodies,
            # but the shadows can overlap.
            # Third day A candle with a higher close, but the candle can be any color.
            # Fourth day A white candle with a higher close.
            # Last day A tall black candle with a close within the gap between the first
            # two candle bodies. Ignore the shadows on the first two
            # candles for citing the gap.
            
            # All must be tall then average and white candle
            if not (body_0 >= average_body and candlestick_0.close > candlestick_0.open):
                continue            

            # candlestick_1 must be a bullish candlestick and has gap with candlestick_0
            if not (candlestick_1.close > candlestick_1.open and candlestick_1.open >= candlestick_0.close):
                continue

            # # candlestick_2 must have higher close
            if not (candlestick_2.close > candlestick_1.close):
                continue
            
            # candlestick_3 must be a bullish candlestick and has higher close
            if not (candlestick_3.close > candlestick_2.close and candlestick_3.close > candlestick_3.open):
                continue

            # candlestick_4 must be a bearish candlestick and has close within the gap between the first two candle bodies
            if not (candlestick_4.close < candlestick_4.open \
                    and body_4 >= average_body \
                        # and candlestick_4.close > candlestick_0.close \
                            and candlestick_4.close < candlestick_1.open):
                continue

            found_positions.append(i + 4)

        return found_positions

    def __repr__(self) -> str:
        return "BreakawayBearish pattern"

            
            