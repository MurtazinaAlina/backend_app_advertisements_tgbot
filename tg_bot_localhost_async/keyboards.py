from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_keyboard(
    *btns: str,  # принимает последовательность строк через запятую
    placeholder: str = None,
    sizes: tuple[int] | tuple[int, int] | tuple[int, int, int] = (2, 1),
):
    """
    Гибко генерит клавиатуру внутри хэндлера.
    Сразу настроено отображение с вызовом метода маркап, ресайзом кнопки, установкой плейсхолдера; в таком виде
    можно передавать в reply_markup= напрямую.

    Example:
    get_keyboard(
            "Кнопка 1",
            "Кнопка 2",
            placeholder="Что вас интересует?",
            sizes=(2, )
        )
    """
    keyboard = ReplyKeyboardBuilder()
    for text in btns:
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )


# генерация callback кнопок
def get_callback_btns(
    *,
    btns: dict[
        str, str
    ],  # словарь {'текст_кнопки': 'строка отправляемая боту в callback_query при нажатии'}
    sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()
