import re
import base64
import os
import requests
import json
import time
import configparser
import random

# import renpy

running_state = False
background_list = []
if_already = False

character_list = []
# game_directory = renpy.config.basedir
game_directory = r"D:\renpy-8.1.1-sdk.7z\AI GAL"
game_directory = os.path.join(game_directory, "game")
images_directory = os.path.join(game_directory, "images")
audio_directory = os.path.join(game_directory, "audio")
config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')

def gpt(system, prompt, mode="default"):
    config = configparser.ConfigParser()
    config.read(rf"{game_directory}\config.ini", encoding='utf-8')
    key = config.get('CHATGPT', 'GPT_KEY')
    url = config.get('CHATGPT', 'BASE_URL')

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
        'Authorization': f'Bearer {key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
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
online_draw_key = config.get('AI绘画', '绘画key')
url = "https://cn.tensorart.net/v1/jobs"
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {online_draw_key}"
}


def online_generate(prompt, mode):
    # TMND:611399039965066695
    # 天空:611437926598989702
    requests_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if mode == 'background':
        width = 960
        height = 540
        prompt2 = "(no_human)" + prompt
        if config.get('AI绘画', '人物绘画模型ID(本地模式不填)'):
            model = config.get('AI绘画', '人物绘画模型ID(本地模式不填)')
        else:
            model = "611399039965066695"

    else:
        width = 512
        height = 768
        prompt2 = "(upper_body),solo" + prompt
        if config.get('AI绘画', '背景绘画模型ID(本地模式不填)'):
            model = config.get('AI绘画', '背景绘画模型ID(本地模式不填)')
        else:
            model = "700862942452666384"
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
                    "cfg_scale": 7
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
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 检查响应状态码
    if response.status_code == 200:
        id = json.loads(response.text)['job']['id']
        return id
    else:
        print(f"请求失败，状态码：{response.status_code}，请检查是否正确填写了key")


def get_result(job_id, image_name):
    while True:
        time.sleep(1)
        response = requests.get(f"{url}/{job_id}", headers=headers)
        get_job_response_data = json.loads(response.text)
        if 'job' in get_job_response_data:
            job_dict = get_job_response_data['job']
            job_status = job_dict.get('status')
            if job_status == 'SUCCESS':
                url2 = job_dict["successInfo"]["images"][0]["url"]
                response = requests.get(url2)
                with open(fr'{images_directory}\{image_name}.png', 'wb') as f:
                    # 将图片数据写入文件
                    f.write(response.content)
                break
            elif job_status == 'FAILED':
                print(job_dict)
                break


def generate_image_pro(prompt, image_name, mode):
    id = online_generate(prompt, mode)
    get_result(id, image_name)


def generate_audio_pro(content, speaker, output_name):
    if speaker == 1:
        speaker = "罗刹【中】"
    elif speaker == 2:
        speaker = "花火【中】"
    elif speaker == 3:
        speaker = "流萤【中】"
    elif speaker == 4:
        speaker = "藿藿【中】"
    elif speaker == 5:
        speaker = "三月七【中】"
    else:
        speaker = "符玄【中】"
    data = {
        "access_token": config.get('SOVITS', '语音key'),
        "type": "tts",
        "brand": "bert-vits2",
        "name": "sr",
        "prarm": {
            "speaker": speaker,
            "text": content,
            "sdp_ratio": 0.2,
            "noise_scale": 0.6,
            "noise_scale_w": 0.9,
            "length_scale": 1.0,
            "language": "ZH",
            "cut_by_sent": True,
            "interval_between_sent": 0.2,
            "interval_between_para": 1.0,
            "style_text": None,
            "style_weight": 0.7
        }
    }
    headers = {
        'Content-Type': 'application/json',
    }
    url = 'https://infer.acgnai.top/infer/gen'

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        mp3_url = response_data["audio"]
        with requests.get(mp3_url, stream=True) as r:
            # 检查请求是否成功
            r.raise_for_status()

            # 以流的方式写入文件
            with open(fr'{audio_directory}\{output_name}.wav', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f'音频已下载: {output_name}.wav')
    else:
        print('Failed:', response.status_code, response.text)


# ----------------------------------------------------------------------


