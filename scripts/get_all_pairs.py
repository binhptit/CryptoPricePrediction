import requests

query = {
}
response = requests.get("https://api.binance.com/api/v3/exchangeInfo", params=query)
result = response.json()

all_symbols = [x['symbol'] for x in result['symbols'] if x['symbol'].endswith('USDT')]
print(result.keys())


import pdb; pdb.set_trace()

