
import requests
import os
import json
import random
import time
from datetime import datetime
import base64
import toml

from path_config import game_directory, images_directory

config_path = os.path.join(game_directory, "config.toml")
with open(config_path, 'r', encoding="utf-8") as f:
    config = toml.load(f)


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
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        r = response.json()
        img_data = r.get('image', None)
        if not img_data:
            print("rembg failed: no image data in response")
            return encoded_image
        base64_data = img_data.strip()
        padding = len(base64_data) % 4
        if padding != 0:
            base64_data += '=' * (4 - padding)
        return base64_data
    except requests.exceptions.RequestException as e:
        print(f"rembg request failed: {e}")
        return encoded_image  # Return original on error


def download_image(url, save_dir=images_directory, filename=None):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # 生成文件名（使用时间戳）
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
    save_path = os.path.join(save_dir, filename)
    # 下载图片
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"图片已保存到: {save_path}")
        return save_path
    else:
        print(f"下载图片失败: {response.status_code}")
        return None


# 提交工作流到 ComfyUI
def queue_prompt(prompt_data, ComfyUI_url):
    payload = {"client_id": "533ef3a3-39c0-4e39-9ced-37c290f378f8", "prompt": prompt_data}
    response = requests.post(f"{ComfyUI_url}/prompt", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"提交工作流失败: {response.status_code}")


def get_history(prompt_id, ComfyUI_url):
    response = requests.get(f"{ComfyUI_url}/history/{prompt_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取任务历史失败: {response.status_code}")
        return {}


def ComfyUI_generate_image(prompt, image_name, mode):
    ComfyUI_url = "http://127.0.0.1:8188"
    if mode == 'background':
        workflow_path = os.path.join(game_directory, "ComfyUI/gen_background.json")
    else:
        workflow_path = os.path.join(game_directory, "ComfyUI/gen_characters.json")

    with open(workflow_path, "r", encoding="utf-8") as file:
        prompt_data = json.load(file)
    if mode == 'background':
        prompt_data["5"]["inputs"]["seed"] = random.randint(1, 1000000)
        prompt_data["5"]["inputs"]["prompt"] += prompt
    if mode == 'character':
        prompt_data["3"]["inputs"]["seed"] = random.randint(1, 1000000)
        prompt_data["3"]["inputs"]["prompt"] += prompt
    result = queue_prompt(prompt_data, ComfyUI_url)
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise Exception("未获取到 prompt_id")
    print(f"任务已提交，prompt_id: {prompt_id}")

    while True:
        history = get_history(prompt_id, ComfyUI_url)
        if history and prompt_id in history:
            print("图片下载完成！")

            outputs = history[prompt_id].get('outputs', {})
            output_node = '7' if mode == 'background' else '10'
            if outputs and output_node in outputs:
                images = outputs[output_node].get('images', [])
                for idx, image in enumerate(images):
                    image_url = f"{ComfyUI_url}/view?filename={image['filename']}"
                    fname = f"{image_name}.png" if image_name and idx == 0 else None
                    download_image(image_url, filename=fname)
                break
            else:
                print("未找到图片输出")
                break
        time.sleep(1)


def StableDiffusion_generate_image(prompt, image_name, mode):
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
        "negative_prompt": "EasyNagative,lowres,bad anatomy,text,cropped,low quality,(mutation, poorly drawn:1.2),"
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
        response.raise_for_status()
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
            with open(os.path.join(images_directory, final_image_name), 'wb') as f:
                f.write(image_data)
            print(f'图片已保存为 {final_image_name}')
        return "ok"
    except requests.exceptions.RequestException as e:
        print(f"绘图失败！请求错误: {e}")
        return "error"
    except Exception as e:
        print(f"绘图失败！未知错误: {e}")
        return "error"


def generate_image(prompt, image_name, mode):
    use_comfyui = config.get('AI绘画', {}).get('if_ComfyUI', False)
    if use_comfyui:
        ComfyUI_generate_image(prompt, image_name, mode)
    else:
        StableDiffusion_generate_image(prompt, image_name, mode)
