import configparser
import random
import requests
import json
import time
import os

try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()

images_directory = os.path.join(game_directory, "images")
config = configparser.ConfigParser()
config.read(rf"{game_directory}\config.ini", encoding='utf-8')
online_draw_key = config.get('AI绘画', 'draw_key')
url = "https://cn.tensorart.net/v1/jobs"
online_draw_headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {online_draw_key}"
}


def online_generate(prompt, mode):
    requests_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if mode == 'background':
        width = 960
        height = 540
        prompt2 = "(no_human)" + prompt
        if config.get('AI绘画', 'character_id'):
            model = config.get('AI绘画', 'character_id')
        else:
            model = "611399039965066695"

    else:
        width = 512
        height = 768
        prompt2 = "masterpiece,wallpaper,(upper_body),face focus,solo,looking at the viewer,((front_view,standing_illustration))," + prompt
        if config.get('AI绘画', 'background_id'):
            model = config.get('AI绘画', 'background_id')
        else:
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
                    "sampler": "Euler",
                    "prompts": [{"text": prompt2}],
                    "negativePrompts": [{"text": "EasyNegative, badhandv4, verybadimagenegative_v1.3, bad-hands-5, "
                                                 "lowres, bad anatomy, bad hands, text, error, missing fingers, "
                                                 "extra digit, fewer digits, cropped, worst quality, low quality, "
                                                 "normal quality, jpeg artifacts, signature, watermark, username, "
                                                 "blurry, Missing limbs, three arms, bad feet, text font ui, "
                                                 "signature, blurry, text font ui, malformed hands, long neck, limb, "
                                                 "Sleeveles, bad anatomy disfigured malformed mutated, (mutated hands "
                                                 "and fingers :1.5).(long body :1.3), (mutation , poorly drawn :1.2), "
                                                 "bad anatomy, disfigured, malformed, mutated, multiple breasts, "
                                                 "futa, yaoi, three legs"}],
                    "steps": 25,
                    "sdVae": "animevae.pt",

                    "sd_model": model,
                    "clip_skip": 2,
                    "cfg_scale": 7,
                    **({"layerDiffusion": {"enable": True, "weight": 1}} if mode != "background" else {})
                }
            },
            {
                "type": "IMAGE_TO_UPSCALER",
                "image_to_upscaler": {
                    "hr_upscaler": "R-ESRGAN 4x+ Anime6B",
                    "hr_scale": 2,
                    "hr_second_pass_steps": 10,
                    "denoising_strength": 0.2
                }
            }
        ]
    }
    response = requests.post(url, headers=online_draw_headers, data=json.dumps(data))
    if response.status_code == 200:
        id = json.loads(response.text)['job']['id']
        return id
    else:
        print(f"请求失败，状态码：{response.status_code}，请检查是否正确填写了key")
        return "error"


def get_result(job_id, image_name):
    while True:
        time.sleep(1)
        response = requests.get(f"{url}/{job_id}", headers=online_draw_headers)
        get_job_response_data = json.loads(response.text)

        if 'job' in get_job_response_data:
            job_dict = get_job_response_data['job']
            job_status = job_dict.get('status')

            if job_status == 'SUCCESS':
                url2 = job_dict["successInfo"]["images"][0]["url"]
                response = requests.get(url2)
                file_path = os.path.join(images_directory, f"{image_name}.png")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                break
            elif job_status == 'FAILED':
                print(job_dict)
                break


def online_generate_image(prompt, image_name, mode):
    task_id = online_generate(prompt, mode)
    get_result(task_id, image_name)
