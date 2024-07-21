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
from aiogram import F
from googletrans import Translator
from utils.suffix_text_meals import show_suffix
from interfaces.api_themealdb import get_categories, get_recipes_by_category, get_recipe_by_id

translator = Translator()
router = Router()


class OrderRecipes(StatesGroup):
    choosing_category = State()
    selected_recipes = State()


@router.message(Command("category_search_random"))
async def recipes(message: Message, command: CommandObject, state: FSMContext):
    """
    Обработчик команды /category_search_random
    :param message:
    :param command:
    :param state:
    :return:
    """
    if command.args is None:
        await message.answer('Вы забыли указать количество рецептов, которое хотите получить. 🙂\n'
                             'Пожалуйста повторите комманду и передайте число.\n'
                             'Пример вызова "/category_search_random 2"')
        return

    try:
        int(command.args)
    except:
        await message.answer(f'Не удалось распознать значение "{command.args}'
                             f'\nПожалуйста, введите число. Пример команды:\n"/category_search_random 1"')
        return

    # Записываем число ожидаемых рецептов
    await state.set_data({'count_recipes': int(command.args)})

    async with aiohttp.ClientSession() as session:
        # Получаем список категорий
        categories = await get_categories(session)
        await state.update_data({'categories': categories})

        # И выводим его пользователю в виде кнопок
        builder = ReplyKeyboardBuilder()
        for date_item in categories:
            builder.add(types.KeyboardButton(text=date_item))
        builder.adjust(2)

        await message.answer(f"Выберите категорию:", reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderRecipes.choosing_category.state)


@router.message(OrderRecipes.choosing_category)
async def recipes_by_category(message: types.Message, state: FSMContext):
    """
    Работает по нажатию на кнопку с категорией.
    Собирает список рецептов (meals) по переданной категории
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    if not message.text or not message.text in data['categories']:
        await message.answer(f'Не могу понять твой текст.\n'
                             f'Пожалуйста, выбери категорию из предложенных. 🙂')
        return

    async with aiohttp.ClientSession() as session:
        meals = await get_recipes_by_category(session=session, category=message.text)
        if not meals:
            await message.answer(f'В категории "{message.text}" рецептов не найдено.\n'
                                 f'Пожалуйста, выберите другую категорию.')
            return

        # Получаем из списка рецептов случайные рецепты
        # и запоминаем их id
        # Если общее количество рецептов меньше или равно количеству, которое ввел пользователь
        # Пишем другой текст
        count_recipes = int(data['count_recipes'])
        meals_len = meals.__len__()
        if count_recipes > meals_len or count_recipes == meals_len:
            selected_meals = meals
            text_message = f'В этой категории только "{meals_len}" рецепт{show_suffix(meals_len)}'
        else:
            # Выбираем случайные
            selected_meals = choices(meals, k=count_recipes)
            text_message = 'Как вам такие варианты'

        text_meals = [translator.translate(el.str_meal, dest='ru').text for el in selected_meals]
        await state.set_data({'id_meals': [el.id_meal for el in selected_meals]})

        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Покажи рецепты'))
        builder.adjust(1)

        await message.answer(f"{text_message}: {', '.join(text_meals)}",
                             reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderRecipes.selected_recipes.state)


@router.message(OrderRecipes.selected_recipes)
async def show_recipes(message: types.Message, state: FSMContext):
    """
    Логика по отображению текста рецептов (после нажатия кнопки "Покажи рецепты")
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    async with aiohttp.ClientSession() as session:
        recipes = await asyncio.gather(*[get_recipe_by_id(session, id_meal) for id_meal in data['id_meals']])

        # Проверяем на ошибки
        # Если не удалось получить рецепты, выводим текстовое сообщение с предупреждением
        recipes_not_found = list(filter(lambda x: x.status == 'Error', recipes))

        # Выводим пользователю рецепты
        for recipe in recipes:
            # Если удалось получить рецепт - выводим его пользователю
            if recipe.status == 'Success':
                title_recipe = translator.translate(recipe.str_meal, dest='ru').text
                text_recipe = translator.translate(recipe.str_instructions, dest='ru').text
                ingredients = [translator.translate(v, dest='ru').text for v in recipe.ingredients]

                response = as_list(
                    as_section(Bold(f"📌 {title_recipe}")),
                    as_section(Bold("📖 Рецепт:"), f"{text_recipe}\n"),
                    as_section(Bold("📝 Ингредиенты:"), f"{', '.join(ingredients)}"))

                await message.answer(**response.as_kwargs(), reply_markup=types.ReplyKeyboardRemove())

        if recipes_not_found:
            text_message = "По остальным блюдам не удалось" if recipes else "Не удалось"
            await message.answer(f"{text_message} получить рецепты 😔.", reply_markup=types.ReplyKeyboardRemove())

        await state.clear()


@router.message(F.text)
async def any_text_handler(message: Message) -> None:
    """
    Обработчик на сторонний текст, отличный от сценария работы бота
    :param message:
    :return:
    """
    await message.answer(f'Не могу понять твой текст.\n'
                         f'Если хочешь начать диалог со мной, набери команду '
                         f'"/start" 🙂')
