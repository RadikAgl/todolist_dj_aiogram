from tgbot.data_exchanger import request_new_access_token

FAILURE_MESSAGE = "Что-то пошло не так. Уже решаем проблему, попробуйте еще раз чуть позднее"


# Класс для хранения токенов пользователя
class UserTokens:

    def __init__(self):
        self.tokens = {}  # {user_id: {"access": "...", "refresh": "..."}}

    def set_tokens(self, user_id, access_token, refresh_token):
        self.tokens[user_id] = {
            "access": access_token,
            "refresh": refresh_token
        }

    def get_access_token(self, user_id):
        if user_id in self.tokens:
            return self.tokens[user_id]["access"]
        return None

    def get_refresh_token(self, user_id):
        if user_id in self.tokens:
            return self.tokens[user_id]["refresh"]
        return None

    async def refresh_access_token(self, user_id):
        refresh_token = self.get_refresh_token(user_id)
        if not refresh_token:
            return False

        response = await request_new_access_token(refresh_token)
        if response["status"] == 200:
            data = response["json"]
            self.tokens[user_id]["access"] = data["access"]
            if "refresh" in data:
                self.tokens[user_id]["refresh"] = data["refresh"]
            return True
        return False


user_tokens = UserTokens()
