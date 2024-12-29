import whisper
import torch
from typing import Callable
import warnings
from abc import ABC, abstractmethod

# 忽略 FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)


class BaseTranscriber(ABC):
    """转写器基类"""

    @abstractmethod
    def transcribe(
        self, audio_path: str, progress_callback: Callable[[int], None] = None
    ) -> str:
        pass


class WhisperTranscriber(BaseTranscriber):
    def __init__(self):
        # 检查是否可用GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # 加载模型(默认使用base模型,可以通过配置修改)
        self.model = whisper.load_model("medium", device=self.device)

    def transcribe(
        self, audio_path: str, progress_callback: Callable[[int], None] = None
    ) -> str:
        """使用 Whisper 进行转写"""
        try:
            if progress_callback:
                progress_callback(0)

            result = self.model.transcribe(
                audio_path,
                language="zh",
                task="transcribe",
                fp16=False,
                verbose=True,
                word_timestamps=True,
            )

            if progress_callback:
                progress_callback(100)

            formatted_text = []
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()
                if text:
                    timestamp = (
                        f"[{format_timestamp(start)} --> {format_timestamp(end)}]"
                    )
                    formatted_text.append(f"{timestamp} {text}\n")

            return "".join(formatted_text)

        except Exception as e:
            raise RuntimeError(f"Whisper转写失败: {str(e)}")


class FunASRTranscriber(BaseTranscriber):
    def __init__(self):
        try:
            from funasr import AutoModel
            from funasr.utils.postprocess_utils import rich_transcription_postprocess

            # 保存后处理函数的引用
            self.postprocess = rich_transcription_postprocess

            # 使用官方支持的模型
            self.model = AutoModel(
                model="damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                device="cuda" if torch.cuda.is_available() else "cpu",
            )
        except ImportError:
            raise ImportError(
                "请先安装必要的依赖:\n" "pip install torchaudio\n" "pip install funasr"
            )
        except Exception as e:
            raise RuntimeError(f"FunASR 初始化失败: {str(e)}")

    def transcribe(
        self, audio_path: str, progress_callback: Callable[[int], None] = None
    ) -> str:
        """使用 FunASR 进行转写"""
        try:
            if progress_callback:
                progress_callback(0)

            # FunASR 转写
            result = self.model.generate(
                input=audio_path,
                cache={},
                batch_size=1,  # 单个批次处理
                hotwords=None,  # 不使用热词
                mode="offline",  # 离线模式
            )

            if progress_callback:
                progress_callback(50)

            # 格式化输出
            formatted_text = []
            if isinstance(result, list) and result:
                current_time = 0
                for i, segment in enumerate(result):
                    if isinstance(segment, dict):
                        # 应用后处理
                        text = self.postprocess(segment.get("text", "")).strip()
                        timestamps = segment.get("timestamp", None)
                        if text:
                            if timestamps:
                                start, end = timestamps
                            else:
                                # 如果没有时间戳，估算时间
                                duration = len(text) * 0.3
                                start = current_time
                                end = start + duration
                                current_time = end + 0.1

                            timestamp = f"[{format_timestamp(start)} --> {format_timestamp(end)}]"
                            formatted_text.append(f"{timestamp} {text}\n")

            if progress_callback:
                progress_callback(100)

            return "".join(formatted_text)

        except Exception as e:
            raise RuntimeError(f"FunASR转写失败: {str(e)}")


def format_timestamp(seconds: float) -> str:
    """格式化时间戳"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:05.3f}"


def create_transcriber(engine: str = "whisper") -> BaseTranscriber:
    """创建转写器工厂方法"""
    if engine.lower() == "whisper":
        return WhisperTranscriber()
    elif engine.lower() == "funasr":
        return FunASRTranscriber()
    else:
        raise ValueError(f"不支持的转写引擎: {engine}")
