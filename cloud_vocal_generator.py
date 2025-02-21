import requests
import configparser
import os
import time

try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
import json

config = configparser.ConfigParser()
audio_directory = os.path.join(game_directory, "audio")
config.read(rf"{game_directory}\config.ini", encoding='utf-8')


def online_generate_audio(content, speaker, output_name):
    audio_key = config.get("SOVITS", "语音key")
    if speaker == 1:
        speaker = "杰帕德"
    elif speaker == 2:
        speaker = "三月七"
    elif speaker == 3:
        speaker = "克拉拉"
    elif speaker == 4:
        speaker = "符玄"
    elif speaker == 5:
        speaker = "青雀"
    else:
        speaker = "黑塔"
    data = {
        "access_token": audio_key,
        "model_name": "星穹铁道",
        "speaker_name": speaker,
        "prompt_text_lang": "中文",
        "emotion": "中立_neutral",
        "text": content,
        "text_lang": "多语种混合",
        "top_k": 10,
        "top_p": 1,
        "temperature": 1,
        "text_split_method": "按标点符号切",
        "batch_size": 1,
        "batch_threshold": 0.75,
        "split_bucket": "true",
        "speed_facter": 1,
        "fragment_interval": 0.3,
        "media_type": "wav",
        "parallel_infer": "true",
        "repetition_penalty": 1.35,
        "seed": -1
    }

    headers = {
        'Content-Type': 'application/json',
    }
    online_audio_url_endpoint = 'https://gsv.ai-lab.top/infer_single'

    response = requests.post(online_audio_url_endpoint, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        mp3_url = response_data["audio_url"]

        with requests.get(mp3_url) as r:
            r.raise_for_status()
            file_path = os.path.join(audio_directory, f"{output_name}.wav")

            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f'音频已下载: {output_name}.wav')
    else:
        return "error"


if __name__ == "__main__":
    start_time = time.time()
    result = online_generate_audio("测试,你好", 2, "test")
    end_time = time.time()
    execution_time = end_time - start_time
    print(execution_time)

