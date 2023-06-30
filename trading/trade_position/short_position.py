from base_position import BasePosition

class ShortPosition(BasePosition):
    """
    Class for a long position.
    """

    def __init__(self, symbol: str, quantity: int, entry_price: int, profit_price: int, stop_loss_price: int, client: Client):
        """
        Initializes the long position.
        """
        super().__init__(symbol, quantity, entry_price, profit_price, stop_loss_price, client)
    
    def open_position(self):
        """
        Opens a long position.
        """
        pass
    
    def close_position(self):
        """
        Closes a long position.
        """
        pass
    
    def calculate_profit_and_loss(entry_price: int, profit_price: int, stop_loss_price: int, candlesticks: List[CandleStick]) -> int:
        """
        Calculates the profit and loss prices.
        """
        for candlestick in candlesticks:
            open_price = candlestick.open
            high_price = candlestick.high
            low_price = candlestick.low
            close_price = candlestick.close

            if (open_price >= stop_loss_price and close_price <= stop_loss_price) or (open_price <= stop_loss_price and close_price >= stop_loss_price):
                profit = 0
                loss = stop_loss_price - entry_price
                return profit, loss
            elif (open_price >= profit_price and close_price <= profit_price) or (open_price <= profit_price and close_price >= profit_price):
                profit = entry_price - profit_price
                loss = 0

        return profit, loss