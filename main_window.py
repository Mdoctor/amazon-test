import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QGridLayout,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from config import load_pickle, dump_pickle, conf_pkl
from logger import logger
from main import main as runner
from threading import Thread


class WorkerThread(QThread):
    finished = Signal(bool)  # 添加执行结果参数

    def __init__(self, search_terms, parent=None):
        super().__init__(parent)
        self.search_terms = search_terms

    def run(self):
        try:
            runner(search_terms=self.search_terms)
            self.finished.emit(True)
        except Exception as e:
            print(f"执行出错: {str(e)}")
            self.finished.emit(False)


class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.setWindowTitle("Amazon采集器 v1.0")
        self.init_ui()
        self.load_config()
        self.setup_controls_list()

    def setup_controls_list(self):
        """收集所有需要禁用的控件"""
        self.controls = [
            self.search_input,
            self.max_products,
            self.max_workers,
            self.chunk_size,
            self.wait_time,
            self.min_sleep,
            self.max_sleep,
            self.scroll_steps,
            self.headless,
            self.vpn_enabled,
            self.vpn_name,
            self.vpn_username,
            self.vpn_password,
        ]

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
        search_layout.addWidget(self.search_input)

        # 日志区域
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(300)
        log_layout.addWidget(self.log_area)

        # 配置区域（三列网格布局）
        config_group = QGroupBox("配置参数")
        config_layout = QGridLayout(config_group)
        config_layout.setHorizontalSpacing(30)  # 列间距
        config_layout.setVerticalSpacing(15)  # 行间距

        # ========== 第一列 ==========
        col = 0
        row = 0
        # 爬虫参数
        config_layout.addWidget(QLabel("最大产品数/分类:"), row, col)
        self.max_products = self.create_spinbox(10, 1, 100)
        config_layout.addWidget(self.max_products, row, col + 1)

        row += 1
        config_layout.addWidget(QLabel("最大工作线程:"), row, col)
        self.max_workers = self.create_spinbox(4, 1, 16)
        config_layout.addWidget(self.max_workers, row, col + 1)

        row += 1
        config_layout.addWidget(QLabel("数据块大小:"), row, col)
        self.chunk_size = self.create_spinbox(10, 1, 100)
        config_layout.addWidget(self.chunk_size, row, col + 1)

        row += 1
        config_layout.addWidget(QLabel("VPN名称:"), row, col)
        self.vpn_name = QLineEdit()
        config_layout.addWidget(self.vpn_name, row, col + 1)

        # ========== 第二列 ==========
        col = 2  # 跳过中间的空列作为分隔
        row = 0
        # 时间参数
        config_layout.addWidget(QLabel("等待时间(秒):"), row, col)
        self.wait_time = self.create_spinbox(10, 1, 60)
        config_layout.addWidget(self.wait_time, row, col + 1)

        row += 1
        config_layout.addWidget(QLabel("最小间隔(秒):"), row, col)
        self.min_sleep = self.create_spinbox(1, 1, 10)
        config_layout.addWidget(self.min_sleep, row, col + 1)

        row += 1
        config_layout.addWidget(QLabel("最大间隔(秒):"), row, col)
        self.max_sleep = self.create_spinbox(2, 1, 10)
        config_layout.addWidget(self.max_sleep, row, col + 1)

        row += 1
        config_layout.addWidget(QLabel("VPN用户名:"), row, col)
        self.vpn_username = QLineEdit()
        config_layout.addWidget(self.vpn_username, row, col + 1)

        # ========== 第三列 ==========
        col = 4  # 继续向右跳过空列
        row = 0
        # 浏览器参数
        config_layout.addWidget(QLabel("滚动步骤:"), row, col)
        self.scroll_steps = self.create_spinbox(3, 1, 10)
        config_layout.addWidget(self.scroll_steps, row, col + 1)

        row += 1
        self.headless = QCheckBox("无界面模式")
        config_layout.addWidget(self.headless, row, col, 1, 2)

        row += 1
        self.vpn_enabled = QCheckBox("启用 VPN")
        config_layout.addWidget(self.vpn_enabled, row, col, 1, 2)

        row += 1
        config_layout.addWidget(QLabel("VPN密码:"), row, col)
        self.vpn_password = QLineEdit()
        self.vpn_password.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.vpn_password, row, col + 1)

        # 操作按钮
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        self.start_btn = QPushButton("启动")
        self.exit_btn = QPushButton("退出")
        self.start_btn.setFixedSize(150, 45)
        self.exit_btn.setFixedSize(150, 45)
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

    def create_spinbox(self, default, min_val, max_val):
        """创建统一风格的SpinBox"""
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(default)
        spinbox.setFixedWidth(120)
        return spinbox

    def set_style(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2D2D2D;
            }
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #CCCCCC;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 8px;
                font-family: Consolas;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2D2D2D;
            }
            QLineEdit, QSpinBox {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: #AAAAAA;
            }
            QCheckBox {
                color: #CCCCCC;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """
        )
        self.setMinimumSize(1200, 800)
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.setFont(font)

    def toggle_vpn_fields(self):
        enabled = self.vpn_enabled.isChecked()
        self.vpn_name.setEnabled(enabled)
        self.vpn_username.setEnabled(enabled)
        self.vpn_password.setEnabled(enabled)
        if not enabled:
            self.vpn_name.setText("")
            self.vpn_username.setText("")
            self.vpn_password.setText("")

    def load_config(self):
        try:
            config = load_pickle(conf_pkl)
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

    def check_config(self):
        if self.max_sleep.value() <= self.min_sleep.value():
            return False
        else:
            return True

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
            "vpn_password": self.vpn_password.text(),
        }
        dump_pickle(conf_pkl, config)
        return config

    def log(self, message):
        self.log_area.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        )
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )

    def toggle_ui_state(self, enabled):
        """切换界面控件的可用状态"""
        for control in self.controls:
            control.setEnabled(enabled)
        self.start_btn.setEnabled(enabled)
        self.start_btn.setText("🚀 启动" if enabled else "🔄 运行中...")

    def start_process(self):
        if not self.check_config():
            self.log("间隔时间范围配置错误,请重新配置")
            return
        config = self.save_config()
        logger.info(config)
        search_input = self.search_input.text().strip()
        if not search_input:
            self.log("搜索词不能为空")
            return
        self.toggle_ui_state(False)
        self.log(f"工作线程数: {self.max_workers.value()}")
        self.log("启动处理流程...")
        search_terms = search_input.split(",")
        self.worker_thread = WorkerThread(search_terms)
        self.worker_thread.finished.connect(self.on_process_finished)
        self.worker_thread.start()

    def on_process_finished(self, success):
        """任务完成处理"""
        self.toggle_ui_state(True)
        status = "成功" if success else "失败"
        self.log(f"处理流程完成 [{status}]")
        self.worker_thread.deleteLater()
        self.worker_thread = None

    def closeEvent(self, event):
        self.save_config()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())
