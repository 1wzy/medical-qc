# knowledge 模块初始化文件

"""
知识库模块

提供知识库向量数据库的构建和检索功能。

主要组件：
- knowledge_config.py: 配置文件
- knowledge_builder.py: 向量库构建器
- knowledge_retriever.py: 检索器

使用示例：

1. 构建知识库：
   python knowledge_builder.py --build-all

2. 检索知识：
   from knowledge_retriever import get_retriever
   retriever = get_retriever()
   results = retriever.retrieve_by_department("诊疗规范", "产科", top_k=5)
"""

__version__ = "1.0.0"

