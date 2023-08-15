import sys
sys.path.append('.')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.signal import argrelextrema
from collections import deque

from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from utils.json_handler import dump_json, load_json
from datetime import datetime
import matplotlib.ticker as mticker
from trading.candlestick import CandleStick
from utils.utility import calculate_profit_and_loss

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

def get_yahoo_finance_data(ticker):
    start = '2011-01-01'
    end = '2011-07-31'
    yfObj = yf.Ticker(ticker)
    data = yfObj.history(start=start, end=end)
    # Drop unused columns
    data.drop(['Open', 'High', 'Low', 'Volume', 'Dividends', 
    'Stock Splits'], axis=1, inplace=True)

    return data

def btc_data():
    from trading.candlechart import CandleChart
    symbol = 'BTCUSDT'
    time_frame = '4h'

    start_date = datetime.strptime("06/08/2023", "%d/%m/%Y")
    end_date = datetime.strptime("11/08/2023", "%d/%m/%Y")

    binance_crypto_data_crawler = BinanceCryptoDataCrawler()
    crypto_data = binance_crypto_data_crawler.load_from_file(r'dataset/lastest_crypto_price_data.json')

    all_candlestick = []
    for i, candle_info in enumerate(crypto_data[symbol][time_frame]['data'][:]):
        try:
            candle_date = datetime.fromtimestamp(int(candle_info['open_time']) / 1000)
        except Exception as e:
            candle_date = datetime.fromtimestamp(int(candle_info[0]) / 1000)
        
        # Check if candlestick is in date range
        if candle_date < start_date or candle_date > end_date:
            continue

        candlestick = CandleStick()
        candlestick.load_candle_stick(candle_info)
    
        all_candlestick.append(candlestick)
    
    candle_chart = CandleChart(all_candlestick, None)
    candle_chart.candlesticks_df.index = pd.DatetimeIndex(candle_chart.candlesticks_df['Date'])
    return candle_chart.candlesticks_df   

ticker = 'XOM'
data = get_yahoo_finance_data(ticker)
data = btc_data()
from matplotlib.lines import Line2D # For legend
price = data['Close'].values
dates = data.index

# Get higher highs, lower lows, etc.
order = 3

data = calcRSI(data.copy())
rsi = data['RSI'].values
# Get values to mark RSI highs/lows and plot
rsi_hh = getHigherHighs(rsi, order)
rsi_lh = getLowerHighs(rsi, order)
rsi_ll = getLowerLows(rsi, order)
rsi_hl = getHigherLows(rsi, order)
# Get indices
rsi_hh_idx = getHHIndex(rsi, order)
rsi_lh_idx = getLHIndex(rsi, order)
rsi_ll_idx = getLLIndex(rsi, order)
rsi_hl_idx = getHLIndex(rsi, order)

from matplotlib.lines import Line2D # For legend
price = data['Close'].values
dates = data.index
# Get higher highs, lower lows, etc.
hh = getHigherHighs(price, order)
lh = getLowerHighs(price, order)
ll = getLowerLows(price, order)
hl = getHigherLows(price, order)
# Get confirmation indices
hh_idx = np.array([i[1] + order for i in hh])
lh_idx = np.array([i[1] + order for i in lh])
ll_idx = np.array([i[1] + order for i in ll])
hl_idx = np.array([i[1] + order for i in hl])

print(len(price))
print(hh)

for line_deque in hh:
    line_lst = list(line_deque)
    left_idx = line_lst[0]
    right_idx = line_lst[-1]

    if rsi[left_idx] > rsi[right_idx]:
        print("Found disvergence")
        print("RSI: ", rsi[left_idx], rsi[right_idx])
        print("Price: ", price[left_idx], price[right_idx])
        
