

class BaseGenerator:
    """An abstract base dataset operations"""

    def __init__(self, api_key: str = None, api_secret: str = None) -> None:
        if api_key is None:
            self.api_key = 'EisNmtJ21usfKa6mwvNfIkXNISLDeI0g4VexzNCPdR2SDsA8SycX8x6MhPuToxnV'
        else:
            self.api_key = api_key

        if api_secret is None:
            self.api_secret = 'vM5yQk8T8xbCoB4vGtwMD63dTF33xkorpW0s16tDybm8RQzQHGGoyop69MsHP2F6'
        else:
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
