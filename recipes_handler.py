import asyncio
import aiohttp
from random import choices
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import Bold, as_list, as_section
from googletrans import Translator
from interfaces.api_themealdb import get_categories, get_meals_for_category, get_recipes

"""
Обработчики для взаимодействия с API themealdb
"""
translator = Translator()
router = Router()


class OrderRecipes(StatesGroup):
    waiting_for_category = State()
    waiting_for_show_recipes = State()


@router.message(Command("category_search_random"))
async def weather(message: Message, command: CommandObject, state: FSMContext):
    """
    Обработчик команды /category_search_random
    :param message:
    :param command:
    :param state:
    :return:
    """
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return

    try:
        int(command.args)
    except:
        await message.answer(f'Ошибка: не удалось распознать аргумент "{command.args}'
                             f'\nПожалуйста, введите числовое значение. Пример команды "/category_search_random 1"')
        return

    # Записываем число ожидаемых рецептов
    await state.set_data({'count_recipes': int(command.args)})

    async with aiohttp.ClientSession() as session:
        # Получаем список категорий
        categories = await get_categories(session)

        # И выводим его пользователю в виде кнопок
        builder = ReplyKeyboardBuilder()
        for date_item in categories:
            builder.add(types.KeyboardButton(text=date_item))
        builder.adjust(2)

        await message.answer(f"Выберите категорию:", reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderRecipes.waiting_for_category.state)


@router.message(OrderRecipes.waiting_for_category)
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
        meals = await get_meals_for_category(session=session, category=message.text)
        if not meals:
            await message.answer(f'В категории "{message.text}" рецептов не найдено.\n'
                                 f'Пожалуйста, выберите другую категорию.')
            return

        # Получаем из списка рецептов случайные рецепты
        # и запоминаем их id
        choices_meals = choices(meals, k=data['count_recipes'])
        text_meals = [translator.translate(el.str_meal, dest='ru').text for el in choices_meals]
        await state.set_data({'id_meals': [el.id_meal for el in choices_meals]})

        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Покажи рецепты'))
        builder.adjust(1)

        await message.answer(f"Как вам такие варианты: {', '.join(text_meals)}",
                             reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderRecipes.waiting_for_show_recipes.state)


@router.message(OrderRecipes.waiting_for_show_recipes)
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
            title_recipe = translator.translate(recipe.str_meal, dest='ru').text
            text_recipe = translator.translate(recipe.str_instructions, dest='ru').text
            ingredients = [translator.translate(v, dest='ru').text for v in recipe.ingredients]

            response = as_list(
                as_section(Bold(title_recipe)),
                as_section(Bold("Рецепт:"), f"\n{text_recipe}"),
                as_section(Bold("Ингредиенты:"), f"\n{', '.join(ingredients)}"))
            await message.answer(**response.as_kwargs())
