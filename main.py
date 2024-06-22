import requests
import json
import re
import base64
import os

import renpy #调试时需要把这行注释掉

running_state = False
background_list = []
if_already = False

character_list = []
game_directory = renpy.config.basedir
# game_directory = r"D:\renpy-8.1.1-sdk.7z\AI GAL" #默认使用上者，调试py文件时修改路径地址使用
game_directory = os.path.join(game_directory, "game")
images_directory = os.path.join(game_directory, "images")
audio_directory = os.path.join(game_directory, "audio")


def gpt(system, prompt, mode="default"):
    config.read('config.ini', encoding='utf-8')
    key = config.get('CHATGPT', 'GPT_KEY')
    url = config.get('CHATGPT', 'BASE_URL')
    if mode == "default":
        url = "https://one-api.bltcy.top/v1/chat/completions"
        key = "sk-Lf7dN6r59Dv9KvHM4b353a777a6247F7Bd4729C6B0E87a28"
        model = "gpt-4o"

    elif mode == "free":
        url = "https://one.caifree.com/v1/chat/completions"
        key = "sk-RD8n3ajylKBA6178505eB1D34300485683E279EbBc90D2B8"
        model = "gpt-4"

    elif mode == "deepseek":
        url = "https://api.deepseek.com/v1/chat/completions"
        key = "sk-c05703ac68b74c3f8c6e6429bc2a82fa"
        model = "deepseek-chat"

    elif mode == "Baichuan":
        key = 'sk-d174a0e509f628026d155fa1f2da4b96'
        url = 'https://api.baichuan-ai.com/v1/chat/completions'
        model = "Baichuan4"

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


def fenli(text):
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
    config.read('config.ini', encoding='utf-8')

    json_data = {
        "gpt_model_path": config.get('SOVITS', 'gpt_model_path'),
        "sovits_model_path": config.get('SOVITS', 'sovits_model_path')
    }
    if name == 1:
        url = config.get('SOVITS', 'sovits_url1').format(response=response)
        url = f"url"
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

    with open(rf'{game_directory}\dialogues.json', 'w') as file:
        file.write("""{\n"conversations": [\n]\n}""")

    with open(rf"{game_directory}\characters.txt", 'w') as file:
        file.write('')

    title, outline, background, characters = fenli(
        gpt("现在你是一名gal game剧情设计师，精通写各种各样的gal game剧情，不要使用markdown格式",
            "现在请你写一份gal game的标题，大纲，背景，人物,你的输出格式为:标题:xx\n大纲:xx\n背景:xx\n人物:xx(每个人物占一行,人物不多于5人)，每个人物的格式是人物名:介绍,无需序号。男主角也要名字").replace(
            "：", ":"))

    book = gpt("现在你是一名galgame剧情作家，精通写各种各样的galgame剧情，请不要使用markdown格式",
               f"现在根据以下内容开始写第一章:gal game标题:{title},gal game大纲:{outline},gal game背景:{background},galgame角色:{characters}。你的输出格式应该为对话模式，例xxx:xx表达，你的叙事节奏要非常非常慢，可以加一点新的内容进去。需要切换地点时，在句尾写[地点名]，[地点名]不可单独一行，不用切换则不写，开头第一句是旁白而且必须要包含地点[]，地点理论上不应该超过3处。不需要标题。输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。")

    lines = book.split('\n')  # 去掉文本最后一行
    book = '\n'.join(lines[:-1])

    booklines = book.splitlines()
    print(book)

    characters = re.sub(r'[^\u4e00-\u9fa5]', '', characters)  # 标准化名字

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
                generate_audio(text2, audio_num, text1)

            character = "" if character == "旁白" else character

            if text != "":
                add_dialogue_to_json(character, text2, background_image, text1)

    running_state = False


if __name__ == "__main__":
    generate_image_pro("a girl,sea,night,", "123", "character")
