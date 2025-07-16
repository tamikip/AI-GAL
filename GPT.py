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

def _send_chat_request(messages, json_mode=False):
    """内部函数，用于发送请求到llm模型"""
    chat_config = config.get('CHATGPT', {})
    gpt_url = chat_config.get('base_url', '')
    model = chat_config.get('model', '')
    proxies = None
    proxy_url = chat_config.get('proxy')
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
    is_ollama = any(host in gpt_url for host in ['localhost:11434', '127.0.0.1:11434'])
    if is_ollama:
        payload_dict = {"model": model, "messages": messages, "stream": False}
        if json_mode:
            payload_dict["format"] = "json"

        payload = json.dumps(payload_dict)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(gpt_url, headers=headers, data=payload)
        response.raise_for_status()
        parsed_data = response.json()
        if 'message' in parsed_data:
            content = parsed_data['message'].get('content', '')
        elif 'choices' in parsed_data:
            content = parsed_data['choices'][0]['message']['content']
        else:
            content = response.text
    else: # OpenAI
        payload_dict = {"model": model, "temperature": 0.8, "messages": messages}
        if json_mode:
            payload_dict["response_format"] = {'type': 'json_object'}
        payload = json.dumps(payload_dict)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {chat_config.get("gpt_key")}'
        }

        response = requests.post(gpt_url, headers=headers, data=payload, proxies=proxies)
        response.raise_for_status()
        parsed_data = response.json()
        content = parsed_data['choices'][0]['message']['content']
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    if json_mode:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        content = match.group(0) if match else content
    return content

def gpt(system, prompt, json_mode=False):
    """单次对话函数"""
    messages = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return _send_chat_request(messages, json_mode)

def gpt_context(system, prompt, history, json_mode=False):
    """上下文模式的对话函数"""
    messages = []
    if system is not None:
        messages.append({"role": "system", "content": system})
    if isinstance(history, list):
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    return _send_chat_request(messages, json_mode)

if __name__ == "__main__":
    # 单元测试
    # 确保在同一目录下有一个 config.toml 文件，
    # 其中包含您的 API 密钥和其他设置。
    
    # 1 测试 gpt 函数
    print("测试 gpt 函数...")
    try:
        system_message = "你是一个乐于助人的助手。"
        user_prompt = "你好，你是谁？"
        response = gpt(system=system_message, prompt=user_prompt)
        print("gpt 函数的响应：")
        print(response)
    except Exception as e:
        print(f"发生错误：{e}")
        print("请确保您的 config.toml 文件已正确设置。")

    print("-" * 20)

    # 2.测试带 JSON 模式的 gpt 函数
    print("测试带 JSON 模式的 gpt 函数...")
    try:
        system_message_json = "你是一个提供 JSON 输出的乐于助人的助手。"
        user_prompt_json = "纽约的天气怎么样？请以 JSON 格式回应，包含 'city' 和 'temperature' 键。"
        response_json = gpt(system=system_message_json, prompt=user_prompt_json, json_mode=True)
        print("gpt 函数的响应（JSON 模式）：")
        print(response_json)
    except Exception as e:
        print(f"JSON 模式测试期间发生错误：{e}")
        print("请确保您的 config.toml 文件已正确设置，并且模型支持 JSON 模式。")

    print("-" * 20)

    # 3. 测试 gpt_context 函数
    print("测试 gpt_context 函数...")
    try:
        system_message_context = "你是一个能记住对话历史的乐于助人的助手。"
        history = [
            {"role": "user", "content": "我的名字是约翰。"},
            {"role": "assistant", "content": "很高兴认识你，约翰！"}
        ]
        user_prompt_context = "我叫什么名字？"
        response_context = gpt_context(system=system_message_context, prompt=user_prompt_context, history=history)
        print("gpt_context 函数的响应：")
        print(response_context)
    except Exception as e:
        print(f"上下文测试期间发生错误：{e}")
        print("请确保您的 config.toml 文件已正确设置。")

    print("-" * 20)

    # 4. 测试带 JSON 模式的 gpt_context 函数
    print("测试带 JSON 模式的 gpt_context 函数...")
    try:
        system_message_context_json = "你是一个能记住对话历史并以 JSON 格式回应的助手。"
        history_json = [
            {"role": "user", "content": "请记住我最喜欢的城市是巴黎。"},
            {"role": "assistant", "content": "好的，我记住你最喜欢的城市是巴黎了。"}
        ]
        user_prompt_context_json = "我最喜欢的城市是什么？请以 JSON 格式回应，包含 'city' 键。"
        response_context_json = gpt_context(system=system_message_context_json, prompt=user_prompt_context_json, history=history_json, json_mode=True)
        print("gpt_context 函数的响应（JSON 模式）：")
        print(response_context_json)
    except Exception as e:
        print(f"上下文 JSON 模式测试期间发生错误：{e}")
        print("请确保您的 config.toml 文件已正确设置。")
