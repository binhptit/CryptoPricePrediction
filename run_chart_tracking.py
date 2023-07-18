from backend.notification.telegram_notification import TelegramNotification
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from datahub.data_generator.forex_data_collector import ForexDataCollector
from trading.candlestick import CandleStick
import config
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



def task(symbol, time_frames, data_collector, all_pattern_detection, telegram_notification):
    logging.basicConfig(filename='logs/chart_tracking.log', level=logging.INFO)
    logging.info(f"Start tracking chart for {symbol} with timeframes {time_frames}")

    last_hour = -1
    while True:
        # Get the current time
        current_time = datetime.now()
        dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")
        if 6 >= current_time.minute >= 0 and last_hour != current_time.hour:
            full_message = f"\nCurrent time: {dt_string}\n"
            count_send_notice = 0

            all_pivots = []
            for time_frame in time_frames:
                message = ""
                logging.info(f"--------------\nTimeframe: {time_frame}||{symbol}")
                message += f"--------------\nTimeframe: {time_frame}||{symbol}\n"
                candles_data = data_collector.get_lastest_k_candles(symbol, time_frame, time_frames[time_frame])

                candlesticks = []
                for i, candle_info in enumerate(candles_data):
                    candlestick = CandleStick()
                    candlestick.load_candle_stick(candle_info)

                    candlesticks.append(candlestick)
                
                logging.info(f"Get {len(candlesticks)} candlesticks successfully")

                # message += "Current price: " + str(candlesticks[-1].close) + "\n"
                # Check if last candlestick is in pattern
                matched_pattern = []
                for pattern_detection in all_pattern_detection:
                    pattern = pattern_detection(candlesticks)
                    pattern_indexes = pattern.run()

                    if len(pattern_indexes) and pattern_indexes[-1] == len(candlesticks)-2:
                        matched_pattern.append(pattern)

                if len(matched_pattern):
                    message += f"Pattern: {matched_pattern}.\n"
                    logging.info(f"Found Pattern: {matched_pattern}")
                
                # Check if last candlestick is in supply demand area
                last_candle_stick = candlesticks[-2]
                supply_demand_detector = SupplyDemandPrice(candlesticks, None)
                pivots = supply_demand_detector.run()
                
                if time_frame not in ["1h"]:
                    all_pivots.extend(pivots)
                
                overlap_area = []
                for i, level in all_pivots:
                    upper_bound = level * 1.02
                    lower_bound = level * 0.98

                    if (last_candle_stick.low <= upper_bound and last_candle_stick.low >= lower_bound) \
                    or (last_candle_stick.high <= upper_bound and last_candle_stick.high >= lower_bound) \
                    or (last_candle_stick.high >= upper_bound and last_candle_stick.low <= lower_bound):
                        overlap_area.append(level)
                
                if len(overlap_area):
                    message += f"Reach support_demand area.\n"
                    logging.info(f"Support_demand area: {overlap_area}.")

                if len(overlap_area) and len(matched_pattern):
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

def main():
    binance_data_collector = BinanceCryptoDataCrawler(config.binance_api, config.binance_secret)
    forex_data_collector = ForexDataCollector()

    crypto_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 
                     'BCHUSDT', 'LTCUSDT']
    
    # Timeframe and limit
    crypto_time_frames = {
        "1w": 88,
        "1d": 365,
        "4h": 400,
        "1h": 600,
    }

    forex_time_frames = {
        "1h": 600,
        "1d": 365,
        "1wk": 100,
        # "1mo": 100,
    }
    forex_symbols = ["GC=F"]
    telegram_notification = TelegramNotification()


    patterns = [
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
            # Piercing,
            RainDrop,
            ShootingStar,
            Star
    ]

    # task(forex_symbols[0], forex_time_frames, forex_data_collector, patterns, telegram_notification)

    # Create a list to store the process instances
    processes = []

    # Start the processes
    for symbol in crypto_symbols:
        process = multiprocessing.Process(target=task, args=(symbol, crypto_time_frames, binance_data_collector, patterns, telegram_notification))
        process.start()
        processes.append(process)
    
    for symbol in forex_symbols:
        process = multiprocessing.Process(target=task, args=(symbol, forex_time_frames, forex_data_collector, patterns, telegram_notification))
        process.start()
        processes.append(process)

    # Wait for all processes to complete
    for process in processes:
        process.join()

if __name__ == '__main__':
    main()


