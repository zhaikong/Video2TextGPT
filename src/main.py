import sys
import os
import atexit
import multiprocessing

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import Logger


def cleanup():
    """清理资源"""
    # 清理多进程资源
    if hasattr(multiprocessing, "resource_tracker"):
        multiprocessing.resource_tracker._resource_tracker = None


def main():
    # 注册清理函数
    atexit.register(cleanup)

    # 创建日志记录器
    logger = Logger()
    logger.info("启动应用程序")

    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)

        # 设置应用程序信息
        app.setApplicationName("VideoText Converter")
        app.setApplicationVersion("1.0.0")

        # 创建并显示主窗口
        window = MainWindow()
        window.show()

        # 运行应用程序
        sys.exit(app.exec())

    except Exception as e:
        logger.exception("应用程序异常退出")
        sys.exit(1)


if __name__ == "__main__":
    main()
