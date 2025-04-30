from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QSystemTrayIcon,
    QMenu,
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QApplication
import os
from pathlib import Path
from datetime import datetime

from src.core.converter import Converter
from src.utils.config import Config
from src.utils.logger import Logger
from src.gui.file_list import FileListWidget
from src.gui.progress import ProgressWidget
from src.gui.status import StatusWidget
from src.gui.theme import ThemeManager
from src.gui.settings import SettingsDialog


class DropArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存对主窗口的引用
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("拖拽文件到这里\n或点击选择文件")
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #666;
                border-radius: 8px;
                padding: 20px;
                background: #f0f0f0;
            }
        """
        )
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(
                """
                QLabel {
                    border: 2px dashed #2196F3;
                    border-radius: 8px;
                    padding: 20px;
                    background: #E3F2FD;
                }
            """
            )

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #666;
                border-radius: 8px;
                padding: 20px;
                background: #f0f0f0;
            }
        """
        )

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #666;
                border-radius: 8px;
                padding: 20px;
                background: #f0f0f0;
            }
        """
        )
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(url.toLocalFile())
            # 使用保存的主窗口引用
            if hasattr(self.main_window, "handle_dropped_files"):
                self.main_window.handle_dropped_files(links)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoText Converter")
        self.setMinimumSize(800, 600)

        # 初始化组件
        self.config = Config()
        self.logger = Logger()
        self.converter = Converter()

        # 初始化主题管理器
        self.theme_manager = ThemeManager(QApplication.instance())
        self.theme_manager.apply_theme(self.config.get("theme", "light"))

        # 创建主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 创建主布局
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # 左侧文件列表
        self.file_list = FileListWidget()
        layout.addWidget(self.file_list, stretch=2)

        # 中央处理区
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_widget.setLayout(center_layout)

        # 拖拽区域
        self.drop_area = DropArea(self)
        center_layout.addWidget(self.drop_area)

        # 按钮区
        button_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("选择文件")
        self.select_dir_btn = QPushButton("选择目录")
        button_layout.addWidget(self.select_file_btn)
        button_layout.addWidget(self.select_dir_btn)
        center_layout.addLayout(button_layout)

        # 进度展示
        self.progress = ProgressWidget()
        center_layout.addWidget(self.progress)

        layout.addWidget(center_widget, stretch=4)

        # 右侧状态区
        self.status = StatusWidget()
        layout.addWidget(self.status, stretch=2)

        # 底部控制栏
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始转换")
        self.pause_btn = QPushButton("暂停")
        self.cancel_btn = QPushButton("取消")
        self.output_btn = QPushButton("输出目录")

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.cancel_btn)
        control_layout.addWidget(self.output_btn)

        center_layout.addLayout(control_layout)

        # 添加主题切换按钮
        self.theme_btn = QPushButton("切换主题")
        control_layout.addWidget(self.theme_btn)
        self.theme_btn.clicked.connect(self.toggle_theme)

        # 添加设置按钮
        self.settings_btn = QPushButton("设置")
        control_layout.addWidget(self.settings_btn)
        self.settings_btn.clicked.connect(self.show_settings)

        # 连接信号
        self.select_file_btn.clicked.connect(self.select_files)
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.start_btn.clicked.connect(self.start_conversion)
        self.pause_btn.clicked.connect(self.pause_conversion)
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.output_btn.clicked.connect(self.select_output_dir)

        # 连接转换器信号
        self.converter.progress_updated.connect(self.update_progress)
        self.converter.stage_changed.connect(self.update_stage)
        self.converter.conversion_complete.connect(self.handle_completion)
        self.converter.error_occurred.connect(self.handle_error)

        self.logger.info("主窗口初始化完成")

        # 创建系统托盘
        self.setup_tray_icon()

    def select_files(self):
        """选择文件"""
        # 从配置获取支持的格式
        formats = self.config.get("supported_formats", [".mp4", ".avi", ".mkv", ".mov", ".flv"])
        # 构建过滤器字符串
        filter_str = "视频文件 ("
        for fmt in formats:
            filter_str += f"*{fmt} "
        filter_str = filter_str.strip() + ")"
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件", "", filter_str
        )
        if files:
            self.handle_dropped_files(files)

    def select_directory(self):
        """选择目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择视频目录")
        if directory:
            self.handle_dropped_files([directory])

    def handle_dropped_files(self, paths):
        """处理拖放的文件"""
        supported_formats = self.config.get("supported_formats")
        for path in paths:
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in supported_formats:
                    self.file_list.add_file(path)
                    self.logger.info(f"添加文件: {path}")
                else:
                    self.logger.warning(f"不支持的文件格式: {path}")
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext in supported_formats:
                            self.file_list.add_file(file_path)
                            self.logger.info(f"添加文件: {file_path}")

    def start_conversion(self):
        """开始转换"""
        if self.file_list.list_widget.count() == 0:
            QMessageBox.warning(self, "警告", "请先添加需要转换的文件")
            return

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)

        # 获取所有待处理文件
        for i in range(self.file_list.list_widget.count()):
            item = self.file_list.list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data["status"] == "pending":
                self.converter.add_task(data["path"])

        self.converter.start()
        self.logger.info("开始转换任务")

    def pause_conversion(self):
        """暂停转换"""
        if self.pause_btn.text() == "暂停":
            self.converter.pause()
            self.pause_btn.setText("继续")
            self.logger.info("暂停转换任务")
        else:
            self.converter.resume()
            self.pause_btn.setText("暂停")
            self.logger.info("继续转换任务")

    def cancel_conversion(self):
        """取消转换"""
        reply = QMessageBox.question(
            self,
            "确认取消",
            "确定要取消当前转换任务吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.converter.stop()
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            self.logger.info("取消转换任务")

    def select_output_dir(self):
        """选择输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择输出目录", self.config.get("output_dir")
        )
        if directory:
            self.config.set("output_dir", directory)
            self.logger.info(f"设置输出目录: {directory}")

    def update_progress(self, file_path: str, progress: int):
        """更新进度"""
        self.progress.update_current_progress(progress)

        # 更新总体进度
        total = self.file_list.list_widget.count()
        completed = 0
        for i in range(total):
            item = self.file_list.list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data["status"] == "completed":
                completed += 1
            elif data["path"] == file_path:
                completed += progress / 100

        total_progress = int((completed / total) * 100)
        self.progress.update_total_progress(total_progress)

    def update_stage(self, file_path: str, stage: str):
        """更新处理阶段"""
        stage_map = {
            "extracting_audio": "正在提取音频",
            "transcribing": "正在转写文本",
            "saving": "正在保存文件",
        }

        self.progress.set_stage(stage_map.get(stage, stage))
        self.status.update_stage(stage_map.get(stage, stage))
        self.status.update_current_file(os.path.basename(file_path))
        self.file_list.update_status(file_path, "processing")

    def handle_completion(self, file_path: str):
        """处理完成回调"""
        self.file_list.update_status(file_path, "completed")

        # 获取输出路径
        output_dir = Path(self.config.get("output_dir"))
        video_name = os.path.basename(file_path)
        video_name_without_ext = os.path.splitext(video_name)[0]
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"{video_name_without_ext}_{current_time}.md"
        output_path = output_dir / md_filename

        self.status.add_detail(f"完成转换: {os.path.basename(file_path)}")
        self.status.add_detail(f"输出文件: {output_path}")
        self.logger.info(f"完成文件转换: {file_path}")
        self.logger.info(f"输出文件路径: {output_path}")

        # 检查是否所有任务都已完成
        all_completed = True
        for i in range(self.file_list.list_widget.count()):
            item = self.file_list.list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data["status"] != "completed":
                all_completed = False
                break

        if all_completed:
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            # 修改完成提示，包含输出目录信息
            QMessageBox.information(
                self, "完成", f"所有文件转换完成!\n\n输出目录: {output_dir}"
            )
            self.logger.info("所有转换任务完成")

    def handle_error(self, file_path: str, error: str):
        """处理错误回调"""
        self.file_list.update_status(file_path, "failed")
        self.status.add_detail(f"转换失败: {os.path.basename(file_path)} - {error}")
        self.logger.error(f"文件转换失败: {file_path} - {error}")

        QMessageBox.critical(
            self, "错误", f"转换失败: {os.path.basename(file_path)}\n{error}"
        )

    def setup_tray_icon(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)

        # 创建默认图标
        icon = QIcon()
        # 创建一个1x1的透明图标（如果没有实际的图标文件）
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        icon.addPixmap(pixmap)
        self.tray_icon.setIcon(icon)

        # 创建托盘菜单
        tray_menu = QMenu()

        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("隐藏", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.handle_tray_activation)

    def handle_tray_activation(self, reason):
        """处理托盘图标激活"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isHidden():
                self.show()
            else:
                self.hide()

    def toggle_theme(self):
        """切换主题"""
        current_theme = self.config.get("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.config.set("theme", new_theme)
        self.theme_manager.apply_theme(new_theme)

    def closeEvent(self, event):
        """重写关闭事件"""
        if self.config.get("minimize_to_tray", True):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "VideoText Converter",
                "应用程序已最小化到系统托盘",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )
        else:
            event.accept()

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.config, self)
        result = dialog.exec()
        if result:
            # 如果用户保存了设置，更新主题
            self.theme_manager.apply_theme(self.config.get("theme", "light"))
            # 更新转换器的配置
            self.converter.update_config()
            # 更新状态
            self.status.update_stage(f"设置已更新，转写引擎: {self.config.get('transcriber')}, 模型: {self.config.get('whisper_model')}")
            self.logger.info("配置已更新")
