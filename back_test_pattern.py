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
from utils.utility import calculate_profit_and_loss, calculate_profit_and_loss_n_days
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

    print(f"Length of all candlestick: {len(all_candlestick)}")
    single_candle_patterns = [
    ]

    multiple_candle_patterns = [
        # ThreeWhiteSoldiers,
        # ThreeStarsInTheSouth,
        # ThreeLineStrikeBullish,
        # BearishEngulfing,
        # ThreeBlackSoldiers,
        # ThreeLineStrikeBearish,
        # BreakawayBearish,
        # BreakawayBullish,
        # ThreeOutsideUp,
        # MorningStarNoGap,
        # EveningStarNoGap,
        # BellHoldBullish,
        # BellHoldBearish,
        # MatHold,
        # AnomalyHammer,
        AnomalyInvertedHammer
    ]
    
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
        if len(idx_pattern[i]):
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

            save_path = f'images/plot/{symbol}/{start_date}-{end_date}/{time_frame}/'
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
            profit_3_day = calculate_profit_and_loss_n_days(entry_price, take_profit_price, stop_loss_price, all_candlestick[i + 1:], 3)
            profit_5_day = calculate_profit_and_loss_n_days(entry_price, take_profit_price, stop_loss_price, all_candlestick[i + 1:], 5)
            profit_7_day = calculate_profit_and_loss_n_days(entry_price, take_profit_price, stop_loss_price, all_candlestick[i + 1:], 7)
            profit_10_day = calculate_profit_and_loss_n_days(entry_price, take_profit_price, stop_loss_price, all_candlestick[i + 1:], 10)

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
                "rsi": 0,
                "profit_3_day": profit_3_day,
                "profit_5_day": profit_5_day,
                "profit_7_day": profit_7_day,
                "profit_10_day": profit_10_day,
                }
            )

            pd_candlesticks = pd.DataFrame(data=d)
            win_or_lose = "win" if profit > 0 else "lose"
            plot(pd_candlesticks, candle_with_price, rsi_data, save_path + "/" + win_or_lose + "_" + str(all_candlestick[i].date) + ".png")

    for back_test_pattern_name in [
        # "ThreeStarsInTheSouth",
        # "BreakawayBearish",
        # "BreakawayBullish",
        # "AnomalyHammer",
        "AnomalyInvertedHammer"
        ]:
        count_total_transaction = 0
        count_total_win_transaction = 0
        count_total_win_3_day_transaction = 0
        count_total_win_5_day_transaction = 0
        count_total_win_7_day_transaction = 0
        count_total_win_10_day_transaction = 0
        for pattern_name in transaction_history:        
            if back_test_pattern_name in pattern_name:
                count_total_transaction += len(transaction_history[pattern_name])
                count_total_win_transaction += len([transaction for transaction in transaction_history[pattern_name] if transaction['profit'] > 0])
                count_total_win_3_day_transaction += len([transaction for transaction in transaction_history[pattern_name] if transaction['profit_3_day'] > 0])
                count_total_win_5_day_transaction += len([transaction for transaction in transaction_history[pattern_name] if transaction['profit_5_day'] > 0])
                count_total_win_7_day_transaction += len([transaction for transaction in transaction_history[pattern_name] if transaction['profit_7_day'] > 0])
                count_total_win_10_day_transaction += len([transaction for transaction in transaction_history[pattern_name] if transaction['profit_10_day'] > 0])

        if count_total_transaction == 0:
            continue
        
        print(f"Total {back_test_pattern_name} transaction: {count_total_transaction}")
        print(f"Total win {back_test_pattern_name} transaction: {count_total_win_transaction}")
        print(f"Total win {back_test_pattern_name} transaction ratio: {count_total_win_transaction / count_total_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 3 day: {count_total_win_3_day_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 3 day ratio: {count_total_win_3_day_transaction / count_total_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 5 day: {count_total_win_5_day_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 5 day ratio: {count_total_win_5_day_transaction / count_total_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 7 day: {count_total_win_7_day_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 7 day ratio: {count_total_win_7_day_transaction / count_total_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 10 day: {count_total_win_10_day_transaction}")
        print(f"Total win {back_test_pattern_name} transaction 10 day ratio: {count_total_win_10_day_transaction / count_total_transaction}")
    
    return transaction_history

from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler

def main():
    # forex_data_crawler = ForexDataCollector()
    # forex_data = forex_data_crawler.load_from_file(r'dataset/lastest_forex_price_data.json')
    
    binance_crypto_data_crawler = BinanceCryptoDataCrawler()
    crypto_data = binance_crypto_data_crawler.load_from_file(r'dataset/lastest_crypto_price_data.json')

    time_frames = [
        # '1h',
        '4h',
        '1d',
        '1w'
    ]

    symbols = [
        "GC=F",
        # "EURUSD=X",
        # "JPY=X",
        # "GBPUSD=X",
        # "AUDUSD=X",
        # "EURJPY=X",
        # "GBPJPY=X",
        # "EURGBP=X",
        # "EURCAD=X",
        # "EURSEK=X",
        # "EURCHF=X",
        # "EURHUF=X",
        # "EURJPY=X"
    ]

    symbols = [
        'BTCUSDT', 
        # 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        # 'SOLUSDT', 'DOTUSDT', 'BCHUSDT', 
        # 'LTCUSDT', 'XRPUSDT', 'AVAXUSDT'
    ]

    time_range_dict = {
        "year": [
            ("01/01/2018", "01/01/2024")
        ],
    }

    for trend_key, time_range_list in time_range_dict.items():
        for time_range in time_range_list:
            for symbol in symbols:
                for time_frame in time_frames:
                    transaction_history = back_test(crypto_data, time_frame, symbol, time_range[0], time_range[1])
                   
if __name__ == "__main__":
    main()