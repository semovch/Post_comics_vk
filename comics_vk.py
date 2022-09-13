import os
import argparse

import requests
import random

from dotenv import load_dotenv


def get_random_comic_stat():
    response_current = requests.get('https://xkcd.com/info.0.json')
    current_num = response_current.json()['num']
    random_num = random.randint(1, current_num)
    random_url = f'https://xkcd.com/{random_num}/info.0.json'
    response = requests.get(random_url)
    response.raise_for_status()
    return response.json()


def wall_upload(vk_token):    
    params_wall_upload = {
        'access_token': vk_token,
        'group_id': 215862413,
        'v': '5.131'
            }
    wall_upload_response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params_wall_upload)
    return(wall_upload_response.json())


def wall_save(vk_token,filename,dir_path):
    with open(os.path.join(dir_path, filename), 'rb') as file:
        url = wall_upload(vk_token)['response']['upload_url']
        server_params = {
            'group_id': 215862413
                }
        files = {
            'photo': file
                }
        server_response = requests.post(url, files=files, params=server_params)
        server_response.raise_for_status()    
    wall_save_params = {
        'photo': server_response.json()['photo'],
        'group_id': 215862413,
        'access_token': vk_token,
        'server': server_response.json()['server'],
        'hash': server_response.json()['hash'],
        'v': '5.131'
            }
    wall_save_response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=wall_save_params)
    wall_save_response.raise_for_status
    return wall_save_response.json()


def wall_post(vk_token,filename,dir_path):
    own_id = wall_save(vk_token,filename,dir_path)['response'][0]['owner_id']
    media_id = wall_save(vk_token,filename,dir_path)['response'][0]['id']

    wall_post_params = {
        'owner_id': -215862413,
        'from_group': 1,
        'message': get_comics()['alt'],
        'access_token': vk_token,
        'v': '5.131',
        'attachments': f'photo{own_id}_{media_id}'
            }

    wall_post_response = requests.post('https://api.vk.com/method/wall.post', params=wall_post_params)
    return(wall_post_response.json())


def main():
    load_dotenv('.env')
    vk_token = os.environ['VK_TOKEN']
    parser = argparse.ArgumentParser(
        description='публикация комикса'
    )
    parser.add_argument('dir_path', help='введите путь к нужной директории')
    parser.add_argument('filename', help='введите название комикса')
    args = parser.parse_args()
    dir_path = args.dir_path
    filename = args.filename
    img_url = get_random_comic_stat()['img']
    response_img = requests.get(img_url)
    response_img.raise_for_status()
    with open(os.path.join(dir_path,filename), 'wb') as file:
        file.write(response_img.content)
    print(wall_post(vk_token,filename,dir_path))
    os.remove(dir_path +'/'+ filename)


if __name__ == '__main__':
    main()

