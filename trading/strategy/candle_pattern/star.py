from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class Star(BasePattern):
    """
    Class for an starpattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the starpattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bearish"
        self.pattern_name = "star"
        self.no_candles = 2

    def run(self):
        """
        Runs the starpattern.

        Return:
            list[int]: index of the candlestick where the starpattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the starpattern"
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

            if (prev_close > prev_open and
                abs(prev_close - prev_open) / (prev_high - prev_low +  0.0001) >= 0.7 and
                0.3 > abs(close - open) / (high - low +  0.0001) >= 0.1 and
                prev_close < close and
                prev_close < open):
                found_positions.append(self.candlesticks.index(candlestick))
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Star Pattern"

            
            