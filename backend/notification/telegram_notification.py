from abc import ABC, abstractmethod
import config
import requests

class TelegramNotification:
    def __init__(self, dev=False) -> None:
        super().__init__()
        self.telegram_bot_token = config.dev_telegram_bot_token if dev else config.telegram_bot_token
        self.chat_id = config.dev_chat_id if dev else config.chat_id
        
        # Construct the API URL
        self.url = f'https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage'

    def send(self, message: str):
        # Set the request parameters
        params = {
            'chat_id': self.chat_id,
            'text': message
        }

        # Send the POST request
        response = requests.post(self.url, params=params)

        # Check the response status
        return response.status_code == 200