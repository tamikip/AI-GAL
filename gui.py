# 默认深色模式和json模式
# 修改了字体大小
# 修改了初始化以便深色模式正常工作
# 改为toml配置文件
# 改为mac,linux,win全平台支持的路径格式
import os
import shutil
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs, urlencode
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt5.QtGui import QIcon, QTextCursor, QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,  QSizePolicy, QGridLayout
from qfluentwidgets import (NavigationItemPosition, LineEdit, TitleLabel, TogglePushButton, TransparentToolButton, ComboBox, PushButton, FluentIcon, Theme, setTheme, InfoBar, InfoBarPosition, HyperlinkCard, HorizontalFlipView, PrimaryPushButton, StrongBodyLabel, HyperlinkButton, PasswordLineEdit, FluentWindow, Dialog, IndeterminateProgressBar, MessageBoxBase, SubtitleLabel, SwitchSettingCard, TextEdit, PrimaryPushSettingCard, SingleDirectionScrollArea, CardWidget, theme)
import update
import subprocess
import zipfile
import toml

from PIL import Image, ImageDraw, ImageFont



# --- 全局路径常量 ---
GAME_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
AIGAL_EXE_PATH = os.path.join(GAME_ROOT_DIR, "AIGAL.exe")
AIGAL_SH_PATH = os.path.join(GAME_ROOT_DIR, "AIGAL.sh")
AIGAL_LOG_PATH = os.path.join(GAME_ROOT_DIR, "log.txt")

# 读取TOML配置文件
try:
    with open('config.toml', 'r', encoding='utf-8') as f:
        config = toml.load(f)
except FileNotFoundError:
    config = {}

