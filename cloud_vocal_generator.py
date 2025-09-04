# 改用toml
import requests
import toml
import time
import json
from path_config import game_directory, audio_directory
from concurrent.futures import ThreadPoolExecutor
import os
import re

config_path = os.path.join(game_directory, "config.toml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = toml.load(f)


def contains_japanese_precise(text):
    """
    精确检测日文字符，避免与中文混淆
    主要检测日文特有的假名和常用助词
    """
    # 平假名范围（日文特有）
    hiragana_pattern = r'[\u3040-\u309f]'
    # 片假名范围（日文特有）
    katakana_pattern = r'[\u30a0-\u30ff]'
    # 片假名音标扩展
    katakana_phonetic_pattern = r'[\u31f0-\u31ff]'

    # 日文特有的标点符号和字符
    japanese_specific_chars = r'[々〆〤㈱㈲㈹㊤㊥㊦㊧㊨㊩㊪㊫㊬㊭㊮㊯㊰]'

    # 检测日文假名（最可靠的指标）
    if (re.search(hiragana_pattern, text) or
            re.search(katakana_pattern, text) or
            re.search(katakana_phonetic_pattern, text) or
            re.search(japanese_specific_chars, text)):
        return True

    return False


def get_audio_url(content, speaker_id):
    token = config["SOVITS"]["api_key"]
    url = "https://ht.ttson.cn:37284/flashsummary/tts?token=" + token
    character_id = config["SOVITS"][f"model_id{speaker_id}"] if 1 <= speaker_id <= 6 else 6
    payload = json.dumps({
        "voice_id": character_id,
        "text": content,
        "to_lang": "JP" if contains_japanese_precise(content) else "auto",  # 自动识别内容文本，日文则切换到日文模式，auto兼容中文和英文
        "format": "mp3",
        "speed_factor": 1,
        "pitch_factor": 0,
        "volume_change_dB": 0,
        "emotion": 1
    })

    response = requests.request("POST", url, data=payload)

    if response.status_code != 200:
        print(response.text)
        return None
    response_json = response.json()

    result = response_json['url'] + ':' + str(
        response_json['port']) + '/flashsummary/retrieveFileData?stream=True&token=' + token + '&voice_audio_path=' + \
             response_json['voice_path']
    return result


def download_audio(url, save_path):
    if url == "":
        print("Empty url")
        return False
    try:
        audio_content = requests.get(url)
        if audio_content.status_code == 200:
            with open(f"{save_path}.mp3", "wb") as f:
                f.write(audio_content.content)
            return True
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
    return False


def online_generate_audio(content, speaker_id, output_name):
    url = get_audio_url(content, speaker_id)
    output_name = os.path.join(audio_directory, output_name)
    download_audio(url, output_name)


def simple_concurrent_test():
    """简单的并发测试"""
    test_text = "皆さんこんにちは"
    num_requests = 4
    concurrency_levels = [2]  # 测试不同的并发度

    results = {}

    for concurrency in concurrency_levels:
        time.sleep(2)
        print(f"\n测试 {concurrency} 并发，{num_requests} 个请求...")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for i in range(num_requests):
                filename = f"test_{concurrency}_{i}"
                future = executor.submit(online_generate_audio, test_text, 2, filename)
                futures.append(future)

            # 等待所有完成
            success = 0
            for future in futures:
                try:
                    future.result()
                    success += 1
                except Exception as e:
                    print(f"请求失败: {e}")

        total_time = time.time() - start_time
        throughput = success / total_time if total_time > 0 else 0

        results[concurrency] = {
            'total_time': total_time,
            'success': success,
            'throughput': throughput,
            'avg_time': total_time / num_requests
        }

        print(f"并发 {concurrency}: {total_time:.2f}秒, 吞吐量: {throughput:.2f}请求/秒")

    return results


if __name__ == "__main__":
    # start_time = time.time()
    # online_generate_audio(
    #     "你的笑容，是银河中最璀璨的星轨，让我忍不住想将整个宇宙的浪漫都揉进你的名字，只为让它配得上你的美好。", 2, "test")
    # end_time = time.time()
    # execution_time = end_time - start_time
    # os.startfile(rf"{audio_directory}\test.mp3")
    # print(f"用时: {execution_time:.2f} 秒")
    simple_concurrent_test()
