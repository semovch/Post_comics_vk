import os

import requests
import random
import urllib.parse

from dotenv import load_dotenv


def get_random_comic_stat():
    response_current = requests.get('https://xkcd.com/info.0.json')
    current_num = response_current.json()['num']
    random_num = random.randint(1, current_num)
    random_url = f'https://xkcd.com/{random_num}/info.0.json'
    response = requests.get(random_url)
    response.raise_for_status()
    decoded_response = response.json()
    return decoded_response['img'], decoded_response['alt']


def upload_comic(vk_token, vk_group_id, filename):    
    params_wall_upload = {
        'access_token': vk_token,
        'group_id': vk_group_id,
        'v': '5.131'
    }
    upload_comic_response = requests.get('https://api.vk.com/method/photos.getWallUploadServer',
                                         params=params_wall_upload)
    upload_comic_response.raise_for_status()
    upload_url = upload_comic_response.json()['response']['upload_url']
    with open(os.path.join(filename), 'rb') as file:
        server_params = {
            'group_id': vk_group_id
        }
        files = {
            'photo': file
        }
        server_response = requests.post(upload_url,
                                        files=files, params=server_params)
    try:
        pass
    finally:
        os.remove(filename)
    server_response.raise_for_status()
    decoded_server_response = server_response.json()
    return decoded_server_response['photo'], decoded_server_response['server'], decoded_server_response['hash']


def save_comic(vk_token, filename, vk_group_id, photo, server, server_hash):
    save_to_wall_params = {
        'photo': photo,
        'group_id': vk_group_id,
        'access_token': vk_token,
        'server': server,
        'hash': server_hash,
        'v': '5.131'
    }
    save_comic_response = requests.post('https://api.vk.com/method/photos.saveWallPhoto',
                                        params=save_to_wall_params)
    save_comic_response.raise_for_status()
    save_comic_stat = save_comic_response.json()
    return save_comic_stat['response'][0]['owner_id'], save_comic_stat['response'][0]['id']


def post_comic(vk_token, filename, vk_group_id, comment, own_id, media_id):
    post_to_wall_params = {
        'owner_id': -vk_group_id,
        'from_group': 1,
        'message': comment,
        'access_token': vk_token,
        'v': '5.131',
        'attachments': f'photo{own_id}_{media_id}'
    }

    post_comic_response = requests.post('https://api.vk.com/method/wall.post',
                                        params=post_to_wall_params)
    post_comic_response.raise_for_status()
    return post_comic_response.json()


def main():
    load_dotenv('.env')
    vk_token = os.environ['VK_TOKEN']
    vk_group_id = int(os.environ['VK_GROUP_ID'])
    img_url, comment = get_random_comic_stat()
    filename = os.path.basename(img_url)
    response_img = requests.get(img_url)
    response_img.raise_for_status()
    with open(os.path.join(filename), 'wb') as file:
        file.write(response_img.content) 
    photo, server, server_hash = upload_comic(vk_token, vk_group_id, filename)
    own_id, media_id = save_comic(vk_token, filename, vk_group_id, photo, server, server_hash)
    print(post_comic(vk_token, filename, vk_group_id, comment, own_id, media_id))


if __name__ == '__main__':
    main()
