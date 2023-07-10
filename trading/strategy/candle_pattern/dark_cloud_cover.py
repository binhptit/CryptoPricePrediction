from .base_pattern import BasePattern
from typing import List
from ...candlestick import CandleStick

class DarkCloudCover(BasePattern):
    def __init__(self, candlesticks: List[CandleStick]):
        super().__init__(candlesticks)
        self.candlesticks = candlesticks

    def run(self):
        """
            Finds the dark cloud cover pattern.

            Return:
                list[int]: index of the candlestick where the dark cloud cover was found
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
            high = candlestick.high
            low = candlestick.low

            if ((prev_close > prev_open) and
                (((prev_close + prev_open) / 2) > close) and
                (open > close) and
                (open > prev_close) and
                (close > prev_open) and
                ((open - close) / (.001 + (high - low)) > 0.6)):
                found_positions.append(self.candlesticks.index(candlestick))
            
            previous_candlestick = candlestick

        return found_positions

    def __repr__(self) -> str:
        return "Dark Cloud Cover Pattern"