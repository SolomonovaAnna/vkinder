from vk_api.longpoll import VkEventType, VkLongPoll
from tools import bot
from database import creating_database


if __name__ == '__main__':
    for event in bot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            res = event.text.lower()
            user_id = event.user_id
            if res == 'поиск':
                creating_database()
                bot.get_profile_info(user_id)
                bot.users_search(offset=0)
                bot.show_found_person(user_id)
            elif res == 'далее':
                bot.users_search(offset=50)
                bot.show_found_person(user_id)
            elif res == 'пока':
                bot.send_msg(user_id, "Спасибо за использование сервиса. Всего доброго!")
                break
            else:
                bot.send_msg(user_id, f' Бот готов к поиску, наберите: \n '
                                      f' "Поиск - поиск людей. \n'
                                      f' "Далее - продолжить поиск. \n'
                                      f' "Пока - закончить поиск. \n'
                                      )
        
