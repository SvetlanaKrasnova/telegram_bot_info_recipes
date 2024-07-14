import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.utils.markdown import hbold
from aiogram import types
from recipes_handler import router
from token_data import TOKEN
from button_start import keyboard

dp = Dispatcher()
dp.include_router(router)


@dp.message(F.text.lower() == "команды")
async def commands(message: types.Message):
    response = as_list(
        as_marked_section(
            Bold("Команды:"),
            "/category_search_random - для указания количества рецептов",
            marker="✅ ",
        ),
    )
    # Теперь отправим ответ, отрендерив, то есть придав структуру,
    # при помощи метода .as_kwargs() и распаковав внутрь метода .answer()
    await message.answer(**response.as_kwargs())


@dp.message(F.text.lower() == "описание бота")
async def description(message: types.Message):
    text = r"Этот бот предоставляет информацию о рецептах с сайта https://www.themealdb.com/" \
           "\n\nКак пользоваться ботом" \
           "\nДля запуска бота, набери команду /category_search_random \"количество рецептов\"." \
           "\nПример:" \
           "\n/category_search_random 2" \
           "\nДалее, у вас состоится диалог с ботом, по оканчанию которого бот предложит " \
           "вам какие рецепты он выбрал из определенной категории."
    await message.answer(text)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    /start
    """
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! С чего начнем?",
                         reply_markup=keyboard)


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
