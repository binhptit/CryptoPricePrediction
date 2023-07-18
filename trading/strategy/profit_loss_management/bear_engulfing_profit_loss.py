from .base_profit_loss import BaseProfitLoss

class BearEngulfingProfitLoss(BaseProfitLoss):
    def __init__(self, candlesticks, candle_idx,):
        super().__init__()
        self.candlesticks = candlesticks
        self.candle_idx = candle_idx
    
    def run(self, ratio_retracement_for_entry=0.0001, ratio_padding_loss=0, rr_ratio=1):
        """
        Runs the engulfing pattern.

        Return:
            list[int]: index of the candlestick where the engulfing pattern was found
        """
        candlestick = self.candlesticks[self.candle_idx]
        previous_candlestick = self.candlesticks[self.candle_idx - 1]
        
        previous_open_price = previous_candlestick.open
        previous_close_price = previous_candlestick.close

        open_price = candlestick.open
        close_price = candlestick.close
        low_price = candlestick.low
        high_price = candlestick.high

        dif_open_close = abs(open_price - close_price)
        dis_retracement = dif_open_close * ratio_retracement_for_entry

        entry_price = close_price + dis_retracement
        stop_loss_price = high_price + ratio_padding_loss * dif_open_close
        take_profit_price = entry_price - abs(entry_price - stop_loss_price) * rr_ratio

        return entry_price, stop_loss_price, take_profit_price