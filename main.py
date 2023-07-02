from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError
from config import access_token


class VkTools:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)
        self.searchYearRange = 1
        self.worksheetsPerPage = 3
        self.photosPerPage = 3

    def _get_birthday(self, birthdate):
        user_year = birthdate.split('.')[2]
        now = datetime.now().year
        return now - int(user_year)

    def _response_to_profile_info(self, info):
        return {
            'name': (info['first_name'] + ' ' + info['last_name']) if
            'first_name' in info and 'last_name' in info else None,
            'sex': info.get('sex'),
            'city': info.get('city')['title'] if info.get('city') is not None else None,
            'year': self._get_birthday(info.get('bdate'))
        }

    def get_profile_info(self, user_id):
        method_param = {
            'user_id': user_id,
            'fields': 'city, sex, relation, bdate'
        }

        try:
            info, = self.vkapi.method('users.get', method_param)
        except ApiError as error:
            info = {}
            print(f'error = {error}')

        return self._response_to_profile_info(info)

    def search_worksheet(self, params, offset):
        method_param = {
            'count': self.worksheetsPerPage,
            'offset': offset,
            'hometown': params['city'],
            'sex': 1 if params['sex'] == 2 else 2,
            'has_photo': True,
            'age_from': params['year'] - self.searchYearRange,
            'age_to': params['year'] + self.searchYearRange,
        }

        try:
            users = self.vkapi.method('users.search', method_param)
        except ApiError as error:
            users = []
            print(f'error = {error}')

        result = [{
            'name': item['first_name'] + " " + item['last_name'],
            'id': item['id']
        } for item in users['items'] if not item['is_closed']]

        return result

    def _recast_photo_to_local_format(self, photo):
        photo_recast = {}
        photo_recast['owner_id'] = photo['owner_id']
        photo_recast['id'] = photo['id']
        photo_recast['likes'] = photo['likes']['count']
        photo_recast['comments'] = photo['comments']['count']
        return photo_recast

    def get_photos(self, id):
        method_param = {
            'user_id': id,
            'album_id': 'profile',
            'extended': 1,
            'count': self.photosPerPage
        }

        try:
            photos = self.vkapi.method('photos.get', method_param)
            photos = photos['items']
        except KeyError:
            return []
        except ApiError as error:
            print(f'error = {error}')
            return []

        res = list(map(lambda photo: self._recast_photo_to_local_format(photo), photos))
        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)

        return res


if __name__ == '__main__':
    tools = VkTools(access_token)