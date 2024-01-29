import datetime
import os
import telebot
import keyboard
import logic
import setings

from telebot import types
bot = telebot.TeleBot(setings.Token)


@bot.message_handler(commands=['start', 'admin_new_product', 'admin_edit'])
def send_welcome(message):
    user_id = message.chat.id
    if message.text == '/start':
        markup = keyboard.main_keyboard()
        data = logic.read_from_file('users.json')

        if message.chat.id not in data['users']:
            data['users'].append(user_id)

        logic.write_to_file('users.json',
                            data)

        bot.send_photo(user_id,
                       open('image.jpg', 'rb'),
                       caption=logic.read_from_file('text.json')['hellow'],
                       reply_markup=markup)

    elif message.chat.id in setings.admins:
        if message.text == '/admin_new_product':
            bot.send_message(user_id, 'напишите название продукта')
            bot.register_next_step_handler(message, new_product)

        elif message.text == '/admin_edit':
            markup = keyboard.main_keyboard()
            hellow = types.InlineKeyboardButton('Приветствие', callback_data='hellow_edit')
            bot.send_message(user_id, 'Выберите что, хотите поменять:',
                             reply_markup=markup.add(hellow))


def new_product(message):
    bot.send_message(message.chat.id, 'Отлично!\nТеперь укажи цену')
    bot.register_next_step_handler(message, get_price, {'name': message.text})


def get_price(message, product):
    product['price'] = message.text
    bot.send_message(message.chat.id, 'напишите описание, можете написать $'
                                      ' вместо цены и она подставится автоматически')
    bot.register_next_step_handler(message, get_text, product)


def get_text(message, product):
    product['text'] = message.text
    bot.send_message(message.chat.id, 'Пришлите ссылку которая будет на кнопке')
    bot.register_next_step_handler(message, get_link, product, False)


def get_link(message, product):
    product['link'] = message.text
    bot.send_message(message.chat.id, 'пришлите фото, так же можете добавить видео')
    bot.register_next_step_handler(message, get_media, product, False)

def get_media(message, product):

    if not os.path.exists('products/{0}'.format(product['name'])):
        os.makedirs(f'products/{product['name']}')
    src = 'image.jpg'
    file_info = ''
    if message.photo:
        file_info = bot.get_file(message.photo[1].file_id)

        src = f'products/{product['name']}/1.jpg'
    elif message.video:
        file_info = bot.get_file(message.video[1].file_id)
        src = f'products/{product['name']}/1.mkv'

    downloaded_file = bot.download_file(file_info.file_path)

    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    product['media'] = src

    data = logic.read_from_file('text.json')
    data['products'].append(product)
    logic.write_to_file('text.json',
                        data)
    bot.send_message(message.chat.id,
                     'Продукт добавлен!!')


