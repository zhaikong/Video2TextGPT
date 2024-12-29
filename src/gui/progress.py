from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt


class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 总体进度
        total_layout = QHBoxLayout()
        total_label = QLabel("总体进度:")
        self.total_progress = QProgressBar()
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_progress)
        layout.addLayout(total_layout)

        # 当前任务进度
        current_layout = QHBoxLayout()
        current_label = QLabel("当前进度:")
        self.current_progress = QProgressBar()
        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_progress)
        layout.addLayout(current_layout)

        # 阶段说明
        self.stage_label = QLabel("准备就绪")
        self.stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stage_label)

    def update_total_progress(self, value):
        """更新总体进度"""
        self.total_progress.setValue(value)

    def update_current_progress(self, value):
        """更新当前任务进度"""
        self.current_progress.setValue(value)

    def set_stage(self, stage):
        """设置当前阶段"""
        self.stage_label.setText(stage)
