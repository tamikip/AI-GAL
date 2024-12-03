import re
import base64
import os
import requests
import json
import time
import configparser
import random
import threading
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

try:
    import renpy

    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()

generate_new_chapters_state = False
background_list = []
if_already = False
threads = []
thread2s = []

character_list = []

images_directory = os.path.join(game_directory, "images")
audio_directory = os.path.join(game_directory, "audio")
config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')
sovits_type = "V2" if config.get('SOVITS', 'version') == "1" else "V1"


def gpt(system, prompt):
    gpt_key = config.get('CHATGPT', 'GPT_KEY')
    gpt_url = config.get('CHATGPT', 'BASE_URL')
    model = config.get('CHATGPT', 'model')

    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {gpt_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", gpt_url, headers=headers, data=payload)
    content = json.loads(response.text)['choices'][0]['message']['content']
    return content


def separate_content(text):
    title_pattern = re.compile(r"标题:(.+)")
    outline_pattern = re.compile(r"大纲:(.+?)背景:", re.DOTALL)
    background_pattern = re.compile(r"背景:(.+?)人物:", re.DOTALL)
    characters_pattern = re.compile(r"人物:(.+)", re.DOTALL)
    title = title_pattern.search(text).group(1).strip()
    outline = outline_pattern.search(text).group(1).strip()
    background = background_pattern.search(text).group(1).strip()
    characters = characters_pattern.search(text).group(1).strip()
    information = (title, outline, background, characters)
    return information


# ----------------------------------------------------------------------
"""下面是关于云端部分的设置内容"""
online_draw_key = config.get('AI绘画', 'draw_key')

url = "https://cn.tensorart.net/v1/jobs"
online_draw_headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {online_draw_key}"
}


def online_generate(prompt, mode):
    print("云端启动绘画")
    requests_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if mode == 'background':
        width = 960
        height = 540
        prompt2 = "(no_human)" + prompt
        if config.get('AI绘画', 'character_id'):
            model = config.get('AI绘画', 'character_id')
        else:
            model = "611399039965066695"

    else:
        width = 512
        height = 768
        prompt2 = "(upper_body),solo" + prompt
        if config.get('AI绘画', 'background_id'):
            model = config.get('AI绘画', 'background_id')
        else:
            model = "611437926598989702"
    data = {
        "request_id": str(requests_id),
        "stages": [
            {
                "type": "INPUT_INITIALIZE",
                "inputInitialize": {
                    "seed": -1,
                    "count": 1
                }
            },
            {
                "type": "DIFFUSION",
                "diffusion": {
                    "width": width,
                    "height": height,
                    "prompts": [{"text": prompt2}],
                    "steps": 25,
                    "sdVae": "animevae.pt",
                    "sd_model": model,
                    "clip_skip": 2,
                    "cfg_scale": 7,
                    **({"layerDiffusion": {"enable": True, "weight": 0}} if mode != "background" else {})
                }
            },
            {
                "type": "IMAGE_TO_UPSCALER",
                "image_to_upscaler": {
                    "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
                    "hr_scale": 2,
                    "hr_second_pass_steps": 10,
                    "denoising_strength": 0.3
                }
            }
        ]
    }
    response = requests.post(url, headers=online_draw_headers, data=json.dumps(data))

    if response.status_code == 200:
        id = json.loads(response.text)['job']['id']
        return id
    else:
        print(f"请求失败，状态码：{response.status_code}，请检查是否正确填写了key")
        return "error"


def get_result(job_id, image_name):
    while True:
        time.sleep(1)
        response = requests.get(f"{url}/{job_id}", headers=online_draw_headers)
        get_job_response_data = json.loads(response.text)
        if 'job' in get_job_response_data:
            job_dict = get_job_response_data['job']
            job_status = job_dict.get('status')
            if job_status == 'SUCCESS':
                url2 = job_dict["successInfo"]["images"][0]["url"]
                response = requests.get(url2)
                with open(fr'{images_directory}\{image_name}.png', 'wb') as f:
                    f.write(response.content)
                break
            elif job_status == 'FAILED':
                print(job_dict)
                break


def online_generate_image(prompt, image_name, mode):
    task_id = online_generate(prompt, mode)
    get_result(task_id, image_name)


