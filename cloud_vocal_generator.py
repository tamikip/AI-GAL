# 改用toml
import requests
import toml
import time
import json
from path_config import game_directory, audio_directory
import os

config_path = os.path.join(game_directory, "config.toml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = toml.load(f)


def get_audio_url(content, speaker_id):
    token = config["SOVITS"]["api_key"]
    url = "https://ht.ttson.cn:37284/flashsummary/tts?token=" + token
    character_id = config["SOVITS"][f"model_id{speaker_id}"] if 1 <= speaker_id <= 6 else 6
    payload = json.dumps({
        "voice_id": character_id,
        "text": content,
        "to_lang": "auto",
        "format": "mp3",
        "speed_factor": 1,
        "pitch_factor": 0,
        "volume_change_dB": 0
    })

    response = requests.request("POST", url, data=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    response_json = response.json()

    result = response_json['url'] + ':' + str(
        response_json['port']) + '/flashsummary/retrieveFileData?stream=True&token=' + token + '&voice_audio_path=' + \
             response_json['voice_path']
    return result


def download_audio(url, save_path):
    if url == "":
        print("Empty url")
        return False
    try:
        audio_content = requests.get(url)
        if audio_content.status_code == 200:
            with open(f"{save_path}.mp3", "wb") as f:
                f.write(audio_content.content)
            return True
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
    return False


def online_generate_audio(content, speaker_id, output_name):
    url = get_audio_url(content, speaker_id)
    output_name = os.path.join(audio_directory, output_name)
    download_audio(url, output_name)


if __name__ == "__main__":
    start_time = time.time()
    online_generate_audio("测试,你好", 1, "test")
    end_time = time.time()
    execution_time = end_time - start_time
    print(execution_time)