# Plot results
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
plt.figure(figsize=(12, 8))
plt.plot(data['Close'])
# plt.scatter(dates[hh_idx], price[hh_idx-order], marker='^', c=colors[1])
# plt.scatter(dates[lh_idx], price[lh_idx-order], marker='v', c=colors[2])
# plt.scatter(dates[ll_idx], price[ll_idx-order], marker='v', c=colors[3])
# plt.scatter(dates[hl_idx], price[hl_idx-order], marker='^', c=colors[4])
_ = [plt.plot(dates[i], price[i], c=colors[1]) for i in hh]
_ = [plt.plot(dates[i], price[i], c=colors[2]) for i in lh]
_ = [plt.plot(dates[i], price[i], c=colors[3]) for i in ll]
_ = [plt.plot(dates[i], price[i], c=colors[4]) for i in hl]
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.title(f'Potential Divergence Points for {ticker} Closing Price')
legend_elements = [
  Line2D([0], [0], color=colors[0], label='Close'),
  Line2D([0], [0], color=colors[1], label='Higher Highs'),
  Line2D([0], [0], color='w',  marker='^',
         markersize=10,
         markerfacecolor=colors[1],
         label='Higher High Confirmation'),
  Line2D([0], [0], color=colors[2], label='Higher Lows'),
  Line2D([0], [0], color='w',  marker='^',
         markersize=10,
         markerfacecolor=colors[2],
         label='Higher Lows Confirmation'),
  Line2D([0], [0], color=colors[3], label='Lower Lows'),
  Line2D([0], [0], color='w',  marker='v',
         markersize=10,
         markerfacecolor=colors[3],
         label='Lower Lows Confirmation'),
  Line2D([0], [0], color=colors[4], label='Lower Highs'),
  Line2D([0], [0], color='w',  marker='^',
         markersize=10,
         markerfacecolor=colors[4],
         label='Lower Highs Confirmation')
]
# plt.legend(handles=legend_elements, bbox_to_anchor=(1, 0.65))
# plt.show()

fig, ax = plt.subplots(2, figsize=(20, 12), sharex=True)
ax[0].plot(data['Close'])
# ax[0].scatter(dates[hh_idx], price[hh_idx-order], 
#               marker='^', c=colors[1])
# ax[0].scatter(dates[lh_idx], price[lh_idx-order],
#               marker='v', c=colors[2])
# ax[0].scatter(dates[hl_idx], price[hl_idx-order],
#               marker='^', c=colors[3])
# ax[0].scatter(dates[ll_idx], price[ll_idx-order],
#               marker='v', c=colors[4])
_ = [ax[0].plot(dates[i], price[i], c=colors[1]) for i in hh]
_ = [ax[0].plot(dates[i], price[i], c=colors[2]) for i in lh]
_ = [ax[0].plot(dates[i], price[i], c=colors[3]) for i in hl]
_ = [ax[0].plot(dates[i], price[i], c=colors[4]) for i in ll]
ax[0].set_ylabel('Price ($)')
ax[0].set_title(f'Price and Potential Divergence Points for {ticker}')
ax[0].legend(handles=legend_elements)
ax[1].plot(data['RSI'])
# print(rsi_hh_idx)
# ax[1].scatter(dates[rsi_hh_idx], rsi[rsi_hh_idx-order], 
#               marker='^', c=colors[1])
# ax[1].scatter(dates[rsi_lh_idx], rsi[rsi_lh_idx-order],
#               marker='v', c=colors[2])
# ax[1].scatter(dates[rsi_hl_idx], rsi[rsi_hl_idx-order],
#               marker='^', c=colors[3])
# ax[1].scatter(dates[rsi_ll_idx], rsi[rsi_ll_idx-order],
#               marker='v', c=colors[4])
_ = [ax[1].plot(dates[i], rsi[i], c=colors[1]) for i in rsi_hh]
_ = [ax[1].plot(dates[i], rsi[i], c=colors[2]) for i in rsi_lh]
_ = [ax[1].plot(dates[i], rsi[i], c=colors[3]) for i in rsi_hl]
_ = [ax[1].plot(dates[i], rsi[i], c=colors[4]) for i in rsi_ll]
ax[1].set_ylabel('RSI')
ax[1].set_title(f'RSI and Potential Divergence Points for {ticker}')
ax[1].set_xlabel('Date')
plt.tight_layout()
plt.show()

