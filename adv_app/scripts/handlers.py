from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram import F, types, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.authtoken.models import Token

from sqlalchemy.ext.asyncio import AsyncSession

from adv_app.models import Advertisement, Favourites
from .keyboards import get_keyboard, get_callback_btns
from .middlewares import AuthSession


router = Router()

# варианты меню
START_KB = [
    "Все объявления",
    "🔎 Поиск объявлений",
    "📲 Авторизация",
]
START_KB_PLACEHOLDER = "Выберите действие"
START_KB_SIZES = (2, 1)

START_AUTH_KB = [
    "Все oбъявления",  # o - латиница! для варианта настройка ветвления с авторизацией/без
    "🔎 Поиск объявлений",
    "📌 Мои объявления",
    "📝 Черновики",
    "➕ Новое объявление",
    "⭐ Избранное",
    "📴 Выйти из аккаунта",
]
START_AUTH_PLACEHOLDER = "Выберите действие"
START_AUTH_SIZES = (2, 2, 2)

# статусы заявок для inline-кнопок
STATE_BTNS = {'OPEN': 'state_open', 'CLOSED': 'state_closed', 'DRAFT': 'state_draft'}


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    """
    Команда /start
    """
    await message.answer(
        "Выберите действие в меню",
        reply_markup=get_keyboard(
            *START_KB, placeholder=START_KB_PLACEHOLDER, sizes=START_KB_SIZES
        ),
    )


# noinspection PyUnusedLocal
@router.message(
    F.text == "Все oбъявления"
)  # версия авторизованного пользователя (есть опция добавить в избранное)
async def get_cmd(message: types.Message, session: AsyncSession, auth_token: str):
    """
    Вывести информацию по всем OPEN объявлениям
    """
    # info = await orm_get_all_open_advertisements(session)
    info = Advertisement.objects.filter(status="OPEN")

    await message.answer(f"Все объявления: {len(info)}")
    for adv in info:
        await message.answer(
            f"<b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}",
            reply_markup=get_callback_btns(btns={"Добавить в избранное": f"add-fvr_{adv.id}"}),
        )


@router.message(F.text == "Все объявления")
async def get_cmd_unauth(message: types.Message, session: AsyncSession):
    """
    Вывести информацию по всем OPEN объявлениям.
    Версия неавторизованного пользователя (нет опции добавить в избранное)
    """
    # info = await orm_get_all_open_advertisements(session)
    # попробуем такое, раз не пашет асинхрон в раскладе runscript'а
    info = Advertisement.objects.filter(status="OPEN")

    await message.answer(f"Все объявления: {len(info)}")
    for adv in info:
        await message.answer(
            f"<b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}"
        )


# noinspection PyUnresolvedReferences
@router.message(F.text == "📌 Мои объявления")
async def get_my_advs(message: types.Message, session: AsyncSession, auth_token: str):
    """
    Вывести все объявления авторизованного пользователя (все статусы)
    """
    user_id = Token.objects.get(key=auth_token).user.id
    # info = await orm_get_user_advertisements(session, user_id)
    info = Advertisement.objects.filter(creator_id=user_id)

    await message.answer(f"Мои объявления: {len(info)}")
    for adv in info:
        await message.answer(
            f"📌 <b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}",
            reply_markup=get_callback_btns(
                btns={
                    "Изменить": f"update-adv_{adv.id}_{auth_token}",
                    "Удалить": f"delete-adv_{adv.id}_{auth_token}",
                }
            ),
        )


# noinspection PyUnresolvedReferences
@router.message(F.text == "📝 Черновики")
async def get_my_drafts(message: types.Message, session: AsyncSession, auth_token: str):
    """
    Вывести все черновики авторизованного пользователя
    """
    user_id = Token.objects.get(key=auth_token).user.id
    # info = await orm_get_user_drafts(session, user_id)
    info = Advertisement.objects.filter(creator_id=user_id, status="DRAFT")

    await message.answer(f"Черновики: {len(info)}")
    for adv in info:
        await message.answer(
            f"📝 <b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}",
            reply_markup=get_callback_btns(
                btns={
                    "Изменить": f"update-adv_{adv.id}_{auth_token}",
                    "Удалить": f"delete-adv_{adv.id}_{auth_token}",
                }
            ),
        )


