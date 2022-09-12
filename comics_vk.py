import os
import argparse

import requests
import random

from dotenv import load_dotenv


def get_comics():
    response_current = requests.get('https://xkcd.com/info.0.json')
    num_current = response_current.json()['num']
    random_num = random.randint(1, num_current)
    url_random = f'https://xkcd.com/{random_num}/info.0.json'
    response = requests.get(url_random)
    response.raise_for_status
    return response.json()


def wall_upload(vk_token):    
    params_wall_upload = {
        'access_token': vk_token,
        'group_id': 215862413,
        'v': '5.131'
            }
    response_wall_upload = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params_wall_upload)
    return(response_wall_upload.json())


def wall_save(vk_token,filename,dir_path):
    with open(os.path.join(dir_path, filename), 'rb') as file:
        url = wall_upload(vk_token)['response']['upload_url']
        params_server = {
            'group_id': 215862413
                }
        files = {
            'photo': file
                }
        response_server = requests.post(url, files=files, params=params_server)
        response_server.raise_for_status()    
    params_wall_save = {
        'photo': response_server.json()['photo'],
        'group_id': 215862413,
        'access_token': vk_token,
        'server': response_server.json()['server'],
        'hash': response_server.json()['hash'],
        'v': '5.131'
            }
    response_wall_save = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params_wall_save)
    return response_wall_save.json()


def wall_post(vk_token,filename,dir_path):
    own_id = wall_save(vk_token,filename,dir_path)['response'][0]['owner_id']
    media_id = wall_save(vk_token,filename,dir_path)['response'][0]['id']

    params_wall_post = {
        'owner_id': -215862413,
        'from_group': 1,
        'message': get_comics()['alt'],
        'access_token': vk_token,
        'v': '5.131',
        'attachments': f'photo{own_id}_{media_id}'
            }

    response_wall_post = requests.post('https://api.vk.com/method/wall.post', params=params_wall_post)
    return(response_wall_post.json())


def main():
    load_dotenv('.env')
    vk_token = os.environ['VK_TOKEN']
    #dir_path = 'Документы/GitHub'
    #filename = 'comics_python.png'
    parser = argparse.ArgumentParser(
        description='публикация комикса'
    )
    parser.add_argument('dir_path', help='введите путь к нужной директории')
    parser.add_argument('filename', help='введите название комикса')
    args = parser.parse_args()
    dir_path = args.dir_path
    filename = args.filename
    url_img = get_comics()['img']
    response_img = requests.get(url_img)
    response_img.raise_for_status()
    with open(os.path.join(dir_path,filename), 'wb') as file:
        file.write(response_img.content)
    print(wall_post(vk_token,filename,dir_path))
    os.remove(dir_path +'/'+ filename)


if __name__ == '__main__':
    main()

