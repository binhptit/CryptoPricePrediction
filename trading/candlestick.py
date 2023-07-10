from datetime import datetime

class CandleStick:
    def __init__(self, open = 0, high = 0, low = 0, close = 0, volume = 0, open_time = 0, close_time = 0, date = None):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.open_time = open_time
        self.close_time = close_time
        self.date = date
        self.type = 'normal'
        self.eps = 0.0000001
    
    def get_candle_type(self, open_price, high_price, low_price, close_price):
        candle_type = 'normal'

        gap_top = high_price - max(open_price, close_price) + self.eps
        gap_down = min(open_price, close_price) - low_price + + self.eps

        if (abs(open_price - close_price) / gap_top <= 0.5 and gap_down / gap_top < 0.2):
            candle_type = 'shooting_star'
        elif (abs(open_price - close_price) / gap_down <= 0.5 and gap_top / gap_down < 0.2):
            candle_type = 'hammer'
        elif abs(open_price - close_price) / (high_price - low_price +  0.0001) >= 0.9:
            if open_price < close_price:
                candle_type = 'bull_mazubuzu'
            elif open_price > close_price:
                candle_type = 'bear_mazubuzu'
        
        return candle_type
            
    def load_candle_stick(self, candle_info):
        if 'open' not in candle_info:
            self.open = float(candle_info[1])
            self.high = float(candle_info[2])
            self.low = float(candle_info[3])
            self.close = float(candle_info[4])
            self.volume = float(candle_info[5])
            self.open_time = int(candle_info[0]) / 1000
            self.close_time = int(candle_info[6]) / 1000
            self.date = datetime.fromtimestamp(int(candle_info[0]) / 1000)
        else:
            self.open = candle_info['open']
            self.high = candle_info['high']
            self.low = candle_info['low']
            self.close =candle_info['close']
            self.volume = candle_info['volume']
            self.open_time = int(candle_info['open_time']) / 1000
            self.close_time = int(candle_info['close_time']) / 1000
            self.date = datetime.fromtimestamp(int(candle_info['open_time']) / 1000)

        try:
            self.type = self.get_candle_type(self.open, self.high, self.low, self.close)
        except Exception as e:
            print(e, self.open, self.high, self.low, self.close)
