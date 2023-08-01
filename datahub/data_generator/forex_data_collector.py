from .base_generator import BaseGenerator
from typing import List
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from utils.json_handler import dump_json, load_json

class ForexDataCollector(BaseGenerator):
    """
    Class for collecting forex data.
    """

    def __init__(self):
        """
        Initializes the forex data collector.
        """
        super().__init__()
        self.symbols = []

        self.intervals = ['30m', '1h','1d']
        
        self.interval_days = {
            "30m": 10,
            "1h": 10,
            "1d": 365
        }
        self.forex_data = {
        }

        self.symbols = [
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

    def load_from_file(self, file_path: str):
        print(f"Load forex data from {file_path}..")
        self.crypto_data = load_json(file_path)
        print(f"Load done!")
        return self.crypto_data
    
    def find_date_after_n_days(self, date = "2017-01-01", n_days=30):
        date = datetime.strptime(date, "%Y-%m-%d")
        date_after_n_days = date + timedelta(days=n_days)
        return date_after_n_days.strftime("%Y-%m-%d")

    def load_from_api(self, save_path, mode = 'all'):
        for symbol in self.symbols:
            self.forex_data[symbol] = {}
            for interval in self.intervals:
                self.forex_data[symbol][interval] = {
                    "data": [],
                    "attributes": []
                }

                msft = yf.Ticker(symbol)

                start_date = "2021-01-01"
                while True:
                    # End loop when start date is greater than today
                    if datetime.strptime(start_date, "%Y-%m-%d") > datetime.today():
                        break
                    
                    if interval == "1d":
                        data = msft.history(period="max", interval="1d")
                    else:
                        end_date = self.find_date_after_n_days(date=start_date, n_days=self.interval_days[interval])
                        data = msft.history(start=start_date, end=end_date, interval=interval)
                    
                    print(f"Collecting {symbol} {interval} from {start_date} to {end_date} done!")
                    start_date = end_date

                    for index, row in data.iterrows():
                        self.forex_data[symbol][interval]["data"].append({
                            # Convert index to timestamp in milliseconds
                            'open_time': datetime.timestamp(index) * 1000,
                            'open': row['Open'],
                            'high': row['High'],
                            'low': row['Low'],
                            'close': row['Close'],
                            'volume': row['Volume'],
                            'close_time': datetime.timestamp(index) * 1000,
                        })
                        
        dump_json(save_path, self.forex_data)
        print(f"Save data to {save_path} done!")
        return self.forex_data

    def get_lastest_k_candles(
        self, symbol: str = "GC=F", interval: str = "1h", k: int = 5
    ):
        """
        Gets the lastest k candles from the forex market.
        """
        assert interval in ["1m", "5m", "15m", "30m", "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        json_data = []
        data = yf.download(tickers = symbol , period =f'{k}{interval[1:]}', interval = interval)
        for index, row in data.iterrows():
            json_data.append({
                # Convert index to timestamp in milliseconds
                'open_time': datetime.timestamp(index) * 1000,
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume'],
                'adj_close': row['Adj Close'],
                'close_time': datetime.timestamp(index) * 1000,
            })
        
        return json_data
        

    