# 数据目录说明

此目录包含文档处理的各个阶段文件：

## 目录结构

- `ori/` - 原始文档存放目录，支持格式：
  - Word文档 (.doc, .docx)
  - Excel表格 (.xls, .xlsx)  
  - PDF文件 (.pdf)

- `mid/` - 中间转换结果，LibreOffice转换后的文件

- `pdf_tab/` - Excel转PDF的专门目录

- `out/` - 最终输出目录
  - `table/` - HTML表格转Markdown结果
  - `doc/` - PDF文档转Markdown结果
  - `pdf_tab/` - PDF表格转Markdown结果
  - `llm_tab/` - LLM增强处理结果
  - `merge_tab/` - 合并后的最终结果

## 使用说明

1. 将待处理的原始文档放入 `ori/` 目录
2. 运行处理程序
3. 在 `out/merge_tab/` 目录查看最终结果
