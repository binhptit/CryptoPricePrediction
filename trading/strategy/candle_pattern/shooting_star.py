from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class ShootingStar(BasePattern):
    """
    Class for an shooting starpattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the shooting starpattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks

    def run(self):
        """
        Runs the shooting starpattern.

        Return:
            list[int]: index of the candlestick where the shooting starpattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the shooting starpattern"
        found_positions = []
        previous_candlestick = None

        for candlestick in self.candlesticks:
            if previous_candlestick is None:
                previous_candlestick = candlestick
                continue
            
            prev_open = previous_candlestick.open
            prev_close = previous_candlestick.close
            prev_high = previous_candlestick.high
            prev_low = previous_candlestick.low

            open = candlestick.open
            close = candlestick.close
            high = candlestick.high
            low = candlestick.low

            if (prev_open < prev_close <= open and
                high - max(open, close) >= abs(open - close) * 3 and
                min(close, open) - low <= abs(open - close)):
                found_positions.append(self.candlesticks.index(candlestick))
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Shooting Star pattern"

            
            