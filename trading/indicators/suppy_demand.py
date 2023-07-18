from .base import BaseIndicator
from typing import List
from ..candlestick import CandleStick
import pandas as pd
import numpy as np

import yfinance as yf
import numpy as np
import math
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
import datetime

def is_support(df,i):
  cond1 = df['Low'][i] < df['Low'][i-1] 
  cond2 = df['Low'][i] < df['Low'][i+1] 
  cond3 = df['Low'][i+1] < df['Low'][i+2] 
  cond4 = df['Low'][i-1] < df['Low'][i-2]
  return (cond1 and cond2 and cond3 and cond4)

def is_resistance(df,i):
  cond1 = df['High'][i] > df['High'][i-1] 
  cond2 = df['High'][i] > df['High'][i+1] 
  cond3 = df['High'][i+1] > df['High'][i+2] 
  cond4 = df['High'][i-1] > df['High'][i-2]
  return (cond1 and cond2 and cond3 and cond4)

def is_far_from_level(value, levels, df):
    ave =  np.mean(df['High'] - df['Low'])
    return np.sum([abs(value - level) < ave for _, level in levels]) == 0

class SupplyDemandPrice(BaseIndicator):
    def __init__(self, candlesticks = None, candlesticks_df = None) -> None:
        super().__init__(candlesticks, candlesticks_df)
        self.candlesticks_df.index = pd.DatetimeIndex(self.candlesticks_df['Date'])
        self.candlesticks_df['Date'] = self.candlesticks_df['Date'].apply(mpl_dates.date2num)
        self.supply_demand_levels = []

    def run(self):
        """
            Returns a list of tuples containing the index and value of the pivot points
        """
        pivots = []
        max_list = []
        min_list = []
        for i in range(5, len(self.candlesticks_df)-5):
            high_range = self.candlesticks_df['High'][i-5:i+4]
            current_max = high_range.max()

            if current_max not in max_list:
                max_list = []

            max_list.append(current_max)
            if len(max_list) == 5 and is_far_from_level(current_max, pivots, self.candlesticks_df):
                pivots.append((high_range.idxmax(), current_max))
            
            low_range = self.candlesticks_df['Low'][i-5:i+5]
            current_min = low_range.min()
            if current_min not in min_list:
                min_list = []
            min_list.append(current_min)
            if len(min_list) == 5 and is_far_from_level(current_min, pivots, self.candlesticks_df):
                pivots.append((low_range.idxmin(), current_min))
        self.supply_demand_levels = pivots

        return pivots

    def plot(self, output_path, timeframe = '1d'):
        width_candle_ohlc = 0.6 if timeframe == '1d' else 0.1

        fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
        candlestick_ohlc(ax, self.candlesticks_df.values, width=width_candle_ohlc, colorup='green', colordown='red', alpha=0.8)
        date_format = mpl_dates.DateFormatter('%d %b  %Y')
        ax.xaxis.set_major_formatter(date_format)
        for level in self.supply_demand_levels:
            plt.hlines(level[1], xmin=self.candlesticks_df['Date'][level[0]], xmax=max(self.candlesticks_df['Date']), colors='blue', linestyle='--')
        # fig.show()

        # Save fig
        plt.savefig(output_path)
    
