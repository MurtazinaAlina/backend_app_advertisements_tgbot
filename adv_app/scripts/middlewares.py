from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


class DataBaseSession(BaseMiddleware):  # ППО для подключения к БД в который передаем сессион мэйкер
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(
                event, data
            )  # теперь в КАЖДОМ хэндлере в параметре 'session' будет доступна асинхронная сессия с БД


class AuthSession(BaseMiddleware):
    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        data["auth_token"] = self.auth_token  # в auth_token доступен токен
        return await handler(event, data)
