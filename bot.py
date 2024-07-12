import json

import telebot
from telebot import types
from instance.database import (get_guides_names,
                               get_guide_by_name,
                               get_guides,
                               add_to_favorite,
                               add_user,
                               get_rating,
                               get_user,
                               get_favorite,
                               rating_likes_add,
                               rating_likes_remove,
                               remove_from_favorite,
                               get_guide_by_id,
                               rating_views_add,
                               get_rating_board)
from Classes.Server import Server
import base64
import re
from keyboa import Keyboa

server = Server(8050)
server.start()

bot = telebot.TeleBot("")


@bot.message_handler(commands=['start', 'help', 'menu'])
def start(message=None, chat_id=None):
    user = get_user(message.chat.id if message else chat_id)
    menu = [['Избранное', 'Калькулятор артефактов', 'Рейтинг'], "Созвездия"]
    keyboard = Keyboa(items=menu, copy_text_to_callback=True)
    bot.send_message(message.chat.id if message else chat_id, "⭐ Выберите пункт меню ⭐", reply_markup=keyboard())


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    def remove_emojis(text):
        # Удаляем все, кроме букв и цифр ASCII
        return re.sub(r'[^\w\s]', '', text)

    def remove_ending_digit_if_four_or_five(text):
        # Проверяем, заканчивается ли строка на 4 или 5
        if text[-1] in '45':
            # Удаляем последнюю цифру, если это 4 или 5
            return text[:-2]
        else:
            return text

    print(f"call data = {call.data}")

    if remove_ending_digit_if_four_or_five(remove_emojis(call.data)) in get_guides_names():
        constellation_name = remove_ending_digit_if_four_or_five(remove_emojis(call.data))
        guide = get_guide_by_name(constellation_name)
        send_guide(call.message.chat.id, guide[0])
    if call.data in ['Калькулятор артефактов']:
        bot.send_message(call.message.chat.id, "🛸 Извините мы уже собираем необхдимые данные 🛸")
        file = open('./static/vids/aw.gif', 'rb')
        bot.send_animation(call.message.chat.id, file)
        file.close()
        start(chat_id=call.message.chat.id)
    if call.data in ['Избранное']:
        send_favorite(call.message)
        start(chat_id=call.message.chat.id)
    if call.data in ['Созвездия']:
        constellation_menu(call.message)
    if 'favorite' in call.data:
        data = call.data.split()
        command = data[1]
        user_id = data[2]
        guide_id = data[3]
        if command == 'add':
            user = add_to_favorite(user_id, guide_id)
            print(user.favorite_guides)
            rating_likes_add(guide_id)
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, f'🔥 Ваше созвездие {int(guide_id)} добавлено в избранное 🔥')
            start(chat_id=user.chat_id)

            return
        if command == 'remove':
            user = remove_from_favorite(user_id, guide_id)
            rating_likes_remove(guide_id)
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, f'💔 Ваше созвездие {guide_id} удалено из избранного 💔')
            start(chat_id=user.chat_id)

            return
    if call.data in ['Рейтинг']:
        send_rating(call)
        start(chat_id=call.message.chat.id)


def send_rating(call):
    rating = get_rating_board()
    menu = []
    for constellation in rating:
        constellation_data = get_guide_by_id(constellation.constellation_id)
        menu.append([f"{constellation_data.constellation_name} {constellation_data.constellation_rarity}\U00002B50",
                     f"👁 {constellation.views}", f"❤️ {constellation.likes}"])

    keyboard = Keyboa(items=menu, copy_text_to_callback=True)
    bot.send_message(call.message.chat.id, "🌟 Рейтинг созвездий 🌟", reply_markup=keyboard())


def constellation_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    query = get_guides()
    rarity_4 = []
    rarity_5 = []
    for guide in query:
        if guide.constellation_rarity == 4:
            rarity_4.append(types.KeyboardButton(f"{guide.constellation_name} {guide.constellation_rarity}\U00002B50"))
        if guide.constellation_rarity == 5:
            rarity_5.append(types.KeyboardButton(f"{guide.constellation_name} {guide.constellation_rarity}\U00002B50"))

    # Добавляем кнопки редкости 4 в первую колонку
    for i in range(max([len(rarity_4), len(rarity_5)])):
        try:
            b_1 = rarity_5[i]
        except IndexError:
            b_1 = types.KeyboardButton(" ")
        try:
            b_2 = rarity_4[i]
        except IndexError:
            b_2 = types.KeyboardButton(" ")
        markup.add(b_1, b_2)

    bot.send_message(message.chat.id,
                     "Выбери созвездие в меню снизу 👇. Или отправь мне часть его имени, я попробую его найти 🔭",
                     reply_markup=markup)


