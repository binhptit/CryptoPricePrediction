from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class BearishHarami(BasePattern):
    def __init__(self, candlesticks: List[CandleStick]):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks

    def run(self):
        """
            Finds the bearish harami pattern.

            Return:
                list[int]: index of the candlestick where the bearish harami pattern was found
        """
        assert len(self.candlesticks) > 1, "There must be at least 2 candlesticks to run the engulfing pattern"
        found_positions = []
        previous_candlestick = None

        for candlestick in self.candlesticks:
            if previous_candlestick is None:
                previous_candlestick = candlestick
                continue
            
            prev_open = previous_candlestick.open
            prev_close = previous_candlestick.close

            open = candlestick.open
            close = candlestick.close

            if (prev_close > prev_open and
                prev_open <= close < open <= prev_close and
                open - close < prev_close - prev_open):
                found_positions.append(self.candlesticks.index(candlestick))
            
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Bear Harami Pattern"