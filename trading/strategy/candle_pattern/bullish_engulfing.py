from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class BullishEngulfing(BasePattern):
    """
    Class for an engulfing pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the engulfing pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks
        self.trend = "bullish"
        self.pattern_name = "bullish_engulfing"
        self.no_candles = 2

    def run(self):
        """
        Runs the bull engulfing pattern.

        Return:
            list[int]: index of the candlestick where the engulfing pattern was found
        """
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

            if (close >= prev_open > prev_close and
                close > open and
                prev_close >= open and
                close - open > prev_open - prev_close):
                found_positions.append(self.candlesticks.index(candlestick))

            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Bullish Engulfing Pattern"

            
            