@router.message(F.text == "⭐ Избранное")
async def get_my_favourites(message: types.Message, session: AsyncSession, auth_token: str):
    """
    Вывести все объявления, находящиеся у пользователя в избранном
    """
    usr = User.objects.filter(auth_token__key=auth_token).first()
    # fvs = usr.favourites.all()
    # info = await orm_get_user_favourites(session, fvs)
    info = usr.favourites.all()

    await message.answer(f"Мое избранное: {len(info)}")
    # for adv in info:
    #     await message.answer(f'⭐ <b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}',
    #                          reply_markup=get_callback_btns(
    #                              btns={'Убрать из избранного': f'rm-fvr_{adv.id}_{auth_token}'}))
    for adv in info:
        await message.answer(
            f"⭐ <b>{adv.advertisement.title}:</b>\n{adv.advertisement.description}\n<i>"
            f"{adv.advertisement.status}</i>\nuser: {adv.advertisement.creator_id}",
            reply_markup=get_callback_btns(
                btns={"Убрать из избранного": f"rm-fvr_{adv.advertisement.id}_{auth_token}"}
            ),
        )


@router.message(F.text == "📴 Выйти из аккаунта")
async def start_menu(message: types.Message, bot: Bot):
    """
    Возврат в стартовое меню с показом всех объявлений и фильтром без инлайн-кнопок
    """
    await message.answer(
        "Вы вышли из аккаунта",
        reply_markup=get_keyboard(
            *START_KB, placeholder=START_KB_PLACEHOLDER, sizes=START_KB_SIZES
        ),
    )
    bot.is_authenticated = None


""" ------------------------ простые CallbackQuery события ------------------------------"""


# noinspection PyUnresolvedReferences
@router.callback_query(F.data.startswith("delete-adv_"))
async def delete_adv(callback: types.CallbackQuery, session: AsyncSession):
    """
    Удалить свое объявление по инлайн-кнопке
    """
    id_for_delete = int(callback.data.split("_")[1])
    auth_token = callback.data.split("_")[2]
    user_id = Token.objects.filter(key=auth_token).first().user.id

    try:
        # await orm_delete_advertisement(session, id_for_delete, user_id)
        del_ = Advertisement.objects.filter(creator_id=user_id, id=id_for_delete).delete()[0]
        if del_:
            await callback.answer("Удалено", show_alert=True)
            await callback.message.answer(f"Вы удалили свое объявление id {id_for_delete}")
        else:
            await callback.message.answer(f"Произошла ошибка.\nДействие не удалось")
    except (Exception,) as e:
        await callback.message.answer(f"Произошла ошибка: {e}.\nДействие не удалось")


# noinspection PyUnresolvedReferences
@router.callback_query(F.data.startswith("rm-fvr_"))
async def delete_from_fvs(callback: types.CallbackQuery, session: AsyncSession):
    """
    Удалить объявление из своего Избранного по инлайн-кнопке
    """
    id_for_delete = int(callback.data.split("_")[1])
    auth_token = callback.data.split("_")[2]
    user_id = Token.objects.filter(key=auth_token).first().user.id

    try:
        # await orm_delete_from_favourites(session, id_for_delete, user_id)
        del_ = Favourites.objects.filter(user_id=user_id, advertisement_id=id_for_delete).delete()[
            0
        ]
        if del_:
            await callback.answer("Удалено", show_alert=True)
            await callback.message.answer("Объявление удалено из избранного")
        else:
            await callback.message.answer(f"Произошла ошибка.\nДействие не удалось")
    except (Exception,) as e:
        await callback.message.answer(f"Произошла ошибка: {e}.\nДействие не удалось")


# noinspection PyUnresolvedReferences
@router.callback_query(F.data.startswith("add-fvr_"))
async def add_to_fvs(callback: types.CallbackQuery, auth_token: str):
    """
    Добавить объявление в свое Избранное по инлайн-кнопке
    """
    id_for_add = int(callback.data.split("_")[-1])
    usr_id = Token.objects.get(key=auth_token).user.id
    adv = Advertisement.objects.filter(id=id_for_add).first()

    if adv.creator.id == usr_id:
        await callback.message.answer(
            "Нельзя добавить в избранное собственное объявление",
            reply_markup=get_keyboard(
                *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
            ),
        )
    else:
        try:
            # чтобы не дублировать готовые ограничения на создание записи
            Favourites.objects.create(advertisement_id=id_for_add, user_id=usr_id)
            await callback.message.answer(
                "Объявление добавлено в избранное",
                reply_markup=get_keyboard(
                    *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
                ),
            )
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                msg = "Объявление уже есть в Избранном"
            else:
                msg = f"произошла ошибка: {e}"
            await callback.message.answer(
                msg,
                reply_markup=get_keyboard(
                    *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
                ),
            )


