from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class AnomalyHammer(BasePattern):
    def __init__(self, candlesticks: List[CandleStick], r_shadow_with_body=1.0, r_shadow_average_lower_shadow=0.75, r_body_average=1.65):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "AnomalyHammer"
        self.no_candles = 1

        self.r_shadow_with_body = r_shadow_with_body
        self.r_shadow_average_lower_shadow = r_shadow_average_lower_shadow
        self.r_body_average = r_body_average

    def run(self):
        """
            Finds the Hammer pattern.

            Return:
                list[int]: index of the candlestick where the Hammer was found
        """
        found_positions = []

        candlestick_0 = None
        
        dp = [0] * len(self.candlesticks)
        for i in range(len(self.candlesticks)):
            if i == 0:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open)
            else:
                dp[i] = abs(self.candlesticks[i].close - self.candlesticks[i].open) + dp[i - 1]

        dp_lower_shadows = [0] * len(self.candlesticks)
        for i in range(len(self.candlesticks)):
            if i == 0:
                dp_lower_shadows[i] = abs(self.candlesticks[i].low - min(self.candlesticks[i].open, self.candlesticks[i].close))
            else:
                dp_lower_shadows[i] = abs(self.candlesticks[i].low - min(self.candlesticks[i].open, self.candlesticks[i].close)) + dp_lower_shadows[i - 1]

        for i in range(len(self.candlesticks)):
            candlestick_0 = self.candlesticks[i]

            upper_shadow_0 = candlestick_0.high - max(candlestick_0.open, candlestick_0.close)
            lower_shadow_0 = min(candlestick_0.open, candlestick_0.close) - candlestick_0.low
            body_0 = abs(candlestick_0.close - candlestick_0.open)

            min_idx = i - 22 if i >= 22 else 0
            average_body = (dp[i] - dp[min_idx]) / (i - min_idx + 1)
            average_lower_shadow = (dp_lower_shadows[i] - dp_lower_shadows[min_idx]) / (i - min_idx + 1)

            # lower shadow is at least twice the size of the body and lower shadow is tall

            if not (candlestick_0.close >= candlestick_0.open and \
                    lower_shadow_0 >= self.r_shadow_with_body * body_0 \
                        and lower_shadow_0 > self.r_shadow_average_lower_shadow * average_lower_shadow \
                            and body_0 > self.r_body_average * average_body):
                continue

            found_positions.append(i)

        return found_positions

    def __repr__(self) -> str:
        return "Anomaly Hammer Pattern"