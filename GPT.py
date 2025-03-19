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

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config.get("CHATGPT", "GPT_KEY")}'
}


def gpt(system, prompt, json_mode=False):
    """普通的gpt调用"""
    gpt_url = config.get('CHATGPT', 'BASE_URL')
    model = config.get('CHATGPT', 'model')
    response_format = {'type': 'json_object'}
    if json_mode:
        json_mode = config.getboolean("Settings", "json_mode")

    messages = []
    if system is not None:
        messages.append({
            "role": "system",
            "content": system
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    payload = json.dumps({
        "model": model,
        "temperature": 0.8,
        **({"response_format": response_format} if json_mode else {}),
        "messages": messages
    })

    response = requests.post(gpt_url, headers=headers, data=payload)
    parsed_data = json.loads(response.text)
    content = parsed_data['choices'][0]['message']['content']
    # 去除思考模型的部分
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    # 为了防止不支持json格式的模型额外输出，利用正则提取json内容,原理是提取花括号
    match = re.search(r'\{.*\}', content, re.DOTALL)
    content = match.group(0) if match else content
    print(content)
    return content


def gpt_context(system, prompt, history):
    """上下文模式的GPT对话函数"""
    gpt_url = config.get('CHATGPT', 'BASE_URL')
    model = config.get('CHATGPT', 'model')

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]

    # 合并历史对话和当前对话
    messages = history + messages

    payload = json.dumps({
        "model": model,
        "messages": messages
    })

    response = requests.post(gpt_url, headers=headers, data=payload)
    content = json.loads(response.text)['choices'][0]['message']['content']

    # 去除思考模型的部分
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    return content


