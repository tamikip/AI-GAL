def translate_to_renpy_string(input_data):
    renpy_script = []
    for conversation in input_data["conversations"]:
        if conversation["background_image"]:
            renpy_script.append(f'renpy.show("{conversation["background_image"]}").png")')
        if conversation["character"]:
            renpy_script.append(f'renpy.show("{conversation["character"]}").png"')
        if conversation["character"]:
            renpy_script.append(f'renpy.sound.play("{conversation["audio"]}.wav", channel="sound")')
        renpy_script.append(f'renpy.say("{conversation["character"]}", "{conversation["text"]}")')
        if conversation["character"]:
            renpy_script.append(f'renpy.hide("{conversation["character"]}").png"')
    return "\n".join(renpy_script)
