# knowledge_builder.py
# 知识库向量数据库构建脚本

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # 兼容旧版本
    from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from knowledge_config import KNOWLEDGE_CONFIG
except ImportError:
    # 如果直接运行脚本，使用相对导入
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from knowledge_config import KNOWLEDGE_CONFIG

# 全局 embedding 模型（共享，避免重复初始化）
_embeddings = None

def get_embeddings():
    """获取 embedding 模型实例（单例模式）"""
    global _embeddings
    if _embeddings is None:
        api_key = KNOWLEDGE_CONFIG["embedding_api_key"]
        
        # 检查 API key 是否有效
        if not api_key or api_key == "none":
            raise ValueError(
                "⚠️  OpenAI API Key 未配置！\n"
                "请设置环境变量 OPENAI_API_KEY，或在 knowledge_config.py 中配置 embedding_api_key"
            )
        
        embedding_config = {
            "model": KNOWLEDGE_CONFIG["embedding_model"],
            "api_key": api_key,
            "check_embedding_ctx_length": False,
        }
        
        # 如果配置了自定义 API URL，则使用
        if KNOWLEDGE_CONFIG.get("embedding_api_url"):
            embedding_config["base_url"] = KNOWLEDGE_CONFIG["embedding_api_url"]
        
        _embeddings = OpenAIEmbeddings(**embedding_config)
    
    return _embeddings


def chunk_text_by_paragraph(text: str) -> List[str]:
    """
    按段落分块（推荐用于医疗知识文档）
    保持语义完整性
    """
    if not text or not text.strip():
        return []
    
    # 按双换行符分割段落
    paragraphs = text.split('\n\n')
    # 过滤空段落并去除首尾空白
    chunks = [p.strip() for p in paragraphs if p.strip()]
    
    # 如果某个段落太长，进一步分割
    max_length = KNOWLEDGE_CONFIG["chunk_size"]
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            final_chunks.append(chunk)
        else:
            # 使用 RecursiveCharacterTextSplitter 进一步分割长段落
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_length,
                chunk_overlap=KNOWLEDGE_CONFIG["chunk_overlap"],
                separators=["\n", "。", "；", "，", " "]
            )
            sub_chunks = splitter.split_text(chunk)
            final_chunks.extend(sub_chunks)
    
    return final_chunks


def chunk_text_fixed_size(text: str) -> List[str]:
    """
    固定长度分块（备选方案）
    """
    if not text or not text.strip():
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=KNOWLEDGE_CONFIG["chunk_size"],
        chunk_overlap=KNOWLEDGE_CONFIG["chunk_overlap"],
        separators=["\n\n", "\n", "。", "；", "，", " "]
    )
    return splitter.split_text(text)


