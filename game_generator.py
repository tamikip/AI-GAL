# 1. 采用面向对象设计，将所有流程封装为 GameGenerator 类，提升了代码可维护性和扩展性。
# 2. 使用 toml 配置文件
# 3. 明确管理资源路径，自动创建所需目录，提升健壮性。
# 4. 角色、背景、对话、音频等资源生成流程独立封装，职责单一，便于测试和复用。
# 5. 使用 ThreadPoolExecutor 统一并发处理，提高处理效率。
# 6. 所有状态均为实例成员变量，避免全局变量污染，线程安全性更好。
# 7. 处理每行故事文本采用纯函数，便于单元测试和流程复用。
import os
import json
import toml
import re
import threading
from concurrent.futures import ThreadPoolExecutor,as_completed
from Prompts import PromptsManager
from GPT import gpt
from music_generator import generate_music
from local_image_generator import generate_image
from cloud_image_generator import online_generate_image
from local_vocal_generator import generate_audio
from cloud_vocal_generator import online_generate_audio
import time
from path_config import game_directory, images_directory, audio_directory

ILLEGAL_CHAR_REPLACEMENTS = {'!': '！', '?': '？', ':': '：', '"': '“', '/': '／', '\\': '＼', '|': '｜', '*': '＊', '<': '＜',
                             '>': '＞'}


