"""
主程序入口
协调各个模块完成完整的文档处理流程
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

from .config import load_config
from .file_converter import FileConverter
from .html_processor import HTMLTableProcessor
from .pdf_processor import PDFProcessor
from .llm_client import LLMClient
from .document_merger import DocumentMerger
from .utils import read_md, load_json_to_dict


class DocumentProcessor:
    """文档处理主类"""

    def __init__(self, config_path: Path):
        self.config = load_config(config_path)
        self.converter = FileConverter()
        self.html_processor = HTMLTableProcessor()
        self.pdf_processor = PDFProcessor()
        self.llm_client = LLMClient(self.config)
        self.merger = DocumentMerger()

    def process_file_conversion(self, source_dir: Path, output_dir: Path) -> None:
        """执行文件格式转换"""
        print("开始文件格式转换...")
        self.converter.batch_convert(source_dir, output_dir)

        # 专门处理Excel转PDF
        pdf_tab_dir = Path("./data/pdf_tab")
        self.converter.convert_excel_to_pdf(source_dir, pdf_tab_dir)
        print("文件格式转换完成")

    def process_html_tables(self, source_dir: Path, output_dir: Path) -> None:
        """处理HTML表格"""
        print("开始处理HTML表格...")
        self.html_processor.batch_process_html(source_dir, output_dir)
        print("HTML表格处理完成")

    def process_pdf_documents(self, source_dir: Path, output_dir: Path) -> None:
        """处理PDF文档"""
        print("开始处理PDF文档...")
        self.pdf_processor.batch_process_pdfs(source_dir, output_dir)
        print("PDF文档处理完成")

    def process_pdf_tables(self, source_dir: Path, output_dir: Path) -> None:
        """处理PDF表格"""
        print("开始处理PDF表格...")
        self.pdf_processor.batch_process_pdf_tables(source_dir, output_dir)
        print("PDF表格处理完成")

    def process_llm_enhancement(self, source_dir: Path, output_dir: Path) -> None:
        """使用LLM增强表格内容"""
        print("开始LLM增强处理...")
        output_dir.mkdir(parents=True, exist_ok=True)

        for md_file in source_dir.glob("*.md"):
            md_content = read_md(md_file)
            chat_id = md_file.stem

            enhanced_content = self.llm_client.process_table_with_llm(
                md_content, chat_id
            )

            output_file = output_dir / md_file.name
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(enhanced_content)

        print("LLM增强处理完成")

    def merge_documents(self, pdf_dir: Path, llm_dir: Path, output_dir: Path) -> None:
        """合并文档"""
        print("开始合并文档...")
        self.merger.merge_md_files(pdf_dir, llm_dir, output_dir)
        print("文档合并完成")

    def evaluate_qa_performance(self, qa_file: Path, output_file: Path) -> None:
        """评估问答性能"""
        print("开始评估问答性能...")

        qa_list = load_json_to_dict(qa_file)
        if not qa_list:
            print("无法加载QA数据")
            return

        role_prompt = """<context>你的角色是"财务制度库查询助手"，主要职责是帮助用户快速准确地查找公司内部的财务制度、政策文件以及相关的指导原则。请遵循以下指导来完成任务：

