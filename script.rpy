# list_change函数下choices删除重复添加的问题
# 将配置管理集中到 config.toml 文件中
# 添加了 last_background_image 和 last_character_image 变量来跟踪最后显示的图像，避免不必要的重绘和闪烁
# 优化了图像和音频资源的加载逻辑，使用更简洁的条件表达式
# 增加了对 story.txt 文件是否存在的检查，如果不存在则创建
# 优化了对话选择逻辑，添加了空行过滤
# 简化了音频文件路径处理，移除了硬编码的 .wav 扩展名
init python:
    import json
    import os
    import threading
    from game_generator import GameGenerator
    from GPT import gpt_context
    from local_vocal_generator import generate_audio
    from cloud_vocal_generator import online_generate_audio


    config_path = os.path.join(renpy.config.gamedir, "config.toml")
    generator = GameGenerator(config_path)

    # 处理并且整合生成好的分支选项。使其符合renpy的格式
    def list_change(*args, mode="story"):
        original_list = list(args)
        if mode == "story":
            choices = [*args, 'user_input']
            original_list.append("让我自己输入")
        else:
            choices = [f'choice{i+1}' for i in range(len(args))]
        transformed_list = [[item, choice] for item, choice in zip(original_list, choices)]
        return transformed_list

    # 创建一个新的后台线程，异步执行 story_continue 函数
    def create_thread(arg):
        thread = threading.Thread(target=generator.story_continue, args=(arg,), daemon=True)
        thread.start()
        return thread

    # 读取文件内容
    def read(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
        return data

    # 从生成器的内存对话中获取下一个对话
    def get_next_dialogue():
        global current_dialogue_index
        if current_dialogue_index < len(generator.dialogues["conversations"]):
            dialogue = generator.dialogues["conversations"][current_dialogue_index]
            current_dialogue_index += 1
            return dialogue
        else:
            return None

    # 获取GPT回复并生成音频
    def get_gpt_response(system, ask, history, result_container, id):
        global ok
        ok = False
        result = gpt_context(f"现在你要扮演以下角色:{system},你的语气应当生动，有自己的情绪，尽量让对话流畅自然。你的话语会让人觉得可爱和有趣，并逐渐展露暖面,语言简短精炼，不要用()", ask, history=history)
        if generator.if_generate_audio:
            if generator.if_cloud_audio:
                online_generate_audio(result, id, "response")
            else:
                generate_audio(result, id, "response")
        result_container.append(result)
        ok = True

    current_dialogue_index = 0
    characters = {}
    game_directory = renpy.config.gamedir
    music_path = os.path.join(game_directory, "music", "happy bgm.mp3")

    # 追踪最后显示的图像，以避免可能导致闪烁的冗余更新
    last_background_image = ""
    last_character_image = ""

image loading movie = Movie(play="gui/custom/loading.webm")
image warning = "gui/warning.png"
image bedroom = "talk/bedroom.jpg"
image sea = "talk/海.jpg"
image logo = "gui/custom/logo.png"
define small_center = Transform(xalign=0.5, yalign=1.0, xpos=0.5, ypos=1.0, xzoom=0.7, yzoom=0.7)
image eileen movie = Movie(play="gui/custom/background.webm")
image load = "gui/custom/load.png"

# 人物抖动样式,仅在对话模式生效
transform shake:
    yoffset 0
    linear 0.1 yoffset -30
    linear 0.1 yoffset 0

# 进软件前的logo
label splashscreen:
    scene black
    play sound "gui/custom/logo.mp3"
    show logo with Dissolve(1)
    $ renpy.pause(2)
    hide logo with Dissolve(1)
    return

# 对话模式
label talk_mode:
    show eileen movie
    python:
        extracted_lines = read(os.path.join(game_directory, "characters.txt"))
        extracted_lines = extracted_lines.strip().split('\n')
        choice1, choice2, choice3, choice4 = extracted_lines[1:5]
        choice_list = list_change(choice1, choice2, choice3, choice4, mode="talk")
        character_choice = renpy.display_menu(choice_list, interact=True, screen='choice')
        character_choices = {
            "choice1": choice1,
            "choice2": choice2,
            "choice3": choice3,
            "choice4": choice4
        }
        character = character_choices.get(character_choice)
        id = int(''.join(filter(str.isdigit, character_choice))) + 1
        history = []
    while True:
        scene bedroom
        stop music
        $ renpy.show(character, at_list=[small_center])
        $ ask = renpy.input("请输入你的对话内容:")
        $ response_container = []
        $ info = read(os.path.join(game_directory, "character_info.txt"))
        $ lines = info.splitlines()
        $ system = lines[2 * id - 2]

        $ gpt_thread = threading.Thread(target=get_gpt_response, args=(system, ask, history, response_container, id))
        $ gpt_thread.start()
        while not ok:
            $ renpy.pause(0.5, hard=True)
        $ response = response_container[0]
        $ renpy.show(character, at_list=[shake])
        if generator.if_generate_audio:
            $ renpy.sound.play("audio/response.mp3", channel='sound')
        $ renpy.say(character, f"『{response}』")
        $ history.append({"role": "assistant", "content": response})
        $ history.append({"role": "user", "content": ask})
    return

# 剧情模式
label start:
    if not os.path.exists(os.path.join(game_directory, "story.txt")):
        python:
            with open(os.path.join(game_directory, "story.txt"), 'w') as f:
                f.write('Start')

    if os.path.getsize(os.path.join(game_directory, "story.txt")) == 0:
        $ t = threading.Thread(target=generator.main, daemon=True)
        show sea
        $ t.start()
        "大纲生成中..."
        while generator.already_state != "complete":
            if generator.already_state == "story":
                "故事生成中..."
            elif generator.already_state == "picture":
                "图片生成中..."
            elif generator.already_state == "audio":
                "语音生成中..."
            $ renpy.pause(1, hard=True)
        scene black
        stop music
        "资源加载完成,单击开始游戏"
        $ renpy.pause(1, hard=True)
        scene warning
        $ renpy.pause(5, hard=True)


    stop music
    if os.path.exists(music_path):
        play_music = [
            os.path.join("music", "happy bgm.mp3").replace("\\", "/"),
            os.path.join("music", "happy bgm2.mp3").replace("\\", "/")
        ]
    else:
        play_music = [
            os.path.join("music", "default.mp3").replace("\\", "/"),
            os.path.join("music", "default2.mp3").replace("\\", "/")
        ]
    play music play_music fadeout 2.0 fadein 2.0
    while True:
        $ dialogue = get_next_dialogue()

        if dialogue is None:
            $ extracted_lines = read(os.path.join(game_directory, "choice.txt"))
            $ extracted_lines = [line.strip() for line in extracted_lines.strip().splitlines() if line.strip()]
            $ choice1, choice2, choice3 = extracted_lines[:3]
            $ choice_list = list_change(choice1, choice2, choice3)
            $ answer = renpy.display_menu(choice_list, interact=True, screen='choice')
            if answer == "user_input":
                $ answer = renpy.input("请输入你接下来的选择:")
            $ create_thread(answer)
            $ renpy.pause(0.5, hard=True)
            while generator.generate_new_chapters_state:
                $ renpy.pause(1, hard=True)
            hide text
            hide load
            $ dialogue = get_next_dialogue()

        $ character_name = dialogue["character"]
        $ text = dialogue["text"]
        $ background_image = f"images/{dialogue['background_image']}.png" if dialogue['background_image'] and os.path.exists(os.path.join(game_directory, "images", f"{dialogue['background_image']}.png")) else ""
        $ audio = f"{dialogue['audio']}"
        $ character_image = f"images/{dialogue['character']}.png" if dialogue['character'] and os.path.exists(os.path.join(game_directory, "images", f"{dialogue['character']}.png")) else ""

        if character_name not in characters:
            $ characters[character_name] = Character(character_name)
        if character_name and generator.if_generate_audio:
            $ renpy.sound.play(audio, channel='sound')
        # 仅当背景发生变化时才更新
        if background_image and background_image != last_background_image:
            scene expression background_image with fade
            $ last_background_image = background_image
        # 仅当立绘发生变化时才更新
        if character_image and character_image != last_character_image:
            show expression character_image at small_center with dissolve
            $ last_character_image = character_image
        $ text = text[:-1]
        $ renpy.say(characters[character_name], f"『{text}』" if character_name != "" else text)
    return