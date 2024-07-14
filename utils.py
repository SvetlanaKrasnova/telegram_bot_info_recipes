async def get_categories(session) -> list:
    """
    Функция по получению списка категорий
    Затем делает запрос и записывает json-данные из ответа в переменную data.
    :param session: объект сессии
    :return: список категорий
    """
    async with session.get(url='https://www.themealdb.com/api/json/v1/1/list.php?c=list') as resp:
        data = await resp.json()
        return [x['strCategory'] for x in data.get('meals', '') if x.get('strCategory')]


async def get_meals(session, category: str):
    """
    Функция собирает список всех рецептов данной категории
    :param session:
    :return:
    """
    async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/search.php?s={category}') as resp:
        data = await resp.json()
        return data.get('meals', [])


async def get_recipes(session, id_meal):
    """
    Функция по получению рецепта
    :param session:
    :param id_meal: id блюда
    :return:
    """
    async with session.get(url=f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={id_meal}') as resp:
        data = await resp.json()
        if data.get('meals'):
            if data.get('meals').__len__() == 1:
                return data['meals'][0]
