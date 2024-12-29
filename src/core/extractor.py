try:
    from moviepy.editor import VideoFileClip
except ImportError:
    # 尝试替代导入方式
    from moviepy.video.io.VideoFileClip import VideoFileClip

import os
from typing import Callable
from proglog import ProgressBarLogger


class MyLogger(ProgressBarLogger):
    def __init__(self, progress_callback=None):
        super().__init__()
        self.progress_callback = progress_callback

    def callback(self, **changes):
        # 获取当前进度
        if "index" in changes and "total" in self.state:
            progress = int((changes["index"] / self.state["total"]) * 100)
            if self.progress_callback:
                self.progress_callback(progress)
        super().callback(**changes)


class AudioExtractor:
    def __init__(self):
        self.supported_formats = [".mp4", ".avi", ".mkv", ".mov", ".flv"]

    def extract(
        self, video_path: str, progress_callback: Callable[[int], None] = None
    ) -> str:
        """
        从视频中提取音频

        Args:
            video_path: 视频文件路径
            progress_callback: 进度回调函数

        Returns:
            音频文件路径
        """
        # 检查文件格式
        ext = os.path.splitext(video_path)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"不支持的视频格式: {ext}")

        # 生成音频输出路径
        audio_path = os.path.splitext(video_path)[0] + ".wav"

        try:
            # 加载视频
            video = VideoFileClip(video_path)

            if video.audio is None:
                raise ValueError("视频文件没有音频轨道")

            # 创建自定义logger
            my_logger = MyLogger(progress_callback) if progress_callback else None

            # 写入音频文件
            video.audio.write_audiofile(
                audio_path,
                fps=16000,  # whisper推荐采样率
                nbytes=2,  # 16位音频
                codec="pcm_s16le",
                logger=my_logger,
            )

            return audio_path

        except Exception as e:
            raise RuntimeError(f"音频提取失败: {str(e)}")

        finally:
            # 清理资源
            if "video" in locals():
                video.close()
