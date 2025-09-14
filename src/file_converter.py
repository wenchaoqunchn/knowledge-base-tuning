"""
文件转换模块
使用LibreOffice进行文档格式转换
"""

import subprocess
from pathlib import Path
from typing import Dict, Optional


class FileConverter:
    """文件转换器"""

    def __init__(
        self,
        libreoffice_path: str = "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
    ):
        self.libreoffice_path = libreoffice_path

        # 默认转换映射
        self.conversion_map = {
            ".doc": "pdf",
            ".docx": "pdf",
            ".xls": "html",
            ".xlsx": "html",
            ".pdf": "pdf",
        }

    def libre_convert(self, input_path: Path, format_to: str, out_dir: Path) -> bool:
        """通过LibreOffice命令行转换文件"""
        cmd = [
            self.libreoffice_path,
            "--headless",
            "--convert-to",
            format_to,
            "--outdir",
            str(out_dir),
            str(input_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ 转换成功: {input_path}")
            return True
        else:
            print(f"❌ 转换失败: {result.stderr}")
            return False

    def batch_convert(
        self,
        source_dir: Path,
        output_dir: Path,
        conversion_map: Optional[Dict[str, str]] = None,
    ) -> None:
        """批量转换文件"""
        if conversion_map is None:
            conversion_map = self.conversion_map

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        for doc in source_dir.rglob("*.*"):
            if doc.suffix in conversion_map:
                target_format = conversion_map[doc.suffix]
                self.libre_convert(doc, target_format, output_dir)

    def convert_excel_to_pdf(self, source_dir: Path, output_dir: Path) -> None:
        """专门转换Excel文件为PDF"""
        output_dir.mkdir(parents=True, exist_ok=True)

        for doc in source_dir.rglob("*.xls*"):
            self.libre_convert(doc, "pdf", output_dir)