class GameGenerator:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding="utf-8") as f:
            config = toml.load(f)
        story_config = config.get('剧情', {})
        music_config = config.get('AI音乐', {})
        self.theme_language = story_config.get('language', '中文')
        self.theme = story_config.get('theme', {})
        self.if_generate_music = music_config.get('if_on', False)
        self.if_cloud_image = config.get('AI绘画', {}).get('if_cloud', False)
        self.if_cloud_audio = config.get('SOVITS', {}).get('if_cloud', False)
        self.if_generate_audio = config.get('SOVITS', {}).get('if_on', True)
        self.prompts_manager = PromptsManager(config_path)
        self.game_directory = game_directory
        self.dialogues_path = os.path.join(self.game_directory, "dialogues.json")
        self.images_directory = images_directory
        os.makedirs(self.images_directory, exist_ok=True)
        self.background_list = []
        self.current_background_name = ""
        self.character_list = []
        self.story_content = ""
        self.generate_new_chapters_state = False
        self.already_state = False
        self.next_audio_id = 1  # 音频文件ID计数器
        with open(self.dialogues_path, 'r', encoding='utf-8') as f:
            self.dialogues = json.load(f)

    def clean_filename(self, text):
        """替换文本中不适用于文件名的非法字符"""
        cleaned_text = text
        for char, repl in ILLEGAL_CHAR_REPLACEMENTS.items():
            cleaned_text = cleaned_text.replace(char, repl)
        return cleaned_text

    def add_dialogue(self, character, text, background_image, audio_filename):
        """将一条包含角色、文本、背景图和音频文件名的对话追加到 self.dialogues 列表中"""
        self.dialogues["conversations"].append({
            "character": character,
            "text": text,
            "background_image": background_image,
            "audio": audio_filename,
        })

    def save_dialogues(self):
        """将 self.dialogues 中的所有对话内容以 JSON 格式保存到 dialogues.json"""
        with open(self.dialogues_path, "w", encoding="utf-8") as file:
            json.dump(self.dialogues, file, indent=4, ensure_ascii=False)

    def _generate_character_assets(self, character_info_line):
        """辅助方法：根据单行角色信息生成角色形象并更新列表,character_info_line 格式: "名字:性别，外貌性格描述" """
        system_msg_char_image = self.prompts_manager.get_character_image_system_message()
        image_prompt = gpt(system_msg_char_image, character_info_line)
        name_part = character_info_line.split(":", 1)[0]
        name_no_brackets = re.sub(r'\（[^)]*\）|\([^()]*\)', '', name_part)
        character_name = re.sub(r'[^\u4e00-\u9fa5]', '', name_no_brackets)
        # 支持云端/本地角色图片生成
        if self.if_cloud_image:
            online_generate_image(image_prompt, character_name, "character")
        else:
            generate_image(image_prompt, character_name, "character")
        if character_name not in self.character_list:
            self.character_list.append(character_name)
        with open(os.path.join(self.game_directory, "characters.txt"), "a", encoding='utf-8') as f:
            f.write(f"{character_name}\n")

    def _pre_generate_initial_background(self):
        """扫描整个故事文本，预先生成并设置第一个出现的背景，确保故事开始就有背景图。"""
        first_location_match = re.search(r'\[([^\[\]]+)\]', self.story_content)

        if first_location_match:  # 情况一：在故事中找到了明确的地点标记
            background_name = first_location_match.group(1).strip()
            context_end_index = min(first_location_match.end() + 80, len(self.story_content))
            context_for_prompt = self.story_content[:context_end_index]
            image_prompt_text = f"场景：{background_name}。相关描述：{context_for_prompt}"
            print(f"根据故事开头的地点 '[{background_name}]' 生成初始背景...")
        else:  # 情况二：故事中没有地点标记，但有内容，则使用开篇内容生成
            background_name = "初始场景"
            initial_context = self.story_content[:200]
            image_prompt_text = f"根据以下开场描述生成一个合适的背景：{initial_context}"
            print("故事开头未找到特定地点，根据初始内容生成通用背景...")

        if background_name and background_name not in self.background_list:
            system_msg_background_image = self.prompts_manager.get_background_image_system_message()
            background_image_generation_prompt = gpt(system_msg_background_image, image_prompt_text)
            threading_pre_pic = threading.Thread(
                target=online_generate_image if self.if_cloud_image else generate_image,
                args=(background_image_generation_prompt, background_name, "background"))
            threading_pre_pic.start()
            # 更新全局状态，将此背景设为当前背景
            self.background_list.append(background_name)
            self.current_background_name = background_name

    def process_story_line_pure(self, line):
        """处理单行故事文本：不修改实例状态，返回处理结果"""
        if not line.strip():
            return None

        result = {
            "background_change": None,
            "dialogue": None,
            "new_audio_id": None,
            "new_character": None
        }

        # 1. 背景处理与生成判断
        explicit_location_match = re.search(r'\[([^\[\]]+)\]', line)
        if explicit_location_match:
            extracted_location_name = explicit_location_match.group(1).strip()
            if extracted_location_name:
                result["background_change"] = {
                    "name": extracted_location_name,
                    "is_new": True,
                    "prompt_input": f"场景：{extracted_location_name}。描述：{line}"
                }

        # 移除文本中的地点标记并统一冒号
        text_for_dialogue = re.sub(r'\[.*?\]', '', line).strip().replace("：", ":")

        # 2. 角色和对话文本解析
        if ":" not in text_for_dialogue:
            text_for_dialogue = "旁白:" + text_for_dialogue
        character, original_text = text_for_dialogue.split(":", 1)
        text_no_location = re.sub(r'\[.*?\]', '', original_text)
        text_no_description = re.sub(r'\（[^)]*\）', '', text_no_location.replace("(", "（").replace(")", "）"))

        # 3. 准备音频生成信息，但不直接生成
        if character and original_text:
            result["dialogue"] = {
                "character": "" if character == "旁白" else character,
                "text": text_no_location,
                "audio_text": text_no_description
            }

            # 如果是新角色，记录下来
            if character != "旁白" and character:
                result["new_character"] = character

        return result

    def _initialize_story_files(self):
        # 清空或初始化故事相关文件
        if os.path.exists(os.path.join(self.game_directory, "characters.txt")):
            open(os.path.join(self.game_directory, "characters.txt"), "w").close()
        self.dialogues = {"conversations": []}
        self.background_list = []
        self.character_list = []
        self.current_background_name = ""  # 重置当前背景名
        self.next_audio_id = 1  # 重置音频ID计数器

    def select_branch(self):
        system_msg = self.prompts_manager.get_select_branch_system_message()
        user_msg_template = self.prompts_manager.get_select_branch_user_template()
        user_msg = user_msg_template.format(story_content=self.story_content)

        choices = json.loads(gpt(system_msg, user_msg, json_mode=True))
        cleaned_text = "\n".join(choices.values())
        with open(os.path.join(self.game_directory, "choice.txt"), 'w', encoding='utf-8') as file:
            file.write(cleaned_text)
        return cleaned_text

    # todo:多线程优化

    def _process_story_results(self, results):
        valid_results = [r for r in results if r is not None]

        # 任务收集
        background_tasks = []
        audio_tasks = []
        dialogues = []

        new_characters = []
        for result in valid_results:
            if (result["new_character"]
                    and result["new_character"] not in self.character_list
                    and result["new_character"] not in new_characters):
                new_characters.append(result["new_character"])
        if new_characters:
            self.character_list.extend(new_characters)

        next_audio_id = self.next_audio_id
        for result in valid_results:
            # 背景任务
            if result["background_change"]:
                bg_info = result["background_change"]
                extracted_location_name = bg_info["name"]
                if extracted_location_name != self.current_background_name:
                    if extracted_location_name not in self.background_list:
                        system_msg_background_image = self.prompts_manager.get_background_image_system_message()
                        background_prompt = gpt(system_msg_background_image, bg_info["prompt_input"])
                        background_tasks.append((background_prompt, extracted_location_name))
                    self.current_background_name = extracted_location_name

            # 对话和音频任务
            if result["dialogue"]:
                dialogue = result["dialogue"]
                character = dialogue["character"]
                text_no_location = dialogue["text"]
                text_no_description = dialogue["audio_text"]

                audio_filename = ""
                if self.if_generate_audio and character in self.character_list:
                    audio_speaker_id = self.character_list.index(character) + 1
                    audio_base_filename = f"audio_{next_audio_id}"
                    next_audio_id += 1
                    audio_tasks.append((text_no_description, audio_speaker_id, audio_base_filename))
                    audio_filename = f"{audio_base_filename}.mp3"

                dialogues.append((character, text_no_location, self.current_background_name, audio_filename))

        # === 分开两个线程池 ===
        with ThreadPoolExecutor(max_workers=8) as bg_executor, \
                ThreadPoolExecutor(max_workers=2) as audio_executor:

            bg_futures = []
            audio_futures = []

            # 背景任务提交
            for prompt, name in background_tasks:
                if self.if_cloud_image:
                    bg_futures.append(bg_executor.submit(online_generate_image, prompt, name, "background"))
                else:
                    bg_futures.append(bg_executor.submit(generate_image, prompt, name, "background"))
                self.background_list.append(name)

            # 音频任务提交
            for text, speaker_id, base_filename in audio_tasks:
                if self.if_cloud_audio:
                    audio_futures.append(audio_executor.submit(online_generate_audio, text, speaker_id, base_filename))
                else:
                    audio_futures.append(audio_executor.submit(generate_audio, text, speaker_id, base_filename))

            # 背景任务完成监听
            for future in as_completed(bg_futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"背景任务出错: {e}")

            # 音频任务完成监听
            for future in as_completed(audio_futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"音频任务出错: {e}")

        # 添加对话记录
        for character, text, bg, audio_file in dialogues:
            self.add_dialogue(character, text, bg, audio_file)

        # 更新音频ID计数器
        self.next_audio_id = next_audio_id

        # 更新音频ID计数器
        self.next_audio_id = next_audio_id

    def custom_story(self):
        input("请先将剧情按照格式放入story.txt,\n人物信息放入character_info.txt,\n回车开始运行程序:\n")
        print("读取中...")
        self._initialize_story_files()
        with open(os.path.join(self.game_directory, 'story.txt'), 'r', encoding='utf-8') as file:
            self.story_content = self.clean_filename(file.read())
        with open(os.path.join(self.game_directory, 'character_info.txt'), 'r', encoding='utf-8') as file:
            characters_lines = [line.strip() for line in file if ":" in line.strip()]
        print("生成角色形象并写入characters.txt...")
        for character_line in characters_lines:
            self._generate_character_assets(character_line)

        self._pre_generate_initial_background()
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.process_story_line_pure, self.story_content.splitlines()))
        self._process_story_results(results)

        self.select_branch()
        self.save_dialogues()
        print("自定义故事处理完成，可退出。")

    def main(self):
        print("程序已开始运行")
        start_time = time.time()
        if self.if_generate_music:
            # 启动音乐生成线程
            print("启动音乐生成线程")
            music_thread1 = threading.Thread(target=generate_music, args=("common", "happy bgm"))
            music_thread2 = threading.Thread(target=generate_music, args=("sad", "sad bgm"))
            music_thread1.start()
            music_thread2.start()
        else:
            print("用户未启动生成音乐模式")
        self._initialize_story_files()
        # 1. GPT生成故事大纲、角色等
        system_msg_initial = self.prompts_manager.get_initial_system_message()
        user_msg_prompt_initial_template = self.prompts_manager.get_initial_user_template()
        user_msg_prompt_initial = user_msg_prompt_initial_template.format(theme=self.theme)
        data_ori = gpt(system_msg_initial, user_msg_prompt_initial, json_mode=True)
        data = json.loads(data_ori)

        title = data['title']
        outline = data['outline']

        game_world_background = data['background']
        # 角色信息字符串: "名字:性别, 描述"
        characters = "\n".join(
            [f"{character['name']}:{character['gender']}，{character['kind']}" for character in data['characters']])
        self.already_state = "story"

        # todo:多线程
        characters_lines = [line.strip() for line in characters.splitlines() if ":" in line.strip()]
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            for char_line in characters_lines:
                future = executor.submit(self._generate_character_assets, char_line)
                futures.append(future)

        # 2. GPT生成第一章故事内容
        system_msg_story_content = self.prompts_manager.get_generate_story_content_system_message()
        user_msg_story_content_template = self.prompts_manager.get_generate_story_content_user_template()
        user_msg_story_content = user_msg_story_content_template.format(
            title=title,
            outline=outline,
            background=game_world_background,
            characters=characters,
            language=self.theme_language
        )

        self.story_content = '\n'.join(
            line.strip() for line in gpt(system_msg_story_content, user_msg_story_content).split('\n') if line.strip())

        with open(os.path.join(self.game_directory, 'story.txt'), 'w', encoding='utf-8') as file:
            file.write(f"{self.story_content}\n")
        with open(os.path.join(self.game_directory, 'title.txt'), 'w', encoding='utf-8') as file:
            file.write(title)
        with open(os.path.join(self.game_directory, 'character_info.txt'), 'w', encoding='utf-8') as file:
            file.write(characters)

        # 3. 生成背景资源
        self.already_state = "picture"

        # 4. 处理故事内容（生成对话、背景图、音频）
        dialogue_lines = self.story_content.splitlines()
        print(dialogue_lines)
        self.already_state = "audio"
        self._pre_generate_initial_background()
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.process_story_line_pure, self.story_content.splitlines()))
        self._process_story_results(results)

        # 5. 生成分支选项并保存对话
        self.select_branch()
        self.save_dialogues()
        self.already_state = "complete"
        end_time = time.time()
        use_time = end_time - start_time
        print(f"游戏 '{title}' 的第一章已生成完毕！")
        print(f"用时{use_time:.2f}秒")

    def story_continue(self, choice):
        start_time = time.time()
        self.generate_new_chapters_state = True
        character_names_for_prompt = ",".join(self.character_list)
        system_msg_continue = self.prompts_manager.get_story_continue_system_message()
        user_msg_continue_template = self.prompts_manager.get_story_continue_user_template()
        user_msg_continue = user_msg_continue_template.format(
            character_names_for_prompt=character_names_for_prompt,
            story_content=self.story_content,
            choice=choice
        )
        additional_story = gpt(system_msg_continue, user_msg_continue).strip()
        self.story_content += "\n" + additional_story
        with open(os.path.join(self.game_directory, 'story.txt'), 'w', encoding='utf-8') as file:
            file.write(f"{self.story_content}\n")
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.process_story_line_pure, additional_story.splitlines()))
        self._process_story_results(results)

        self.select_branch()
        self.save_dialogues()
        self.generate_new_chapters_state = False
        print("故事续写完成。")
        end_time = time.time()
        use_time = end_time - start_time
        print(f"用时{use_time:.2f}秒")


if __name__ == "__main__":
    generator = GameGenerator("config.toml")
    generator.custom_story()
