import sys
import os
import json
import base64
import random
import string
import time
import csv
from typing import Optional

import requests
from PySide6.QtCore import Qt, QObject, QThread, Signal, QUrl
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QLineEdit,
    QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QProgressBar,
    QMessageBox, QDialog, QGroupBox
)


# ================= 路径配置（兼容 PyInstaller 打包） =================

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
DATA_DIR = os.path.join(APP_DIR, "data")
COOKIE_FILE = os.path.join(DATA_DIR, "cookies.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "网易云评论.csv")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

os.makedirs(DATA_DIR, exist_ok=True)


# ================= 网易云加密核心算法 =================

MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
PUBKEY = "010001"
NONCE = "0CoJUm6Qyw8W8jud"


def get_random_secret_key(length=16):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def aes_encrypt(text, key):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    iv = b"0102030405060708"
    pad_text = pad(text.encode("utf-8"), 16)
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(pad_text)).decode("utf-8")


def rsa_encrypt(text, pub_key, modulus):
    text = text[::-1]
    m = int(text.encode("utf-8").hex(), 16)
    e = int(pub_key, 16)
    n = int(modulus, 16)
    c = pow(m, e, n)
    return format(c, "x").zfill(256)


def get_weapi_data(plaintext_dict):
    text = json.dumps(plaintext_dict)
    secret_key = get_random_secret_key()
    enc_text = aes_encrypt(text, NONCE)
    params = aes_encrypt(enc_text, secret_key)
    enc_sec_key = rsa_encrypt(secret_key, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": enc_sec_key}


# ================= 配置常量 =================

API_URL = "https://music.163.com/weapi/comment/resource/comments/get"
DEFAULT_HEADERS = {
    "accept": "*/*",
    "origin": "https://music.163.com",
    "referer": "https://music.163.com/playlist?id=469708961",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
}

FIELDNAMES = [
    "comment_id", "page", "is_hot", "thread_id", "parent_comment_id",
    "user_id", "nickname", "vip_type", "content", "time", "time_str",
    "liked_count", "reply_count", "ip_location", "be_replied_count",
]

MAX_RETRIES = 5
RETRY_BASE_WAIT = 2
RETRY_MAX_WAIT = 60
SLEEP_MIN = 3.0
SLEEP_MAX = 5.0


# ================= Cookie 持久化 =================

def load_cookies():
    if not os.path.exists(COOKIE_FILE):
        return {}
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cookies(cookies):
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


# ================= 爬虫 Worker =================

class CrawlerWorker(QObject):
    """爬虫工作对象，运行在子线程中。"""
    log = Signal(str)
    progress = Signal(int, int)        # current_page, max_pages
    finished_signal = Signal(int, int) # total_rows, completed_pages

    def __init__(self, thread_id, max_pages, cookies):
        super().__init__()
        self.thread_id = thread_id
        self.max_pages = max_pages
        self.cookies = cookies or {}
        self._stop = False

    def stop(self):
        self._stop = True
        self.log.emit("[!] 收到停止信号，将在当前页完成后停止...")

    def run(self):
        music_u = self.cookies.get("MUSIC_U", "")
        csrf = self.cookies.get("__csrf", "")

        if not music_u:
            self.log.emit("[X] 未登录（缺少 MUSIC_U cookie），请先登录")
            self.finished_signal.emit(0, 0)
            return

        headers = dict(DEFAULT_HEADERS)
        url_params = {"csrf_token": csrf}

        completed_pages, seen_ids, cursor, last_page, hot_done = self._load_progress()
        self.log.emit(f"读取到断点进度：已完成 {len(completed_pages)} 页，已去重 {len(seen_ids)} 条评论")

        csv_file, writer = self._open_csv_writer()
        rows_total = 0

        try:
            for page in range(1, self.max_pages + 1):
                if self._stop:
                    self.log.emit(f"[!] 用户主动停止，已完成 {len(completed_pages)} 页")
                    break

                if page in completed_pages:
                    self.log.emit(f"[{page}/{self.max_pages}] 已完成，跳过")
                    self.progress.emit(page, self.max_pages)
                    continue

                self.log.emit(f"--- [{page}/{self.max_pages}] 正在抓取 ---")
                self.progress.emit(page, self.max_pages)

                plaintext_payload = {
                    "cursor": cursor,
                    "pageSize": 20,
                    "orderType": 1,
                    "pageNo": page,
                    "threadId": self.thread_id,
                }
                encrypted_form_data = get_weapi_data(plaintext_payload)

                try:
                    response = self._request_with_retry(encrypted_form_data, headers, url_params)
                    res_json = response.json()

                    if res_json.get("code") != 200:
                        self.log.emit(f"  接口返回异常 code={res_json.get('code')} msg={res_json.get('message', '')}")
                        time.sleep(3)
                        continue

                    data = res_json.get("data", {}) or {}
                    comments = data.get("comments", []) or []
                    hot_comments = data.get("hotComments", []) or []
                    has_more = data.get("hasMore", False)
                    next_cursor = data.get("cursor", "")

                    self.log.emit(f"  普通评论 {len(comments)} 条，热评 {len(hot_comments)} 条，hasMore={has_more}")

                    if not comments:
                        self.log.emit("  本页普通评论为空，判定已抓取完毕")
                        completed_pages.add(page)
                        self._save_progress(completed_pages, seen_ids, cursor, page, hot_done)
                        break

                    if next_cursor and next_cursor == cursor and page > 1:
                        self.log.emit("  cursor 未变化，判定已抓取完毕")
                        completed_pages.add(page)
                        self._save_progress(completed_pages, seen_ids, cursor, page, hot_done)
                        break

                    new_rows = 0
                    if hot_comments and not hot_done:
                        new_rows += self._write_comments(hot_comments, writer, seen_ids, page, True, csv_file)
                        hot_done = True
                    new_rows += self._write_comments(comments, writer, seen_ids, page, False, csv_file)
                    rows_total += new_rows

                    cursor = next_cursor or cursor
                    completed_pages.add(page)
                    self._save_progress(completed_pages, seen_ids, cursor, page, hot_done)

                    self.log.emit(f"  新增 {new_rows} 条，累计本次 {rows_total} 条")

                    if not has_more:
                        self.log.emit("  hasMore=false（API 此字段不可靠，继续抓下一页验证）")

                    sleep_time = random.uniform(SLEEP_MIN, SLEEP_MAX)
                    self.log.emit(f"  等待 {sleep_time:.2f} 秒...")

                    slept = 0.0
                    while slept < sleep_time:
                        if self._stop:
                            break
                        step = min(0.5, sleep_time - slept)
                        time.sleep(step)
                        slept += step

                except Exception as e:
                    self.log.emit(f"  请求异常（重试耗尽）：{repr(e)}")
                    self.log.emit("  跳过该页，下次运行会续爬此处")
                    time.sleep(3)
        finally:
            csv_file.close()

        self.log.emit("")
        self.log.emit(f"本次新增保存 {rows_total} 条评论")
        self.log.emit(f"CSV 文件：{OUTPUT_FILE}")
        self.log.emit(f"已完成 {len(completed_pages)}/{self.max_pages} 页")
        self.finished_signal.emit(rows_total, len(completed_pages))

    def _request_with_retry(self, encrypted_form_data, headers, url_params):
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            if self._stop:
                raise RuntimeError("用户主动停止")
            try:
                response = requests.post(
                    API_URL, headers=headers, cookies=self.cookies,
                    params=url_params, data=encrypted_form_data, timeout=15,
                )
                if response.status_code in (429,) or 500 <= response.status_code < 600:
                    raise requests.HTTPError(f"状态码 {response.status_code}")
                return response
            except Exception as e:
                last_exc = e
                if attempt >= MAX_RETRIES:
                    break
                wait = min(RETRY_BASE_WAIT * (2 ** (attempt - 1)) + random.uniform(0, 1), RETRY_MAX_WAIT)
                self.log.emit(f"  第 {attempt}/{MAX_RETRIES} 次请求失败（{repr(e)}），{wait:.1f}s 后重试...")
                time.sleep(wait)
        raise last_exc

    @staticmethod
    def _parse_comment(comment, page, is_hot):
        user = comment.get("user", {}) or {}
        ip_loc = comment.get("ipLocation", {}) or {}
        if isinstance(ip_loc, dict):
            ip_location = ip_loc.get("location", "") or ""
        else:
            ip_location = str(ip_loc)
        be_replied = comment.get("beReplied", []) or []
        timestamp = comment.get("time", 0) or 0
        return {
            "comment_id": comment.get("commentId", ""),
            "page": page,
            "is_hot": 1 if is_hot else 0,
            "thread_id": comment.get("threadId", ""),
            "parent_comment_id": comment.get("parentCommentId", 0),
            "user_id": user.get("userId", ""),
            "nickname": user.get("nickname", "") or "",
            "vip_type": user.get("vipType", 0) or 0,
            "content": (comment.get("content", "") or "").replace("\r", " ").replace("\n", " "),
            "time": timestamp,
            "time_str": comment.get("timeStr", "") or "",
            "liked_count": comment.get("likedCount", 0) or 0,
            "reply_count": comment.get("replyCount", 0) or 0,
            "ip_location": ip_location,
            "be_replied_count": len(be_replied),
        }

    def _write_comments(self, comments, writer, seen_ids, page, is_hot, csv_file):
        new_rows = 0
        for comment in comments:
            comment_id = comment.get("commentId")
            if comment_id and comment_id in seen_ids:
                continue
            if comment_id:
                seen_ids.add(comment_id)
            row = self._parse_comment(comment, page, is_hot)
            writer.writerow(row)
            new_rows += 1
        csv_file.flush()
        return new_rows

    def _load_progress(self):
        if not os.path.exists(PROGRESS_FILE):
            return set(), set(), "-1", 0, False
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return (
                set(data.get("completed_pages", [])),
                set(data.get("seen_ids", [])),
                data.get("cursor", "-1"),
                data.get("last_page", 0),
                data.get("hot_comments_done", False),
            )
        except Exception as e:
            self.log.emit(f"读取进度文件失败（{repr(e)}），从头开始")
            return set(), set(), "-1", 0, False

    def _save_progress(self, completed_pages, seen_ids, cursor, last_page, hot_done):
        tmp = PROGRESS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({
                "completed_pages": sorted(completed_pages),
                "seen_ids": list(seen_ids),
                "cursor": cursor,
                "last_page": last_page,
                "hot_comments_done": hot_done,
            }, f, ensure_ascii=False)
        os.replace(tmp, PROGRESS_FILE)

    @staticmethod
    def _open_csv_writer():
        file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
        f = open(OUTPUT_FILE, "a", encoding="utf-8-sig", newline="")
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
            f.flush()
        return f, writer


# ================= 登录对话框 =================

class LoginDialog(QDialog):
    """网易云登录对话框，用 QWebEngineView 加载官方登录页并采集 cookie。"""
    cookies_ready = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("网易云音乐登录")
        self.resize(960, 800)

        self.profile = QWebEngineProfile("netease_login_profile", self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)

        self.cookie_store = self.profile.cookieStore()
        self.cookies: dict = {}
        self.cookie_store.cookieAdded.connect(self._on_cookie_added)

        layout = QVBoxLayout(self)

        tip = QLabel(
            "请使用网易云音乐 App 扫描下方二维码，或切换到手机号/邮箱登录。"
            "登录成功后点击下方「我已登录完成」按钮，cookie 会自动提取并保存。"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("padding: 8px; background: #f0f7ff; border-radius: 4px;")
        layout.addWidget(tip)

        self.webview = QWebEngineView(self)
        page = QWebEnginePage(self.profile, self.webview)
        self.webview.setPage(page)
        self.webview.setUrl(QUrl("https://music.163.com/#/login"))
        self.webview.urlChanged.connect(self._on_url_changed)
        layout.addWidget(self.webview, 1)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("我已登录完成")
        self.ok_btn.setStyleSheet("padding: 6px 18px; background: #c20c0c; color: white;")
        self.ok_btn.clicked.connect(self._on_done)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _on_cookie_added(self, cookie):
        try:
            name = bytes(cookie.name()).decode("utf-8", errors="ignore")
            domain = cookie.domain()
            if "music.163.com" in domain or domain.endswith("163.com"):
                value = bytes(cookie.value()).decode("utf-8", errors="ignore")
                self.cookies[name] = value
        except Exception:
            pass

    def _on_url_changed(self, url):
        self.setWindowTitle(f"网易云音乐登录 - {url.toString()}")

    def _on_done(self):
        if "MUSIC_U" not in self.cookies:
            ret = QMessageBox.warning(
                self, "提示",
                "未检测到 MUSIC_U cookie，可能登录未完成。是否仍然保存当前 cookie？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret != QMessageBox.Yes:
                return
        self.cookies_ready.emit(self.cookies)
        self.accept()


# ================= 主窗口 =================

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网易云音乐评论爬虫")
        self.resize(720, 640)

        self.cookies = load_cookies()
        self.worker: Optional[CrawlerWorker] = None
        self.worker_thread: Optional[QThread] = None

        self._build_ui()
        self._refresh_login_status()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # 登录区
        login_group = QGroupBox("登录状态")
        login_layout = QHBoxLayout(login_group)

        self.login_status_label = QLabel("未登录")
        self.login_status_label.setStyleSheet("color: red; font-weight: bold;")
        login_layout.addWidget(self.login_status_label)
        login_layout.addStretch()

        self.login_btn = QPushButton("登录网易云音乐")
        self.login_btn.clicked.connect(self._on_login)
        login_layout.addWidget(self.login_btn)

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.clicked.connect(self._on_logout)
        self.logout_btn.setEnabled(False)
        login_layout.addWidget(self.logout_btn)

        layout.addWidget(login_group)

        # 抓取参数
        param_group = QGroupBox("抓取参数")
        form = QFormLayout(param_group)

        self.thread_id_input = QLineEdit("A_PL_0_469708961")
        form.addRow("Thread ID:", self.thread_id_input)

        self.max_pages_input = QSpinBox()
        self.max_pages_input.setRange(1, 10000)
        self.max_pages_input.setValue(100)
        form.addRow("抓取页数:", self.max_pages_input)

        layout.addWidget(param_group)

        # 控制按钮
        ctrl_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始抓取")
        self.start_btn.setStyleSheet("padding: 6px 18px; background: #c20c0c; color: white;")
        self.start_btn.clicked.connect(self._on_start)
        ctrl_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        ctrl_layout.addWidget(self.stop_btn)

        ctrl_layout.addStretch()
        layout.addLayout(ctrl_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("尚未开始")
        layout.addWidget(self.progress_label)

        # 日志
        layout.addWidget(QLabel("运行日志："))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        self.log_box.setFont(font)
        layout.addWidget(self.log_box, 1)

        # 底部状态
        footer = QLabel(f"数据目录：{DATA_DIR}")
        footer.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(footer)

    def _refresh_login_status(self):
        if self.cookies.get("MUSIC_U"):
            preview = self.cookies["MUSIC_U"][:12] + "..."
            self.login_status_label.setText(f"已登录（MUSIC_U: {preview}）")
            self.login_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.login_btn.setEnabled(False)
            self.logout_btn.setEnabled(True)
        else:
            self.login_status_label.setText("未登录")
            self.login_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.login_btn.setEnabled(True)
            self.logout_btn.setEnabled(False)

    def _on_login(self):
        dialog = LoginDialog(self)
        dialog.cookies_ready.connect(self._on_cookies_received)
        dialog.exec()

    def _on_cookies_received(self, cookies):
        self.cookies = cookies
        save_cookies(cookies)
        self._refresh_login_status()
        self._log(f"已保存 cookie，共 {len(cookies)} 项")

    def _on_logout(self):
        self.cookies = {}
        if os.path.exists(COOKIE_FILE):
            os.remove(COOKIE_FILE)
        self._refresh_login_status()
        self._log("已退出登录")

    def _on_start(self):
        if not self.cookies.get("MUSIC_U"):
            QMessageBox.warning(self, "提示", "请先登录网易云音乐")
            return

        thread_id = self.thread_id_input.text().strip()
        if not thread_id:
            QMessageBox.warning(self, "提示", "请输入 Thread ID")
            return

        max_pages = self.max_pages_input.value()

        self.worker = CrawlerWorker(thread_id, max_pages, self.cookies)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.worker.log.connect(self._on_log)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished_signal.connect(self.worker_thread.quit)

        self.worker_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.login_btn.setEnabled(False)
        self.logout_btn.setEnabled(False)
        self.thread_id_input.setEnabled(False)
        self.max_pages_input.setEnabled(False)

        self.progress_bar.setRange(0, max_pages)
        self.progress_bar.setValue(0)
        self._log(f"开始抓取：thread_id={thread_id}, max_pages={max_pages}")

    def _on_stop(self):
        if self.worker:
            self.worker.stop()
        self.stop_btn.setEnabled(False)

    def _on_progress(self, current, total):
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"进度：{current}/{total} 页")

    def _on_log(self, msg):
        self.log_box.append(msg)
        self.log_box.moveCursor(QTextCursor.End)

    def _on_finished(self, total_rows, completed_pages):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.login_btn.setEnabled(not self.cookies.get("MUSIC_U"))
        self.logout_btn.setEnabled(bool(self.cookies.get("MUSIC_U")))
        self.thread_id_input.setEnabled(True)
        self.max_pages_input.setEnabled(True)
        self.progress_label.setText(f"完成：本次新增 {total_rows} 条，已完成 {completed_pages} 页")
        self._log("")
        self._log(f"抓取完成：本次新增 {total_rows} 条，已完成 {completed_pages} 页")

    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            ret = QMessageBox.question(
                self, "确认",
                "爬虫正在运行，确定要退出吗？下次启动可断点续爬。",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret != QMessageBox.Yes:
                event.ignore()
                return
            if self.worker:
                self.worker.stop()
            self.worker_thread.quit()
            self.worker_thread.wait(3000)
        event.accept()


# ================= 入口 =================

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