def generate_image(prompt, image_name, mode):
    global images_directory
    url = "http://127.0.0.1:7860"

    if mode == 'background':
        width = 960
        height = 540
        prompt2 = "(no_human)"
        model = "tmndMix_tmndMixVPruned.safetensors [d9f11471a8]"

    else:
        width = 512
        height = 768
        prompt2 = "(upper_body),solo"
        model = "天空之境.safetensors [c1d961233a]"

    payload = {
        "prompt": f"masterpiece,wallpaper,simple background,{prompt},{prompt2}",
        "negative_prompt": "Easynagative,bad,worse,nsfw",
        "steps": 30,
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

        else:
            print("Failed to generate image:", response.text)

    except:
        print("绘图失败！")


def generate_audio(response, name, output_name):
    global audio_directory
    config = configparser.ConfigParser()
    config.read(rf"{game_directory}\config.ini", encoding='utf-8')

    json_data = {
        "gpt_model_path": config.get('SOVITS', 'gpt_model_path'),
        "sovits_model_path": config.get('SOVITS', 'sovits_model_path')
    }
    if name == 1:
        url = config.get('SOVITS', 'sovits_url1').format(response=response)
    elif name == 2:
        url = config.get('SOVITS', 'sovits_url2').format(response=response)
    elif name == 3:
        url = config.get('SOVITS', 'sovits_url3').format(response=response)
    elif name == 4:
        url = config.get('SOVITS', 'sovits_url4').format(response=response)
    elif name == 5:
        url = config.get('SOVITS', 'sovits_url5').format(response=response)
    else:
        url = config.get('SOVITS', 'sovits_url6').format(response=response)

    requests.post('http://127.0.0.1:9880/set_model', json=json_data)

    try:
        response = requests.get(url)
        with open(rf'{audio_directory}\{output_name}.wav', 'wb') as file:
            file.write(response.content)

    except Exception as e:
        print("语音错误", e)


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

    except FileNotFoundError:
        print("错误:找不到文件 dialogues.json")

    except Exception as e:
        print(f"发生错误:{e}")


def rembg(pic):
    global images_directory
    url = "http://localhost:7000/api/remove"
    file_path = rf"{images_directory}/{pic}.png"

    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})

    with open(file_path, 'wb') as output_file:
        output_file.write(response.content)


def main():
    global book, game_directory, if_already, character_list
    config = configparser.ConfigParser()
    config.read(rf"{game_directory}\config.ini", encoding='utf-8')

    with open(rf'{game_directory}\dialogues.json', 'w') as file:
        file.write("""{\n"conversations": [\n]\n}""")

    with open(rf"{game_directory}\characters.txt", 'w') as file:
        file.write('')

    theme = config.get('生成配置', '剧本的主题')

    title, outline, background, characters = separate_content(
        gpt("现在你是一名gal game剧情设计师，精通写各种各样的gal game剧情，不要使用markdown格式",
            f"现在请你写一份gal game的标题，大纲，背景，人物,我给出的主题是{theme}，你的输出格式为:标题:xx\n大纲:xx\n背景:xx\n人物:xx(每个人物占一行,人物不多于5人)，每个人物的格式是人物名:介绍,无需序号。男主角也要名字").replace(
            "：", ":"))

    book = gpt("现在你是一名galgame剧情作家，精通写各种各样的galgame剧情，请不要使用markdown格式",
               f"现在根据以下内容开始写第一章:gal game标题:{title},gal game大纲:{outline},gal game背景:{background},galgame角色:{characters}。你的输出格式应该为对话模式，例xxx:xx表达，你的叙事节奏要非常非常慢，可以加一点新的内容进去。需要切换地点时，在句尾写[地点名]，[地点名]不可单独一行，不用切换则不写，开头第一句是旁白而且必须要包含地点[]，地点理论上不应该超过3处。不需要标题。输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。")

    lines = book.split('\n')  # 去掉文本最后一行
    book = '\n'.join(lines[:-1])

    booklines = book.splitlines()
    print(book)

    with open(rf"{game_directory}\story.txt", 'w', encoding='utf-8') as file:
        file.write(f"{book}\n")

    with open(rf"{game_directory}\character_info.txt", 'w', encoding='utf-8') as file:
        file.write(characters)

    characterslines = characters.splitlines()
    characterslines = [item for item in characterslines if ":" in item]
    print(characterslines)

    for i in range(len(characterslines)):
        prompt = gpt(
            "根据人物设定给出相应的人物形象，应该由简短的英文单词或短句组成，输出格式样例:a girl,pink hair,black shoes,long hair,young,lovely。请注意，人名与实际内容无关无需翻译出来，只输出英文单词，不要输出多余的内容",
            f"人物形象{characterslines[i]}")

        name = characterslines[i].split(":", 1)[0]
        name = re.sub(r'[^\u4e00-\u9fa5]', '', name)  # 标准化名字
        if config.get('AI绘画', '云端模式'):
            generate_image_pro(prompt, name, "character")
        else:
            generate_image(prompt, name, "character")
        rembg(name)
        character_list.append(name)
        with open(rf"{game_directory}\characters.txt", "a", encoding='utf-8') as file:
            file.write(f"{name}\n")

    for i in booklines:
        if i.strip() != "":
            background = re.findall(r'(?<=\[).*?(?=\])', i)

            if background and background[0] not in background_list:
                prompt = gpt(
                    "把下面的内容翻译成英文并且变成短词,比如red,apple,big这样。请注意，地名与实际内容无关无需翻译出来，例如星之学院应该翻译成academy而不是star academy。下面是你要翻译的内容:",
                    background[0])
                print(prompt)
                if config.get('AI绘画', '云端模式'):
                    generate_image_pro(prompt, background[0], "background")
                else:
                    generate_image(prompt, background[0], "background")
                background_image = background[0]
                background_list.append(background_image)

            else:
                background_image = ""

            i = i.replace("：", ":")

            i = "旁白:" + i if ":" not in i else i

            character, text = i.split(":", 1)
            text1 = re.sub(r'\[.*?\]', '', text)
            text2 = re.sub(r'\（[^)]*\）', '', text1.replace("(", "（").replace(")", "）"))

            try:
                index = character_list.index(character)
                audio_num = index + 1

            except ValueError:
                print(f"{character} 不在列表中")
                audio_num = 6

            if character != "旁白":
                if config.get('SOVITS', '云端模式'):
                    generate_audio_pro(text2, audio_num, text1)
                else:
                    generate_audio(text2, audio_num, text1)

            character = "" if character == "旁白" else character

            if text != "":
                add_dialogue_to_json(character, text2, background_image, text1)

    if_already = True


