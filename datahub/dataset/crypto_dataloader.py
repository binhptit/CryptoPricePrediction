import sys 
sys.path.append('D:\Coding\CryptoWorkPlace')

import os
import torch
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils



# Ignore warnings
import warnings
warnings.filterwarnings("ignore")


class CryptoCurrencyPriceDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, binance_crypto_crawler, timeframe='1h', mode='train', window_len = 128, slide_len = 1):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.binance_crypto_datahub = binance_crypto_crawler
        self.crypto_data = self.binance_crypto_datahub.crypto_data

        self.crypto_data_by_timeframe = []

        self.window_len = window_len
        self.slide_len = slide_len
        self.mode = mode

        self.X = dict()
        self.Y = dict()

        self.X['train'] = []
        self.Y['train'] = []

        self.X['val'] = []
        self.Y['val'] = []

        self.X['test'] = []
        self.Y['test'] = []

        self.timeframes = ['1h', '4h', '1d']

        self.__init_candle_data_all_timeframe()

        for m in ['train', 'val', 'test']:
            self.X[m] = torch.FloatTensor(np.array(self.X[m]))
            self.Y[m] = torch.FloatTensor(np.array(self.Y[m]))

    # convert an array of values into a dataset matrix
    def split_sequence_into_data(self, sequence, look_back=1):
        dataX, dataY = [], []
        for i in range(len(sequence)-look_back-1):
            a = sequence[i:(i+look_back)]
            dataX.append(a)
            dataY.append(sequence[i + look_back][0:4])

        return dataX, dataY
    
    def split_train_val_test(self, X, Y, train_ratio = 0.8, val_ratio = 0.1, test_ratio = 0.1):
        len_sample = len(X)

        len_train = int(len_sample * train_ratio)
        len_val = int(len_sample * val_ratio)
        len_test = int(len_sample * test_ratio)

        self.X['train'] += X[:len_train]
        self.Y['train'] += Y[:len_train]

        self.X['val'] += X[len_train:len_train + len_val]
        self.Y['val'] += Y[len_train:len_train + len_val]

        self.X['test'] += X[len_train + len_val:]
        self.Y['test'] += Y[len_train + len_val:]

    def normalize_min_max(self, value, minv, maxv, mode='max'):
        if mode == 'max':
            return value * 1.0 / maxv
        
        return (value - minv) * 1.0 / (maxv - minv)

    def __init_candle_data_all_timeframe(self):
        for symbol, timeframe_data in self.crypto_data.items():
            for timeframe in self.timeframes:
                preprocess_timeframe_data = []
                full_data = timeframe_data[timeframe]['data']
                attr = timeframe_data[timeframe]['attributes']

                max_price = attr['max_price']
                min_price = attr['min_price'] 
                max_volume = attr['max_volume']
                min_volume = attr['min_volume']
                max_number_of_trades = attr['max_number_of_trades']
                min_number_of_trades = attr['min_number_of_trades']

                for candle_info in full_data:
                    open_price = candle_info['open']
                    high = candle_info['high']
                    low = candle_info['low']
                    close =candle_info['close']
                    volume = candle_info['volume']

                    preprocess_timeframe_data.append([
                        self.normalize_min_max(open_price, min_price, max_price),
                        self.normalize_min_max(high, min_price, max_price),
                        self.normalize_min_max(low, min_price, max_price),
                        self.normalize_min_max(close, min_price, max_price),
                        self.normalize_min_max(volume, min_volume, max_volume),
                        (self.timeframes.index(timeframe) + 1.0) / len(self.timeframes)
                    ])

                all_X, all_Y = self.split_sequence_into_data(preprocess_timeframe_data, self.window_len)
                self.split_train_val_test(all_X, all_Y)


    def __len__(self):
        return len(self.X[self.mode])   

    def __getitem__(self, idx):
        return self.X[self.mode][idx], self.Y[self.mode][idx]


# if __name__ == '__main__':
#     cd = CryptoCurrencyPriceDataset()
#     print(cd.__getitem__(0))
#     import pdb; pdb.set_trace()