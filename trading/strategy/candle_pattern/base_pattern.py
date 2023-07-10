from abc import ABC, abstractmethod
from typing import List, Tuple
from ...candlestick import CandleStick

class BasePattern(ABC):
    """
    Abstract class for a trading strategy.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the strategy.
        """
        self.candlesticks = candlesticks

    @abstractmethod
    def run(self):
        """
        Runs the strategy.
        """
        pass

    def __repr__(self) -> str:
        return "Candle pattern:\t"