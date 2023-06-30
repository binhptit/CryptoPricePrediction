
class CandleStick:
    def __init__(self):
        self.open = 0
        self.high = 0
        self.low = 0
        self.close =0
        self.volume = 0
        self.timestamp = 0
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
        elif abs(open_price - close_price) / (high_price - low_price) >= 0.9:
            if open_price < close_price:
                candle_type = 'bull_mazubuzu'
            elif open_price > close_price:
                candle_type = 'bear_mazubuzu'
        
        return candle_type
            
    def load_candle_stick(self, candle_info):
        self.open = candle_info['open']
        self.high = candle_info['high']
        self.low = candle_info['low']
        self.close =candle_info['close']
        self.volume = candle_info['volume']
        self.timestamp = candle_info['open_time']

        try:
            self.type = self.get_candle_type(self.open, self.high, self.low, self.close)
        except Exception as e:
            print(e, self.open, self.high, self.low, self.close)
