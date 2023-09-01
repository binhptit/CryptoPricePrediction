from backend.notification.telegram_notification import TelegramNotification
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from datahub.data_generator.forex_data_collector import ForexDataCollector
from trading.candlestick import CandleStick
import config
import json
from trading.strategy.profit_loss_management.bear_disvergence_profit_loss import BearDisvergenceProfitLoss
from trading.strategy.profit_loss_management.bull_disvergence_profit_loss import BullDisvergenceProfitLoss
from trading.strategy.profit_loss_management.bull_engulfing_profit_loss import BullEngulfingProfitLoss
from trading.strategy.profit_loss_management.bear_engulfing_profit_loss import BearEngulfingProfitLoss
from trading.strategy.candle_pattern import *
from datetime import datetime
import time
import logging
import multiprocessing
logging.basicConfig(filename='logs/chart_tracking.log', level=logging.INFO)

single_candle_patterns = [
            Hammer,
            InvertedHammer,
            DragonFlyDoji,
            GraveStoneDoji,
            BeltHoldBearish,
            BeltHoldBullish,
            AnomalyHammer,
            AnomalyInvertedHammer
    ]

multiple_candle_patterns = [
        BearishEngulfing,
        BullishEngulfing,
        MorningStarDojiNoGap,
        MorningStarNoGap,
        BullishHarami,
        BearishHarami,
        DarkCloudCover,
        EveningStarDoji,
        EveningStarNoGap,
        ShootingStar,
        HangingMan,
        MatHold,
        BreakawayBearish,
        BreakawayBullish,
        ThreeBlackSoldiers,
        ThreeLineStrikeBearish,
        ThreeLineStrikeBullish,
        ThreeOutsideUp,
        ThreeStarsInTheSouth,
        ThreeWhiteSoldiers,
        StrongBearishDivergence,
        StrongBullishDivergence,
        HiddenBearishDivergence,
        HiddenBullishDivergence
    ]

crypto_time_frames = {
    "1w": 88,
    "1d": 356,
    "4h": 356 * 6,
    "1h": 600,
}

forex_time_frames = {
    # "30m": 200,
    "1h": 600,
    "4h": 356,
    "1d": 365,
    "1w": 365
}

def get_allow_pattern_dict(transaction_history_file = r'dataset/crypto_all_transaction_history.json', symbols=[]):
    pattern_statistics = {}
    allow_pattern = {}
    time_frame = ['15m', '30m', '1h', '4h', '1d', '1w']
    with open(transaction_history_file, 'r') as f:
        transaction_history = json.load(f)

        for pattern, transactions in transaction_history.items():
            pattern_statistics[pattern] = {}
            for tf in time_frame:
                pattern_statistics[pattern][tf] = {}
                for symbol in symbols:
                    total_win_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf and t['win_or_lose'] == "win"])
                    total_trade = len([t for t in transactions if t['symbol'] == symbol and t['time_frame'] == tf])
                    win_rate = total_win_trade / total_trade if total_trade > 0 else 0

                    if symbol not in allow_pattern:
                        allow_pattern[symbol] = {}

                    if tf not in allow_pattern[symbol]:
                        allow_pattern[symbol][tf] = {}

                    if not ((win_rate > 0.5) or ("ivergence" in pattern)):
                        continue

                    allow_pattern[symbol][tf][pattern.replace("/", "")] = {
                        "total_win_trade": total_win_trade,
                        "total_lose_trade": total_trade - total_win_trade,
                        "total_trade": total_trade,
                        "win_rate": win_rate
                    }

    return allow_pattern
    
