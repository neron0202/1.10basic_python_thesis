import requests
import json
from pprint import pprint
from datetime import datetime
import time

class VKPhotosLoader:

    def __init__(self, token_vk, vk_user_id, num_of_photos=5, url_vk='https://api.vk.com/method/photos.get'):
        self.token_vk = token_vk
        self.vk_user_id = vk_user_id
        self.num_of_photos = num_of_photos
        self.url_vk = 'https://api.vk.com/method/photos.get'

    def get_avatars_VK(self):
        params = {
                 'user_id': self.vk_user_id,
                 'access_token': self.token_vk,
                 'v': '5.131',
                 'album_id': 'profile',
                 'extended': 1,
        }
        vk_avatars_info = requests.get(self.url_vk, params).json()
        return vk_avatars_info

    def get_wall_photos_VK(self):
        photos_list = []
        params = {
                 'user_id': self.vk_user_id,
                 'access_token': self.token_vk,
                 'v': '5.131',
                 'album_id': 'wall',
                 'extended': 1,
        }
        wall_photos_vk = requests.get(self.url_vk, params).json()
        for post_dict in wall_photos_vk.values():
            for photos_info_dict in post_dict['items']:
                wall_photo_likes = photos_info_dict['likes']['count']
                for photo_info_list in photos_info_dict['sizes']:
                    if photo_info_list['type'] == 's':
                        wall_photo_url = photo_info_list['url']
                        photos_list.append((wall_photo_url, wall_photo_likes))
        photos_list = photos_list[:self.num_of_photos]
        return photos_list

    def get_largest_photos(self):
        largest_photos_list = []
        for photos_list in self.get_avatars_VK().values():
            for avatar_info in self.get_avatars_VK()['response']['items']:
                w_h_photo = -1  # width and height of photo. По-умолчанию задано как (-1)
                photos_sizes_list = avatar_info['sizes']
                largest_photo_likes = avatar_info['likes']['count']
                largest_photo_date = avatar_info['date']
                for photo in photos_sizes_list:
                    photo_square = photo['width'] * photo['height']
                    if photo_square > w_h_photo:
                        size_photo = photo_square
                        largest_photo_url = photo['url']
                        largest_photo_type = photo['type']
                largest_photos_list.append((size_photo, largest_photo_likes, largest_photo_date, largest_photo_type,  largest_photo_url))
            largest_photos_list.sort(reverse=True)
            largest_photos_list = largest_photos_list[:self.num_of_photos]
            return largest_photos_list

class YaDisk:
    def __init__(self, token_ya, vk_user_id, vk_photo_loader, url_fold_create_ya='https://cloud-api.yandex.net/v1/disk/resources'):
        self.token_ya = token_ya
        self.folder_identificator = vk_user_id
        self.vk_photo_loader = VKPhotosLoader(token_vk, vk_user_id, num_of_photos)
        self.url_fold_create_ya = 'https://cloud-api.yandex.net/v1/disk/resources'

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token_ya)
        }

    def create_folder(self):
        params = {
            "path": f"{get_current_time()}_ID{self.folder_identificator}"
        }
        creation = requests.put(url=self.url_fold_create_ya, params=params, headers=self.get_headers())
        return creation.raise_for_status()

    def upload_photo(self):
        files_name_list_ava = []
        files_name_list_wall = []
        list_for_json = []
        url_ya = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.create_folder()
        for photo_tuple in self.vk_photo_loader.get_largest_photos():
            dict_for_json = {}
            params = {
                "path": f'{get_current_time()}_ID{self.folder_identificator}/{photo_tuple[1]}',
                "overwrite": "true",
                "url": photo_tuple[4]
            }
            if photo_tuple[1] in files_name_list_ava:
                params["path"] = f'{get_current_time()}_ID/{photo_tuple[1]}_{photo_tuple[2]}'
            files_name_list_ava.append(photo_tuple[1])
            upload = requests.post(url=url_ya, params=params, headers=self.get_headers())
            upload.raise_for_status()
            print('avatar upload:', upload.json())
            dict_for_json['file_name'] = f'{photo_tuple[1]}.jpg'
            dict_for_json['size'] = photo_tuple[3]
            list_for_json.append(dict_for_json)

        wall_photos_counter = 0
        for wall_photo in self.vk_photo_loader.get_wall_photos_VK():
            dict_for_json = {}
            params = {
                "path": f'{get_current_time()}_ID{self.folder_identificator}/wall_{wall_photo[1]}',
                "overwrite": "true",
                "url": wall_photo[0]
            }

            if wall_photo[1] in files_name_list_wall:
                params["path"] = f'{get_current_time()}_ID/{wall_photo[1]}'
            wall_photos_counter += 1
            upload = requests.post(url=url_ya, params=params, headers=self.get_headers())
            print('wall photo upload: ', upload.json())
            dict_for_json['file_name'] = f'wall_{wall_photo[1]}.jpg'
            dict_for_json['size'] = 's'
            list_for_json.append(dict_for_json)

        with open('photos.json', 'w') as file:
            json.dump(list_for_json, file, indent=2, ensure_ascii=False)
        return upload.json()


def get_current_time():
    current_datetime = datetime.strftime(datetime.now(), "%d%H%M")
    return current_datetime


if __name__ == '__main__':
    token_vk = input('Введите токен VK: ')
    vk_user_id = input('Введите userID в VK: ')
    token_ya = input('Введите токен Yandex\'а: ')
    num_of_photos = int(input('Введите количество загружаемых фото: '))
    obj = VKPhotosLoader(token_vk, vk_user_id, num_of_photos)
    obj2 = YaDisk(token_ya, vk_user_id, obj)
    print(obj2.upload_photo())

