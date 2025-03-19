import requests
import base64
import os
import json
import random
import time
import configparser
import shutil

try:
    import renpy

    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
images_directory = os.path.join(game_directory, "images")

config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')
comfyui_output_address = config.get("AI绘画", "comfyui_address")


def rembg(encoded_image):
    data = {
        "input_image": encoded_image,
        "model": "u2net",
        "return_mask": False,
        "alpha_matting": False,
        "alpha_matting_foreground_threshold": 240,
        "alpha_matting_background_threshold": 10,
        "alpha_matting_erode_size": 10
    }

    url = 'http://localhost:7860/rembg'
    response = requests.post(url, json=data)
    r = response.json()
    img_data = r.get('image', None)
    base64_data = img_data.strip()
    padding = len(base64_data) % 4
    if padding != 0:
        base64_data += '=' * (4 - padding)
    return base64_data


def generate_image(prompt, image_name, mode):
    if config.getboolean("AI绘画", "if_comfyui"):
        ComfyUI_generate_image(prompt, mode)
        for filename in os.listdir(comfyui_output_address):
            if filename.startswith("AI-GAL"):
                source_file = os.path.join(comfyui_output_address, filename)
                target_file = os.path.join(images_directory, filename)
                shutil.move(source_file, target_file)
                print(filename)
                os.rename(f"{images_directory}/{filename}", f"{images_directory}/{image_name}.png")
    else:
        url = "http://localhost:7860"

        if mode == 'background':
            width = 960
            height = 540
            prompt2 = "(no_human)"

        else:
            width = 512
            height = 768
            prompt2 = "(upper_body),solo,((front_view,standing_illustration))"

        payload = {
            "prompt": f"masterpiece,wallpaper,8k,detailed CG,{prompt},{prompt2}",
            "negative_prompt": "EasyNagative,lowres, bad anatomy, text,cropped,low quality,(mutation, poorly drawn :1.2),"
                               "normal quality, obesity,bad proportions,unnatural body,bad shadow, uncoordinated body, "
                               "worst quality,censored,low quality,signature,watermark, username, blurry,nsfw",
            "steps": 25,
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
                    if mode != "background":
                        base64_data = rembg(base64_data)
                    image_data = base64.b64decode(base64_data)
                    final_image_name = f'{image_name}.png'
                    with open(fr'{images_directory}\{final_image_name}', 'wb') as f:
                        f.write(image_data)
                    print(f'图片已保存为 {final_image_name}')
                return "ok"
            else:
                print("Failed to generate image:", response.text)
                return "error"
        except:
            print("绘图失败！")
            return "error"


def ComfyUI_generate_image(prompt, mode):
    url = "http://127.0.0.1:8000/prompt"
    if mode == 'background':
        with open("ComfyUI/gen_background.json", "r", encoding="utf-8") as file:
            json1 = file.read()
    else:
        with open("ComfyUI/gen_characters.json", "r", encoding="utf-8") as file:
            json1 = file.read()
    prompt_data = json.loads(json1)
    prompt_data["3"]["inputs"]["seed"] = random.randint(1, 1000000)
    prompt_data["6"]["inputs"]["text"] = prompt_data["6"]["inputs"]["text"] + prompt
    print(prompt_data)

    new_json_dict = {
        "client_id": "533ef3a3-39c0-4e39-9ced-37c290f378f8",
        "prompt": prompt_data
    }

    response = requests.post(url, json=new_json_dict)
    print("Response JSON:", response.json())
    while True:
        time.sleep(1)
        response = requests.get(url)
        data = json.loads(response.text)
        if data["exec_info"]["queue_remaining"] == 0:
            break