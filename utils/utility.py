from datetime import datetime, timedelta

def merge_1h4h(data):
    """
    Merge 1h and 4h data.
    Each 1h candlestick will contains: 
    {
        # Convert index to timestamp in milliseconds
            'open_time': timestamp,
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close'],
            'volume': row['Volume'],
            'close_time': timestamp,
            "original_time": row[0]
    }
    Merge 4 candlestick into 1
    """
    merged_data = []

    # Find the first 4h candlestick in 1h data
    start_index = 0
    for candle_data in data:
        # candle_data["original_time"]  will have value like that '31.12.2006 19:00:00.000 GMT-0500'
        date_time = datetime.strptime(candle_data["original_time"], '%d.%m.%Y %H:%M:%S.%f GMT%z')
        # get timezone
        time_zone = date_time.strftime("%z")
        if (time_zone == "-0400" and date_time.hour in [0, 4, 8, 12, 16, 20])\
            or (time_zone == "-0500" and date_time.hour in [3, 7, 11, 15, 19, 23]):
            start_index
            break
    
    for i in range(start_index, len(data), 4):
        try:
            candlestick = {
                # Convert index to timestamp in milliseconds
                'open_time': data[i]['open_time'],
                'open': data[i]['open'],
                'high': max([data[i]['high'], data[i + 1]['high'], data[i + 2]['high'], data[i + 3]['high']]),
                'low': min([data[i]['low'], data[i + 1]['low'], data[i + 2]['low'], data[i + 3]['low']]),
                'close': data[i + 3]['close'],
                'volume': data[i]['volume'] + data[i + 1]['volume'] + data[i + 2]['volume'] + data[i + 3]['volume'],
                'close_time': data[i + 3]['close_time'],
                "original_time": data[i + 3]["original_time"]
            }
        except:
            break
        merged_data.append(candlestick)
        
    return merged_data

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

def calculate_profit_and_loss_n_days(entry_price: int, profit_price: int, stop_loss_price: int, candlesticks, n_days: int) -> int:
    """
    Calculates the profit and loss prices.
    """
    is_long = entry_price < profit_price
    if n_days > len(candlesticks):
        try:
            max_high = max([candlestick.high for candlestick in candlesticks])
            min_low = min([candlestick.low for candlestick in candlesticks])
        except:
            return 0.0
        
        if is_long:
            profit = max_high - entry_price
        else:
            profit = entry_price - min_low
    else:
        profit = candlesticks[n_days - 1].high - entry_price if is_long else entry_price - candlesticks[n_days - 1].low
    
    if profit > 0 and profit < abs(profit_price - entry_price):
        profit = 0.0
        
    return profit