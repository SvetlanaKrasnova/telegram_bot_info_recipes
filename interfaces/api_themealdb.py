import logging
from typing import List
from interfaces.models import ResponceMeals, Meal


async def get_categories(session) -> list:
    """
    Функция по получению списка категорий по которым можно получить рецепты.
    :param session: объект сессии
    :return: список категорий
    """
    async with session.get(url='https://www.themealdb.com/api/json/v1/1/list.php?c=list') as resp:
        data = await resp.json()
        return [x['strCategory'] for x in data.get('meals', '') if x.get('strCategory')]


async def get_recipes_by_category(session, category: str) -> List[Meal]:
    """
    Функция собирает список всех рецептов по наименованию категории
    :param session: объект сессии
    :param category: наименование категории, по которой нужно получить рецепты
    :return:
    """
    async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/search.php?s={category}') as resp:
        data = await resp.json()
        return ResponceMeals(**data).meals


async def get_recipe_by_id(session, id_meal) -> Meal:
    """
    Функция получает рецепт блюда по его id
    :param session:
    :param id_meal: id блюда
    :return:
    """
    async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id_meal}') as resp:
        try:
            data = await resp.json()
            if data.get('meals'):
                if data.get('meals').__len__() == 1:
                    return Meal(**data.get('meals')[0])
            logging.exception(f'Не удалось получить рецепт по id_meal "{id_meal}". '
                              f'Структура ответа от api не соответствует ожиданиям.\ndata:{data}')
        except Exception as e:
            logging.exception(f'Не удалось получить рецепт по id_meal "{id_meal}": {e}')
            return Meal(**{'status': "Error"})
