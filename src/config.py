"""
配置管理模块
处理配置文件读取和配置对象创建
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any


class IdKeyPair:
    """ID和Key对类"""

    @staticmethod
    def mask(value: str) -> str:
        """掩码显示敏感信息"""
        return value[:2] + "****" + value[-2:] if value and len(value) > 4 else "****"

    def __init__(self, dic: Dict[str, str]):
        self.id = dic.get("id")
        self.key = dic.get("key")

    def __str__(self) -> str:
        return f"  id: {self.mask(self.id)}\n" f"  key: {self.mask(self.key)}\n"


class Prompts:
    """提示词配置类"""

    def __init__(self, dic: Dict[str, str]):
        self.start_prompt = dic.get("start")
        self.continue_prompt = dic.get("continue")

    def __str__(self) -> str:
        return f"  start: {self.start_prompt}\n" f"  continue: {self.continue_prompt}\n"


class Config:
    """配置类"""

    def __init__(self, config_path: Path):
        # 支持YAML和JSON两种格式
        with open(config_path, "r", encoding="utf-8") as file:
            if config_path.suffix in [".yml", ".yaml"]:
                self.__config_dict__ = yaml.safe_load(file)
            elif config_path.suffix == ".json":
                self.__config_dict__ = json.load(file)

        self.url = self.__config_dict__.get("url")
        self.dataset = IdKeyPair(self.__config_dict__.get("dataset", {}))
        self.app = IdKeyPair(self.__config_dict__.get("app", {}))
        self.prompts = Prompts(self.__config_dict__.get("prompts", {}))

    def __str__(self) -> str:
        return (
            f"dataset: \n{self.dataset}"
            f"app: \n{self.app}"
            f"prompts: \n{self.prompts}"
        )


def load_config(config_path: Path) -> Config:
    """加载配置文件"""
    return Config(config_path)
