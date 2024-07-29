import configparser
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QStackedWidget, QTabWidget, QScrollArea, QToolBar,
    QAction, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont
from qt_material import apply_stylesheet
import os
import translate
import update
import shutil
import json
import requests


def copy_folder(src_folder, dest_folder):
    try:
        if os.path.exists(dest_folder):
            shutil.rmtree(dest_folder)
        shutil.copytree(src_folder, dest_folder)
        print(f"文件夹 '{src_folder}' 成功复制到 '{dest_folder}'")
    except Exception as e:
        print(f"复制文件夹失败: {e}")


def copy_file(src_file, dest_file):
    try:
        dest_dir = os.path.dirname(dest_file)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy(src_file, dest_file)
        print(f"文件 '{src_file}' 成功复制到 '{dest_file}'")
    except Exception as e:
        print(f"复制文件失败: {e}")


class ToggleSwitch(QPushButton):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumSize(50, 25)
        self.setMaximumSize(50, 25)
        self.updateStyle()
        self.clicked.connect(self.updateStyle)

    def updateStyle(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    border-radius: 12px;
                }
                QPushButton::before {
                    content: '';
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: white;
                    position: absolute;
                    margin-left: 25px;
                    margin-top: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #CCCCCC;
                    border-radius: 12px;
                }
                QPushButton::before {
                    content: '';
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: white;
                    position: absolute;
                    margin-left: 2px;
                    margin-top: 2px;
                }
            """)
        self.toggled.emit(self.isChecked())


class ConfigTab(QWidget):
    def __init__(self, tab_name, fields, checkbox_fields, config=None):
        super().__init__()
        self.tab_name = tab_name
        self.fields = fields
        self.checkbox_fields = checkbox_fields
        self.config = config
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.inputs = {}

        for field_name in self.fields:
            input_layout = QVBoxLayout()
            if field_name in self.checkbox_fields:
                label = QLabel(f"{field_name}:")
                toggle_switch = ToggleSwitch()
                toggle_switch.setObjectName(field_name)
                input_layout.addWidget(label)
                input_layout.addWidget(toggle_switch)
                self.inputs[field_name] = toggle_switch
                toggle_switch.toggled.connect(self.updateFields)

                # Initialize toggle switch state from configuration
                if self.config and self.config.has_option(self.tab_name, field_name):
                    toggle_switch.setChecked(self.config.getboolean(self.tab_name, field_name))
            else:
                label = QLabel(f"{field_name}:")
                input_edit = QLineEdit()
                input_edit.setObjectName(field_name)
                input_layout.addWidget(label)
                input_layout.addWidget(input_edit)
                self.inputs[field_name] = input_edit

                # Initialize text field from configuration
                if self.config and self.config.has_option(self.tab_name, field_name):
                    input_edit.setText(self.config.get(self.tab_name, field_name))

            layout.addLayout(input_layout)
            layout.addSpacing(10)

        layout.addStretch()
        self.setLayout(layout)

    def updateFields(self, checked):
        if self.tab_name == "SOVITS":
            self.inputs["语音key"].setEnabled(checked)
            for field in ["gpt_model_path", "sovits_model_path", "sovits_url1", "sovits_url2", "sovits_url3",
                          "sovits_url4", "sovits_url5", "sovits_url6"]:
                self.inputs[field].setEnabled(not checked)
        elif self.tab_name == "AI绘画":
            self.inputs["绘画key"].setEnabled(checked)
            self.inputs["人物绘画模型ID(本地模式不填)"].setEnabled(checked)
            self.inputs["背景绘画模型ID(本地模式不填)"].setEnabled(checked)


class ConfigPage(QWidget):
    def __init__(self, title, tabs, checkbox_fields, show_buttons=False, config=None, extra_buttons=None):
        super().__init__()
        self.tabs = tabs
        self.checkbox_fields = checkbox_fields
        self.config = config
        self.extra_buttons = extra_buttons
        self.initUI(title, tabs, checkbox_fields, show_buttons)

    def initUI(self, title, tabs, checkbox_fields, show_buttons):
        main_layout = QVBoxLayout()
        titleLabel = QLabel(title)
        titleLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(titleLabel)
        self.tab_widget = QTabWidget()
        self.tab_contents = {}
        for tab_name, fields in tabs.items():
            tab_content = ConfigTab(tab_name, fields, checkbox_fields.get(tab_name, []), self.config)
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(tab_content)
            self.tab_widget.addTab(scroll_area, tab_name)
            self.tab_contents[tab_name] = tab_content

        main_layout.addWidget(self.tab_widget)

        if show_buttons or self.extra_buttons:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            if show_buttons:
                save_button = QPushButton("保存")
                start_game_button = QPushButton("开始游戏")
                button_layout.addWidget(save_button)
                button_layout.addWidget(start_game_button)
                save_button.clicked.connect(self.saveConfig)
                start_game_button.clicked.connect(self.startGame)
            if self.extra_buttons:
                for button in self.extra_buttons:
                    button_layout.addWidget(button)
            main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def saveConfig(self):
        config = configparser.ConfigParser()
        for tab_name, tab_content in self.tab_contents.items():
            config[tab_name] = {}
            for field_name, widget in tab_content.inputs.items():
                if isinstance(widget, QLineEdit):
                    config[tab_name][field_name] = widget.text()
                elif isinstance(widget, ToggleSwitch):
                    config[tab_name][field_name] = str(widget.isChecked())

        with open('game/config.ini', 'w', encoding="utf-8") as configfile:
            config.write(configfile)

        self.showSuccessMessage()

    def showSuccessMessage(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("保存成功")
        msg_box.setText("配置已成功保存!")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.show()
        QTimer.singleShot(3000, msg_box.close)

    def startGame(self):
        exe_path = "AI GAL.exe"
        try:
            subprocess.Popen(exe_path)
            QApplication.quit()
        except Exception as e:
            print(f"无法启动游戏: {e}")


class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("配置界面")
        self.setGeometry(100, 100, 1000, 600)
        self.setFixedSize(1000, 600)
        self.config = self.loadConfig()
        self.initUI()

    def loadConfig(self):
        config = configparser.ConfigParser()
        config.read('game/config.ini', encoding='utf-8')
        return config

    def initUI(self):
        main_layout = QHBoxLayout()
        self.toolbar = QToolBar("导航栏")
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setMovable(False)
        self.toolbar.setFixedWidth(150)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.basic_action = QAction("基础配置", self)
        self.advanced_action = QAction("高级配置", self)
        self.new_action = QAction("构建分发版", self)

        self.toolbar.addAction(self.basic_action)
        self.toolbar.addAction(self.advanced_action)
        self.toolbar.addAction(self.new_action)

        self.toolbar.setStyleSheet("QToolBar { border: none; }")
        self.stack_widget = QStackedWidget()

        basic_tabs = {
            "CHATGPT": ["GPT_KEY", "BASE_URL", "model"],
            "SOVITS": ["云端模式", "语音key", "gpt_model_path", "sovits_model_path", "sovits_url1", "sovits_url2",
                       "sovits_url3", "sovits_url4", "sovits_url5", "sovits_url6"],
            "AI绘画": ["云端模式", "绘画key", "人物绘画模型ID(本地模式不填)", "背景绘画模型ID(本地模式不填)"],
            "剧情": ["剧本的主题"],
            "音乐": ["音乐生成", "BASE_URL", "KEY"]
        }

        checkbox_fields = {
            "CHATGPT": [],
            "SOVITS": ["云端模式"],
            "AI绘画": ["云端模式"],
            "音乐": ["音乐生成"]
        }

        self.basic_page = ConfigPage("基础配置", basic_tabs, checkbox_fields, show_buttons=True, config=self.config)
        self.advanced_page = ConfigPage("高级配置", {"高级配置": []}, {}, config=self.config)

        self.stack_widget.addWidget(self.basic_page)
        self.stack_widget.addWidget(self.advanced_page)

        distribute_tabs = {
            "分发版": ["输入分发版的名字"]
        }

        build_button = QPushButton("构建分发版")
        build_button.clicked.connect(self.handleBuildDistribution)

        self.distribute_page = ConfigPage("分发版", distribute_tabs, {}, config=self.config,
                                          extra_buttons=[build_button])
        self.stack_widget.addWidget(self.distribute_page)

        main_layout.addWidget(self.stack_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.basic_action.triggered.connect(lambda: self.stack_widget.setCurrentIndex(0))
        self.advanced_action.triggered.connect(lambda: self.stack_widget.setCurrentIndex(1))
        self.new_action.triggered.connect(lambda: self.stack_widget.setCurrentIndex(2))

        self.switchToBasic()

    def switchToBasic(self):
        self.stack_widget.setCurrentIndex(0)

    def shownewSuccessMessage(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("保存构建成功")
        msg_box.setText("分发版已成功构建!")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.show()
        QTimer.singleShot(3000, msg_box.close)

    def handleBuildDistribution(self):
        current_index = self.stack_widget.currentIndex()
        current_page = self.stack_widget.widget(current_index)
        distribute_tab = current_page.tab_contents.get("分发版")
        distribution_name_widget = distribute_tab.inputs.get("输入分发版的名字")
        if distribution_name_widget:
            distribution_name = distribution_name_widget.text()
        else:
            distribution_name = "分发版"
        os.makedirs(distribution_name)
        copy_folder("game", f"{distribution_name}/game")
        copy_folder("lib", f"{distribution_name}/lib")
        copy_folder("renpy", f"{distribution_name}/renpy")
        copy_file("AI GAL.exe", f"{distribution_name}/AI GAL.exe")
        copy_file("AI GAL.py", f"{distribution_name}/AI GAL.py")

        with open(f"{distribution_name}/game/dialogues.json", "r", encoding="UTF-8") as file:
            input_data = json.load(file)
        custom_content = translate.translate_to_renpy_string(input_data)

        with open(f"{distribution_name}/game/script.rpy", 'r', encoding='utf-8') as file:
            lines = file.readlines()
        indentation = "    "
        indented_text = '\n'.join(map(lambda x: indentation + x, custom_content.splitlines()))

        start_line = 65
        end_line = 125
        del lines[start_line:end_line + 1]
        lines.insert(start_line, indented_text + '\n')
        with open(f"{distribution_name}/game/script.rpy", 'w', encoding='utf-8') as file:
            file.writelines(lines)

        self.shownewSuccessMessage()


class UpdateDialog(QMessageBox):
    def __init__(self, parent=None):
        super(UpdateDialog, self).__init__(parent)
        update_docx = requests.get(
            "https://github.moeyy.xyz/https://raw.githubusercontent.com/tamikip/AI-GAL/main/update_docx.txt").text
        self.setWindowTitle("新更新!")
        self.setText(f"有新的更新！新版本{latest_version}!\n{update_docx}")
        self.setIcon(QMessageBox.Information)
        self.setGeometry(500, 300, 0, 0)

        # 添加自定义按钮
        self.later_button = self.addButton("稍后更新", QMessageBox.RejectRole)
        self.now_button = self.addButton("立刻更新", QMessageBox.AcceptRole)

        # 连接按钮的点击信号到槽函数
        self.later_button.clicked.connect(self.handleLater)
        self.now_button.clicked.connect(self.handleNow)

    def handleLater(self):
        pass

    def handleNow(self):
        update.update_program()
        with open("version.txt", "w") as file:
            file.write(update.get_latest_release()["tag_name"])
        QMessageBox.information(None, "更新成功", "更新成功！")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    window = UserInterface()
    window.show()

    with open("version.txt", "r") as file:
        version = file.read()
    try:
        latest_version = update.get_latest_release()["tag_name"]
        if not latest_version == version:
            dialog = UpdateDialog()
            dialog.show()
    except:
        pass

    sys.exit(app.exec_())
