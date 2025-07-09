# 添加本地ollama支持
# 改用toml
import requests
import toml
import re
import json
import os
try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()

config_path = os.path.join(game_directory, "config.toml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = toml.load(f)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {config.get("CHATGPT", "GPT_KEY")}'
}


def gpt(system, prompt, json_mode=False):
    """普通的gpt调用，兼容OpenAI和本地ollama模型"""
    gpt_url = config['CHATGPT']['base_url']
    model = config['CHATGPT']['model']
    is_ollama = any(host in gpt_url for host in ['localhost:11434', '127.0.0.1:11434'])
    messages = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    if is_ollama:
        payload_dict = {"model": model, "messages": messages, "stream": False}
        if json_mode:
            payload_dict["format"] = "json"
            
        payload = json.dumps(payload_dict)
        headers_local = {'Content-Type': 'application/json'}
        response = requests.post(gpt_url, headers=headers_local, data=payload)
        response.raise_for_status()
        parsed_data = json.loads(response.text)
        if 'message' in parsed_data:
            content = parsed_data['message'].get('content', '')
        elif 'choices' in parsed_data:
            content = parsed_data['choices'][0]['message']['content']
        else:
            content = response.text
    else:
        response_format = {'type': 'json_object'}
        if json_mode:
            json_mode = config.get("Settings", "json_mode")
        payload = json.dumps({"model": model,"temperature": 0.8,**({"response_format": response_format} if json_mode else {}),"messages": messages})
        headers_remote = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config["CHATGPT"]["gpt_key"]}'
        }
        response = requests.post(gpt_url, headers=headers_remote, data=payload)
        parsed_data = json.loads(response.text)
        print(parsed_data)
        content = parsed_data['choices'][0]['message']['content']
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    print(content)
    match = re.search(r'\{.*\}', content, re.DOTALL)
    content = match.group(0) if match else content
    return content


def gpt_context(system, prompt, history):
    """上下文模式的GPT对话函数"""
    gpt_url = config.get('CHATGPT', 'BASE_URL')
    model = config.get('CHATGPT', 'model')
    messages = [{"role": "system", "content": system},{"role": "user", "content": prompt}]
    messages = history + messages
    payload = json.dumps({"model": model, "messages": messages})
    response = requests.post(gpt_url, headers=headers, data=payload)
    content = json.loads(response.text)['choices'][0]['message']['content']
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    return content