""" ------------------------ Блок FSM ------------------------------"""


class AddAdv(StatesGroup):
    """
    Для ввода данных добавления/изменения объявления
    """

    title = State()
    description = State()
    status = State()

    adv_object = None  # для работы с update

    texts = {  # для вывода по действию шаг назад
        "AddAdv:title": "Введите заголовок объявления заново",
        "AddAdv:description": "Введите описание объявления заново",
        "AddAdv:status": "Вы на последнем шаге",
    }


class AddLogIn(StatesGroup):
    """
    Для ввода данных авторизации
    """

    login = State()
    password = State()


class AddSearch(StatesGroup):
    """
    Для ввода ключа поиска по объявлениям
    """

    search = State()


# noinspection PyUnresolvedReferences
@router.message(StateFilter("*"), or_f((F.text.casefold() == "отмена"), (Command("cancel"))))
async def cancel_handler(message: types.Message, state: FSMContext, bot: Bot) -> None:
    """
    Отмена диалога и полный сброс состояния пользователя
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    if bot.is_authenticated:
        await message.answer(
            "Действия отменены",
            reply_markup=get_keyboard(
                *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
            ),
        )
    else:
        await message.answer(
            "Действия отменены",
            reply_markup=get_keyboard(
                *START_KB, placeholder=START_KB_PLACEHOLDER, sizes=START_KB_SIZES
            ),
        )


@router.message(StateFilter("*"), F.text.casefold() == "назад")
async def step_back_add_adv(message: types.Message, state: FSMContext):
    """
    Возврат к предыдущему шагу состояния при создании/изменении объявления
    """
    current_state = await state.get_state()

    # если это первый шаг
    if current_state == AddAdv.title:
        await message.answer(
            'Предыдущего шага нет, введите название объявления или напишите "отмена"'
        )
        return

    previous = None
    for step in AddAdv.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"<b>Вы вернулись к предыдущему шагу</b>.\n{AddAdv.texts[previous.state]}"
            )
            return
        previous = step


@router.message(StateFilter(None), F.text == "🔎 Поиск объявлений")
async def search_advs_start(message: types.Message, state: FSMContext):
    """
    ПОИСК, шаг 1.
    Вход в ожидание поискового запроса
    """
    await message.answer(
        f"<b>Введите ключевое слово/фразу для начала поиска.</b>\nСистема будет искать по совпадению "
        f"в названии или описании объявления",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(AddSearch.search)


# noinspection PyUnresolvedReferences
@router.message(AddSearch.search, F.text)
async def search_advs_result(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    """
    ПОИСК, шаг 2.
    Находит все объявления, в названии или описании которых встречается поисковое слово/фраза и
    находящиеся в статусе 'OPEN'
    """
    await state.update_data(search_param=message.text)
    data = await state.get_data()
    # info = await orm_search_in_advertisements(session, data)
    info = Advertisement.objects.filter(status="OPEN").filter(
        Q(title__icontains=data["search_param"]) | Q(description__icontains=data["search_param"])
    )

    # для авторизованных пользователей с инлайном добавления в избранное
    if bot.is_authenticated:
        await message.answer(
            f"Найдено объявлений: {len(info)}",
            reply_markup=get_keyboard(
                *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
            ),
        )
        for adv in info:
            await message.answer(
                f"🔎 <b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}",
                reply_markup=get_callback_btns(btns={"Добавить в избранное": f"add-fvr_{adv.id}"}),
            )

    else:
        await message.answer(
            f"Найдено объявлений: {len(info)}",
            reply_markup=get_keyboard(
                *START_KB, placeholder=START_KB_PLACEHOLDER, sizes=START_KB_SIZES
            ),
        )
        for adv in info:
            await message.answer(
                f"🔎 <b>{adv.title}:</b>\n{adv.description}\n<i>{adv.status}</i>\nuser: {adv.creator_id}"
            )
    await state.clear()


@router.message(StateFilter(None), F.text == "📲 Авторизация")
async def check_user(message: types.Message, state: FSMContext):
    """
    АВТОРИЗАЦИЯ, шаг 1.
    Запрос имени пользователя
    """
    await message.answer("Введите имя пользователя", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddLogIn.login)


@router.message(AddLogIn.login, F.text)
async def check_user_set_username(message: types.Message, state: FSMContext):
    """
    АВТОРИЗАЦИЯ, шаг 2.
    Запрос ввода пароля
    """
    await state.update_data(username=message.text)
    await message.answer("Введите пароль")
    await state.set_state(AddLogIn.password)


@router.message(AddLogIn.password, F.text)
async def check_user_set_password(message: types.Message, state: FSMContext, bot: Bot):
    """
    АВТОРИЗАЦИЯ, шаг 3.
    Проверка данных, запись токена в middleware и проставление признака is_authenticated в бот
    """
    await state.update_data(password=message.text)
    await message.delete()  # удаляем сообщение с паролем
    data = await state.get_data()

    usr = authenticate(username=data["username"], password=data["password"])
    if usr:
        # токен передается в middleware по логину и паролю
        router.message.middleware(AuthSession(auth_token=usr.auth_token.key))
        router.callback_query.middleware(AuthSession(auth_token=usr.auth_token.key))

        # вешаем признак авторизации боту, чтобы подбираться в ветвлении поведения в обработчиках, где проще так
        bot.is_authenticated = True
        await message.answer(
            f"Привет, {usr.username}!",
            reply_markup=get_keyboard(
                *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
            ),
        )

    else:
        await message.answer(
            "неверный логин или пароль, попробуйте авторизоваться заново",
            reply_markup=get_keyboard(
                *START_KB, placeholder=START_KB_PLACEHOLDER, sizes=START_KB_SIZES
            ),
        )
    await state.clear()


@router.callback_query(StateFilter(None), F.data.startswith("update-adv_"))
async def update_adv_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    UPDATE объявления по инлайн, шаг 1.
    Запись id и объекта объявления. Запрос ввода названия
    """
    adv_id = int(callback.data.split("_")[1])
    await state.update_data(id=adv_id)

    # adv_for_update = await orm_get_advertisement_by_id(session, adv_id)
    adv_for_update = Advertisement.objects.get(id=adv_id)
    AddAdv.adv_object = adv_for_update  # сохраняем объект, чтобы обращаться к его атрибутам

    await callback.answer()
    await callback.message.answer(
        "<b>Сейчас бот запросит данные для изменения объявления.</b>\nЕсли вы хотите "
        "оставить предыдущее значение и <b>пропустить какое-либо поле</b>, то введите "
        "символ точки .\nЕсли хотите вернуться на шаг назад и изменить указанные данные, "
        "введите в строке слово <b>назад</b>"
    )
    await callback.message.answer(
        "Введите название объявления", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddAdv.title)


