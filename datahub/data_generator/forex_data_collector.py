from .base_generator import BaseGenerator
from typing import List
import pandas as pd
import yfinance as yf
from datetime import datetime

class ForexDataCollector(BaseGenerator):
    """
    Class for collecting forex data.
    """

    def __init__(self):
        """
        Initializes the forex data collector.
        """
        super().__init__()
        pass

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


        

    