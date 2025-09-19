from aiogram.types import CallbackQuery

from tgbot.data_exchanger import verify_access_token, auth_user
from tgbot.utils import api_client, FAILURE_MESSAGE


# Middleware для проверки авторизации
class AuthMiddleware:
    async def __call__(self, handler, event, data):

        access_token = api_client.get_access_token()

        response = await verify_access_token(access_token)

        if response["status"] != 200:
            if await api_client.refresh_access_token():
                access_token = api_client.get_access_token()
                response = await verify_access_token(access_token)
                if response["status"] != 200:
                    response = await auth_user(api_client.username, api_client.password)
            else:
                response = await auth_user(api_client.username, api_client.password)
            if response["status"] != 200:
                await event.answer(FAILURE_MESSAGE)
                return
            else:
                api_client.set_tokens(response["json"]["access"], response["json"]["refresh"])

        data["headers"] = {"Authorization": f"Bearer {api_client.get_access_token()}"}
        return await handler(event, data)


