import asyncio
import aiohttp
from random import choices
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from googletrans import Translator
from utils import get_categories, get_meals, get_recipes

"""
Обработчики для взаимодействия с API themealdb
"""
translator = Translator()
router = Router()


class OrderWeather(StatesGroup):
    waiting_for_forecast = State()
    waiting_for_forecas = State()


@router.message(Command("category_search_random"))
async def weather(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return

    # TODO Проверка на ввод
    # Записываем число ожидаемых рецептов
    await state.set_data({'count_recipes': int(command.args)})

    async with aiohttp.ClientSession() as session:
        # Получаем список категорий
        categories = await get_categories(session)

        # И выводим его пользователю
        builder = ReplyKeyboardBuilder()
        for date_item in categories:
            builder.add(types.KeyboardButton(text=date_item))
        builder.adjust(2)

        await message.answer(f"Выберите категорию:", reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderWeather.waiting_for_forecast.state)


@router.message(OrderWeather.waiting_for_forecast)
async def weather_by_category(message: types.Message, state: FSMContext):
    """
    Работает по нажатию на кнопку с категорией.
    Собирает список рецептов (meals) по переданной категории
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()

    async with aiohttp.ClientSession() as session:
        meals = await get_meals(session=session, category=message.text)
        if not meals:
            await message.answer(f'В категории "{message.text}" рецептов не найдено.\n'
                                 f'Пожалуйста, выберите другую категорию.')
            return
        # Получаем из списка рецептов случайные рецепты
        # и запоминаем их id
        choices_meals = choices(meals, k=data['count_recipes'])
        text_meals = [translator.translate(el['strMeal'], dest='ru').text for el in choices_meals]
        await state.set_data({'id_meals': [el['idMeal'] for el in choices_meals]})

        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Покажи рецепты'))
        builder.adjust(1)

        await message.answer(f"Как вам такие варианты: {', '.join(text_meals)}",
                             reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderWeather.waiting_for_forecas.state)


@router.message(OrderWeather.waiting_for_forecas)
async def show_recipes(message: types.Message, state: FSMContext):
    """
    Логика по отображению текста рецептов (после нажатия кнопки "Покажи рецепты")
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    async with aiohttp.ClientSession() as session:
        recipes = await asyncio.gather(*[get_recipes(session, id_meal) for id_meal in data['id_meals']])

        # Выводим пользователю рецепты
        for recipe in recipes:
            title_recipe = translator.translate(recipe['strMeal'], dest='ru').text
            text_recipe = translator.translate(recipe['strInstructions'], dest='ru').text
            ingredients = [translator.translate(v, dest='ru').text for k, v in recipe.items() if
                           k.__contains__('strIngredient') and v]
            await message.answer(f"{title_recipe}"
                                 f"\n\nРецепт:\n{text_recipe}"
                                 f"\n\nИнгредиенты: {', '.join(ingredients)}")
