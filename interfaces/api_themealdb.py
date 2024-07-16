from typing import List
from interfaces.models import Responce, Meals

async def get_categories(session) -> list:
    """
    Функция по получению списка категорий по которым можно получить рецепты.
    :param session: объект сессии
    :return: список категорий
    """
    async with session.get(url='https://www.themealdb.com/api/json/v1/1/list.php?c=list') as resp:
        data = await resp.json()
        return [x['strCategory'] for x in data.get('meals', '') if x.get('strCategory')]


async def get_meals_for_category(session, category: str) -> List[Meals]:
    """
    Функция собирает список всех рецептов данной категории
    :param session: объект сессии
    :param category: наименование категории, по которой нужно получить рецепты
    :return:
    """
    async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/search.php?s={category}') as resp:
        data = await resp.json()
        return Responce(**data).meals


async def get_recipes(session, id_meal) -> Meals:
    """
    Функция получает рецепт блюда по его id
    :param session:
    :param id_meal: id блюда
    :return:
    """
    async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id_meal}') as resp:
        data = await resp.json()
        if data.get('meals'):
            if data.get('meals').__len__() == 1:
                return Responce(**data).meals[0]
