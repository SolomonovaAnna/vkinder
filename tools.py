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
        self.sex = 0
        self.age_from = 0
        self.age_to = 0
        self.city_id = 0
        self.city_title = 0

    # функция отправки сообщений, в том числе с медиа вложением
    def send_msg(self, user_id, message, attachment=None):
        self.vk_group_got_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id(),
            attachment=attachment
        )

    def get_profile_info(self, user_id):

        info = self.vk_user_got_api.users.get(
                                            user_id=user_id,
                                            fields="bdate,city,sex")

        self.send_msg(user_id,
                      f' Введите "ок" - будем искать людей в вашем городе и в возрастном диапазон +2 и -2 года'
                      f' от вашей даты рождения.'
                      f' Если вы хотите искать по другим параметрам,'
                      f' то введите свой возрастной диапазон и город для поиска'
                      f' в формате: 25-29-Москва.'

                      )

        for i in info:
            if i['sex'] == 1:
                self.sex = 2
            elif i['sex'] == 2:
                self.sex = 1
            else:
                print("Ошибка!")

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                if answer == "ок":
                    self.city_id = info[0]['city']["id"]
                    self.city_title = info[0]['city']["title"]
                    date = info[0]['bdate']
                    date_list = date.split('.')
                    if len(date_list) == 3:
                        year = int(date_list[2])
                        year_now = int(datetime.date.today().year)
                        age = year_now - year
                        self.age_from = age - 2
                        self.age_to = age + 2
                        return
                else:
                    a = answer.split("-")
                    self.age_from = int(a[0])
                    self.age_to = int(a[1])

                    cities = self.vk_user_got_api.database.getCities(
                                country_id=1,
                                q=answer.capitalize(),
                                need_all=1,
                                count=1000
                        )['items']
                    for i in cities:
                        if i["title"] == (a[2]):
                            self.city_id = i["id"]
                            self.city_title = int(i[1])

        return


    # ищем пользователей, удовлетворяющих запросам юзера, и сохраняем ссылки на них в список
    # id  найденных пользователей сохраняем в БД

    def users_search(self, offset=None):
        list_found_persons = []
        res = self.vk_user_got_api.users.search(
            city=self.city_id,
            hometown=self.city_title,
            sex=self.sex,
            status=1,
            age_from=self.age_from,
            age_to=self.age_to,
            has_photo=1,
            count=30,
            offset=offset,
            fields="can_write_private_message, "  
                   "city, "    
                   "home_town,"
                   "domain, "
        )


        for person in res["items"]:
            if not person["is_closed"]:
                if "city" in person and person["city"]["id"] == self.city_id and person["city"]["title"] == self.city_title:
                    vk_id = int(person['id'])
                    # name = str(person['first_name'] + ' ' + person['last_name'])
                    link = str('vk.com/' + str(person['domain']))
                    insert_data_search(vk_id)
                    list_found_persons.append(link)

        return list_found_persons


    # возвращает 3 лучших(лайки+комменты) фото найденного пользователя
    def get_photo(self, user_id):
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