# noinspection PyUnusedLocal
@router.message(StateFilter(None), F.text == "➕ Новое объявление")
async def create_adv(
    message: types.Message, state: FSMContext, auth_token: str
):  # для закрытия доступа неавторизов
    """
    ADD объявление, шаг 1.
    Запрос ввода названия
    """
    await message.answer(
        "<b>Сейчас бот запросит данные для создания объявления.</b>\nЕсли вы захотите вернуться на "
        "шаг назад и изменить указанные данные, введите в строке слово <b>назад</b>"
    )
    await message.answer("Введите название объявления", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddAdv.title)


@router.message(AddAdv.title, F.text)
async def create_adv_set_title(message: types.Message, state: FSMContext):
    """
    UPDATE/ADD объявления, шаг 2.
    Запись названия, ожидание описания
    """

    # логика пропуска шага при апдейте, оставляем старые данные
    if message.text == ".":
        await state.update_data(title=AddAdv.adv_object.title)

    else:
        if len(message.text) > 5:
            await state.update_data(title=message.text)
        else:
            await message.answer(
                "Название объявления не может содержать менее 5 символов. Введите заново"
            )
            return

    await message.answer("Введите описание объявления")
    await state.set_state(AddAdv.description)


@router.message(AddAdv.description, F.text)
async def create_adv_set_descr(message: types.Message, state: FSMContext):
    """
    UPDATE/ADD объявления, шаг 3.
    Запись описания, запрос статуса
    """

    # логика пропуска шага при апдейте, оставляем старые данные
    if message.text == ".":
        await state.update_data(description=AddAdv.adv_object.description)

    else:
        if len(message.text) > 5:
            await state.update_data(description=message.text)
        else:
            await message.answer("Описание не может содержать менее 5 символов. Введите заново")
            return

    # await message.answer("Введите статус OPEN, CLOSED ИЛИ DRAFT")
    await message.answer(text='Выберите статус объявления', reply_markup=get_callback_btns(
        btns=STATE_BTNS, sizes=(3,)))
    await state.set_state(AddAdv.status)


