import json
import os
import requests
from zipfile import ZipFile
import shutil


GITHUB_REPO = "tamikip/AI-GAL"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DOWNLOAD_DIR = "downloads"
GAME_DIR = "game"
CONFIG_FILE = "config.ini"


def get_latest_release():
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        browser_download_url = response.json()['assets'][0]["browser_download_url"]
        print("仓库连接成功")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"无法获取最新版本信息: {e}")
        return None


def download_file(url, download_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"下载完成：{download_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        return False


def update_program():
    latest_release = get_latest_release()
    if latest_release:
        asset = latest_release['assets'][0]
        browser_download_url = asset['browser_download_url']
        GITHUB_DOWNLOAD_URL = f"https://github.moeyy.xyz/{browser_download_url}"  # 镜像加速
        download_url = GITHUB_DOWNLOAD_URL
        filename = asset['name']

        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)

        download_path = os.path.join(DOWNLOAD_DIR, filename)
        if download_file(download_url, download_path):
            with ZipFile(download_path, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file == os.path.join(filename, "game", "config.ini"):
                        continue
                    zip_ref.extract(file, ".")
            shutil.rmtree("downloads")
            print("更新完成")
        else:
            print("更新过程中出现问题，下载失败")


if __name__ == "__main__":
    update_program()
