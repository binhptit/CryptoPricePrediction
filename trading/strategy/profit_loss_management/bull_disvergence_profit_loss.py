from .base_profit_loss import BaseProfitLoss

class BullDisvergenceProfitLoss(BaseProfitLoss):
    def __init__(self, candlesticks, candle_idx,):
        super().__init__()
        self.candlesticks = candlesticks
        self.candle_idx = candle_idx
    
    def run(self, ratio_retracement_for_entry=0.5, ratio_padding_loss=0.005, rr_ratio=1, k_previous_neighbours=3):
        """
        Runs the Disvergence pattern.

        Return:
            list[int]: index of the candlestick where the Disvergence pattern was found
        """
        candlestick = self.candlesticks[self.candle_idx]
        
        min_low = min([x.low for x in self.candlesticks[self.candle_idx - k_previous_neighbours:self.candle_idx]])
        min_low = min(min_low, candlestick.low)

        open_price = candlestick.open
        close_price = candlestick.close

        # open_price always > close_price
        dif_open_close = abs(open_price - close_price)
        dis_retracement = dif_open_close * ratio_retracement_for_entry

        entry_price = close_price + dis_retracement
        stop_loss_price = min_low - ratio_padding_loss * dif_open_close
        take_profit_price = entry_price + abs(entry_price - stop_loss_price) * rr_ratio

        return entry_price, stop_loss_price, take_profit_price