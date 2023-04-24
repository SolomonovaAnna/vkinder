from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import vk_api
from vk_api.utils import get_random_id
from config import access_token, comunity_token
from database import check, insert_data_search



class Bot:
    def __init__(self):
        self.vk_user = vk_api.VkApi(token=access_token)
        self.vk_user_got_api = self.vk_user.get_api()
        self.vk_group = vk_api.VkApi(token=comunity_token)
        self.vk_group_got_api = self.vk_group.get_api()
        self.longpoll = VkLongPoll(self.vk_group)

    # функция отправки сообщений, в том числе с медиа вложением
    def send_msg(self, user_id, message, attachment=None):
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id(),
            attachment=attachment
        )


    # запрашиваем возрастной диапазон для поиска
    def input_age(self, user_id, age):
        global age_from, age_to
        a = age.split("-")
        try:
            age_from = int(a[0])
            age_to = int(a[1])
            if age_from == age_to:
                self.send_msg(user_id, {age_to, False})
                return
            self.send_msg(user_id, f' Ищем возраст в пределах от {age_from} и до {age_to}')
            return
        except IndexError:

            return 'Неправильный формат ввода возраста'

    # ищем пользователей на 2 года старше и младше от возраста юзера, пользующегося ботом.
    # или юзер вводит интересующий его возрастной интервал
    def get_age(self, user_id):
        global age_from, age_to
        try:
            self.send_msg(user_id,
                          f' Введите "ок" - будем искать людей в возрастном диапазон +2 и -2 года от вашей даты рождения.'
                          f' Или введите возраст поиска в формате : 21-35'
                          )
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    answer = event.text.lower()
                    if answer == "ок":
                        info = self.vk_user_got_api.users.get(
                                        user_id=user_id,
                                        fields="bdate",)
                        date = info[0]['bdate']
                        date_list = date.split('.')
                        if len(date_list) == 3:
                            year = int(date_list[2])
                            year_now = int(datetime.date.today().year)
                            age = year_now - year
                            age_from = age - 2
                            age_to = age + 2
                            return

                    else:
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                age = event.text
                                return self.input_age(user_id, age)
        except:
            return'Неправильный формат ввода'

    # запрашиваем город, в котором будет осуществлен поиск
    # или бот ищет в городе юзера
    def get_city(self, user_id):
        global city_id, city_title
        self.send_msg(user_id,
                      f' Введите "да" и пару будем искать в вашем городе.'
                      f' Или введите название города, например: Москва'
                      )
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "да":
                    info = self.vk_user_got_api.users.get(
                        user_id=user_id,
                        fields="city"
                    )
                    city_id = info[0]['city']["id"]
                    city_title = info[0]['city']["title"]
                    return f' в городе {city_title}.'
                else:
                    cities = self.vk_user_got_api.database.getCities(
                        country_id=1,
                        q=answer.capitalize(),
                        need_all=1,
                        count=1000
                    )['items']
                    for i in cities:
                        if i["title"] == answer.capitalize():
                            city_id = i["id"]
                            city_title = answer.capitalize()
                            return f' в городе {city_title}'

    # в зависимости от пола юзера ищем людей противоположного пола
    def get_sex(self, user_id):
        global sex
        info = self.vk_user_got_api.users.get(
            user_id=user_id,
            fields="sex"
        )
        for i in info:
            if i['sex'] == 1:
                sex = 2
            elif i['sex'] == 2:
                sex = 1
            else:
                print("Ошибка!")
        return sex


    # ищем пользователей, удовлетворяющих запросам юзера, и сохраняем ссылки на них в список
    # id  найденных пользователей сохраняем в БД
    def users_search(self, offset=None):
        global list_found_persons
        list_found_persons = []
        res = self.vk_user_got_api.users.search(
            city=city_id,
            hometown=city_title,
            sex=sex,
            status=1,
            age_from=age_from,
            age_to=age_to,
            has_photo=1,
            count=5,
            offset=offset,
            fields="can_write_private_message, "  
                   "city, "    
                   "home_town,"
                   "domain, "
        )


        for person in res["items"]:
            if not person["is_closed"]:
                if "city" in person and person["city"]["id"] == city_id and person["city"]["title"] == city_title:
                    if not person in check():
                        vk_id = int(person['id'])
                        # name = str(person['first_name'] + ' ' + person['last_name'])
                        link = str('vk.com/' + str(person['domain']))
                        insert_data_search(vk_id)
                        list_found_persons.append(link)

        return list_found_persons

    # сдвигаем offset для нового списка пользователей
    def move_offset(self):
        global offset
        offset = 0
        offset += 30
        return offset

    # возвращает 3 лучших(лайки+комменты) фото найденного пользователя
    def get_photo(self, user_id):
        global attachments
        attachments = []
        photos = self.vk_user_got_api.photos.get(
                                             owner_id=user_id,
                                             album_id='profile',
                                             extended=1,
                                             count=30
                                             )

        top_photo = []
        for photo in photos["items"]:
            top_photo.append({'top': photo['likes']['count'] + photo['comments']['count'],
                              'owner_id': photo['owner_id'], 'id': photo['id']})
            top_photo = sorted(top_photo, key=lambda x: x['top'], reverse=True)
        for num, items in enumerate(top_photo):
            top_photo.append({'owner_id': (items['owner_id']), 'id': (items['id'])})
            if num == 2:
                break

        photo_ids = []
        for i in top_photo:
            photo_ids.append(i['id'])
        attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
        attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
        attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
        return attachments


    # запрашиваем из бд id найденных пользователей
    def get_profile_id(self):
        global id_list
        list_person = []
        id_list = []
        for i in check():
            list_person.append(i)
        for element in range(len(list_person)):
            list_person[element] = int(list_person[element][0])
            id_list.append(list_person[element])
        return id_list

    def show_found_person(self, user_id):
        for id in self.get_profile_id():
            link = str('vk.com/id' + str(id))
            self.send_msg(user_id, link, self.get_photo(id))


bot = Bot()

if __name__ == '__main__':
    bot.show_found_person()
