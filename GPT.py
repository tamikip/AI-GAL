import requests
import configparser
import re
import json
import os

try:
    import renpy

    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()

config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')

import json
import requests
import re


def gpt(system, prompt, mode="common", history=None):
    gpt_key = config.get('CHATGPT', 'GPT_KEY')
    gpt_url = config.get('CHATGPT', 'BASE_URL')
    model = config.get('CHATGPT', 'model')

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    # 如果有历史对话，并且是上下文模式，将历史对话和当前对话合并
    if mode == "context" and history:
        messages = history + messages  # 将历史消息和当前消息合并

    payload = json.dumps({
        "model": model,
        "messages": messages
    })

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {gpt_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.post(gpt_url, headers=headers, data=payload)
    content = json.loads(response.text)['choices'][0]['message']['content']

    # 去除思考模型的部分
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    return content

