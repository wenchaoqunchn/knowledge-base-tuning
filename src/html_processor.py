"""
HTML处理模块
处理HTML表格的提取、清理和格式化
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional


class HTMLTableProcessor:
    """HTML表格处理器"""

    def __init__(self):
        pass

    def get_first_table(self, soup: BeautifulSoup) -> BeautifulSoup:
        """只保留第一个table标签"""
        first_table = soup.find("table")
        new_soup = BeautifulSoup(features="xml")
        if first_table:
            new_soup.append(first_table)
        self.remove_style_attributes(new_soup)
        return new_soup

    def only_get_table(self, soup: BeautifulSoup) -> BeautifulSoup:
        """只保留所有table标签"""
        tables = soup.find_all("table")
        new_soup = BeautifulSoup(features="xml")
        for tab in tables:
            new_soup.append(tab)
        self.remove_style_attributes(new_soup)
        return new_soup

    def remove_trailing_empty_cells(self, table) -> int:
        """移除表格每行末尾共有的空白单元格"""
        trailing_empty_counts = []

        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            empty_cnt = 0

            # 从后向前计算空白单元格数量
            for cell in reversed(cells):
                if not cell.text.strip():
                    empty_cnt += 1
                else:
                    break

            trailing_empty_counts.append(empty_cnt)

        if not trailing_empty_counts:
            return 0

        common_empty_cnt = min(trailing_empty_counts)

        if common_empty_cnt > 0:
            for tr in table.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                for _ in range(common_empty_cnt):
                    if cells:
                        cells[-1].decompose()
                        cells = cells[:-1]

        return common_empty_cnt

    def flatten_paragraphs(self, soup: BeautifulSoup, label: str) -> None:
        """去除指定标签，只保留文本内容"""
        for l in soup.find_all(label):
            text_content = l.get_text(" ", strip=True)
            l.replace_with(text_content)

    def remove_empty_rows(self, soup: BeautifulSoup) -> None:
        """移除表格中的空行并简化空白单元格"""
        for tr in soup.find_all("tr"):
            # 先处理空白单元格
            for cell in tr.find_all(["td", "th"]):
                if not cell.text.strip():
                    new_cell = soup.new_tag(cell.name)
                    new_cell.attrs = cell.attrs.copy()
                    cell.replace_with(new_cell)

            # 然后检查是否整行为空
            if not tr.text.strip() or all(
                cell.name in ["td", "th"] and not cell.contents
                for cell in tr.find_all(["td", "th"])
            ):
                tr.decompose()

    def add_basic_table_styles(self, soup: BeautifulSoup) -> None:
        """为表格添加基础样式"""
        for table in soup.find_all("table"):
            table["border"] = "1"
            table["cellspacing"] = "0"
            table["cellpadding"] = "4"

    def remove_unnecessary_elements(self, soup: BeautifulSoup) -> None:
        """移除不必要的元素"""
        elements_to_remove = [
            "style",
            "script",
            "comment",
            "head",
            "meta",
            "link",
            "colgroup",
            "col",
            "title",
        ]
        for element in soup.find_all(elements_to_remove):
            element.decompose()

    def remove_style_attributes(self, soup: BeautifulSoup) -> None:
        """移除样式和类属性"""
        for tag in soup.find_all(True):
            attrs = {}
            for attr in ["colspan", "rowspan"]:
                if attr in tag.attrs:
                    attrs[attr] = tag[attr]
            tag.attrs = attrs

    def prettify(self, soup: BeautifulSoup, compact: bool = False) -> str:
        """格式化HTML输出"""
        out = soup.prettify()
        tab = " "

        out = re.sub(r"(</?t[rdable].*?>)\n\s+", r"\1\n", out)
        out = re.sub(r"\s+(</t[rdable]>)", r"\n\1", out)
        out = re.sub(r"(<td.*?>)\n(.*?)\n(</td>)", r"\1\2\3", out)
        out = re.sub(r"(<td.*?>)\n(</td>)", r"\1\2", out)
        out = re.sub(r"<td", tab * 2 + r"<td", out)
        out = re.sub(r"(</*tr)", tab + r"\1", out)

        if compact:
            out = re.sub(r"(</*)t([drh].*?>)", r"\1\2", out)
        return out

    def medium_compact(self, soup: BeautifulSoup) -> str:
        """中等压缩格式"""
        output = self.prettify(soup)
        output = re.sub(r"<\?xml.*?\?>", "", output).strip()
        return output

    def high_compact(self, soup: BeautifulSoup) -> str:
        """高压缩格式"""
        output = self.prettify(soup, compact=True)
        output = re.sub(r"<\?xml.*?\?>", "", output)
        output = (
            r"<!-- 标签映射表={<table>:<t>,<tr>:<r>,<td>:<d>,<th>:<h>} -->" + output
        )
        return output

    def simplify_html_table(self, html_content: str, compact_level: int = 0) -> str:
        """主函数：简化XHTML表格内容"""
        soup = BeautifulSoup(html_content, "lxml")

        # 处理流程
        self.remove_unnecessary_elements(soup)
        self.remove_style_attributes(soup)
        self.flatten_paragraphs(soup, "font")
        self.flatten_paragraphs(soup, "b")
        self.remove_empty_rows(soup)

        for table in soup.find_all("table"):
            self.remove_trailing_empty_cells(table)

        self.add_basic_table_styles(soup)

        if compact_level == 0:
            output = re.sub(r"\s+", " ", str(soup))
        elif compact_level == 1:
            output = self.medium_compact(self.only_get_table(soup))
        else:
            output = self.high_compact(self.only_get_table(soup))

        return output

    def html_to_markdown(self, html_path: Path, output_path: Path) -> None:
        """将HTML文件转换为Markdown格式"""
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        simplified_html = self.simplify_html_table(html_content, compact_level=1)
        md = "```markdown\n" + simplified_html + "\n```"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)

    def batch_process_html(self, source_dir: Path, output_dir: Path) -> None:
        """批量处理HTML文件"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cnt = 0
        for html_file in source_dir.glob("*.html"):
            cnt += 1
            print(f"Processing file {cnt}: {html_file.stem}")
            output_file = output_dir / html_file.with_suffix(".md").name
            self.html_to_markdown(html_file, output_file)