auto_update = config.get('Settings', {}).get('auto_update', False)


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.snapshot_folder = os.path.join(os.getcwd(), "snapshot")
        self.snapshots = self.get_snapshots()
        self.setWindowTitle("AI GAL 启动器")
        self.navigationInterface.setExpandWidth(200)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setGeometry(200, 200, 1280, 720)
        with open('config.toml', 'r', encoding='utf-8') as f:
            self.config = toml.load(f)
        self.menu_page = self.create_menu_page("主页")
        self.chatgpt_page = self.create_chatgpt_page("ChatGPT")
        self.ai_painting_page = self.create_ai_painting_page("AI 绘画")
        self.gpt_sovits_page = self.create_gpt_sovits_page("GPT-SOVITS")
        self.ai_music_page = self.create_ai_music_page("AI 音乐")
        self.story_page = self.create_story_page("剧情")
        self.snapshot_page = self.create_snapshot_page("快照")
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
        self.addSubInterface(self.snapshot_page, FluentIcon.SAVE, "快照")
        self.addSubInterface(self.make_logs_page, FluentIcon.DOCUMENT, "日志")
        self.addSubInterface(self.downloads_page, FluentIcon.CLOUD_DOWNLOAD, "资源下载")
        self.addSubInterface(self.options_page, FluentIcon.SETTING, "设置", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(1280, 720)
        self.setWindowTitle("AI GAL 启动器")

    def create_page(self, object_name):
        page = QWidget()
        page.setObjectName(object_name)
        return page

    def create_menu_page(self, title):
        page = QWidget()
        page.setObjectName("menu_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = TitleLabel("AI GAL 启动器", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        font = title_label.font()
        font.setPointSize(24)
        title_label.setFont(font)

        flipView = HorizontalFlipView()
        flipView.addImages([os.path.join("gui_image", "image.png")])
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
        button4.clicked.connect(self.start_game)

        for button in (button1, button2, button3, button4):
            button.setFixedSize(500, 60)

        button_layout.addWidget(button1, 0, 0)
        button_layout.addWidget(button2, 0, 1)
        button_layout.addWidget(button3, 1, 0)
        button_layout.addWidget(button4, 1, 1)

        layout.addLayout(button_layout)
        layout.addStretch(1)

        bottom_left_label = StrongBodyLabel("AI GAL版本:1.6\nqq群:982330586")
        bottom_left_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        
        font = bottom_left_label.font()
        font.setPointSize(12)
        bottom_left_label.setFont(font)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addWidget(bottom_left_label)
        layout.addLayout(bottom_layout)

        return page

    def success_tips(self, content):
        InfoBar.success('成功', content, orient=Qt.Horizontal, isClosable=False, position=InfoBarPosition.TOP, duration=2000, parent=self)

    def error_tips(self, content):
        InfoBar.error('失败', content, orient=Qt.Horizontal, isClosable=False, position=InfoBarPosition.TOP, duration=2000, parent=self)

    def clean_resource(self):
        folders_to_delete = [
            os.path.join(os.getcwd(), "audio"),
            os.path.join(os.getcwd(), "music"),
            os.path.join(os.getcwd(), "saves"),
            os.path.join(os.getcwd(), "images"),
            os.path.join(os.getcwd(), "cache")
        ]
        for folder in folders_to_delete:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
        self.success_tips("资源清理完成")

    def restart(self):
        story_txt_path = os.path.join(os.getcwd(), 'story.txt')
        if os.path.exists(story_txt_path):
            os.remove(story_txt_path)
        with open(story_txt_path, 'w', encoding='utf-8'):
            pass
        self.success_tips("已经重置游戏")

    def check_web_port(self, url):
        try:
            requests.get(url, timeout=0.5)
            return True
        except requests.RequestException:
            return False

    def start_game(self):
        sovits_url = "http://127.0.0.1:9880/"
        comfyui_url = "http://127.0.0.1:8188/"

        sovits_config = self.config.get('SOVITS', {})
        if sovits_config.get('if_on', True) and not sovits_config.get('if_cloud', False):
            if not self.check_web_port(sovits_url):
                InfoBar.error('本地语音服务出错', "请检查是否已开启本地语音服务", orient=Qt.Vertical, position=InfoBarPosition.BOTTOM_LEFT, duration=-1, parent=self)
                return

        if not self.config.get('AI绘画', {}).get('if_cloud', False):
            if not self.check_web_port(comfyui_url):
                InfoBar.error('本地绘画服务出错', "请检查是否已开启本地绘画服务", orient=Qt.Vertical, position=InfoBarPosition.BOTTOM_RIGHT, duration=-1, parent=self)
                return
        self.success_tips("服务检查完成！准备开始游戏")
        if sys.platform.startswith('win'):
            QTimer.singleShot(1000, lambda: subprocess.Popen([AIGAL_EXE_PATH]))
        elif sys.platform.startswith(('linux', 'darwin')):
            QTimer.singleShot(1000, lambda: subprocess.Popen(["/bin/bash", AIGAL_SH_PATH]))
        else:
            self.error_tips("暂不支持此操作系统")


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
        story_config = self.config.get('剧情', {})
        theme_text = story_config.get('theme', '')
        outline_path = story_config.get('outline', '')
        theme_language = story_config.get('Language', '中文')

        input_field1 = LineEdit(page)
        input_field1.setPlaceholderText("主题")
        input_field1.setText(theme_text)
        input_field1.setMinimumHeight(40)
        input_field1.textChanged.connect(lambda: self.save_config('剧情', 'theme', input_field1.text()))

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("大纲文件地址")
        input_field2.setText(outline_path)
        input_field2.setMinimumHeight(40)
        input_field2.textChanged.connect(lambda: self.save_config('剧情', 'outline', input_field2.text()))

        button = TransparentToolButton(FluentIcon.FOLDER_ADD)
        button.setMinimumSize(50, 40)
        button.clicked.connect(lambda: self.openFileDialog(input_field2, "文本文件 (*.txt)"))

        h_layout = QHBoxLayout()
        h_layout.addWidget(input_field2)
        h_layout.addWidget(button)

        comboBox = ComboBox()
        items = ['中文', '英文', '日文']
        comboBox.addItems(items)
        if theme_language in items:
            comboBox.setCurrentIndex(items.index(theme_language))
        comboBox.currentIndexChanged.connect(lambda idx: self.save_config('剧情', 'Language', items[idx]))

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.addWidget(input_field1)
        input_layout.addLayout(h_layout)

        layout.addWidget(title_label)
        layout.addWidget(comboBox)
        layout.addLayout(input_layout)
        return page

    def create_snapshot_page(self, title):
        page = QWidget()
        page.setObjectName("snapshot_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("font-size: 24px; margin-bottom: 15px;")

        save_button = PrimaryPushButton('保存当前快照', page)
        save_button.clicked.connect(self.save_snapshot)
        save_button.setMinimumSize(100, 50)
        save_button.setFixedWidth(150)

        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(save_button)

        scroll_area = SingleDirectionScrollArea(orient=Qt.Vertical)
        scroll_area.setStyleSheet("QScrollArea{background: transparent; border: none}")
        scroll_area.setWidgetResizable(True)

        self.snapshot_list_widget = QWidget()
        self.snapshot_list_layout = QVBoxLayout(self.snapshot_list_widget)
        self.snapshot_list_layout.setSpacing(15)
        self.snapshot_list_layout.setAlignment(Qt.AlignTop)
        self.snapshot_list_layout.setContentsMargins(0, 0, 0, 0)
        self.snapshot_list_widget.setStyleSheet("background: transparent;")
        
        self.refresh_snapshot_list()

        scroll_area.setWidget(self.snapshot_list_widget)
        
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area, 1)
        return page

    def refresh_snapshot_list(self):
        while self.snapshot_list_layout.count():
            item = self.snapshot_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.snapshots = self.get_snapshots()
        if not self.snapshots:
            empty_label = StrongBodyLabel("暂无快照，请点击上方按钮创建快照")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 16px; color: #888; margin: 50px;")
            self.snapshot_list_layout.addWidget(empty_label)
        else:
            for snapshot_name in self.snapshots:
                snapshot_base_name = snapshot_name.removesuffix(".zip")
                card = self.create_snapshot_card(snapshot_base_name)
                self.snapshot_list_layout.addWidget(card)
        
        self.snapshot_list_layout.addStretch(1)

    def create_snapshot_card(self, snapshot_base_name):
        card = CardWidget()
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        
        thumbnail_path = os.path.join(self.snapshot_folder, f"{snapshot_base_name}.png")
        thumbnail_label = TitleLabel()
        thumbnail_label.setFixedSize(200, 120)
        
        if os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path).scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumbnail_label.setPixmap(pixmap)
        else:
            thumbnail_label.setText("无缩略图")
            thumbnail_label.setStyleSheet("background-color: #f0f0f0; color: #888; border: 1px solid #ddd; border-radius: 4px;")
            thumbnail_label.setAlignment(Qt.AlignCenter)
        
        info_label = StrongBodyLabel(snapshot_base_name)
        info_label.setStyleSheet("font-size: 20px; color: #333;")
        card_layout.addWidget(info_label, 1)  # 1表示可伸展
        restore_button = PushButton("还原快照")
        restore_button.setFixedSize(150, 50)
        restore_button.clicked.connect(lambda _, name=snapshot_base_name: self.restore_snapshot(name))
        
        card_layout.addWidget(thumbnail_label)
        card_layout.addWidget(info_label, 1)
        card_layout.addWidget(restore_button)
        
        return card

    def find_first_1920x1080_image(self):
        for root, _, files in os.walk("images"):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(root, file)
                    try:
                        with Image.open(img_path) as img:
                            if img.size == (1920, 1080):
                                return img_path
                    except Exception:
                        continue
        return None

    def add_text_to_image(self, image_path, text, output_path):
        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("SourceHanSansLite.ttf", 150)
        except IOError:
            font = ImageFont.load_default()

        image_width, image_height = image.size
        max_width = image_width * 0.8
        lines = []
        line = ""
        for char in text:
            test_line = line + char
            text_bbox = draw.textbbox((0, 0), test_line, font=font)
            if text_bbox[2] - text_bbox[0] <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = char
        lines.append(line)

        text_heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]
        total_text_height = sum(text_heights) + (len(lines) - 1) * 10
        y = (image_height - total_text_height) / 2
        
        padding = 10
        bg_x1, bg_y1 = image_width * 0.1, y - padding
        bg_x2, bg_y2 = image_width * 0.9, y + total_text_height + padding
        
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(0, 0, 0, 150))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        
        outline_color = "black"
        for line in lines:
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (image_width - text_width) / 2
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
                draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            draw.text((x, y), line, font=font, fill="white")
            y += text_height + 10
        
        image = image.resize((640, 360), Image.LANCZOS)
        image.convert("RGB").save(output_path)

    def get_snapshots(self):
        if not os.path.exists(self.snapshot_folder):
            return []
        return sorted([f for f in os.listdir(self.snapshot_folder) if f.lower().endswith(".zip")])

    def save_snapshot(self):
        try:
            with open("title.txt", "r", encoding="utf-8") as file:
                title = file.read().strip()
            if not title:
                self.error_tips("标题为空，无法创建快照")
                return
        except FileNotFoundError:
            self.error_tips("未找到 title.txt 文件，无法创建快照")
            return

        try:
            self.packer(title)
            self.success_tips(f"成功保存快照: {title}")
            self.refresh_snapshot_list()
        except Exception as e:
            self.error_tips(f"保存快照失败: {e}")

    def packer(self, title):
        os.makedirs(self.snapshot_folder, exist_ok=True)
        
        directories = ["audio", "images", "music"]
        files_to_pack = ["characters.txt", "character_info.txt", "choice.txt", "story.txt", "dialogues.json"]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        zip_path = os.path.join(self.snapshot_folder, f"{title}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for directory in directories:
                for root, _, files_in_dir in os.walk(directory):
                    for file in files_in_dir:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.getcwd()).replace(os.sep, '/')
                        zipf.write(file_path, arcname)
            for file in files_to_pack:
                if os.path.exists(file):
                    zipf.write(file, file.replace(os.sep, '/'))

        img_path = self.find_first_1920x1080_image()
        output_img_path = os.path.join(self.snapshot_folder, f"{title}.png")
        if img_path:
            self.add_text_to_image(img_path, title, output_img_path)
        else:
            self.create_placeholder_image(output_img_path, title)

    def create_placeholder_image(self, output_path, text):
        image = Image.new('RGB', (640, 360), color=(100, 100, 100))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("SourceHanSansLite.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((640 - text_width) // 2, (360 - text_height) // 2)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        image.save(output_path)

    def restore_snapshot(self, snapshot_name):
        snapshot_path = os.path.join(self.snapshot_folder, f"{snapshot_name}.zip")
        if os.path.exists(snapshot_path):
            try:
                with zipfile.ZipFile(snapshot_path, 'r') as zip_ref:
                    zip_ref.extractall(".")
                self.success_tips(f"成功还原快照 {snapshot_name}")
            except Exception as e:
                self.error_tips(f"还原快照失败: {e}")
        else:
            self.error_tips(f"找不到快照文件 {snapshot_path}")

    def create_make_logs_page(self, title):
        page = QWidget()
        page.setObjectName("make_logs_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面")
        layout.addWidget(title_label)

        self.log_viewer = TextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("background-color: #f5f5f5; padding: 12px; font-size: 18px;")
        layout.addWidget(self.log_viewer)
        
        self.log_file_path = AIGAL_LOG_PATH
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(1000)
        self.update_logs()

        return page

    def update_logs(self):
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r', encoding='utf-8') as file:
                    logs = file.read()
                current_text = self.log_viewer.toPlainText()
                if logs != current_text:
                    self.log_viewer.setPlainText(logs)
                    self.log_viewer.moveCursor(QTextCursor.End)
            else:
                self.log_viewer.setPlainText("日志文件不存在...")
        except Exception as e:
            self.log_viewer.setPlainText(f"读取日志文件失败: {e}")

    def create_chatgpt_page(self, title):
        page = QWidget()
        page.setObjectName("chatgpt_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        chatgpt_config = self.config.get('CHATGPT', {})
        url = chatgpt_config.get('base_url', '')
        model_name = chatgpt_config.get('model', '')
        api_key = chatgpt_config.get('gpt_key', '')
        proxy = chatgpt_config.get('proxy', '')
        model_supplier = chatgpt_config.get('ModelSupplier', 'OpenAI')

        # 模型供应商列表
        supplier_layout = QHBoxLayout()
        supplier_label = StrongBodyLabel("模型供应商:", page)
        supplier_combo = ComboBox()
        suppliers = ['OpenAI', 'GoogleAIstudio', 'Ollama']
        supplier_combo.addItems(suppliers)
        if model_supplier in suppliers:
            supplier_combo.setCurrentIndex(suppliers.index(model_supplier))
        
        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(supplier_combo)
        supplier_layout.setContentsMargins(10, 10, 10, 20)

        input_field1 = LineEdit(page)
        input_field1.setPlaceholderText("请输入LLM的转发URL")
        input_field1.setText(url)

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("请输入模型名称")
        input_field2.setText(model_name)

        input_field3 = PasswordLineEdit(page)
        input_field3.setPlaceholderText("请输入API密钥")
        input_field3.setText(api_key)

        input_field4 = LineEdit(page)
        input_field4.setPlaceholderText("请输入代理地址 (例如: http://127.0.0.1:7890)")
        input_field4.setText(proxy)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(10, 10, 10, 10)
        for widget in [input_field1, input_field2, input_field3, input_field4]:
            widget.setMinimumHeight(40)
            input_layout.addWidget(widget)

        layout.addWidget(title_label)
        layout.addLayout(supplier_layout)
        layout.addLayout(input_layout)

        def update_visibility(index):
            supplier = suppliers[index]
            if supplier == 'OpenAI':
                input_field1.show()
                input_field3.show()
                input_field4.show()
            elif supplier == 'GoogleAIstudio':
                input_field1.hide()
                input_field3.show()
                input_field4.show()
            elif supplier == 'Ollama':
                input_field1.hide()
                input_field3.hide()
                input_field4.hide()
            self.save_config('CHATGPT', 'ModelSupplier', supplier)

        supplier_combo.currentIndexChanged.connect(update_visibility)
        update_visibility(supplier_combo.currentIndex())

        input_field1.textChanged.connect(lambda text: self.save_config('CHATGPT', 'base_url', text))
        input_field2.textChanged.connect(lambda text: self.save_config('CHATGPT', 'model', text))
        input_field3.textChanged.connect(lambda text: self.save_config('CHATGPT', 'gpt_key', text))
        input_field4.textChanged.connect(lambda text: self.save_config('CHATGPT', 'proxy', text))

        return page

    def save_config(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open('config.toml', 'w', encoding="utf-8") as f:
            toml.dump(self.config, f)

    def create_ai_painting_page(self, title):
        page = QWidget()
        page.setObjectName("ai_painting_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        ai_config = self.config.get('AI绘画', {})
        if_ComfyUI = ai_config.get('if_ComfyUI', False)
        if_cloud = ai_config.get('if_cloud', False)
        draw_key = ai_config.get('draw_key', '')
        character_id = ai_config.get('character_id', '')
        background_id = ai_config.get('background_id', '')
        comfyui_address = ai_config.get('comfyui_address', '')

        toggle_button = TogglePushButton('云端模式', self, FluentIcon.CLOUD)
        toggle_button.setChecked(if_cloud)
        toggle_button.toggled.connect(lambda checked: self.save_config('AI绘画', 'if_cloud', checked))

        toggle_button2 = TogglePushButton('ComfyUI', self, FluentIcon.IOT)
        toggle_button2.setChecked(if_ComfyUI)
        toggle_button2.toggled.connect(lambda checked: self.save_config('AI绘画', 'if_ComfyUI', checked))

        input_field4 = LineEdit(page)
        input_field4.setPlaceholderText("comfyui路径(可不填，默认127.0.0.1:8188)")
        input_field4.setText(comfyui_address)

        input_field1 = PasswordLineEdit(page)
        input_field1.setPlaceholderText("云端绘画的API密钥")
        input_field1.setText(draw_key)

        input_field2 = LineEdit(page)
        input_field2.setPlaceholderText("人物绘画模型ID(仅对云端模式生效)")
        input_field2.setText(character_id)

        input_field3 = LineEdit(page)
        input_field3.setPlaceholderText("背景绘画模型ID(仅对云端模式生效)")
        input_field3.setText(background_id)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(0, 10, 10, 10)
        for widget in [input_field4, input_field1, input_field2, input_field3]:
            widget.setMinimumHeight(40)
            input_layout.addWidget(widget)

        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignLeft)
        switch_layout.addWidget(toggle_button)
        switch_layout.addWidget(toggle_button2)

        layout.addWidget(title_label)
        layout.addLayout(switch_layout)
        layout.addLayout(input_layout)

        input_field1.textChanged.connect(lambda text: self.save_config('AI绘画', 'draw_key', text))
        input_field2.textChanged.connect(lambda text: self.save_config('AI绘画', 'character_id', text))
        input_field3.textChanged.connect(lambda text: self.save_config('AI绘画', 'background_id', text))
        input_field4.textChanged.connect(lambda text: self.save_config('AI绘画', 'comfyui_address', text))

        return page

    def create_gpt_sovits_page(self, title):
        page = QWidget()
        page.setObjectName("gpt_sovits_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        # --- 读取整个 SOVITS 配置区 ---
        sovits_config = self.config.get('SOVITS', {})
        if_cloud = sovits_config.get('if_cloud', False)
        api_key = sovits_config.get('api_key', '')
        if_on = sovits_config.get('if_on', True) 

        # --- 顶部控件 ---
        toggle_button = TogglePushButton('云端模式', self, FluentIcon.CLOUD)
        toggle_button.setChecked(if_cloud)
        toggle_button.toggled.connect(lambda checked: self.save_config('SOVITS', 'if_cloud', checked))

        help_button = HyperlinkButton(FluentIcon.HELP, "https://tamikip.github.io/AI-GAL-doc/", "帮助")

        header_layout = QHBoxLayout()
        header_layout.addWidget(toggle_button)
        header_layout.addStretch(1)
        header_layout.addWidget(help_button)

        api_key_input = LineEdit(page)
        api_key_input.setPlaceholderText("云端语音API密钥")
        api_key_input.setText(api_key)
        api_key_input.setMinimumHeight(40)
        api_key_input.textChanged.connect(lambda text: self.save_config('SOVITS', 'api_key', text))

        # --- 添加启用语音的开关 ---
        voice_toggle_card = SwitchSettingCard(
            FluentIcon.MICROPHONE,
            "启用语音",
            "是否在游戏中生成角色语音",
            parent=page
        )
        voice_toggle_card.setChecked(if_on)
        voice_toggle_card.checkedChanged.connect(
            lambda checked: self.save_config('SOVITS', 'if_on', checked)
        )

        layout.addWidget(title_label)
        layout.addLayout(header_layout)
        layout.addWidget(api_key_input)
        layout.addWidget(voice_toggle_card)

        # --- 动态模型输入区 ---
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)
        input_layout.setContentsMargins(0, 10, 0, 10)

        models = sovits_config.get('models', [])
        placeholders = ["男主", "女主1", "女主2", "女主3", "女主4", "女主5"]

        def get_url_param(url, param_name):
            try:
                return parse_qs(urlparse(url).query).get(param_name, [''])[0]
            except (AttributeError, IndexError):
                return ''

        def update_url_param(original_url, param_name, new_value):
            parsed_url = urlparse(original_url or 'http://127.0.0.1:9880/tts?')
            query_params = parse_qs(parsed_url.query)
            query_params[param_name] = [new_value]
            if 'prompt_language' not in query_params:
                query_params['prompt_language'] = ['zh']
            new_query = urlencode(query_params, doseq=True)
            return parsed_url._replace(query=new_query).geturl()

        for i, model_data in enumerate(models):
            h_layout = QHBoxLayout()
            
            model_name = model_data.get('name', '')
            url = model_data.get('url', '')
            
            ref_audio = get_url_param(url, 'ref_audio_path')
            prompt_text = get_url_param(url, 'prompt_text')
            
            ref_audio_input = LineEdit(page)
            ref_audio_input.setPlaceholderText(f"{placeholders[i]} 参考音频")
            ref_audio_input.setText(ref_audio)
            ref_audio_input.setReadOnly(True)

            file_button = TransparentToolButton(FluentIcon.FOLDER_ADD)
            file_button.clicked.connect(lambda _, le=ref_audio_input: self.openFileDialog(le, "音频文件 (*.mp3 *.wav)"))

            prompt_input = LineEdit(page)
            prompt_input.setPlaceholderText("参考音频文本")
            prompt_input.setText(prompt_text)

            model_input = LineEdit(page)
            model_input.setPlaceholderText("模型名称(本地)")
            model_input.setText(model_name)

            for widget in [ref_audio_input, prompt_input, model_input, file_button]:
                widget.setMinimumHeight(40)

            def save_and_update_config():
                self.save_config('SOVITS', 'models', models)

            ref_audio_input.textChanged.connect(lambda text, i=i: [
                models[i].update({'url': update_url_param(models[i].get('url'), 'ref_audio_path', text)}),
                save_and_update_config()
            ])
            prompt_input.textChanged.connect(lambda text, i=i: [
                models[i].update({'url': update_url_param(models[i].get('url'), 'prompt_text', text)}),
                save_and_update_config()
            ])
            model_input.textChanged.connect(lambda text, i=i: [
                models[i].update({'name': text}),
                save_and_update_config()
            ])

            h_layout.addWidget(ref_audio_input, 2)
            h_layout.addWidget(file_button)
            h_layout.addWidget(prompt_input, 2)
            h_layout.addWidget(model_input, 1)
            input_layout.addLayout(h_layout)

        layout.addLayout(input_layout)
        return page

    def openFileDialog(self, lineEdit, file_type):
        fileName, _ = QFileDialog.getOpenFileName(self, "选择文件", "", file_type, options=QFileDialog.Options())
        if fileName:
            lineEdit.setText(fileName)

    def create_ai_music_page(self, title):
        page = QWidget()
        page.setObjectName("ai_music_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(f"{title} 页面", page)
        title_label.setStyleSheet("font-size: 24px; margin: 10px;")

        music_config = self.config.get('AI音乐', {})
        if_on = music_config.get('if_on', False)
        api_key = music_config.get('api_key', '')
        base_url = music_config.get('base_url', '')

        toggle_button = TogglePushButton('开关', self, FluentIcon.PLAY)
        toggle_button.setChecked(if_on)
        toggle_button.toggled.connect(lambda checked: self.save_config('AI音乐', 'if_on', checked))

        input_field1 = LineEdit(page)
        input_field1.setPlaceholderText("请输入AI音乐URL地址")
        input_field1.setText(base_url)

        input_field2 = PasswordLineEdit(page)
        input_field2.setPlaceholderText("请输入API密钥")
        input_field2.setText(api_key)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(40)
        input_layout.setContentsMargins(0, 10, 10, 10)
        for widget in [input_field1, input_field2]:
            widget.setMinimumHeight(40)
            input_layout.addWidget(widget)

        switch_layout = QHBoxLayout()
        switch_layout.setAlignment(Qt.AlignLeft)
        switch_layout.addWidget(toggle_button)

        input_field1.textChanged.connect(lambda text: self.save_config('AI音乐', 'base_url', text))
        input_field2.textChanged.connect(lambda text: self.save_config('AI音乐', 'api_key', text))

        layout.addWidget(title_label)
        layout.addLayout(switch_layout)
        layout.addLayout(input_layout)
        return page

    def create_options_page(self, title):
        page = QWidget()
        page.setObjectName("options_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(title, page)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title_label)

        settings_config = self.config.get('Settings', {})

        auto_update_card = SwitchSettingCard(FluentIcon.UPDATE, "自动更新", "软件启动时自动检查更新")
        auto_update_card.setChecked(settings_config.get('auto_update', False))
        auto_update_card.checkedChanged.connect(self.on_auto_update_toggle)
        layout.addWidget(auto_update_card)

        theme_card = SwitchSettingCard(FluentIcon.BRUSH, "深色模式", "更适合在夜晚使用")
        theme_card.setChecked(theme() == Theme.DARK)
        theme_card.checkedChanged.connect(self.on_theme_change)
        layout.addWidget(theme_card)

        json_mode_card = SwitchSettingCard(FluentIcon.CODE, "强制json输出", "兼容JsonMode的模型可提高准确性，推荐开启。若剧情生成失败可关闭，本地LLM请关闭。")
        json_mode_card.setChecked(settings_config.get('json_mode', True))
        json_mode_card.checkedChanged.connect(self.json_mode)
        layout.addWidget(json_mode_card)


        doc_card = HyperlinkCard("https://tamikip.github.io/AI-GAL-doc", "查看", FluentIcon.QUICK_NOTE, "使用文档", "不会使用？来看！")
        layout.addWidget(doc_card)

        about_card = PrimaryPushSettingCard("检查更新", FluentIcon.INFO, "关于", "© 版权所有2025，TamikiP. 当前版本1.6")
        about_card.clicked.connect(self.on_check_update_clicked)
        layout.addWidget(about_card)

        layout.addStretch(1)
        return page

    def create_downloads_page(self, title):
        page = QWidget()
        page.setObjectName("downloads_page")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        title_label = TitleLabel(title, page)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title_label)

        cards_data = [
            ("https://pan.quark.cn/s/2c832199b09b", "AI绘画整合包", "下载AI绘画整合包", FluentIcon.PALETTE),
            ("https://tusiart.com/", "吐司AI", "AI绘画模型资源，云端模型也可以在这里看模型id", FluentIcon.CLOUD),
            ("https://www.123pan.com/s/5tIqVv-GVRcv.html", "GPT-SOVITS整合包", "下载GPT-SOVITS整合包", FluentIcon.MICROPHONE),
            ("https://www.ai-hobbyist.com/forum-138-1.html", "GPT-SOVITS模型资源", "各种各样的模型资源", FluentIcon.CLOUD)
        ]

        for url, card_title, content, icon in cards_data:
            card = HyperlinkCard(url, "下载", icon, card_title, content)
            layout.addWidget(card)

        return page

    def on_theme_change(self, index):
        if index:
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        InfoBar.success(
            title="主题已切换",
            content="",
            position=InfoBarPosition.TOP_RIGHT,
            parent=self
        )

    def on_auto_update_toggle(self, checked):
        self.save_config("Settings", "auto_update", checked)
        status = "启用" if checked else "禁用"
        InfoBar.info("自动更新", f"自动更新已{status}", position=InfoBarPosition.TOP_RIGHT, parent=self)

    def json_mode(self, checked):
        self.save_config("Settings", "json_mode", checked)
        status = "启用" if checked else "禁用"
        InfoBar.info("JSON模式", f"JSON模式已{status}", position=InfoBarPosition.TOP_RIGHT, parent=self)

    def on_check_update_clicked(self):
        if updater():
            InfoBar.success("检查更新", "当前已经是最新版本！", position=InfoBarPosition.TOP_RIGHT, parent=self)


class Worker(QThread):
    finished = pyqtSignal()
    def run(self):
        update.update_program()
        self.finished.emit()


class CustomMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('更新中,请勿退出', self)
        self.bar = IndeterminateProgressBar(self, start=True)
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
            update_docx = requests.get("https://github.moeyy.xyz/https://raw.githubusercontent.com/tamikip/AI-GAL/main/update_docx.txt").text
            w = Dialog(f"AI GAL可以更新到{latest_version}版本！", update_docx)
            w.yesButton.setText("更新")
            w.cancelButton.setText("稍后")
            if w.exec():
                showMessage(window)
        else:
            return True
    except:
        window.error_tips("检查更新失败！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    setTheme(Theme.DARK)
    window.show()
    if auto_update:
        updater()
    sys.exit(app.exec_())