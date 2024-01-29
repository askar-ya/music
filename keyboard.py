import logic
from telebot import types


def main_keyboard():
    markup = types.InlineKeyboardMarkup()
    bt1 = types.InlineKeyboardButton('О Свете', callback_data='light')
    bt2 = types.InlineKeyboardButton('Об Иване', callback_data='ivan')
    markup.add(bt1, bt2)
    bt3 = types.InlineKeyboardButton('Доступ к каналу с исцеляющей музыкой', callback_data='baf_music')
    markup.add(bt3)
    bt4 = types.InlineKeyboardButton('Товары', callback_data='products^f^1')
    bt5 = types.InlineKeyboardButton('Концерты ', callback_data='concert')
    bt6 = types.InlineKeyboardButton('Наш канал', url='https://t.me/+_ZZsW08Yfcw0Nzhi',  callback_data='chanel')
    bt7 = types.InlineKeyboardButton('Контакты', callback_data='contacts')

    return markup.add(bt4, bt5, bt6, bt7)


def products_list(page: int, url):
    products = logic.read_from_file('text.json')['products']
    pages = len(products)
    markup = types.InlineKeyboardMarkup()
    link = types.InlineKeyboardButton('Подробнее', url=url)
    if page == 1 and pages != 0:
        markup.add(link, types.InlineKeyboardButton(f'{page + 1} ->', callback_data=f'products^past_page^{page+1}'))
    elif page > 1 and page != pages:
        markup.add(link)
        markup.add(types.InlineKeyboardButton(f'<- {page - 1}', callback_data=f'products^past_page^{page-1}'),
                   types.InlineKeyboardButton(f'{page + 1} ->', callback_data=f'products^past_page^{page+1}'))
    elif page == pages:
        if pages != 1:
            markup.add(types.InlineKeyboardButton(f'<- {page - 1}', callback_data=f'products^past_page^{page-1}'), link)

    return [markup, page]


def all_products():
    markup = types.InlineKeyboardMarkup()
    products = logic.read_from_file('text.json')
    for n, prod in enumerate(products['products']):
        markup.add(types.InlineKeyboardButton(prod['name'], callback_data=f'edit_p {n}'))
    return markup


def edit_p(n):
    markup = types.InlineKeyboardMarkup()
    name = types.InlineKeyboardButton('название', callback_data=f'edit>name {n}')
    text = types.InlineKeyboardButton('описание', callback_data=f'edit>text {n}')
    link = types.InlineKeyboardButton('ссылка', callback_data=f'edit>link {n}')
    pic = types.InlineKeyboardButton('медиа', callback_data=f'edit>media {n}')
    price = types.InlineKeyboardButton('цена', callback_data=f'edit>price {n}')
    markup.add(name, text, link, pic, price)
    return markup
