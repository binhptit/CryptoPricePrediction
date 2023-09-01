from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class BeltHoldBearish(BasePattern):
    """
    Class for an BeltHoldBearish pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the BeltHoldBearish pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bearish"
        self.pattern_name = "BeltHoldBearish"
        self.no_candles = 1

    def run(self):
        """
        Runs the BeltHoldBearish pattern.

        Return:
            list[int]: index of the candlestick where the BeltHoldBearish pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the BeltHoldBearish pattern"
        found_positions = []

        candlestick_0 = None
        
        dp = [0] * len(self.candlesticks)
        for i in range(len(self.candlesticks)):
            if i == 0:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open)
            else:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open) + dp[i - 1]

        for i in range(len(self.candlesticks)):
            candlestick_0 = self.candlesticks[i]

            upper_shadow_0 = candlestick_0.high - max(candlestick_0.open, candlestick_0.close)
            lower_shadow_0 = min(candlestick_0.open, candlestick_0.close) - candlestick_0.low
            body_0 = abs(candlestick_0.close - candlestick_0.open)

            min_idx = i - 22 if i >= 22 else 0
            average_body = (dp[i] - dp[min_idx]) / (i - min_idx + 1)

            # Price trend Upward leading to the candle line.
            # Configuration Price opens at the high and closes near the low, creating a tall
            # black candle.
            
            # All must be tall then average and have a small upper shadow and a long lower shadow
            if body_0 < average_body:
                continue            

            if candlestick_0.open != candlestick_0.high:
                continue

            if candlestick_0.close > candlestick_0.low + 0.05 * body_0:
                continue

            found_positions.append(i)

        return found_positions

    def __repr__(self) -> str:
        return "BeltHoldBearish pattern"

            
            