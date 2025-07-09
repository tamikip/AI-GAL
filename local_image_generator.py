# 1. 结构更清晰：分离了下载、提交任务、历史查询等功能，易于维护和扩展。
# 2. 简化功能：仅保留 ComfyUI 支持，去除 SDWebUI、本地抠图等冗余功能。
# 3. 健壮性提升：增加异常处理，图片命名防止覆盖，流程更易追踪。
# 4. 代码更简洁：删除无用依赖和复杂流程，便于理解和后续开发。
# 5. 自动创建图片目录，提升兼容性。
import requests
import os
import json
import random
import time
from datetime import datetime

try:
    import renpy
    game_directory = renpy.config.gamedir
except:
    game_directory = os.getcwd()
images_directory = os.path.join(game_directory, "images")

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
def queue_prompt(prompt_data,ComfyUI_url):
    payload = {"client_id": "533ef3a3-39c0-4e39-9ced-37c290f378f8","prompt": prompt_data}
    response = requests.post(f"{ComfyUI_url}/prompt", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"提交工作流失败: {response.status_code}")


def get_history(prompt_id,ComfyUI_url):
    response = requests.get(f"{ComfyUI_url}/history/{prompt_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"获取任务历史失败: {response.status_code}")
        return {}

def generate_image(prompt, image_name, mode):
    ComfyUI_url = "http://127.0.0.1:6000"
    if mode == 'background':
        workflow_path = "ComfyUI/gen_background.json"
    else:
        workflow_path = "ComfyUI/gen_characters.json"
    
    with open(workflow_path, "r", encoding="utf-8") as file:
        prompt_data = json.load(file)
    if mode == 'background':
        prompt_data["7"]["inputs"]["seed"] = random.randint(1, 1000000)
        prompt_data["4"]["inputs"]["text"] += prompt
        # print(f"background: {prompt_data['4']['inputs']['text']}")
    if mode == 'character':
        prompt_data["3"]["inputs"]["seed"] = random.randint(1, 1000000)
        prompt_data["57"]["inputs"]["text"] += prompt
        # print(f"character: {prompt_data['57']['inputs']['text']}")
    result = queue_prompt(prompt_data,ComfyUI_url)
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise Exception("未获取到 prompt_id")
    print(f"任务已提交，prompt_id: {prompt_id}")

    while True:
        history = get_history(prompt_id,ComfyUI_url)
        if history and prompt_id in history:
            print("图片下载完成！")
            
            # 获取生成的图片
            outputs = history[prompt_id].get('outputs', {})
            output_node = '12' if mode == 'background' else '64'
            if outputs and output_node in outputs:
                images = outputs[output_node].get('images', [])
                for idx, image in enumerate(images):
                    image_url = f"{ComfyUI_url}/view?filename={image['filename']}"
                    # 如果提供了 image_name，仅对第一张图片使用，否则用默认命名
                    fname = f"{image_name}.png" if image_name and idx == 0 else None
                    download_image(image_url, filename=fname)
                break
            else:
                print("未找到图片输出")
                break
        time.sleep(1)