import requests


query = {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "limit": 5,
    # "startTime": 1502755200000,
    # "endTime": 1502928000000,
}
response = requests.get("https://api.binance.com/api/v3/klines", params=query)

result = response.json()
print(response.json())

import pdb; pdb.set_trace()