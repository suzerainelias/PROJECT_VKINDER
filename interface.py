import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import community_token, access_token, data_base_url
from main import VkTools
from data import user_check, add_database_user
from sqlalchemy import create_engine

class BotInterface:
    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(access_token)
        self.longpoll = VkLongPoll(self.interface)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()}
                              )
    def request_info(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event.text

    def int_check(self, num):
        try:
            int(num)
        except (TypeError, ValueError):
            return False
        else:
            return True

    # Найденное совпадение добавляется в базу данных
    def send_user_from_worksheet(self, worksheet, event):
        if not user_check(engine, event.user_id, worksheet["id"]):
            add_database_user(engine, event.user_id, worksheet["id"])
            photos = self.api.get_photos(worksheet['id'])
            photo_string = ''
            for photo in photos:
                photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
            self.message_send(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/id{worksheet["id"]}',
                              attachment=photo_string)

    # Разведопрос
    def hard_work(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'начать':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Программа запущена, {self.params["name"]}!')
                    if self.params['year'] is None:
                        self.message_send(event.user_id, f'Укажите возраст')
                        age = (self.request_info())
                        while not self.int_check(age):
                            self.message_send(event.user_id, f'Введите корректный возраст')
                            age = (self.request_info())
                        self.params['year'] = int(age)
                    if self.params['city'] is None:
                        self.message_send(event.user_id, f'Укажите город')
                        self.params['city'] = self.request_info()
                    self.message_send(event.user_id, f'Введите "найти", чтобы найти пару')
                elif event.text.lower() == 'найти':
                    self.message_send(event.user_id, 'Начинаю поиск')
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        self.send_user_from_worksheet(worksheet, event)
                    else:
                        self.worksheets = self.api.search_worksheet(self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        self.send_user_from_worksheet(worksheet, event)
                        self.offset += 10

                elif event.text.lower() == 'закончить':
                    self.message_send(event.user_id,'До новых встреч')
                else:
                    self.message_send(event.user_id, 'Произошла ошибка, попробуйте другую комманду')


if __name__ == '__main__':
    engine = create_engine(data_base_url)
    bot_interface = BotInterface(community_token, access_token)
    bot_interface.hard_work()