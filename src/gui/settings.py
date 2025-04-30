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

        # 转写引擎选择
        engine_layout = QHBoxLayout()
        engine_label = QLabel("转写引擎:")
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["whisper", "funasr"])
        self.engine_combo.setCurrentText(self.config.get("transcriber", "whisper"))
        engine_layout.addWidget(engine_label)
        engine_layout.addWidget(self.engine_combo)
        layout.addLayout(engine_layout)

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

        # 主题选择
        theme_layout = QHBoxLayout()
        theme_label = QLabel("界面主题:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.config.get("theme", "light"))
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

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
        # 当转写引擎变化时更新UI状态
        self.engine_combo.currentTextChanged.connect(self.update_ui_state)
        # 初始化UI状态
        self.update_ui_state(self.engine_combo.currentText())

    def update_ui_state(self, engine):
        """根据选择的转写引擎更新UI状态"""
        # 只有选择whisper时，才启用whisper相关设置
        is_whisper = engine == "whisper"
        self.model_combo.setEnabled(is_whisper)

    def save_settings(self):
        """保存设置"""
        self.config.set("transcriber", self.engine_combo.currentText())
        self.config.set("whisper_model", self.model_combo.currentText())
        self.config.set("language", self.lang_combo.currentText())
        self.config.set("theme", self.theme_combo.currentText())
        self.config.set("max_threads", self.thread_spin.value())
        self.config.set("minimize_to_tray", self.tray_check.isChecked())
        self.accept()
