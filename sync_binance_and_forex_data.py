from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from datahub.data_generator.forex_data_collector import ForexDataCollector

# bcdc = BinanceCryptoDataCrawler()
# bcdc.load_from_api("dataset/lastest_crypto_price_data.json")

fdc = ForexDataCollector()
fdc.load_from_api("dataset/lastest_forex_price_data.json")

# import yfinance as yf
# data = yf.download("GC=F", start="2022-01-01", end="2023-04-30",
#                    group_by="ticker", interval="30m")

# print(len(data))