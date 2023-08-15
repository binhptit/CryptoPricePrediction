from .base import BaseIndicator
from typing import List
from ..candlestick import CandleStick
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from collections import deque

import yfinance as yf
import numpy as np
import math
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

def getHigherLows(data: np.array, order=5, K=2):
    '''
    Finds consecutive higher lows in price pattern.
    Must not be exceeded within the number of periods indicated by the width 
    parameter for the value to be confirmed.
    K determines how many consecutive lows need to be higher.
    '''
    # Get lows
    low_idx = argrelextrema(data, np.less, order=order)[0]
    lows = data[low_idx]
    # Ensure consecutive lows are higher than previous lows
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(low_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if lows[i] < lows[i-1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema

def getLowerHighs(data: np.array, order=5, K=2):
    '''
    Finds consecutive lower highs in price pattern.
    Must not be exceeded within the number of periods indicated by the width 
    parameter for the value to be confirmed.
    K determines how many consecutive highs need to be lower.
    '''
    # Get highs
    high_idx = argrelextrema(data, np.greater, order=order)[0]
    highs = data[high_idx]
    # Ensure consecutive highs are lower than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] > highs[i-1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema

def getHigherHighs(data: np.array, order=5, K=2):
    '''
    Finds consecutive higher highs in price pattern.
    Must not be exceeded within the number of periods indicated by the width 
    parameter for the value to be confirmed.
    K determines how many consecutive highs need to be higher.
    '''
    # Get highs
    high_idx = argrelextrema(data, np.greater, order=order)[0]
    highs = data[high_idx]
    # Ensure consecutive highs are higher than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] < highs[i-1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema

def getLowerLows(data: np.array, order=5, K=2):
    '''
    Finds consecutive lower lows in price pattern.
    Must not be exceeded within the number of periods indicated by the width 
    parameter for the value to be confirmed.
    K determines how many consecutive lows need to be lower.
    '''
    # Get lows
    low_idx = argrelextrema(data, np.less, order=order)[0]
    lows = data[low_idx]
    # Ensure consecutive lows are lower than previous lows
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(low_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if lows[i] > lows[i-1]:
            ex_deque.clear()    

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema

def getHHIndex(data: np.array, order=5, K=2):
    extrema = getHigherHighs(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx<len(data))]

def getLHIndex(data: np.array, order=5, K=2):
    extrema = getLowerHighs(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx<len(data))]

def getLLIndex(data: np.array, order=5, K=2):
    extrema = getLowerLows(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx<len(data))]

def getHLIndex(data: np.array, order=5, K=2):
    extrema = getHigherLows(data, order, K)
    idx = np.array([i[-1] + order for i in extrema])
    return idx[np.where(idx<len(data))]

def calcRSI(data, P=14):
  data['diff_close'] = data['Close'] - data['Close'].shift(1)
  data['gain'] = np.where(data['diff_close']>0, data['diff_close'], 0)
  data['loss'] = np.where(data['diff_close']<0, np.abs(data['diff_close']), 0)
  data[['init_avg_gain', 'init_avg_loss']] = data[
    ['gain', 'loss']].rolling(P).mean()
  avg_gain = np.zeros(len(data))
  avg_loss = np.zeros(len(data))
  for i, _row in enumerate(data.iterrows()):
    row = _row[1]
    if i < P - 1:
        last_row = row.copy()
        continue
    elif i == P-1:
        avg_gain[i] += row['init_avg_gain']
        avg_loss[i] += row['init_avg_loss']
    else:
        avg_gain[i] += ((P - 1) * avg_gain[i-1] + row['gain']) / P
        avg_loss[i] += ((P - 1) * avg_loss[i-1] + row['loss']) / P
            
    last_row = row.copy()
      
  data['avg_gain'] = avg_gain
  data['avg_loss'] = avg_loss
  data['RS'] = data['avg_gain'] / data['avg_loss']
  data['RSI'] = 100 - 100 / (1 + data['RS'])

  return data

class RsiDivergence(BaseIndicator):
    def __init__(self, candlesticks = None, candlesticks_df = None) -> None:
        super().__init__(candlesticks, candlesticks_df)
        self.candlesticks_df.index = pd.DatetimeIndex(self.candlesticks_df['Date'])
        self.supply_demand_levels = []

    def run(self):
        """
            Returns a list of tuples containing the index and value of the pivot points
        """
        data = self.candlesticks_df
        price = data['Close'].values

        data = calcRSI(data.copy())
        rsi = data['RSI'].values
        # Get higher highs, lower lows, etc.
        order = 5
        hh = getHigherHighs(price, order)
        lh = getLowerHighs(price, order)
        ll = getLowerLows(price, order)
        hl = getHigherLows(price, order)

        # Get index of lines
        result = []
        for line_deque in hh:
            line_lst = list(line_deque)
            left_idx = line_lst[0]
            right_idx = line_lst[-1]

            if rsi[left_idx] > rsi[right_idx]:
                result.append((left_idx, right_idx))
        
        for line_deque in lh:
            line_lst = list(line_deque)
            left_idx = line_lst[0]
            right_idx = line_lst[-1]

            if rsi[left_idx] < rsi[right_idx]:
                result.append((left_idx, right_idx))
        
        for line_deque in ll:
            line_lst = list(line_deque)
            left_idx = line_lst[0]
            right_idx = line_lst[-1]

            if rsi[left_idx] < rsi[right_idx]:
                result.append((left_idx, right_idx))
        
        for line_deque in hl:
            line_lst = list(line_deque)
            left_idx = line_lst[0]
            right_idx = line_lst[-1]

            if rsi[left_idx] > rsi[right_idx]:
                result.append((left_idx, right_idx))
        
        return result
                
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
    