def story_continue():
    global book, running_state, game_directory, character_list
    running_state = True
    add_dialogue_to_json("", "new", "", "")
    with open(rf"{game_directory}\story.txt", 'r', encoding='utf-8') as file:
        book = file.read()
    with open(rf"{game_directory}\character_info.txt", 'r', encoding='utf-8') as file:
        character_info = file.read()

    add_book = gpt(
        "现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情。只输出文本，不要输出任何多余的。不要使用markdown格式，如果需要切换场景在对话的后面加上[地点]，输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。",
        f"请你根据以下内容继续续写galgame剧情。只返回剧情。人物设定：{character_info}，内容:{book},")

    booklines = add_book.splitlines()
    book = book + "\n" + add_book

    with open(rf'{game_directory}\story.txt', 'w', encoding='utf-8') as file:
        file.write(f"{book}\n")

    for i in booklines:
        if i.strip() != "":
            print(i)
            background = re.findall(r'(?<=\[).*?(?=\])', i)

            if background and background[0] not in background_list:
                prompt = gpt(
                    "把下面的内容翻译成英文并且变成短词,比如red,apple,big这样。请注意，地名与实际内容无关无需翻译出来，例如星之学院应该翻译成academy而不是star academy。下面是你要翻译的内容:",
                    background[0])
                print(prompt)
                if config.get('ai绘画', '云端模式'):
                    generate_image_pro(prompt, background[0], "background")
                else:
                    generate_image(prompt, background[0], "background")
                background_image = background[0]
                background_list.append(background_image)

            else:
                background_image = ""

            i = i.replace("：", ":")

            i = "旁白:" + i if ":" not in i else i

            character, text = i.split(":", 1)
            text1 = re.sub(r'\[.*?\]', '', text)  # 去除地点

            text2 = re.sub(r'\（[^)]*\）', '', text1.replace("(", "（").replace(")", "）"))  # 去除小括号

            try:
                with open(rf"{game_directory}\characters.txt", 'r', encoding='utf-8') as file:
                    line_number = 0
                    for line in file:
                        line_number += 1
                        if character in line:
                            audio_num = line_number
            except ValueError:
                print(f"{character} 不在列表中")
                audio_num = 6

            if character != "旁白" and character != "new":
                if config.get('SOVITS', '云端模式'):
                    generate_audio_pro(text2, audio_num, text1)
                else:
                    generate_audio(text2, audio_num, text1)

            character = "" if character == "旁白" else character

            if text != "":
                add_dialogue_to_json(character, text2, background_image, text1)

    running_state = False


if __name__ == "__main__":
    main()
