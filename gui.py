import configparser
import os
import shutil
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel, \
    QWidget, QSpacerItem, QSizePolicy, QGridLayout
from qfluentwidgets import NavigationItemPosition, LineEdit, TitleLabel, \
    TogglePushButton, TransparentToolButton, ComboBox, PushButton, SwitchButton, FluentIcon, Theme, setTheme, \
    InfoBar, InfoBarPosition, CardWidget, IconWidget, HyperlinkCard, HorizontalFlipView, PrimaryPushButton, \
    StrongBodyLabel, HyperlinkButton, PasswordLineEdit, FluentWindow, Dialog, IndeterminateProgressBar, MessageBoxBase, \
    SubtitleLabel, QConfig, ConfigItem, SwitchSettingCard, BoolValidator, qconfig, OptionsConfigItem, OptionsValidator, \
    ComboBoxSettingCard, TextEdit, ProgressBar
import update
import subprocess
from main import gpt, generate_audio, generate_image, online_generate, online_generate_audio

config = configparser.ConfigParser()
config.read('config.ini', "utf-8")
auto_update = config.getboolean("Settings", "auto_update")
current_working_directory = os.getcwd()
parent_directory_of_cwd = os.path.dirname(current_working_directory)
aigal_exe_path = os.path.join(parent_directory_of_cwd, "AIGAL.exe")
aigal_log_path = os.path.join(parent_directory_of_cwd, "log.txt")


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI GAL 启动器")
        self.navigationInterface.setExpandWidth(200)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(200, 200, 1280, 720)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', "utf-8")
        self.menu_page = self.create_menu_page("主页")
        self.chatgpt_page = self.create_chatgpt_page("ChatGPT")
        self.ai_painting_page = self.create_ai_painting_page("AI 绘画")
        self.gpt_sovits_page = self.create_gpt_sovits_page("GPT-SOVITS")
        self.ai_music_page = self.create_ai_music_page("AI 音乐")
        self.story_page = self.create_story_page("剧情")
        self.make_logs_page = self.create_make_logs_page("日志")
        self.downloads_page = self.create_downloads_page("资源下载")
        self.options_page = self.create_options_page("设置")
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.menu_page, FluentIcon.HOME, "菜单")
        self.addSubInterface(self.chatgpt_page, FluentIcon.MESSAGE, "ChatGPT")
        self.addSubInterface(self.ai_painting_page, FluentIcon.PALETTE, "AI 绘画")
        self.addSubInterface(self.gpt_sovits_page, FluentIcon.MICROPHONE, "GPT-SOVITS")
        self.addSubInterface(self.ai_music_page, FluentIcon.MUSIC, "AI 音乐")
        self.addSubInterface(self.story_page, FluentIcon.LABEL, "剧情")
        self.addSubInterface(self.make_logs_page, FluentIcon.DOCUMENT, "日志")
        self.addSubInterface(self.downloads_page, FluentIcon.CLOUD_DOWNLOAD, "资源下载")
        self.addSubInterface(self.options_page, FluentIcon.SETTING, "设置", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1280, 720)
        self.setWindowTitle("AI GAL 启动器")

    def create_page(self, object_name, text):
        page = QWidget()
        page.setObjectName(object_name)
        return page

    def create_menu_page(self, title):
        page = QWidget()
        page.setObjectName("menu_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel("AI GAL 启动器", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 30px; margin: 10px;")

        flipView = HorizontalFlipView()
        flipView.addImages(["gui_image/image.png"])
        flipView.currentIndexChanged.connect(lambda index: print("当前页面：", index))
        flipView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        flipView.setItemSize(QSize(1050, 300))
        flipView.setFixedSize(QSize(1050, 300))
        flipView.setBorderRadius(5)

        layout.addWidget(title_label)
        layout.addWidget(flipView, alignment=Qt.AlignCenter)

        button_layout = QGridLayout()
        button_layout.setContentsMargins(0, 20, 0, 20)
        button_layout.setSpacing(20)

        button1 = PushButton(FluentIcon.DELETE, '清除所有游戏内的资源文件')
        button2 = PushButton(FluentIcon.CANCEL, '重新开始新的游戏')
        button3 = PushButton(FluentIcon.GITHUB, 'Github')
        button4 = PrimaryPushButton(FluentIcon.RIGHT_ARROW, '开始游戏')

        button1.clicked.connect(self.clean_resource)
        button2.clicked.connect(self.restart)
        button3.clicked.connect(lambda: webbrowser.open('https://github.com/tamikip/AI-GAL'))
        button4.clicked.connect(self.Start_game)

        for button in (button1, button2, button3, button4):
            button.setFixedSize(500, 60)

        button_layout.addWidget(button1, 0, 0)
        button_layout.addWidget(button2, 0, 1)
        button_layout.addWidget(button3, 1, 0)
        button_layout.addWidget(button4, 1, 1)

        layout.addLayout(button_layout)

        layout.addStretch(1)

        bottom_left_label = StrongBodyLabel("AI GAL版本:1.4")
        bottom_left_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        bottom_left_label.setStyleSheet("font-size: 16px; margin: 10px;")

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(bottom_left_label)
        layout.addLayout(bottom_layout)

        return page

    def success_tips(self, content):
        InfoBar.success(
            title='成功',
            content=content,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=window
        )

    def error_tips(self, content):
        InfoBar.error(
            title='失败',
            content=content,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=window
        )

    def clean_resource(self):
        try:
            image_folder = "./images"
            audio_folder = "./audio"
            music_folder = "./music"
            cache_folder = "./cache"
            folders_to_delete = [audio_folder, music_folder, image_folder,cache_folder]
            for folder in folders_to_delete:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)

            self.success_tips("资源清理完成")

        except Exception as e:
            print(f"An error occurred: {e}")

    def restart(self):
        os.remove('story.txt')
        with open('story.txt', 'w') as file:
            pass
        self.success_tips("已经重置游戏")

    def check_web_port(self, url):
        """使用requests库检查Web端口是否有响应"""
        try:
            requests.get(url, timeout=0.5)
            return True
        except:
            return False

    def Start_game(self):
        sovits_url = "http://localhost:9880/"
        sd_url = "http://localhost:7860/"
        rembg_url = "http://localhost:7000/"
        config.read('config.ini', "utf-8")
        if not config.getboolean("SOVITS", "if_cloud"):
            if self.check_web_port(sovits_url):
                print("语音开启成功！")
            else:
                print("本地语音服务出现问题，请检查是否已开启本地语音服务")
                InfoBar.error(
                    title='本地语音服务出错',
                    content="请检查是否已开启本地语音服务",
                    orient=Qt.Vertical,
                    position=InfoBarPosition.BOTTOM_LEFT,
                    duration=-1,
                    parent=window
                )
                return
        if not config.getboolean("AI绘画", "if_cloud"):
            if self.check_web_port(sd_url):
                print("绘画开启成功！")
            else:
                print("本地绘画服务出现问题，请检查是否已开启本地绘画服务")
                InfoBar.error(
                    title='本地绘画服务出错',
                    content="请检查是否已开启本地绘画服务",
                    orient=Qt.Vertical,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,
                    parent=window
                )
                return
            if self.check_web_port(rembg_url):
                print("rembg开启成功！")
            else:
                print("rembg出现问题，请检查是否已开启rembg")
                InfoBar.error(
                    title='rembg服务出错',
                    content="请检查是否已开启rembg",
                    orient=Qt.Vertical,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,
                    parent=window
                )
                return
        self.success_tips("开启成功！准备开始游戏")
        QTimer.singleShot(1000, lambda: subprocess.Popen(aigal_exe_path))

    def try_run(self):
        sovits_if_cloud = config.getboolean("SOVITS", "if_cloud")
        draw_if_cloud = config.getboolean("AI绘画", "if_cloud")
        count = 0
        ProgressBar()
        try:
            gpt("you are ai", "say 1")
            count += 1
        except:
            self.error_tips("LLM配置未成功")

        if draw_if_cloud:
            try:
                response = online_generate("a girl", "character")
                count += 1
                if response == "error":
                    self.error_tips("云端绘画配置未成功")
            except:
                self.error_tips("云端绘画配置未成功")
        else:
            try:
                response = generate_image("a girl", "test", "character")
                if response == "error":
                    self.error_tips("本地绘画配置未成功")
                else:
                    count += 1
            except:
                self.error_tips("本地绘画配置未成功")

        if sovits_if_cloud:
            try:
                response = online_generate_audio("1", 1, "test")
                if response == "error":
                    print("云端语音配置未成功")
                    self.error_tips("云端语音配置未成功")
                else:
                    count += 1
            except:
                print("云端语音配置未成功")
                self.error_tips("云端语音配置未成功")
        else:
            try:
                response = generate_audio("V2", "a girl", "test", "character")
                if response == "error":
                    print("本地语音配置未成功")
                    self.error_tips("本地语音配置未成功")
                else:
                    count += 1
            except:
                print("本地语音配置未成功")
                self.error_tips("本地语音配置未成功")
        if count == 3:
            self.success_tips("测试完毕，暂未发现问题")

    def create_story_page(self, title):
        page = QWidget()
        page.setObjectName("story_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(10, 10, 10, 10)

        theme = self.config.get('剧情', 'theme', fallback='')
        outline = self.config.get('剧情', 'outline', fallback='')

        button = TransparentToolButton(FluentIcon.FOLDER_ADD)
        button.setMinimumSize(50, 40)
        button.setStyleSheet("font-size: 16px;")
        button.clicked.connect(lambda: self.openFileDialog(input_field2, "文本文件 (*.txt)"))

        input_field1 = LineEdit(page)
        input_field1.setPlaceholderText("主题")
        input_field1.setText(theme)
        input_field1.setMinimumHeight(40)

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("大纲地址")
        input_field2.setReadOnly(True)
        input_field2.setText(outline)
        input_field2.setMinimumHeight(40)

        h_layout = QHBoxLayout()
        h_layout.addWidget(input_field2)
        h_layout.addWidget(button)

        input_layout.addWidget(input_field1)
        input_layout.addLayout(h_layout)

        layout.addWidget(title_label)
        layout.addLayout(input_layout)

        input_field1.textChanged.connect(
            lambda: self.save_config('剧情', 'theme', input_field2.text()))
        input_field2.textChanged.connect(lambda: self.save_config('剧情', 'outline', input_field2.text()))

        return page

    def create_make_logs_page(self, title):
        page = QWidget()
        page.setObjectName("make_logs_page")

        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title_label)

        self.log_viewer = TextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.moveCursor(QTextCursor.End)
        self.log_viewer.setStyleSheet(
            "background-color: #f5f5f5; padding: 12px; font-size: 18px;")
        layout.addWidget(self.log_viewer)
        self.log_file_path = os.path.abspath(aigal_log_path)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(1000)
        self.update_logs()

        return page

    def update_logs(self):
        try:
            scroll_position = self.log_viewer.verticalScrollBar().value()
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                logs = file.read()
                self.log_viewer.setPlainText(logs)
            self.log_viewer.verticalScrollBar().setValue(scroll_position)

        except FileNotFoundError:
            self.log_viewer.setPlainText("Log file not found.")

    def create_chatgpt_page(self, title):
        page = QWidget()
        page.setObjectName("chatgpt_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(10, 10, 10, 10)

        url = self.config.get('CHATGPT', 'base_url', fallback='')
        model_name = self.config.get('CHATGPT', 'model', fallback='')
        api_key = self.config.get('CHATGPT', 'gpt_key', fallback='')

        input_field1 = LineEdit(page)
        input_field1.setPlaceholderText("请输入LLM的转发URL")
        input_field1.setText(url)
        input_field1.setMinimumHeight(40)

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("请输入模型名称")
        input_field2.setText(model_name)
        input_field2.setMinimumHeight(40)

        input_field3 = PasswordLineEdit(page)
        input_field3.setPlaceholderText("请输入API密钥")
        input_field3.setText(api_key)
        input_field3.setMinimumHeight(40)

        input_layout.addWidget(input_field1)
        input_layout.addWidget(input_field2)
        input_layout.addWidget(input_field3)

        layout.addWidget(title_label)
        layout.addLayout(input_layout)

        input_field1.textChanged.connect(
            lambda: self.save_config('CHATGPT', 'base_url', f"https://{input_field1.text()}/v1/chat/completions"))
        input_field2.textChanged.connect(lambda: self.save_config('CHATGPT', 'model', input_field2.text()))
        input_field3.textChanged.connect(lambda: self.save_config('CHATGPT', 'gpt_key', input_field3.text()))

        return page

    def save_config(self, section, key, value):
        try:
            if section not in self.config:
                self.config.add_section(section)
            self.config[section][key] = value
            with open('config.ini', 'w', encoding="utf-8") as configfile:
                self.config.write(configfile)
        except Exception as e:
            print(f"Error saving config: {e}")

    def create_ai_painting_page(self, title):
        page = QWidget()
        page.setObjectName("ai_painting_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        if_cloud = self.config.getboolean('AI绘画', 'if_cloud', fallback=False)
        draw_key = self.config.get('AI绘画', 'draw_key', fallback='')
        character_id = self.config.get('AI绘画', 'character_id', fallback='')
        background_id = self.config.get('AI绘画', 'background_id', fallback='')

        toggle_button = TogglePushButton(FluentIcon.CLOUD, '云端模式')
        toggle_button.setChecked(if_cloud)

        toggle_button.toggled.connect(
            lambda checked: self.save_config('AI绘画', 'if_cloud', str(checked)))

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(0, 10, 10, 10)

        input_field1 = PasswordLineEdit(page)
        input_field1.setPlaceholderText("云端绘画的API密钥")
        input_field1.setText(draw_key)
        input_field1.setMinimumHeight(40)

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("人物绘画模型ID(仅对云端模式生效)")
        input_field2.setText(character_id)
        input_field2.setMinimumHeight(40)

        input_field3 = LineEdit(page)
        input_field3.setPlaceholderText("背景绘画模型ID(仅对云端模式生效)")
        input_field3.setText(background_id)
        input_field3.setMinimumHeight(40)

        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignLeft)
        switch_layout.addWidget(toggle_button)

        layout.addWidget(title_label)
        layout.addLayout(switch_layout)
        input_layout.addWidget(input_field1)
        input_layout.addWidget(input_field2)
        input_layout.addWidget(input_field3)
        layout.addLayout(input_layout)

        input_field1.textChanged.connect(lambda: self.save_config('AI绘画', 'draw_key', input_field1.text()))
        input_field2.textChanged.connect(lambda: self.save_config('AI绘画', 'character_id', input_field2.text()))
        input_field3.textChanged.connect(lambda: self.save_config('AI绘画', 'background_id', input_field3.text()))

        return page

    def create_gpt_sovits_page(self, title):
        page = QWidget()
        page.setObjectName("gpt_sovits_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        # Add title label
        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        if_cloud = self.config.getboolean('SOVITS', 'if_cloud', fallback=False)
        api_key = self.config.get('SOVITS', '语音key', fallback='')
        version = self.config.get('SOVITS', 'version', fallback='')
        models = [
            self.config.get('SOVITS', 'model1', fallback=''),
            self.config.get('SOVITS', 'model2', fallback=''),
            self.config.get('SOVITS', 'model3', fallback=''),
            self.config.get('SOVITS', 'model4', fallback=''),
            self.config.get('SOVITS', 'model5', fallback=''),
            self.config.get('SOVITS', 'model6', fallback='')
        ]
        sovits_urls = [
            self.config.get('SOVITS', 'sovits_url1', fallback=''),
            self.config.get('SOVITS', 'sovits_url2', fallback=''),
            self.config.get('SOVITS', 'sovits_url3', fallback=''),
            self.config.get('SOVITS', 'sovits_url4', fallback=''),
            self.config.get('SOVITS', 'sovits_url5', fallback=''),
            self.config.get('SOVITS', 'sovits_url6', fallback='')
        ]

        def separate_url_parameters(url, mode):
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            refer_wav_path = query_params.get("refer_wav_path", [None])[0]
            prompt_text = query_params.get("prompt_text", [None])[0]
            return refer_wav_path if mode == "refer_wav_path" else prompt_text

        def update_url(original_url, new_value, mode):
            parsed_url = urlparse(original_url)
            query_params = parse_qs(parsed_url.query)

            if mode == "refer_wav_path":
                query_params["refer_wav_path"] = [new_value]
            else:
                query_params["prompt_text"] = [new_value]

            new_query = '&'.join(f"{key}={value[0]}" for key, value in query_params.items())
            return parsed_url._replace(query=new_query).geturl()

        standalone_input = LineEdit(page)
        standalone_input.setPlaceholderText("云端语音API密钥")
        standalone_input.setText(api_key)
        standalone_input.setMinimumHeight(40)
        standalone_input.textChanged.connect(lambda: self.save_config('SOVITS', 'api_key', standalone_input.text()))

        toggle_button = TogglePushButton(FluentIcon.CLOUD, '云端模式')
        toggle_button.setChecked(if_cloud)
        toggle_button.toggled.connect(lambda checked: self.save_config('SOVITS', 'if_cloud', str(checked)))

        comboBox = ComboBox()
        items = ['V1', 'V2']
        comboBox.addItems(items)
        comboBox.currentIndexChanged.connect(lambda index: self.save_config('SOVITS', 'version', str(index)))
        comboBox.setCurrentIndex(int(version))

        help = HyperlinkButton(FluentIcon.HELP, "https://tamikip.github.io/AI-GAL-doc/", "帮助")

        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignLeft)
        switch_layout.addWidget(toggle_button)
        switch_layout.addWidget(comboBox)
        switch_layout.addStretch(1)
        switch_layout.addWidget(help)

        layout.addWidget(title_label)
        layout.addLayout(switch_layout)
        layout.addWidget(standalone_input)

        def create_input_with_button(placeholder, url, model_key, url_key):
            h_layout = QHBoxLayout()

            input_field = LineEdit(page)
            input_field.setPlaceholderText(placeholder)
            input_field.setText(separate_url_parameters(url, "refer_wav_path"))
            input_field.setMinimumHeight(40)
            input_field.setReadOnly(True)
            input_field.textChanged.connect(
                lambda text: self.save_config('SOVITS', url_key, update_url(url, text, "refer_wav_path"))
            )

            button = TransparentToolButton(FluentIcon.FOLDER_ADD)
            button.setMinimumSize(50, 40)
            button.setStyleSheet("font-size: 16px;")
            button.clicked.connect(lambda: self.openFileDialog(input_field, "音频文件 (*.mp3 *.wav)"))

            speaker_input = LineEdit(page)
            speaker_input.setPlaceholderText("输入说话人语音文字")
            speaker_input.setText(separate_url_parameters(url, "prompt_text"))
            speaker_input.setMinimumHeight(40)
            speaker_input.textChanged.connect(
                lambda text: self.save_config('SOVITS', url_key, update_url(url, text, "prompt_text"))
            )

            model_input = LineEdit(page)
            model_input.setPlaceholderText("输入模型名称")
            model_input.setText(models[int(url_key[-1]) - 1])
            model_input.setMinimumHeight(40)
            model_input.textChanged.connect(lambda text: self.save_config('SOVITS', model_key, text))

            h_layout.addWidget(input_field)
            h_layout.addWidget(button)
            h_layout.addWidget(speaker_input)
            h_layout.addWidget(model_input)

            return h_layout

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(0, 10, 0, 10)

        placeholders = ["男主语音文件", "女1语音文件", "女2语音文件", "女3语音文件", "女4语音文件", "女5语音文件"]
        for i, (placeholder, url) in enumerate(zip(placeholders, sovits_urls)):
            model_key = f'model{i + 1}'
            url_key = f'sovits_url{i + 1}'
            input_layout.addLayout(create_input_with_button(placeholder, url, model_key, url_key))

        layout.addLayout(input_layout)

        return page

    def openFileDialog(self, lineEdit, type):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "选择文件", "", type, options=options)

        if fileName:
            lineEdit.setText(fileName)

    def create_ai_music_page(self, title):
        page = QWidget()
        page.setObjectName("ai_music_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")  # 增大字体

        if_on = self.config.getboolean('AI音乐', 'if_on', fallback=False)
        api_key = self.config.get('AI音乐', 'api_key', fallback='')
        base_url = self.config.get('AI音乐', 'base_url', fallback='')

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(0, 10, 10, 10)

        toggle_button = TogglePushButton(FluentIcon.PLAY, '开关')
        toggle_button.setChecked(if_on)

        toggle_button.toggled.connect(
            lambda checked: self.save_config('AI音乐', 'if_on', str(checked)))

        input_field1 = LineEdit(page)
        input_field1.setPlaceholderText("请输入AI音乐URL地址")
        input_field1.setText(base_url)
        input_field1.setMinimumHeight(40)

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("请输入API密钥")
        input_field2.setText(api_key)
        input_field2.setMinimumHeight(40)

        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignLeft)
        switch_layout.addWidget(toggle_button)

        input_field1.textChanged.connect(lambda: self.save_config('AI音乐', 'base_url', input_field1.text()))
        input_field2.textChanged.connect(lambda: self.save_config('AI音乐', 'api_key', input_field2.text()))

        layout.addWidget(title_label)
        layout.addLayout(switch_layout)
        input_layout.addWidget(input_field1)
        input_layout.addWidget(input_field2)
        layout.addLayout(input_layout)

        return page

    def create_options_page(self, title):
        options_page = QWidget()
        options_page.setObjectName("options_page")
        main_layout = QVBoxLayout(options_page)

        page_title = TitleLabel(title)
        page_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        main_layout.addWidget(page_title)

        class Config(QConfig):
            enableAcrylicBackground = ConfigItem("MainWindow", "EnableAcrylicBackground", False, BoolValidator())

        cfg = Config()
        qconfig.load("config.json", cfg)

        card = SwitchSettingCard(
            icon=FluentIcon.TRANSPARENT,
            title="启用亚克力效果",
            content="亚克力效果的视觉体验更好，但是可能导致窗口卡顿",
            configItem=cfg.enableAcrylicBackground
        )
        main_layout.addWidget(card)

        class Config(QConfig):
            dpiScale = OptionsConfigItem(
                "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

        cfg = Config()
        qconfig.load("config.json", cfg)

        card = ComboBoxSettingCard(
            configItem=cfg.dpiScale,
            icon=FluentIcon.ZOOM,
            title="界面缩放",
            content="调整组件和字体的大小",
            texts=["100%", "125%", "150%", "175%", "200%", "跟随系统设置"]
        )

        main_layout.addWidget(card)
        cfg.dpiScale.valueChanged.connect(print)

        # 添加分组
        main_layout.addWidget(self.create_section("个性化", [
            self.create_card("应用主题", "调整视觉的外观", FluentIcon.PALETTE,
                             self.create_combo(["浅色", "深色"], self.on_theme_change))
        ]))

        main_layout.addWidget(self.create_section("软件更新", [
            self.create_card("自动更新", "在应用启动时检查更新", FluentIcon.UPDATE,
                             self.create_switch(self.on_auto_update_toggle))
        ]))

        main_layout.addWidget(self.create_section("关于", [
            self.create_card("试运行", "看看配置有没有出错", FluentIcon.PLAY_SOLID,
                             self.create_button("开始", self.try_run)),
            self.create_card("检查更新", "看看有没有新版本", FluentIcon.CLOUD_DOWNLOAD,
                             self.create_button("检查更新", self.on_check_update_clicked))
        ]))

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        gpt_sovits_card = HyperlinkCard(
            url="https://tamikip.github.io/AI-GAL-doc",
            text="查看",
            icon=FluentIcon.QUICK_NOTE,
            title="使用文档",
            content="不会使用？来看！"
        )
        main_layout.addWidget(gpt_sovits_card)

        return options_page

    def create_downloads_page(self, title):
        downloads_page = QWidget()
        downloads_page.setObjectName("downloads_page")
        main_layout = QVBoxLayout(downloads_page)
        main_layout.setAlignment(Qt.AlignTop)

        page_title = TitleLabel(title)
        page_title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px 0;")
        page_title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        main_layout.addWidget(page_title)

        ai_draw_card = HyperlinkCard(
            url="https://pan.quark.cn/s/2c832199b09b",
            text="下载",
            icon=FluentIcon.PALETTE,
            title="AI绘画整合包",
            content="下载AI绘画整合包"
        )
        main_layout.addWidget(ai_draw_card)

        gpt_sovits_card = HyperlinkCard(
            url="https://www.123pan.com/s/5tIqVv-GVRcv.html",
            text="下载",
            icon=FluentIcon.MICROPHONE,
            title="GPT-SOVITS整合包",
            content="下载GPT-SOVITS整合包"
        )
        main_layout.addWidget(gpt_sovits_card)

        gpt_sovits_model_card = HyperlinkCard(
            url="https://www.ai-hobbyist.com/forum-121-1.html",
            text="下载",
            icon=FluentIcon.CLOUD,
            title="GPT-SOVITS模型资源",
            content="各种各样的模型资源"
        )
        main_layout.addWidget(gpt_sovits_model_card)

        rembg_card = HyperlinkCard(
            url="https://github.com/danielgatis/rembg/releases/download/v2.0.60/rembg-cli-installer.exe",
            text="下载",
            icon=FluentIcon.PHOTO,
            title="Rembg下载",
            content="用于本地SD的抠图(下载可能要魔法)"
        )
        main_layout.addWidget(rembg_card)

        return downloads_page

    def create_section(self, title, cards):
        section_layout = QVBoxLayout()
        section_label = TitleLabel(title)
        section_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px 0;")
        section_layout.addWidget(section_label)

        for card in cards:
            section_layout.addWidget(card)
        return self.wrap_in_widget(section_layout)

    def create_card(self, title, subtitle, icon, control):
        card = CardWidget(self)
        card_layout = QHBoxLayout()

        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(32, 32)

        text_layout = QVBoxLayout()
        title_label = TitleLabel(title)
        title_label.setStyleSheet("font-size: 14px;")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 12px; color: gray;")
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        left_layout = QHBoxLayout()
        left_layout.addWidget(icon_widget)
        left_layout.addLayout(text_layout)

        card_layout.addLayout(left_layout)
        card_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        card_layout.addWidget(control)

        card.setLayout(card_layout)
        return card

    def create_combo(self, items, on_change_callback):
        combo = ComboBox(self)
        combo.addItems(items)
        combo.currentIndexChanged.connect(on_change_callback)
        return combo

    def create_switch(self, on_toggle_callback):
        switch = SwitchButton()
        switch.setChecked(auto_update)
        switch.checkedChanged.connect(on_toggle_callback)
        return switch

    def create_button(self, text, on_click_callback):
        button = PushButton(text, self)
        button.clicked.connect(on_click_callback)
        return button

    def wrap_in_widget(self, layout):
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def on_theme_change(self, index):
        themes = ["浅色", "深色"]
        selected_theme = themes[index]
        if selected_theme == "浅色":
            setTheme(Theme.LIGHT)
        else:
            setTheme(Theme.DARK)
        InfoBar.success(
            title="主题已切换",
            content=f"当前主题: {selected_theme}",
            position=InfoBarPosition.TOP_RIGHT,
            parent=self
        )

    def on_auto_update_toggle(self, checked):
        status = "启用" if checked else "禁用"
        if status == "启用":
            self.save_config("Settings", "auto_update", "True")
        else:
            self.save_config("Settings", "auto_update", "False")

        InfoBar.info("自动更新", f"自动更新已{status}", position=InfoBarPosition.TOP_RIGHT, parent=self)

    def on_check_update_clicked(self):
        if updater():
            InfoBar.success(
                title="检查更新",
                content="当前已经是最新版本！",
                position=InfoBarPosition.TOP_RIGHT,
                parent=self
            )


class Worker(QThread):
    finished = pyqtSignal()

    def run(self):
        update.update_program()
        self.finished.emit()


class CustomMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('更新中,请勿退出')
        self.bar = IndeterminateProgressBar(start=True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.bar)
        self.widget.setMinimumSize(500, 200)


def showMessage(window):
    w = CustomMessageBox(window)
    w.yesButton.hide()
    w.cancelButton.hide()
    worker = Worker()
    worker.finished.connect(w.accept)
    worker.start()
    if w.exec():
        w = Dialog("更新成功！", "请自行解压替换", )
        w.yesButton.setText("更新")
        w.cancelButton.hide()
        if w.exec():
            pass


def updater():
    with open("version.txt", "r") as file:
        version = file.read()
    try:
        latest_version = update.get_latest_release()["tag_name"]
        if not latest_version == version:
            update_docx = requests.get(
                "https://github.moeyy.xyz/https://raw.githubusercontent.com/tamikip/AI-GAL/main/update_docx.txt").text
            w = Dialog(f"AI GAL可以更新到{latest_version}版本！", update_docx, )
            w.yesButton.setText("更新")
            w.cancelButton.setText("稍后")
            if w.exec():
                showMessage(window)
            else:
                print('取消')
        else:
            return True
    except:
        print("检查更新失败！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    if auto_update:
        updater()
    sys.exit(app.exec_())
