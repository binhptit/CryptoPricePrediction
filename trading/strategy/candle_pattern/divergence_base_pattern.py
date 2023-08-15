import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from collections import deque

import numpy as np
from trading.candlechart import CandleChart
from trading.candlestick import CandleStick
from .base_pattern import BasePattern
from typing import List

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

class RsiDivergence(BasePattern):
    def __init__(self, candlesticks: List[CandleStick], divergence_type="hh"):
        super().__init__(candlesticks)
        candle_chart = CandleChart(candlesticks)
        self.candlesticks = candle_chart.candlesticks
        self.candlesticks_df = candle_chart.candlesticks_df
        self.divergence_type = divergence_type

        self.data = self.candlesticks_df
        self.rsi_data = calcRSI(self.data.copy())
        
    
    def run_divergence_detect(self):
        """
            Finds the doji star pattern.

            Return:
                list[int]: index of the candlestick where the doji star was found
        """
        price = self.data['Close'].values
        rsi = self.rsi_data['RSI'].values

        potential_divergence = []
        orders = [3, 5]
        if self.divergence_type == "hh":
            for order in orders:
                hh = getHigherHighs(price, order)

                for line_deque in hh:
                    line_lst = list(line_deque)
                    left_idx = line_lst[0]
                    right_idx = line_lst[-1]

                    if rsi[left_idx] >= rsi[right_idx]:
                        potential_divergence.append((left_idx, right_idx))
        elif self.divergence_type == "lh":
            for order in orders:
                lh = getLowerHighs(price, order)

                for line_deque in lh:
                    line_lst = list(line_deque)
                    left_idx = line_lst[0]
                    right_idx = line_lst[-1]

                    if rsi[left_idx] <= rsi[right_idx]:
                        potential_divergence.append((left_idx, right_idx))
        elif self.divergence_type == "ll":
            for order in orders:
                ll = getLowerLows(price, order)

                for line_deque in ll:
                    line_lst = list(line_deque)
                    left_idx = line_lst[0]
                    right_idx = line_lst[-1]

                    if rsi[left_idx] <= rsi[right_idx]:
                        potential_divergence.append((left_idx, right_idx))
        elif self.divergence_type == "hl":
            for order in orders:
                hl = getHigherLows(price, order)

                for line_deque in hl:
                    line_lst = list(line_deque)
                    left_idx = line_lst[0]
                    right_idx = line_lst[-1]

                    if rsi[left_idx] >= rsi[right_idx]:
                        potential_divergence.append((left_idx, right_idx))

        # check if there is a divergence in 01/06/2023 or 31/05/2023
        # for line_idx in potential_divergence:
        #     left_idx, right_idx = line_idx

        #     print(self.data.iloc[left_idx]['Date'], self.data.iloc[right_idx]['Date'], self.divergence_type)
        return potential_divergence

    def run(self):
        pass

    def __repr__(self) -> str:
        return "Divergence base pattern"