from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
from utils.json_handler import dump_json, load_json

if __name__ == '__main__':
    api_key = 'EisNmtJ21usfKa6mwvNfIkXNISLDeI0g4VexzNCPdR2SDsA8SycX8x6MhPuToxnV'
    api_secret = 'vM5yQk8T8xbCoB4vGtwMD63dTF33xkorpW0s16tDybm8RQzQHGGoyop69MsHP2F6'

    output_path = r'dataset/binance_crypto_price_data.json'
    binance_dataset = BinanceCryptoDataCrawler(api_key, api_secret)
    crypto_data = binance_dataset.load_from_api(output_path)
    # crypto_data = binance_dataset.load_from_file(output_path)


    import pdb; pdb.set_trace()