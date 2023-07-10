from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class MorningStar(BasePattern):
    """
    Class for an morning star pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the morning Star pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks

    def run(self):
        """
        Runs the morning Star pattern.

        Return:
            list[int]: index of the candlestick where the morning Star pattern was found
        """
        assert len(self.candlesticks) > 2, "There must be at least 3 candlesticks to run the morning Star pattern"
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

            if (max(prev_open, prev_close) <= prev_prev_close <= prev_prev_open and
                close > open >= max(prev_open, prev_close)):
                found_positions.append(self.candlesticks.index(candlestick))

            pre_previous_candlestick = previous_candlestick
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Morning Star Pattern"

            
            