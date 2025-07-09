import toml


class PromptsManager:
    """管理所有与GPT交互的prompt"""

    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            config = toml.load(f)
        self._prompts = config.get('Prompts', {})

    def get_character_image_system_message(self):
        """获取角色图片生成的系统消息prompt"""
        return self._prompts.get('character_image_system_message')

    def get_background_image_system_message(self):
        """获取背景图片生成的系统消息prompt"""
        return self._prompts.get('background_image_system_message')

    def get_select_branch_system_message(self):
        """获取分支选项选择的系统消息prompt"""
        return self._prompts.get('select_branch_system_message', "你是galgame剧情家，精通各种galgame写作")

    def get_select_branch_user_template(self):
        """获取分支选项选择的用户消息prompt模板"""
        return self._prompts.get('select_branch_user_template',
                                 "根据galgame剧情，以男主角的视角，设计男主角接下来的三个分支选项。内容是: {story_content},要求每个选项尽量简短，返回json格式: {{ \"Option1\":\"xxxxx\",\"Option2\":\"xxxxx\",\"Option3\":\"xxxxx\" }}")

    def get_generate_story_content_system_message(self):
        """获取生成故事内容的系统消息prompt"""
        return self._prompts.get('generate_story_content_system_message',
                                 "现在你是一名galgame剧情作家，精通写各种各样的galgame剧情，请不要使用markdown格式")

    def get_generate_story_content_user_template(self):
        """获取生成故事内容的用户消息prompt模板"""
        return self._prompts.get('generate_story_content_user_template')

    def get_story_continue_system_message(self):
        """获取故事续写的系统消息prompt"""
        return self._prompts.get('story_continue_system_message',
                                 "现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情。只输出文本，不要输出任何多余的。不要使用markdown格式，如果需要切换场景在对话的后面加上[地点]，输出例子:旁白:xxx[地点A]\n角色A:xxx\n角色B:xxx\n角色:xxx[地点B]\n旁白:xxx，角色名字要完整。")

    def get_story_continue_user_template(self):
        """获取故事续写的用户消息prompt模板"""
        return self._prompts.get('story_continue_user_template',
                                 "请你根据以下内容继续续写galgame剧情。只返回剧情。人物设定参考（已有角色）：{character_names_for_prompt}，当前剧情概要:{story_content}，我选择的分支是{choice}")

    def get_initial_system_message(self):
        """获取初始系统消息prompt"""
        return self._prompts.get('initial_system_message', "现在你是一名galgame剧情设计师，精通写各种各样的galgame剧情")

    def get_initial_user_template(self):
        """获取初始用户消息prompt模板"""
        return self._prompts.get('initial_user_template',
                                 "现在请你写一份galgame的标题，大纲，背景，人物,我给出的主题和概要是{theme}，你的输出json格式为:{{'title':'xxxxx','outline':'xxxxx','background':'xxxxx','characters':[{{'name':'xxx','gender':'男','kind':'xxxxx'}},{{'name':'xxx','gender':'女','kind':'xxxxx'}}]}}，kind部分包括角色的外貌和性格特点，人物为5人，一男四女，男主在角色列表中排第一位")
