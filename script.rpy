init python:
    import json
    import os
    import string
    import threading
    from main import main,story_continue,generate_new_chapters_state,already_state
    from GPT import gpt,gpt_context
    from local_vocal_generator import generate_audio
    from trs2 import translate_gpt

    def list_change(*args, mode="story"):
        original_list = list(args)
        if mode == "story":
            choices = [*args, 'user_input']
            original_list.append("让我自己输入")
            choices.append('user_input')
        else:
            choices = [f'choice{i+1}' for i in range(len(args))]
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

    def get_gpt_response(system,ask, history, result_container,id):
        global ok
        ok = False
        result = gpt_context(f"现在你要扮演以下角色:{system},你的语气应当生动，有自己的情绪，尽量让对话流畅自然。你的话语会让人觉得可爱和有趣，并逐渐展露暖面,语言简短精炼，不要用()", ask,history=history)
        generate_audio("V2",translate(result),id,"response")
        result_container.append(result)
        ok = True

    current_dialogue_index = 0
    dialogues = []
    characters = {}
    game_directory = renpy.config.gamedir

image loading movie = Movie(play="gui/custom/loading.webm")
image bedroom = "talk/bedroom.jpg"
image sea = "talk/海.jpg"
image warning = "gui/warning.png"
image logo = "gui/custom/logo.png"
define small_center = Transform(xalign=0.5, yalign=1.0, xpos=0.5, ypos=1.0, xzoom=0.7, yzoom=0.7)
image eileen movie = Movie(play="gui/custom/background.webm")
image load = "gui/custom/load.png"

transform shake:
    yoffset 0
    linear 0.1 yoffset -30
    linear 0.1 yoffset 0

transform spin:
    xpos 0.05
    ypos 0.65
    rotate 0
    linear 1.0 rotate 360
    repeat

transform my_position:
    xalign 0.25
    yalign 0.8


label splashscreen:
    scene black
    play sound "gui/custom/logo.mp3"
    show logo with Dissolve(1)
    $ renpy.pause(2)
    hide logo with Dissolve(1)
    return


label talk_mode:
    show eileen movie
    python:
        extracted_lines = read(os.path.join(game_directory, "characters.txt"))
        extracted_lines = extracted_lines.strip().split('\n')
        choice1, choice2, choice3, choice4 = extracted_lines[1:5]
        choice_list = list_change(choice1, choice2, choice3, choice4,mode="talk")
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
        $ renpy.show(character,at_list=[small_center])
        $ ask = renpy.input("请输入你的对话:")
        $ response_container = []
        $ info = read(os.path.join(game_directory, "character_info.txt"))
        $ lines = info.splitlines()
        $ system= lines[2*id - 2]

        $ gpt_thread = threading.Thread(target=get_gpt_response, args=(system,ask, history, response_container,id))
        $ gpt_thread.start()
        while not ok:
            $ renpy.pause(0.5, hard=True)
        $ response = response_container[0]
        $ renpy.show(character,at_list=[shake])
        $ renpy.sound.play("audio/response.wav", channel='sound')
        $ renpy.say(character, f"『{response}』")
        $ history.append({"role": "assistant", "content": response})
        $ history.append({"role": "user", "content": ask})
    return


label start:
    if os.path.getsize(os.path.join(game_directory, "story.txt")) == 0:
        $ t = threading.Thread(target=main,daemon = True)
        show sea
        show load at spin
        show text "{color=#000000}{size=72}大纲生成中...{/size}{/color}" at my_position

        $ t.start()
        while already_state != True:
            if already_state == "story":
                hide text
                show text "{color=#000000}{size=72}故事生成中...{/size}{/color}" at my_position
            elif already_state == "picture":
                hide text
                show text "{color=#000000}{size=72}图像生成中...{/size}{/color}" at my_position
            elif already_state == "audio":
                hide text
                show text "{color=#000000}{size=72}语音生成中...{/size}{/color}" at my_position
            $ renpy.pause(1, hard=True)
            $ from main import already_state
        scene black
        stop music
        "资源加载完成,单击开始游戏"
        $ renpy.pause(1,hard = True)
        show warning with Dissolve(2)
        $ renpy.pause(3,hard = True)
        hide warning with Dissolve(2)

    stop music
    if os.path.exists(os.path.join(game_directory, "music", "happy bgm.mp3")):
        play music [ "music/happy bgm.mp3", "music/happy bgm2.mp3" ] fadeout 2.0 fadein 2.0
    while True:
        $ dialogues = load_dialogues(os.path.join(game_directory, "dialogues.json"))
        $ dialogue = get_next_dialogue()

        if dialogue is None:
            $ extracted_lines = read(os.path.join(game_directory, "choice.txt"))
            $ extracted_lines = extracted_lines.strip().split('\n')
            $ choice1, choice2, choice3 = extracted_lines[:3]
            $ choice_list=list_change(choice1,choice2,choice3)
            $ answer = renpy.display_menu(choice_list, interact=True, screen='choice')
            if answer == "user_input":
                $ answer = renpy.input("请输入你接下来的选择:")
            $ create_thread(answer)
            show load at spin
            show text "{color=#000000}{size=72}剧情生成中...{/size}{/color}" at my_position
            $ renpy.pause(0.5, hard=True)
            $ from main import generate_new_chapters_state
            while generate_new_chapters_state:
                $ renpy.pause(1, hard=True)
                $ from main import generate_new_chapters_state
            hide text
            hide load
            $ dialogues = load_dialogues(os.path.join(game_directory, "dialogues.json"))
            $ dialogue = get_next_dialogue()

        $ character_name = dialogue["character"]
        $ text = dialogue["text"]
        if os.path.exists(os.path.join(game_directory, "images", f"{dialogue['background_image']}.png")):
            $ background_image = f"images/{dialogue['background_image']}.png"
        else:
            $ background_image = ""
        $ audio = f"{dialogue['audio']}.wav"
        if os.path.exists(os.path.join(game_directory, "images", f"{dialogue['character']}.png")):
            $ character_image = f"images/{dialogue['character']}.png"
        else:
            $ character_image = ""
        if character_name not in characters:
            $ characters[character_name] = Character(character_name)
        if character_name:
            $ renpy.sound.play(audio, channel='sound')
        if background_image:
            scene expression background_image with fade
        if character_image:
            show expression character_image at small_center with dissolve
        $ text = text[:-1]
        $ renpy.say(characters[character_name], f"『{text}』"if character_name != "" else text)
    return
