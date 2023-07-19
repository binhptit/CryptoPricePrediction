from trading.indicators.suppy_demand import SupplyDemandPrice
from trading.indicators.rsi import RSI
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from utils.json_handler import dump_json, load_json
from datetime import datetime
from trading.strategy.profit_loss_management.bull_engulfing_profit_loss import BullEngulfingProfitLoss
from trading.strategy.profit_loss_management.bear_engulfing_profit_loss import BearEngulfingProfitLoss
from trading.candlestick import CandleStick
from utils.utility import calculate_profit_and_loss
import xlsxwriter
import json

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
import logging
# logging to file
logging.basicConfig(filename='back_test.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def plot(candlesticks_df, pattern_indexex, output_path, timeframe='4h'):
    if timeframe == '1d':
        width_candle_ohlc = 1.5
        figsize = (16, 9)
    elif timeframe == '4h':
        width_candle_ohlc = 0.1
        figsize = (16, 9)
    elif timeframe == '1w':
        width_candle_ohlc = 8.0
        figsize = (10, 9)

    candlesticks_df.index = pd.DatetimeIndex(candlesticks_df['Date'])
    candlesticks_df['Date'] = candlesticks_df['Date'].apply(mpl_dates.date2num)

    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    candlestick_ohlc(ax, candlesticks_df.values,width=width_candle_ohlc, colorup='green', colordown='red', alpha=0.9)
    date_format = mpl_dates.DateFormatter('%d %b  %Y')
    ax.xaxis.set_major_formatter(date_format)
    for level in pattern_indexex:
        plt.hlines(level[1], xmin=candlesticks_df['Date'][level[0]], xmax=max(candlesticks_df['Date']), colors='blue', linestyle='--')

    # Save fig
    plt.savefig(output_path)

    # Release memory
    plt.close(fig)

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

def back_test(crypto_data, time_frame,symbol, start_date="01/01/2022", end_date="01/12/2022", backtest_candle=1000):
    print(f"Back test for {symbol} on {time_frame} time frame from {start_date} to {end_date}")
    all_candlestick = []

    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")

    # if time_frame == '1d':
    #     backtest_candle = 550
    # elif time_frame == '4h':
    #     backtest_candle = 365 * 6
    # elif time_frame == '1h':
    #     backtest_candle = 365 * 6 * 2

    for i, candle_info in enumerate(crypto_data[symbol][time_frame]['data'][:]):
        try:
            candle_date = datetime.fromtimestamp(int(candle_info['open_time']) / 1000)
        except Exception as e:
            candle_date = datetime.fromtimestamp(int(candle_info[0]) / 1000)
        
        # Check if candlestick is in date range
        if candle_date < start_date or candle_date > end_date:
            continue

        candlestick = CandleStick()
        candlestick.load_candle_stick(candle_info)
        
        
        all_candlestick.append(candlestick)

    single_candle_patterns = [
            BearishEngulfing,
            BullishEngulfing,
            Hammer,
            InvertedHammer,
            # Doji,
            DragonFlyDoji,
            GraveStoneDoji,
    ]

    multiple_candle_patterns = [
        MorningStar,
        MorningStarDoji,
        BullishHarami,
        BearishHarami,
        DarkCloudCover,
        # DojiStar,
        EveningStarDoji,
        EveningStar,
        ShootingStar,
        # Star,
        HangingMan,
    ]

    rsi = RSI(all_candlestick, None)
    rsi_values = rsi.run() 

    try:
        idx_pattern = {i: [] for i in range(len(all_candlestick))}
        for pattern in single_candle_patterns:
            pattern_detection = pattern(all_candlestick)
            single_candle_idx = pattern_detection.run()

            for idx in single_candle_idx:
                idx_pattern[idx].append(pattern_detection)
    except Exception as e:
        return None
    
    multiple_candle_idx = []
    for pattern in multiple_candle_patterns:
        pattern_detection = pattern(all_candlestick)
        multiple_candle_idx = pattern_detection.run()

        for idx in multiple_candle_idx:
            idx_pattern[idx].append(pattern_detection)

    
    transaction_history = {}
    for i in range(len(all_candlestick)):
        if len(idx_pattern[i]) > 1 and idx_pattern[i][0].no_candles != idx_pattern[i][1].no_candles \
            and idx_pattern[i][0].trend == idx_pattern[i][1].trend:
            padding_right = 15
            padding_left = 50
            padding_left = i if i < padding_left else padding_left
            padding_right = len(all_candlestick) - i if len(all_candlestick) - i < padding_right else padding_right
            d = {"Date": [],"Open": [], "High": [], "Low":[], "Close": []}
            for ii in range(max(0, i - padding_left), min(len(all_candlestick), i + padding_right), 1):
                d["Date"].append(all_candlestick[ii].date)
                d["Open"].append(all_candlestick[ii].open)
                d["High"].append(all_candlestick[ii].high)
                d["Low"].append(all_candlestick[ii].low)
                d["Close"].append(all_candlestick[ii].close)

            candle_with_price = []
            candle_with_price.append([padding_left, all_candlestick[i].close])

            save_path = f'images/plot/{symbol}/{start_date}-{end_date}/{time_frame}/'
            overlap_pattern_name = idx_pattern[i][0].pattern_name + "_" + idx_pattern[i][1].pattern_name + "/"
            save_path += overlap_pattern_name

            # Make multiple directory if not exist
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            if idx_pattern[i][0].trend == 'bearish':
                bear_engulfing_profit_loss = BearEngulfingProfitLoss(all_candlestick, i)
                entry_price, stop_loss_price, take_profit_price = bear_engulfing_profit_loss.run(rr_ratio=1)
            else:
                bull_engulfing_profit_loss = BullEngulfingProfitLoss(all_candlestick, i)
                entry_price, stop_loss_price, take_profit_price = bull_engulfing_profit_loss.run(rr_ratio=1)

            if overlap_pattern_name not in transaction_history:
                transaction_history[overlap_pattern_name] = []
            
            profit = calculate_profit_and_loss(entry_price, take_profit_price, stop_loss_price, all_candlestick[i + 1:])

            transaction_history[overlap_pattern_name].append(
                {
                "pattern_name": overlap_pattern_name,
                "date": str(all_candlestick[i].date),
                "time_frame": time_frame,
                "symbol": symbol,
                "long_or_short": "short" if idx_pattern[i][0].trend == 'bearish' else "long",
                "profit": profit,
                "entry_price": entry_price,
                "take_profit_price": take_profit_price,
                "stop_loss_price": stop_loss_price,
                "win_or_lose": "win" if profit > 0 else "lose",
                "rsi": rsi_values[i]
                }
            )

            pd_candlesticks = pd.DataFrame(data=d)
            win_or_lose = "win" if profit > 0 else "lose"
            plot(pd_candlesticks, candle_with_price, save_path + "/" + win_or_lose + "_" + str(all_candlestick[i].date) + ".png")
    
    # Statisic
    # for pattern_name in transaction_history:
    #     profit = 0
    #     for transaction in transaction_history[pattern_name]:
    #         profit += transaction['profit']
        
    #     print(f"/-------------- {pattern_name} ---------------------/")
    #     print(f"Profit: {profit}. Total transaction: {len(transaction_history[pattern_name])}")
    #     print(f"Ratio win/loss: {len([transaction for transaction in transaction_history[pattern_name] if transaction['profit'] > 0]) / len(transaction_history[pattern_name])}")

    return transaction_history

def main():
    binance_crypto_data_crawler = BinanceCryptoDataCrawler()
    crypto_data = binance_crypto_data_crawler.load_from_file(r'dataset/lastest_crypto_price_data.json')

    time_frames = ['4h', '1d', '1w']
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        'SOLUSDT', 'DOTUSDT', 'BCHUSDT', 
        'LTCUSDT', 'XRPUSDT', 'AVAXUSDT'
    ]

    symbols = [
            # 'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT',
            # 'BCHUSDT', 'LTCUSDT', 'XRPUSDT', 'AVAXUSDT', 'DOGEUSDT', 'ALGOUSDT',
            'MATICUSDT', 'LINKUSDT', 'XLMUSDT', 'CAKEUSDT', 'UNIUSDT', 'ATOMUSDT',
            # 'FILUSDT', 'ICPUSDT', 'VETUSDT', 'TRXUSDT', 'XTZUSDT', 'XMRUSDT', 'EOSUSDT',
            # 'THETAUSDT', 'ETCUSDT', 'NEOUSDT', 'AAVEUSDT', 'XEMUSDT', 'MKRUSDT', 'KSMUSDT'
    ]

    headers = [
        "Pattern Name",
        "Date",
        "Time Frame",
        "Symbol",
        "Long or Short",
        "Win or Lose",
        "Profit",
        "Entry Price",
        "Take Profit Price",
        "Stop Loss Price",
        "RSI"
    ]
    
    background_colors = [
        "#F2F2F2",  # Light gray
        "#E5E5E5",  # Lighter gray
        "#FAFAD2",  # Light goldenrod yellow
        "#FFF8DC",  # Cornsilk
        "#F5FFFA",  # Mint cream
        "#F0FFF0",  # Honeydew
        "#F0F8FF",  # Alice blue
        "#F5F5F5",  # White smoke
        "#F8F8FF",  # Ghost white
        "#F0FFFF"   # Azure
    ]

    excel_file = xlsxwriter.Workbook('crypto_current_transaction_history.xlsx')

    time_range_dict = {
        "year": [
            # ("01/01/2018", "01/01/2019"),
            # ("01/01/2019", "01/01/2020"),
            # ("01/01/2020", "01/01/2021"),
            # ("01/01/2021", "01/01/2022"),
            # ("01/01/2022", "01/01/2023"),
            # ("01/01/2023", "01/01/2024"),
            ("01/01/2018", "01/01/2024")
        ],
        # "uptrend": [
        #     ("10/12/2018", "16/09/2019"),
        #     ("16/03/2020", "03/05/2021"),
        #     ("21/06/2021", "15/11/2021"),
        #     ("14/11/2022", "01/12/2023")
        # ],
        # "downtrend": [
        #     ("17/06/2019", "16/03/2020"),
        #     ("15/04/2021", "19/07/2021"),
        #     ("18/10/2021", "02/01/2023")
        # ]
    }

    all_transaction_history = {}

    for trend_key, time_range_list in time_range_dict.items():
        for time_range in time_range_list:
            worksheet = excel_file.add_worksheet(f'{trend_key}_{time_range[0].replace("/", ".")}_{time_range[1].replace("/", ".")}')
        
            # Define cell formats
            header_format = excel_file.add_format({'bold': True})

            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)

            color_idx = 0

            row = 1
            row_analyze = 0
            col_analyze = 13

            analyze_sheet = ["Pattern", "Symbol", "Timeframe", "Win", "Lose", "Total Transaction", "Win Ratio", "Final Profit"]
            for col, header in enumerate(analyze_sheet):
                worksheet.write(row_analyze, col_analyze + col, header, header_format)
            row_analyze += 1
            
            for symbol in symbols:
                color_idx += 1
                color_idx = color_idx % len(background_colors)
                row_format = excel_file.add_format({'bg_color': background_colors[color_idx]})

                for time_frame in time_frames:
                    transaction_history = back_test(crypto_data, time_frame, symbol, time_range[0], time_range[1])
                    if transaction_history is None:
                        continue
                        
                    for pattern_name in transaction_history:
                        if pattern_name not in all_transaction_history:
                            all_transaction_history[pattern_name] = []
                        all_transaction_history[pattern_name] += transaction_history[pattern_name]

                        final_profit = 0
                        for data in transaction_history[pattern_name]:
                            worksheet.write(row, 0, data["pattern_name"], row_format)
                            # Convert timestamp to datetime
                            worksheet.write(row, 1, data["date"], row_format)
                            worksheet.write(row, 2, data["time_frame"], row_format)
                            worksheet.write(row, 3, data["symbol"], row_format)
                            worksheet.write(row, 4, data["long_or_short"], row_format)
                            worksheet.write(row, 5, data["win_or_lose"], row_format)
                            worksheet.write(row, 6, data["profit"], row_format)
                            worksheet.write(row, 7, data["entry_price"], row_format)
                            worksheet.write(row, 8, data["take_profit_price"], row_format)
                            worksheet.write(row, 9, data["stop_loss_price"], row_format)
                            worksheet.write(row, 10, data["rsi"], row_format)

                            row += 1

                            final_profit += data["profit"]
                        
                        worksheet.write(row_analyze, col_analyze, pattern_name, row_format)
                        worksheet.write(row_analyze, col_analyze + 1, symbol, row_format)
                        worksheet.write(row_analyze, col_analyze + 2, time_frame, row_format)
                        worksheet.write(row_analyze, col_analyze + 3, len([transaction for transaction in transaction_history[pattern_name] if transaction['profit'] > 0]), row_format)
                        worksheet.write(row_analyze, col_analyze + 4, len([transaction for transaction in transaction_history[pattern_name] if transaction['profit'] < 0]), row_format)
                        worksheet.write(row_analyze, col_analyze + 5, len(transaction_history[pattern_name]), row_format)
                        worksheet.write(row_analyze, col_analyze + 6, len([transaction for transaction in transaction_history[pattern_name] if transaction['profit'] > 0]) / len(transaction_history[pattern_name]), row_format)
                        worksheet.write(row_analyze, col_analyze + 7, final_profit, row_format)

                        row_analyze += 1 
    excel_file.close()

    # Save all transaction history
    with open('all_transaction_history.json', 'w') as f:
        json.dump(all_transaction_history, f, indent=4)


if __name__ == "__main__":
    main()