import re
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer sk-oMSFVkVHr8u5BeIHD6C578Fc82F84509B172E8C3F63eD08e'
}


def gpt(system, prompt):
    """调用 GPT 接口"""
    gpt_url = "https://api.bltcy.cn/v1/chat/completions"
    model = "gpt-4.1-mini"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "temperature": 0.8,
        "messages": messages
    })

    try:
        response = requests.post(gpt_url, headers=headers, data=payload, timeout=60)
        response.raise_for_status()
        parsed_data = json.loads(response.text)
        content = parsed_data['choices'][0]['message']['content']
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        return content
    except Exception as e:
        return f"[ERROR] 调用失败: {e}"


def split_text(text, max_length=2000):
    """按段落切分文本，控制最大长度"""
    paragraphs = text.split('\n\n')
    chunks, current = [], ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_length:
            current += para + "\n\n"
        else:
            chunks.append(current.strip())
            current = para + "\n\n"
    if current:
        chunks.append(current.strip())
    return chunks


# 主逻辑
if __name__ == "__main__":
    with open("input.txt", 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = split_text(content, max_length=2000)
    print(f"[INFO] 共切分为 {len(chunks)} 段，开始并行处理...")

    system_prompt = "把文章转换成对话格式如: XXX:xxx\n旁白:xxx\nXXX:xxx，文章中可能带有一些作者写的一些和文章内容无关的的话，可以直接排除，保留文章部分即可。角色XXX中不要出现小括号"
    results = [None] * len(chunks)

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_index = {
            executor.submit(gpt, system_prompt, chunk): i
            for i, chunk in enumerate(chunks)
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                results[i] = future.result()
                print(f"[完成] 第 {i + 1}/{len(chunks)} 段")
            except Exception as e:
                results[i] = f"[ERROR] 第 {i + 1} 段处理失败: {e}"

    final_result = "\n\n".join(results)

    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(final_result)

    print("[INFO] 全部处理完成，已保存到 output.txt")
