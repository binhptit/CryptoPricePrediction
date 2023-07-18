
def calculate_profit_and_loss(entry_price: int, profit_price: int, stop_loss_price: int, candlesticks) -> int:
    """
    Calculates the profit and loss prices.
    """
    profit = abs(entry_price - profit_price) / 2
    for candlestick in candlesticks:
        open_price = candlestick.open
        high_price = candlestick.high
        low_price = candlestick.low
        close_price = candlestick.close

        # print(f"High price: {high_price}. Low price: {low_price}.")
        
        if low_price <= stop_loss_price <= high_price:
            if stop_loss_price <= entry_price:
                profit = -(entry_price - stop_loss_price)
            else:
                profit = entry_price - stop_loss_price
            return profit
        elif low_price <= profit_price <= high_price:
            if profit_price >= entry_price:
                profit = profit_price - entry_price
            else:
                profit = entry_price - profit_price
            return profit

    return profit