def analyze_and_send_noti(symbol, time_frame, data_collector, allow_pattern_dict, telegram_notification):
    logging.info(f"Start tracking chart for {symbol} with timeframes {time_frame}")

    current_time = datetime.now()
    dt_string = current_time.strftime("%d/%m/%Y %H:%M:%S")

    full_message = f"\nCurrent time: {dt_string}\n"
    count_send_notice = 0

    message = ""
    message += f"-------------x-\nTimeframe: {time_frame}||{symbol}\n"
    candles_data = data_collector.get_lastest_k_candles(symbol, time_frame, 88)

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
            if "ivergence" in pattern_detection.pattern_name:
                idx_pattern[idx+1].append(pattern_detection)
            else:
                idx_pattern[idx].append(pattern_detection)

    last_candle_idx = len(candlesticks) - 1
    # Check if last candlestick is in pattern
    if len(idx_pattern[last_candle_idx]) > 1 and \
        any(idx_pattern[last_candle_idx][ii].trend != idx_pattern[last_candle_idx][jj].trend 
            for ii in range(len(idx_pattern[last_candle_idx]))
            for jj in range(ii + 1, len(idx_pattern[last_candle_idx]))):
        return
        
    if len(idx_pattern[last_candle_idx]) == 0:
        return
    
    count_pattern_name = dict()
    for pattern in idx_pattern[last_candle_idx]:
        if pattern.pattern_name not in count_pattern_name:
            count_pattern_name[pattern.pattern_name] = 0
        count_pattern_name[pattern.pattern_name] += 1

    overlap_pattern_name = ""
    for pattern_name in count_pattern_name:
        overlap_pattern_name += str(count_pattern_name[pattern_name]) + pattern_name + "_"

    if time_frame not in allow_pattern_dict[symbol] or overlap_pattern_name not in allow_pattern_dict[symbol][time_frame]:
        overlap_pattern_name = None
    else:
        pattern_statistic = allow_pattern_dict[symbol][time_frame][overlap_pattern_name]                        
        pattern_trend = idx_pattern[last_candle_idx][0].trend

        if "divergence" not in overlap_pattern_name:
            if pattern_trend == 'bearish':
                bear_engulfing_profit_loss = BearEngulfingProfitLoss(candlesticks, i)
                entry_price, stop_loss_price, take_profit_price = bear_engulfing_profit_loss.run(rr_ratio=1)
            else:
                bull_engulfing_profit_loss = BullEngulfingProfitLoss(candlesticks, i)
                entry_price, stop_loss_price, take_profit_price = bull_engulfing_profit_loss.run(rr_ratio=1)
        else:
            if pattern_trend == 'bearish':
                bear_disvergence_profit_loss = BearDisvergenceProfitLoss(candlesticks, last_candle_idx)
                entry_price, stop_loss_price, take_profit_price = bear_disvergence_profit_loss.run(rr_ratio=1)
            else:
                bull_disvergence_profit_loss = BullDisvergenceProfitLoss(candlesticks, last_candle_idx)
                entry_price, stop_loss_price, take_profit_price = bull_disvergence_profit_loss.run(rr_ratio=1)
        
        how_much_money_lose_in_failure_case = 5.0
        change_ratio = abs(entry_price - stop_loss_price) / entry_price
        total_usdt = int(how_much_money_lose_in_failure_case / change_ratio)

    if overlap_pattern_name is not None:
        long_or_short = "LONG" if idx_pattern[last_candle_idx][0].trend == "bullish" else "SHORT"
        message += f"Overlaped Pattern: {overlap_pattern_name}.[{pattern_statistic['win_rate']:.2f}%]({pattern_statistic['total_win_trade']}:{pattern_statistic['total_lose_trade']}:{pattern_statistic['total_trade']})\n"
        message += f"Trade {total_usdt}$. Maximum loss:{how_much_money_lose_in_failure_case}$.\n"
        message += f"[{long_or_short}] \nEntry:{entry_price:.4f}, \nStop:{stop_loss_price:.4f}, \nProfit:{take_profit_price:.4f}\n"        
        logging.info(f"Found Pattern: {overlap_pattern_name}")
    
        count_send_notice += 1
        full_message += message

    if count_send_notice:
        telegram_notification.send(full_message)
        logging.info(full_message)
        logging.info("=> Send notification successfully")

