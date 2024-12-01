init python:
    import json
    import threading
    import re
    import requests
    import time
    import random
    import os
    import glob
    import configparser

    game_directory = renpy.config.gamedir
    running_state = False
    background_list = []
    if_already = False
    if_music = False
    character_list = []
    current_dialogue_index = 0
    dialogues = []
    characters = {}
    config_content = "xxx"

    if not os.path.exists(fr'{game_directory}/config.ini'):
        with open(fr'{game_directory}/config.ini', 'w') as file:
            file.write(config_content)

    cfg = configparser.ConfigParser()
    cfg.read(f'{game_directory}/config.ini')
    gpt_key = cfg.get('Settings', 'gpt_key', fallback=None)
    base_url = cfg.get('Settings', 'base_url', fallback=None)
    model = cfg.get('Settings', 'model', fallback=None)
    draw_key = cfg.get('Settings', 'draw_key', fallback=None)
    audio_key = cfg.get('Settings', 'audio_key', fallback=None)
    if_proxies = cfg.get('Settings', 'if_proxies', fallback=None)


    def gpt(system, prompt):
        global gpt_key, base_url, model
        key = gpt_key
        url = base_url
        model = model

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
        if response.status_code == 200:
            try:
                content = json.loads(response.text)['choices'][0]['message']['content']
            except ValueError:
                return "error"
        else:
            return "error"
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


    url = "https://cn.tensorart.net/v1/jobs"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {draw_key}"
    }


    def online_generate(prompt, mode):
        print(prompt, mode)
        print("云端启动绘画")
        requests_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        if mode == 'background':
            width = 960
            height = 540
            prompt2 = "(no_human)" + prompt
            model = "611399039965066695"

        else:
            width = 512
            height = 768
            prompt2 = "(upper_body),solo" + prompt
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
                        ** ({"layerDiffusion": {"enable": True, "weight": 0}} if mode != "background" else {})
                    },
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

        if response.status_code == 200:
            id = json.loads(response.text)['job']['id']
            return id
        else:
            print(f"请求失败，状态码：{response.status_code}，请检查是否正确填写了key")
            return "error"


    def get_result(job_id, image_name, mode):
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
                    with open(f'{game_directory}/{image_name}.png', 'wb') as f:
                        f.write(response.content)
                    break


    def generate_image_pro(prompt, image_name, mode):
        id = online_generate(prompt, mode)
        get_result(id, image_name, mode)


    def generate_audio_pro(content, speaker, output_name):
        global audio_key, if_proxies
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
        url = 'https://infer.acgnai.top/infer/gen'
        ip = "160.86.242.23:8080"
        proxies = {
            'http': f'http://{ip}',
            'https': f'https://{ip}',
        }

        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
        except:
            response = requests.post(url, data=json.dumps(data), headers=headers)

        print(json.loads(response.text))

        if response.status_code == 200:
            response_data = json.loads(response.text)
            mp3_url = response_data["audio"]
            try:
                with requests.get(mp3_url) as r:
                    r.raise_for_status()
                    with open(fr'{game_directory}/{output_name}.wav', 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            except Exception as e:
                print(f"proxy error,{e}")
                with requests.get(mp3_url) as r:
                    r.raise_for_status()
                    with open(fr'{game_directory}/{output_name}.wav', 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
            print(f'音频已下载: {output_name}.wav')
        else:
            return "error"


    def generate_music(prompt, filename):
        def run(prompt):
            url = "api.bltcy.ai"
            url1 = f"https://{url}/suno/submit/music"
            key = "sk-Lf7dN6r59Dv9KvHM4b353a777a6247F7Bd4729C6B0E87a28"

            sad = "Pure music, light music, game,galgame,piano,sad"
            common = "Pure music, light music, relaxed,cafe,game,galgame,piano"

            payload = {
                "prompt": "a",
                "tags": sad if prompt == "sad" else common,
                "mv": "chirp-v3-5",
                "title": "BGM",
                "make_instrumental": True
            }

            headers = {
                'Authorization': f'Bearer {key}',
                'Accept': 'application/json',
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'application/json'
            }
            response = requests.post(url1, headers=headers, json=payload)
            id = json.loads(response.text)["data"]
            return id

        def download_music(id, filename):
            url = "api.bltcy.ai"
            url2 = f"https://{url}/suno/fetch/{id}"
            key = "sk-Lf7dN6r59Dv9KvHM4b353a777a6247F7Bd4729C6B0E87a28"

            payload = {}
            headers = {
                'Authorization': f'Bearer {key}',
                'Accept': 'application/json',
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'application/json'
            }
            while True:
                response = requests.request("GET", url2, headers=headers, data=payload)
                json.loads(response.text)
                response_data = json.loads(response.text)

                if response_data['data']["status"] == 'SUCCESS':

                    audio_urls = [item["audio_url"] for item in response_data["data"]["data"]]
                    with requests.get(audio_urls[0], stream=True) as r:
                        with open(fr"{game_directory}/{filename}.mp3", 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    print(f"文件 {filename} 已下载。")
                    with requests.get(audio_urls[1], stream=True) as r:
                        with open(fr"{game_directory}/{filename}2.mp3", 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    print(f"文件 {filename}2 已下载。")
                    break

        download_music(run(prompt), filename)


    # ----------------------------------------------------------------------


    def add_dialogue_to_json(character, text, background_image, audio):
        global game_directory

        try:
            with open(rf"{game_directory}/dialogues.json", "r", encoding="utf-8") as file:
                dialogues = json.load(file)

            dialogues["conversations"].append({
                "character": character,
                "text": text,
                "background_image": background_image,
                "audio": audio
            })

            with open(rf"{game_directory}/dialogues.json", "w", encoding="utf-8") as file:
                json.dump(dialogues, file, indent=4, ensure_ascii=False)

            print("新的对话已成功添加到dialogues.json文件中")

        except FileNotFoundError:
            print("错误:找不到文件 dialogues.json")

        except Exception as e:
            print(f"发生错误:{e}")




    def choose_story():
        with open(rf"{game_directory}/story.txt", 'r', encoding='utf-8') as file:
            book = file.read()
        choices = gpt("你是galgame剧情家，精通各种galgame写作",
                      f"根据galgame剧情,以男主角的视角，设计男主角接下来的三个分支选项。内容:{book},返回格式:1.xxx\n2.xxx\n3.xxx,要求每个选项尽量简短。不要使用markdown语法。")
        cleaned_text = '\n'.join([line.split('. ', 1)[1] if '. ' in line else line for line in choices.strip().split('\n')])
        with open(rf"{game_directory}/choice.txt", 'w', encoding='utf-8') as file:
            file.write(cleaned_text)
        return cleaned_text

    semaphore = threading.BoundedSemaphore(value=10)
    threads = []
    thread2s = []


    def start_online_draw_threads(prompt, image_name, mode):
        global threads
        thread = threading.Thread(target=generate_image_pro, args=(prompt, image_name, mode))
        thread.start()
        threads.append(thread)


    def start_online_audio_threads(content, speaker, output_name):
        global thread2s, semaphore

        def thread_function(content, speaker, output_name):
            try:
                generate_audio_pro(content, speaker, output_name)
            finally:
                semaphore.release() 

        semaphore.acquire()
        thread = threading.Thread(target=thread_function, args=(content, speaker, output_name))
        thread.start()
        thread2s.append(thread)


    def main():
        global book, game_directory, if_already, character_list
        namelist = []

        with open(rf'{game_directory}/dialogues.json', 'w') as file:
            file.write("""{\n"conversations": [\n]\n}""")

        with open(rf"{game_directory}/characters.txt", 'w') as file:
            file.write('')

        theme = "校园恋爱"

        title, outline, background, characters = separate_content(
            gpt("现在你是一名gal game剧情设计师，精通写各种各样的gal game剧情，不要使用markdown格式",
                f"现在请你写一份gal game的标题，大纲，背景，人物,我给出的主题和要求是{theme}，你的输出格式为:标题:xx\n大纲:xx\n背景:xx\n人物:xx(每个人物占一行,人物不多于5人)，每个人物的格式是人物名:介绍,无需序号。男主角也要名字").replace(
                "：", ":"))

        book = gpt("现在你是一名galgame剧情作家，精通写各种各样的galgame剧情，请不要使用markdown格式",
                   f"现在根据以下内容开始写第一章:gal game标题:{title},gal game大纲:{outline},gal game背景:{background},galgame角色:{characters}。你的输出格式应该为对话模式，例xxx:xx表达，你的叙事节奏要非常非常慢，可以加一点新的内容进去。需要切换地点时，在句尾写[地点名]，[地点名]不可单独一行，不用切换则不写，开头第一句是旁白而且必须要包含地点[]，地点理论上不应该超过3处。不需要标题。输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。不要出现（）")

        lines = book.split('\n')  # 去掉文本最后一行
        book = '\n'.join(lines[:-1])

        booklines = book.splitlines()
        print(book)

        with open(rf"{game_directory}/story.txt", 'w', encoding='utf-8') as file:
            file.write(f"{book}\n")

        with open(rf"{game_directory}/character_info.txt", 'w', encoding='utf-8') as file:
            file.write(characters)

        characterslines = characters.splitlines()
        characterslines = [item for item in characterslines if ":" in item]

        for i in range(len(characterslines)):
            prompt = gpt(
                "根据人物设定给出相应的人物形象，应该由简短的英文单词或短句组成，输出格式样例:a girl,pink hair,black shoes,long hair,young,lovely。请注意，人名与实际内容无关无需翻译出来，只输出英文单词，不要输出多余的内容，一定要输出角色的性别",
                f"人物形象{characterslines[i]}")

            name = characterslines[i].split(":", 1)[0]
            name = re.sub(r'[^\u4e00-\u9fa5]', '', name)  # 标准化名字
            start_online_draw_threads(prompt, name, "character")
            character_list.append(name)
            with open(rf"{game_directory}/characters.txt", "a", encoding='utf-8') as file:
                file.write(f"{name}\n")
        print(characterslines)

        for i in booklines:
            if i.strip() != "":
                i = re.sub(r'[【】]', lambda x: '[' if x.group() == '【' else ']', i)
                background = re.findall(r'(?<=\[).*?(?=\])', i)

                if background and background[0] not in background_list:
                    prompt = gpt(
                        "把下面的内容翻译成英文并且变成短词,比如red,apple,big这样。请注意，地名与实际内容无关无需翻译出来，例如星之学院应该翻译成academy而不是star academy。你应该只返回英文单词，下面是你要翻译的内容:",
                        background[0])
                    print(prompt)

                    start_online_draw_threads(prompt, background[0], "background")

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
                    start_online_audio_threads(text2, audio_num, text1)

                character = "" if character == "旁白" else character

                if text != "":
                    add_dialogue_to_json(character, text2, background_image, text1)

        for thread in threads:
            thread.join()
        for thread in thread2s:
            thread.join()
        choose_story()
        if_already = True


    def story_continue(choice):
        global book, running_state, game_directory, character_list
        running_state = True
        with open(rf"{game_directory}/story.txt", 'r', encoding='utf-8') as file:
            book = file.read()
        with open(rf"{game_directory}/character_info.txt", 'r', encoding='utf-8') as file:
            character_info = file.read()

        add_book = gpt(
            "现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情。只输出文本，不要输出任何多余的。不要使用markdown格式，如果需要切换场景在对话的后面加上[地点]，输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。",
            f"请你根据以下内容继续续写galgame剧情。只返回剧情。人物设定：{character_info}，内容:{book},我选则的分支是{choice}")

        booklines = add_book.splitlines()
        book = book + "\n" + add_book

        with open(rf'{game_directory}/story.txt', 'w', encoding='utf-8') as file:
            file.write(f"{book}\n")

        for i in booklines:
            if i.strip() != "":
                background = re.findall(r'(?<=\[).*?(?=\])', i)

                if background and background[0] not in background_list:
                    prompt = gpt(
                        "把下面的内容翻译成英文并且变成短词,比如red,apple,big这样。请注意，地名与实际内容无关无需翻译出来，例如星之学院应该翻译成academy而不是star academy。你应该只返回英文单词，下面是你要翻译的内容:",
                        background[0])
                    print(prompt)

                    start_online_draw_threads(prompt, background[0], "background")

                    background_image = background[0]
                    background_list.append(background_image)

                else:
                    background_image = ""

                i = i.replace("：", ":")

                i = "旁白:" + i if ":" not in i else i

                character, text = i.split(":", 1)
                text1 = re.sub(r'\[.*?\]', '', text)

                text2 = re.sub(r'\（[^)]*\）', '', text1.replace("(", "（").replace(")", "）"))  # 去除小括号

                try:
                    with open(rf"{game_directory}/characters.txt", 'r', encoding='utf-8') as file:
                        line_number = 0
                        for line in file:
                            line_number += 1
                            if character in line:
                                audio_num = line_number
                except ValueError:
                    print(f"{character} 不在列表中")
                    audio_num = 6

                if character != "旁白" and character != "new":
                    start_online_audio_threads(text2, audio_num, text1)

                character = "" if character == "旁白" else character

                if text != "":
                    add_dialogue_to_json(character, text2, background_image, text1)
        for thread in threads:
            thread.join()
        for thread in thread2s:
            thread.join()
        choose_story()
        running_state = False


    def list_change(a, b, c):
        original_list = [a, b, c, "让我自己输入"]
        choices = ['choice1', 'choice2', 'choice3', 'user_input']
        transformed_list = [[item, choice] for item, choice in zip(original_list, choices)]
        return transformed_list


    def create_thread(arg):
        thread = threading.Thread(target=story_continue, args=(arg,), daemon=True)
        thread.start()
        return thread


    def load_dialogues(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["conversations"]


    def read(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
        return data


    def get_next_dialogue():
        global current_dialogue_index
        if current_dialogue_index < len(dialogues):
            dialogue = dialogues[current_dialogue_index]
            current_dialogue_index += 1
            return dialogue
        else:
            return None


    def remove_data():

        global game_directory
        png_files = glob.glob(os.path.join(game_directory, "*.png"))
        wav_files = glob.glob(os.path.join(game_directory, "*.wav"))

        for file_path in png_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

        for file_path in wav_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")



image loading movie = Movie(play="loading.webm")
define small_center = Transform(xalign=0.5, yalign=1.0, xpos=0.5, ypos=1.0, xzoom=0.7, yzoom=0.7)


label start:
    $ start_list = [["重新开始新的游戏","1"],["继续上一次的游戏","2"]]
    $ answer = renpy.display_menu(start_list, interact=True, screen='choice')
    if  answer == "1":
        $ remove_data()
        $ t = threading.Thread(target=main,daemon = True)
        show loading movie
        $ t.start()
        while not if_already:
            $ renpy.pause(1, hard=True)
        scene black
        "资源加载完成,单击开始游戏"
    else:
        python:
            with open(f'{game_directory}/characters.txt', 'r', encoding='utf-8') as file:
                lines = file.readlines()
                character_list = [line.strip() for line in lines]


    if if_music:
        play music "happy bgm1.mp3"
    while True:
        $ dialogues = load_dialogues(rf"{game_directory}/dialogues.json")
        $ dialogue = get_next_dialogue()

        if dialogue is None:
            $ extracted_lines = read(rf"{game_directory}/choice.txt")
            $ extracted_lines = extracted_lines.strip().split('\n')
            $ choice1 = extracted_lines[0]
            $ choice2 = extracted_lines[1]
            $ choice3 = extracted_lines[2]
            $ choice_list=list_change(choice1,choice2,choice3)
            $ answer = renpy.display_menu(choice_list, interact=True, screen='choice')
            if answer == "user_input":
                $ answer = renpy.input("请输入你接下来的选择:")
            $ create_thread(answer)
            $ renpy.pause(0.5, hard=True)
            while running_state:
                $ renpy.pause(1, hard=True)
            $ dialogues = load_dialogues(rf"{game_directory}/dialogues.json")
            $ dialogue = get_next_dialogue()

        $ character_name = dialogue["character"]
        $ text = dialogue["text"]
        if dialogue['background_image'] != "":
            $ background_image = f"{dialogue['background_image']}.png"
        else:
            $ background_image = ""
        $ audio = f"{dialogue['audio']}.wav"
        if dialogue['character'] in character_list:
            $ character_image = f"{dialogue['character']}.png"
        else:
            $ character_image = ""

        if character_name not in characters:
            $ characters[character_name] = Character(character_name)
        if character_name:
            $ renpy.sound.play(audio, channel='sound')

        if background_image:
            scene expression background_image
        if character_image:
            show expression character_image at small_center

        $ renpy.say(characters[character_name], text)

    return

label config:
    $ config_successful = False

    while not config_successful:
        $ gpt_key = renpy.input("请输入gpt密钥") or gpt_key
        $ base_url = renpy.input("请输入base_url") or base_url
        $ model = renpy.input("请输入模型名称") or model
        $ test = gpt("you are an AI", "1+1=")

        if test == "error":
            "gpt配置有误，请重新输入，或检查网络"
        else:
            "gpt配置成功！"
            $ cfg.set('Settings', 'gpt_key', gpt_key)
            $ cfg.set('Settings', 'base_url', base_url)
            $ cfg.set('Settings', 'model', model)
            $ config_successful = True
    $ config_successful = False
    while not config_successful:
        $ draw_key = renpy.input("请输入AI绘画密钥") or draw_key
        $ test = online_generate("a girl","character")
        if test == "error":
            "AI绘画密钥有误，请重新输入，或检查网络"
        else:
            "AI绘画配置成功！"
            $ cfg.set('Settings', 'draw_key', draw_key)

            $ config_successful = True
    $ config_successful = False
    while not config_successful:
        $ audio_key = renpy.input("请输入AI语音密钥") or audio_key
        $ if_proxies = renpy.input("是否开启代理，内置默认代理，可以加快生成速度，但是不稳定,关闭输入0，否则开启") or audio_key
        $ if_proxies = (if_proxies == "0")
        $ cfg.set('Settings', 'if_proxies', str(if_proxies))
        $ test = generate_audio_pro("测试",1,"test")
        if test == "error":
            "AI语音密钥有误，请重新输入，或关闭代理试试"
        else:
            "AI语音配置成功！"
            $ cfg.set('Settings', 'audio_key', audio_key)
            $ config_successful = True
    python:
        with open(f'{game_directory}/config.ini', 'w') as configfile:
            cfg.write(configfile)
    return
