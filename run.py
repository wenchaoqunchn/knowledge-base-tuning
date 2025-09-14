#!/usr/bin/env python3
"""
快速启动脚本
运行完整的文档处理流水线
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.main import DocumentProcessor


def main():
    """主程序入口"""
    print("=" * 50)
    print("知识库文档处理工具")
    print("=" * 50)

    # 检查配置文件
    config_path = Path("./config.json")
    if not config_path.exists():
        print("❌ 配置文件 config.json 不存在，请先创建配置文件")
        return

    # 检查源文档目录
    source_dir = Path("./data/ori")
    if not source_dir.exists():
        print("❌ 源文档目录 ./data/ori 不存在，请先创建目录并放入待处理文档")
        return

    try:
        # 创建处理器实例
        processor = DocumentProcessor(config_path)

        # 定义路径
        output_dir = Path("./data")
        qa_file = Path("./qa.json")

        print("🚀 开始运行文档处理流水线...")
        print(f"📁 源目录: {source_dir}")
        print(f"📁 输出目录: {output_dir}")

        # 运行完整流水线
        processor.run_full_pipeline(source_dir, output_dir, qa_file)

        print("✅ 处理完成！")
        print(f"📄 结果保存在: {output_dir}")

    except Exception as e:
        print(f"❌ 处理过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
