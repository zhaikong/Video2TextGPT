from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QPushButton,
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("设置")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Whisper模型选择
        model_layout = QHBoxLayout()
        model_label = QLabel("Whisper模型:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText(self.config.get("whisper_model", "base"))
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # 语言选择
        lang_layout = QHBoxLayout()
        lang_label = QLabel("识别语言:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["zh", "en", "ja", "ko", "auto"])
        self.lang_combo.setCurrentText(self.config.get("language", "zh"))
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # 最大线程数
        thread_layout = QHBoxLayout()
        thread_label = QLabel("最大线程数:")
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 8)
        self.thread_spin.setValue(self.config.get("max_threads", 2))
        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.thread_spin)
        layout.addLayout(thread_layout)

        # 最小化到托盘
        self.tray_check = QCheckBox("最小化到系统托盘")
        self.tray_check.setChecked(self.config.get("minimize_to_tray", True))
        layout.addWidget(self.tray_check)

        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # 连接信号
        save_btn.clicked.connect(self.save_settings)
        cancel_btn.clicked.connect(self.reject)

    def save_settings(self):
        """保存设置"""
        self.config.set("whisper_model", self.model_combo.currentText())
        self.config.set("language", self.lang_combo.currentText())
        self.config.set("max_threads", self.thread_spin.value())
        self.config.set("minimize_to_tray", self.tray_check.isChecked())
        self.accept()
