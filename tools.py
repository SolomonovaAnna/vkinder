from vk_api.longpoll import VkLongPoll
import datetime
import vk_api
from vk_api.utils import get_random_id
from config import access_token, comunity_token




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

        self.city_title = info[0]['city']["title"]
        date = info[0].get('bdate')
        year = int(date.split('.')[2])
        year_now = int(datetime.date.today().year)
        age = year_now - year
        self.age_from = age - 2
        self.age_to = age + 2
        self.sex = info[0]['sex']
        if self.sex == 1:
            self.sex = 2
        elif self.sex == 2:
            self.sex = 1
        else:
            print("Ошибка!")

        return self.city_title, self.sex, self.age_from, self.age_to


    # ищем пользователей, удовлетворяющих запросам юзера, и сохраняем ссылки на них в список
    # id  найденных пользователей сохраняем в БД

    def users_search(self, city_title, sex, age_from, age_to, offset):

        res = self.vk_user_got_api.users.search(
            hometown=city_title,
            sex=sex,
            status=1,
            age_from=age_from,
            age_to=age_to,
            has_photo=1,
            count=30,
            offset=offset,
            fields="can_write_private_message, "  
                   "city, "    
                   "home_town,"
                   "domain, "
        )

        list_found_persons = []
        for person in res["items"]:
            if not person["is_closed"]:
                if "city" in person and person["city"]["title"] == city_title:
                    list_found_persons.append({'link': str('vk.com/' + str(person['domain'])), 'id': person['id']})


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
        try:
            attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[1]))
            attachments.append('photo{}_{}'.format(user_id, photo_ids[2]))
            return attachments
        except IndexError:
            try:
                attachments.append('photo{}_{}'.format(user_id, photo_ids[0]))
                return attachments
            except IndexError:
                return print(f'Нет фото')


    


bot = Bot()