def online_generate_audio(content, speaker, output_name):
    audio_key = config.get("SOVITS", "语音key")
    if speaker == 1:
        speaker = "哲【绝区零】"
    elif speaker == 2:
        speaker = "银狼【星穹铁道】"
    elif speaker == 3:
        speaker = "流萤【星穹铁道】"
    elif speaker == 4:
        speaker = "宵宫【原神】"
    elif speaker == 5:
        speaker = "艾丝妲【星穹铁道】"
    else:
        speaker = "莫娜【原神】"
    data = {
        "access_token": audio_key,
        "type": "tts",
        "brand": "gpt-sovits",
        "name": "anime",
        "method": "api",
        "prarm": {
            "speaker": speaker,
            "emotion": "中立",
            "text": content,
            "text_language": "中英混合",
            "audio_url": "https://gsv.ai-lab.top",
            "top_k": 10,
            "top_p": 1.0,
            "temperature": 1.0,
            "speed": 1.0
        }
    }
    headers = {
        'Content-Type': 'application/json',
    }
    online_audio_url_endpoint = 'https://infer.acgnai.top/infer/gen'

    response = requests.post(online_audio_url_endpoint, data=json.dumps(data), headers=headers)

    print(json.loads(response.text))

    if response.status_code == 200:
        response_data = json.loads(response.text)
        mp3_url = response_data["audio"]
        with requests.get(mp3_url) as r:
            r.raise_for_status()
            with open(fr'{audio_directory}/{output_name}.wav', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f'音频已下载: {output_name}.wav')
    else:
        return "error"


