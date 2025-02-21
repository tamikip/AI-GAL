import requests
import configparser
import json
import os
try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()

config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')


def generate_music(prompt, filename):
    music_url = config.get("AI音乐", "base_url")
    key = config.get("AI音乐", "api_key")
    headers = {
        'Authorization': f'Bearer {key}',
        'Accept': 'application/json',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    full_music_url = f"https://{music_url}/suno/submit/music"

    sad = "Pure music, light music, game,galgame,piano,sad,violin"
    common = "Pure music, light music, relaxed,cafe,game,galgame,piano"

    payload = {
        "prompt": "a",
        "tags": sad if prompt == "sad" else common,
        "mv": "chirp-v3-5",
        "title": "BGM",
        "make_instrumental": True
    }

    response = requests.post(full_music_url, headers=headers, json=payload)
    music_id = json.loads(response.text)["data"]

    url2 = f"https://{music_url}/suno/fetch/{music_id}"

    while True:
        response = requests.request("GET", url2, headers=headers)
        json.loads(response.text)
        response_data = json.loads(response.text)

        if response_data['data']["status"] == 'SUCCESS':

            audio_urls = [item["audio_url"] for item in response_data["data"]["data"]]
            with requests.get(audio_urls[0], stream=True) as r:
                with open(fr"{game_directory}/music/{filename}.mp3", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"文件 {filename} 已下载。")
            with requests.get(audio_urls[1], stream=True) as r:
                with open(fr"{game_directory}/music/{filename}2.mp3", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"文件 {filename}2 已下载。")
            break