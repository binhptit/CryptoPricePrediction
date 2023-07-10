from trading.indicators.suppy_demand import SupplyDemandPrice
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from utils.json_handler import dump_json, load_json
from datetime import datetime
from trading.candlestick import CandleStick
from trading.strategy.candle_pattern import (
        BearishEngulfing,
        BullishEngulfing,
        BearishHarami,
        BullishHarami,
        DarkCloudCover,
        DojiStar,
        Doji,
        DragonFlyDoji,
        EveningStarDoji,
        EveningStar,
        GraveStoneDoji,
        Hammer,
        HangingMan,
        InvertedHammer,
        MorningStar,
        MorningStarDoji,
        Piercing,
        RainDrop,
        ShootingStar,
        Star
)
import mplfinance as mpl
import os
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

def plot(candlesticks_df, pattern_indexex, output_path, timeframe='4h'):
    width_candle_ohlc = 0.6 if timeframe == '1d' else 0.1

    candlesticks_df.index = pd.DatetimeIndex(candlesticks_df['Date'])
    candlesticks_df['Date'] = candlesticks_df['Date'].apply(mpl_dates.date2num)

    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    candlestick_ohlc(ax, candlesticks_df.values,width=width_candle_ohlc, colorup='green', colordown='red', alpha=0.9)
    date_format = mpl_dates.DateFormatter('%d %b  %Y')
    ax.xaxis.set_major_formatter(date_format)
    for level in pattern_indexex:
        plt.hlines(level[1], xmin=candlesticks_df['Date'][level[0]], xmax=max(candlesticks_df['Date']), colors='blue', linestyle='--')

    # Save fig
    plt.savefig(output_path)

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
    
def main():
    binance_crypto_data_crawler = BinanceCryptoDataCrawler()
    crypto_data = binance_crypto_data_crawler.load_from_file(r'dataset/lastest_crypto_price_data.json')
    all_candlestick = []


    time_frame = '4h'
    for i, candle_info in enumerate(crypto_data['BTCUSDT'][time_frame]['data'][-365:-2]):
        candlestick = CandleStick()
        candlestick.load_candle_stick(candle_info)

        all_candlestick.append(candlestick)

    sdp = SupplyDemandPrice(all_candlestick, None)
    pivots = sdp.run()
    sdp.plot("images/supply_demand.png")
    
    patterns = [
            BearishEngulfing,
            BullishEngulfing,
            Hammer,
            HangingMan,
            InvertedHammer,
            # BearishHarami,
            # BullishHarami,
            # DarkCloudCover,
            DojiStar,
            Doji,
            DragonFlyDoji,
            EveningStarDoji,
            EveningStar,
            GraveStoneDoji,
            MorningStar,
            MorningStarDoji,
            # Piercing,
            # RainDrop,
            ShootingStar,
            Star
    ]

    for pattern in patterns:
        pattern_detection = pattern(all_candlestick)
        index_pattern = pattern_detection.run()

        print("Finding pattern: ", pattern_detection)
        print("Index pattern: ", index_pattern)

        padding_left = 35
        padding_right = 35
        for index in index_pattern:
            d = {"Date": [],"Open": [], "High": [], "Low":[], "Close": []}
            for i in range(max(0, index - padding_left), min(index + padding_right, len(all_candlestick)), 1):
                d["Date"].append(all_candlestick[i].date)
                d["Open"].append(all_candlestick[i].open)
                d["High"].append(all_candlestick[i].high)
                d["Low"].append(all_candlestick[i].low)
                d["Close"].append(all_candlestick[i].close)

            save_path = r'images/plot/'
            # make_plot_from_dataframe(d, save_path, str(pattern_detection))

            if not os.path.exists(save_path + str(pattern_detection)):
                os.mkdir(save_path + str(pattern_detection))
            
            pd_candlesticks = pd.DataFrame(data=d) 
            plot(pd_candlesticks, [[padding_left, all_candlestick[index].close]], save_path + str(pattern_detection) + "/" + str(all_candlestick[index].date) + ".png")


if __name__ == "__main__":
    main()