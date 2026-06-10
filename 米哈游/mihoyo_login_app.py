import sys
import json
import csv
import time
import uuid
import base64
from datetime import datetime, timedelta
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import requests

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QStatusBar,
    QDateEdit,
    QGroupBox,
    QGridLayout,
    QFrame,
    QSplitter,
    QAbstractItemView,
    QCheckBox,
    QSizePolicy,
    QSpacerItem,
)
from PySide6.QtCore import Qt, QDate, QThread, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QColor, QBrush, QAction

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDvekdPMHN3AYhm/vktJT+YJr7
cI5DcsNKqdsx5DZX0gDuWFuIjzdwButrIYPNmRJ1G8ybDIF7oDW2eEpm5sMbL9zs
9ExXCdvqrn51qELbqj0XxtMTIpaCHFSI50PfPpTFV9Xt/hmyVwokoOXFlAEgCn+Q
CgGs52bFoYMtyi+xEQIDAQAB
-----END PUBLIC KEY-----"""

key = RSA.import_key(PUBLIC_KEY_PEM)
rsa_cipher = PKCS1_v1_5.new(key)

ACTION_LABELS = {
    1: "登录",
    7: "登出",
    100: "修改密码",
    101: "修改邮箱",
    102: "绑定手机",
    103: "解绑手机",
    104: "绑定邮箱",
    105: "解绑邮箱",
    201: "实名认证",
    202: "实名信息修改",
    401: "冻结账号",
    402: "解冻账号",
    501: "第三方绑定",
    502: "第三方解绑",
}

STYLE_SHEET = """
QMainWindow {
    background-color: #0f0f1a;
}
QWidget {
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    color: #e0e0e0;
    font-size: 13px;
}
QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    padding: 0px;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #8888aa;
    padding: 0px;
}
QLabel#sectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #ccccff;
    padding: 0px 0px 8px 0px;
}
QLabel#statusIcon {
    font-size: 13px;
    color: #8888aa;
}
QGroupBox {
    background-color: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    margin-top: 0px;
    padding: 20px 24px 24px 24px;
    font-size: 13px;
    font-weight: 600;
    color: #aaaacc;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0px 0px 0px 0px;
    color: #8888bb;
}
QLineEdit {
    background-color: #16162b;
    border: 1px solid #2a2a50;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #e0e0e0;
    selection-background-color: #4466cc;
}
QLineEdit:focus {
    border: 1px solid #5577ee;
    background-color: #1a1a30;
}
QLineEdit::placeholder {
    color: #555577;
}
QPushButton#loginBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4466ee, stop:1 #6644ee);
    border: none;
    border-radius: 10px;
    padding: 12px 32px;
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    min-height: 20px;
}
QPushButton#loginBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5577ff, stop:1 #7755ff);
}
QPushButton#loginBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3355dd, stop:1 #5533dd);
}
QPushButton#loginBtn:disabled {
    background: #2a2a4a;
    color: #555577;
}
QPushButton#logoutBtn {
    background: transparent;
    border: 1px solid #3a3a5a;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
    color: #9999bb;
}
QPushButton#logoutBtn:hover {
    background: #2a1a1a;
    border: 1px solid #664444;
    color: #ff8888;
}
QPushButton {
    background-color: #222244;
    border: 1px solid #333366;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
    color: #ccccff;
}
QPushButton:hover {
    background-color: #2a2a55;
    border: 1px solid #4455cc;
}
QPushButton:pressed {
    background-color: #1a1a44;
}
QPushButton:disabled {
    background-color: #1a1a28;
    color: #444466;
    border: 1px solid #252540;
}
QPushButton#dangerBtn {
    background: transparent;
    border: 1px solid #553333;
    color: #cc6666;
}
QPushButton#dangerBtn:hover {
    background: #2a1818;
}
QTableWidget {
    background-color: #141428;
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    gridline-color: #1e1e3a;
    outline: none;
}
QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1a1a35;
    color: #d0d0e0;
}
QTableWidget::item:selected {
    background-color: #2a2a5a;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #1a1a35;
    border: none;
    border-bottom: 1px solid #2a2a55;
    border-right: 1px solid #1a1a35;
    padding: 10px 12px;
    font-weight: 700;
    font-size: 12px;
    color: #9999cc;
}
QHeaderView::section:hover {
    background-color: #222248;
    color: #bbbbee;
}
QScrollBar:vertical {
    background: #12122a;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #333366;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #4455aa;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QDateEdit {
    background-color: #16162b;
    border: 1px solid #2a2a50;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #e0e0e0;
}
QDateEdit:focus {
    border: 1px solid #5577ee;
}
QDateEdit::drop-down {
    border: none;
    background: transparent;
}
QDateEdit::down-arrow {
    image: none;
    border: none;
}
QStatusBar {
    background-color: #0a0a18;
    border-top: 1px solid #1a1a35;
    color: #6666aa;
    font-size: 12px;
    padding: 4px 12px;
}
QStatusBar::item {
    border: none;
}
QFrame#headerWidget {
    background-color: #0f0f1a;
    border-bottom: 1px solid #1a1a35;
    padding: 0px;
}
QFrame#card {
    background-color: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
}
"""


def rsa_encrypt(text):
    return base64.b64encode(rsa_cipher.encrypt(text.encode("utf-8"))).decode("utf-8")


class LoginWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, account, password):
        super().__init__()
        self.account = account
        self.password = password

    def run(self):
        try:
            device_id = str(uuid.uuid4())
            lifecycle_id = hex(int(time.time() * 1000))[2:12]
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Content-Type": "application/json",
                "Origin": "https://user.mihoyo.com",
                "Referer": "https://user.mihoyo.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "x-rpc-app_id": "dw9y09jqjpxc",
                "x-rpc-client_type": "4",
                "x-rpc-device_fp": "38d818f8368c1",
                "x-rpc-device_id": device_id,
                "x-rpc-device_model": "Chrome%20148.0.0.0",
                "x-rpc-device_name": "Chrome",
                "x-rpc-device_os": "Windows%2010%2064-bit",
                "x-rpc-game_biz": "plat_cn",
                "x-rpc-lifecycle_id": lifecycle_id,
                "x-rpc-mi_referrer": "https://user.mihoyo.com/login-platform/index.html?app_id=dw9y09jqjpxc&theme=passport&token_type=4&game_biz=plat_cn&message_origin=https%253A%252F%252Fuser.mihoyo.com&succ_back_type=message%253Alogin-platform%253Alogin-success&fail_back_type=message%253Alogin-platform%253Alogin-fail&ux_mode=popup&iframe_level=1#/login/password",
                "x-rpc-sdk_version": "2.52.0",
                "x-rpc-source": "v2.webLogin",
            }
            cookies = {
                "_MHYUUID": device_id,
                "DEVICEFP_SEED_ID": "6bc4e8b35944de4b",
                "DEVICEFP_SEED_TIME": str(int(time.time() * 1000)),
                "DEVICEFP": "38d818f8368c1",
                "MIHOYO_LOGIN_PLATFORM_LIFECYCLE_ID": lifecycle_id,
            }
            s = requests.Session()
            s.cookies.update(cookies)
            s.headers.update(headers)

            resp = s.post(
                "https://passport-api.mihoyo.com/account/ma-cn-passport/web/loginByPassword",
                json={
                    "account": rsa_encrypt(self.account),
                    "password": rsa_encrypt(self.password),
                },
            )
            result = resp.json()
            if result.get("retcode") == 0:
                self.finished.emit(s)
            else:
                self.error.emit(f"登录失败: {result.get('message', str(result))}")
        except Exception as e:
            self.error.emit(f"网络错误: {str(e)}")


class FetchLogsWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, session, start_time, end_time):
        super().__init__()
        self.session = session
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        try:
            resp = self.session.get(
                "https://passport-api.mihoyo.com/account/ma-cn-passport/passport/getActionLogs",
                params={"start_time": self.start_time, "end_time": self.end_time},
                timeout=15,
            )
            result = resp.json()
            if result.get("retcode") != 0:
                self.error.emit(f"获取日志失败: {result.get('message', str(result))}")
            else:
                self.finished.emit(result["data"]["logs"])
        except Exception as e:
            self.error.emit(f"网络错误: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = None
        self.logs_data = []
        self.setWindowTitle("米哈游通行证 - 活动日志管理")
        self.setMinimumSize(1100, 720)
        self.resize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Header ===
        header = QFrame()
        header.setObjectName("headerWidget")
        header.setFixedHeight(80)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(32, 0, 32, 0)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("米哈游通行证")
        title.setObjectName("titleLabel")
        subtitle = QLabel("账号活动日志管理工具")
        subtitle.setObjectName("subtitleLabel")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        h_layout.addLayout(title_col)
        h_layout.addStretch()

        self.status_icon = QLabel("● 未登录")
        self.status_icon.setObjectName("statusIcon")
        self.status_icon.setStyleSheet(
            "color: #cc4444; font-size: 13px; font-weight: 600;"
        )
        h_layout.addWidget(self.status_icon)

        main_layout.addWidget(header)

        # === Content ===
        content = QWidget()
        content.setContentsMargins(32, 24, 32, 24)
        c_layout = QVBoxLayout(content)
        c_layout.setSpacing(20)

        # --- Login Card ---
        login_card = QGroupBox("  账号登录")
        login_card.setObjectName("card")
        login_grid = QGridLayout(login_card)
        login_grid.setContentsMargins(0, 16, 0, 0)
        login_grid.setSpacing(12)

        login_grid.addWidget(QLabel("手机号 / 邮箱"), 0, 0)
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("请输入米哈游通行证账号")
        self.account_input.setText("15322349311")
        login_grid.addWidget(self.account_input, 0, 1)

        login_grid.addWidget(QLabel("密码"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("943576081zdkZDK")
        login_grid.addWidget(self.password_input, 1, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.login_btn = QPushButton(" 登录")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.do_login)
        self.login_btn.setFixedWidth(140)
        btn_row.addWidget(self.login_btn)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.do_logout)
        self.logout_btn.setVisible(False)
        btn_row.addWidget(self.logout_btn)

        btn_row.addStretch()

        self.login_status_label = QLabel("")
        self.login_status_label.setStyleSheet("color: #8888aa; font-size: 12px;")
        btn_row.addWidget(self.login_status_label)

        login_grid.addLayout(btn_row, 2, 0, 1, 2)

        c_layout.addWidget(login_card)

        # --- Logs Section ---
        logs_section = QVBoxLayout()
        logs_section.setSpacing(12)

        section_header = QHBoxLayout()
        section_header.setSpacing(16)

        section_label = QLabel("活动日志")
        section_label.setObjectName("sectionLabel")
        section_header.addWidget(section_label)
        section_header.addStretch()

        section_header.addWidget(QLabel("开始日期:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setFixedWidth(150)
        section_header.addWidget(self.start_date)

        section_header.addWidget(QLabel("结束日期:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedWidth(150)
        section_header.addWidget(self.end_date)

        self.fetch_btn = QPushButton(" 获取日志")
        self.fetch_btn.setCursor(Qt.PointingHandCursor)
        self.fetch_btn.clicked.connect(self.do_fetch)
        self.fetch_btn.setEnabled(False)
        section_header.addWidget(self.fetch_btn)

        self.export_btn = QPushButton(" 导出 CSV")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.clicked.connect(self.do_export)
        self.export_btn.setEnabled(False)
        section_header.addWidget(self.export_btn)

        logs_section.addLayout(section_header)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["操作类型", "操作", "平台", "设备", "地点", "IP", "时间"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #161630;")
        self.table.setMinimumHeight(280)

        logs_section.addWidget(self.table)
        c_layout.addLayout(logs_section)

        main_layout.addWidget(content)

        # === Status Bar ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label, 1)

    def do_login(self):
        account = self.account_input.text().strip()
        password = self.password_input.text().strip()
        if not account or not password:
            QMessageBox.warning(self, "提示", "请输入账号和密码")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")
        self.login_status_label.setText("正在登录...")
        self.login_status_label.setStyleSheet("color: #ccaaff; font-size: 12px;")
        self.status_label.setText("正在登录...")

        self.worker = LoginWorker(account, password)
        self.worker.finished.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        self.worker.start()

    def on_login_success(self, session):
        self.session = session
        self.login_btn.setEnabled(True)
        self.login_btn.setText(" 登录")
        self.login_btn.setVisible(False)
        self.logout_btn.setVisible(True)
        self.fetch_btn.setEnabled(True)
        self.login_status_label.setText("✓ 已登录")
        self.login_status_label.setStyleSheet(
            "color: #44cc88; font-size: 12px; font-weight: 600;"
        )
        self.status_icon.setText("● 已登录")
        self.status_icon.setStyleSheet(
            "color: #44cc88; font-size: 13px; font-weight: 600;"
        )
        self.status_label.setText("登录成功 | 账号: " + self.account_input.text())
        self.account_input.setEnabled(False)
        self.password_input.setEnabled(False)

    def on_login_error(self, msg):
        self.login_btn.setEnabled(True)
        self.login_btn.setText(" 登录")
        self.login_status_label.setText("✗ " + msg)
        self.login_status_label.setStyleSheet("color: #cc4444; font-size: 12px;")
        self.status_label.setText("登录失败")
        QMessageBox.warning(self, "登录失败", msg)

    def do_logout(self):
        self.session = None
        self.logs_data = []
        self.table.setRowCount(0)
        self.login_btn.setVisible(True)
        self.logout_btn.setVisible(False)
        self.fetch_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.account_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.login_status_label.setText("")
        self.status_icon.setText("● 未登录")
        self.status_icon.setStyleSheet(
            "color: #cc4444; font-size: 13px; font-weight: 600;"
        )
        self.status_label.setText("已退出登录")

    def do_fetch(self):
        if not self.session:
            QMessageBox.warning(self, "提示", "请先登录")
            return

        qstart = self.start_date.date()
        qend = self.end_date.date()
        start_ts = int(
            datetime(qstart.year(), qstart.month(), qstart.day()).timestamp()
        )
        end_ts = int(
            datetime(qend.year(), qend.month(), qend.day(), 23, 59, 59).timestamp()
        )

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("获取中...")
        self.status_label.setText("正在获取活动日志...")

        self.worker = FetchLogsWorker(self.session, start_ts, end_ts)
        self.worker.finished.connect(self.on_fetch_success)
        self.worker.error.connect(self.on_fetch_error)
        self.worker.start()

    def on_fetch_success(self, logs):
        self.logs_data = logs
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText(" 获取日志")
        self.export_btn.setEnabled(len(logs) > 0)
        self.populate_table(logs)
        self.status_label.setText(f"获取成功 | 共 {len(logs)} 条记录")
        self.login_status_label.setText(f"✓ 已登录 | {len(logs)} 条日志")

    def on_fetch_error(self, msg):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText(" 获取日志")
        self.status_label.setText("获取失败")
        QMessageBox.warning(self, "获取失败", msg)

    def populate_table(self, logs):
        self.table.setRowCount(len(logs))
        colors = {1: "#44cc88", 402: "#66aaff", 100: "#ffaa44"}

        for row, log in enumerate(logs):
            action_code = log["action"]
            action_label = ACTION_LABELS.get(action_code, f"未知({action_code})")
            biz = log.get("biz", "")
            device_name = log.get("device_name", "")
            addr = log.get("addr", "")
            ip = log.get("ip", "")
            log_time = log.get("log_time", "0")
            time_str = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(log_time)))
                if log_time
                else ""
            )

            items = [
                QTableWidgetItem(str(action_code)),
                QTableWidgetItem(action_label),
                QTableWidgetItem(biz),
                QTableWidgetItem(device_name),
                QTableWidgetItem(addr),
                QTableWidgetItem(ip),
                QTableWidgetItem(time_str),
            ]

            color = colors.get(action_code, "#d0d0e0")
            for item in items:
                item.setForeground(QColor(color))
                if row % 2 == 0:
                    item.setBackground(QColor(0x14, 0x14, 0x28))
                else:
                    item.setBackground(QColor(0x16, 0x16, 0x30))

            self.table.setItem(row, 0, items[0])
            self.table.setItem(row, 1, items[1])
            self.table.setItem(row, 2, items[2])
            self.table.setItem(row, 3, items[3])
            self.table.setItem(row, 4, items[4])
            self.table.setItem(row, 5, items[5])
            self.table.setItem(row, 6, items[6])

        self.table.scrollToBottom()

    def do_export(self):
        if not self.logs_data:
            QMessageBox.warning(self, "提示", "没有数据可导出")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "导出 CSV",
            f"action_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV 文件 (*.csv)",
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "action_code",
                        "action_label",
                        "biz",
                        "device_name",
                        "addr",
                        "ip",
                        "log_time",
                        "log_time_readable",
                    ]
                )
                for log in self.logs_data:
                    action_label = ACTION_LABELS.get(
                        log["action"], f"未知({log['action']})"
                    )
                    time_str = (
                        time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(int(log.get("log_time", 0))),
                        )
                        if log.get("log_time")
                        else ""
                    )
                    writer.writerow(
                        [
                            log["action"],
                            action_label,
                            log.get("biz", ""),
                            log.get("device_name", ""),
                            log.get("addr", ""),
                            log.get("ip", ""),
                            log.get("log_time", ""),
                            time_str,
                        ]
                    )

            self.status_label.setText(f"导出成功 → {path}")
            QMessageBox.information(self, "导出成功", f"已保存到:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
