from .base_generator import BaseGenerator
from typing import List
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from utils.json_handler import dump_json, load_json
from utils.utility import merge_1h4h
from twelvedata import TDClient
import config
import time
import os

class ForexDataCollector(BaseGenerator):
    """
    Class for collecting forex data.
    """

    def __init__(self):
        """
        Initializes the forex data collector.
        """
        super().__init__()
        self.yfinance_intervals = ['30m', '1h','1d']
        self.td_intervals = ['1day', '1week', '4h', '1h']

        self.yf_interval_days = {
            "1h": 10,
            "1d": 365
        }

        self.output_size_dict = {
            "1week": 20 * 52,
            "1day": 10 * 365,
            "4h": 5000,
            "1h": 5000,
        }

        self.forex_data = {
        }

        self.yf_symbols = config.yf_symbols
        self.td_symbols = config.td_symbols

        self.endpoint_cor = "twelevedata"

    def adding_data(self, data, symbol, interval):
        if interval == "1day":
            interval = "1d"
        
        if interval == "1week":
            interval = "1w"

        try:
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
        except Exception as e:
            for index, row in data.iterrows():
                self.forex_data[symbol][interval]["data"].append({
                    # Convert index to timestamp in milliseconds
                    'open_time': datetime.timestamp(index) * 1000,
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': 0,
                    'close_time': datetime.timestamp(index) * 1000,
                })

    def load_from_file(self, file_path: str):
        print(f"Load forex data from {file_path}..")
        self.forex_data = load_json(file_path)
        print(f"Load done!")
        return self.forex_data
    
    def find_date_after_n_days(self, date = "2017-01-01", n_days=30):
        date = datetime.strptime(date, "%Y-%m-%d")
        date_after_n_days = date + timedelta(days=n_days)
        return date_after_n_days.strftime("%Y-%m-%d")

    def load_from_csv_data(self, save_path, data_path: str = "demo/Database-Currency-Pair/"):
        for symbol in self.td_symbols:
            self.forex_data[symbol] = {}

            for interval in self.td_intervals:
                interval = "1d" if interval == "1day" else interval
                interval = "1w" if interval == "1week" else interval

                self.forex_data[symbol][interval] = {
                    "data": [],
                    "attributes": []
                }

                folder_name = symbol.replace("/", "")
                folder_path = f"{data_path}{folder_name}/"

                # File the csv file contain "1_D_" in file name
                try:
                    if interval == "1d":
                        csv_file = [file for file in os.listdir(folder_path) if "1_D_" in file][0]
                    elif interval == "1w":
                        csv_file = [file for file in os.listdir(folder_path) if "1_W_" in file][0]
                    elif interval == "1h" or interval == "4h":
                        csv_file = [file for file in os.listdir(folder_path) if "1_Hour_" in file][0]
                except Exception as e:
                    print(e)
                    continue

                print(f"Collecting {symbol} {interval} from {csv_file}..")

                csv_data = pd.read_csv(f"{folder_path}{csv_file}")
                
                for index, row in csv_data.iterrows():
                    date_value = row[0]
                    try:
                        date_value = datetime.strptime(date_value, "%d.%m.%Y %H:%M:%S.%f GMT-0500")
                    except Exception as e:
                        date_value = datetime.strptime(date_value, "%d.%m.%Y %H:%M:%S.%f GMT-0400")
                    timestamp = datetime.timestamp(date_value) * 1000

                    self.forex_data[symbol][interval]["data"].append({
                    # Convert index to timestamp in milliseconds
                        'open_time': timestamp,
                        'open': row['Open'],
                        'high': row['High'],
                        'low': row['Low'],
                        'close': row['Close'],
                        'volume': row['Volume'],
                        'close_time': timestamp,
                        "original_time": row[0]
                    })
                
                if interval == "4h":
                    self.forex_data[symbol][interval]["data"] = merge_1h4h(self.forex_data[symbol][interval]["data"])
            
            dump_json(save_path, self.forex_data)

    def load_from_api(self, save_path):
        if not self.endpoint_cor == "twelevedata":
            for symbol in self.yf_symbols:
                self.forex_data[symbol] = {}

                for interval in self.yfinance_intervals:
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
                            end_date = self.find_date_after_n_days(date=start_date, n_days=self.yf_interval_days[interval])
                            data = msft.history(start=start_date, end=end_date, interval=interval)
                        
                        print(f"Collecting {symbol} {interval} from {start_date} to {end_date} done!")
                        start_date = end_date

                        self.adding_data(data, symbol, interval)

        elif self.endpoint_cor == "twelevedata":
            print(f"Start collecting forex data from {self.endpoint_cor}..")
            td = TDClient(apikey=config.api_key_list[0])

            for symbol in self.td_symbols:
                self.forex_data[symbol] = {}

                for interval in self.td_intervals:
                    if interval in ["1day", "1week"]:
                        if interval == "1day":
                            interval_format = "1d"
                        else:
                            interval_format = "1w"

                        self.forex_data[symbol][interval_format] = {
                            "data": [],
                            "attributes": []
                        }
                        # Construct the necessary time series
                        ts = td.time_series(
                            symbol=symbol,
                            interval=interval,
                            outputsize=self.output_size_dict[interval],
                            timezone="UTC",
                            order="asc"
                        )

                        try:
                            pd_data = ts.as_pandas()
                        except Exception as e:
                            print(e)
                            current_minute = datetime.today().minute
                            while current_minute == datetime.today().minute:
                                print(f"Sleep for 5 seconds..")
                                time.sleep(5)
                            
                            pd_data = ts.as_pandas()

                        self.adding_data(pd_data, symbol, interval)
                        dump_json(save_path, self.forex_data)
                    else:
                        self.forex_data[symbol][interval] = {
                            "data": [],
                            "attributes": []
                        }
                        start_date = "2012-01-01 00:00:00"
                        current_date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                        while True:
                            print(f"Collecting {symbol} {interval} from {start_date} to {current_date} done!")

                            ts = td.time_series(
                                symbol=symbol,
                                interval=interval,
                                outputsize=self.output_size_dict[interval],
                                timezone="UTC",
                                order="asc",
                                start_date=start_date,
                                end_date=current_date
                            )

                            try:
                                pd_data = ts.as_pandas()
                            except Exception as e:
                                print(e)
                                current_minute = datetime.today().minute
                                while current_minute == datetime.today().minute:
                                    print(f"Sleep for 5 seconds..")
                                    time.sleep(5)
                                
                                pd_data = ts.as_pandas()
                            
                            if len(pd_data) == 1:
                                break
                            
                            current_date = pd_data.index[0].strftime("%Y-%m-%d %H:%M:%S")
                            pd_data = pd_data[1:]

                            # Reverse pd_data
                            pd_data = pd_data[::-1]
                            self.adding_data(pd_data, symbol, interval)

                            
                            
                            # Break if current date is smaller than start date
                            if datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S") < datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"):
                                break
                        
                        # Reverse self.forex_data[symbol][interval]["data"]
                        self.forex_data[symbol][interval]["data"] = self.forex_data[symbol][interval]["data"][::-1]
                        dump_json(save_path, self.forex_data)
        print(f"Save data to {save_path} done!")
        return self.forex_data

    def get_lastest_k_candles(
        self, symbol: str = "GC=F", interval: str = "1h", k: int = 5
    ):
        """
        Gets the lastest k candles from the forex market.
        """
        json_data = []

        interval_td = "1day" if interval == "1d" else interval
        interval_td = "1week" if interval == "1w" else interval_td

        if self.endpoint_cor == "twelevedata":
            td = TDClient(apikey=config.api_key_list[0])
            ts = td.time_series(
                symbol=symbol,
                interval=interval_td,
                outputsize=50,
                timezone="UTC",
                order="asc"
            )

            try:
                pd_data = ts.as_pandas()
            except Exception as e:
                print(e)
                current_minute = datetime.today().minute
                while current_minute == datetime.today().minute:
                    print(f"Sleep for 5 seconds..")
                    time.sleep(5)
                
                pd_data = ts.as_pandas()
            
            for index, row in pd_data.iterrows():
                json_data.append({
                    # Convert index to timestamp in milliseconds
                    'open_time': datetime.timestamp(index) * 1000,
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': 0,
                    'close_time': datetime.timestamp(index) * 1000,
                    "original_time": index.strftime("%Y-%m-%d %H:%M:%S")
                })

        else:
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
        

    