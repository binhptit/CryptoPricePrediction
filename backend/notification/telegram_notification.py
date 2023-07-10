from abc import ABC, abstractmethod
import config
import requests

class TelegramNotification:
    def __init__(self) -> None:
        super().__init__()
        # Construct the API URL
        self.url = f'https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage'

    def send(self, message: str):
        # Set the request parameters
        params = {
            'chat_id': config.chat_id,
            'text': message
        }

        # Send the POST request
        response = requests.post(self.url, params=params)

        # Check the response status
        return response.status_code == 200