import os

import requests
from binance.client import Client
from sympy import symbols

# init
api_key = 'EisNmtJ21usfKa6mwvNfIkXNISLDeI0g4VexzNCPdR2SDsA8SycX8x6MhPuToxnV'
api_secret = 'vM5yQk8T8xbCoB4vGtwMD63dTF33xkorpW0s16tDybm8RQzQHGGoyop69MsHP2F6'

print(api_key)
print(api_secret)
client = Client(api_key, api_secret)

# client.API_URL = 'https://testnet.binance.vision/api'

# get balances for all assets & some account information
account_info = client.get_account()

symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT', 'SOLUSDT', 'DOTUSDT', 'DAIUSDT']
# get latest price from Binance API
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# print full output (dictionary)
print(btc_price)

timestamp = client._get_earliest_valid_timestamp('BTCUSDT', '1d')
print(timestamp)

# request historical candle (or klines) data
bars = client.get_historical_klines('ETHUSDT', '1d', timestamp, limit=500)


import pdb; pdb.set_trace()
