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
    model_supplier = chat_config.get('ModelSupplier', 'OpenAI').lower()
    model = chat_config.get('model', '')
    api_key = chat_config.get('gpt_key')
    proxies = None
    if proxy_url := chat_config.get('proxy'):
        proxies = {"http": proxy_url, "https": proxy_url}

    # 根据供应商选择不同的处理逻辑
    if model_supplier == 'googleaistudio':
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        
        system_instruction = None
        if messages and messages[0]['role'] == 'system':
            system_instruction = {"parts": [{"text": messages.pop(0)['content']}]}

        google_contents = [
            {"role": "model" if msg["role"] == "assistant" else "user", "parts": [{"text": msg["content"]}]}
            for msg in messages
        ]

        # 构建请求体
        payload = {"contents": google_contents}
        if system_instruction:
            payload['system_instruction'] = system_instruction
            
        generation_config = {"temperature": 0.8}
        if json_mode:
            generation_config["responseMimeType"] = "application/json"
        payload['generationConfig'] = generation_config

        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        content = data['candidates'][0]['content']['parts'][0]['text']

    elif model_supplier == 'ollama':
        # Ollama API 调用逻辑
        url = 'http://localhost:11434/api/chat'
        payload = {"model": model, "messages": messages, "stream": False}
        if json_mode:
            payload["format"] = "json"
        
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        response.raise_for_status()
        data = response.json()
        content = data.get('message', {}).get('content', '')

    elif model_supplier == 'openai':  
        # OpenAI 兼容 API调用逻辑
        url = chat_config.get('base_url').rstrip('/')+"/chat/completions"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        payload = {"model": model, "temperature": 0.8, "messages": messages}
        if json_mode:
            payload["response_format"] = {'type': 'json_object'}

        response = requests.post(url, headers=headers, json=payload, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']

    else:
        raise ValueError(f"不支持的供应商: {model_supplier}")

    # 对返回内容进行通用后处理
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    if json_mode:
        # 提取被代码块包裹的 JSON 字符串
        if match := re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL):
            content = match.group(1)
        # 如果没有代码块，则直接查找 JSON 对象
        elif match := re.search(r'\{.*\}', content, re.DOTALL):
            content = match.group(0)
            
    return content

def gpt(system, prompt, json_mode = False):
    """单次对话函数"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return _send_chat_request(messages, json_mode)

def gpt_context(system, prompt, history, json_mode = False):
    """上下文模式的对话函数"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if isinstance(history, list):
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    return _send_chat_request(messages, json_mode)


if __name__ == "__main__":
    # 单元测试
    # 确保在同一目录下有一个 config.toml 文件，
    # 其中包含您的 API 密钥和其他设置。

    print(f"当前选择的供应商: {config.get('CHATGPT', {}).get('ModelSupplier', '未指定')}")
    print("-" * 20)

    # 1. 测试 gpt 函数
    print("测试 gpt 函数...")
    try:
        response = gpt(system="你是一个乐于助人的助手。", prompt="你好，你是谁？")
        print("1.测试通过，gpt 函数的响应：\n", response)
    except Exception as e:
        print(f"发生错误：{e}\n请确保您的 config.toml 文件已正确设置。")

    print("-" * 20)

    # 2. 测试带 JSON 模式的 gpt 函数
    print("测试带 JSON 模式的 gpt 函数...")
    try:
        response_json = gpt(
            system="你是一个提供 JSON 输出的助手。",
            prompt="纽约的天气怎么样？请以 JSON 格式回应，包含 'city' 和 'temperature' 键。",
            json_mode=True
        )
        print("gpt 函数的响应（JSON 模式）：\n", response_json)
        # 验证是否为有效的 JSON
        json.loads(response_json)
        print("2.测试通过，JSON 格式验证通过。")
    except Exception as e:
        print(f"JSON 模式测试期间发生错误：{e}\n请确保模型支持 JSON 模式。")

    print("-" * 20)

    # 3. 测试 gpt_context 函数
    print("测试 gpt_context 函数...")
    try:
        history = [
            {"role": "user", "content": "我的名字是约翰。"},
            {"role": "assistant", "content": "很高兴认识你，约翰！"}
        ]
        response_context = gpt_context(
            system="你是一个能记住对话历史的助手。",
            prompt="我叫什么名字？",
            history=history
        )
        print("3.测试通过，gpt_context 函数的响应：\n", response_context)
    except Exception as e:
        print(f"上下文测试期间发生错误：{e}")