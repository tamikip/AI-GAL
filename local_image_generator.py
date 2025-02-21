import requests
import base64
import os
import configparser
try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
images_directory = os.path.join(game_directory, "images")
config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')


def generate_image(prompt, image_name, mode):
    url = "http://127.0.0.1:7860"

    if mode == 'background':
        width = 960
        height = 540
        prompt2 = "(no_human)"

    else:
        width = 512
        height = 768
        prompt2 = "(upper_body),solo"

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
