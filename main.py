from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from utils.json_handler import dump_json, load_json
from datetime import datetime

# if __name__ == '__main__':
    # api_key = 'EisNmtJ21usfKa6mwvNfIkXNISLDeI0g4VexzNCPdR2SDsA8SycX8x6MhPuToxnV'
    # api_secret = 'vM5yQk8T8xbCoB4vGtwMD63dTF33xkorpW0s16tDybm8RQzQHGGoyop69MsHP2F6'

    # output_path = r'dataset/binance_crypto_price_data.json'
    # binance_dataset = BinanceCryptoDataCrawler(api_key, api_secret)
    # crypto_data = binance_dataset.load_from_api(output_path)
    # # crypto_data = binance_dataset.load_from_file(output_path)

    # import pdb; pdb.set_trace()

def make_plot_from_dataframe(d, save_path, name):
    save_path += name

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    df = pd.DataFrame(data=d)
    df.index = pd.DatetimeIndex(df['Date'])

    filename = save_path + "/" + str(d['Date'][0]) + '.png'
    coin = f"BTC-{name}"
    
    mpl.plot(
        df,
        type="candle", 
        title = f"{coin} Price",  
        style="yahoo",
        savefig=filename
        )

def calculate_profit_and_loss(entry_price: int, profit_price: int, stop_loss_price: int, candlesticks) -> int:
    """
    Calculates the profit and loss prices.
    """
    for candlestick in candlesticks:
        open_price = candlestick.open
        high_price = candlestick.high
        low_price = candlestick.low
        close_price = candlestick.close

        print(f"High price: {high_price}. Low price: {low_price}.")
        
        if low_price <= stop_loss_price <= high_price:
            profit = -(entry_price - stop_loss_price)
            return profit
        elif low_price <= profit_price <= high_price:
            profit = profit_price - entry_price
            return profit

    return profit

if __name__ == '__main__':
    from trading.strategy.candle_pattern.bearish_engulfing import BearEngulfingPattern
    from trading.strategy.candle_pattern.bullish_engulfing import BullEngulfingPattern

    from trading.strategy.profit_loss_management.bull_engulfing_profit_loss import BullEngulfingProfitLoss
    from trading.candlestick import CandleStick
    from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
    from matplotlib.pyplot import title
    import requests
    import json
    import os
    import pandas as pd
    import mplfinance as mpl

    candle_types = [
        # 'shooting_star', 
        'hammer', 
        # 'bull_mazubuzu', 
        # 'bear_mazubuzu'
    ]

    save_path = r'images/plot/'

    binance_crypto_data_crawler = BinanceCryptoDataCrawler()
    crypto_data = binance_crypto_data_crawler.load_from_file(r'dataset/btc_binance_crypto_price_data.json')

    number_winning_candlestick = 0
    total_candlestick = 0

    all_candlestick = []
    for i, candle_info in enumerate(crypto_data['BTCUSDT']['4h']['data'][:]):
        candlestick = CandleStick()
        candlestick.load_candle_stick(candle_info)

        all_candlestick.append(candlestick)
    
    engulfing_pattern = BullEngulfingPattern(all_candlestick)

    engulfing_candle_idxs = engulfing_pattern.run()

    len_candle_right = 10
    len_candle_left = 2
    # Get top 20 candlesticks

    profit_history = []
    loss_history = []
    for engulfing_candle_idx in engulfing_candle_idxs[-30:-19]:
        d = {"Date": [],"Open": [], "High": [], "Low":[], "Close": []}

        for i in range(engulfing_candle_idx - len_candle_left, engulfing_candle_idx + len_candle_right, 1):
            candle_info_j = crypto_data['BTCUSDT']['4h']['data'][i]
            d["Date"].append(datetime.fromtimestamp(candle_info_j['open_time']/1000.0))
            d["Open"].append(candle_info_j['open'])
            d["High"].append(candle_info_j['high'])
            d["Low"].append(candle_info_j['low'])
            d["Close"].append(candle_info_j['close'])

        make_plot_from_dataframe(d, save_path, str(engulfing_pattern))

        bull_engulfing_profit_loss = BullEngulfingProfitLoss(all_candlestick, engulfing_candle_idx)
        entry_price, stop_loss_price, take_profit_price = bull_engulfing_profit_loss.run()

        print("---", datetime.fromtimestamp(crypto_data['BTCUSDT']['4h']['data'][engulfing_candle_idx]['open_time']/1000.0))
        print("Entry price: ", entry_price)
        print("Stop loss price: ", stop_loss_price)
        print("Take profit price: ", take_profit_price)
        profit = calculate_profit_and_loss(entry_price, take_profit_price, stop_loss_price, all_candlestick[engulfing_candle_idx + 1:])

        print("Profit: ", profit)

        profit_history.append(profit)
    
    print("Final profit: ", sum(profit_history))
    # Count number of positive profit
    for profit in profit_history:
        if profit > 0:
            number_winning_candlestick += 1
        total_candlestick += 1

    print("Number of winning candlestick: ", number_winning_candlestick, " / ", total_candlestick)

        

        
