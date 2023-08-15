import os
import statistics
import requests
from datetime import datetime
import pandas as pd

from binance.client import Client
from utils.json_handler import dump_json, load_json
from datahub.data_generator.base_generator import BaseGenerator

class BinanceCryptoDataCrawler(BaseGenerator):
    def __init__(self, api_key: str = None, api_secret: str = None) -> None:
        super().__init__(api_key, api_secret)
        self.client = Client(self.api_key, self.api_secret)
        # self.account_info = self.client.get_account()
        
        self.symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT',
            'BCHUSDT', 'LTCUSDT', 'XRPUSDT', 'AVAXUSDT', 'DOGEUSDT', 'ALGOUSDT',
            'MATICUSDT', 'LINKUSDT', 'XLMUSDT', 'CAKEUSDT', 'UNIUSDT', 'ATOMUSDT',
            'FILUSDT', 'ICPUSDT', 'VETUSDT', 'TRXUSDT', 'XTZUSDT', 'XMRUSDT', 'EOSUSDT',
            'THETAUSDT', 'ETCUSDT', 'NEOUSDT', 'AAVEUSDT', 'XEMUSDT', 'MKRUSDT', 'KSMUSDT',
            
            ]

        self.intervals = [
            # '15m', '30m', 
                          '1h', '4h', '1d', '1w']

        self.crypto_data = {
        }

    def load_symbols():
        query = {}
        response = requests.get("https://api.binance.com/api/v3/exchangeInfo", params=query)
        result = response.json()

        all_symbols = [x['symbol'] for x in result['symbols'] if x['symbol'].endswith('USDT')]
        
        symbol_dict = {}
        symbol_dict["USDT"] = [x['symbol'] for x in result['symbols'] if x['symbol'].endswith('USDT')]
        symbol_dict["BUSD"] = [x['symbol'] for x in result['symbols'] if x['symbol'].endswith('BUSD')]
        symbol_dict["BTC"] = [x['symbol'] for x in result['symbols'] if x['symbol'].endswith('BTC')]

        dump_json(f'dataset/all_crypto_symbols.json', symbol_dict)

        return symbol_dict
        
    def load_from_file(self, file_path: str):
        print(f"Load crypto data from {file_path}..")
        self.crypto_data = load_json(file_path)
        print(f"Load done!")
        return self.crypto_data

    def save_as_csv(self, output_path, symbol, timeframe):
        data = {"Date": [],"Open": [], "High": [], "Low":[], "Close": [], "Volume": [], "Adj Close": []}
        
        for candle_info in self.crypto_data[symbol][timeframe]['data']:
            data["Date"].append(datetime.fromtimestamp(candle_info['open_time']/1000.0))
            data["Open"].append(candle_info['open'])
            data["High"].append(candle_info['high'])
            data["Low"].append(candle_info['low'])
            data["Close"].append(candle_info['close'])
            data["Volume"].append(candle_info['volume'])
            data["Adj Close"].append(candle_info['close'])
        
        df = pd.DataFrame(data=data)
        # df.index = pd.DatetimeIndex(df['Date'])
        
        df.to_csv(output_path, index=False)


    def load_from_api(self, save_path, mode = 'all'):
        timestamp = self.client._get_earliest_valid_timestamp('BTCUSDT', '1d')

        for symbol in self.symbols:
            print(f"//- Crawling {symbol} data..")
            self.crypto_data[symbol] = {}
            

            for interval in self.intervals:
                print(f"\tCrawling {interval} timeframe..")
                # request historical candle (or klines) data
                bars = self.client.get_historical_klines(symbol, interval, timestamp)

                self.crypto_data[symbol][interval] = {}
                self.crypto_data[symbol][interval]['data'] = []
                

                min_price = min_volume = min_number_of_trades = 922337203685477580
                max_price = max_volume = max_number_of_trades = 0

                for bar in bars:
                    min_price = min(min_price, float(bar[1]), float(bar[2]),float(bar[3]),float(bar[4]))
                    max_price = max(max_price, float(bar[1]), float(bar[2]),float(bar[3]),float(bar[4]))
                    min_volume = min(min_volume, float(bar[5]))
                    max_volume = max(max_volume, float(bar[5]))
                    min_number_of_trades = min(min_number_of_trades, float(bar[8]))
                    max_number_of_trades = max(max_number_of_trades, float(bar[8]))
                    
                    self.crypto_data[symbol][interval]['data'].append({
                        'open_time': bar[0],
                        'open': float(bar[1]),
                        'high': float(bar[2]),
                        'low': float(bar[3]),
                        'close': float(bar[4]),
                        'volume': float(bar[5]),
                        'close_time': bar[6],
                        'quote_asset_volume': float(bar[7]),
                        'number_of_trades': bar[8],
                        'taker_buy_base_asset_volume': float(bar[9]),
                        'taker_buy_quote_asset_volume': float(bar[10]),
                        'ignore': bar[11]
                    })

                self.crypto_data[symbol][interval]['attributes'] = {
                    'max_price': max_price,
                    'min_price': min_price,
                    'max_volume': max_volume,
                    'min_volume': min_volume,
                    'max_number_of_trades': max_number_of_trades,
                    'min_number_of_trades': min_number_of_trades
                }
            print(f"\tDone {symbol}. -//")

        dump_json(save_path, self.crypto_data)
        print(f"Save data to {save_path} done!")
        return self.crypto_data

    def get_lastest_k_candles(
        self, symbol: str = "BTCUSDT", interval: str = "1d", k: int = 5
    ):
        assert (k > 0), 'k must larger than 0.'
        query = {
            "symbol": symbol,
            "interval": interval,
            "limit": k,
            # "startTime": 1502755200000,
            # "endTime": 1502928000000,
        }
        response = requests.get("https://api.binance.com/api/v3/klines", params=query)

        info_candles = response.json()

        return info_candles
        

    def get_real_time_price(self, symbol: str = "BTCUSDT"):
        # get latest price from Binance API
        current_price = self.client.get_symbol_ticker(symbol=symbol)
        return current_price
