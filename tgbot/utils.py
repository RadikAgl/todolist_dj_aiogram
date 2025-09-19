import os

from tgbot.data_exchanger import request_new_access_token
from dotenv import load_dotenv

load_dotenv(os.path.join(".", ".env"))

PASSWORD = os.getenv('BOT_PASSWORD')
USERNAME = os.getenv('BOT_USERNAME')

FAILURE_MESSAGE = "Что-то пошло не так. Уже решаем проблему, попробуйте еще раз чуть позднее"


class APIClient:

    def __init__(self, username, password):
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.password = password

    def set_tokens(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_access_token(self):
        return self.access_token

    def get_refresh_token(self):
        return self.access_token

    async def refresh_access_token(self):
        refresh_token = self.get_refresh_token()
        if not refresh_token:
            return False

        response = await request_new_access_token(refresh_token)
        if response["status"] == 200:
            data = response["json"]
            self.access_token = data["access"]
            if "refresh" in data:
                self.access_token = data["refresh"]
            return True
        return False


api_client = APIClient(USERNAME, PASSWORD)
