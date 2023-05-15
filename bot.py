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
        creating_database()
        offset = 0
        id_list = []
        res_id = []
        id_person = []

        for event in bot.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                res = event.text.lower()
                user_id = event.user_id
                if res == "поиск":
                    bot.get_profile_info(user_id)
                    found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                    for profile in found_persons:
                        id = profile.get('id')
                        id_list.append(id)
                    id_person = check()
                    seen_person = [item for t in id_person for item in t]
                    res_id = list(set(id_list).difference(seen_person))
                    if res_id == []:
                        bot.send_msg(user_id, "Для дальнейшего поиска введите 1")
                    else:
                        id_found = res_id.pop()
                        link_found = str('vk.com/id' + str(id_found))
                        insert_data_search(user_id, id_found)
                        attachment = bot.get_photo(id_found)
                        bot.send_msg(user_id, link_found, attachment=attachment)
                        bot.send_msg(user_id, "Для дальнейшего поиска введите 1")


                elif res == "1":
                    if len(res_id) != 0:
                        id_found = res_id.pop()
                        link_found = str('vk.com/id' + str(id_found))
                        insert_data_search(user_id, id_found)
                        attachment = bot.get_photo(id_found)
                        bot.send_msg(user_id, link_found, attachment=attachment)
                        bot.send_msg(user_id, "Для дальнейшего поиска введите 1")

                    else:
                        offset = offset + 30
                        found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                        for profile in found_persons:
                            id = profile.get('id')
                            id_list.append(id)
                        id_person = check()
                        seen_person = [item for t in id_person for item in t]
                        res_id = list(set(id_list).difference(seen_person))
                        if res_id == []:
                            bot.send_msg(user_id, "Для дальнейшего поиска введите 1")
                        else:
                            id_found = res_id.pop()
                            link_found = str('vk.com/' + str(id_found))
                            insert_data_search(user_id, id_found)
                            attachment = bot.get_photo(id_found)
                            bot.send_msg(user_id, link_found, attachment=attachment)
                            bot.send_msg(user_id, "Для дальнейшего поиска введите 1")


                elif res == "другое":
                    bot.send_msg(user_id,
                                          f' Если вы хотите искать по другим параметрам,\n'
                                          f' то введите свой пол(м или ж), возрастной диапазон и город для поиска'
                                          f' в формате: м(ж)-25-29-Москва. \n')

                    self.input_data()
                    found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                    for profile in found_persons:
                        id = profile.get('id')
                        id_list.append(id)
                    id_person = check()
                    seen_person = [item for t in id_person for item in t]
                    res_id = list(set(id_list).difference(seen_person))
                    if res_id == []:
                        bot.send_msg(user_id, "Для дальнейшего поиска введите 2")
                    else:
                        id_found = res_id.pop()
                        link_found = str('vk.com/id' + str(id_found))
                        insert_data_search(user_id, id_found)
                        attachment = bot.get_photo(id_found)
                        bot.send_msg(user_id, link_found, attachment=attachment)
                        bot.send_msg(user_id, "Для дальнейшего поиска введите 2")


                elif res == '2':
                    if len(res_id) != 0:
                        id_found = res_id.pop()
                        link_found = str('vk.com/id' + str(id_found))
                        insert_data_search(user_id, id_found)
                        attachment = bot.get_photo(id_found)
                        bot.send_msg(user_id, link_found, attachment=attachment)
                        bot.send_msg(user_id, "Для дальнейшего поиска введите 2")

                    else:
                        offset = offset + 30
                        found_persons = bot.users_search(bot.city_title, bot.sex, bot.age_from, bot.age_to, offset)
                        for profile in found_persons:
                            id = profile.get('id')
                            id_list.append(id)
                        id_person = check()
                        seen_person = [item for t in id_person for item in t]
                        res_id = list(set(id_list).difference(seen_person))
                        if res_id == []:
                            bot.send_msg(user_id, "Для дальнейшего поиска введите 2")
                        else:
                            id_found = res_id.pop()
                            link_found = str('vk.com/' + str(id_found))
                            insert_data_search(user_id, id_found)
                            attachment = bot.get_photo(id_found)
                            bot.send_msg(user_id, link_found, attachment=attachment)
                            bot.send_msg(user_id, "Для дальнейшего поиска введите 2")

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

                                            f' "Введите "1", если хотите продолжить поиск. \n'
                                            f' "Введите "пока", если хотите закончить поиск. \n'
                                          )
interfase = Interface()

if __name__ == '__main__':
    interfase.handler()
