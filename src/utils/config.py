import json
import os
from pathlib import Path


class Config:
    def __init__(self):
        # 默认配置
        self.default_config = {
            "output_dir": str(Path.home() / "Documents" / "VideoText"),
            "whisper_model": "base",
            "language": "zh",
            "theme": "light",
            "max_threads": 2,
            "supported_formats": [".mp4", ".avi", ".mkv", ".mov", ".flv"],
            "transcriber": "funasr",
            "minimize_to_tray": True,
        }

        # 配置文件路径
        self.config_dir = Path.home() / ".videotext"
        self.config_file = self.config_dir / "config.json"

        # 加载配置
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return {**self.default_config, **json.load(f)}
            return self.default_config
        except Exception:
            return self.default_config

    def save_config(self):
        """保存配置到文件"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save_config()