@bot.message_handler(content_types=['text', 'photo', 'video'])
def mailing(message):
    if message.chat.id in setings.admins:
        for user in logic.read_from_file('users.json')['users']:
            bot.copy_message(user, message.chat.id, message.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    call_back = call.data
    admin = False
    if user_id in setings.admins:
        admin = True

    if call_back.split('^')[0] == 'products':
        if not admin:
            if len(call_back.split('^')) > 1:
                product = logic.read_from_file('text.json')['products'][int(call_back.split('^')[2]) - 1]
                markup = keyboard.products_list(
                    int(call_back.split('^')[2]), product['link'])[0]

                if product['media'][-3:] == 'jpg':
                    bot.send_photo(chat_id=user_id,
                                   photo=open(product['media'], 'rb'),
                                   caption=f'{product['name']}\n{product['text'].replace('$', product['price'])}',
                                   reply_markup=markup)
                elif product['media'][-3:] == 'mkv':
                    bot.send_video(user_id,
                                   open(product['media'], 'rb'),
                                   caption=f'{product['name']}\n{product['text'].replace('$', product['price'])}',
                                   reply_markup=markup)

                if call_back.split('^')[1] != 'f':
                    bot.delete_message(user_id, message_id=call.message.id)
        else:
            markup = keyboard.all_products()
            bot.send_message(user_id, 'Выберите товар для правки', reply_markup=markup)
    elif call_back.split(' ')[0] == 'edit_p':
        if admin:
            markup = keyboard.edit_p(call_back.split(' ')[1])
            bot.send_message(user_id, "Выберите, что изменить:",
                             reply_markup=markup)
    elif call_back.split('>')[0] == 'edit':
        row = call_back.split('>')[1].split(' ')[0]
        n = call_back.split('>')[1].split(' ')[1]
        if row != 'media':
            bot.send_message(user_id, 'Введите новое значение')
            bot.register_next_step_handler(call.message, re_prod, row, n)
        elif row == 'media':
            bot.send_message(user_id, 'Отправьте новое фото или видео')
            bot.register_next_step_handler(call.message, re_prod_m, n)
    elif call_back == 'contacts':
        if not admin:
            text = logic.read_from_file('text.json')['contacts']
            bot.send_message(user_id, text)
        else:
            text = logic.read_from_file('text.json')['contacts']
            bot.send_message(user_id, text)
            bot.send_message(user_id, 'напишите новый текст')
            bot.register_next_step_handler(call.message, edit_contacts)
    elif call_back == 'concert':
        if not admin:
            text = logic.read_from_file('text.json')['concert']
            bot.send_message(user_id, text)
        else:
            text = logic.read_from_file('text.json')['concert']
            bot.send_message(user_id, text)
            bot.send_message(user_id, 'напишите новый текст')
            bot.register_next_step_handler(call.message, edit_concert)
    elif call_back == 'light':
        if not admin:
            text = logic.read_from_file('text.json')['sveta']
            bot.send_message(user_id, text)
        else:
            text = logic.read_from_file('text.json')['sveta']
            bot.send_message(user_id, text)
            bot.send_message(user_id, 'напишите новый текст')
            bot.register_next_step_handler(call.message, edit_sveta)
    elif call_back == 'ivan':
        if not admin:
            text = logic.read_from_file('text.json')['ivan']
            bot.send_message(user_id, text)
        else:
            text = logic.read_from_file('text.json')['ivan']
            bot.send_message(user_id, text)
            bot.send_message(user_id, 'напишите новый текст')
            bot.register_next_step_handler(call.message, edit_ivan)
    elif call_back == 'baf_music':
        price = types.LabeledPrice(label='Доступ нв 2 недели', amount=500*100)
        bot.send_invoice(user_id,
                         'доступ на 2 недели',
                         'Активация доступа на 2 недели к закрытому каналу',
                         '2week-payload',
                         setings.Token_pay,
                         "rub",
                         is_flexible=False,
                         prices=[price],
                         start_parameter='two-week-sub')


def re_prod(message, row, n):
    text = message.text
    data = logic.read_from_file('text.json')
    data['products'][int(n)][row] = text
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Готово!')


def re_prod_m(message, n):
    data = logic.read_from_file('text.json')
    path = data['products'][int(n)]['media'][:-5]

    file_info = ''
    src = ''
    if message.photo:
        file_info = bot.get_file(message.photo[1].file_id)

        src = f'{path}1.jpg'
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
        src = f'{path}1.mkv'

    downloaded_file = bot.download_file(file_info.file_path)

    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    data['products'][int(n)]['media'] = src
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Готово!')


def edit_contacts(message):
    text = message.text
    data = logic.read_from_file('text.json')
    data['contacts'] = text
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Правки внесены!')


def edit_sveta(message):
    text = message.text
    data = logic.read_from_file('text.json')
    data['sveta'] = text
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Правки внесены!')


def edit_ivan(message):
    text = message.text
    data = logic.read_from_file('text.json')
    data['ivan'] = text
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Правки внесены!')


def edit_concert(message):
    text = message.text
    data = logic.read_from_file('text.json')
    data['concert'] = text
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Правки внесены!')


def edit_hellow(message):
    text = message.text
    data = logic.read_from_file('text.json')
    data['hellow'] = text
    logic.write_to_file('text.json', data)
    bot.send_message(message.chat.id, 'Правки внесены!\nОтправьте новую фотографию!')
    bot.register_next_step_handler(message, edit_hellow_pic)


def edit_hellow_pic(message):
    src = 'image.jpg'
    file_info = ''
    if message.photo:
        file_info = bot.get_file(message.photo[1].file_id)

        downloaded_file = bot.download_file(file_info.file_path)

        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, 'фото обновлено!')


@bot.pre_checkout_query_handler(lambda q: True)
def pre_checkout_handler(pre_checkout_q):
    bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    link = bot.create_chat_invite_link(setings.group, member_limit=1)
    data = logic.read_from_file('users.json')
    data['prime'].append({'user': message.chat.id,
                          'prime_to': str(datetime.datetime.now())})
    logic.write_to_file('users.json', data)
    bot.send_message(message.chat.id,
                     f'ваша ссылка:{link.invite_link}')


bot.infinity_polling()
