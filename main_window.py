import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSpinBox, 
    QCheckBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自动化工具 v1.0")
        self.init_ui()
        self.load_config()

    def init_ui(self):
        # 主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 搜索区域
        search_group = QGroupBox("搜索设置")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索关键词...")
        search_btn = QPushButton("搜索")
        search_btn.setFixedWidth(100)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        # 日志区域
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)

        # 配置区域
        config_group = QGroupBox("配置参数")
        config_layout = QGridLayout(config_group)
        
        # 配置项
        self.headless = QCheckBox("无界面模式")
        self.max_products = QSpinBox()
        self.max_products.setRange(1, 100)
        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 16)
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(1, 100)
        self.wait_time = QSpinBox()
        self.min_sleep = QSpinBox()
        self.max_sleep = QSpinBox()
        self.scroll_steps = QSpinBox()
        self.vpn_enabled = QCheckBox("启用VPN")
        self.vpn_name = QLineEdit()
        self.vpn_username = QLineEdit()
        self.vpn_password = QLineEdit()
        self.vpn_password.setEchoMode(QLineEdit.Password)

        # 布局配置项
        row = 0
        config_layout.addWidget(QLabel("最大产品数/分类:"), row, 0)
        config_layout.addWidget(self.max_products, row, 1)
        row +=1
        config_layout.addWidget(QLabel("最大工作线程:"), row, 0)
        config_layout.addWidget(self.max_workers, row, 1)
        row +=1
        config_layout.addWidget(QLabel("数据块大小:"), row, 0)
        config_layout.addWidget(self.chunk_size, row, 1)
        row +=1
        config_layout.addWidget(QLabel("等待时间(秒):"), row, 0)
        config_layout.addWidget(self.wait_time, row, 1)
        row +=1
        config_layout.addWidget(QLabel("最小间隔(秒):"), row, 0)
        config_layout.addWidget(self.min_sleep, row, 1)
        row +=1
        config_layout.addWidget(QLabel("最大间隔(秒):"), row, 0)
        config_layout.addWidget(self.max_sleep, row, 1)
        row +=1
        config_layout.addWidget(QLabel("滚动步骤:"), row, 0)
        config_layout.addWidget(self.scroll_steps, row, 1)
        row +=1
        config_layout.addWidget(self.headless, row, 0, 1, 2)
        row +=1
        config_layout.addWidget(self.vpn_enabled, row, 0, 1, 2)
        row +=1
        config_layout.addWidget(QLabel("VPN名称:"), row, 0)
        config_layout.addWidget(self.vpn_name, row, 1)
        row +=1
        config_layout.addWidget(QLabel("VPN用户名:"), row, 0)
        config_layout.addWidget(self.vpn_username, row, 1)
        row +=1
        config_layout.addWidget(QLabel("VPN密码:"), row, 0)
        config_layout.addWidget(self.vpn_password, row, 1)

        # 操作按钮
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        self.start_btn = QPushButton("启动")
        self.exit_btn = QPushButton("退出")
        self.start_btn.setFixedSize(120, 40)
        self.exit_btn.setFixedSize(120, 40)
        btn_layout.addStretch()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.exit_btn)

        # 组合所有区域
        main_layout.addWidget(search_group)
        main_layout.addWidget(log_group)
        main_layout.addWidget(config_group)
        main_layout.addWidget(btn_group)

        # 连接信号
        self.exit_btn.clicked.connect(self.close)
        self.start_btn.clicked.connect(self.start_process)
        self.vpn_enabled.stateChanged.connect(self.toggle_vpn_fields)

        # 样式设置
        self.set_style()

    def set_style(self):
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #2E7D32;
            }
            QTextEdit {
                background-color: #F1F8E9;
                border: 1px solid #C8E6C9;
                border-radius: 3px;
                padding: 5px;
                min-height: 100px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #C8E6C9;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        self.setMinimumSize(800, 800)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

    def toggle_vpn_fields(self):
        enabled = self.vpn_enabled.isChecked()
        self.vpn_name.setEnabled(enabled)
        self.vpn_username.setEnabled(enabled)
        self.vpn_password.setEnabled(enabled)

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.headless.setChecked(config["headless"])
                self.max_products.setValue(config["max_products_per_category"])
                self.max_workers.setValue(config["max_workers"])
                self.chunk_size.setValue(config["chunk_size"])
                self.wait_time.setValue(config["wait_time"])
                self.min_sleep.setValue(config["min_sleep"])
                self.max_sleep.setValue(config["max_sleep"])
                self.scroll_steps.setValue(config["scroll_steps"])
                self.vpn_enabled.setChecked(config["vpn_enabled"])
                self.vpn_name.setText(config["vpn_name"])
                self.vpn_username.setText(config["vpn_username"])
                self.vpn_password.setText(config["vpn_password"])
                self.toggle_vpn_fields()
        except FileNotFoundError:
            self.log("未找到配置文件，使用默认设置")

    def save_config(self):
        config = {
            "headless": self.headless.isChecked(),
            "max_products_per_category": self.max_products.value(),
            "max_workers": self.max_workers.value(),
            "chunk_size": self.chunk_size.value(),
            "wait_time": self.wait_time.value(),
            "min_sleep": self.min_sleep.value(),
            "max_sleep": self.max_sleep.value(),
            "scroll_steps": self.scroll_steps.value(),
            "vpn_enabled": self.vpn_enabled.isChecked(),
            "vpn_name": self.vpn_name.text(),
            "vpn_username": self.vpn_username.text(),
            "vpn_password": self.vpn_password.text()
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    def log(self, message):
        self.log_area.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    def start_process(self):
        self.log("启动处理流程...")
        # 这里添加实际业务逻辑
        self.log("配置参数加载成功")
        self.log(f"工作线程数: {self.max_workers.value()}")

    def closeEvent(self, event):
        self.save_config()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())