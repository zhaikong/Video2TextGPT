from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt


class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 标题
        title = QLabel("状态信息")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 当前文件
        self.current_file = QLabel("当前文件: 无")
        layout.addWidget(self.current_file)

        # 处理阶段
        self.stage = QLabel("处理阶段: 待开始")
        layout.addWidget(self.stage)

        # 剩余时间
        self.time_left = QLabel("预计剩余时间: --:--")
        layout.addWidget(self.time_left)

        # 详细信息
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        layout.addWidget(self.details)

    def update_current_file(self, filename):
        """更新当前处理文件"""
        self.current_file.setText(f"当前文件: {filename}")

    def update_stage(self, stage):
        """更新处理阶段"""
        self.stage.setText(f"处理阶段: {stage}")

    def update_time_left(self, time_str):
        """更新剩余时间"""
        self.time_left.setText(f"预计剩余时间: {time_str}")

    def add_detail(self, text):
        """添加详细信息"""
        self.details.append(text)
