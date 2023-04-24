from vk_api.longpoll import VkEventType, VkLongPoll
from tools import bot
from database import creating_database



for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        res = event.text.lower()
        user_id = event.user_id
        if res == 'поиск':
               creating_database() 
               bot.get_age(user_id)
               bot.get_city(user_id)
               bot.get_sex(user_id)
               bot.users_search(bot.move_offset())
               bot.show_found_person(user_id)
        else:
            bot.send_msg(user_id, f' Бот готов к поиску, наберите: \n '
                                  f' "Поиск - Поиск людей. \n'
                                  )
