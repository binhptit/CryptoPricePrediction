

class BaseGenerator:
    """An abstract base dataset operations"""

    def __init__(self, api_key: str = None, api_secret: str = None) -> None:
        self.api_key = api_key
        self.api_secret = api_secret

    def load_from_file(self, file_path: str):
        raise NotImplementedError

    def load_from_api(self):
        raise NotImplementedError

    def get_lastest_candle(
        self, symbol: str = "BTCUSDT", interval: str = "1d", limit: int = 5
    ):
        raise NotImplementedError

    def get_real_time_price(self, symbol: str = "BTCUSDT"):
        raise NotImplementedError
