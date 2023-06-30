import sys
sys.path.append('/mnt/lustre/home/jason/sota_exp/CryptoPricePrediction/')
import os
import numpy as np
from datahub.dataset.crypto_dataloader import CryptoCurrencyPriceDataset
from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler


binance_crypto_data_crawler = BinanceCryptoDataCrawler()
binance_crypto_data_crawler.load_from_file(r'../dataset/btc_binance_crypto_price_data.json')

crypto_data = binance_crypto_data_crawler.crypto_data
binance_crypto_data_crawler.save_as_csv('../dataset/btc_binance_crypto_price_data_4h.csv', 'BTCUSDT', '4h')

import pdb; pdb.set_trace()
#  Date    Open    High     Low   Close    Volume  Adj Close