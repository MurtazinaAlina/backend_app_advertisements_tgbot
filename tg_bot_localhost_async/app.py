"""
Добавление телеграм-бота к приложению
# test_dj_tg_336699_bot

* Немного нестандартный путь к базе sqlite, т.к. иначе создается дубль базы в папке бота, а нам нужно, чтобы работы
была с существующей базой джанго.

Бот:
- видит данные существующей базы django
- отображает данные из БД, фильтрует, создает новые записи, удаляет
- авторизация по логину и паролю с записью токена в middleware message &callback_query и атрибутом бота (так проще в
тех обработчиках, где не нужен пользователь, а просто логика, например, отображать или нет инлайны и т.п.)
- logout (становятся недоступны инлайны, доступно базовое меню. Данные в мидлвейр остаются)
- пароль удаляется из чата после ввода при авторизации
- поиск по фильтру - кнопкой (по названию и описанию) - через запрос - состояние
- реализована некоторая валидация данных при создании/редактировании объявления
- реализована пагинация вывода объявлений для удобства просмотра

- 2 базовые команды:
    - start - для начала работы
    - cancel - бля сброса ввода данных и возврата в пользовательское меню. Доступно также по вводу слова "отмена" в чат

- для неавторизованного:
    - просмотр всех объявлений, поиск объявлений, авторизация

- для авторизованного:
    - отображаются инлайновые кнопки действий (изменить/удалить) на объявлениях
    - удаление из избранного по инлайн-кнопке
    - удаление своего объявления по инлайн-кнопке в моих, черновиках
    - просмотр всех объявлений с инлайн-опцией добавить в избранное
    - просмотр объявлений поиска с инлайн-опцией добавить в избранное
    - "черновики" - просмотр своих черновиков
    - "избранное" - просмотр своего избранного
    - "мои объявления" - просмотр своих во всех статусах
    - создание нового объявления, добавляется в базу
    - редактирование объявлений по кнопке в инлайне

Данные для тестирования:
user2 Qw123456!
admin admin
"""

import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "advs.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # джанго объекты внутри async
import django  # noqa

django.setup()

from tg_bot_localhost_async.models_alchemy import create_db, session_maker  # noqa
from tg_bot_localhost_async.middlewares import DataBaseSession  # noqa
from tg_bot_localhost_async.handlers import router  # noqa

import asyncio  # noqa

from aiogram import Bot, Dispatcher  # noqa
from aiogram.enums import ParseMode  # noqa
from aiogram.types import BotCommand  # noqa


bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
bot.is_authenticated = None

dp = Dispatcher()
dp.include_router(router)

commands_list = [
    BotCommand(command="start", description="начать работу"),
    BotCommand(command="cancel", description="отменить ввод данных и вернуться к меню"),
]


async def main():
    """
    Запуск бота
    """
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=commands_list)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
