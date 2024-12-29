from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QApplication


class ThemeManager(QObject):
    LIGHT_THEME = """
        QMainWindow, QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        QLabel {
            color: #333333;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
        }
        QProgressBar {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
        }
    """

    DARK_THEME = """
        QMainWindow, QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPushButton {
            background-color: #bb86fc;
            color: #000000;
            border: none;
            padding: 5px 15px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #9965f4;
        }
        QPushButton:disabled {
            background-color: #666666;
        }
        QLabel {
            color: #ffffff;
        }
        QListWidget {
            background-color: #3b3b3b;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
        }
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #bb86fc;
        }
    """

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app

    def apply_theme(self, theme: str):
        """应用主题"""
        if theme == "dark":
            self.app.setStyleSheet(self.DARK_THEME)
        else:
            self.app.setStyleSheet(self.LIGHT_THEME)
