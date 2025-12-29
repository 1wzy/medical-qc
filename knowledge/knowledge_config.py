# knowledge_config.py
# 知识库配置文件

import os
from pathlib import Path

# 获取当前文件所在目录
BASE_DIR = Path(__file__).parent

# 知识库目录配置
KNOWLEDGE_CONFIG = {
    # 原始知识文件目录
    "txt_dir": BASE_DIR,
    
    # Chroma 向量数据库存储目录
    "chroma_dir": BASE_DIR / "chroma_db",
    
    # 元数据索引文件
    "meta_file": BASE_DIR / "meta" / "knowledge_index.json",
    
    # 文本分块配置
    "chunk_size": 500,          # 固定长度分块的字符数
    "chunk_overlap": 50,        # 分块重叠字符数
    
    # Embedding 模型配置（参考 ICD_recall3.py）
    "embedding_model": "text-embedding-3-large",  # 可根据实际情况修改
    "embedding_api_url": "https://api.openai-proxy.org/v1",  # 如果使用自定义 API，在这里配置
    "embedding_api_key": os.getenv("OPENAI_API_KEY", "sk-WL5Q0rvWQAJMt3D22MLV5i4XVCJWInDSNoTir3z8E2JgiEDi"),  # 从环境变量读取，如果没有则使用 "none"
    
    # 检索配置
    "default_top_k": 5,         # 默认返回结果数量
    "similarity_threshold": 0.7,  # 相似度阈值（可选，用于过滤低质量结果）
    
    # 向量库配置
    "collection_metadata": {
        "hnsw:space": "cosine"  # 使用余弦相似度
    }
}

# 确保必要的目录存在
def ensure_directories():
    """确保必要的目录存在"""
    KNOWLEDGE_CONFIG["chroma_dir"].mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "meta").mkdir(parents=True, exist_ok=True)
    (KNOWLEDGE_CONFIG["chroma_dir"] / "department").mkdir(parents=True, exist_ok=True)
    (KNOWLEDGE_CONFIG["chroma_dir"] / "general").mkdir(parents=True, exist_ok=True)

# 初始化时创建目录
ensure_directories()

