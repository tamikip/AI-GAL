import os

try:
    import renpy

    game_directory = renpy.config.gamedir
except ImportError:
    game_directory = os.getcwd()
images_directory = os.path.join(game_directory, "images")
audio_directory = os.path.join(game_directory, "audio")
