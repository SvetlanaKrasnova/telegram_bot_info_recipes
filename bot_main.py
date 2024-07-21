import sys
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.utils.formatting import Bold, as_list, as_marked_section, as_section, as_numbered_list
from aiogram.utils.markdown import hbold
from aiogram import types
from recipes_handler import router
from config.token_data import TOKEN
from keyboards.keyboard_start import keyboard

dp = Dispatcher()
dp.include_router(router)


@dp.message(F.text.lower() == "команды")
async def commands(message: types.Message):
    response = as_list(
        as_marked_section(
            Bold("Команды:"),
            "/category_search_random - для указания количества рецептов. "
            "Пример вызова: \"/category_search_random 5\"",
            marker="✅  ",
        ),
    )
    await message.answer(**response.as_kwargs())


@dp.message(F.text.lower() == "описание бота")
async def description(message: types.Message):
    response = as_list(as_section("Этот бот предоставляет информацию о рецептах с сайта https://www.themealdb.com\n"
                                  "Вам необходимо ввести количество рецептов, которое вы хотите получить, "
                                  "выбрать категорию, а бот предложит вам варианты."),
                       as_section(Bold("Как пользоваться ботом")),
                       as_numbered_list(*["Набери команду\n /category_search_random \"количество рецептов\"",
                                          "Выбери категорию, по которой хочешь получить рецепты",
                                          "Если варианты понравились, нажми \"Показать рецепты\""]))

    await message.answer(**response.as_kwargs())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик кнопки /start
    :param message:
    :return:
    """
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! С чего начнем?",
                         reply_markup=keyboard)


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
