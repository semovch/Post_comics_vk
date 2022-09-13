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


def wall_upload(vk_token, vk_group_id):    
    params_wall_upload = {
        'access_token': vk_token,
        'group_id': vk_group_id,
        'v': '5.131'
            }
    wall_upload_response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params_wall_upload)
    wall_upload_response.raise_for_status()
    return(wall_upload_response.json())


def wall_save(vk_token,filename,dir_path, vk_group_id):
    url = wall_upload(vk_token,vk_group_id)['response']['upload_url']
    with open(os.path.join(dir_path, filename), 'rb') as file:
        server_params = {
            'group_id': vk_group_id
                }
        files = {
            'photo': file
                }
    server_response = requests.post(url, files=files, params=server_params)
    server_response.raise_for_status()
    decoded_server_response = server_response.json()
    wall_save_params = {
        'photo': decode_server_response['photo'],
        'group_id': vk_group_id,
        'access_token': vk_token,
        'server': decoded_server_response['server'],
        'hash': decoded_server_response['hash'],
        'v': '5.131'
            }
    wall_save_response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=wall_save_params)
    wall_save_response.raise_for_status()
    return wall_save_response.json()


def wall_post(vk_token,filename,dir_path, vk_group_id):
    own_id = wall_save(vk_token,filename,dir_path)['response'][0]['owner_id']
    media_id = wall_save(vk_token,filename,dir_path)['response'][0]['id']

    wall_post_params = {
        'owner_id': -vk_group_id,
        'from_group': 1,
        'message': get_comics()['alt'],
        'access_token': vk_token,
        'v': '5.131',
        'attachments': f'photo{own_id}_{media_id}'
            }

    wall_post_response = requests.post('https://api.vk.com/method/wall.post', params=wall_post_params)
    wall_post_response.raise_for_status()
    return(wall_post_response.json())


def main():
    load_dotenv('.env')
    vk_token = os.environ['VK_TOKEN']
    vk_group_id = int(os.environ['VK_GROUP_ID'])
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
    os.remove(f'{dir_path}/{filename}')


if __name__ == '__main__':
    main()

