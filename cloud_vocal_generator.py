# 改用toml
import requests
import toml
import os
import time

try:
    import renpy

    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
import json

audio_directory = os.path.join(game_directory, "audio")
with open(rf"{game_directory}\config.toml", 'r', encoding='utf-8') as f:
    config = toml.load(f)


def get_audio_url(content, speaker_id):
    token = config["SOVITS"]["api_key"]
    url = "https://ht.ttson.cn:37284/flashsummary/tts?token=" + token
    character_id = config.get("sovits", f"model_id{speaker_id}") if 1 <= speaker_id <= 6 else 6
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

    print(url)
    return result


def download_audio(url, save_path):
    if url == "":
        print("Empty url")
        return False
    try:
        audio_content = requests.get(url)
        if audio_content.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(audio_content.content)
            return True
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
    return False


def online_generate_audio(content, speaker_id, output_name):
    url = get_audio_url(content, speaker_id)
    download_audio(url, output_name)


if __name__ == "__main__":
    start_time = time.time()
    online_generate_audio("测试,你好", 430, "test.mp3")
    end_time = time.time()
    execution_time = end_time - start_time
    print(execution_time)
