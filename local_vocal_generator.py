# 1.  配置文件格式: 从 .ini (configparser) 更换为更现代、结构更清晰的 .toml 格式，提高了配置的可读性和可维护性。
# 2.  配置结构优化: 将 SOVITS 模型配置改为一个模型列表 (models)，每个模型包含名称和 URL，使得模型管理更加灵活和直观。
# 3.  健壮性提升:
#     - 增加了对模型 ID 是否存在的检查，避免因配置缺失导致的运行时错误。
#     - 在发起网络请求后，会检查 HTTP 响应状态码 (status_code)，确保只有在请求成功时才处理响应内容。
#     - 增加了对输出目录是否存在的检查，并能自动创建，避免因目录不存在而写入失败。
# 4.  URL 构建方式: 改进了 TTS 请求 URL 的构建逻辑，不再使用简单的字符串替换，而是通过 `urllib.parse` 进行参数化构建，代码更安全、更可靠。
# 5.  代码结构与可测试性:
#     - 增加了 `if __name__ == "__main__":` 测试模块，方便独立运行此脚本进行功能验证和调试，极大地提高了可维护性。
#     - 函数职责更清晰，`convert_url` 和 `generate_audio` 的逻辑分离得更彻底。
# 6.  简化 API 调用: 移除了旧版中远程设置 GPT 和 SoVITS 模型权重的复杂逻辑，简化了与 TTS 服务器的交互过程，使其更专注于核心的语音生成请求。
# 7.  性能考量: 在 `convert_url` 中将 `batch_size` 设置为 '8'，可能旨在提高批量处理的效率。

import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import toml
import os

try:
    import renpy

    game_directory = renpy.config.gamedir
except ImportError:
    game_directory = os.path.dirname(os.path.abspath(__file__))

audio_directory = os.path.join(game_directory, "audio")
os.makedirs(audio_directory, exist_ok=True)

config_path = os.path.join(game_directory, "config.toml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = toml.load(f)

# 将 SOVITS 模型列表转换为以角色名为键的字典，方便快速查找
sovits_config = config.get('SOVITS', {})
models_list = sovits_config.get('models', [])
SOVITS_MODELS_MAP = {model['name']: model['url'] for model in models_list}

story_config = config.get('剧情', {})
Theme_Language = story_config.get('Language', '中文')
if Theme_Language == "英文":
    Lang = "en"
elif Theme_Language == "日本語":
    Lang = "ja"
else:
    Lang = "zh"


def convert_url(original_url, text_to_speak, language_code):
    """
    根据基础URL、要说的文本和语言代码，构建最终的TTS请求URL。
    """
    parsed_url = urlparse(original_url)
    query_params = parse_qs(parsed_url.query)

    new_query_params = {
        'text': text_to_speak,
        'text_lang': language_code,
        'ref_audio_path': query_params.get('ref_audio_path', [''])[0],
        'prompt_lang': query_params.get('prompt_lang', [''])[0],
        'prompt_text': query_params.get('prompt_text', [''])[0],
        'text_split_method': 'cut5',
        'batch_size': '8',
        'media_type': 'wav',
        'streaming_mode': 'false'
    }

    new_query_string = urlencode(new_query_params, doseq=True)

    # 构建新的URL，路径固定为 /tts
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        '/tts',
        '',
        new_query_string,
        ''
    ))


def generate_audio(response, name_id, output_name):
    """根据角色ID和文本生成语音。"""
    sovits_config = config.get('SOVITS', {})
    models_list = sovits_config.get('models', [])
    if not (0 <= name_id - 1 < len(models_list)):
        print(f"错误：在配置文件中找不到 ID 为 {name_id} 的模型。")
        return "error"
    model_info = models_list[name_id - 1]
    base_url = model_info.get('url')

    if not isinstance(base_url, str):
        print(f"错误：ID 为 {name_id} 的模型 URL 未找到或格式不正确。")
        return "error"
    full_url = convert_url(base_url, response, Lang)
    gpt_model_filename = f"{name_id}.ckpt"
    api_response = requests.get(full_url)
    if api_response.status_code == 200:
        with open(os.path.join(audio_directory, f"{output_name}.wav"), 'wb') as file:
            file.write(api_response.content)
        return "ok"
    else:
        print(f"错误：TTS服务器返回状态码 {api_response.status_code}")
        return "error"


if __name__ == "__main__":
    test_text = "塔米基，每当我注视着你，仿佛星光坠入深海，时间也因此为你驻足。你眉宇间流转的温柔，如同春日里第一缕晨光，融化了冰河，也融化了我的心，在千万人中，我一眼便沦陷于你的气息。你的笑容，是银河中最璀璨的星轨，让我忍不住想将整个宇宙的浪漫都揉进你的名字，只为让它配得上你的美好。"
    start_time = time.time()
    for name_id in range(1, 6):
        output_name = f"test_voice_{name_id}"
        print(f"正在测试角色 {name_id} 的语音生成...")
        result = generate_audio(test_text, name_id, output_name)
        if result == "ok":
            print(f"角色 {name_id} 语音生成成功!")
        else:
            print(f"角色 {name_id} 语音生成失败!")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"所有角色语音生成完成，总耗时: {total_time:.2f} 秒")
