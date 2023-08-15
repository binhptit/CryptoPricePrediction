from trading.indicators.suppy_demand import SupplyDemandPrice
from trading.indicators.rsi import RSI
from datahub.data_generator.forex_data_collector import ForexDataCollector
from utils.json_handler import dump_json, load_json
from datetime import datetime
from trading.indicators.rsi_divergence import RsiDivergence
import matplotlib.ticker as mticker
from trading.strategy.profit_loss_management.bull_engulfing_profit_loss import BullEngulfingProfitLoss
from trading.strategy.profit_loss_management.bear_engulfing_profit_loss import BearEngulfingProfitLoss
from trading.strategy.profit_loss_management.bear_disvergence_profit_loss import BearDisvergenceProfitLoss
from trading.strategy.profit_loss_management.bull_disvergence_profit_loss import BullDisvergenceProfitLoss
from trading.candlestick import CandleStick
from utils.utility import calculate_profit_and_loss
import xlsxwriter
import json
import mplfinance as mpf

from trading.strategy.candle_pattern import *
import mplfinance as mpl
import os
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import logging
# logging to file
logging.basicConfig(filename='back_test.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def plot(candlesticks_df, pattern_indexex, rsi_data, output_path, timeframe='4h'):
    candlesticks_df.index = pd.DatetimeIndex(candlesticks_df['Date'])
    # candlesticks_df['Date'] = candlesticks_df['Date'].apply(mpl_dates.date2num)

    mco = [None] * len(candlesticks_df['Date'])
    mco[pattern_indexex[0][0]] = 'blue'

    ap =[ mpf.make_addplot(candlesticks_df['Close'],panel=1,type='line',ylabel='Line'),
          mpf.make_addplot(rsi_data['RSI'],panel=2,type='line',ylabel='RSI'),
    ]
    
    # mpf.plot(candlesticks_df,type='candle',savefig=output_path, style='yahoo', marketcolor_overrides=mco)
    mpf.plot(candlesticks_df,
             type='candle',
             savefig=output_path,
             style='yahoo',
             addplot=ap,
             vlines=dict(vlines=candlesticks_df['Date'][pattern_indexex[0][0]],
                         linewidths=10,alpha=0.4)
            )

def back_test(crypto_data, time_frame,symbol, start_date="01/01/2022", end_date="01/12/2022", backtest_candle=1000):
    print(f"Back test for {symbol} on {time_frame} time frame from {start_date} to {end_date}")
    all_candlestick = []

    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")

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
            HiddenBearishDivergence,
            HiddenBullishDivergence,
            StrongBearishDivergence,
            StrongBullishDivergence,
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
        try:
            pattern_detection = pattern(all_candlestick)
            multiple_candle_idx = pattern_detection.run()
        except Exception as e:
            continue
        for idx in multiple_candle_idx:
            idx_pattern[idx].append(pattern_detection)

    transaction_history = {}
    for i in range(len(all_candlestick)):
        if (len(idx_pattern[i]) == 1) or (len(idx_pattern[i]) > 1 \
            and idx_pattern[i][0].trend == idx_pattern[i][1].trend)\
                or any([ "divergence" in pattern.pattern_name for pattern in idx_pattern[i]]):
            padding_right = 30
            padding_left = 50
            padding_left = i if i < padding_left else padding_left
            padding_right = len(all_candlestick) - i if len(all_candlestick) - i < padding_right else padding_right
            
            sub_candlesticks = all_candlestick[max(0, i - padding_left): min(len(all_candlestick), i + padding_right)]
            rsi_divergence = RsiDivergence(sub_candlesticks)
            rsi_data = rsi_divergence.rsi_data
    
            d = {"Date": [],"Open": [], "High": [], "Low":[], "Close": []}
            for ii in range(max(0, i - padding_left), min(len(all_candlestick), i + padding_right), 1):
                d["Date"].append(all_candlestick[ii].date)
                d["Open"].append(all_candlestick[ii].open)
                d["High"].append(all_candlestick[ii].high)
                d["Low"].append(all_candlestick[ii].low)
                d["Close"].append(all_candlestick[ii].close)

            candle_with_price = []
            candle_with_price.append([padding_left, all_candlestick[i].close])

            save_path = f'images/plot_forex/{symbol}/{start_date}-{end_date}/{time_frame}/'
            count_pattern_name = dict()
            for pattern in idx_pattern[i]:
                if pattern.pattern_name not in count_pattern_name:
                    count_pattern_name[pattern.pattern_name] = 0
                count_pattern_name[pattern.pattern_name] += 1
            
            overlap_pattern_name = ""
            for pattern_name in count_pattern_name:
                overlap_pattern_name += str(count_pattern_name[pattern_name]) + pattern_name + "_"

            save_path += overlap_pattern_name

            # Make multiple directory if not exist
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            
            pattern_trend = None
            for pattern in idx_pattern[i]:
                if "divergence" in pattern.pattern_name:
                    pattern_trend = pattern.trend
            
            if pattern_trend is None:
                pattern_trend = idx_pattern[i][0].trend

            if "divergence" not in overlap_pattern_name:
                if pattern_trend == 'bearish':
                    bear_engulfing_profit_loss = BearEngulfingProfitLoss(all_candlestick, i)
                    entry_price, stop_loss_price, take_profit_price = bear_engulfing_profit_loss.run(rr_ratio=1)
                else:
                    bull_engulfing_profit_loss = BullEngulfingProfitLoss(all_candlestick, i)
                    entry_price, stop_loss_price, take_profit_price = bull_engulfing_profit_loss.run(rr_ratio=1)
            else:
                if pattern_trend == 'bearish':
                    bear_disvergence_profit_loss = BearDisvergenceProfitLoss(all_candlestick, i)
                    entry_price, stop_loss_price, take_profit_price = bear_disvergence_profit_loss.run(rr_ratio=1)
                else:
                    bull_disvergence_profit_loss = BullDisvergenceProfitLoss(all_candlestick, i)
                    entry_price, stop_loss_price, take_profit_price = bull_disvergence_profit_loss.run(rr_ratio=1)

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
            plot(pd_candlesticks, candle_with_price, rsi_data, save_path + "/" + win_or_lose + "_" + str(all_candlestick[i].date) + ".png")

    count_total_divergence_transaction = 0
    count_total_win_divergence_transaction = 0
    for pattern_name in transaction_history:        
        if "divergence" in pattern_name:
            count_total_divergence_transaction += len(transaction_history[pattern_name])
            count_total_win_divergence_transaction += len([transaction for transaction in transaction_history[pattern_name] if transaction['profit'] > 0])

    print(f"Total divergence transaction: {count_total_divergence_transaction}")
    print(f"Total win divergence transaction: {count_total_win_divergence_transaction}")
    print(f"Total win divergence transaction ratio: {count_total_win_divergence_transaction / count_total_divergence_transaction}")
    return transaction_history

def main():
    forex_data_crawler = ForexDataCollector()
    forex_data = forex_data_crawler.load_from_file(r'dataset/lastest_forex_price_data.json')

    time_frames = [
        '30m','1h', '1d'
    ]

    symbols = [
        "GC=F",
        "EURUSD=X",
        "JPY=X",
        "GBPUSD=X",
        "AUDUSD=X",
        "EURJPY=X",
        "GBPJPY=X",
        "EURGBP=X",
        "EURCAD=X",
        "EURSEK=X",
        "EURCHF=X",
        "EURHUF=X",
        "EURJPY=X"
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

    excel_file = xlsxwriter.Workbook('forex_current_transaction_history.xlsx')

    time_range_dict = {
        "year": [
            ("01/01/2020", "04/08/2023")
        ],
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
                    transaction_history = back_test(forex_data, time_frame, symbol, time_range[0], time_range[1])
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
                            # worksheet.write(row, 10, data["rsi"], row_format)

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
    with open('dataset/forex_all_transaction_history.json', 'w') as f:
        json.dump(all_transaction_history, f, indent=4)


if __name__ == "__main__":
    main()