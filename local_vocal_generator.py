import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import configparser
import os

try:
    import renpy

    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
audio_directory = os.path.join(game_directory, "audio")

config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')
sovits_type = "V2" if config.get('SOVITS', 'version') == "1" else "V1"
Theme_Language = config.get('剧情', 'Language')
if Theme_Language == "中文":
    Lang = "zh"
elif Theme_Language == "英文":
    Lang = "en"
else:
    Lang = "ja"


def generate_audio(type, response, name_id, output_name):
    """    type：sovits模型版本"""

    model_name = config.get('SOVITS', f'model{name_id}')
    json_data = {
        "gpt_model_path": f'GPT_weights\\{model_name}.ckpt',
        "sovits_model_path": f'SoVITS_weights\\{model_name}.pth'
    }

    full_url = config.get('SOVITS', f'sovits_url{name_id}' if 1 <= name_id <= 5 else 'sovits_url6')
    full_url = full_url.replace("response", response)

    def convert_url(original_url):
        """把v1格式的url转换成v2格式"""
        parsed_url = urlparse(original_url)
        query_params = parse_qs(parsed_url.query)

        new_query_params = {
            'text': query_params.get('text', [''])[0],
            'text_lang': query_params.get('text_language', [''])[0],
            'ref_audio_path': query_params.get('refer_wav_path', [''])[0],
            'prompt_lang': query_params.get('prompt_language', [''])[0],
            'prompt_text': query_params.get('prompt_text', [''])[0],
            'text_split_method': 'cut5',
            'batch_size': '1',
            'media_type': 'wav',
            'streaming_mode': 'false'
        }

        new_query_string = urlencode(new_query_params, doseq=True)

        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            '/tts',
            parsed_url.params,
            new_query_string,
            parsed_url.fragment
        ))

        return new_url

    if type == "V2":
        full_url.replace("/", "//")
        full_url = convert_url(full_url)
        full_url = full_url.replace("text_lang=zh", f"text_lang={Lang}")
        requests.get(
            f"http://127.0.0.1:9880/set_gpt_weights?weights_path=GPT_weights_v2/{model_name}.ckpt")
        requests.get(
            f"http://127.0.0.1:9880/set_sovits_weights?weights_path=SoVITS_weights_v2/{model_name}.pth")
    else:
        requests.post('http://127.0.0.1:9880/set_model', json=json_data)

    try:
        response = requests.get(full_url)
        with open(rf'{audio_directory}\{output_name}.wav', 'wb') as file:
            file.write(response.content)
        return "ok"

    except Exception as e:
        print("语音错误", e)
        return "error"

