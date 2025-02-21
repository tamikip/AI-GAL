import re
import os
import requests
import json
import configparser
import threading
from GPT import gpt
from music_generator import generate_music
from local_image_generator import generate_image
from cloud_image_generator import online_generate_image
from local_vocal_generator import generate_audio
from cloud_vocal_generator import online_generate_audio
from trs2 import translate

ILLEGAL_CHAR_REPLACEMENTS = {
    '!': '！',
    '?': '？',
    ':': '：',
    '"': '“',
    '/': '／',
    '\\': '＼',
    '|': '｜',
    '*': '＊',
    '<': '＜',
    '>': '＞'
}

try:
    import renpy

    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
images_directory = os.path.join(game_directory, "images")

config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')
sovits_type = "V2" if config.get('SOVITS', 'version') == "1" else "V1"
Theme_Language = config.get('剧情', 'Language')

generate_new_chapters_state = False
background_list = []
if_already = False
threads = []
thread2s = []
character_list = []


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
    thread2s.append(thread)


def main():
    global story_content, game_directory, if_already, character_list, sovits_type
    print("\n============分界线============\n")
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
        theme_add = config.get('剧情', "outline")
        with open(theme_add, 'r', encoding='utf-8') as file:
            theme = file.read()
    except:
        pass

    title, outline, background, characters = separate_content(
        gpt("现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情，不要使用markdown格式",
            f"现在请你写一份galgame的标题，大纲，背景，人物,我给出的主题和要求是{theme}，你的输出格式为:标题:xx\n大纲:xx\n背景:xx\n人物:xx"
            f"(每个人物占一行,人物不多于5人,人物要求包括外貌性格等特点，一男多女，男主放第一的位置，介绍人物时要提及性别)，每个人物的格式是人物名:介绍,无需序号。男主角也要名字").replace(
            "：", ":"))

    story_content = gpt("现在你是一名galgame剧情作家，精通写各种各样的galgame剧情，请不要使用markdown格式",
                        f"现在根据以下内容开始写第一章:galgame标题:{title},galgame大纲:{outline},galgame背景:{background},galgame角色:{characters}。"
                        f"你的输出格式应该为对话模式，例:角色A:你好。你的叙事节奏要非常慢，可以加一点新的内容进去。需要切换地点时，在句尾写[地点名]，[地点名]不可单独一行，不用切换则不写，"
                        f"开头第一句是旁白而且必须要包含地点[]，地点理论上不应该超过3处。不需要标题。"
                        f"输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx。"
                        f"角色名字要完整。不要出现小括号。请你使用{Theme_Language}输出角色的台词(不用加引号)，包括旁白也要用{Theme_Language}输出，而引号前面的角色名，中括号的地点保持回中文。")

    lines = story_content.split('\n')  # 去掉文本最后一行,因为ai会经常总结内容
    story_content = '\n'.join(lines[:-1])

    def clean_filename(filename):
        for illegal_char, replacement in ILLEGAL_CHAR_REPLACEMENTS.items():
            filename = filename.replace(illegal_char, replacement)
        return filename

    story_content = clean_filename(story_content)
    book_lines = story_content.splitlines()
    print(story_content)

    with open(rf"{game_directory}\story.txt", 'w', encoding='utf-8') as file:
        file.write(f"{story_content}\n")

    with open(rf"{game_directory}\title.txt", 'w', encoding='utf-8') as file:
        file.write(f"{title}\n")

    with open(rf"{game_directory}\character_info.txt", 'w', encoding='utf-8') as file:
        file.write(characters)

    characters_lines = characters.splitlines()
    characters_lines = [item for item in characters_lines if ":" in item]
    print(characters_lines)

    for i in range(len(characters_lines)):
        print(characters_lines[i])
        prompt = gpt(
            "根据人物设定给出相应的人物形象，应该由简短的英文单词或短句组成，一定要加上角色的性别。输出格式样例:"
            "a girl,pink hair,black shoes,long hair,young,lovely。请注意，人名与实际内容无关无需翻译出来，只输出英文单词，不要输出多余的内容",
            f"人物形象{characters_lines[i]}")
        print(prompt)

        name = characters_lines[i].split(":", 1)[0]
        name = re.sub(r'[^\u4e00-\u9fa5]', '', name)  # 标准化名字
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
