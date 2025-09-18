from aiogram.types import CallbackQuery

from tgbot.data_exchanger import verify_access_token, auth_user
from tgbot.utils import user_tokens, FAILURE_MESSAGE


# Middleware для проверки авторизации
class AuthMiddleware:
    async def __call__(self, handler, event, data):
        init_event = event
        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            event = event.message
        else:
            user_id = event.from_user.id

        if event.text.startswith('/start'):
            return await handler(event, data)

        access_token = user_tokens.get_access_token(user_id)

        if not access_token:
            await event.answer("Вы не авторизованы. Используйте /start для авторизации.")
            return

        response = await verify_access_token(access_token)

        if response["status"] == 401:
            if await user_tokens.refresh_access_token(user_id):
                access_token = user_tokens.get_access_token(user_id)
                response = await verify_access_token(access_token)
                if response["status"] != 200:
                    response = await auth_user(user_id)
            else:
                response = await auth_user(user_id)
            if response["status"] != 200:
                await event.answer(FAILURE_MESSAGE)
                return
            else:
                user_tokens.set_tokens(user_id, response["json"]["access"], response["json"]["refresh"])
        elif response["status"] != 200:
            await event.answer(FAILURE_MESSAGE)
            return
        data["headers"] = {"Authorization": f"Bearer {user_tokens.get_access_token(user_id)}"}
        return await handler(init_event, data)


