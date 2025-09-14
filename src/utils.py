"""
工具函数模块
包含各种通用的工具函数
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Optional


def mask(key: str) -> str:
    """掩码显示密钥"""
    return "*****" + key[-4:] if key and len(key) > 4 else "*****"


def read_md(file_path: Path) -> str:
    """读取Markdown文件"""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def remove_spire(text: str) -> str:
    """去除Spire.Doc水印文本"""
    return text.replace(
        "Evaluation Warning: The document was created with Spire.Doc for Python.", ""
    )


def remove_style(text: str) -> str:
    """移除Markdown样式标记"""
    cleaned_text = text.replace("**", "").replace("#", "")
    return remove_multi_newlines(cleaned_text)


def change_bullet_points(text: str) -> str:
    """改变项目符号格式"""
    pattern = r"(\d+)\.\s"
    replacement = r"\1） "
    return re.sub(pattern, replacement, text)


def remove_think(input_string: str) -> str:
    """移除<think>标签内容"""
    pattern = re.compile(r"<think>.*?</think>", re.DOTALL)
    return re.sub(pattern, "", input_string)


def remove_multi_newlines(input_string: str) -> str:
    """移除多余的换行符"""
    pattern = re.compile(r"\n{3,}")
    cleaned_string = re.sub(pattern, "\n\n", input_string)
    return cleaned_string.strip()


def clean_content(content: str) -> str:
    """清理内容"""
    return remove_multi_newlines(remove_think(content))


def load_json_to_dict(file_path: Path) -> Optional[Dict[str, Any]]:
    """安全地将JSON文件加载为字典"""
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None


def get_index_from_response(ans: str) -> list:
    """从回答中提取索引列表"""
    # 提取方括号内的内容
    match = re.search(r"\[(.*?)\]", ans)
    if not match:
        return []

    content = match.group(1)
    items = [item.strip() for item in content.split(",")]

    # 构造目标格式
    return [{"type": "custom", "text": item} for item in items]
