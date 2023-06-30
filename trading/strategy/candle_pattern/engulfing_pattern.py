from .base_pattern import BasePattern

class EngulfingPattern(BasePattern):
    """
    Class for an engulfing pattern.
    """

    def __init__(self, candlesticks: List[CandleStick]):
        """
        Initializes the engulfing pattern.
        """
        super().__init__(candlesticks)
        self.candlesticks = candlesticks

    def run(self):
        """
        Runs the engulfing pattern.

        Return:
            list[int]: index of the candlestick where the engulfing pattern was found
        """
        previous_candlestick = None
        found_positions = []

        for candlestick in self.candlesticks:
            if previous_candlestick is None:
                previous_candlestick = candlestick
                continue
            
            previous_open_price = previous_candlestick.open
            previous_close_price = previous_candlestick.close
            previous_high_price = previous_candlestick.high
            previous_low_price = previous_candlestick.low

            open_price = candlestick.open
            close_price = candlestick.close
            high_price = candlestick.high
            low_price = candlestick.low

            if previous_close_price < previous_open_price and close_price > open_price and close_price > previous_high_price and open_price < previous_low_price:
                found_positions.append(self.candlesticks.index(candlestick))

            previous_candlestick = candlestick

        return found_positions

if __name__ == '__main__':
    from trading.candlestick import CandleStick
    from datahub.data_generator.crypto_currency_crawler import BinanceCryptoDataCrawler
    from matplotlib.pyplot import title
    import requests
    import json
    import os
    import pandas as pd
    import mplfinance as mpl

    candle_types = [
        # 'shooting_star', 
        'hammer', 
        # 'bull_mazubuzu', 'bear_mazubuzu'
    ]

    binance_crypto_data_crawler = BinanceCryptoDataCrawler()
    crypto_data = binance_crypto_data_crawler.load_from_file(r'dataset/btc_binance_crypto_price_data.json')

    candle_data = {
        }
    for ct in candle_types:
        candle_data[ct] = {"Date": [],"Open": [], "High": [], "Low":[], "Close": []}

    print(len(crypto_data['BTCUSDT']['4h']['data']))

    # number_winning_candlestick = 0
    # total_candlestick = 0
    # for i, candle_info in enumerate(crypto_data['BTCUSDT']['4h']['data'][:]):
    #     candlestick = CandleStick()
    #     candlestick.load_candle_stick(candle_info)
            
            