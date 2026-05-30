import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,
    QMessageBox
)
from PySide6.QtCore import Qt


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口
        self.setWindowTitle("我的第一个 PySide6 软件")
        self.resize(500, 400)

        # 创建组件
        self.title_label = QLabel("请输入内容：")
        self.input_box = QLineEdit()

        self.button = QPushButton("开始执行")

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        # 绑定按钮事件
        self.button.clicked.connect(self.handle_click)

        # 布局
        layout = QVBoxLayout()

        layout.addWidget(self.title_label)
        layout.addWidget(self.input_box)
        layout.addWidget(self.button)
        layout.addWidget(self.log_box)

        self.setLayout(layout)

    def handle_click(self):
        text = self.input_box.text().strip()

        if not text:
            QMessageBox.warning(self, "提示", "请输入内容")
            return

        # 输出日志
        self.log_box.append(f"收到输入：{text}")
        self.log_box.append("正在执行任务...")
        self.log_box.append("任务完成\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyWindow()
    window.show()

    sys.exit(app.exec())
    # pyinstaller - F - w code.py打包成exe
