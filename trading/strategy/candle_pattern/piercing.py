from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class Piercing(BasePattern):
    """
    Class for an piercing pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the piercing pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "unsure"
        self.pattern_name = "piercing"
        self.no_candles = 2

    def run(self):
        """
        Runs the piercing pattern.

        Return:
            list[int]: index of the candlestick where the piercing pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the piercing pattern"
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

            if  (prev_close < prev_open and
                open < prev_low and
                prev_open > close > prev_close + ((prev_open - prev_close) / 2)):
                found_positions.append(self.candlesticks.index(candlestick))
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "piercing pattern"

            
            