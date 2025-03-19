import requests
import hashlib
import random
import os
import configparser
from GPT import gpt

try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()

images_directory = os.path.join(game_directory, "images")
config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')
lang = config.get('剧情', 'language')

language = "zh" if lang == "中文" else "en" if lang == "英文" else "jp"

appid = 'xxxx'
secret_key = 'xxx'
url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'


def translate_baidu(text, from_lang='zh', to_lang=language):
    """百度翻译API"""
    if from_lang == to_lang:
        return text
    salt = random.randint(32768, 65536)
    sign = appid + text + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    response = requests.get(url, params=params)
    result = response.json()
    return result['trans_result'][0]['dst']


def translate_gpt(text, from_lang='zh', to_lang=language):
    global lang
    if from_lang == to_lang:
        return text
    response = gpt("你是一名翻译专家", f"请你帮我把这一句翻译成{lang},你直接输出译文即可:{text}")
    return response
