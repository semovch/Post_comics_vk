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
    return server_response.json()


def save_comic(vk_token, filename, vk_group_id, decoded_server_response):
    save_to_wall_params = {
        'photo': decoded_server_response['photo'],
        'group_id': vk_group_id,
        'access_token': vk_token,
        'server': decoded_server_response['server'],
        'hash': decoded_server_response['hash'],
        'v': '5.131'
    }
    save_comic_response = requests.post('https://api.vk.com/method/photos.saveWallPhoto',
                                        params=save_to_wall_params)
    save_comic_response.raise_for_status()
    return save_comic_response.json()


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
    decoded_server_response = upload_comic(vk_token, vk_group_id, filename)
    photo = decoded_server_response['photo']
    server = decoded_server_response['server']
    hash = decoded_server_response['hash']
    save_comic_stat = save_comic(vk_token, filename, vk_group_id, decoded_server_response)['response'][0]
    own_id = save_comic_stat['owner_id']
    media_id = save_comic_stat['id']
    print(post_comic(vk_token, filename, vk_group_id, comment, own_id, media_id))


if __name__ == '__main__':
    main()
