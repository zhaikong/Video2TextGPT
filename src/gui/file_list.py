from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt


class FileListWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 标题
        title = QLabel("文件列表")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 文件列表
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    def add_file(self, file_path):
        """添加文件到列表"""
        item = QListWidgetItem(file_path)
        item.setData(
            Qt.ItemDataRole.UserRole,
            {
                "status": "pending",  # pending/processing/completed/failed
                "path": file_path,
            },
        )
        self.list_widget.addItem(item)

    def update_status(self, file_path, status):
        """更新文件状态"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data["path"] == file_path:
                data["status"] = status
                item.setData(Qt.ItemDataRole.UserRole, data)
                break
