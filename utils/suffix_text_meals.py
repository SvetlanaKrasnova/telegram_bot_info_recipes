def show_suffix(x: int):
    """
    Для форматирования текста.
    Исользуется в функции, которая предлагает пользователю рецепты
    :param x:
    :return:
    """
    last_digits = x % 100
    if last_digits // 100 == 1:
        return 'ов'
    elif last_digits % 10 == 1:
        return ''
    elif last_digits % 10 >= 2 and last_digits % 10 <= 4:
        return 'а'
    return 'ов'
