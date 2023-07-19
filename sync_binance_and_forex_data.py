from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from datahub.data_generator.forex_data_collector import ForexDataCollector

bcdc = BinanceCryptoDataCrawler()
bcdc.load_from_api("dataset/lastest_crypto_price_data.json")

# fdc = ForexDataCollector()

# import yfinance as yf
# data = yf.download("AAPL", interval="1h", start="2022-01-01", end="2023-07-16")

# import pdb; pdb.set_trace()