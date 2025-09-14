# Knowledge Base Tuning

文档知识库转换和处理工具包，用于将各种格式的文档转换为结构化的知识库内容。

## 功能特性

- **多格式文档转换**: 支持 DOC/DOCX/XLS/XLSX/PDF 等格式的转换
- **智能表格处理**: 自动提取和格式化HTML/PDF中的表格内容
- **大模型增强**: 使用LLM对内容进行智能增强和结构化
- **批量处理**: 支持大批量文档的自动化处理
- **自定义索引**: 为知识库内容生成智能索引
- **质量评估**: 提供问答系统的性能评估功能

## 项目结构

```text
knowledge-base-tuning/
├── src/
│   ├── __init__.py          # 包初始化文件
│   ├── config.py            # 配置管理模块
│   ├── utils.py             # 工具函数模块
│   ├── file_converter.py    # 文件格式转换模块
│   ├── html_processor.py    # HTML表格处理模块
│   ├── pdf_processor.py     # PDF文档处理模块
│   ├── llm_client.py        # 大模型API客户端
│   ├── document_merger.py   # 文档合并模块
│   └── main.py              # 主程序入口
├── data/
│   ├── ori/                 # 原始文档目录
│   ├── mid/                 # 中间转换结果
│   ├── pdf_tab/             # PDF表格文件
│   └── out/                 # 最终输出目录
├── config.json.template     # 配置文件模板
├── config.json              # 配置文件（需要创建）
├── qa.json                  # 问答数据文件
├── requirements.txt         # 依赖包列表
├── run.py                   # 快速启动脚本
└── README.md               # 项目说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

复制配置模板并填入你的API信息：

```bash
cp config.json.template config.json
```

编辑 `config.json` 文件，填入正确的API地址和密钥。

### 3. 准备数据

将待处理的文档文件放入 `data/ori/` 目录中。

### 4. 运行处理

```bash
python run.py
```

或者使用Python模块方式：

```bash
python -m src.main
```

## 配置文件

创建 `config.json` 文件，包含以下配置：

```json
{
  "url": "http://your-api-url/",
  "dataset": {
    "id": "your-dataset-id",
    "key": "your-dataset-key"
  },
  "app": {
    "id": "your-app-id", 
    "key": "your-app-key"
  },
  "prompts": {
    "start": "请处理以下表格内容...",
    "continue": "请继续处理..."
  }
}
```

## 使用方法

### 基本使用

```python
from pathlib import Path
from src.main import DocumentProcessor

# 创建处理器实例
config_path = Path("./config.json")
processor = DocumentProcessor(config_path)

# 运行完整的处理流水线
source_dir = Path("./data/ori")
output_dir = Path("./data")
qa_file = Path("./qa.json")

processor.run_full_pipeline(source_dir, output_dir, qa_file)
```

### 分步处理

```python
# 1. 文件格式转换
processor.process_file_conversion(source_dir, mid_dir)

# 2. HTML表格处理
processor.process_html_tables(mid_dir, table_dir)

# 3. PDF文档处理  
processor.process_pdf_documents(mid_dir, doc_dir)

# 4. LLM增强处理
processor.process_llm_enhancement(table_dir, llm_tab_dir)

# 5. 文档合并
processor.merge_documents(pdf_dir, llm_dir, merge_dir)
```

### 独立模块使用

```python
# 使用文件转换器
from src.file_converter import FileConverter
converter = FileConverter()
converter.batch_convert(source_dir, output_dir)

# 使用HTML处理器
from src.html_processor import HTMLTableProcessor
html_processor = HTMLTableProcessor()
html_processor.batch_process_html(source_dir, output_dir)

# 使用PDF处理器
from src.pdf_processor import PDFProcessor
pdf_processor = PDFProcessor()
pdf_processor.batch_process_pdfs(source_dir, output_dir)
```

## 依赖要求

- Python 3.7+
- LibreOffice (用于文档格式转换)
- beautifulsoup4 (HTML解析)
- pandas (数据处理)
- pdfplumber (PDF文本提取)
- camelot-py (PDF表格提取)
- requests (HTTP请求)
- PyYAML (YAML配置支持)

## 注意事项

1. 确保系统已安装LibreOffice，并配置正确的路径
2. 配置文件中的API密钥需要有相应的权限
3. 处理大量文档时请注意磁盘空间和处理时间
4. 建议在处理前备份原始文档

## 许可证

MIT License
