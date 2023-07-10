from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class MorningStarDoji(BasePattern):
    """
    Class for an morning star doji pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the morning Star Doji pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks

    def run(self):
        """
        Runs the morning Star Doji pattern.

        Return:
            list[int]: index of the candlestick where the morning Star Doji pattern was found
        """
        assert len(self.candlesticks) > 2, "There must be at least 3 candlesticks to run the morning Star Doji pattern"
        found_positions = []
        previous_candlestick = None
        pre_previous_candlestick = None

        for candlestick in self.candlesticks:
            if pre_previous_candlestick is None:
                pre_previous_candlestick = candlestick
                continue

            if previous_candlestick is None:
                previous_candlestick = candlestick
                continue
            
            prev_open = previous_candlestick.open
            prev_close = previous_candlestick.close
            prev_high = previous_candlestick.high
            prev_low = previous_candlestick.low

            prev_prev_open = pre_previous_candlestick.open
            prev_prev_close = pre_previous_candlestick.close
            prev_prev_high = pre_previous_candlestick.high
            prev_prev_low = pre_previous_candlestick.low

            open = candlestick.open
            close = candlestick.close
            high = candlestick.high
            low = candlestick.low

            if (prev_prev_close < prev_prev_open and
                abs(prev_prev_close - prev_prev_open) / (prev_prev_high - prev_prev_low +  0.0001) >= 0.7 and
                abs(prev_close - prev_open) / (prev_high - prev_low +  0.0001) < 0.1 and
                close > open and
                abs(close - open) / (high - low) >= 0.7 and
                prev_prev_close > prev_close and
                prev_prev_close > prev_open and
                prev_close < open and
                prev_open < open and
                close > prev_prev_close
                and (prev_high - max(prev_close, prev_open)) > (3 * abs(prev_close - prev_open))
                and (min(prev_close, prev_open) - prev_low) > (3 * abs(prev_close - prev_open))):
                found_positions.append(self.candlesticks.index(candlestick))

            pre_previous_candlestick = previous_candlestick
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Morning Star Doji Pattern"

            
            