import time

import update
import hashlib
import requests


def get_repofiles():
    files = []
    url = f'https://api.github.com/repos/tamikip/AI-GAL/git/trees/main?recursive=1'
    response = requests.get(url)
    if response.status_code == 200:
        tree = response.json()['tree']
        for item in tree:
            if item['type'] == 'blob':
                filename = item['path']
                if filename.endswith('.py') or filename.endswith('.rpy'):
                    files.append(filename)
    else:
        print(f"Failed to retrieve files: {response.status_code}")
    return files


def calculate_file_hash(file_path):
    hash_algo = hashlib.new("md5")
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()


def get_remote_file_md5(url):
    md5_hash = hashlib.md5()
    response = requests.get("https://github.moeyy.xyz/" + url, stream=True)
    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=4096):
        md5_hash.update(chunk)
    return md5_hash.hexdigest()


def download_file(filename):
    file_url = f'https://github.moeyy.xyz/raw.githubusercontent.com/tamikip/AI-GAL/main/{filename}'
    response = requests.get(file_url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


if __name__ == "__main__":
    with open("version.txt", "r") as file:
        version = file.read()
    latest_version = update.get_latest_release()["tag_name"]
    count = 0

    if latest_version == version:
        file_list = get_repofiles()
        for file in file_list:
            file_url = f"https://github.com/tamikip/AI-GAL/blob/main/{file}"
            online_hash_value = get_remote_file_md5(file_url)
            file_path = file
            local_hash_value = calculate_file_hash(file_path)
            if local_hash_value != online_hash_value:
                print(f"{file} 需要更新！")
                download_file(file)
                count += 1
        if count == 0:
            print("程序无需更新")
            time.sleep(3)
        else:
            print("已更新完成")
            time.sleep(3)
    else:
        print("版本不匹配，请先更新至最新版本")
