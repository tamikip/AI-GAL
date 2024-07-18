import configparser
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QStackedWidget, QTabWidget, QScrollArea, QToolBar,
    QAction, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from qt_material import apply_stylesheet


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
                          "sovits_url4", "sovits_url5", "sovits_url6"]:  # Added sovits_url6 here
                self.inputs[field].setEnabled(not checked)
        elif self.tab_name == "AI绘画":
            self.inputs["绘画key"].setEnabled(checked)
            self.inputs["人物绘画模型ID(本地模式不填)"].setEnabled(checked)  # Moved from advanced configuration
            self.inputs["背景绘画模型ID(本地模式不填)"].setEnabled(checked)  # Moved from advanced configuration


class ConfigPage(QWidget):
    def __init__(self, title, tabs, checkbox_fields, show_buttons=False, config=None):
        super().__init__()
        self.tabs = tabs
        self.checkbox_fields = checkbox_fields
        self.config = config  # Receive incoming configuration object
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

        if show_buttons:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            save_button = QPushButton("保存")
            start_game_button = QPushButton("开始游戏")
            button_layout.addWidget(save_button)
            button_layout.addWidget(start_game_button)
            main_layout.addLayout(button_layout)

            save_button.clicked.connect(self.saveConfig)
            start_game_button.clicked.connect(self.startGame)

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
        self.config = self.loadConfig()  # Load configuration file
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
        self.toolbar.addAction(self.basic_action)
        self.toolbar.addAction(self.advanced_action)
        self.toolbar.setStyleSheet("QToolBar { border: none; }")
        self.stack_widget = QStackedWidget()

        basic_tabs = {
            "CHATGPT": ["GPT_KEY", "BASE_URL", "model"],
            "SOVITS": ["云端模式", "语音key", "gpt_model_path", "sovits_model_path", "sovits_url1", "sovits_url2",
                       "sovits_url3", "sovits_url4", "sovits_url5", "sovits_url6"],  # Added sovits_url6 here
            "AI绘画": ["云端模式", "绘画key", "人物绘画模型ID(本地模式不填)", "背景绘画模型ID(本地模式不填)"],
            # Moved from advanced configuration
            "剧情": ["剧本的主题"]
        }

        checkbox_fields = {
            "CHATGPT": [],
            "SOVITS": ["云端模式"],
            "AI绘画": ["云端模式"],
            "剧情": []
        }

        self.basic_page = ConfigPage("基础配置", basic_tabs, checkbox_fields, show_buttons=True, config=self.config)
        self.advanced_page = ConfigPage("高级配置", {"高级配置": []}, {}, config=self.config)  # Empty advanced_fields

        self.stack_widget.addWidget(self.basic_page)
        self.stack_widget.addWidget(self.advanced_page)

        main_layout.addWidget(self.stack_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.basic_action.triggered.connect(lambda: self.stack_widget.setCurrentIndex(0))
        self.advanced_action.triggered.connect(lambda: self.stack_widget.setCurrentIndex(1))

        self.switchToBasic()

    def switchToBasic(self):
        self.stack_widget.setCurrentIndex(0)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')  # Assuming you have a custom stylesheet
    window = UserInterface()
    window.show()
    sys.exit(app.exec_())


