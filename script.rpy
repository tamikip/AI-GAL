init python:
    import json
    import os
    import string
    import threading
    from main import main,story_continue,generate_new_chapters_state,if_already
    from GPT import gpt
    import configparser
    from local_vocal_generator import generate_audio

    def list_change(*args, mode="story"):
        original_list = list(args)
        choices = [f'choice{i+1}' for i in range(len(args))]

        if mode == "story":
            original_list.append("让我自己输入")
            choices.append('user_input')

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
        result = gpt(f"现在你要扮演以下角色:{system},你的语气应当生动，有自己的情绪，尽量让对话流畅自然。你的话语会让人觉得可爱和有趣，并逐渐展露出温暖一面,语言简短精炼，不要用()", ask, mode="context", history=history)
        generate_audio("V2",result,id,"response")
        result_container.append(result)
        ok = True

    current_dialogue_index = 0
    dialogues = []
    characters = {}
    game_directory = renpy.config.gamedir

image loading movie = Movie(play="loading.webm")
image bedroom = "talk/bedroom.jpg"
image sea = "talk/海.jpg"
define small_center = Transform(xalign=0.5, yalign=1.0, xpos=0.5, ypos=1.0, xzoom=0.7, yzoom=0.7)


label splashscreen:
    scene black
    with Pause(1)
    show text "Made By TamikiP" with dissolve
    with Pause(2)
    hide text with dissolve
    with Pause(1)
    return

label talk_mode:
    scene sea
    python:
        extracted_lines = read(rf"{game_directory}\characters.txt")
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
        $ renpy.show(character,at_list=[small_center])
        $ ask = renpy.input("请输入你的对话:")
        $ response_container = []
        $info = read(rf"{game_directory}\character_info.txt")
        $lines = info.splitlines()
        $print(id)
        $print(lines)
        $system= lines[2*id - 2]
        $print(system)

        $ gpt_thread = threading.Thread(target=get_gpt_response, args=(system,ask, history, response_container,id))
        $ gpt_thread.start()
        while not ok:
             $renpy.pause(0.5, hard=True)
        $ response = response_container[0]
        $ renpy.sound.play("audio/response.wav", channel='sound')
        $ renpy.say(character, f"『{response}』")
        $ history.append({"role": "assistant", "content": response})
        $ history.append({"role": "user", "content": ask})
    return


label start:
    if os.path.getsize(rf"{game_directory}\story.txt") == 0:
        $ t = threading.Thread(target=main,daemon = True)
        show loading movie
        $ t.start()
        while not if_already:
            $ renpy.pause(1, hard=True)
            $ from main import if_already
        scene black
        "资源加载完成,单击开始游戏"

    if os.path.exists(f"{game_directory}/music/happy bgm.mp3"):
        play music [ "music/happy bgm.mp3", "music/happy bgm2.mp3" ] fadeout 2.0 fadein 2.0
    while True:
        $ dialogues = load_dialogues(rf"{game_directory}\dialogues.json")
        $ dialogue = get_next_dialogue()

        if dialogue is None:
            $ extracted_lines = read(rf"{game_directory}\choice.txt")
            $ extracted_lines = extracted_lines.strip().split('\n')
            $ choice1, choice2, choice3 = extracted_lines[:3]
            $ choice_list=list_change(choice1,choice2,choice3)
            $ answer = renpy.display_menu(choice_list, interact=True, screen='choice')
            if answer == "user_input":
                $ answer = renpy.input("请输入你接下来的选择:")
            $ create_thread(answer)
            "剧情生成中...(请点击一下鼠标)"
            $ renpy.pause(0.5, hard=True)
            $ from main import generate_new_chapters_state
            while generate_new_chapters_state:
                $ renpy.pause(1, hard=True)
                $ from main import generate_new_chapters_state
            $ dialogues = load_dialogues(rf"{game_directory}\dialogues.json")
            $ dialogue = get_next_dialogue()

        $ character_name = dialogue["character"]
        $ text = dialogue["text"]
        if os.path.exists(f"{game_directory}/images/{dialogue['background_image']}.png"):
            $ background_image = f"images/{dialogue['background_image']}.png"
        else:
            $ background_image = ""
        $ audio = f"{dialogue['audio']}.wav"
        if os.path.exists(f"{game_directory}/images/{dialogue['character']}.png"):
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
