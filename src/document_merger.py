"""
文档合并模块
处理不同来源文档的合并操作
"""

from pathlib import Path
from typing import List


class DocumentMerger:
    """文档合并器"""

    def __init__(self):
        pass

    def merge_md_files(
        self, pdf_tab_dir: Path, llm_tab_dir: Path, merge_tab_dir: Path
    ) -> None:
        """
        拼接pdf_tab和llm_tab中的同名MD文件，结果存入merge_tab

        参数:
            pdf_tab_dir: 包含PDF生成MD文件的目录
            llm_tab_dir: 包含LLM生成MD文件的目录
            merge_tab_dir: 存放合并结果的目录
        """
        # 确保输出目录存在
        merge_tab_dir.mkdir(parents=True, exist_ok=True)

        # 获取pdf_tab中的所有md文件
        pdf_files = list(pdf_tab_dir.glob("*.md"))

        # 遍历所有pdf文件
        for pdf_file in pdf_files:
            # 获取对应的llm文件路径
            llm_file = llm_tab_dir / pdf_file.name

            # 检查llm文件是否存在
            if not llm_file.exists():
                print(f"警告: {pdf_file.name} 在llm_tab中不存在，跳过")
                continue

            # 读取两个文件内容
            pdf_content = pdf_file.read_text(encoding="utf-8")
            llm_content = llm_file.read_text(encoding="utf-8")

            # 拼接内容(pdf在前，llm在后)
            merged_content = f"{pdf_content}\n\n---\n\n{llm_content}"

            # 写入合并后的文件
            output_file = merge_tab_dir / pdf_file.name
            output_file.write_text(merged_content, encoding="utf-8")
            print(f"已合并: {pdf_file.name}")

    def merge_documents_from_dirs(
        self, source_dirs: List[Path], output_dir: Path, separator: str = "\n\n---\n\n"
    ) -> None:
        """
        从多个目录合并同名文档

        参数:
            source_dirs: 源目录列表
            output_dir: 输出目录
            separator: 文档间的分隔符
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if not source_dirs:
            return

        # 以第一个目录的文件为基准
        base_files = list(source_dirs[0].glob("*.md"))

        for base_file in base_files:
            contents = []

            # 收集所有目录中的同名文件内容
            for source_dir in source_dirs:
                target_file = source_dir / base_file.name
                if target_file.exists():
                    content = target_file.read_text(encoding="utf-8")
                    contents.append(content)
                else:
                    print(f"警告: {base_file.name} 在 {source_dir} 中不存在")

            if contents:
                # 合并内容
                merged_content = separator.join(contents)

                # 写入合并后的文件
                output_file = output_dir / base_file.name
                output_file.write_text(merged_content, encoding="utf-8")
                print(f"已合并: {base_file.name} (来自 {len(contents)} 个源)")


def main():
    """主函数示例"""
    # 定义目录路径
    base_dir = Path("./data/out")
    pdf_tab = base_dir / "pdf_tab"
    llm_tab = base_dir / "llm_tab"
    merge_tab = base_dir / "merge_tab"

    # 创建合并器实例
    merger = DocumentMerger()

    # 验证输入目录存在
    if not pdf_tab.exists() or not pdf_tab.is_dir():
        raise FileNotFoundError(f"目录不存在: {pdf_tab}")
    if not llm_tab.exists() or not llm_tab.is_dir():
        raise FileNotFoundError(f"目录不存在: {llm_tab}")

    # 执行合并
    merger.merge_md_files(pdf_tab, llm_tab, merge_tab)
    print("所有文件合并完成！")


if __name__ == "__main__":
    main()