def generate_music(prompt, filename):
    music_url = config.get("AI音乐", "base_url")
    key = config.get("AI音乐", "api_key")
    headers = {
        'Authorization': f'Bearer {key}',
        'Accept': 'application/json',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    def run(prompt):
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
        return music_id

    def download_music(music_id, filename):
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

    download_music(run(prompt), filename)


# ----------------------------------------------------------------------


def generate_image(prompt, image_name, mode):
    global images_directory
    url = "http://127.0.0.1:7860"

    if mode == 'background':
        width = 960
        height = 540
        prompt2 = "(no_human)"
        model = "x"

    else:
        width = 512
        height = 768
        prompt2 = "(upper_body),solo"
        model = "x"

    payload = {
        "prompt": f"masterpiece,wallpaper,8k,{prompt},{prompt2}",
        "negative_prompt": "EasyNagative,lowres, bad anatomy, text,cropped,low quality,(mutation, poorly drawn :1.2),"
                           "normal quality, obesity,bad proportions,unnatural body,bad shadow, uncoordinated body, "
                           "worst quality,censored,low quality,signature,watermark, username, blurry,nsfw",
        "steps": 25,
        "sampler_name": "DPM++ 2M SDE",
        "width": width,
        "height": height,
        "restore_faces": False,
        "enable_hr": True,
        "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
        "hr_scale": 2,
        "hr_second_pass_steps": 15,
        "denoising_strength": 0.3
    }

    try:
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        if response.status_code == 200:
            r = response.json()
            for i, img_data in enumerate(r['images']):
                if ',' in img_data:
                    base64_data = img_data.split(",", 1)[1]
                else:
                    base64_data = img_data
                image_data = base64.b64decode(base64_data)
                final_image_name = f'{image_name}.png'
                with open(fr'{images_directory}\{final_image_name}', 'wb') as f:
                    f.write(image_data)
                print(f'图片已保存为 {final_image_name}')
            return "ok"
        else:
            print("Failed to generate image:", response.text)
            return "error"

    except:
        print("绘图失败！")
        return "error"


def generate_audio(type, response, name_id, output_name):
    """    type：sovits模型版本"""

    global audio_directory
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


def add_dialogue_to_json(character, text, background_image, audio):
    global game_directory

    try:
        with open(rf"{game_directory}\dialogues.json", "r", encoding="utf-8") as file:
            dialogues = json.load(file)

        dialogues["conversations"].append({
            "character": character,
            "text": text,
            "background_image": background_image,
            "audio": audio
        })

        with open(rf"{game_directory}\dialogues.json", "w", encoding="utf-8") as file:
            json.dump(dialogues, file, indent=4, ensure_ascii=False)

        print("新的对话已成功添加到dialogues.json文件中")

    except Exception as e:
        print(f"发生错误:{e}")


def rembg(pic):
    global images_directory
    rembg_url = "http://localhost:7000/api/remove"
    file_path = rf"{images_directory}/{pic}.png"

    with open(file_path, 'rb') as file:
        response = requests.post(rembg_url, files={'file': file})

    with open(file_path, 'wb') as output_file:
        output_file.write(response.content)


def select_branch():
    with open(rf"{game_directory}\story.txt", 'r', encoding='utf-8') as file:
        story_content = file.read()
    choices = gpt("你是galgame剧情家，精通各种galgame写作",
                  f"根据galgame剧情,以男主角的视角，设计男主角接下来的三个分支选项。内容:{story_content},返回格式:1.xxx\n2.xxx\n3.xxx,要求每个选项尽量简短。不要使用markdown语法。")
    cleaned_text = '\n'.join([line.split('. ', 1)[1] if '. ' in line else line for line in choices.strip().split('\n')])
    with open(rf"{game_directory}\choice.txt", 'w', encoding='utf-8') as file:
        file.write(cleaned_text)
    return cleaned_text


def start_online_draw_threads(prompt, image_name, mode):
    global threads
    thread = threading.Thread(target=online_generate_image, args=(prompt, image_name, mode))
    thread.start()
    threads.append(thread)


def start_online_audio_threads(content, speaker, output_name):
    global thread2s
    thread = threading.Thread(target=online_generate_audio, args=(content, speaker, output_name))
    thread.start()
    threads.append(thread)


def main():
    global story_content, game_directory, if_already, character_list, sovits_type
    namelist = []
    if config.getboolean('AI音乐', 'if_on'):
        thread1 = threading.Thread(target=generate_music, args=("common", "happy bgm"))
        thread2 = threading.Thread(target=generate_music, args=("sad", "sad bgm"))
        thread1.start()
        thread2.start()

    with open(rf'{game_directory}\dialogues.json', 'w') as file:
        file.write("""{\n"conversations": [\n]\n}""")

    with open(rf"{game_directory}\characters.txt", 'w') as file:
        file.write('')

    theme = config.get('剧情', '剧本的主题', fallback='随机主题，自行发挥想象')
    try:
        theme = config.get('剧情', "outline")
    except:
        pass

    title, outline, background, characters = separate_content(
        gpt("现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情，不要使用markdown格式",
            f"现在请你写一份gal game的标题，大纲，背景，人物,我给出的主题和要求是{theme}，你的输出格式为:标题:xx\n大纲:xx\n背景:xx\n人物:xx"
            f"(每个人物占一行,人物不多于5人)，每个人物的格式是人物名:介绍,无需序号。男主角也要名字").replace(
            "：", ":"))

    story_content = gpt("现在你是一名galgame剧情作家，精通写各种各样的galgame剧情，请不要使用markdown格式",
                        f"现在根据以下内容开始写第一章:gal game标题:{title},gal game大纲:{outline},gal game背景:{background},galgame角色:{characters}。"
                        f"你的输出格式应该为对话模式，例xxx:xx表达，你的叙事节奏要非常非常慢，可以加一点新的内容进去。需要切换地点时，在句尾写[地点名]，[地点名]不可单独一行，不用切换则不写，"
                        f"开头第一句是旁白而且必须要包含地点[]，地点理论上不应该超过3处。不需要标题。"
                        f"输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。不要出现小括号")

    lines = story_content.split('\n')  # 去掉文本最后一行,因为ai会经常总结内容
    story_content = '\n'.join(lines[:-1])

    book_lines = story_content.splitlines()
    print(story_content)

    with open(rf"{game_directory}\story.txt", 'w', encoding='utf-8') as file:
        file.write(f"{story_content}\n")

    with open(rf"{game_directory}\character_info.txt", 'w', encoding='utf-8') as file:
        file.write(characters)

    characters_lines = characters.splitlines()
    characters_lines = [item for item in characters_lines if ":" in item]
    print(characters_lines)

    for i in range(len(characters_lines)):
        prompt = gpt(
            "根据人物设定给出相应的人物形象，应该由简短的英文单词或短句组成，一定要加上角色的性别，男生帅，女生美。输出格式样例:"
            "a girl,pink hair,black shoes,long hair,young,lovely。请注意，人名与实际内容无关无需翻译出来，只输出英文单词，不要输出多余的内容",
            f"人物形象{characters_lines[i]}")

        name = characters_lines[i].split(":", 1)[0]
        name = re.sub(r'[^\u4e00-\u9fa5]', '', name)  # 标准化名字
        namelist.append(name)
        if config.getboolean('AI绘画', 'if_cloud'):
            start_online_draw_threads(prompt, name, "character")
        else:
            generate_image(prompt, name, "character")
            rembg(name)
        character_list.append(name)
        with open(rf"{game_directory}\characters.txt", "a", encoding='utf-8') as file:
            file.write(f"{name}\n")
    for thread in threads:
        thread.join()

    for i in book_lines:
        if i.strip() != "":
            background = re.findall(r'(?<=\[).*?(?=\])', i)

            if background and background[0] not in background_list:
                prompt = gpt(
                    "把下面的内容翻译成英文并且变成短词,比如red,apple,big这样。请注意，地名与实际内容无关无需翻译出来，"
                    "例如星之学院应该翻译成academy而不是star academy。你应该只返回英文单词，下面是你要翻译的内容:",
                    background[0])
                print(prompt)
                if config.getboolean('AI绘画', 'if_cloud'):
                    online_generate_image(prompt, background[0], "background")
                else:
                    generate_image(prompt, background[0], "background")
                background_image = background[0]
                background_list.append(background_image)

            else:
                background_image = ""

            i = i.replace("：", ":")

            i = "旁白:" + i if ":" not in i else i

            character, original_text = i.split(":", 1)
            de_place_text = re.sub(r'\[.*?\]', '', original_text)
            de_discribe_text = re.sub(r'\（[^)]*\）', '', de_place_text.replace("(", "（").replace(")", "）"))

            try:
                audio_index = character_list.index(character) + 1

            except ValueError:
                print(f"{character} 不在列表中")
                audio_index = 6

            if character != "旁白":
                if config.getboolean('SOVITS', 'if_cloud'):
                    start_online_audio_threads(de_discribe_text, audio_index, de_place_text)
                else:
                    generate_audio(sovits_type, de_discribe_text, audio_index, de_place_text, )

            character = "" if character == "旁白" else character

            if original_text != "":
                add_dialogue_to_json(character, de_discribe_text, background_image, de_place_text)
    for thread in thread2s:
        thread.join()
    select_branch()
    if_already = True


def story_continue(choice):
    global story_content, generate_new_chapters_state, game_directory, character_list, sovits_type
    generate_new_chapters_state = True
    with open(rf"{game_directory}\story.txt", 'r', encoding='utf-8') as file:
        story_content = file.read()
    with open(rf"{game_directory}\character_info.txt", 'r', encoding='utf-8') as file:
        character_info = file.read()

    add_book = gpt(
        "现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情。只输出文本，不要输出任何多余的。不要使用markdown格式，如果需要切换场景在对话的后面加上[地点]，"
        "输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。",
        f"请你根据以下内容继续续写galgame剧情。只返回剧情。人物设定：{character_info}，内容:{story_content},我选则的分支是{choice}")

    book_lines = add_book.splitlines()
    story_content = story_content + "\n" + add_book

    with open(rf'{game_directory}\story.txt', 'w', encoding='utf-8') as file:
        file.write(f"{story_content}\n")

    for i in book_lines:
        if i.strip() != "":
            background = re.findall(r'(?<=\[).*?(?=\])', i)

            if background and background[0] not in background_list:
                prompt = gpt(
                    "把下面的内容翻译成英文并且变成短词,比如red,apple,big这样。请注意，地名与实际内容无关无需翻译出来，"
                    "例如星之学院应该翻译成academy而不是star academy。你应该只返回英文单词，下面是你要翻译的内容:",
                    background[0])
                print(prompt)
                cloud_mode = config.getboolean('AI绘画', 'if_cloud')
                if cloud_mode:
                    online_generate_image(prompt, background[0], "background")
                else:
                    generate_image(prompt, background[0], "background")
                background_image = background[0]
                background_list.append(background_image)

            else:
                background_image = ""

            i = i.replace("：", ":")

            i = "旁白:" + i if ":" not in i else i

            character, original_text = i.split(":", 1)
            de_place_text = re.sub(r'\[.*?\]', '', original_text)  # 去除地点

            de_discribe_text = re.sub(r'\（[^)]*\）', '', de_place_text.replace("(", "（").replace(")", "）"))  # 去除小括号

            try:
                with open(rf"{game_directory}\characters.txt", 'r', encoding='utf-8') as file:
                    line_number = 0
                    for line in file:
                        line_number += 1
                        if character in line:
                            audio_index = line_number
            except ValueError:
                print(f"{character} 不在列表中")
                audio_index = 6

            if character != "旁白" and character != "new":
                if config.getboolean('SOVITS', 'if_cloud'):
                    online_generate_audio(de_discribe_text, audio_index, de_place_text)
                else:
                    generate_audio(sovits_type, de_discribe_text, audio_index, de_place_text)

            character = "" if character == "旁白" else character

            if original_text != "":
                add_dialogue_to_json(character, de_discribe_text, background_image, de_place_text)
    select_branch()
    generate_new_chapters_state = False


if __name__ == "__main__":
    main()

