import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=5min&apikey=PSLIB6TXBS1CMLPA'
r = requests.get(url)
data = r.json()

print(data['Information'])


# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=PSLIB6TXBS1CMLPA'
r = requests.get(url)
data = r.json()

print(len(data['Time Series (5min)']))

# import pdb; pdb.set_trace()

