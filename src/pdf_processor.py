"""
PDF处理模块
处理PDF文档的文本提取和表格处理
"""

import re
import pandas as pd
import pdfplumber
import camelot
from pathlib import Path
from typing import List, Any


class PDFProcessor:
    """PDF处理器"""

    def __init__(self):
        pass

    def md_formatter(self, str_in: str) -> str:
        """格式化文档文本为Markdown格式"""
        if "章" in str_in:
            str_in = re.sub(
                r"(第[一二三四五六七八九十百]+章)",
                r"\n\n## \1 ",
                str_in,
            )
        if "条" in str_in:
            str_in = re.sub(
                r"(第[一二三四五六七八九十百]+条)",
                r"\n\n#### \1\n",
                str_in,
            )
        if "节" in str_in:
            str_in = re.sub(
                r"(第[一二三四五六七八九十百]+节)",
                r"\n\n### \1 ",
                str_in,
            )
        if "（" in str_in:
            str_in = re.sub(
                r"(（[一二三四五六七八九十百]+）)",
                r"\n\n\1",
                str_in,
            )
        if "." in str_in:
            str_in = re.sub(
                r"(\d+)\.",
                r"\n\n（\1）",
                str_in,
            )
        if "附件" in str_in:
            str_in = re.sub(
                r"(附件：)",
                r"\n\n## \1\n",
                str_in,
            )
        return str_in

    def format_table(self, table: List[List[str]]) -> str:
        """格式化表格为Markdown"""
        df = pd.DataFrame(table)
        df = df.fillna("")
        df = df.map(lambda str_in: "".join(str_in.split("\n")))
        md = df.to_markdown(index=False)

        md = re.sub(r"( {2,})", r" ", md)
        md = re.sub(r"(-{3,})", r"-----", md)

        intent = " " * 0
        md = intent + f"\n{intent}".join(md.split("\n"))
        return f"\n{intent}\n" + md + f"\n{intent}\n"

    def find_non_empty_indexes(
        self, inserted_list: List[Any], table: List[List[str]]
    ) -> int:
        """查找非空索引位置"""
        if not table or not table[0]:
            return None

        try:
            for i in range(len(inserted_list)):
                if (
                    inserted_list[i] is not None
                    and inserted_list[i].strip() != ""
                    and inserted_list[i] == table[0][0]
                ):
                    return i

            # 尝试匹配前两个单元格
            for i in range(len(inserted_list) - 1):
                if (
                    inserted_list[i] is not None
                    and inserted_list[i].strip() != ""
                    and inserted_list[i] == table[0][0]
                    and i + 1 < len(inserted_list)
                    and inserted_list[i + 1] == table[0][1]
                ):
                    return i
        except (IndexError, AttributeError):
            pass

        return None

    def replace_table_in_text(
        self, tables: List[List[List[str]]], text_list: List[str]
    ) -> List[str]:
        """在文本中替换表格"""
        inserted_list = text_list.copy()

        for table in tables:
            table_inserted = self.format_table(table)
            h_idx = self.find_non_empty_indexes(inserted_list, table)
            if h_idx is not None:
                inserted_list = text_list[:h_idx] + [table_inserted] + text_list[h_idx:]
            else:
                inserted_list = text_list

        return inserted_list

    def pdf_doc_to_markdown(self, pdf_path: Path, output_path: Path) -> None:
        """将PDF文档转换为Markdown"""
        with pdfplumber.open(pdf_path) as pdf:
            page_list = []
            for page in pdf.pages:
                words = page.extract_words(x_tolerance=3, y_tolerance=3)
                tables = page.extract_tables()
                text_list = [w.get("text") for w in words]

                text_list = self.replace_table_in_text(tables, text_list)
                if text_list:
                    text_list.pop()  # 移除最后一个元素

                text_list = [self.md_formatter(l) for l in text_list]
                page_list.append("".join(text_list))

            content = "# " + "".join(page_list)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def pdf_table_to_markdown(self, pdf_path: Path, output_path: Path) -> None:
        """将PDF表格转换为Markdown"""
        try:
            ctabs = camelot.io.read_pdf(
                str(pdf_path), pages="1", flavor="lattice", strip_text="\n"
            )
            md = f"# {pdf_path.stem}\n\n" + "\n\n".join(
                [ctab.df.to_markdown(index=False) for ctab in ctabs]
            )

            md = re.sub(r"( {2,})", r" ", md)
            md = re.sub(r"(-{3,})", r"-----", md)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md)
        except Exception as e:
            print(f"处理PDF表格时出错 {pdf_path}: {e}")

    def batch_process_pdfs(self, source_dir: Path, output_dir: Path) -> None:
        """批量处理PDF文件"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cnt = 0
        for pdf_file in source_dir.glob("*.pdf"):
            print(f"文件{cnt}开始处理（{pdf_file.stem}）")
            output_path = output_dir / pdf_file.with_suffix(".md").name

            if "通知" in pdf_file.name:
                # 直接复制通知类文件
                import shutil

                shutil.copyfile(pdf_file, output_dir / pdf_file.name)
            elif (
                "表" in pdf_file.name
                or "单" in pdf_file.name
                or "签报" in pdf_file.name
            ):
                print("处理表格文件")
                self.pdf_table_to_markdown(pdf_file, output_path)
            elif (
                "标准" in pdf_file.name
                or "细则" in pdf_file.name
                or "办法" in pdf_file.name
            ):
                self.pdf_doc_to_markdown(pdf_file, output_path)

            cnt += 1

    def batch_process_pdf_tables(self, source_dir: Path, output_dir: Path) -> None:
        """批量处理PDF表格文件"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cnt = 0
        for pdf_file in source_dir.glob("*.pdf"):
            print(f"文件{cnt}开始处理（{pdf_file.stem}）")
            output_path = output_dir / pdf_file.with_suffix(".md").name
            self.pdf_table_to_markdown(pdf_file, output_path)
            cnt += 1
