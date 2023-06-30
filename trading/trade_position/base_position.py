import os
from abc import ABC, abstractmethod
from typing import List, Tuple
from ..candlestick import CandleStick
from ..client.client import Client

class BasePosition(ABC):
    """
    Abstract class for a trade position.
    """

    def __init__(self, symbol: str, quantity: int, entry_price: int, profit_price: int, stop_loss_price: int, client: Client):
        """
        Initializes the trade position.
        """
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.profit_price = profit_price
        self.stop_loss_price = stop_loss_price
        self.client = client


    @abstractmethod
    def open_position(self):
        """
        Opens a position.
        """
        pass
    
    @abstractmethod
    def close_position(self):
        """
        Closes a position.
        """
        pass
    
    @abstractmethod
    def calculate_profit_and_loss(entry_price: int, profit_price: int, stop_loss_price: int, candlesticks: List[CandleStick]) -> int:
        """
        Calculates the profit and loss prices.
        """
        pass
        