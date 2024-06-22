init python:
    import json
    import os
    import threading
    import main
    import threading
    import importlib

    from main import if_already
    from main import running_state


    def create_thread():
        thread = threading.Thread(target = main.story_continue)
        thread.start()
        return thread 

    def load_dialogues(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["conversations"]

    def get_next_dialogue():
        global current_dialogue_index
        if current_dialogue_index < len(dialogues):
            dialogue = dialogues[current_dialogue_index]
            current_dialogue_index += 1
            return dialogue
        else:
            return None

    current_dialogue_index = 0
    dialogues = []
    characters = {}
    game_directory = renpy.config.gamedir
image loading movie = Movie(play="loading.webm")
define small_center = Transform(xalign=0.5, yalign=1.0, xpos=0.5, ypos=1.0, xzoom=0.7, yzoom=0.7)



label splashscreen:
    scene black
    with Pause(1)
    show text "Made By TamikiP" with dissolve
    with Pause(2)
    hide text with dissolve
    with Pause(1)
    return

label start:
    if os.path.getsize(rf"{game_directory}\story.txt") == 0:
        $ t = threading.Thread(target=main.main,daemon = True)
        show loading movie
        $ t.start()
        while not if_already:
            $ renpy.pause(1, hard=True)
            $ from main import if_already
        scene black
        "资源加载完成,单击开始游戏"

    play music "music.mp3"
    $ create_thread()

    while True:
        $ dialogues = load_dialogues(rf"{game_directory}\dialogues.json")
        $ dialogue = get_next_dialogue()

        if dialogue is None:
            "资源加载中...请稍后..."
            if not running_state:
                $ create_thread()
                $ renpy.pause(0.5, hard=True)
                $ from main import running_state
            while running_state:
                $ renpy.pause(1, hard=True)
                $ from main import running_state
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


        if text == "new":
            $ current_dialogue_index += 1
            $ from main import running_state
            if not running_state:
                $ create_thread()

        else:
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
