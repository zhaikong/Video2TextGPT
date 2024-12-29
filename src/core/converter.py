from PyQt6.QtCore import QObject, pyqtSignal
from queue import Queue, Empty
import threading
from .extractor import AudioExtractor
from .transcriber import create_transcriber
from ..utils.logger import Logger
import os
from datetime import datetime
from pathlib import Path


class Converter(QObject):
    # 信号定义
    progress_updated = pyqtSignal(str, int)  # 文件路径, 进度值
    stage_changed = pyqtSignal(str, str)  # 文件路径, 阶段
    conversion_complete = pyqtSignal(str)  # 文件路径
    error_occurred = pyqtSignal(str, str)  # 文件路径, 错误信息

    def __init__(self):
        super().__init__()
        self.task_queue = Queue()
        self.is_running = False
        self.current_task = None
        self.logger = Logger()

        # 从配置获取转写引擎
        from utils.config import Config

        config = Config()
        transcriber_engine = config.get("transcriber", "funasr")

        self.extractor = AudioExtractor()
        self.transcriber = create_transcriber(transcriber_engine)

    def add_task(self, file_path):
        """添加转换任务"""
        self.task_queue.put(file_path)

    def start(self):
        """开始处理队列中的任务"""
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self._process_queue, daemon=True).start()

    def stop(self):
        """停止处理"""
        self.is_running = False

    def _process_queue(self):
        """处理任务队列"""
        while self.is_running:
            try:
                try:
                    file_path = self.task_queue.get(timeout=1)
                except Empty:
                    continue

                self.current_task = file_path

                try:
                    # 第一步：提取音频
                    self.stage_changed.emit(file_path, "extracting_audio")
                    audio_path = self.extractor.extract(
                        file_path,
                        progress_callback=lambda p: self.progress_updated.emit(
                            file_path, p
                        ),
                    )

                    # 第二步：转写文本
                    self.stage_changed.emit(file_path, "transcribing")
                    text = self.transcriber.transcribe(
                        audio_path,
                        progress_callback=lambda p: self.progress_updated.emit(
                            file_path, p
                        ),
                    )

                    # 第三步：保存文件
                    self.stage_changed.emit(file_path, "saving")
                    output_path = self._save_markdown(file_path, text)
                    self.logger.info(f"保存转写文件到: {output_path}")

                    # 删除临时音频文件
                    try:
                        os.remove(audio_path)
                        self.logger.info(f"删除临时音频文件: {audio_path}")
                    except Exception as e:
                        self.logger.warning(f"删除临时音频文件失败: {str(e)}")

                    self.conversion_complete.emit(file_path)
                    self.task_queue.task_done()

                except Exception as e:
                    import traceback

                    error_msg = f"{str(e)}\n{traceback.format_exc()}"
                    self.error_occurred.emit(file_path, error_msg)
                    self.task_queue.task_done()

            except Exception as e:
                import traceback

                print(f"Queue processing error: {str(e)}\n{traceback.format_exc()}")

    def _save_markdown(self, video_path, text):
        """保存为markdown文件"""
        try:
            # 获取视频文件信息
            video_name = os.path.basename(video_path)
            video_name_without_ext = os.path.splitext(video_name)[0]
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 从配置获取输出目录
            from utils.config import Config

            config = Config()
            output_dir = Path(config.get("output_dir"))
            output_dir.mkdir(parents=True, exist_ok=True)

            # 生成markdown文件路径
            md_filename = f"{video_name_without_ext}_{current_time}.md"
            md_path = output_dir / md_filename

            # 获取视频时长(如果可用)
            duration = ""
            try:
                from moviepy.editor import VideoFileClip

                with VideoFileClip(video_path) as video:
                    duration = (
                        f"{int(video.duration // 60)}分{int(video.duration % 60)}秒"
                    )
            except Exception:
                duration = "未知"

            # 生成纯文本版本（移除时间戳）
            pure_text = []
            for line in text.split("\n"):
                if line.strip():
                    # 移除时间戳部分 [00:00.000 --> 00:00.000]
                    if "]" in line:
                        pure_text.append(line.split("]", 1)[1].strip())
                    else:
                        pure_text.append(line.strip())

            # 生成markdown内容
            content = f"""# {video_name_without_ext}

## 基本信息
- 文件名: {video_name}
- 创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 视频时长: {duration}

## 转写文本（带时间戳）
{text}

## 纯文本版本
{chr(10).join(pure_text)}
"""

            # 写入文件
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)

            return str(md_path)

        except Exception as e:
            raise RuntimeError(f"保存Markdown文件失败: {str(e)}")
