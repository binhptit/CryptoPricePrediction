from backend.notification.telegram_notification import TelegramNotification
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from datahub.data_generator.forex_data_collector import ForexDataCollector
from trading.candlestick import CandleStick
import config
import json
from trading.indicators.suppy_demand import SupplyDemandPrice
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
from datetime import datetime
import time
import logging
import multiprocessing

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

def task(symbol, time_frames, data_collector, allow_pattern_dict, telegram_notification):
    logging.basicConfig(filename='logs/chart_tracking.log', level=logging.INFO)
    logging.info(f"Start tracking chart for {symbol} with timeframes {time_frames}")

    last_hour = -1
    while True:
        # Get the current time
        current_time = datetime.now()
        dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
        if 59 >= current_time.minute >= 0 and last_hour != current_time.hour:
            full_message = f"\nCurrent time: {dt_string}\n"
            count_send_notice = 0

            for time_frame in time_frames:
                message = ""
                message += f"--------------\nTimeframe: {time_frame}||{symbol}\n"
                candles_data = data_collector.get_lastest_k_candles(symbol, time_frame, time_frames[time_frame])

                logging.info(f"[{symbol}_{time_frame}] Get {len(candles_data)} candles successfully")
                candlesticks = []
                for i, candle_info in enumerate(candles_data):
                    candlestick = CandleStick()
                    candlestick.load_candle_stick(candle_info)

                    candlesticks.append(candlestick)
                
                try:
                    idx_pattern = {i: [] for i in range(len(candlesticks))}
                    for pattern in single_candle_patterns:
                        pattern_detection = pattern(candlesticks)
                        single_candle_idx = pattern_detection.run()
                        for idx in single_candle_idx:
                            idx_pattern[idx].append(pattern_detection)
                except Exception as e:
                    return None
                
                multiple_candle_idx = []
                for pattern in multiple_candle_patterns:
                    pattern_detection = pattern(candlesticks)
                    multiple_candle_idx = pattern_detection.run()
                    for idx in multiple_candle_idx:
                        idx_pattern[idx].append(pattern_detection)
               
                last_candle_idx = len(candlesticks) - 2
                # Check if last candlestick is in pattern
                overlap_pattern_name = None
                if len(idx_pattern[last_candle_idx]) > 1 and idx_pattern[last_candle_idx][0].no_candles != idx_pattern[last_candle_idx][1].no_candles \
                    and idx_pattern[last_candle_idx][0].trend == idx_pattern[last_candle_idx][1].trend:
                    overlap_pattern_name = idx_pattern[last_candle_idx][0].pattern_name + "_" + idx_pattern[last_candle_idx][1].pattern_name

                    if overlap_pattern_name not in allow_pattern_dict[symbol][time_frame]:
                        overlap_pattern_name = None

                if overlap_pattern_name is not None:
                    message += f"Overlaped Pattern: {overlap_pattern_name}.\n"
                    logging.info(f"Found Pattern: {overlap_pattern_name}")
                
                if overlap_pattern_name is not None:
                    count_send_notice += 1
                    full_message += message

            if count_send_notice:
                telegram_notification.send(full_message)
                logging.info(full_message)
                logging.info("=> Send notification successfully")
            
            last_hour = current_time.hour

        # Sleep for 5 minutes
        logging.info("Sleep for 5 minutes")
        time.sleep(60*5)

def get_allow_pattern_dict(transaction_histore_file = r'dataset/all_transaction_history.json', symbols=[]):
    pattern_statistics = {}
    allow_pattern = {}
    time_frame = ['4h', '1d', '1w']
    with open(transaction_histore_file, 'r') as f:
        transaction_history = json.load(f)

        for pattern, transactions in transaction_history.items():
            pattern_statistics[pattern] = {}
            for tf in time_frame:
                pattern_statistics[pattern][tf] = {}
                for symbol in symbols:
                    total_win_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf and t['win_or_lose'] == "win"])
                    total_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf])
                    win_rate = total_win_trade / total_trade if total_trade > 0 else 0

                    if win_rate < 0.4 or total_trade < 3:
                        continue

                    if symbol not in allow_pattern:
                        allow_pattern[symbol] = {}

                    if tf not in allow_pattern[symbol]:
                        allow_pattern[symbol][tf] = []

                    allow_pattern[symbol][tf].append(pattern.replace("/", ""))

    return allow_pattern
    
def main():
    binance_data_collector = BinanceCryptoDataCrawler(config.binance_api, config.binance_secret)
    forex_data_collector = ForexDataCollector()

    crypto_symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        'SOLUSDT', 'DOTUSDT', 'BCHUSDT', 
        'LTCUSDT', 'XRPUSDT', 'AVAXUSDT'
    ]
    
    # Timeframe and limit
    crypto_time_frames = {
        "1w": 88,
        "1d": 356,
        "4h": 356 * 6,
    }

    forex_time_frames = {
        "1h": 600,
        "1d": 365,
        "1wk": 100,
        # "1mo": 100,
    }
    forex_symbols = ["GC=F"]
    telegram_notification = TelegramNotification()

    processes = []
    allow_pattern_dict = get_allow_pattern_dict(symbols=crypto_symbols)

    # Start the processes
    for symbol in crypto_symbols:
        process = multiprocessing.Process(target=task, args=(symbol, crypto_time_frames, binance_data_collector, allow_pattern_dict, telegram_notification))
        process.start()
        processes.append(process)
    
    # for symbol in forex_symbols:
    #     process = multiprocessing.Process(target=task, args=(symbol, forex_time_frames, forex_data_collector, allow_pattern_dict, telegram_notification))
    #     process.start()
    #     processes.append(process)

    # Wait for all processes to complete
    for process in processes:
        process.join()

if __name__ == '__main__':
    main()


