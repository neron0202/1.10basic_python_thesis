import requests
from pprint import pprint
from datetime import datetime

class VKPhotosLoader:

    def __init__(self):
        with open('token_vk.txt', 'r') as file:
            self.token_vk = file.read().strip()

    def inputUserID(self, user_id='1'):
        with open('user_id_vk.txt', 'r') as file:
            self.user_id= file.read()
        return self.user_id

    def getPhotosVK(self):
        url_vk = 'https://api.vk.com/method/photos.get'
        params = {
                 'user_id': self.inputUserID(),
                 'access_token': self.token_vk,
                 'v': '5.131',
                 'album_id': 'profile',
                 'extended': 1,
        }
        vk_photo_info = requests.get(url_vk, params).json()
        return vk_photo_info


class YaDisk:
    def __init__(self):
        with open('token_ya.txt', 'r') as file:
            self.token = file.read().strip()

    def getHeaders(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def getParams(self, num_of_photos=5):
        largest_photos_list = []
        num_of_photos = int(input("Введите количество фото: "))
        for photos_list in VKPhotosLoader().getPhotosVK().values():
            for photo_number in range(len(photos_list['items'])):
                w_h_photo = -1
                photos_sizes_list = photos_list['items'][photo_number]['sizes']
                largest_photo_likes = photos_list['items'][photo_number]['likes']['count']
                largest_photo_date = photos_list['items'][photo_number]['date']
                for photo in photos_sizes_list:
                    photo_square = photo['width'] * photo['height']
                    if photo_square > w_h_photo:
                        size_photo = photo_square
                        largest_photo_url = photo['url']
                        largest_photo_type = photo['type']
                largest_photos_list.append((size_photo, largest_photo_likes, largest_photo_date, largest_photo_type,  largest_photo_url))
        largest_photos_list.sort(reverse=True)
        largest_photos_list = largest_photos_list[:num_of_photos]
        return largest_photos_list

    def checkCurrentTime(self):
        current_datetime = datetime.now()
        current_datetime = f"{current_datetime.day}{current_datetime.hour}{current_datetime.minute}"
        return current_datetime

    def createFolder(self):
        url_fold_create_ya = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            "path": f"{self.checkCurrentTime()}_ID{VKPhotosLoader().inputUserID()}"
        }
        creation =requests.put(url=url_fold_create_ya, params=params, headers=self.getHeaders())
        return creation.json()

    def uploadPhoto(self):
        files_name_list = []
        url_ya = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        self.createFolder()
        for photo_tuple in self.getParams():
            print("█", end='')
            params = {
                "path": f'{self.checkCurrentTime()}_ID{VKPhotosLoader().inputUserID()}/{photo_tuple[1]}',
                "overwrite": "true",
                "url": photo_tuple[4]
            }
            if photo_tuple[1] in files_name_list:
                params["path"] = f'{self.checkCurrentTime()}_ID{VKPhotosLoader().inputUserID()}/{photo_tuple[1]}_{photo_tuple[2]}'
            files_name_list.append(photo_tuple[1])
            upload = requests.post(url=url_ya, params=params, headers=self.getHeaders())
            upload2 = upload.json()
        print()
        return upload2


obj = VKPhotosLoader()
# pprint(obj.getPhotosVK())
# pprint(obj.getPhotosVK())
# print(obj.inputUserID())
# print('-------------------------------')
# pprint(obj.filterLargePhotos())
# print("obj2.inputUserID(()=", obj.inputUserID())
# print("obj2.inputUserID(()=", obj.getPhotosVK())
obj2 = YaDisk()
# print("obj2.getHeaders()=", obj2.getHeaders())
# print("obj2.getParams()=", obj2.getParams())
# print("obj2.createFolder(()=", obj2.createFolder())
# print(obj2.checkCurrentTime())
print("obj2.uploadPhoto(()=", obj2.uploadPhoto())