理解查询需求：首先，你需要理解用户的查询需求。这可能包括具体的政策名称、关键词或者与某个特定主题相关的信息。
数据库搜索：使用内部数据库或知识库进行搜索，找到与用户请求最相关的规章制度或文件。确保搜索范围包括但不限于公司手册、员工守则、合规指南等文档。
提供结果摘要：为用户提供搜索结果的简要概述，并附上直接链接或附件（如果适用），以便他们可以进一步阅读完整内容。
确认与反馈：询问用户是否找到了他们所需要的信息，如果没有找到，请进一步澄清他们的需求并再次尝试提供帮助；如果找到了，询问是否有其他问题需要解答。
记录查询情况：在每次交互后，记录下查询的情况，包括查询主题、提供的资料、用户满意度等信息，以便于后续分析和改进服务。
请以礼貌且专业的态度回应所有请求，并确保所提供的信息是最新的且准确无误。</context>\n 问题如下：\n"""

        exp_dict = {"问题": [], "标答": [], "对标": [], "优化": []}

        # 基础评估
        for qa in qa_list:
            question = qa["问题"]
            answer = qa["答案"]
            chat_id = question

            self.llm_client.delete_one_chat(chat_id)
            response = self.llm_client.chat(role_prompt + question, chat_id)

            exp_dict["问题"].append(question)
            exp_dict["标答"].append(answer)
            exp_dict["对标"].append(response)

        # 优化评估（可选的部分数据）
        for qa in qa_list[:6]:  # 只处理前6个
            question = qa["问题"]
            chat_id = "0" + question

            self.llm_client.delete_one_chat(chat_id)
            response = self.llm_client.chat(role_prompt + question, chat_id)
            exp_dict["优化"].append(response)

        # 保存结果
        exp_df = pd.DataFrame(exp_dict)
        exp_df.to_excel(output_file, index=False)
        print(f"评估结果已保存到: {output_file}")

    def add_custom_indexes(self, parent_ids: List[str]) -> None:
        """为数据添加自定义索引"""
        print("开始添加自定义索引...")

        # 收集所有集合ID
        all_collection_ids = []
        for parent_id in parent_ids:
            collections = self._get_all_collections_recursive(parent_id)
            all_collection_ids.extend(collections)

        # 为每个集合中的数据添加索引
        for collection_id in all_collection_ids:
            self._add_indexes_to_collection(collection_id)

        print("自定义索引添加完成")

    def _get_all_collections_recursive(self, parent_id: str) -> List[str]:
        """递归获取所有集合ID"""
        collection_ids = []
        page = 0

        while True:
            response = self.llm_client.get_collection_list(parent_id, page)
            collections = response.get("data", {}).get("list", [])

            if not collections:
                break

            collection_ids.extend([col.get("_id") for col in collections])
            page += 1

        return collection_ids

    def _add_indexes_to_collection(self, collection_id: str) -> None:
        """为集合中的数据添加索引"""
        page = 0

        while True:
            response = self.llm_client.get_data_list(collection_id, page)
            data_list = response.get("data", {}).get("list", [])

            if not data_list:
                break

            for data_item in data_list:
                data_id = data_item["_id"]
                data_q = data_item["q"]

                try:
                    index_list = self.llm_client.generate_custom_indexes(
                        data_q, data_id
                    )
                    if index_list:
                        self.llm_client.add_index(data_id, data_q, index_list)
                except Exception as e:
                    print(f"为数据 {data_id} 添加索引失败: {e}")

            page += 1

    def run_full_pipeline(
        self, source_dir: Path, base_output_dir: Path, qa_file: Path = None
    ) -> None:
        """运行完整的处理流水线"""
        print("开始运行完整的文档处理流水线...")

        # 创建输出目录结构
        mid_dir = base_output_dir / "mid"
        pdf_tab_dir = base_output_dir / "pdf_tab"
        out_dir = base_output_dir / "out"
        table_dir = out_dir / "table"
        doc_dir = out_dir / "doc"
        llm_tab_dir = out_dir / "llm_tab"
        merge_tab_dir = out_dir / "merge_tab"

        # 步骤1: 文件格式转换
        self.process_file_conversion(source_dir, mid_dir)

        # 步骤2: 处理HTML表格
        self.process_html_tables(mid_dir, table_dir)

        # 步骤3: 处理PDF文档
        self.process_pdf_documents(mid_dir, doc_dir)

        # 步骤4: 处理PDF表格
        self.process_pdf_tables(pdf_tab_dir, out_dir / "pdf_tab")

        # 步骤5: LLM增强处理
        self.process_llm_enhancement(table_dir, llm_tab_dir)

        # 步骤6: 合并文档
        self.merge_documents(out_dir / "pdf_tab", llm_tab_dir, merge_tab_dir)

        # 步骤7: 评估QA性能（可选）
        if qa_file and qa_file.exists():
            self.evaluate_qa_performance(qa_file, base_output_dir / "qa_results.xlsx")

        print("完整流水线处理完成！")


def main():
    """主程序入口"""
    # 配置文件路径
    config_path = Path("./config.json")

    # 创建处理器实例
    processor = DocumentProcessor(config_path)

    # 定义路径
    source_dir = Path("./data/ori")
    output_dir = Path("./data")
    qa_file = Path("./qa.json")

    # 运行完整流水线
    processor.run_full_pipeline(source_dir, output_dir, qa_file)

    # 可选：添加自定义索引
    # parent_ids = ["68a2be19311a079022e3bdb1", "68a2be11311a079022e3bd87", "689edbd8311a079022e2843f"]
    # processor.add_custom_indexes(parent_ids)


if __name__ == "__main__":
    main()