## noinspection PyUnresolvedReferences
@router.callback_query(AddAdv.status)
async def create_adv_set_status_creator(
        callback: types.CallbackQuery, session: AsyncSession, state: FSMContext, auth_token: str
):
    """
    UPDATE/ADD объявления, шаг 4.
    Запись статуса и создание/изменение
    """

    passed_state = [i for i in STATE_BTNS if STATE_BTNS[i] == callback.data]

    if passed_state:
        await state.update_data(status=passed_state[0])
    else:
        await callback.message.answer(
            text='Некорректное значение. Введите статус заново', reply_markup=get_callback_btns(
                btns=STATE_BTNS, sizes=(3, )))
        return

    user = Token.objects.filter(key=auth_token).first().user
    await state.update_data(creator=user)
    data = await state.get_data()

    adv_id = None
    if data.get("id"):
        adv_id = data.pop("id")

    # проверяем, что пользователь при смене статуса/создании не превышает максимально допустимое кол-во объявлений
    if passed_state[0] == "OPEN":
        counter = Advertisement.objects.filter(status="OPEN", creator=user).count()
        if counter >= 10:
            # проверка, что это не редактирование уже ранее открытого объявления
            if AddAdv.adv_object:
                if AddAdv.adv_object.status != "OPEN":
                    await callback.message.answer(
                        "У пользователя может быть не более 10 открытых объявлений одновременно"
                    )
                    return
            # если создание нового при максимально допустимом значении
            else:
                await callback.message.answer(
                    "У пользователя может быть не более 10 открытых объявлений одновременно"
                )
                return

    try:
        res, _ = Advertisement.objects.update_or_create(id=adv_id, creator=user, defaults={**data})
        if res:
            msg = "Объявление опубликовано"
        else:
            msg = "Произошла ошибка"
    except Exception as e:
        msg = f"Произошла ошибка: {e} "

    await state.clear()
    AddAdv.adv_object = None
    await callback.message.answer(
        msg,
        reply_markup=get_keyboard(
            *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
        ),
    )


# # noinspection PyUnresolvedReferences
# @router.message(AddAdv.status, F.text)
# async def create_adv_set_status_creator(message: types.Message, state: FSMContext, auth_token: str):
#     """
#     UPDATE/ADD объявления, шаг 4.
#     Запись статуса и создание/изменение
#     """
#
#     # логика пропуска шага при апдейте, оставляем старые данные
#     if message.text == ".":
#         await state.update_data(status=AddAdv.adv_object.status)
#
#     else:
#         # проверяем допустимое значение статуса
#         if {message.text}.intersection(["OPEN", "DRAFT", "CLOSED", "."]):
#             await state.update_data(status=message.text)
#         else:
#             await message.answer("Некорректное значение. Введите статус заново")
#             return
#
#     user = Token.objects.filter(key=auth_token).first().user
#     await state.update_data(creator=user)
#     data = await state.get_data()
#
#     # проверяем, что пользователь при смене статуса/создании не превышает максимально допустимое кол-во объявлений
#     if message.text == "OPEN":
#         counter = Advertisement.objects.filter(status="OPEN", creator=user).count()
#         if counter >= 5:
#             # проверка, что это не редактирование уже ранее открытого объявления
#             if AddAdv.adv_object:
#                 if AddAdv.adv_object.status != "OPEN":
#                     await message.answer(
#                         "У пользователя может быть не более 5 открытых объявлений одновременно"
#                     )
#                     return
#             # если создание нового при максимально допустимом значении
#             else:
#                 await message.answer(
#                     "У пользователя может быть не более 5 открытых объявлений одновременно"
#                 )
#                 return
#
#     adv_id = None
#     if data.get("id"):
#         adv_id = data.pop("id")
#
#     try:
#         res, _ = Advertisement.objects.update_or_create(id=adv_id, creator=user, defaults={**data})
#         if res:
#             msg = "Объявление опубликовано"
#         else:
#             msg = "Произошла ошибка"
#     except Exception as e:
#         msg = f"Произошла ошибка: {e} "
#
#     await state.clear()
#     AddAdv.adv_object = None
#     await message.answer(
#         msg,
#         reply_markup=get_keyboard(
#             *START_AUTH_KB, placeholder=START_AUTH_PLACEHOLDER, sizes=START_AUTH_SIZES
#         ),
#     )