class KnowledgeBaseBuilder:
    """知识库构建器"""
    
    def __init__(self):
        self.txt_dir = Path(KNOWLEDGE_CONFIG["txt_dir"])
        self.chroma_dir = Path(KNOWLEDGE_CONFIG["chroma_dir"])
        self.meta_file = Path(KNOWLEDGE_CONFIG["meta_file"])
        self.embeddings = get_embeddings()
        self.meta_index = self._load_meta_index()
    
    def _load_meta_index(self) -> Dict:
        """加载元数据索引"""
        if self.meta_file.exists():
            try:
                with open(self.meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载元数据索引失败: {e}，将创建新索引")
        return {}
    
    def _save_meta_index(self):
        """保存元数据索引"""
        self.meta_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.meta_file, 'w', encoding='utf-8') as f:
            json.dump(self.meta_index, f, ensure_ascii=False, indent=2)
    
    def build_department_knowledge(self, department_name: str, chunk_method: str = "paragraph") -> bool:
        """
        构建指定科室的知识库向量数据库
        
        Args:
            department_name: 科室名称（对应 txt 文件名）
            chunk_method: 分块方法，"paragraph" 或 "fixed"
        
        Returns:
            bool: 是否构建成功
        """
        # 1. 读取知识文件
        txt_file = self.txt_dir / f"{department_name}.txt"
        if not txt_file.exists():
            print(f"❌ 文件不存在: {txt_file}")
            return False
        
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            if not text:
                print(f"⚠️  文件为空: {txt_file}，跳过构建")
                return False
        except Exception as e:
            print(f"❌ 读取文件失败 {txt_file}: {e}")
            return False
        
        # 2. 文本分块
        if chunk_method == "paragraph":
            chunks = chunk_text_by_paragraph(text)
        else:
            chunks = chunk_text_fixed_size(text)
        
        if not chunks:
            print(f"⚠️  文本分块后为空，跳过构建")
            return False
        
        print(f"📝 科室: {department_name}, 文件: {txt_file.name}, 分块数: {len(chunks)}")
        
        # 3. 准备文档和元数据
        documents = []
        metadatas = []
        
        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source": f"{department_name}.txt",
                "department": department_name,
                "chunk_index": idx,
                "chunk_method": chunk_method,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # 4. 构建向量库路径
        persist_dir = self.chroma_dir / "department" / department_name
        
        # 5. 如果向量库已存在，先删除（重建）
        if persist_dir.exists():
            import shutil
            shutil.rmtree(persist_dir)
            print(f"🗑️  删除旧向量库: {persist_dir}")
        
        # 6. 创建 Chroma 向量库
        try:
            vectorstore = Chroma.from_texts(
                texts=documents,
                metadatas=metadatas,
                embedding=self.embeddings,
                persist_directory=str(persist_dir),
                collection_metadata=KNOWLEDGE_CONFIG["collection_metadata"]
            )
            
            # 注意：新版本的 langchain-chroma 使用 persist_directory 时会自动持久化，无需手动调用 persist()
            
            print(f"✅ 成功构建向量库: {persist_dir}")
            
            # 7. 更新元数据索引
            self.meta_index[department_name] = {
                "source_file": f"{department_name}.txt",
                "chunk_count": len(chunks),
                "vectorstore_path": str(persist_dir.relative_to(self.chroma_dir)),
                "chunk_method": chunk_method,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_chars": sum(len(chunk) for chunk in chunks)
            }
            self._save_meta_index()
            
            return True
            
        except Exception as e:
            print(f"❌ 构建向量库失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def build_all_knowledge(self, chunk_method: str = "paragraph") -> Dict[str, bool]:
        """
        构建所有知识库
        
        Returns:
            Dict[str, bool]: {科室名: 是否成功}
        """
        results = {}
        
        # 扫描 txt_dir 下的所有 .txt 文件
        txt_files = list(self.txt_dir.glob("*.txt"))
        
        # 过滤掉不需要处理的文件
        exclude_files = {'requirements.txt', '__init__.py'}
        txt_files = [f for f in txt_files if f.name not in exclude_files]
        
        if not txt_files:
            print(f"⚠️  在 {self.txt_dir} 下未找到有效的知识文件")
            return results
        
        print(f"📚 找到 {len(txt_files)} 个知识文件")
        
        for txt_file in txt_files:
            # 提取科室名（去掉 .txt 后缀）
            department_name = txt_file.stem
            
            # 跳过空文件或无效文件
            if txt_file.stat().st_size == 0:
                print(f"⚠️  跳过空文件: {txt_file.name}")
                continue
            
            print(f"\n{'='*50}")
            print(f"处理: {department_name}")
            print(f"{'='*50}")
            
            success = self.build_department_knowledge(department_name, chunk_method)
            results[department_name] = success
        
        # 打印总结
        print(f"\n{'='*50}")
        print(f"构建完成总结")
        print(f"{'='*50}")
        success_count = sum(1 for v in results.values() if v)
        print(f"成功: {success_count}/{len(results)}")
        for dept, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {dept}")
        
        return results
    
    def rebuild_department(self, department_name: str, chunk_method: str = "paragraph") -> bool:
        """重建指定科室的知识库"""
        return self.build_department_knowledge(department_name, chunk_method)
    
    def get_meta_info(self) -> Dict:
        """获取元数据信息"""
        return self.meta_index.copy()


def main():
    """主函数：命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="知识库向量数据库构建工具")
    parser.add_argument("--build-all", action="store_true", help="构建所有知识库")
    parser.add_argument("--department", type=str, help="构建指定科室的知识库")
    parser.add_argument("--rebuild", type=str, help="重建指定科室的知识库")
    parser.add_argument("--chunk-method", type=str, choices=["paragraph", "fixed"], 
                       default="paragraph", help="分块方法：paragraph（按段落）或 fixed（固定长度）")
    parser.add_argument("--meta", action="store_true", help="查看元数据信息")
    
    args = parser.parse_args()
    
    builder = KnowledgeBaseBuilder()
    
    if args.meta:
        meta = builder.get_meta_info()
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return
    
    if args.build_all:
        builder.build_all_knowledge(chunk_method=args.chunk_method)
    elif args.department:
        builder.build_department_knowledge(args.department, chunk_method=args.chunk_method)
    elif args.rebuild:
        builder.rebuild_department(args.rebuild, chunk_method=args.chunk_method)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