def send_favorite(call):
    menu = []
    favorites = get_favorite(call.chat.id)
    for favorites_id in favorites:
        guide = get_guide_by_id(favorites_id)
        menu.append([f"{guide.constellation_name} {guide.constellation_rarity}\U00002B50"])

    keyboard = Keyboa(items=menu, copy_text_to_callback=True)
    bot.send_message(call.chat.id, "\U0001F497 Ваш список избранных созвездий \U0001F497", reply_markup=keyboard())


def send_guide(chat_id, guide):
    constellation_image_b64 = guide.constellation_image
    # constellation_artifact_image_b64 = guide.constellation_artifact_image
    constellation_talents_image_b64 = guide.constellation_talents_image
    constellation_weapon_image_b64 = guide.constellation_weapon_image

    materials_reals_string = ""
    talent_string = ""
    for key, item in guide.constellation_rising_materials.items():
        materials_reals_string += f"x{item}\n"

    for key, item in guide.constellation_rising_talent_materials.items():
        talent_string += f"x{item}\n"

    markdown = f"""
{guide.constellation_name}

🌟Редкость:{guide.constellation_rarity}
🌬️Элемент:{guide.constellation_element}
🗡️Тип оружия:{guide.constellation_weapon_type}
👤Роль:{guide.constellation_role}

👣Материалы прокачки персонажа:

{materials_reals_string}

👣Материалы прокачки талантов:

{talent_string}
    """

    with open(f"./temp/constellation_image.jpg", "wb") as fh:
        fh.write(base64.b64decode(constellation_image_b64))

    # with open(f"./temp/constellation_artifact_image.jpg", "wb") as fh:
    #     fh.write(base64.b64decode(constellation_artifact_image_b64))
    #     fh.close()

    with open(f"./temp/constellation_talents_image.jpg", "wb") as fh:
        fh.write(base64.b64decode(constellation_talents_image_b64))
        fh.close()

    with open(f"./temp/constellation_weapon_image.jpg", "wb") as fh:
        fh.write(base64.b64decode(constellation_weapon_image_b64))
        fh.close()

    bot.send_media_group(chat_id, [
        types.InputMediaPhoto(open(f"./temp/constellation_image.jpg", "rb"),
                              caption=markdown),
        # types.InputMediaPhoto(open(f"./temp/constellation_artifact_image.jpg", "rb")),
        types.InputMediaPhoto(open(f"./temp/constellation_talents_image.jpg", "rb")),
        types.InputMediaPhoto(open(f"./temp/constellation_weapon_image.jpg", "rb")),

    ])
    rating = get_rating(guide.id)
    rating_views_add(guide.id)
    rating = get_rating(guide.id)
    user = get_user(chat_id)
    print(user.favorite_guides)
    menu = [[f'👁 {rating.views} просмотров', f'❤️ {rating.likes} лайков']]
    keyboard = Keyboa(items=menu, copy_text_to_callback=True)
    fav_guide_kb = types.InlineKeyboardMarkup()
    if str(guide.id) in json.loads(user.favorite_guides):
        fav_guide_kb.add(types.InlineKeyboardButton(text="❌ отписаться",
                                                    callback_data=f"favorite remove {user.chat_id} {guide.id}"))
    else:
        fav_guide_kb.add(types.InlineKeyboardButton(text="⭕ в избранное",
                                                    callback_data=f"favorite add {user.chat_id} {guide.id}"))
    bot.send_message(chat_id, "⭐ guide statistic ⭐", reply_markup=keyboard())
    bot.send_message(chat_id, "🌟 rating menu 🌟", reply_markup=fav_guide_kb)
    start(chat_id=chat_id)


@bot.message_handler(content_types=['text'])
def get_guide(message):
    def remove_emojis(text):
        # Удаляем все, кроме букв и цифр ASCII
        return re.sub(r'[^\w\s]', '', text)

    def remove_ending_digit_if_four_or_five(text):
        # Проверяем, заканчивается ли строка на 4 или 5
        if text[-1] in '45':
            # Удаляем последнюю цифру, если это 4 или 5
            return text[:-2]
        else:
            return text

    constellation_name = remove_ending_digit_if_four_or_five(remove_emojis(message.text))
    guide = get_guide_by_name(constellation_name)
    if len(guide) > 1:
        keyboard = types.InlineKeyboardMarkup()
        names = []
        for item in guide:
            names.append(item.constellation_name)
            keyboard.add(types.InlineKeyboardButton(f"{item.constellation_name} {item.constellation_rarity}\U00002B50",
                                                    callback_data=item.constellation_name))

        bot.send_message(message.chat.id, f"Возможно вы иммели введу этих созведий? 👇", reply_markup=keyboard)
        return
    if guide is None:
        bot.send_message(message.chat.id, "Я вас не понял \U0001F494")
        return
    if len(guide) == 0:
        bot.send_message(message.chat.id, "Я не могу найти это созвездие \U0001F494")
        return
    guide = guide[0]
    send_guide(message.chat.id, guide)


# @bot.message_handler(commands=['stop'])


bot.infinity_polling()
