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


def upload_to_wall(vk_token, vk_group_id):    
    params_wall_upload = {
        'access_token': vk_token,
        'group_id': vk_group_id,
        'v': '5.131'
            }
    upload_to_wall_response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params_wall_upload)
    upload_to_wall_response.raise_for_status()
    return upload_to_wall_response.json()


def save_to_wall(vk_token,filename,dir_path,vk_group_id,decoded_server_response):
    save_to_wall_params = {
        'photo': decoded_server_response['photo'],
        'group_id': vk_group_id,
        'access_token': vk_token,
        'server': decoded_server_response['server'],
        'hash': decoded_server_response['hash'],
        'v': '5.131'
            }
    save_to_wall_response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=save_to_wall_params)
    save_to_wall_response.raise_for_status()
    return save_to_wall_response.json()


def post_to_wall(vk_token,filename,dir_path,vk_group_id,comment,decoded_server_response):
    save_to_wall_stat = save_to_wall(vk_token,filename,dir_path,vk_group_id,decoded_server_response)['response'][0]
    own_id = save_to_wall_stat['owner_id']
    media_id = save_to_wall_stat['id']

    post_to_wall_params = {
        'owner_id': -vk_group_id,
        'from_group': 1,
        'message': comment,
        'access_token': vk_token,
        'v': '5.131',
        'attachments': f'photo{own_id}_{media_id}'
            }

    post_to_wall_response = requests.post('https://api.vk.com/method/wall.post', params=post_to_wall_params)
    post_to_wall_response.raise_for_status()
    return post_to_wall_response.json()


def main():
    load_dotenv('.env')
    decoded_random_comic_stat = get_random_comic_stat()
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
    img_url = decoded_random_comic_stat['img']
    comment = decoded_random_comic_stat['alt']
    response_img = requests.get(img_url)
    response_img.raise_for_status()
    upload_url = upload_to_wall(vk_token,vk_group_id)['response']['upload_url']
    
    with open(os.path.join(dir_path,filename), 'wb') as file:
        file.write(response_img.content)
    with open(os.path.join(dir_path, filename), 'rb') as file:
        server_params = {
            'group_id': vk_group_id
                }
        files = {
            'photo': file
                }
        server_response = requests.post(upload_url, files=files, params=server_params)
    os.remove(f'{dir_path}/{filename}')
    server_response.raise_for_status()
    decoded_server_response = server_response.json()
    print(post_to_wall(vk_token,filename,dir_path,vk_group_id,comment,decoded_server_response))


if __name__ == '__main__':
    main()