def task(symbol, time_frames, data_collector, allow_pattern_dict, telegram_notification):    
    while True:
        # Get the current time
        current_time = datetime.now()                
        minute_value = current_time.minute
        hour_value = current_time.hour

        # change hour value to Utc+7
        hour_value = (hour_value + 7) % 24

        # Reset minute and hour value for test
        # minute_value = 0
        # hour_value = 0

        is_analyze = False
                
        # if minute_value in [28, 29, 58, 59] and '30m' in time_frames:
        #     # Call analyze and send noti 30m
        #     is_analyze = True
        #     analyze_and_send_noti(symbol, '30m', data_collector, allow_pattern_dict, telegram_notification)

        if minute_value in [50, 51] and '1h' in time_frames:
            # Call analyze and send noti 1h
            is_analyze = True
            analyze_and_send_noti(symbol, '1h', data_collector, allow_pattern_dict, telegram_notification)
        
        if hour_value in [2, 6, 10, 14, 18, 22]  and minute_value in [53, 54] and '4h' in time_frames:
            # Call analyze and send noti 4h
            is_analyze = True
            analyze_and_send_noti(symbol, '4h', data_collector, allow_pattern_dict, telegram_notification)
        
        if hour_value in [6] and minute_value in [56, 57] and '1d' in time_frames:
            # Call analyze and send noti 1d
            is_analyze = True
            analyze_and_send_noti(symbol, '1d', data_collector, allow_pattern_dict, telegram_notification)

        if hour_value in [6] and current_time.weekday() == 0 and minute_value in [57, 58] and '1w' in time_frames:
            # Call analyze and send noti 1w
            is_analyze = True
            analyze_and_send_noti(symbol, '1w', data_collector, allow_pattern_dict, telegram_notification)

        sleep_minute = 1
        if is_analyze:
            sleep_minute = 2

        # Sleep for 1 minutes
        logging.info(f"Sleep for {sleep_minute} minutes")
        time.sleep(60*sleep_minute)

def main():
    binance_data_collector = BinanceCryptoDataCrawler()
    forex_data_collector = ForexDataCollector()

    crypto_symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 
        'SOLUSDT', 'DOTUSDT', 'BCHUSDT', 
        'LTCUSDT', 'XRPUSDT', 'AVAXUSDT'
    ]

    crypto_symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT',
        'BCHUSDT', 'LTCUSDT', 'XRPUSDT', 'AVAXUSDT', 'DOGEUSDT', 'ALGOUSDT',
        'MATICUSDT', 'LINKUSDT', 'XLMUSDT', 'CAKEUSDT', 'UNIUSDT', 'ATOMUSDT',
        'FILUSDT', 'VETUSDT', 'TRXUSDT', 'XTZUSDT', 'XMRUSDT', 
        'EOSUSDT', 'THETAUSDT', 'ETCUSDT', 'NEOUSDT', 'AAVEUSDT', 
        'XEMUSDT', 'KSMUSDT',
    ]
    
    # Timeframe and limit

    forex_symbols = [
        "GC=F",
        "EURUSD=X",
        "JPY=X",
        "GBPUSD=X",
        "AUDUSD=X",
        "GBPJPY=X",
        "EURGBP=X",
        "EURCAD=X",
        "EURSEK=X",
        "EURJPY=X"
    ]
    telegram_notification = TelegramNotification(False)

    processes = []
    allow_pattern_dict = get_allow_pattern_dict(symbols=crypto_symbols)
    logging.info(f"[Crypto] Load allow attern dict: {allow_pattern_dict} successfully")

    for symbol in crypto_symbols:
        process = multiprocessing.Process(target=task, args=(symbol, crypto_time_frames, binance_data_collector, allow_pattern_dict, telegram_notification))
        process.start()
        processes.append(process)
    
    forex_allow_pattern_dict = get_allow_pattern_dict(transaction_history_file="dataset/forex_all_transaction_history.json",symbols=forex_symbols)
    logging.info(f"[Forex] Load allow pattern dict: {forex_allow_pattern_dict} successfully")

    for symbol in forex_symbols:
        process = multiprocessing.Process(target=task, args=(symbol, forex_time_frames, forex_data_collector, forex_allow_pattern_dict, telegram_notification))
        process.start()
        processes.append(process)

    # Wait for all processes to complete
    for process in processes:
        process.join()

if __name__ == '__main__':
    main()


