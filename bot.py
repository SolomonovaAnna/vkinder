from vk_api.longpoll import VkEventType
from tools import bot
from database import creating_database, insert_data_search, check


class Interface:
    def input_data(self):
        for event in bot.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                res = event.text
                a = res.split('-')
                bot.sex = a[0]
                if bot.sex == 'ж':
                    bot.sex = 2
                elif bot.sex == 'м':
                    bot.sex = 1
                else:
                    print("Ошибка!")
                bot.age_from = int(a[1])
                bot.age_to = int(a[2])
                bot.city_title = a[3]
                return bot.city_title, bot.sex, bot.age_from, bot.age_to

    def handler(self):
        for event in bot.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                creating_database()
                res = event.text.lower()
                user_id = event.user_id
                offset = 0


                if res == "другое":
                    bot.send_msg(user_id,
                                          f' Если вы хотите искать по другим параметрам,\n'
                                          f' то введите свой пол(м или ж), возрастной диапазон и город для поиска'
                                          f' в формате: м(ж)-25-29-Москва. \n')

                    self.input_data()
                    found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                    for profile in found_persons:
                        id_found = profile.get('id')
                        link_found = profile.get('link')
                        seen_person = check(id_found)
                        list_id = []
                        for id in seen_person:
                            list_id.append(id[0])
                        if id_found in list_id:
                            continue
                        else:
                            insert_data_search(user_id, id_found)
                            attachment = bot.get_photo(id_found)
                            bot.send_msg(user_id, link_found, attachment=attachment)

                elif res == 'поиск':
                    bot.get_profile_info(user_id)

                    found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                    for profile in found_persons:
                        id_found = profile.get('id')
                        link_found = profile.get('link')
                        seen_person = check(id_found)
                        list_id = []
                        for id in seen_person:
                            list_id.append(id[0])
                        if id_found in list_id:
                            continue
                        else:
                            insert_data_search(user_id, id_found)
                            attachment = bot.get_photo(id_found)
                            bot.send_msg(user_id, link_found, attachment=attachment)

                elif res == 'далее':
                    if check == None:
                        bot.send_msg(user_id, f'База данных пуста, введите команду "поиск"! \n'
                                     )
                    else:
                        bot.get_profile_info(user_id)
                        offset = offset + 30
                        found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                        for profile in found_persons:
                            id_found = profile.get('id')
                            link_found = profile.get('link')
                            seen_person = check(id_found)
                            list_id = []
                            for id in seen_person:
                                list_id.append(id[0])
                            if id_found in list_id:
                                continue
                            else:
                                insert_data_search(user_id, id_found)
                                attachment = bot.get_photo(id_found)
                                bot.send_msg(user_id, link_found, attachment=attachment)
                elif res == 'другое далее':
                    bot.send_msg(user_id,
                                 f' Повторите данные для поиска,\n'
                                 f' в формате: м(ж)-25-29-Москва. \n')

                    self.input_data()
                    offset = offset + 30
                    found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                    for profile in found_persons:
                        id_found = profile.get('id')
                        link_found = profile.get('link')
                        seen_person = check(id_found)
                        list_id = []
                        for id in seen_person:
                            list_id.append(id[0])
                        if id_found in list_id:
                            continue
                        else:
                            insert_data_search(user_id, id_found)
                            attachment = bot.get_photo(id_found)
                            bot.send_msg(user_id, link_found, attachment=attachment)


                elif res == 'пока':
                    bot.send_msg(user_id,
                                 "Спасибо за использование сервиса. Всего доброго!")
                    break

                else:
                    bot.send_msg(user_id,   f'Вас приветствует бот VKinder! \n'
                                            f'Введите "поиск" - будем искать людей в вашем городе \n'
                                            f'в возрастном диапазон +2 и -2 года\n'
                                            f' от вашей даты рождения.\n'
                                            f' Если вы хотите искать по другим параметрам,\n'
                                            f' то введите команду "другое". \n'

                                            f' "Введите "далее", если хотите продолжить поиск. \n'
                                            f' "Введите "пока", если хотите закончить поиск. \n'
                                          )
interfase = Interface()

if __name__ == '__main__':
    interfase.handler()
        
